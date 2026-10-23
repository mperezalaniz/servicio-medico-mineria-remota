"""Datos SINTÉTICOS de un servicio médico de campamento minero (12 meses) y cálculo de indicadores.

Ningún número de este archivo sale de una empresa real. Los parámetros son supuestos razonables
para mostrar cómo se mide y se controla un servicio médico. Semilla fija para que sea reproducible.
Uso: python tablero/generar_datos.py  ->  tablero/datos/*.csv y tablero/tablero.json
"""
import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tablero", "datos")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(8614)

dias = pd.date_range("2025-10-20", "2026-10-18", freq="D")  # 52 semanas completas (lunes a domingo)
n = len(dias)
mes = dias.month.values

# ---------------------------------------------------------------- población en sitio
pob = np.round(820 + 25 * np.sin(np.arange(n) / 14 * 2 * np.pi) + rng.normal(0, 12, n)).astype(int)

# ---------------------------------------------------------------- consultas por motivo
motivos = {  # tasa base por 1.000 personas-día
    "Respiratorio": 9.0, "Musculoesquelético": 8.0, "Cefalea y malestar general": 5.0, "Digestivo": 4.0,
    "Dermatológico": 2.5, "Trauma leve": 3.0, "Control de crónicos": 4.0, "Oftalmológico": 1.5,
}
invierno = np.isin(mes, [6, 7, 8])
brote = (dias >= "2026-03-09") & (dias <= "2026-03-13")  # brote digestivo simulado (comedor)
filas = []
for m, tasa in motivos.items():
    t = np.full(n, tasa)
    if m == "Respiratorio":
        t = np.where(invierno, tasa * 1.9, np.where(np.isin(mes, [5, 9]), tasa * 1.35, tasa))
    if m == "Digestivo":
        t = np.where(brote, tasa * 4.5, tasa)
    cnt = rng.poisson(t * pob / 1000)
    filas.append(pd.DataFrame({"fecha": dias, "motivo": m, "consultas": cnt}))
cons = pd.concat(filas)
cons.to_csv(os.path.join(OUT, "consultas_diarias.csv"), index=False)

# ---------------------------------------------------------------- exámenes periódicos (cobertura mensual por área)
areas = {"Mina subterránea": 430, "Planta de procesos": 260, "Mantenimiento": 240, "Servicios y campamento": 220,
         "Administración y técnicos": 150}
meses = pd.period_range("2025-11", "2026-10", freq="M")
cob = []
for i, p in enumerate(meses):
    mejora = 0 if i < 5 else min(1, (i - 4) / 4)  # desde abril: recordatorios automáticos y agenda por rotación
    for a, dot in areas.items():
        base = {"Mina subterránea": 0.84, "Planta de procesos": 0.90, "Mantenimiento": 0.86,
                "Servicios y campamento": 0.80, "Administración y técnicos": 0.93}[a]
        pct = min(0.995, base + mejora * (0.975 - base) + rng.normal(0, 0.008))
        cob.append({"mes": str(p), "area": a, "dotacion": dot, "al_dia": int(round(dot * pct))})
cob = pd.DataFrame(cob)
cob.to_csv(os.path.join(OUT, "examenes_periodicos.csv"), index=False)

# ---------------------------------------------------------------- stock crítico (política min-máx, reposición con demora)
items = [  # nombre, consumo medio diario, mínimo, máximo, demora de reposición (días)
    ("Oxígeno, cilindro", 0.35, 6, 14, 10), ("Solución fisiológica 500 ml", 3.0, 40, 110, 12),
    ("Adrenalina 1 mg", 0.08, 6, 12, 14), ("Collar cervical", 0.05, 4, 8, 14),
    ("Vendas y apósitos (caja)", 1.2, 15, 45, 10), ("Salbutamol aerosol", 0.6, 8, 24, 12),
    ("Ibuprofeno 400 mg (caja)", 1.8, 25, 70, 10), ("Boquillas alcoholímetro", 9.0, 150, 420, 14),
    ("Test de drogas en orina", 2.2, 40, 110, 14), ("Guantes de nitrilo (caja)", 2.5, 30, 90, 10),
    ("Suero oral (sobres)", 2.0, 30, 80, 12), ("Férula inmovilizadora", 0.07, 4, 8, 14),
]
stock_rows, quiebres = [], []
corte = pd.Timestamp("2026-04-01")  # antes: pedido mensual a ojo; después: tarjeta kanban al llegar al mínimo
estable = pd.Timestamp("2026-05-01")  # abril es transición; la comparación "después" arranca en mayo
ESTACIONAL = ("Salbutamol aerosol", "Oxígeno, cilindro")
nuevos_min = {}
for nom, cmed, mn0, mx0, lt in items:
    # Mínimo recalculado: consumo de la peor temporada x demora máxima real (lt + 3 días) x 1,25 de seguridad
    pico = 1.9 if nom in ESTACIONAL else 1.0
    mn1 = int(np.ceil(cmed * pico * (lt + 3) * 1.25)) + 1
    nuevos_min[nom] = (mn1, max(mx0, mn1 + (mx0 - mn0)))
