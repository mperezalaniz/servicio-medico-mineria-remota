"""Arma docs/index.html (página interactiva) desde la plantilla y los resultados del modelo y del tablero."""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "plan"))
from contenido import FASES  # noqa: E402

M = json.load(open(os.path.join(ROOT, "modelo", "resultados.json")))
rutas = pd.read_csv(os.path.join(ROOT, "data", "rutas_osrm.csv")).set_index("destino")
cen = pd.read_csv(os.path.join(ROOT, "data", "centros_derivacion.csv"))
centros = [dict(id=r.id, nombre=r.nombre, localidad=r.localidad, nivel=r.nivel_denominacion, lat=r.lat, lon=r.lon,
                km=float(rutas.loc[r.id, "km_ruta"]), min=int(rutas.loc[r.id, "min_osrm"])) for r in cen.itertuples()]
j = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
REPO = "https://github.com/mperezalaniz/servicio-medico-mineria-remota"
html = open(os.path.join(ROOT, "docs", "plantilla.html"), encoding="utf-8").read()
rep = {
    "__GEO__": open(os.path.join(ROOT, "data", "geografia.json"), encoding="utf-8").read(),
    "__RUTAS__": j({k: int(v) for k, v in rutas.min_osrm.items()}),
    "__CENTROS__": j(centros),
    "__TABLERO__": open(os.path.join(ROOT, "tablero", "tablero.json"), encoding="utf-8").read(),
    "__FASES__": j(FASES),
    "__VUELO__": str(M["vuelo_min"]),
    "__N__": f"{M['n']:,}".replace(",", "."),
    "__PCT__": str(round(M["pct_controlable_base"])),
    "__A50__": str(round(M["ahorro_salida_p50"])),
    "__A90__": str(round(M["ahorro_salida_p90"])),
    "__REPO__": REPO,
}
for k, v in rep.items():
    assert k in html, k
    html = html.replace(k, v)
assert "__" not in html.replace("__proto__", ""), [l for l in html.splitlines() if "__" in l][:3]
open(os.path.join(ROOT, "docs", "index.html"), "w", encoding="utf-8").write(html)
print("docs/index.html", len(html))
