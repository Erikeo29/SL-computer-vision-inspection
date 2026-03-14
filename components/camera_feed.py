"""Composant d'acquisition d'image (camera / upload / exemples)."""
from __future__ import annotations

import os

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from config import SAMPLE_IMAGES_PATH
from utils.translations import t


def _pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """Convertit une image PIL en array OpenCV BGR.

    Parameters
    ----------
    pil_image : Image.Image
        Image PIL (RGB).

    Returns
    -------
    np.ndarray
        Image en format BGR pour OpenCV.
    """
    rgb = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _list_sample_images() -> list[str]:
    """Liste les images d'exemple disponibles.

    Returns
    -------
    list[str]
        Chemins absolus des images dans data/sample_images/.
    """
    if not os.path.isdir(SAMPLE_IMAGES_PATH):
        return []

    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    images: list[str] = []
    for fname in sorted(os.listdir(SAMPLE_IMAGES_PATH)):
        if os.path.splitext(fname)[1].lower() in extensions:
            images.append(os.path.join(SAMPLE_IMAGES_PATH, fname))
    return images


def render_image_input() -> None:
    """Affiche le composant d'acquisition d'image.

    Propose trois modes :
    - Camera (st.camera_input)
    - Telechargement (st.file_uploader)
    - Image d'exemple (selecteur)

    Ce composant utilise @st.fragment pour eviter un rechargement
    complet de la page a chaque interaction. L'image resultante est
    stockee dans ``st.session_state["current_image"]``.
    """
    mode = st.radio(
        t("input_mode"),
        [t("mode_camera"), t("mode_upload"), t("mode_sample")],
        horizontal=True,
        key="image_input_mode",
    )

    image_bgr: np.ndarray | None = None

    if mode == t("mode_camera"):
        st.caption(t("camera_prompt"))
        camera_photo = st.camera_input(
            label="camera_capture",
            key="camera_widget",
            label_visibility="collapsed",
        )
        if camera_photo is not None:
            pil_img = Image.open(camera_photo)
            image_bgr = _pil_to_cv2(pil_img)

    elif mode == t("mode_upload"):
        st.caption(t("upload_prompt"))
        uploaded = st.file_uploader(
            label="image_uploader",
            type=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
            key="upload_widget",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            pil_img = Image.open(uploaded)
            image_bgr = _pil_to_cv2(pil_img)

    elif mode == t("mode_sample"):
        st.caption(t("sample_prompt"))
        sample_images = _list_sample_images()
        if sample_images:
            selected = st.selectbox(
                label="sample_selector",
                options=sample_images,
                format_func=lambda p: os.path.basename(p),
                key="sample_widget",
                label_visibility="collapsed",
            )
            if selected:
                pil_img = Image.open(selected)
                image_bgr = _pil_to_cv2(pil_img)
                st.image(
                    pil_img,
                    caption=os.path.basename(selected),
                    use_container_width=True,
                )
        else:
            st.info(t("no_sample_images"))

    # Stocker l'image dans le session state pour les autres composants
    if image_bgr is not None:
        st.session_state["current_image"] = image_bgr
        st.session_state["current_image_name"] = _get_image_name(mode)
    else:
        # Nettoyer si aucune image
        st.session_state.pop("current_image", None)
        st.session_state.pop("current_image_name", None)


def get_current_image() -> np.ndarray | None:
    """Retourne l'image courante depuis le session state.

    Returns
    -------
    np.ndarray | None
        Image BGR, ou None si aucune image n'est chargee.
    """
    return st.session_state.get("current_image")


def _get_image_name(mode: str) -> str:
    """Determine le nom de l'image selon le mode d'acquisition.

    Parameters
    ----------
    mode : str
        Mode d'acquisition actif.

    Returns
    -------
    str
        Nom de l'image pour le journal d'inspection.
    """
    if mode == t("mode_camera"):
        return "camera_capture.jpg"
    elif mode == t("mode_upload"):
        widget = st.session_state.get("upload_widget")
        if widget is not None:
            return widget.name
        return "uploaded_image"
    elif mode == t("mode_sample"):
        widget = st.session_state.get("sample_widget")
        if widget:
            return os.path.basename(widget)
        return "sample_image"
    return "unknown"