for nom, cmed, mn0, mx0, lt in items:
    s, pedido, llega = mx0, 0, None
    for d in dias:
        mn, mx = (mn0, mx0) if d < corte else nuevos_min[nom]
        if llega is not None and d >= llega:
            s += pedido
            pedido, llega = 0, None
        dem = rng.poisson(cmed * (1.9 if nom in ("Salbutamol aerosol", "Oxígeno, cilindro") and d.month in (6, 7, 8) else 1))
        if nom == "Suero oral (sobres)" and pd.Timestamp("2026-03-09") <= d <= pd.Timestamp("2026-03-13"):
            dem *= 4
        s = max(0, s - dem)
        if llega is None:
            if d < corte and d.day == 1:
                pedido = max(0, int(mx * 0.7) - s) if s < mx * 0.6 else 0
            elif d >= corte and s <= mn:
                pedido = mx - s
            if pedido > 0:
                llega = d + pd.Timedelta(days=int(lt + rng.integers(-2, 4)))
        stock_rows.append((d, nom, s, mn, mx))
stock = pd.DataFrame(stock_rows, columns=["fecha", "item", "stock", "minimo", "maximo"])
stock.to_csv(os.path.join(OUT, "stock_diario.csv"), index=False)

# ---------------------------------------------------------------- emergencias y brigadistas
emerg = []
for i, p in enumerate(meses):
    k = rng.poisson(7)
    simulacros = i >= 6  # desde mayo: simulacros mensuales con roles fijos
    for _ in range(k):
        llegada = rng.triangular(6, 11, 22) if simulacros else rng.triangular(8, 15, 35)
        emerg.append({"mes": str(p), "llegada_equipo_min": round(llegada, 1),
                      "derivado": bool(rng.random() < 0.28)})
emerg = pd.DataFrame(emerg)
emerg.to_csv(os.path.join(OUT, "emergencias.csv"), index=False)
brig = pd.DataFrame({"mes": [str(p) for p in meses],
                     "brigadistas": 120,
                     "vigentes": [int(round(120 * v)) for v in np.clip(
                         np.r_[np.linspace(0.70, 0.73, 5), np.linspace(0.78, 0.95, 7)] + rng.normal(0, 0.01, 12), 0, 1)]})
brig.to_csv(os.path.join(OUT, "brigadistas.csv"), index=False)

# ---------------------------------------------------------------- indicadores para el tablero
cd = cons.groupby("fecha").consultas.sum()
tasa_dia = 1000 * cd.values / pob
sem = pd.DataFrame({"c": cd.values, "p": pob}, index=dias).resample("W-SUN").sum()
sem["tasa"] = 1000 * sem.c / sem.p
# Carta U (tasa por exposición) con línea base de los meses sin invierno
base_mask = ~sem.index.month.isin([5, 6, 7, 8, 9])
ubar = sem.c[base_mask].sum() / sem.p[base_mask].sum() * 1000
sem["lcs"] = ubar + 3 * np.sqrt(ubar / (sem.p / 1000))
sem["lci"] = np.maximum(0, ubar - 3 * np.sqrt(ubar / (sem.p / 1000)))
fuera = sem[(sem.tasa > sem.lcs) | (sem.tasa < sem.lci)]

par = cons.groupby("motivo").consultas.sum().sort_values(ascending=False)
mens = cons.assign(mes=cons.fecha.dt.to_period("M").astype(str)).groupby(["mes", "motivo"]).consultas.sum().unstack()

cobm = cob.groupby("mes")[["al_dia", "dotacion"]].sum()
cobm["pct"] = 100 * cobm.al_dia / cobm.dotacion
cob_area_ult = cob[cob.mes == cob.mes.max()].assign(pct=lambda x: 100 * x.al_dia / x.dotacion)

