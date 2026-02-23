"""Chargement et gestion du modele de detection YOLO."""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from config import MODELS_PATH, ROOT_DIR, load_app_config


@st.cache_resource
def load_detection_model(model_path: str | None = None) -> tuple:
    """Charge le modele YOLO (personnalise ou pretraine).

    Le modele personnalise est utilise en priorite s'il existe.
    Sinon, le modele pretraine COCO par defaut est telecharge
    automatiquement par ultralytics.

    Parameters
    ----------
    model_path : str | None
        Chemin explicite vers un fichier .pt. Si None, la
        configuration YAML est utilisee.

    Returns
    -------
    tuple
        (model, model_name, is_demo_mode) ou model est l'instance
        YOLO, model_name le nom affiche, et is_demo_mode indique
        si le modele pretraine COCO est utilise.
    """
    from ultralytics import YOLO

    cfg = load_app_config()
    model_cfg = cfg.get("model", {})

    # 1. Chemin explicite
    if model_path and os.path.isfile(model_path):
        model = YOLO(model_path)
        return model, os.path.basename(model_path), False

    # 2. Modele personnalise depuis la config
    custom_path = os.path.join(ROOT_DIR, model_cfg.get("custom", ""))
    if os.path.isfile(custom_path):
        model = YOLO(custom_path)
        return model, os.path.basename(custom_path), False

    # 3. Modele pretraine par defaut (COCO)
    default_name = model_cfg.get("default", "yolov8n.pt")
    model = YOLO(default_name)
    return model, default_name, True


def get_model_config() -> dict:
    """Retourne la configuration du modele depuis config.yaml.

    Returns
    -------
    dict
        Configuration du modele (seuils, chemins, etc.).
    """
    cfg = load_app_config()
    return cfg.get("model", {})


def get_defect_categories() -> list[str]:
    """Retourne la liste des categories de defauts configurees.

    Returns
    -------
    list[str]
        Liste des identifiants de categories.
    """
    cfg = load_app_config()
    return cfg.get("defect_categories", [])
