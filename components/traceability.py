"""Composant de tracabilite et conformite reglementaire."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from core.report_generator import (
    export_log_as_csv,
    generate_pdf_report,
    load_inspection_log,
)
from utils.translations import t


def render_traceability() -> None:
    """Affiche la page de tracabilite et conformite."""
    st.title(t("traceability_title"))
    st.markdown(t("traceability_subtitle"))
    st.divider()

    df = load_inspection_log()

    if df.empty:
        st.info(t("no_log_data"))
        return

    # Convertir le timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # --- Filtres ---
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        status_options = [t("filter_all")]
        if "status" in df.columns:
            status_options.extend(df["status"].unique().tolist())
        selected_status = st.selectbox(
            t("filter_status"),
            options=status_options,
            key="traceability_status_filter",
        )

    with col_filter2:
        if "timestamp" in df.columns and not df["timestamp"].isna().all():
            min_date = df["timestamp"].min().date()
            max_date = df["timestamp"].max().date()
        else:
            min_date = datetime.now().date() - timedelta(days=30)
            max_date = datetime.now().date()

        date_range = st.date_input(
            t("date_range"),
            value=(min_date, max_date),
            key="traceability_date_range",
        )

    with col_filter3:
        operator_filter = st.text_input(
            t("operator"),
            value="",
            key="traceability_operator_filter",
        )

    # Appliquer les filtres
    filtered = df.copy()

    if selected_status != t("filter_all") and "status" in filtered.columns:
        filtered = filtered[filtered["status"] == selected_status]

    if (
        "timestamp" in filtered.columns
        and isinstance(date_range, tuple)
        and len(date_range) == 2
    ):
        start, end = date_range
        mask = (filtered["timestamp"].dt.date >= start) & (
            filtered["timestamp"].dt.date <= end
        )
        filtered = filtered[mask]

    if operator_filter and "operator" in filtered.columns:
        filtered = filtered[
            filtered["operator"]
            .str.lower()
            .str.contains(operator_filter.lower(), na=False)
        ]

    # --- Metriques filtrees ---
    nb_records = len(filtered)
    nb_pass = (
        filtered[filtered["status"] == "PASS"].shape[0]
        if "status" in filtered.columns
        else 0
    )
    nb_fail = (
        filtered[filtered["status"] == "FAIL"].shape[0]
        if "status" in filtered.columns
        else 0
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(t("total_inspections"), nb_records)
    with m2:
        st.metric(t("status_pass"), nb_pass)
    with m3:
        st.metric(t("status_fail"), nb_fail)

    st.divider()

    # --- Tableau des enregistrements ---
    display_cols = [
        "inspection_id",
        "timestamp",
        "image_name",
        "nb_defects",
        "defect_types",
        "model_used",
        "confidence_threshold",
        "operator",
        "status",
    ]
    available_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[available_cols].sort_values("timestamp", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # --- Export ---
    col_csv, col_pdf = st.columns(2)

    with col_csv:
        csv_data = export_log_as_csv()
        if csv_data:
            st.download_button(
                label=t("export_csv"),
                data=csv_data,
                file_name=f"inspection_log_{datetime.now():%Y%m%d}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with col_pdf:
        if st.button(
            t("export_pdf"),
            use_container_width=True,
            key="btn_export_pdf",
        ):
            pdf_bytes = generate_pdf_report(filtered)
            if pdf_bytes is not None:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"inspection_report_{datetime.now():%Y%m%d}.pdf",
                    mime="application/pdf",
                    key="btn_download_pdf",
                )
            else:
                st.warning(t("pdf_not_available"))
