"""Carrusel LinkedIn (1080x1350) del proyecto. Todas las cifras salen de modelo/resultados.json y tablero/tablero.json.
Uso: python docs/carrusel.py  ->  docs/img/slide_XX.png y docs/Carrusel_Servicio_Medico_Mina_Remota.pdf
"""
import json
import os

import img2pdf
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle

FD = "/usr/share/fonts/truetype/google-fonts/"
for f in ["Poppins-Regular.ttf", "Poppins-Medium.ttf", "Poppins-Bold.ttf"]:
    if os.path.exists(FD + f):
        fm.fontManager.addfont(FD + f)
plt.rcParams["font.family"] = "Poppins"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "img")
os.makedirs(OUT, exist_ok=True)
BG, NAVY, INK2, MUTED, GRID = "#F6F4EF", "#0B2545", "#4A5568", "#8A94A6", "#E3E0D8"
BLUE, ORANGE, PALEBLUE, MIDBLUE, PALEORANGE, RED = "#1F5FA8", "#D9731A", "#C9D8EC", "#8FB0DA", "#F2C9A5", "#C0392B"
AUTHOR = "Emiliano Pérez Alaniz"
SOURCE = "Rutas: OpenStreetMap/OSRM · Tiempos internos supuestos · Tablero sintético"
N = 9

M = json.load(open(os.path.join(ROOT, "modelo", "resultados.json")))
T = json.load(open(os.path.join(ROOT, "tablero", "tablero.json")))
GEO = json.load(open(os.path.join(ROOT, "data", "geografia.json")))
cen = pd.read_csv(os.path.join(ROOT, "data", "centros_derivacion.csv")).set_index("id")
rut = pd.read_csv(os.path.join(ROOT, "data", "rutas_osrm.csv")).set_index("destino")
E = M["escenarios"]
b, mj = E["base"], E["mejorado"]


def hm(m):
    h, r = divmod(int(round(m)), 60)
    return f"{h} h {r:02d}" if h else f"{r} min"


def f1(v, d=1):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def canvas(bg=BG):
    fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
    fig.patch.set_facecolor(bg)
    return fig


def header(fig, kicker, title, dark=False):
    fig.text(0.07, 0.935, kicker.upper(), fontsize=17, color="#F2A65A" if dark else ORANGE, weight="bold")
    fig.text(0.07, 0.905, title, fontsize=36, color="white" if dark else NAVY, weight="bold", va="top", linespacing=1.15)


def footer(fig, n, dark=False):
    c = "#9FB3CC" if dark else MUTED
    fig.text(0.07, 0.035, f"{AUTHOR}  ·  {SOURCE}", fontsize=11, color=c)
    fig.text(0.93, 0.035, f"{n}/{N}", fontsize=13, color=c, ha="right")
    if n < N:
        fig.text(0.93, 0.065, "desliza  ›", fontsize=13, color="#F2A65A" if dark else ORANGE, ha="right", weight="medium")


def subtitle(fig, text, y=0.765):
    fig.text(0.10, y, text, fontsize=15, color=INK2)


def takeaway(fig, text, y=0.14):
    fig.patches.append(FancyBboxPatch((0.07, y - 0.04), 0.86, 0.095, boxstyle="round,pad=0.008,rounding_size=0.015",
                                      transform=fig.transFigure, fc="white", ec=GRID, lw=1.2))
    fig.patches.append(FancyBboxPatch((0.07, y - 0.04), 0.010, 0.095, boxstyle="square,pad=0",
                                      transform=fig.transFigure, fc=ORANGE, ec="none"))
    fig.text(0.10, y + 0.008, text, fontsize=16.5, color=NAVY, va="center", linespacing=1.45)


def clean(ax, grid="y"):
    ax.set_facecolor(BG)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=14, length=0)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=1)
    ax.set_axisbelow(True)


paths = []


