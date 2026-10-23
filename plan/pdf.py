"""Arma plan/Plan_100_dias_Servicio_Medico.pdf (A4, para imprimir y llevar a la entrevista)."""
import html
import json
import os
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(__file__))
from contenido import ACTA, DMAIC, FASES, KPIS, RACI, RIESGOS, ROLES, TAREAS, hm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, "modelo", "resultados.json")))
b, mj = M["escenarios"]["base"], M["escenarios"]["mejorado"]
FD = "/usr/share/fonts/truetype/google-fonts/"
e = html.escape
NAVY, BLUE, PALE, ORANGE, INK2, MUTED, GRID = "#0B2545", "#1F5FA8", "#C9D8EC", "#D9731A", "#4A5568", "#8A94A6", "#E3E0D8"
FASE_COLOR = {"Escuchar y medir": "#8FB0DA", "Analizar y ordenar": BLUE, "Mejorar": ORANGE, "Sostener y rendir cuentas": NAVY}


def gantt_svg():
    W, L, rowh, top = 720, 300, 21, 26
    H = top + rowh * len(TAREAS) + 8
    x = lambda d: L + (d - 1) / 100 * (W - L - 6)
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Poppins" font-size="9">']
    for d0, lab in [(1, "Día 1"), (31, "31"), (61, "61"), (91, "91"), (100, "100")]:
        s.append(f'<line x1="{x(d0):.1f}" y1="{top - 6}" x2="{x(d0):.1f}" y2="{H - 6}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{x(d0):.1f}" y="{top - 10}" fill="{MUTED}" text-anchor="middle">{lab}</text>')
    for i, (t, fase, ini, dur, resp, ent) in enumerate(TAREAS):
        y = top + i * rowh
        s.append(f'<text x="0" y="{y + 13}" fill="{NAVY}">{e(t if len(t) < 58 else t[:56] + "…")}</text>')
        s.append(f'<rect x="{x(ini):.1f}" y="{y + 4}" width="{max(3, x(ini + dur) - x(ini)):.1f}" height="12" rx="2" fill="{FASE_COLOR[fase]}"/>')
    s.append("</svg>")
    return "".join(s)


def vsm_svg():
    tramos = [("deteccion", "Aviso"), ("llegada", "Llegada del equipo"), ("extraccion", "Extracción"),
              ("estabilizacion", "Estabilización"), ("coordinacion", "Coordinación"), ("preparacion", "Preparación")]
    col = {"deteccion": "#8FB0DA", "llegada": "#8FB0DA", "extraccion": "#8FB0DA", "estabilizacion": BLUE,
           "coordinacion": ORANGE, "preparacion": "#F2C9A5"}
    W, L = 720, 170
    sc = (W - L - 70) / 175
    s = [f'<svg viewBox="0 0 {W} 150" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Poppins" font-size="10">']
    for j, (k, lab, tot) in enumerate([("base", "Escenario de referencia", b["hitos"]["salida"]["p50"]),
                                       ("mejorado", "Con las dos mejoras", mj["hitos"]["salida"]["p50"])]):
        y = 18 + j * 52
        s.append(f'<text x="0" y="{y + 15}" fill="{NAVY}" font-weight="600">{lab}</text>')
        xx = L
        tm = M["escenarios"][k]["tramos_mediana"]
        for t, tl in tramos:
            v = tm[t]
            if k == "mejorado" and t in ("coordinacion", "preparacion"):  # en paralelo: solo cuenta lo que excede la estabilización
                v = max(0, tm["coordinacion"] + tm["preparacion"] - tm["estabilizacion"]) if t == "coordinacion" else 0
            w = v * sc
            if w > 0:
                s.append(f'<rect x="{xx:.1f}" y="{y}" width="{w:.1f}" height="22" fill="{col[t]}" stroke="#fff" stroke-width="1"/>')
                if w > 34:
                    s.append(f'<text x="{xx + w / 2:.1f}" y="{y + 15}" fill="{"#fff" if t in ("estabilizacion", "coordinacion") else NAVY}" text-anchor="middle" font-size="9">{round(v)}</text>')
            xx += w
        s.append(f'<text x="{xx + 6:.1f}" y="{y + 15}" fill="{NAVY}" font-weight="700">{hm(tot)}</text>')
    lx = L
    for t, tl in tramos:
        s.append(f'<rect x="{lx}" y="128" width="10" height="10" fill="{col[t]}"/><text x="{lx + 14}" y="137" fill="{INK2}" font-size="9">{tl}</text>')
        lx += 14 + len(tl) * 5.6 + 14
    s.append("</svg>")
    return "".join(s)


