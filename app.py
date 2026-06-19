
from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Anime Analytics Dashboard",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------------------
# PALETA (mesma identidade visual do notebook)
# --------------------------------------------------------------------------------------
COR_DESTAQUE = "#E84393"    # rosa vibrante
COR_SECUNDARIA = "#7B2FBE"  # roxo
COR_NEUTRA = "#B0B0C0"      # cinza-azulado
COR_BG = "#0F0F1A"          # fundo escuro
COR_CARD = "#1A1A2E"        # fundo de painel
COR_TEXTO = "#EAEAF2"       # texto claro
COR_POSITIVO = "#3BBA9C"    # verde-esmeralda (destaques positivos)
COR_ALERTA = "#FFD166"      # amarelo (médias / alertas)

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=COR_BG,
        plot_bgcolor=COR_CARD,
        font=dict(color=COR_TEXTO, family="Inter, sans-serif"),
        xaxis=dict(gridcolor="#2A2A4A", zerolinecolor="#2A2A4A"),
        yaxis=dict(gridcolor="#2A2A4A", zerolinecolor="#2A2A4A"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        colorway=[COR_DESTAQUE, COR_SECUNDARIA, COR_POSITIVO, COR_ALERTA, COR_NEUTRA],
        margin=dict(t=60, l=10, r=10, b=10),
    )
)