def save(fig, n):
    p = os.path.join(OUT, f"slide_{n:02d}.png")
    fig.savefig(p, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    paths.append(p)


# 1 PORTADA -------------------------------------------------------------------------------
fig = canvas(NAVY)
fig.text(0.07, 0.87, "LEAN SIX SIGMA · SALUD OCUPACIONAL · MINERÍA", fontsize=17, color="#F2A65A", weight="bold")
fig.text(0.07, 0.83, "En una mina remota,\nla hora de oro se\njuega dentro\ndel sitio.", fontsize=56, color="white",
         weight="bold", va="top", linespacing=1.05)
fig.text(0.07, 0.47, f"Simulé {f1(M['n'], 0)} emergencias graves en una mina subterránea\nde Santa Cruz para ver dónde se va el tiempo.",
         fontsize=20, color=PALEBLUE, va="top", linespacing=1.35)
for i, (v, l) in enumerate([(f"{round(M['pct_controlable_base'])}%", "del tiempo hasta el\nhospital pasa en el sitio"),
                            (f"−{round(M['ahorro_salida_p50'])} min", "en la mediana con\ndos mejoras de proceso"),
                            (f"{round(b['pct_alta_6h'])}% a {round(mj['pct_alta_6h'])}%", "llega a alta complejidad\nen menos de 6 horas")]):
    x = 0.07 + i * 0.30
    fig.text(x, 0.30, v, fontsize=36, color="white", weight="bold")
    fig.text(x, 0.285, l, fontsize=14.5, color="#9FB3CC", va="top", linespacing=1.3)
fig.text(0.07, 0.17, "Python · Monte Carlo · OpenStreetMap · DMAIC · Plan de proyecto", fontsize=15, color="#9FB3CC")
fig.text(0.07, 0.11, AUTHOR, fontsize=22, color="white", weight="bold")
fig.text(0.07, 0.085, "Enfermero Profesional · Salud ocupacional en minería · Datos", fontsize=15, color="#9FB3CC")
fig.text(0.93, 0.065, "desliza  ›", fontsize=15, color="#F2A65A", ha="right", weight="medium")
save(fig, 1)

# 2 MAPA ------------------------------------------------------------------------------------
fig = canvas()
header(fig, "El punto de partida", "El hospital más cercano,\na dos o tres horas por ruta")
ax = fig.add_axes([0.07, 0.25, 0.86, 0.52])
k = np.cos(np.radians(46.5))
ax.set_facecolor(BG)
ax.add_patch(Polygon([(x * k, y) for x, y in GEO["santa_cruz"]], closed=True, fc="#E7E3DA", ec="#CFC9BC", lw=1.2))
col = {"PM": MIDBLUE, "LH": BLUE, "CO": ORANGE, "CR": RED}
for idd in ["CR", "CO", "PM", "LH"]:
    pts = np.array(GEO["rutas"][idd])
    ax.plot(pts[:, 0] * k, pts[:, 1], color=col[idd], lw=3.2, solid_capstyle="round")
for idd, r in cen.iterrows():
    ax.scatter(r.lon * k, r.lat, s=130, color=col[idd], edgecolor=BG, lw=2, zorder=5)
    lab = f"{r.localidad}\n{hm(rut.loc[idd, 'min_osrm'] * 0.65)} a {hm(rut.loc[idd, 'min_osrm'])}"
    dx, ha = (0.06, "left") if idd == "PM" else (-0.06, "right")
    ax.text(r.lon * k + dx, r.lat + 0.05, lab, fontsize=13, color=NAVY, ha=ha, va="bottom", weight="medium", linespacing=1.25)
ax.scatter(GEO["mina"]["lon"] * k, GEO["mina"]["lat"], s=260, marker="D", color=NAVY, edgecolor=BG, lw=2, zorder=6)
ax.text(GEO["mina"]["lon"] * k, GEO["mina"]["lat"] - 0.09, "Mina", fontsize=15, color=NAVY, ha="center", va="top", weight="bold")
ax.text(-69.4 * k, -45.78, "CHUBUT", fontsize=12, color=MUTED)
ax.set_xlim(-71.35 * k, -66.9 * k)
ax.set_ylim(-47.3, -45.6)
ax.set_aspect("equal")
ax.axis("off")
subtitle(fig, "Rutas reales desde la ubicación pública de la mina (OpenStreetMap / OSRM, ajustadas)", y=0.78)
takeaway(fig, f"El hospital de Las Heras queda a {f1(rut.loc['LH', 'km_ruta'], 0)} km y Comodoro Rivadavia a {f1(rut.loc['CR', 'km_ruta'], 0)} km.\n"
              "La ruta no se puede acortar. Lo que pasa antes de salir, sí.")
footer(fig, 2)
save(fig, 2)

# 3 MÉTODO ------------------------------------------------------------------------------------
fig = canvas()
header(fig, "Método", "Qué es real, qué es supuesto\ny qué es sintético")
items = [("Real", "Ubicación de la mina, 4 hospitales de derivación y\ntiempos de ruta por OpenStreetMap (OSRM)."),
         ("Supuesto", "Tiempos de cada tramo dentro del sitio: aviso, llegada,\nextracción, estabilización, coordinación y salida."),
         ("Modelo", f"Monte Carlo: {f1(M['n'], 0)} casos por escenario, con distribuciones\ntriangulares y semilla fija. Código abierto en GitHub."),
         ("Sintético", "Indicadores del servicio médico de 52 semanas para\nmostrar el tablero. No son datos de ninguna empresa.")]
for i, (t, d) in enumerate(items):
    y = 0.70 - i * 0.145
    fig.patches.append(FancyBboxPatch((0.07, y - 0.055), 0.86, 0.12, boxstyle="round,pad=0.006,rounding_size=0.015",
                                      transform=fig.transFigure, fc="white", ec=GRID, lw=1.2))
    fig.patches.append(FancyBboxPatch((0.07, y - 0.055), 0.012, 0.12, boxstyle="square,pad=0", transform=fig.transFigure,
                                      fc=[BLUE, MUTED, NAVY, ORANGE][i], ec="none"))
    fig.text(0.11, y + 0.03, t, fontsize=21, color=NAVY, weight="bold", va="center")
    fig.text(0.11, y - 0.016, d, fontsize=14.5, color=INK2, va="center", linespacing=1.35)
footer(fig, 3)
save(fig, 3)

# 4 DÓNDE SE VA EL TIEMPO ---------------------------------------------------------------------
fig = canvas()
header(fig, "Hallazgo 1", "Casi la mitad del tiempo\npasa antes de salir")
ax = fig.add_axes([0.07, 0.34, 0.86, 0.32])
ax.set_facecolor(BG)
tr = b["tramos_mediana"]
seq = [("deteccion", "Aviso", MIDBLUE), ("llegada", "Llegada", MIDBLUE), ("extraccion", "Extracción", MIDBLUE),
       ("estabilizacion", "Estabilización", BLUE), ("coordinacion", "Coordinación", ORANGE), ("preparacion", "Prep.", PALEORANGE)]
tot = sum(tr[k] for k, _, _ in seq)
fz = b["hitos"]["salida"]["p50"] / tot
x0 = 0
for k_, lab, c in seq:
    w = tr[k_] * fz
    ax.barh(1, w, left=x0, color=c, height=0.5, edgecolor=BG, lw=2)
    if w > 14:
        ax.text(x0 + w / 2, 1, f"{round(w)}", ha="center", va="center", fontsize=14, color="white" if c in (BLUE, ORANGE) else NAVY, weight="bold")
    x0 += w
ruta = b["hitos"]["hosp_cercano"]["p50"] - b["hitos"]["salida"]["p50"]
ax.barh(1, ruta, left=x0, color="#DCD8CE", height=0.5, edgecolor=BG, lw=2)
ax.text(x0 + ruta / 2, 1, f"Ruta a Las Heras  {hm(ruta)}", ha="center", va="center", fontsize=14, color=NAVY)
ax.axvline(x0, color=NAVY, lw=1.5, ls=(0, (3, 3)))
ax.text(x0, 0.45, f"Sale la ambulancia\n{hm(x0)}", ha="center", va="top", fontsize=14, color=NAVY, weight="bold")
ax.text(x0 + ruta, 0.45, f"Hospital\n{hm(x0 + ruta)}", ha="right", va="top", fontsize=14, color=NAVY, weight="bold")
ax.set_xlim(0, x0 + ruta + 3)
ax.set_ylim(-0.3, 1.9)
ax.axis("off")
for i, (lab, c) in enumerate([("Aviso, llegada y extracción", MIDBLUE), ("Estabilización", BLUE), ("Coordinación de la derivación", ORANGE), ("Preparación", PALEORANGE), ("Ruta", "#DCD8CE")]):
    xx, yy = 0.10 + (i % 3) * 0.29, 0.70 - (i // 3) * 0.03
    fig.patches.append(Rectangle((xx, yy), 0.018, 0.013, transform=fig.transFigure, fc=c, ec="none"))
    fig.text(xx + 0.026, yy + 0.0065, lab, fontsize=13, color=INK2, va="center")
subtitle(fig, "Caso típico, escenario de referencia: minutos de cada tramo desde el aviso", y=0.77)
takeaway(fig, f"El {round(M['pct_controlable_base'])}% del tiempo hasta el hospital más cercano pasa dentro del sitio.\n"
              f"La coordinación de la derivación es la espera más larga: {round(tr['coordinacion'])} min de mediana.", y=0.2)
footer(fig, 4)
save(fig, 4)

# 5 COORDINACIÓN EN PARALELO ------------------------------------------------------------------
fig = canvas()
header(fig, "Hallazgo 2", "Dos cambios de proceso\nahorran una hora")
ax = fig.add_axes([0.10, 0.30, 0.83, 0.43])
clean(ax)
bins = np.arange(0, 300, 10)
hb, hmj = np.array(b["hist_salida"][:30]) / M["n"] * 100, np.array(mj["hist_salida"][:30]) / M["n"] * 100
ax.bar(bins + 5, hb, width=9, color="#D3CEC3", label="Escenario de referencia")
ax.bar(bins + 5, hmj, width=5, color=BLUE, label="Con las dos mejoras")
top = max(hb.max(), hmj.max())
for v, c, l, dx, ha in [(b["hitos"]["salida"]["p50"], MUTED, "referencia", 4, "left"), (mj["hitos"]["salida"]["p50"], BLUE, "con mejoras", -4, "right")]:
    ax.axvline(v, color=c, lw=1.6, ls=(0, (3, 3)))
    ax.text(v + dx, top * 1.08, f"mediana {l}\n{hm(v)}", fontsize=13, color=NAVY if c == BLUE else INK2, va="top", ha=ha)
ax.set_xticks([0, 60, 120, 180, 240])
ax.set_xticklabels(["", "1 h", "2 h", "3 h", "4 h"])
ax.set_ylim(0, top * 1.12)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f1(v, 0) + "%"))
ax.set_xlim(0, 270)
ax.legend(frameon=False, fontsize=13.5, loc="center right")
subtitle(fig, f"% de casos según cuándo sale la ambulancia del sitio ({f1(M['n'], 0)} simulaciones por escenario)")
takeaway(fig, f"Derivación preacordada y coordinada mientras se estabiliza, más brigadistas:\n"
              f"{round(M['ahorro_salida_p50'])} min menos en la mediana y {round(M['ahorro_salida_p90'])} min menos en el P90. Sin comprar equipos.")
