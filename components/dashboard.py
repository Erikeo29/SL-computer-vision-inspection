"""Composant tableau de bord des inspections."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.report_generator import clear_inspection_log, load_inspection_log
from utils.translations import t, t_defect

# Palette coherente avec le theme navy
CHART_COLORS = [
    "#004b87",
    "#e74c3c",
    "#f39c12",
    "#2ecc71",
    "#9b59b6",
    "#1abc9c",
    "#e67e22",
    "#3498db",
]


def render_dashboard() -> None:
    """Affiche le tableau de bord complet des inspections."""
    st.title(t("dashboard_title"))
    st.markdown(t("dashboard_subtitle"))
    st.divider()

    df = load_inspection_log()

    if df.empty:
        st.info(t("no_log_data"))
        return

    # Convertir le timestamp si necessaire
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # --- Metriques globales ---
    total_inspections = len(df)
    total_defects = df["nb_defects"].sum() if "nb_defects" in df.columns else 0
    defect_rate = (
        df[df["nb_defects"] > 0].shape[0] / total_inspections * 100
        if total_inspections > 0
        else 0
    )

    # Defaut le plus frequent
    most_common = _get_most_common_defect(df)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(t("total_inspections"), total_inspections)
    with m2:
        st.metric(t("total_defects"), int(total_defects))
    with m3:
        st.metric(t("defect_rate"), f"{defect_rate:.1f}%")
    with m4:
        st.metric(t("most_common"), most_common)

    st.divider()

    # --- Graphiques ---
    col_left, col_right = st.columns(2)

    with col_left:
        _chart_defects_by_category(df)

    with col_right:
        _chart_defects_over_time(df)

    st.divider()

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        _chart_confidence_distribution(df)

    with col_right2:
        _chart_pass_fail_ratio(df)

    st.divider()

    # --- Tableau des inspections recentes ---
    st.subheader(t("recent_inspections"))
    display_cols = [
        "inspection_id",
        "timestamp",
        "image_name",
        "nb_defects",
        "defect_types",
        "status",
    ]
    available_cols = [c for c in display_cols if c in df.columns]
    recent = df.sort_values("timestamp", ascending=False).head(20)
    st.dataframe(
        recent[available_cols],
        use_container_width=True,
        hide_index=True,
    )

    # --- Bouton d'effacement ---
    st.divider()
    if st.button(t("clear_log"), type="secondary", key="btn_clear_log"):
        clear_inspection_log()
        st.toast(t("log_cleared"))
        st.rerun()


def _get_most_common_defect(df: pd.DataFrame) -> str:
    """Identifie le defaut le plus frequent.

    Parameters
    ----------
    df : pd.DataFrame
        Journal d'inspection.

    Returns
    -------
    str
        Nom traduit du defaut le plus frequent.
    """
    if "defect_types" not in df.columns:
        return "-"

    all_types: list[str] = []
    for val in df["defect_types"].dropna():
        for dtype in str(val).split(","):
            dtype = dtype.strip()
            if dtype:
                all_types.append(dtype)

    if not all_types:
        return "-"

    from collections import Counter

    counter = Counter(all_types)
    most_common_key = counter.most_common(1)[0][0]
    return t_defect(most_common_key)


def _chart_defects_by_category(df: pd.DataFrame) -> None:
    """Graphique des defauts par categorie (barres horizontales).

    Parameters
    ----------
    df : pd.DataFrame
        Journal d'inspection.
    """
    st.markdown(f"**{t('defects_by_category')}**")

    if "defect_types" not in df.columns:
        st.info(t("no_log_data"))
        return

    all_types: list[str] = []
    for val in df["defect_types"].dropna():
        for dtype in str(val).split(","):
            dtype = dtype.strip()
            if dtype:
                all_types.append(dtype)

    if not all_types:
        st.info(t("no_log_data"))
        return

    from collections import Counter

    counter = Counter(all_types)
    categories = list(counter.keys())
    counts = list(counter.values())
    labels = [t_defect(c) for c in categories]

    fig = go.Figure(
        go.Bar(
            x=counts,
            y=labels,
            orientation="h",
            marker_color=CHART_COLORS[0],
        )
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(automargin=True),
    )
    st.plotly_chart(fig, use_container_width=True)


def _chart_defects_over_time(df: pd.DataFrame) -> None:
    """Graphique de l'evolution des defauts dans le temps.

    Parameters
    ----------
    df : pd.DataFrame
        Journal d'inspection.
    """
    st.markdown(f"**{t('defects_over_time')}**")

    if "timestamp" not in df.columns or "nb_defects" not in df.columns:
        st.info(t("no_log_data"))
        return

    df_time = df.copy()
    df_time["date"] = df_time["timestamp"].dt.date
    daily = df_time.groupby("date").agg(
        inspections=("inspection_id", "count"),
        defects=("nb_defects", "sum"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["inspections"],
            name=t("total_inspections"),
            mode="lines+markers",
            line=dict(color=CHART_COLORS[0], width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["defects"],
            name=t("total_defects"),
            mode="lines+markers",
            line=dict(color=CHART_COLORS[1], width=2),
        )
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, use_container_width=True)


def _chart_confidence_distribution(df: pd.DataFrame) -> None:
    """Histogramme de la distribution des scores de confiance.

    Note : les scores de confiance individuels ne sont pas dans le
    CSV par defaut. On utilise le nombre de defauts comme proxy.

    Parameters
    ----------
    df : pd.DataFrame
        Journal d'inspection.
    """
    st.markdown(f"**{t('confidence_distribution')}**")

    if "confidence_threshold" not in df.columns:
        st.info(t("no_log_data"))
        return

    fig = px.histogram(
        df,
        x="confidence_threshold",
        nbins=20,
        color_discrete_sequence=[CHART_COLORS[0]],
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=t("confidence_threshold"),
        yaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)


def _chart_pass_fail_ratio(df: pd.DataFrame) -> None:
    """Camembert PASS/FAIL.

    Parameters
    ----------
    df : pd.DataFrame
        Journal d'inspection.
    """
    st.markdown(f"**{t('status')}**")

    if "status" not in df.columns:
        st.info(t("no_log_data"))
        return

    counts = df["status"].value_counts()

    fig = go.Figure(
        go.Pie(
            labels=counts.index.tolist(),
            values=counts.values.tolist(),
            marker=dict(colors=["#2ecc71", "#e74c3c"]),
            hole=0.4,
            textinfo="label+percent+value",
        )
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
