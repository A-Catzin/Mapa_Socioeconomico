import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os, sys, json
import branca.colormap as cm

# ─── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Observatorio de Pobreza · México",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label { color: #8b949e !important; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }

/* Main */
.main .block-container { padding: 1.5rem 2rem; }

/* Header */
.obs-header {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 60%, #1a2332 100%);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.obs-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(88,166,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.obs-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    color: #e6edf3;
    margin: 0;
    line-height: 1.2;
}
.obs-subtitle {
    color: #8b949e;
    font-size: 0.85rem;
    margin-top: 0.3rem;
    font-weight: 300;
}
.obs-badge {
    display: inline-block;
    background: rgba(88,166,255,0.12);
    color: #58a6ff;
    border: 1px solid rgba(88,166,255,0.3);
    border-radius: 20px;
    padding: 0.15rem 0.7rem;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-right: 0.4rem;
    margin-top: 0.6rem;
    text-transform: uppercase;
}

/* KPI Cards */
.kpi-grid { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.kpi-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    flex: 1;
    min-width: 130px;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 0 0 10px 10px;
}
.kpi-card.red::after   { background: linear-gradient(90deg, #f85149, transparent); }
.kpi-card.amber::after { background: linear-gradient(90deg, #d29922, transparent); }
.kpi-card.green::after { background: linear-gradient(90deg, #3fb950, transparent); }
.kpi-card.blue::after  { background: linear-gradient(90deg, #58a6ff, transparent); }
.kpi-label { font-size: 0.68rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 1.8rem; color: #e6edf3; line-height: 1.1; margin-top: 0.2rem; }
.kpi-sub   { font-size: 0.72rem; color: #6e7681; margin-top: 0.1rem; }

/* Section titles */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    color: #e6edf3;
    margin: 0 0 0.8rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #21262d;
}

/* Correlation box */
.corr-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.corr-formula {
    font-family: 'DM Serif Display', serif;
    font-size: 1rem;
    color: #58a6ff;
    text-align: center;
    padding: 0.8rem;
    background: rgba(88,166,255,0.05);
    border-radius: 8px;
    border: 1px solid rgba(88,166,255,0.15);
    margin: 0.8rem 0;
    letter-spacing: 0.02em;
}
.corr-result {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.corr-r {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    line-height: 1;
}
.corr-interp { font-size: 0.82rem; color: #8b949e; flex: 1; line-height: 1.5; }

/* Source note */
.source-note {
    font-size: 0.68rem;
    color: #484f58;
    margin-top: 1rem;
    text-align: right;
}

/* Layer legend */
.legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.78rem;
    color: #8b949e;
    margin-bottom: 0.3rem;
}
.legend-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    csv = os.path.join(os.path.dirname(__file__), "municipios.csv")
    if not os.path.exists(csv):
        import subprocess
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "data_generator.py")])
    return pd.read_csv(csv)

@st.cache_data
def load_geojson():
    geo_path = os.path.join(os.path.dirname(__file__), "mexico_states.geojson")
    with open(geo_path, "r", encoding="utf-8") as f:
        return json.load(f)

df_full = load_data()
geo_states = load_geojson()

# Mapping: app state name → GeoJSON state_name
STATE_NAME_MAP = {
    "CDMX": "Distrito Federal",
    "Coahuila": "Coahuila de Zaragoza",
    "Michoacán": "Michoacán de Ocampo",
    "Veracruz": "Veracruz de Ignacio de la Llave",
}
# Reverse mapping: GeoJSON name → app name
GEO_TO_APP = {v: k for k, v in STATE_NAME_MAP.items()}
for feat in geo_states["features"]:
    geo_name = feat["properties"]["state_name"]
    if geo_name not in GEO_TO_APP:
        GEO_TO_APP[geo_name] = geo_name

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗂️ Filtros")
    st.markdown("---")

    estados_disp = ["Todos"] + sorted(df_full["estado"].unique().tolist())
    estado_sel = st.selectbox("Estado", estados_disp)

    decil_range = st.slider("Decil de ingreso", 1, 10, (1, 10))

    amai_opts = sorted(df_full["amai_2024"].unique().tolist())
    amai_sel = st.multiselect("Clasificación AMAI 2024", amai_opts, default=amai_opts)

    st.markdown("---")
    st.markdown("### 🗺️ Capas del Mapa")
    capa_pobreza    = st.toggle("Pobreza Multidimensional", value=True)
    capa_salarios   = st.toggle("Salarios Mínimos",         value=True)
    capa_escuelas   = st.toggle("Densidad Escolar",         value=True)
    capa_industrial = st.toggle("Zonas Industriales",       value=True)

    st.markdown("---")
    st.markdown("**Leyenda de colores**", unsafe_allow_html=False)
    leyenda = [
        ("#f85149", "Alta pobreza (≥60%)"),
        ("#d29922", "Pobreza media (30-60%)"),
        ("#3fb950", "Baja pobreza (<30%)"),
        ("#58a6ff", "Zona frontera norte"),
    ]
    for color, label in leyenda:
        st.markdown(
            f'<div class="legend-item"><div class="legend-dot" style="background:{color}"></div>{label}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown('<p style="font-size:0.7rem;color:#484f58;">TUP · Observatorio de Pobreza · 2026<br>Datos simulados basados en INEGI/CONEVAL</p>', unsafe_allow_html=True)

# ─── Filter data ──────────────────────────────────────────────────────────────
df = df_full.copy()
if estado_sel != "Todos":
    df = df[df["estado"] == estado_sel]
df = df[(df["decil_ingreso"] >= decil_range[0]) & (df["decil_ingreso"] <= decil_range[1])]
if amai_sel:
    df = df[df["amai_2024"].isin(amai_sel)]

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="obs-header">
  <p class="obs-title">Observatorio de Indicadores de Pobreza</p>
  <p class="obs-subtitle">Mapa Interactivo de Desigualdad y Productividad · México 2024</p>
  <span class="obs-badge">INEGI</span>
  <span class="obs-badge">CONEVAL</span>
  <span class="obs-badge">DENUE 2024</span>
  <span class="obs-badge">ENIGH 2022</span>
  <span class="obs-badge">CONASAMI</span>
</div>
""", unsafe_allow_html=True)

# ─── KPIs ─────────────────────────────────────────────────────────────────────
pob_total = df["poblacion"].sum()
pobreza_media = df["pobreza_multidim"].mean()
rezago_medio  = df["rezago_educativo"].mean()
sal_medio     = df["salario_minimo"].mean()

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card blue">
    <div class="kpi-label">Municipios</div>
    <div class="kpi-value">{len(df)}</div>
    <div class="kpi-sub">en selección</div>
  </div>
  <div class="kpi-card red">
    <div class="kpi-label">Pobreza Multidim.</div>
    <div class="kpi-value">{pobreza_media:.1f}%</div>
    <div class="kpi-sub">promedio municipal</div>
  </div>
  <div class="kpi-card amber">
    <div class="kpi-label">Rezago Educativo</div>
    <div class="kpi-value">{rezago_medio:.1f}%</div>
    <div class="kpi-sub">promedio municipal</div>
  </div>
  <div class="kpi-card green">
    <div class="kpi-label">Salario Promedio</div>
    <div class="kpi-value">${sal_medio:.0f}</div>
    <div class="kpi-sub">pesos / día</div>
  </div>
  <div class="kpi-card blue">
    <div class="kpi-label">Población Total</div>
    <div class="kpi-value">{pob_total/1_000_000:.1f}M</div>
    <div class="kpi-sub">habitantes</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Layout: Mapa + Correlación ───────────────────────────────────────────────
col_map, col_analysis = st.columns([3, 2], gap="medium")

# ── MAPA ──────────────────────────────────────────────────────────────────────
with col_map:
    st.markdown('<p class="section-title">🗺️ Mapa Multi-capa Interactivo</p>', unsafe_allow_html=True)

    if len(df) == 0:
        st.warning("No hay municipios con los filtros seleccionados.")
    else:
        center_lat = df["lat"].mean()
        center_lon = df["lon"].mean()
        zoom = 5 if estado_sel == "Todos" else 7

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles="CartoDB dark_matter",
            width="100%",
        )

        # ── Capa Coropleta de Estados ──────────────────────────────────
        # Aggregate poverty by state for the full dataset (not filtered)
        estado_agg = df_full.groupby("estado").agg(
            pobreza_media=("pobreza_multidim", "mean"),
            rezago_medio=("rezago_educativo", "mean"),
            poblacion_total=("poblacion", "sum"),
            municipios_count=("mun_id", "count"),
        ).reset_index()

        # Map app state names to GeoJSON names
        estado_agg["geo_name"] = estado_agg["estado"].map(
            lambda x: STATE_NAME_MAP.get(x, x)
        )

        # Build a dict: geo_name -> data
        state_data = {}
        for _, r in estado_agg.iterrows():
            state_data[r["geo_name"]] = {
                "pobreza": r["pobreza_media"],
                "rezago": r["rezago_medio"],
                "poblacion": r["poblacion_total"],
                "municipios": r["municipios_count"],
                "app_name": r["estado"],
            }

        # Color scale for poverty
        colormap = cm.LinearColormap(
            colors=["#1a9641", "#a6d96a", "#ffffbf", "#fdae61", "#d7191c"],
            vmin=0, vmax=80,
            caption="Pobreza Multidimensional (%)",
        )

        def style_function(feature):
            geo_name = feature["properties"]["state_name"]
            data = state_data.get(geo_name)
            if data:
                color = colormap(data["pobreza"])
                return {
                    "fillColor": color,
                    "color": "#e6edf3",
                    "weight": 1.2,
                    "dashArray": "",
                    "fillOpacity": 0.55,
                }
            else:
                return {
                    "fillColor": "#21262d",
                    "color": "#484f58",
                    "weight": 0.8,
                    "dashArray": "4",
                    "fillOpacity": 0.25,
                }

        def highlight_function(feature):
            return {
                "weight": 3,
                "color": "#58a6ff",
                "fillOpacity": 0.75,
            }

        # Create tooltip for each state
        geo_layer = folium.GeoJson(
            geo_states,
            name="Estados",
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.GeoJsonTooltip(
                fields=["state_name"],
                aliases=["Estado:"],
                style="""
                    background-color: #161b22;
                    color: #e6edf3;
                    font-family: 'DM Sans', sans-serif;
                    font-size: 12px;
                    border: 1px solid #21262d;
                    border-radius: 6px;
                    padding: 8px;
                """,
            ),
        )

        # Add custom popup with state data
        for feature in geo_layer.data["features"]:
            geo_name = feature["properties"]["state_name"]
            data = state_data.get(geo_name)
            app_name = GEO_TO_APP.get(geo_name, geo_name)
            if data:
                feature["properties"]["state_name"] = (
                    f"{app_name} · Pobreza: {data['pobreza']:.1f}% · "
                    f"Rezago: {data['rezago']:.1f}% · "
                    f"Pob: {data['poblacion']:,.0f}"
                )
            else:
                feature["properties"]["state_name"] = f"{app_name} · Sin datos"

        geo_layer.add_to(m)
        colormap.add_to(m)

        # ── Marcadores de municipios sobre los estados ────────────────
        for _, row in df.iterrows():
            # ── Capa Pobreza ──
            if capa_pobreza:
                pob = row["pobreza_multidim"]
                if pob >= 60:   color_p = "#f85149"
                elif pob >= 30: color_p = "#d29922"
                else:           color_p = "#3fb950"
                radius_p = 6 + pob / 12

                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=radius_p,
                    color=color_p,
                    fill=True,
                    fill_color=color_p,
                    fill_opacity=0.45,
                    weight=1.2,
                    tooltip=folium.Tooltip(
                        f"<b>{row['municipio']}</b><br>"
                        f"Pobreza: <b>{pob:.1f}%</b><br>"
                        f"AMAI: {row['amai_2024']}<br>"
                        f"Decil: {row['decil_ingreso']}"
                    ),
                ).add_to(m)

            # ── Capa Salarios ──
            if capa_salarios:
                sal_color = "#58a6ff" if row["zona_frontera"] else "#bc8cff"
                folium.CircleMarker(
                    location=[row["lat"] + 0.05, row["lon"] + 0.05],
                    radius=4,
                    color=sal_color,
                    fill=True,
                    fill_color=sal_color,
                    fill_opacity=0.6,
                    weight=0,
                    tooltip=folium.Tooltip(
                        f"<b>Salario</b><br>"
                        f"${row['salario_minimo']:.2f}/día<br>"
                        f"{'🔵 Zona Frontera Norte' if row['zona_frontera'] else '🟣 Resto del País'}"
                    ),
                ).add_to(m)

            # ── Capa Escuelas ──
            if capa_escuelas:
                esc = row["densidad_escolar"]
                esc_color = "#39d353" if esc >= 8 else ("#ffa657" if esc >= 5 else "#f85149")
                folium.RegularPolygonMarker(
                    location=[row["lat"] - 0.05, row["lon"]],
                    number_of_sides=4,
                    radius=4,
                    color=esc_color,
                    fill=True,
                    fill_color=esc_color,
                    fill_opacity=0.7,
                    weight=0,
                    tooltip=folium.Tooltip(
                        f"<b>Densidad Escolar</b><br>"
                        f"{esc:.1f} escuelas/10k hab<br>"
                        f"Rezago: {row['rezago_educativo']:.1f}%"
                    ),
                ).add_to(m)

            # ── Capa Industrial ──
            if capa_industrial:
                ind = row["densidad_industrial"]
                if ind > 40: ind_color = "#ff7b72"
                elif ind > 15: ind_color = "#ffa657"
                else: ind_color = "#484f58"
                folium.CircleMarker(
                    location=[row["lat"], row["lon"] - 0.05],
                    radius=3 + ind / 25,
                    color=ind_color,
                    fill=True,
                    fill_color=ind_color,
                    fill_opacity=0.5,
                    weight=0,
                    tooltip=folium.Tooltip(
                        f"<b>Densidad Industrial</b><br>"
                        f"{ind:.1f} unidades/km²<br>"
                        f"(DENUE 2024)"
                    ),
                ).add_to(m)

        # Layer control
        folium.LayerControl().add_to(m)
        st_folium(m, height=520, use_container_width=True, returned_objects=[])

# ── ANÁLISIS ──────────────────────────────────────────────────────────────────
with col_analysis:
    st.markdown('<p class="section-title">📐 Correlación Espacial</p>', unsafe_allow_html=True)

    if len(df) >= 5:
        x = df["densidad_industrial"].values
        y = df["rezago_educativo"].values
        r, p_val = stats.pearsonr(x, y)

        # Interpretación
        if abs(r) >= 0.7:   fuerza = "fuerte"
        elif abs(r) >= 0.4: fuerza = "moderada"
        else:               fuerza = "débil"
        direccion = "negativa" if r < 0 else "positiva"

        if p_val < 0.001: sig_txt = "p < 0.001 (altamente significativo)"
        elif p_val < 0.05: sig_txt = f"p = {p_val:.3f} (significativo)"
        else: sig_txt = f"p = {p_val:.3f} (no significativo)"

        r_color = "#3fb950" if r < -0.3 else ("#f85149" if r > 0.3 else "#d29922")

        st.markdown(f"""
        <div class="corr-box">
          <div style="font-size:0.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:0.08em;">
            Densidad Industrial → Rezago Educativo
          </div>
          <div class="corr-formula">
            r = Σ[(xᵢ−x̄)(yᵢ−ȳ)] / √[Σ(xᵢ−x̄)² · Σ(yᵢ−ȳ)²]
          </div>
          <div class="corr-result">
            <div class="corr-r" style="color:{r_color}">{r:.3f}</div>
            <div class="corr-interp">
              Correlación de Pearson <b style="color:{r_color}">{direccion} {fuerza}</b>.<br>
              A mayor densidad industrial, {"menor" if r < 0 else "mayor"} rezago educativo.<br>
              <span style="color:#484f58;font-size:0.7rem;">{sig_txt} · n={len(df)}</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Scatter plot
        fig_scatter = px.scatter(
            df,
            x="densidad_industrial",
            y="rezago_educativo",
            color="estado" if estado_sel == "Todos" else "pobreza_multidim",
            size="poblacion",
            size_max=25,
            hover_name="municipio",
            hover_data={"densidad_industrial": ":.1f", "rezago_educativo": ":.1f", "estado": True},
            trendline="ols",
            labels={
                "densidad_industrial": "Densidad Industrial (uds/km²)",
                "rezago_educativo": "Rezago Educativo (%)",
            },
            color_continuous_scale="RdYlGn_r" if estado_sel != "Todos" else None,
        )
        fig_scatter.update_layout(
            height=250,
            paper_bgcolor="#161b22",
            plot_bgcolor="#0d1117",
            font=dict(color="#8b949e", size=11),
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        fig_scatter.update_xaxes(gridcolor="#21262d", zeroline=False)
        fig_scatter.update_yaxes(gridcolor="#21262d", zeroline=False)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Selecciona más municipios para calcular la correlación (mínimo 5).")

    # ── Distribución de pobreza ──
    st.markdown('<p class="section-title" style="margin-top:0.5rem;">📊 Distribución por Estado</p>', unsafe_allow_html=True)

    df_estado = df.groupby("estado").agg(
        pobreza=("pobreza_multidim","mean"),
        rezago=("rezago_educativo","mean"),
        municipios=("mun_id","count"),
    ).reset_index().sort_values("pobreza", ascending=True)

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=df_estado["estado"],
        x=df_estado["pobreza"],
        name="Pobreza %",
        orientation="h",
        marker_color="#f85149",
        marker_opacity=0.8,
    ))
    fig_bar.add_trace(go.Bar(
        y=df_estado["estado"],
        x=df_estado["rezago"],
        name="Rezago Educ. %",
        orientation="h",
        marker_color="#58a6ff",
        marker_opacity=0.6,
    ))
    fig_bar.update_layout(
        height=max(200, len(df_estado) * 28),
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font=dict(color="#8b949e", size=10),
        margin=dict(l=5, r=5, t=5, b=5),
        barmode="overlay",
        legend=dict(
            orientation="h", y=1.05,
            font=dict(size=9, color="#8b949e"),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(gridcolor="#21262d", zeroline=False, range=[0,100]),
        yaxis=dict(gridcolor="#21262d"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ─── Bottom row ───────────────────────────────────────────────────────────────
st.markdown("---")
col_amai, col_decil, col_sal = st.columns(3, gap="medium")

with col_amai:
    st.markdown('<p class="section-title">🏷️ Clasificación AMAI 2024</p>', unsafe_allow_html=True)
    amai_cnt = df["amai_2024"].value_counts().reset_index()
    amai_cnt.columns = ["AMAI", "Municipios"]
    orden = ["A/B","C+","C","D+","D","E"]
    amai_cnt["AMAI"] = pd.Categorical(amai_cnt["AMAI"], categories=orden, ordered=True)
    amai_cnt = amai_cnt.sort_values("AMAI")
    fig_amai = px.bar(
        amai_cnt, x="AMAI", y="Municipios",
        color="AMAI",
        color_discrete_map={"A/B":"#3fb950","C+":"#58a6ff","C":"#bc8cff","D+":"#ffa657","D":"#f85149","E":"#da3633"},
    )
    fig_amai.update_layout(
        height=200, showlegend=False,
        paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
        font=dict(color="#8b949e", size=10),
        margin=dict(l=5,r=5,t=5,b=5),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
    )
    st.plotly_chart(fig_amai, use_container_width=True)

with col_decil:
    st.markdown('<p class="section-title">📈 Decil de Ingreso</p>', unsafe_allow_html=True)
    dec_cnt = df["decil_ingreso"].value_counts().sort_index().reset_index()
    dec_cnt.columns = ["Decil","Municipios"]
    fig_dec = px.bar(
        dec_cnt, x="Decil", y="Municipios",
        color="Decil",
        color_continuous_scale="RdYlGn",
    )
    fig_dec.update_layout(
        height=200, showlegend=False, coloraxis_showscale=False,
        paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
        font=dict(color="#8b949e", size=10),
        margin=dict(l=5,r=5,t=5,b=5),
        xaxis=dict(gridcolor="#21262d",tickmode="linear",dtick=1),
        yaxis=dict(gridcolor="#21262d"),
    )
    st.plotly_chart(fig_dec, use_container_width=True)

with col_sal:
    st.markdown('<p class="section-title">💵 Salarios: Frontera vs. Resto</p>', unsafe_allow_html=True)
    sal_df = df.groupby("zona_frontera")["salario_minimo"].mean().reset_index()
    sal_df["Zona"] = sal_df["zona_frontera"].map({True:"Zona Libre\nFrontera Norte", False:"Resto\ndel País"})
    fig_sal = px.bar(
        sal_df, x="Zona", y="salario_minimo",
        color="Zona",
        color_discrete_map={"Zona Libre\nFrontera Norte":"#58a6ff","Resto\ndel País":"#bc8cff"},
        text=sal_df["salario_minimo"].apply(lambda v: f"${v:.0f}"),
        labels={"salario_minimo":"$/día"},
    )
    fig_sal.update_traces(textposition="outside", textfont=dict(color="#e6edf3", size=11))
    fig_sal.update_layout(
        height=200, showlegend=False,
        paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
        font=dict(color="#8b949e", size=10),
        margin=dict(l=5,r=5,t=5,b=5),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
    )
    st.plotly_chart(fig_sal, use_container_width=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="source-note">
  Fuentes: INEGI · DENUE 2024 · Censo de Población y Vivienda 2020 · ENIGH 2022/2024 · CONEVAL · CONASAMI<br>
  Factor de expansión aplicado según metodología INEGI. Clasificación AMAI 2024. Rezago educativo según umbrales CONEVAL.<br>
  <b>Tecnológico Universitario Playacar · Observatorio de Indicadores de Pobreza · 2026</b>
</div>
""", unsafe_allow_html=True)