footer(fig, 5)
save(fig, 5)

# 6 PRIMER CONTACTO Y ALTA COMPLEJIDAD --------------------------------------------------------
fig = canvas()
header(fig, "Hallazgo 3", "Primeros 10 minutos y\nprimeras 6 horas")
for j, (titulo, vals, fmt, nota) in enumerate([
        ("Primer contacto con el paciente (mediana)", [b["hitos"]["primer_contacto"]["p50"], mj["hitos"]["primer_contacto"]["p50"]], lambda v: hm(v),
         "Brigadistas en cada frente bajo mina"),
        ("Casos que llegan a alta complejidad en 6 h", [b["pct_alta_6h"], mj["pct_alta_6h"]], lambda v: f"{round(v)}%",
         "Por ruta a Comodoro o con avión desde Perito Moreno")]):
    ax = fig.add_axes([0.27, 0.50 - j * 0.27, 0.63, 0.15])
    clean(ax, grid=None)
    ax.barh([1, 0], vals, color=["#D3CEC3", BLUE], height=0.62)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.02, 1 - i, fmt(v), va="center", fontsize=22, color=NAVY, weight="bold")
    ax.set_yticks([1, 0])
    ax.set_yticklabels(["Referencia", "Con mejoras"], fontsize=14)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.set_xlim(0, max(vals) * 1.25)
    fig.text(0.10, 0.69 - j * 0.27, titulo, fontsize=18, color=NAVY, weight="bold")
    fig.text(0.10, 0.665 - j * 0.27, nota, fontsize=14, color=INK2)