st = stock.assign(bajo_min=stock.stock < stock.minimo, quiebre=stock.stock == 0)
st["periodo"] = np.where(st.fecha < corte, "antes", np.where(st.fecha >= estable, "despues", "transicion"))
dias_per = st.groupby("periodo").fecha.nunique()
q = st.groupby("periodo")[["bajo_min", "quiebre"]].sum()
ult = st[st.fecha == st.fecha.max()].copy()
ult["cobertura_dias"] = [round(r.stock / c, 1) if c > 0 else None for r, c in
                         zip(ult.itertuples(), [it[1] for it in items])]

em = emerg.groupby("mes").agg(n=("llegada_equipo_min", "size"), p50=("llegada_equipo_min", "median"),
                              p90=("llegada_equipo_min", lambda x: np.percentile(x, 90)), deriv=("derivado", "sum"))

T = {
    "aviso": "Datos sintéticos generados para demostración. No corresponden a ninguna empresa.",
    "periodo": [str(dias[0].date()), str(dias[-1].date())],
    "kpi": {
        "cobertura_examenes": round(float(cobm.pct.iloc[-1]), 1), "cobertura_examenes_ini": round(float(cobm.pct.iloc[0]), 1),
        "brigadistas_vigentes": round(100 * brig.vigentes.iloc[-1] / 120, 1), "brigadistas_ini": round(100 * brig.vigentes.iloc[0] / 120, 1),
        "items_bajo_min": int((ult.stock < ult.minimo).sum()), "items_total": len(items),
        "llegada_p90_ult3": round(float(np.percentile(emerg[emerg.mes >= str(meses[-3])].llegada_equipo_min, 90)), 1),
        "llegada_p90_ini3": round(float(np.percentile(emerg[emerg.mes <= str(meses[2])].llegada_equipo_min, 90)), 1),
        "tasa_consultas": round(float(1000 * cd[-28:].sum() / pob[-28:].sum()), 1),
        "derivaciones_ult": int(em.deriv.iloc[-1]),
        "quiebre_dias_antes": round(float(q.loc["antes", "quiebre"] / dias_per["antes"]), 2),
        "quiebre_dias_despues": round(float(q.loc["despues", "quiebre"] / dias_per["despues"]), 2),
        "quiebres_eventos_antes": int(q.loc["antes", "quiebre"]), "quiebres_eventos_despues": int(q.loc["despues", "quiebre"]),
        "dias_antes": int(dias_per["antes"]), "dias_despues": int(dias_per["despues"]),
    },
    "semanal": [{"s": str(i.date()), "t": round(r.tasa, 2), "lcs": round(r.lcs, 2), "lci": round(r.lci, 2)} for i, r in sem.iterrows()],
    "ubar": round(float(ubar), 2),
    "fuera": [str(i.date()) for i in fuera.index],
    "pareto": [{"m": k, "n": int(v)} for k, v in par.items()],
    "mensual_motivo": {"meses": list(mens.index), "series": {c: mens[c].astype(int).tolist() for c in mens.columns}},
    "cobertura_mes": [{"mes": i, "pct": round(r.pct, 1)} for i, r in cobm.iterrows()],
    "cobertura_area": [{"area": r.area, "pct": round(r.pct, 1), "faltan": int(r.dotacion - r.al_dia)} for r in cob_area_ult.itertuples()],
    "stock": [{"item": r.item, "stock": int(r.stock), "min": int(r.minimo), "max": int(r.maximo), "cob": r.cobertura_dias, "min_anterior": [it[2] for it in items if it[0] == r.item][0]} for r in ult.itertuples()],
    "emergencias": [{"mes": i, "n": int(r.n), "p50": round(r.p50, 1), "p90": round(r.p90, 1), "deriv": int(r.deriv)} for i, r in em.iterrows()],
    "brigadistas": [{"mes": r.mes, "pct": round(100 * r.vigentes / r.brigadistas, 1)} for r in brig.itertuples()],
}
assert len(sem) == 52 and cons.consultas.sum() > 0
with open(os.path.join(ROOT, "tablero", "tablero.json"), "w") as f:
    json.dump(T, f, ensure_ascii=False, separators=(",", ":"))
print(json.dumps(T["kpi"], ensure_ascii=False, indent=0))
print("ubar", T["ubar"], "fuera", T["fuera"])
print("pareto", T["pareto"])
print("cobertura area", T["cobertura_area"])
print("stock", [(s["item"][:18], s["stock"], s["min"]) for s in T["stock"]])
print("emerg", T["emergencias"])