def matriz_riesgos():
    cells = {}
    for i, (r, p, im, _) in enumerate(RIESGOS, 1):
        cells.setdefault((p, im), []).append(str(i))
    s = ['<table class="mat"><tr><td class="ax" rowspan="6">Probabilidad</td>']
    for p in range(5, 0, -1):
        if p != 5:
            s.append("<tr>")
        s.append(f'<td class="lab">{p}</td>')
        for im in range(1, 6):
            sc = p * im
            bg = "#F6D8D4" if sc >= 15 else "#FBEBD3" if sc >= 8 else "#EEF3E9"
            s.append(f'<td style="background:{bg}">{" ".join(cells.get((p, im), []))}</td>')
        s.append("</tr>")
    s.append('<tr><td class="lab"></td>' + "".join(f'<td class="lab">{i}</td>' for i in range(1, 6)) + '</tr><tr><td></td><td></td><td colspan="5" class="ax">Impacto</td></tr></table>')
    return "".join(s)


raci_rows = "".join(f"<tr><td>{e(a)}</td>" + "".join(f'<td class="c{(" a" if l == "A" else "")}">{l}</td>' for l in ls) + "</tr>" for a, ls in RACI)
riesgos_rows = "".join(f'<tr><td class="n">{i}</td><td>{e(r)}</td><td class="c">{p}</td><td class="c">{im}</td><td class="c"><b>{p * im}</b></td><td>{e(resp)}</td></tr>'
                       for i, (r, p, im, resp) in enumerate(RIESGOS, 1))
kpi_rows = "".join(f'<tr><td><span class="tag">{e(k[0])}</span></td><td><b>{e(k[1])}</b><br><span class="mut">{e(k[2])}</span></td><td>{e(k[3])}</td><td><b>{e(k[4])}</b></td><td>{e(k[5])}</td><td class="mut">{e(k[6])}</td></tr>' for k in KPIS)


def dmaic_block(d):
    et = [("D", "Definir"), ("M", "Medir"), ("A", "Analizar"), ("I", "Mejorar"), ("C", "Controlar")]
    return f'<h3>{e(d["titulo"])}</h3><div class="dm">' + "".join(
        f'<div class="st{" hi" if k == "I" else ""}"><div class="k">{n}</div><p>{e(d[k])}</p></div>' for k, n in et) + "</div>"


fases_html = "".join(f'<div class="fase" style="border-top-color:{FASE_COLOR[f[1]]}"><div class="k">Días {f[0]} · {e(f[2])}</div><h4>{e(f[1])}</h4><p>{e(f[3])}</p></div>' for f in FASES)
li = lambda xs: "".join(f"<li>{e(x)}</li>" for x in xs)

