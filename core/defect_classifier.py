"""Post-traitement et classification des detections YOLO.

Classes de defauts PCB (DeepPCB dataset) :
    0: open            — Circuit ouvert (coupure de piste)
    1: short           — Court-circuit (pont entre pistes)
    2: mousebite       — Grignotage (irregularite de bord)
    3: spur            — Excroissance metallique
    4: spurious_copper — Cuivre parasite (residu)
    5: pin_hole        — Trou/void dans le cuivre
"""
from __future__ import annotations

import cv2
import numpy as np

from utils.translations import t_defect


# Classes du modele (ordre identique au training YOLO)
CLASS_NAMES: list[str] = [
    "open",
    "short",
    "mousebite",
    "spur",
    "spurious_copper",
    "pin_hole",
]

# Defauts critiques (declenchent un FAIL immediat)
CRITICAL_DEFECTS: set[str] = {"open", "short"}

# Couleurs BGR pour chaque categorie de defaut
DEFECT_COLORS: dict[str, tuple[int, int, int]] = {
    "open": (0, 0, 220),            # rouge
    "short": (220, 50, 0),          # bleu
    "mousebite": (0, 180, 0),       # vert
    "spur": (0, 165, 255),          # orange
    "spurious_copper": (200, 0, 200),  # violet
    "pin_hole": (200, 200, 0),      # cyan
}

DEFAULT_COLOR: tuple[int, int, int] = (0, 165, 255)


def run_inference(
    model,
    image: np.ndarray,
    confidence: float = 0.3,
    iou: float = 0.45,
) -> list[dict]:
    """Execute l'inference YOLO sur une image.

    Parameters
    ----------
    model : ultralytics.YOLO
        Modele YOLO charge.
    image : np.ndarray
        Image en format BGR (OpenCV).
    confidence : float
        Seuil de confiance minimal.
    iou : float
        Seuil IoU pour la suppression non maximale.

    Returns
    -------
    list[dict]
        Liste de detections, chaque detection contenant :
        - class_id (int)
        - class_name (str)
        - confidence (float)
        - bbox (list[int]) : [x1, y1, x2, y2]
        - severity (str) : "critical" ou "minor"
    """
    results = model.predict(
        source=image,
        conf=confidence,
        iou=iou,
        verbose=False,
    )

    detections: list[dict] = []
    if not results or len(results) == 0:
        return detections

    result = results[0]
    boxes = result.boxes

    if boxes is None or len(boxes) == 0:
        return detections

    for box in boxes:
        cls_id = int(box.cls[0].item())
        cls_name = result.names.get(cls_id, f"class_{cls_id}")
        conf = float(box.conf[0].item())
        xyxy = box.xyxy[0].cpu().numpy().astype(int).tolist()

        severity = "critical" if cls_name in CRITICAL_DEFECTS else "minor"

        detections.append({
            "class_id": cls_id,
            "class_name": cls_name,
            "confidence": round(conf, 3),
            "bbox": xyxy,
            "severity": severity,
        })

    return detections


def annotate_image(
    image: np.ndarray,
    detections: list[dict],
    is_demo_mode: bool = False,
) -> np.ndarray:
    """Dessine les bounding boxes et labels sur l'image.

    Parameters
    ----------
    image : np.ndarray
        Image originale en BGR.
    detections : list[dict]
        Liste de detections issues de run_inference.
    is_demo_mode : bool
        Non utilise (conserve pour compatibilite API).

    Returns
    -------
    np.ndarray
        Image annotee avec les bounding boxes.
    """
    annotated = image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        conf = det["confidence"]
        cls_name = det["class_name"]
        severity = det.get("severity", "minor")

        label_text = t_defect(cls_name)
        color = DEFECT_COLORS.get(cls_name, DEFAULT_COLOR)

        # Bordure plus epaisse pour les defauts critiques
        box_thickness = 3 if severity == "critical" else 2

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, box_thickness)

        # Label background
        label = f"{label_text} {conf:.0%}"
        (tw, th), _ = cv2.getTextSize(label, font, font_scale, thickness)
        cv2.rectangle(
            annotated,
            (x1, y1 - th - 10),
            (x1 + tw + 6, y1),
            color,
            -1,
        )
        cv2.putText(
            annotated,
            label,
            (x1 + 3, y1 - 5),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
        )

    return annotated


def format_detections_for_log(
    detections: list[dict],
    is_demo_mode: bool = False,
) -> list[dict]:
    """Formate les detections pour le journal d'inspection.

    Parameters
    ----------
    detections : list[dict]
        Detections brutes.
    is_demo_mode : bool
        Non utilise (conserve pour compatibilite API).

    Returns
    -------
    list[dict]
        Detections formatees avec categorie traduite.
    """
    formatted: list[dict] = []
    for det in detections:
        category = det["class_name"]
        formatted.append({
            "category": category,
            "category_display": t_defect(category),
            "confidence": det["confidence"],
            "bbox": det["bbox"],
            "severity": det.get("severity", "minor"),
            "original_class": det["class_name"],
        })
    return formatted
