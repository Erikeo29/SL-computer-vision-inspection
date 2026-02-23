"""Post-traitement et classification des detections YOLO."""
from __future__ import annotations

import cv2
import numpy as np

from utils.translations import t_defect


# Couleurs BGR pour chaque categorie de defaut
DEFECT_COLORS: dict[str, tuple[int, int, int]] = {
    "solder_void": (0, 0, 220),
    "missing_component": (0, 100, 255),
    "contamination": (0, 180, 0),
    "dimensional_deviation": (255, 150, 0),
    "bent_pin": (200, 0, 200),
    "foreign_material": (0, 200, 200),
    "scratch": (128, 0, 128),
    "misalignment": (255, 0, 100),
}

# Couleur par defaut si la categorie n'est pas reconnue
DEFAULT_COLOR: tuple[int, int, int] = (0, 165, 255)


def run_inference(
    model,
    image: np.ndarray,
    confidence: float = 0.5,
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

        detections.append({
            "class_id": cls_id,
            "class_name": cls_name,
            "confidence": round(conf, 3),
            "bbox": xyxy,
        })

    return detections


def map_coco_to_defect(class_name: str) -> str:
    """Associe une classe COCO a une categorie de defaut (mode demo).

    En mode demonstration (modele pretraine COCO), les classes
    detectees sont mappees de maniere illustrative vers des
    categories de defauts PCB.

    Parameters
    ----------
    class_name : str
        Nom de la classe COCO detectee.

    Returns
    -------
    str
        Categorie de defaut mappee.
    """
    mapping: dict[str, str] = {
        "person": "foreign_material",
        "bicycle": "misalignment",
        "car": "dimensional_deviation",
        "motorcycle": "bent_pin",
        "airplane": "missing_component",
        "bus": "solder_void",
        "train": "contamination",
        "truck": "scratch",
        "boat": "foreign_material",
        "cell phone": "missing_component",
        "laptop": "solder_void",
        "mouse": "bent_pin",
        "keyboard": "contamination",
        "remote": "missing_component",
        "book": "scratch",
        "bottle": "foreign_material",
        "cup": "contamination",
        "scissors": "bent_pin",
    }
    return mapping.get(class_name, "contamination")


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
        Si True, les labels affichent les categories de defauts
        mappees depuis COCO.

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

        if is_demo_mode:
            defect_cat = map_coco_to_defect(det["class_name"])
            label_text = t_defect(defect_cat)
        else:
            label_text = det["class_name"]
            defect_cat = det["class_name"]

        color = DEFECT_COLORS.get(defect_cat, DEFAULT_COLOR)

        # Bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)

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
        Si True, utilise le mapping COCO vers defauts.

    Returns
    -------
    list[dict]
        Detections formatees avec categorie traduite.
    """
    formatted: list[dict] = []
    for det in detections:
        if is_demo_mode:
            category = map_coco_to_defect(det["class_name"])
        else:
            category = det["class_name"]

        formatted.append({
            "category": category,
            "category_display": t_defect(category),
            "confidence": det["confidence"],
            "bbox": det["bbox"],
            "original_class": det["class_name"],
        })
    return formatted