PAGE = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Plan de 100 días</title><style>
@font-face{{font-family:Poppins;src:url(file://{FD}Poppins-Regular.ttf);font-weight:400}}
@font-face{{font-family:Poppins;src:url(file://{FD}Poppins-Medium.ttf);font-weight:500}}
@font-face{{font-family:Poppins;src:url(file://{FD}Poppins-Bold.ttf);font-weight:700}}
@page{{size:A4;margin:0}}
*{{box-sizing:border-box}}
body{{font-family:Poppins,sans-serif;color:{NAVY};font-size:9.6pt;line-height:1.5;margin:0}}
.page{{page-break-after:always;position:relative;height:297mm;overflow:hidden;padding:16mm 15mm}}
.page:last-child{{page-break-after:auto}}
.eyebrow{{font-size:7.8pt;letter-spacing:.12em;text-transform:uppercase;color:{ORANGE};font-weight:700}}
h1{{font-size:29pt;line-height:1.05;margin:8mm 0 4mm;font-weight:700}}
h2{{font-size:17pt;margin:1mm 0 4mm;font-weight:700}}
h3{{font-size:12pt;margin:6mm 0 2.5mm}}
h4{{font-size:11pt;margin:1mm 0 1mm}}
p{{margin:0 0 2mm;color:{INK2}}}
ul{{margin:0 0 3mm;padding-left:4.5mm;color:{INK2}}} li{{margin-bottom:1mm}}
ol{{margin:0 0 3mm;padding-left:5mm}} ol li{{margin-bottom:1.4mm;color:{NAVY}}}
.mut{{color:{MUTED};font-size:8.3pt}}
.cover{{background:{NAVY};color:#fff;padding:24mm 18mm}}
.cover h1{{color:#fff}} .cover p{{color:#C9D8EC;font-size:11pt;max-width:150mm}}
.big{{display:grid;grid-template-columns:repeat(3,1fr);gap:8mm;margin:16mm 0 14mm}}
.big .v{{font-size:30pt;font-weight:700;color:#fff;line-height:1}} .big .l{{font-size:9pt;color:#9FB3CC;margin-top:2mm}}
.note{{border-left:3px solid {ORANGE};padding:2mm 4mm;background:#13335C;color:#DCE6F4;font-size:8.6pt;margin-top:10mm}}
.author{{position:absolute;bottom:22mm;left:18mm;right:18mm;color:#9FB3CC;font-size:9pt}}
.author b{{color:#fff;font-size:13pt;display:block}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:8mm}}
.box{{border:1px solid {GRID};border-radius:2mm;padding:4mm 5mm}}
.fases{{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin-bottom:6mm}}
.fase{{border-top:3px solid;background:#F5F7FA;padding:3mm;border-radius:0 0 1.5mm 1.5mm}}
.fase p{{font-size:8.3pt;line-height:1.4}} .k{{font-size:7.4pt;color:{MUTED};text-transform:uppercase;letter-spacing:.06em}}
table{{border-collapse:collapse;width:100%;font-size:8.5pt}}
th{{text-align:left;font-size:7.4pt;text-transform:uppercase;letter-spacing:.06em;color:{MUTED};font-weight:500;border-bottom:1.5px solid {NAVY};padding:1.8mm 1.5mm}}
td{{border-bottom:1px solid {GRID};padding:1.8mm 1.5mm;vertical-align:top;color:{INK2}}}
td.c{{text-align:center;color:{NAVY}}} td.a{{background:#F6D9BF;font-weight:700}} td.n{{color:{MUTED}}}
.tag{{font-size:7.3pt;background:#E8EEF6;color:{NAVY};padding:.5mm 2mm;border-radius:5mm}}
.mat{{width:auto;border-collapse:separate;border-spacing:1mm;font-size:8.5pt}} .mat td{{width:11mm;height:9mm;text-align:center;border:0;color:{NAVY};font-weight:600;padding:0}}
.mat td.lab{{background:none;color:{MUTED};font-weight:400;width:5mm}} .mat td.ax{{color:{MUTED};font-weight:400;font-size:7.5pt}}
.mat td.ax[rowspan]{{writing-mode:vertical-rl;transform:rotate(180deg);width:4mm}}
.dm{{display:grid;grid-template-columns:1fr;gap:1.6mm}}
.st{{display:grid;grid-template-columns:22mm 1fr;gap:3mm;align-items:start;border-bottom:1px solid {GRID};padding-bottom:1.6mm}}
.st .k{{font-size:8.5pt;font-weight:700;color:{BLUE};text-transform:none;letter-spacing:0}} .st.hi .k{{color:{ORANGE}}}
.st p{{margin:0;font-size:8.8pt}}
.foot{{position:absolute;bottom:9mm;left:15mm;right:15mm;font-size:7.2pt;color:{MUTED};display:flex;justify-content:space-between}}
.legend span{{display:inline-flex;align-items:center;gap:1.5mm;margin-right:5mm;font-size:8pt;color:{INK2}}} .legend i{{width:3mm;height:3mm;display:inline-block;border-radius:.5mm}}
</style></head><body>

<section class="page cover">
  <div class="eyebrow" style="color:#F2A65A">Plan de 100 días · Team Lead, Servicios Médicos</div>
  <h1>Salir antes del sitio<br>con el paciente estable</h1>
  <p>Plan de trabajo para liderar el servicio médico de una mina subterránea remota en Santa Cruz: respuesta a emergencias, evaluaciones de salud, insumos críticos, brigadistas, bienestar y métricas.</p>
  <div class="big">
    <div><div class="v">{round(M['pct_controlable_base'])}%</div><div class="l">del tiempo hasta el hospital más cercano pasa dentro del sitio</div></div>
    <div><div class="v">−{round(M['ahorro_salida_p50'])} min</div><div class="l">en la mediana de salida del sitio con dos mejoras de proceso</div></div>
    <div><div class="v">−{round(M['ahorro_salida_p90'])} min</div><div class="l">en el percentil 90, que son los casos más complicados</div></div>
  </div>
  <p style="font-size:9.5pt">Cifras de un modelo Monte Carlo con {M['n']:,} simulaciones. Rutas reales de OpenStreetMap entre la ubicación pública de la mina y los hospitales de Perito Moreno, Las Heras, Caleta Olivia y Comodoro Rivadavia.</p>
  <div class="note">Los tiempos internos son supuestos y los indicadores del servicio son datos sintéticos. No hay información de ninguna empresa. El objetivo es mostrar el método: con datos reales del sitio, el mismo modelo se recalibra en una semana.</div>
  <div class="author"><b>Emiliano Pérez Alaniz</b>Enfermero Profesional · Salud ocupacional en minería en Santa Cruz · Lean Six Sigma y análisis de datos<br>Repositorio: github.com/mperezalaniz/servicio-medico-mineria-remota</div>
</section>

<section class="page">
  <div class="eyebrow">Acta del proyecto</div>
  <h2>{e(ACTA['nombre'])}</h2>
  <p style="font-size:10.5pt;color:{NAVY}">{e(ACTA['proposito'])}</p>
  <h3>Objetivos al día 100</h3><ol>{li(ACTA['objetivos'])}</ol>
  <div class="two">
    <div class="box"><h4>Alcance</h4><ul>{li(ACTA['alcance'])}</ul></div>
    <div class="box"><h4>Fuera de alcance</h4><ul>{li(ACTA['fuera_alcance'])}</ul><h4>Restricciones</h4><ul>{li(ACTA['restricciones'])}</ul></div>
  </div>
  <div class="foot"><span>Plan de 100 días · Team Lead, Servicios Médicos</span><span>2</span></div>
</section>

<section class="page">
  <div class="eyebrow">Cronograma</div>
  <h2>Cuatro fases, una por etapa de DMAIC</h2>
  <div class="fases">{fases_html}</div>
  <div class="legend" style="margin-bottom:2mm">{"".join(f'<span><i style="background:{c}"></i>{e(f)}</span>' for f, c in FASE_COLOR.items())}</div>
  {gantt_svg()}
  <p class="mut" style="margin-top:3mm">El Excel del repositorio tiene el mismo cronograma con responsables y entregables. Si se cambian inicio o duración, el Gantt se recalcula solo.</p>
  <div class="foot"><span>Plan de 100 días · Team Lead, Servicios Médicos</span><span>3</span></div>
</section>

<section class="page">
  <div class="eyebrow">Roles</div>
  <h2>Quién hace qué</h2>
  <table><tr><th style='width:42mm'>Actividad</th>{"".join(f"<th style='text-align:center'>{e(r)}</th>" for r in ROLES)}</tr>{raci_rows}</table>
  <p class="mut" style="margin-top:2mm">R hace · A responde por el resultado (una sola por fila) · C se consulta · I se informa</p>
  <div class="eyebrow" style="margin-top:9mm">Respuesta a emergencias</div>
  <h2>Dónde se va el tiempo hasta que sale la ambulancia (mediana, minutos)</h2>
  {vsm_svg()}
  <p>Con la derivación coordinada en paralelo, la espera de la coordinación queda casi entera dentro del tiempo de estabilización. Sin cambiar a nadie de puesto y sin comprar equipos.</p>
  <div class="foot"><span>Plan de 100 días · Team Lead, Servicios Médicos</span><span>4</span></div>
</section>

<section class="page">
  <div class="eyebrow">Riesgos</div>
  <h2>Qué puede salir mal</h2>
  <div style="display:grid;grid-template-columns:1fr;gap:6mm;align-items:start">
    <div>{matriz_riesgos()}</div>
    <table><tr><th>#</th><th>Riesgo</th><th>P</th><th>I</th><th>P×I</th><th>Respuesta</th></tr>{riesgos_rows}</table>
  </div>
    <div class="foot"><span>Plan de 100 días · Team Lead, Servicios Médicos</span><span>5</span></div>
</section>

<section class="page">
  <div class="eyebrow">Indicadores</div>
  <h2>Qué se mide y a dónde se quiere llegar</h2>
  <table><tr><th>Dimensión</th><th>Indicador</th><th>Línea base</th><th>Meta día 100</th><th>Frecuencia</th><th>Origen</th></tr>{kpi_rows}</table>
  <p class="mut" style="margin-top:3mm">Modelo: modelo Monte Carlo del repositorio. Sintético: datos de demostración del tablero. A medir: se toma en los primeros 30 días.</p>
  <div class="foot"><span>Plan de 100 días · Team Lead, Servicios Médicos</span><span>6</span></div>
</section>

<section class="page">
  <div class="eyebrow">Mejora continua</div>
  <h2>Dos proyectos DMAIC para los primeros 100 días</h2>
  {dmaic_block(DMAIC[0])}
  {dmaic_block(DMAIC[1])}
  <h3>Método y fuentes</h3>
  <p class="mut">Ubicación de la mina: artículo "Cerro Negro mine" de Wikipedia. Hospitales y rutas: OpenStreetMap (Nominatim y OSRM), consulta del 23/10/2026. Los tiempos de OSRM se ajustan con un factor de 0,65 a 1,0 para cubrir la referencia de unas dos horas hasta la localidad más cercana del aviso público del puesto. Tiempos internos, probabilidades y datos del servicio: supuestos y datos sintéticos documentados en el repositorio.</p>
  <div class="foot"><span>Plan de 100 días · Team Lead, Servicios Médicos</span><span>7</span></div>
</section>
</body></html>"""

out_html = os.path.join(ROOT, "plan", "plan.html")
open(out_html, "w", encoding="utf-8").write(PAGE)
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page()
    pg.goto("file://" + out_html)
    pg.wait_for_timeout(400)
    pg.pdf(path=os.path.join(ROOT, "plan", "Plan_100_dias_Servicio_Medico.pdf"), format="A4", print_background=True,
           margin=dict(top="0", bottom="0", left="0", right="0"))
    br.close()
print("ok")