takeaway(fig, "El soporte vital avanzado sigue tardando lo que tarda el equipo médico en llegar.\n"
              "Lo que cambia es que alguien capacitado atiende al paciente en minutos.")
footer(fig, 6)
save(fig, 6)

# 7 TABLERO SINTÉTICO --------------------------------------------------------------------------
fig = canvas()
header(fig, "Controlar", "El tablero que miraría\ncada lunes")
fig.text(0.07, 0.80, "DATOS SINTÉTICOS · 52 SEMANAS · CAMPAMENTO DE ~820 PERSONAS", fontsize=12.5, color=ORANGE, weight="bold")
K = T["kpi"]
for i, (v, l) in enumerate([(f"{f1(K['cobertura_examenes_ini'])}% a {f1(K['cobertura_examenes'])}%", "exámenes periódicos al día"),
                            (f"{f1(K['brigadistas_ini'])}% a {f1(K['brigadistas_vigentes'])}%", "brigadistas certificados"),
                            (f"{K['quiebres_eventos_antes']} a {K['quiebres_eventos_despues']}", "días-ítem sin stock crítico")]):
    x = 0.07 + i * 0.30
    fig.text(x, 0.745, v, fontsize=23, color=NAVY, weight="bold")
    fig.text(x, 0.725, l, fontsize=13, color=INK2, va="top")
