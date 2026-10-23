"""Modelo Monte Carlo de la cadena de respuesta médica en una mina subterránea remota (Santa Cruz).

Pregunta: ¿cuánto tarda un trabajador con una emergencia grave en recibir soporte vital avanzado
y en llegar a un hospital, y qué parte de ese tiempo se puede controlar desde el servicio médico?

Datos reales: ubicación pública de la mina, hospitales de derivación y tiempos de ruta (OSRM / OpenStreetMap).
Todo lo demás son supuestos explícitos (modelo/supuestos.csv), no datos de ninguna empresa.
Uso: python modelo/hora_de_oro.py  ->  modelo/resultados.json
"""
import json
import math
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 20_000
rng = np.random.default_rng(2026)

rutas = pd.read_csv(os.path.join(ROOT, "data", "rutas_osrm.csv")).set_index("destino")
centros = pd.read_csv(os.path.join(ROOT, "data", "centros_derivacion.csv")).set_index("id")


def tri(a, m, b, n=N):
    return rng.triangular(a, m, b, n)


def haversine(p, q):
    r = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


KM_AEREO = haversine(centros.loc["PM", ["lat", "lon"]].tolist(), centros.loc["CR", ["lat", "lon"]].tolist())
VUELO = KM_AEREO / 300 * 60 + 35  # minutos: vuelo a 300 km/h más carga y traslado en destino

ESCENARIOS = {
    "base": dict(),
    "protocolo": dict(protocolo=True),
    "brigada": dict(brigada=True),
    "mejorado": dict(protocolo=True, brigada=True),
    "invierno": dict(clima=0.35),
    "invierno_mejorado": dict(protocolo=True, brigada=True, clima=0.35),
}
NOMBRES = {
    "base": "Escenario de referencia",
    "protocolo": "Derivación preacordada",
    "brigada": "Brigadistas bajo mina",
    "mejorado": "Ambas mejoras",
    "invierno": "Invierno, referencia",
    "invierno_mejorado": "Invierno, ambas mejoras",
}


def simular(protocolo=False, brigada=False, clima=0.12):
    det = tri(1, 3, 10)
    llegada = tri(8, 15, 35)
    bajo_mina = rng.random(N) < 0.60
    extr = np.where(bajo_mina, tri(8, 18, 40) if brigada else tri(10, 25, 60), tri(5, 10, 20))
    primer = det + (np.where(bajo_mina, tri(2, 4, 8), llegada) if brigada else llegada)  # brigadistas solo en frentes bajo mina
    sva = det + llegada
    en_posta = sva + extr
    estab = tri(20, 35, 60)
    coord = tri(5, 12, 30) if protocolo else tri(10, 30, 90)
    prep = tri(3, 6, 12) if protocolo else tri(5, 10, 20)
    if protocolo:  # la derivación se coordina en paralelo a la estabilización
        salida = en_posta + np.maximum(estab, coord + prep)
        fin_coord = en_posta + coord
    else:  # todo en serie: primero estabilizar, después llamar, después preparar
        salida = en_posta + estab + coord + prep
        fin_coord = en_posta + estab + coord
    factor = rng.uniform(0.65, 1.0, N)
    demora = np.where(rng.random(N) < clima, rng.uniform(30, 120, N), 0)
    hosp_cercano = salida + rutas.loc["LH", "min_osrm"] * factor + demora
    alta_terrestre = salida + rutas.loc["CR", "min_osrm"] * factor + demora
    avion_listo = fin_coord + tri(60, 120, 240)
    en_aerodromo = salida + rutas.loc["PM", "min_osrm"] * factor + demora
    alta_aerea = np.maximum(avion_listo, en_aerodromo) + VUELO
    return dict(primer_contacto=primer, sva=sva, en_posta=en_posta, salida=salida, hosp_cercano=hosp_cercano,
                alta_terrestre=alta_terrestre, alta_aerea=alta_aerea,
                tramos=dict(deteccion=det, llegada=llegada, extraccion=extr, estabilizacion=estab,
                            coordinacion=coord, preparacion=prep))


def pct(x):
    return {f"p{p}": round(float(np.percentile(x, p)), 1) for p in (10, 50, 90)}


res = {"n": N, "km_aereo_pm_cr": round(KM_AEREO, 1), "vuelo_min": round(VUELO, 1), "escenarios": {}}
for k, kw in ESCENARIOS.items():
    s = simular(**kw)
    hitos = {h: pct(v) for h, v in s.items() if h != "tramos"}
    res["escenarios"][k] = {
        "nombre": NOMBRES[k],
        "hitos": hitos,
        "tramos_mediana": {t: round(float(np.median(v)), 1) for t, v in s["tramos"].items()},
        "pct_primer_contacto_10": round(100 * float((s["primer_contacto"] <= 10).mean()), 1),
        "pct_sva_20": round(100 * float((s["sva"] <= 20).mean()), 1),
        "pct_salida_120": round(100 * float((s["salida"] <= 120).mean()), 1),
        "pct_alta_6h": round(100 * float((np.minimum(s["alta_terrestre"], s["alta_aerea"]) <= 360).mean()), 1),
        "hist_salida": np.histogram(s["salida"], bins=np.arange(0, 361, 10))[0].tolist(),
    }

b, m = res["escenarios"]["base"], res["escenarios"]["mejorado"]
res["ahorro_salida_p50"] = round(b["hitos"]["salida"]["p50"] - m["hitos"]["salida"]["p50"], 1)
res["ahorro_salida_p90"] = round(b["hitos"]["salida"]["p90"] - m["hitos"]["salida"]["p90"], 1)
# Qué parte del tiempo hasta el hospital más cercano se controla desde el sitio (mediana, escenario base)
res["pct_controlable_base"] = round(100 * b["hitos"]["salida"]["p50"] / b["hitos"]["hosp_cercano"]["p50"], 1)

# Controles de coherencia
assert all(res["escenarios"][e]["hitos"]["salida"]["p50"] < res["escenarios"][e]["hitos"]["hosp_cercano"]["p50"]
           for e in ESCENARIOS)
assert m["hitos"]["salida"]["p90"] < b["hitos"]["salida"]["p90"]
assert res["escenarios"]["invierno"]["hitos"]["hosp_cercano"]["p90"] > b["hitos"]["hosp_cercano"]["p90"]

with open(os.path.join(ROOT, "modelo", "resultados.json"), "w") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)

for k, e in res["escenarios"].items():
    h = e["hitos"]
    print(f"{e['nombre']:<28} 1er contacto p50 {h['primer_contacto']['p50']:>5}  SVA p50 {h['sva']['p50']:>5}  "
          f"salida p50 {h['salida']['p50']:>6} p90 {h['salida']['p90']:>6}  hosp p50 {h['hosp_cercano']['p50']:>6} "
          f"p90 {h['hosp_cercano']['p90']:>6}  alta terr p50 {h['alta_terrestre']['p50']:>6}  aérea p50 {h['alta_aerea']['p50']:>6}  "
          f"%alta<=6h {e['pct_alta_6h']}")
print("ahorro salida p50/p90:", res["ahorro_salida_p50"], res["ahorro_salida_p90"], "controlable:", res["pct_controlable_base"],
      "km aéreo:", res["km_aereo_pm_cr"], "vuelo:", res["vuelo_min"])
print("tramos base:", b["tramos_mediana"])