DATA_DIR = Path(__file__).parent / "data"
# DEFAULT_DATA_PATH = DATA_DIR / "anime_dataset_final.csv"  # se for ler direto o csv e nao o parquet
DEFAULT_DATA_PATH = DATA_DIR / "anime_dataset_final.parquet"


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500&display=swap');

            html, body, [class*="css"] {{
                font-family: 'Inter', sans-serif;
            }}

            .stApp {{
                background: radial-gradient(circle at 12% 0%, #1c1430 0%, {COR_BG} 45%);
            }}

            /* Título principal — glow sutil em vez do neon duplo, fica mais clean */
            h1 {{
                font-family: 'Poppins', sans-serif !important;
                color: {COR_TEXTO};
                text-shadow: 0 0 18px rgba(232, 67, 147, 0.35);
                letter-spacing: -0.01em;
            }}

            h2, h3 {{
                font-family: 'Poppins', sans-serif !important;
            }}

            section[data-testid="stSidebar"] {{
                background-color: {COR_CARD};
                border-right: 1px solid #2A2A4A;
            }}

            section[data-testid="stSidebar"] .streamlit-expanderHeader,
            section[data-testid="stSidebar"] details summary {{
                font-family: 'Poppins', sans-serif;
                font-weight: 600;
            }}

            .kpi-card {{
                background: linear-gradient(145deg, {COR_CARD}, #211b38);
                border: 1px solid #2A2A4A;
                border-left: 4px solid {COR_DESTAQUE};
                border-radius: 12px;
                padding: 16px 18px;
                box-shadow: 0 4px 18px rgba(232, 67, 147, 0.15);
                height: 100%;
                transition: transform 0.2s ease-in-out;
            }}

            .kpi-card:hover {{
                transform: scale(1.02);
            }}

            .kpi-label {{
                font-size: 0.74rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: {COR_NEUTRA};
                margin-bottom: 6px;
            }}

            .kpi-value {{
                font-size: 1.55rem;
                font-weight: 700;
                font-family: 'Poppins', sans-serif;
            }}

            .filter-chip {{
                display: inline-block;
                background-color: rgba(232, 67, 147, 0.14);
                border: 1px solid {COR_DESTAQUE};
                color: {COR_DESTAQUE};
                padding: 3px 12px;
                border-radius: 999px;
                font-size: 0.78rem;
                margin: 2px 6px 2px 0;
            }}

            .insight-text {{
                color: {COR_NEUTRA};
                font-size: 0.85rem;
                margin-top: -6px;
            }}

            .subtitle {{
                color: {COR_NEUTRA};
                font-size: 0.95rem;
                margin-top: -8px;
            }}

            /* Botões */
            .stButton > button, .stDownloadButton > button {{
                border-radius: 8px;
                border: 1px solid {COR_DESTAQUE};
                color: {COR_TEXTO};
                background: linear-gradient(145deg, {COR_CARD}, #211b38);
                transition: all 0.2s ease-in-out;
            }}
            .stButton > button:hover, .stDownloadButton > button:hover {{
                box-shadow: 0 0 14px rgba(232, 67, 147, 0.35);
                color: {COR_DESTAQUE};
                border-color: {COR_DESTAQUE};
            }}

            /* Abas */
            .stTabs [data-baseweb="tab"] {{
                font-family: 'Poppins', sans-serif;
                font-weight: 600;
            }}
            .stTabs [aria-selected="true"] {{
                color: {COR_DESTAQUE} !important;
            }}

            /* Scrollbar customizado */
            ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
            ::-webkit-scrollbar-track {{ background: {COR_BG}; }}
            ::-webkit-scrollbar-thumb {{ background: {COR_SECUNDARIA}; border-radius: 8px; }}
            ::-webkit-scrollbar-thumb:hover {{ background: {COR_DESTAQUE}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_floating_mascot() -> None:
    """Mascote flutuante (Anya). Pode ser desativada pelo toggle na sidebar."""
    url_mascote = "https://www.pngmart.com/files/23/Anya-PNG-Photo.png"

    st.markdown(
        f"""
        <style>
        @keyframes float_mascot {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-20px); }}
            100% {{ transform: translateY(0px); }}
        }}

        .floating-mascot {{
            position: fixed;
            bottom: 40px;
            right: 40px;
            width: 150px;
            z-index: 9999;
            animation: float_mascot 3.5s ease-in-out infinite;
            pointer-events: none;
            filter: drop-shadow(0 0 12px {COR_DESTAQUE}80);
        }}

        @media (max-width: 768px) {{
            .floating-mascot {{
                display: none;
            }}
        }}
        </style>
        <img class="floating-mascot" src="{url_mascote}" alt="Mascote Anya">
        """,
        unsafe_allow_html=True,
    )


def kpi_card(col, label: str, value: str, accent: str = COR_DESTAQUE, icon: str = "📊") -> None:
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{icon}&nbsp; {label}</div>
            <div class="kpi-value" style="color:{accent}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_caption(text: str, icon: str = "💡") -> None:
    st.markdown(f'<p class="insight-text">{icon} {text}</p>', unsafe_allow_html=True)


def empty_state(msg: str = "Sem dados suficientes para este gráfico com os filtros atuais.") -> None:
    st.info(f"ℹ️ {msg}")


def format_big(n) -> str:
    if pd.isna(n):
        return "-"
    n = float(n)
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000:
        return f"{sign}{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{sign}{n / 1_000:.1f}K"
    return f"{sign}{n:.0f}"


# --------------------------------------------------------------------------------------
# CARGA E PREPARAÇÃO DOS DADOS
# --------------------------------------------------------------------------------------
@st.cache_data(show_spinner="Carregando base de dados... (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧")
def load_data(source) -> pd.DataFrame:
    df = pd.read_parquet(source)  # se for ler o parquet gerado pelo converter.py
    # df = pd.read_csv(source)  # se for ler direto o csv

    if "release_start" in df.columns:
        df["release_start"] = pd.to_datetime(df["release_start"], errors="coerce")
        df["year"] = df["release_start"].dt.year

    if "decade" not in df.columns and "year" in df.columns:
        decade_num = (df["year"] // 10 * 10)
        df["decade"] = decade_num.astype("Int64").astype(str) + "s"
        df.loc[df["year"].isna(), "decade"] = pd.NA

    if {"favorites", "members"}.issubset(df.columns):
        df["fav_rate"] = df["favorites"] / df["members"].replace(0, np.nan)

    if "episodes" in df.columns:
        bins = [0, 1, 12, 24, 50, 100, 100_000]
        labels = ["1 ep", "2–12 ep", "13–24 ep", "25–50 ep", "51–100 ep", "100+ ep"]
        df["ep_faixa"] = pd.cut(df["episodes"], bins=bins, labels=labels)

    return df


def explode_column(df: pd.DataFrame, col_name: str, new_name: str) -> pd.DataFrame:
    if col_name not in df.columns or df.empty:
        return pd.DataFrame(columns=df.columns.tolist() + [new_name])
    tmp = df.assign(**{new_name: df[col_name].astype(str).str.split("|")}).explode(new_name)
    tmp[new_name] = tmp[new_name].str.strip()
    tmp = tmp[~tmp[new_name].str.lower().isin(["unknown", "nan", "none", ""])]
    return tmp


@st.cache_data
def get_unique_exploded(df: pd.DataFrame, col_name: str, new_name: str) -> list:
    return sorted(explode_column(df, col_name, new_name)[new_name].dropna().unique().tolist())


def get_excel_bytes(df: pd.DataFrame) -> Optional[bytes]:
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="dados")
        return buffer.getvalue()
    except ImportError:
        return None


def get_data_source():
    if DEFAULT_DATA_PATH.exists():
        return DEFAULT_DATA_PATH
    st.sidebar.warning("`data/anime_dataset_final.csv` não encontrado.")
    uploaded = st.sidebar.file_uploader("Envie o CSV da base de animes 📂", type="csv")
    if uploaded is None:
        st.title("⛩️ Anime Analytics Dashboard")
        st.info(
            "👋 Para começar, coloque `anime_dataset_final.csv` em `data/` "
            "ou envie o arquivo pela barra lateral."
        )
        st.stop()
    return uploaded


# --------------------------------------------------------------------------------------
# BARRA LATERAL — FILTROS
# --------------------------------------------------------------------------------------
def build_sidebar(df: pd.DataFrame) -> dict:
    st.sidebar.image("https://www.pngmart.com/files/23/Anya-PNG-Photos.png", width="stretch")

    show_mascot = st.sidebar.toggle(
        "✨ Mostrar mascote flutuante",
        value=st.session_state.get("f_show_mascot", True),
        key="f_show_mascot",
        help="Desative para uma visualização mais limpa, por exemplo ao compartilhar a tela.",
    )

    st.sidebar.markdown("#### Filtros de Pesquisa")
    if st.sidebar.button("↺ Limpar filtros", width="stretch"):
        for key in list(st.session_state.keys()):
            if key.startswith("f_") and key != "f_show_mascot":
                del st.session_state[key]
        st.toast("Filtros limpos! ✨")
        st.rerun()

    year_default = None
    year_range = None
    types_all, sel_types = [], []
    ratings_all, sel_ratings = [], []
    with st.sidebar.expander("Período & Formato", expanded=True):
        if "year" in df.columns and df["year"].notna().any():
            ymin, ymax = int(df["year"].min()), int(df["year"].max())
            year_default = (ymin, ymax)
            year_range = st.slider(
                "Intervalo de anos", ymin, ymax, year_default, key="f_year",
                help="Filtra animes pelo ano de lançamento.",
            )

        if "type" in df.columns:
            types_all = sorted(df["type"].dropna().unique().tolist())
            sel_types = st.multiselect(
                "Formato", types_all, key="f_types",
                help="Filtra pelo formato: TV, Movie, OVA, etc.",
            )

        if "rating" in df.columns:
            ratings_all = sorted(df["rating"].dropna().unique().tolist())
            sel_ratings = st.multiselect(
                "Classificação", ratings_all, key="f_ratings",
                help="Filtra pela classificação indicativa.",
            )

    genres_all, sel_genres = [], []
    studios_all, sel_studios = [], []
    with st.sidebar.expander("Gênero & Estúdio", expanded=True):
        if "genres" in df.columns:
            genres_all = get_unique_exploded(df, "genres", "genre")
            sel_genres = st.multiselect(
                "Gênero", genres_all, key="f_genres",
                help="Selecione um ou mais gêneros para filtrar.",
            )
        if "studios" in df.columns:
            studios_all = get_unique_exploded(df, "studios", "studio")
            sel_studios = st.multiselect(
                "Estúdio", studios_all, key="f_studios",
                help="Selecione um ou mais estúdios de animação.",
            )

    with st.sidebar.expander("Score & Episódios", expanded=False):
        smin, smax = float(df["score"].min()), float(df["score"].max())
        score_default = (smin, smax)
        score_range = st.slider(
            "Faixa de score", smin, smax, score_default, step=0.1, key="f_score",
            help="Filtra pela nota média no MyAnimeList (0 a 10).",
        )

        emin, emax = int(df["episodes"].min()), int(df["episodes"].max())
        ep_default = (emin, emax)
        ep_range = st.slider(
            "Quantidade de episódios", emin, emax, ep_default, key="f_eps",
            help="Filtra pela quantidade total de episódios.",
        )

    with st.sidebar.expander("Sobre"):
        st.caption(
            "Dashboard interativo para exploração de uma base de dados de animes "
            "(Kaggle). Ajuste os filtros acima para refinar a análise — KPIs e "
            "gráficos são atualizados automaticamente."
        )

    return {
        "year_range": year_range,
        "year_default": year_default,
        "genres": sel_genres,
        "studios": sel_studios,
        "types": sel_types,
        "ratings": sel_ratings,
        "score_range": score_range,
        "score_default": score_default,
        "ep_range": ep_range,
        "ep_default": ep_default,
        "show_mascot": show_mascot,
    }


def apply_filters(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    out = df.copy()
    if f["year_range"] and f["year_range"] != f["year_default"] and "year" in out.columns:
        out = out[out["year"].between(f["year_range"][0], f["year_range"][1])]
    if f["genres"]:
        mask = out["genres"].fillna("").apply(lambda s: any(g in s for g in f["genres"]))
        out = out[mask]
    if f["studios"]:
        mask = out["studios"].fillna("").apply(lambda s: any(e in s for e in f["studios"]))
        out = out[mask]
    if f["types"]:
        out = out[out["type"].isin(f["types"])]
    if f["ratings"]:
        out = out[out["rating"].isin(f["ratings"])]
    if f["score_range"] != f["score_default"]:
        out = out[out["score"].between(f["score_range"][0], f["score_range"][1])]
    if f["ep_range"] != f["ep_default"]:
        out = out[out["episodes"].between(f["ep_range"][0], f["ep_range"][1])]
    return out


def render_active_filters(f: dict) -> None:
    chips = []
    if f["year_range"] and f["year_range"] != f["year_default"]:
        chips.append(f"Período: {f['year_range'][0]}–{f['year_range'][1]}")
    if f["genres"]:
        chips.append(f"Gêneros: {', '.join(f['genres'])}")
    if f["studios"]:
        chips.append(f"Estúdios: {', '.join(f['studios'])}")
    if f["types"]:
        chips.append(f"Tipo: {', '.join(f['types'])}")
    if f["ratings"]:
        chips.append(f"Classificação: {', '.join(f['ratings'])}")
    if f["score_range"] != f["score_default"]:
        chips.append(f"Score: {f['score_range'][0]:.1f}–{f['score_range'][1]:.1f}")
    if f["ep_range"] != f["ep_default"]:
        chips.append(f"Episódios: {f['ep_range'][0]}–{f['ep_range'][1]}")

    if chips:
        html = "".join(f'<span class="filter-chip">{c}</span>' for c in chips)
        st.markdown(f"**Filtros ativos:** {html}", unsafe_allow_html=True)
    else:
        st.markdown(
            '<span class="subtitle">Nenhum filtro ativo — exibindo a base completa.</span>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------------------
# KPIs
# --------------------------------------------------------------------------------------
def render_kpis(df: pd.DataFrame) -> None:
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi_card(c1, "Animes Registrados", f"{len(df):,}".replace(",", "."), COR_DESTAQUE, "📺")
    kpi_card(
        c2,
        "Score Médio MAL",
        f"{df['score'].mean():.2f}" if not df.empty else "-",
        COR_POSITIVO,
        "⭐",
    )
    kpi_card(c3, "Total Membros", format_big(df["members"].sum()) if "members" in df.columns else "-", COR_SECUNDARIA, "👥")
    kpi_card(c4, "Total Favoritos", format_big(df["favorites"].sum()) if "favorites" in df.columns else "-", COR_ALERTA, "💖")

    top_genre = "-"
    if "genres" in df.columns and not df.empty:
        exploded = explode_column(df, "genres", "genre")
        if not exploded.empty:
            top_genre = exploded["genre"].value_counts().idxmax().title()
    kpi_card(c5, "Gênero Dominante", top_genre, COR_NEUTRA, "🔥")

    period = "-"
    if "year" in df.columns and df["year"].notna().any():
        period = f"{int(df['year'].min())}–{int(df['year'].max())}"
    kpi_card(c6, "Período Coberto", period, COR_TEXTO, "🗓️")


# --------------------------------------------------------------------------------------
# GRÁFICOS
# --------------------------------------------------------------------------------------
def chart_time_evolution(df: pd.DataFrame) -> None:
    if "decade" not in df.columns or df.empty:
        empty_state("Sem coluna de década disponível para este recorte.")
        return
    g = df.groupby("decade")["score"].mean().reset_index()
    g = g[~g["decade"].astype(str).str.contains("NA", na=False)]
    g["decade_num"] = g["decade"].astype(str).str.extract(r"(\d+)").astype(float)
    g = g.dropna(subset=["decade_num"]).sort_values("decade_num")
    if g.empty:
        empty_state()
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=g["decade"], y=g["score"], mode="lines+markers",
        line=dict(color=COR_DESTAQUE, width=3),
        marker=dict(size=9, color=COR_SECUNDARIA), name="Score médio",
    ))
    fig.update_layout(template=PLOTLY_TEMPLATE, height=420, title="Evolução da Nota Média por Década", xaxis_title="Década", yaxis_title="Score médio")
    st.plotly_chart(fig, width="stretch")

    best = g.loc[g["score"].idxmax()]
    insight_caption(f"Década com maior nota média: <b>{best['decade']}</b> ({best['score']:.2f})")


def chart_top_genres(df: pd.DataFrame, min_qtd: int = 20) -> None:
    if "genres" not in df.columns or df.empty:
        empty_state()
        return
    exploded = explode_column(df, "genres", "genre")
    if exploded.empty:
        empty_state()
        return
    stats = exploded.groupby("genre")["score"].agg(media="mean", qtd="count").query("qtd >= @min_qtd").sort_values("media").reset_index()
    if stats.empty:
        empty_state(f"Nenhum gênero atinge o mínimo de {min_qtd} títulos com os filtros atuais.")
        return

    colors = [COR_NEUTRA] * len(stats)
    for i in range(min(3, len(stats))):
        colors[i] = COR_DESTAQUE
    for i in range(max(-3, -len(stats)), 0):
        colors[i] = COR_POSITIVO

    fig = go.Figure(go.Bar(x=stats["media"], y=stats["genre"], orientation="h", marker_color=colors, text=[f"{v:.2f}" for v in stats["media"]], textposition="outside"))
    fig.update_layout(template=PLOTLY_TEMPLATE, height=460, title=f"Nota Média por Gênero (≥ {min_qtd} títulos)", xaxis_title="Score médio", yaxis_title="")
    st.plotly_chart(fig, width="stretch")

    best, worst = stats.iloc[-1], stats.iloc[0]
    insight_caption(
        f"Maior nota: <b>{best['genre'].title()}</b> ({best['media']:.2f}) · "
        f"Menor nota: <b>{worst['genre'].title()}</b> ({worst['media']:.2f})"
    )


def chart_studios(df: pd.DataFrame, n: int = 12, min_qtd: int = 3) -> None:
    if "studios" not in df.columns or df.empty:
        empty_state()
        return
    exploded = explode_column(df, "studios", "studio")
    if exploded.empty or "engagement_ratio_pct" not in exploded.columns:
        empty_state("Dado de engajamento não disponível para este recorte.")
        return

    stats = exploded.groupby("studio").agg(qtd=("score", "count"), avg_members=("members", "mean"), avg_engagement=("engagement_ratio_pct", "mean")).query("qtd >= @min_qtd").sort_values("avg_members", ascending=False).head(n).reset_index()
    if stats.empty:
        empty_state(f"Nenhum estúdio atinge o mínimo de {min_qtd} títulos com os filtros atuais.")
        return

    stats["members_norm"] = stats["avg_members"] / stats["avg_members"].max() * 100
    eng_max = stats["avg_engagement"].max()
    stats["engagement_norm"] = (stats["avg_engagement"] / eng_max * 100) if eng_max and not pd.isna(eng_max) else 0

    fig = go.Figure()
    fig.add_bar(x=stats["studio"], y=stats["members_norm"], name="Membros (norm.)", marker_color=COR_SECUNDARIA)
    fig.add_bar(x=stats["studio"], y=stats["engagement_norm"], name="Engajamento (norm.)", marker_color=COR_DESTAQUE)
    fig.update_layout(barmode="group", template=PLOTLY_TEMPLATE, height=460, title=f"Top {len(stats)} Estúdios — Membros x Engajamento", xaxis_title="", yaxis_title="Índice normalizado", xaxis_tickangle=-35)
    st.plotly_chart(fig, width="stretch")

    top_studio = stats.iloc[0]
    insight_caption(f"Estúdio mais popular (por membros): <b>{top_studio['studio']}</b>")


def chart_episode_score(df: pd.DataFrame) -> None:
    if "ep_faixa" not in df.columns or df.empty:
        empty_state()
        return
    g = df.groupby("ep_faixa", observed=True)["score"].agg(media="mean", qtd="count").reset_index().dropna(subset=["media"])
    if g.empty:
        empty_state()
        return
    fig = go.Figure(go.Bar(x=g["ep_faixa"].astype(str), y=g["media"], marker_color=COR_SECUNDARIA, text=[f"{v:.2f}" for v in g["media"]], textposition="outside"))
    fig.update_layout(template=PLOTLY_TEMPLATE, height=420, title="Nota Média por Faixa de Episódios", xaxis_title="", yaxis_title="Score médio")
    st.plotly_chart(fig, width="stretch")

    best = g.loc[g["media"].idxmax()]
    insight_caption(f"Melhor faixa de episódios: <b>{best['ep_faixa']}</b> ({best['media']:.2f})")


def chart_popularity_distribution(df: pd.DataFrame) -> None:
    if "members" not in df.columns or df.empty:
        empty_state()
        return
    fig = px.histogram(df, x="members", nbins=30, template=PLOTLY_TEMPLATE, color_discrete_sequence=[COR_DESTAQUE])
    fig.update_layout(height=420, title="Distribuição da Popularidade", xaxis_title="Membros", yaxis_title="Qtd. de animes")
    st.plotly_chart(fig, width="stretch")


def chart_engagement_scatter(df: pd.DataFrame) -> None:
    if not {"members", "fav_rate"}.issubset(df.columns) or df.empty:
        empty_state()
        return
    sample = df.dropna(subset=["members", "fav_rate"])
    if sample.empty:
        empty_state()
        return
    fig = px.scatter(sample, x="members", y="fav_rate", template=PLOTLY_TEMPLATE, color_discrete_sequence=[COR_DESTAQUE], opacity=0.55)
    fig.update_layout(height=420, title="Popularidade x Taxa de Engajamento", xaxis_title="Membros", yaxis_title="Taxa de favoritos")
    st.plotly_chart(fig, width="stretch")


# --------------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------------
def main() -> None:
    inject_css()

    source = get_data_source()
    try:
        df = load_data(source)
    except Exception as exc: 
        st.error(f"Não foi possível carregar a base de dados: {exc}")
        st.stop()

    # Banner — podem alterar a img à vontade, só lembrar de ajustar o tamanho
    url_imagem = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/a2a1cc83-0aed-4c77-a2c4-86dc42d8e99d/dhd14i9-6ac221af-93bc-496c-8b3e-4311595c0a35.png/v1/fill/w_1280,h_512,q_80,strp/anya_forger_by_ryxartz_dhd14i9-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NTEyIiwicGF0aCI6Ii9mL2EyYTFjYzgzLTBhZWQtNGM3Ny1hMmM0LTg2ZGM0MmQ4ZTk5ZC9kaGQxNGk5LTZhYzIyMWFmLTkzYmMtNDk2Yy04YjNlLTQzMTE1OTVjMGEzNS5wbmciLCJ3aWR0aCI6Ijw9MTI4MCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.wlPB24WPNLt6UjuhFJcaq-fKBD3-7HlE0124JDdkb9Q"

    st.markdown(
        f"""
        <img src="{url_imagem}" style="
            width: 100%;
            height: 250px;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 16px;
        ">
        """,
        unsafe_allow_html=True,
    )

    st.markdown("# Anime Analytics Dashboard")
    st.markdown(
        '<p class="subtitle">Exploração interativa de notas, gêneros, estúdios, episódios e popularidade '
        "— a partir da análise da base de dados Anime Dataset (Kaggle). <i>おかえりなさい!</i></p>",
        unsafe_allow_html=True,
    )

    filters = build_sidebar(df)
    if filters.get("show_mascot", True):
        inject_floating_mascot()

    df_f = apply_filters(df, filters)

    render_active_filters(filters)
    st.write("")
    render_kpis(df_f)
    st.markdown("---")

    if df_f.empty:
        st.warning("Nenhum anime corresponde aos filtros selecionados. Tente ajustar os parâmetros na barra lateral! (╥﹏╥)")
        return

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Visão Geral", "Gêneros & Estúdios", "Distribuição & Engajamento", "Dados Brutos"]
    )

    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            chart_time_evolution(df_f)
        with col2:
            chart_episode_score(df_f)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            chart_top_genres(df_f)
        with col2:
            chart_studios(df_f)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            chart_popularity_distribution(df_f)
        with col2:
            chart_engagement_scatter(df_f)

    with tab4:
        # busca por nome, se a base tiver alguma coluna reconhecível de título
        possible_name_cols = ["name", "title", "anime_name", "english_name", "romaji_name"]
        name_col = next((c for c in possible_name_cols if c in df_f.columns), None)

        df_view = df_f
        if name_col:
            busca = st.text_input("🔎 Buscar por título", key="f_search", help="Filtra a tabela abaixo pelo nome do anime.")
            if busca:
                df_view = df_view[df_view[name_col].astype(str).str.contains(busca, case=False, na=False)]

        cols_sel = st.multiselect(
            "Colunas exibidas", df_view.columns.tolist(),
            default=df_view.columns.tolist(), key="f_cols",
        )
        df_view = df_view[cols_sel] if cols_sel else df_view

        st.caption(f"Exibindo {len(df_view):,} de {len(df_f):,} animes filtrados.".replace(",", "."))
        st.dataframe(df_view, width="stretch", height=460)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv = df_view.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Baixar CSV", data=csv, file_name="anime_filtrado.csv",
                mime="text/csv", width="stretch",
            )

    st.markdown("---")


if __name__ == "__main__":
    main()