ax = fig.add_axes([0.10, 0.27, 0.83, 0.37])
clean(ax)
S = pd.DataFrame(T["semanal"])
S["s"] = pd.to_datetime(S.s)
out = S.s.astype(str).str[:10].isin(T["fuera"])
ax.plot(S.s, S.t, color=BLUE, lw=2)
ax.step(S.s, S.lcs, color=RED, lw=1.2, ls=(0, (4, 3)), where="mid")
ax.axhline(T["ubar"], color=NAVY, lw=1.2)
ax.scatter(S.s[out], S.t[out], color=RED, s=60, zorder=5, edgecolor=BG, lw=1.5)
br = S[S.s == pd.Timestamp("2026-03-15")]
ax.annotate("brote digestivo\n(simulado)", (br.s.iloc[0], br.t.iloc[0]), xytext=(-110, 10), textcoords="offset points", fontsize=12.5,
            color=NAVY, arrowprops=dict(arrowstyle="-", color=MUTED))
ax.text(pd.Timestamp("2026-07-20"), S.t.max() + 1.2, "invierno", fontsize=12.5, color=NAVY, ha="center")
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
tk = pd.to_datetime(["2025-11-01", "2026-01-01", "2026-03-01", "2026-05-01", "2026-07-01", "2026-09-01"])
ax.set_xticks(tk)
ax.set_xticklabels([f"{MESES[t.month - 1]} {str(t.year)[2:]}" for t in tk])
ax.set_ylim(28, S.t.max() + 3)
subtitle(fig, "Carta U: consultas por 1.000 personas-día, con límites de control", y=0.665)
takeaway(fig, "La carta marca el brote en la misma semana y separa el invierno, que se planifica,\n"
              "de lo que hay que investigar. Mínimos de stock recalculados con la demora real.")
footer(fig, 7)
save(fig, 7)

# 8 PLAN DE 100 DÍAS ----------------------------------------------------------------------------
fig = canvas()
header(fig, "Plan de proyecto", "Plan de 100 días\npara liderar el servicio")
fases = [("1 a 30", "Escuchar y medir", "Uno a uno con el equipo,\nprotocolos, línea base,\nsimulacro cronometrado", MIDBLUE),
         ("31 a 60", "Analizar y ordenar", "Causas raíz, derivación\npreacordada, kanban,\nagenda de exámenes", BLUE),
         ("61 a 90", "Mejorar", "Simulacros mensuales,\nbrigadistas bajo mina,\npiloto de bienestar", ORANGE),
         ("91 a 100", "Sostener", "Cartas de control,\nprocedimientos e\ninforme de resultados", NAVY)]
