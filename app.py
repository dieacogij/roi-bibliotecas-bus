"""Dashboard ROI de bibliotecas universitarias (réplica del informe Power BI).

Ejecutar en local:  streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / "data"

# Paleta institucional de la Universidad de Sevilla
RED, YELLOW, GRAY, STEEL, TEAL, LINE = "#A40133", "#F9B905", "#3C3C3B", "#65899E", "#009E93", "#E1E1DF"
YEAR_COLOR = {"2023": STEEL, "2024": RED}
INDICADORES = [
    "Coste Personal",
    "Coste Total",
    "Gasto Recursos Información",
    "ROI",
    "Valor Total Servicios Prestados",
]
IND_COLOR = dict(zip(INDICADORES, [GRAY, STEEL, YELLOW, TEAL, RED]))

st.set_page_config(page_title="ROI Bibliotecas", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    f"""
<style>
.block-container {{padding-top: 1.2rem; max-width: 1400px;}}
.hero {{background:{RED}; color:#fff; border-radius:10px; padding:22px 28px 18px; border-bottom:4px solid {YELLOW}; margin-bottom:1rem;}}
.hero .eyebrow {{font-size:.78rem; letter-spacing:.14em; text-transform:uppercase; font-weight:600; opacity:.85; margin:0 0 6px;}}
.hero h1 {{font-family: Georgia, 'Times New Roman', serif; font-weight:400; font-size:2.1rem; line-height:1.15; margin:0; padding:0; color:#fff;}}
.hero p.sub {{margin:6px 0 0; opacity:.9;}}
.intro {{background:#fff; border:1px solid {LINE}; border-left:5px solid {RED}; border-radius:10px; padding:16px 20px; margin-bottom:1rem; line-height:1.5;}}
.intro b {{color:{RED}; font-weight:600;}}
.kpi {{background:#fff; border:1px solid {LINE}; border-top:4px solid var(--k); border-radius:10px; padding:16px 18px; min-height:110px;
       display:flex; flex-direction:column; justify-content:flex-end;}}
.kpi .val {{font-family: Georgia, serif; font-size:2.3rem; line-height:1; color:{GRAY};}}
.kpi .val.blank {{font-family: inherit; font-size:1rem; color:#6c6c6a; padding-bottom:6px;}}
.kpi .lab {{font-size:.85rem; color:#6c6c6a; margin-top:2px;}}
.kpis {{display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:14px;}}
.formula {{background:#fff; border:1px solid {LINE}; border-radius:10px; padding:14px 18px; font-family: Georgia, serif; font-size:1.1rem;}}
h3 {{font-family: Georgia, serif; font-weight:600;}}
</style>
<div class="hero">
  <p class="eyebrow">Biblioteca de la Universidad de Sevilla</p>
  <h1>Retorno de la inversión en bibliotecas universitarias</h1>
  <p class="sub">ROI y ahorro por persona usuaria · 2023 y 2024 · UAH, UGR, BUS, UB, UV y UZ</p>
</div>
""",
    unsafe_allow_html=True,
)


# ---------- utilidades ----------
def es(n: float, d: int = 2) -> str:
    """Formato numérico español: coma decimal, punto de millares."""
    s = f"{n:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def auto(n: float) -> str:
    a = abs(n)
    if a >= 1e9:
        return es(n / 1e9, 1) + " mil mill."
    if a >= 1e6:
        return es(n / 1e6, 0 if a >= 1e7 else 1) + " mill."
    if a >= 1e3:
        return es(n / 1e3, 0 if a >= 1e5 else 1) + " mil"
    return es(n, 2)


def kpi(label: str, value: str, color: str, blank: bool = False) -> str:
    cls = "val blank" if blank else "val"
    return f'<div class="kpi" style="--k:{color}"><div class="{cls}">{value}</div><div class="lab">{label}</div></div>'


def style(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=GRAY, size=13),
        separators=",.",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        bargap=0.25,
    )
    fig.update_yaxes(gridcolor="#ECECEA", zeroline=False)
    fig.update_xaxes(showgrid=False)
    return fig


@st.cache_data
def load():
    ind = pd.read_csv(DATA / "indicadores.csv", dtype={"anio": str})
    svc = pd.read_csv(DATA / "servicios.csv")
    meta = pd.read_csv(DATA / "servicios_meta.csv").sort_values("servicio")
    return ind, svc, meta


ind, svc, meta = load()
BIBS = sorted(ind["biblioteca"].unique())

# ---------- filtros (barra lateral) ----------
with st.sidebar:
    st.header("Filtros")
    year = st.radio("Año", ["Todos", "2023", "2024"], horizontal=True)
    bibs = st.multiselect("Biblioteca", BIBS, placeholder="Todas")
    st.divider()
    servicios = st.multiselect("Servicio (pestaña Servicios per cápita)", list(meta["servicio"]), placeholder="Todos")
    st.divider()
    exacto = st.toggle(
        "ROI exacto (valor total ÷ coste total)",
        value=False,
        help="El informe Power BI original guarda el ROI redondeado a enteros. "
        "Activa esta opción para calcularlo sin redondeo.",
    )

if exacto:
    piv = ind.pivot_table(index=["biblioteca", "anio"], columns="indicador", values="valor").reset_index()
    piv["ROI"] = piv["Valor Total Servicios Prestados"] / piv["Coste Total"]
    ind = pd.concat(
        [ind[ind["indicador"] != "ROI"], piv[["biblioteca", "anio", "ROI"]].melt(
            id_vars=["biblioteca", "anio"], var_name="indicador", value_name="valor").assign(unidad="EUR por EUR")],
        ignore_index=True,
    )

tab_roi, tab_svc = st.tabs(["ROI", "Servicios per cápita"])

# =====================================================================
# Página 1: ROI
# =====================================================================
with tab_roi:
    st.markdown(
        """<div class="intro">El Retorno de la Inversión (ROI) en bibliotecas universitarias mide el valor generado por sus
servicios a partir del uso de la biblioteca (ahorro en adquisición de recursos, impacto en la investigación y docencia,
mejora en el acceso a la información, etc.) en relación con los recursos financieros invertidos. Además del componente
financiero, el ROI en bibliotecas también debe considerar su impacto social, académico y cultural, factores esenciales en
la educación superior.<br><br>
Un ROI <b>superior a 1</b> indica que la biblioteca genera un <b>beneficio económico superior a su coste</b>, mientras que
valores más altos reflejan un impacto aún mayor en la comunidad universitaria. Es decir, por <b>cada euro invertido</b> se
reporta de media un beneficio de <b>2,31 euros</b>.</div>""",
        unsafe_allow_html=True,
    )

    f = ind.copy()
    if year != "Todos":
        f = f[f["anio"] == year]
    if bibs:
        f = f[f["biblioteca"].isin(bibs)]
    roi = f[f["indicador"] == "ROI"]

    left, right = st.columns([1.55, 1], gap="large")

    with left:
        st.subheader("ROI medio por biblioteca")
        if roi.empty:
            st.info("Sin datos para el filtro elegido.")
        else:
            orden = roi.groupby("biblioteca")["valor"].sum().sort_values(ascending=False).index.tolist()
            fig = go.Figure()
            for y in sorted(roi["anio"].unique()):
                d = roi[roi["anio"] == y].set_index("biblioteca").reindex(orden)
                fig.add_bar(
                    x=orden, y=d["valor"], name=y, marker_color=YEAR_COLOR[y],
                    text=[es(v, 0 if float(v).is_integer() else 2) for v in d["valor"].fillna(0)],
                    textposition="outside", hovertemplate="%{x} · " + y + ": %{y:,.2f}<extra></extra>",
                )
            media = roi["valor"].mean()
            fig.add_hline(y=media, line_dash="dash", line_color=RED,
                          annotation_text=f"Media {es(media)}", annotation_position="top right",
                          annotation_font_color=RED)
            fig.update_layout(barmode="group")
            fig.update_yaxes(rangemode="tozero")
            st.plotly_chart(style(fig, 330), width='stretch')

        st.subheader("Costes y valor de los servicios")
        if f.empty:
            st.info("Sin datos para el filtro elegido.")
        else:
            fig = go.Figure()
            for i in INDICADORES:
                d = f[f["indicador"] == i].sort_values(["anio", "biblioteca"])
                fig.add_bar(x=[d["anio"], d["biblioteca"]], y=d["valor"], name=i, marker_color=IND_COLOR[i],
                            hovertemplate="%{x}<br>" + i + ": %{y:,.0f}<extra></extra>")
            fig.update_layout(barmode="stack")
            top = f.groupby(["anio", "biblioteca"])["valor"].sum().max()
            step = 25e6 if top > 5e7 else 10e6
            vals = [i * step for i in range(int(top // step) + 2)]
            fig.update_yaxes(tickvals=vals, ticktext=[auto(v) if v else "0" for v in vals])
            st.plotly_chart(style(fig, 380), width='stretch')

    with right:
        # Las tarjetas de ROI medio ignoran el filtro de año (igual que CALCULATE en el DAX original)
        base = ind[(ind["indicador"] == "ROI")]
        if bibs:
            base = base[base["biblioteca"].isin(bibs)]
        cards = ""
        for y in ("2023", "2024"):
            v = base[base["anio"] == y]["valor"].mean()
            blank = pd.isna(v)
            cards += kpi(f"ROI medio {y}", "Sin datos" if blank else es(v), YEAR_COLOR[y], blank)
        st.markdown(f'<div class="kpis">{cards}</div>', unsafe_allow_html=True)
        st.write("")
        st.subheader("Indicadores por año")
        tabla = f[["anio", "indicador"]].drop_duplicates().sort_values(["anio", "indicador"])
        tabla.columns = ["Año", "Indicador"]
        st.dataframe(tabla, hide_index=True, width='stretch', height=260)

# =====================================================================
# Página 2: Servicios per cápita
# =====================================================================
with tab_svc:
    sel = svc if not servicios else svc[svc["servicio"].isin(servicios)]
    uno = servicios[0] if len(servicios) == 1 else None
    left, right = st.columns([1.55, 1], gap="large")

    with left:
        st.subheader("Justificación")
        mj = meta if not servicios else meta[meta["servicio"].isin(servicios)]
        st.dataframe(mj[["justificacion"]].rename(columns={"justificacion": "Descripción del servicio"}),
                     hide_index=True, width='stretch', height=210)

        cards = kpi("Valor servicios en 2024 (mínimo)", auto(meta["valor_servicios_2024"].min()), STEEL)
        if uno:
            ve = meta.loc[meta["servicio"] == uno, "valor_estimado_2024"].iloc[0]
            cards += kpi("Valor estimado (€ por unidad)", es(ve), YELLOW)
        else:
            cards += kpi("Valor estimado (€ por unidad)", "Elige un servicio", YELLOW, True)
        ahorro = sel["v2024"].mean()
        cards += kpi("Ahorro por persona, 2024", "Sin datos" if pd.isna(ahorro) else es(ahorro), RED, pd.isna(ahorro))
        st.markdown(f'<div class="kpis">{cards}</div>', unsafe_allow_html=True)

        st.subheader("Ahorro del servicio por persona en bibliotecas EFQM")
        agg = sel.groupby("biblioteca")[["v2023", "v2024"]].sum(min_count=1).reindex(BIBS)
        agg = agg.sort_values("v2023", ascending=False, na_position="last")
        fig = go.Figure()
        for col, y in (("v2023", "2023"), ("v2024", "2024")):
            fig.add_bar(x=agg.index, y=agg[col], name=y, marker_color=YEAR_COLOR[y],
                        text=[es(v, 1 if v >= 100 else 2) if pd.notna(v) else "" for v in agg[col]],
                        textposition="outside", hovertemplate="%{x} · " + y + ": %{y:,.2f}<extra></extra>")
            m = agg[col].mean()
            if pd.notna(m):
                fig.add_hline(y=m, line_dash="dash", line_color=YEAR_COLOR[y],
                              annotation_text=f"Media {y}: {es(m, 1)}", annotation_position="top right",
                              annotation_font_color=YEAR_COLOR[y])
        fig.update_layout(barmode="group")
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(style(fig, 380), width='stretch')

    with right:
        st.subheader("Fórmula del servicio")
        txt = meta.loc[meta["servicio"] == uno, "formula"].iloc[0] if uno else "Seleccione un servicio"
        st.markdown(f'<div class="formula">{txt}</div>', unsafe_allow_html=True)
        st.caption("Selecciona un único servicio en la barra lateral para ver su fórmula y su valor estimado.")

st.caption("Reproducción interactiva del informe Power BI «27_02_POWER_BI_ROI». Datos en la carpeta data/.")
