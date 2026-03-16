"""Composant d'affichage des resultats de detection."""
from __future__ import annotations

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from core.defect_classifier import (
    annotate_image,
    format_detections_for_log,
    run_inference,
)
from core.model_loader import load_detection_model
from core.report_generator import save_inspection_record
from utils.translations import t


def _cv2_to_pil(image_bgr: np.ndarray) -> Image.Image:
    """Convertit une image OpenCV BGR en PIL RGB.

    Parameters
    ----------
    image_bgr : np.ndarray
        Image BGR OpenCV.

    Returns
    -------
    Image.Image
        Image PIL RGB.
    """
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def render_detection_results(
    image_bgr: np.ndarray,
    confidence_threshold: float,
) -> None:
    """Execute la detection et affiche les resultats.

    Parameters
    ----------
    image_bgr : np.ndarray
        Image BGR a analyser.
    confidence_threshold : float
        Seuil de confiance pour filtrer les detections.
    """
    # Charger le modele
    model, model_name, is_demo_mode = load_detection_model()

    # Afficher l'avertissement demo ou le modele actif
    if is_demo_mode:
        st.warning(t("demo_mode_warning"))
    else:
        st.success(t("custom_model_active").format(model_name=model_name))

    # Executer l'inference
    with st.spinner("Analyzing..."):
        detections = run_inference(
            model=model,
            image=image_bgr,
            confidence=confidence_threshold,
        )

    # Formater les detections
    formatted = format_detections_for_log(detections, is_demo_mode)

    # --- Resultats ---
    st.subheader(t("results_header"))

    if not detections:
        st.success(t("no_defects"))
        status = "PASS"
    else:
        nb = len(detections)
        has_critical = any(d.get("severity") == "critical" for d in formatted)
        if has_critical:
            st.error(t("defects_found").format(count=nb) + " ⚠ " + t("severity_critical"))
        else:
            st.warning(t("defects_found").format(count=nb) + " — " + t("severity_minor"))
        status = "FAIL"

    # Images : original vs annotee cote a cote
    annotated = annotate_image(image_bgr, detections, is_demo_mode)
    pil_original = _cv2_to_pil(image_bgr)
    pil_annotated = _cv2_to_pil(annotated)

    col_orig, col_annot = st.columns(2)

    with col_orig:
        st.markdown("**Original**")
        st.image(pil_original, use_container_width=True)

    with col_annot:
        st.markdown(f"**{t('annotated_image')}**")
        st.image(pil_annotated, use_container_width=True)

    # Tableau des detections
    st.markdown(f"**{t('detection_table')}**")
    if formatted:
        df = pd.DataFrame(
            [
                {
                    t("class_label"): d["category_display"],
                    t("confidence"): f"{d['confidence']:.1%}",
                    t("status"): t("severity_critical") if d.get("severity") == "critical" else t("severity_minor"),
                }
                for d in formatted
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(t("no_defects"))

    # Metriques rapides
    if detections:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(t("nb_defects"), len(detections))
        with m2:
            avg_conf = sum(d["confidence"] for d in detections) / len(detections)
            st.metric(t("confidence"), f"{avg_conf:.1%}")
        with m3:
            categories = set(d["category"] for d in formatted)
            st.metric(t("defect_types"), len(categories))

    # Bouton de sauvegarde
    st.divider()
    col_save, col_clear = st.columns([1, 1])
    with col_save:
        if st.button(t("save_result"), type="primary", key="btn_save_result"):
            defect_type_str = ", ".join(
                sorted(set(d["category"] for d in formatted))
            ) if formatted else ""
            image_name = st.session_state.get(
                "current_image_name", "unknown"
            )
            save_inspection_record(
                image_name=image_name,
                nb_defects=len(detections),
                defect_types=defect_type_str,
                model_name=model_name,
                confidence_threshold=confidence_threshold,
                status=status,
            )
            st.toast(t("result_saved"))
    with col_clear:
        if st.button(t("btn_clear"), key="btn_clear_result"):
            for key in ["current_image", "current_image_name"]:
                st.session_state.pop(key, None)
            st.rerun()

    # Stocker les resultats dans le session state
    st.session_state["last_detections"] = formatted
    st.session_state["last_status"] = status
    st.session_state["last_model_name"] = model_name