for i, (d, t, desc, c) in enumerate(fases):
    x = 0.07 + i * 0.218
    fig.patches.append(Rectangle((x, 0.50), 0.2, 0.012, transform=fig.transFigure, fc=c, ec="none"))
    fig.patches.append(Rectangle((x, 0.30), 0.2, 0.2, transform=fig.transFigure, fc="white", ec=GRID, lw=1))
    fig.text(x + 0.012, 0.48, f"DÍAS {d}", fontsize=11.5, color=MUTED, va="top", weight="medium")
    fig.text(x + 0.012, 0.455, t, fontsize=16, color=NAVY, va="top", weight="bold")
    fig.text(x + 0.012, 0.415, desc, fontsize=12, color=INK2, va="top", linespacing=1.4)
fig.text(0.07, 0.72, "Acta del proyecto · Cronograma con Gantt · Matriz RACI\nRegistro de riesgos · Árbol de indicadores · 2 proyectos DMAIC",
         fontsize=17, color=NAVY, va="top", linespacing=1.6)
fig.text(0.07, 0.62, "En PDF para imprimir y en Excel con fórmulas, en el repositorio.", fontsize=14.5, color=INK2)
takeaway(fig, "Metas al día 100: salida del sitio en menos de 1 h 50 en el P90, 97% de exámenes\n"
              "al día, 90% de brigadistas vigentes y cero quiebres de insumos críticos.", y=0.18)
footer(fig, 8)
save(fig, 8)

# 9 CIERRE ---------------------------------------------------------------------------------------
fig = canvas(NAVY)
fig.text(0.07, 0.90, "CONCLUSIÓN", fontsize=18, color="#F2A65A", weight="bold")
fig.text(0.07, 0.87, "La distancia no se elige.\nCómo se trabaja en\nel sitio, sí.", fontsize=42, color="white",
         weight="bold", va="top", linespacing=1.12)
pts = [f"Casi la mitad del tiempo hasta el hospital pasa dentro del sitio ({round(M['pct_controlable_base'])}%).",
       f"Derivación en paralelo y brigadistas: la ambulancia sale {round(M['ahorro_salida_p50'])} min antes.",
       f"Con brigadistas, el primer contacto baja de {hm(b['hitos']['primer_contacto']['p50'])} a {hm(mj['hitos']['primer_contacto']['p50'])}.",
       "Un tablero semanal y cartas de control sostienen la mejora."]
for i, t in enumerate(pts):
    y = 0.62 - i * 0.065
    fig.text(0.07, y, "›", fontsize=24, color="#F2A65A", weight="bold", va="center")
    fig.text(0.11, y, t, fontsize=16, color=PALEBLUE, va="center")
fig.text(0.07, 0.33, "Escenario hipotético: los tiempos internos son supuestos y el tablero usa datos sintéticos.\n"
                     "Con registros reales de simulacros y eventos, el modelo se recalibra en una semana.",
         fontsize=13, color="#9FB3CC", va="top", linespacing=1.45)
fig.text(0.07, 0.22, "Trabajé cinco años en salud ocupacional en minería en Santa Cruz.\n¿Cómo lo resolvieron en tu operación?",
         fontsize=19, color="white", weight="medium", va="top", linespacing=1.35)
fig.text(0.07, 0.085, AUTHOR, fontsize=19, color="white", weight="bold")
fig.text(0.07, 0.062, "Simulador, código y plan: github.com/mperezalaniz/servicio-medico-mineria-remota", fontsize=12.5, color="#9FB3CC")
fig.text(0.93, 0.035, f"{N}/{N}", fontsize=13, color="#9FB3CC", ha="right")
save(fig, 9)

pdf = os.path.join(ROOT, "docs", "Carrusel_Servicio_Medico_Mina_Remota.pdf")
with open(pdf, "wb") as f:
    f.write(img2pdf.convert(paths))
print(pdf)
