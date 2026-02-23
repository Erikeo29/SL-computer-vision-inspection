"""Generation de rapports d'inspection (CSV et PDF)."""
from __future__ import annotations

import csv
import io
import os
from datetime import datetime

import pandas as pd

from config import LOG_PATH


def load_inspection_log() -> pd.DataFrame:
    """Charge le journal d'inspection depuis le fichier CSV.

    Returns
    -------
    pd.DataFrame
        Journal d'inspection. DataFrame vide si le fichier
        n'existe pas.
    """
    if not os.path.isfile(LOG_PATH):
        return pd.DataFrame()

    try:
        df = pd.read_csv(LOG_PATH, parse_dates=["timestamp"])
        return df
    except Exception:
        return pd.DataFrame()


def save_inspection_record(
    image_name: str,
    nb_defects: int,
    defect_types: str,
    model_name: str,
    confidence_threshold: float,
    status: str,
    operator: str = "auto",
) -> None:
    """Enregistre un resultat d'inspection dans le journal CSV.

    Parameters
    ----------
    image_name : str
        Nom du fichier image inspecte.
    nb_defects : int
        Nombre de defauts detectes.
    defect_types : str
        Types de defauts detectes (separes par des virgules).
    model_name : str
        Nom du modele utilise.
    confidence_threshold : float
        Seuil de confiance utilise.
    status : str
        Statut de l'inspection ("PASS" ou "FAIL").
    operator : str
        Nom de l'operateur.
    """
    file_exists = os.path.isfile(LOG_PATH)

    # Creer le repertoire parent si necessaire
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    fieldnames = [
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

    # Generer un ID unique base sur le timestamp
    now = datetime.now()
    inspection_id = now.strftime("INS-%Y%m%d-%H%M%S")

    record = {
        "inspection_id": inspection_id,
        "timestamp": now.isoformat(),
        "image_name": image_name,
        "nb_defects": nb_defects,
        "defect_types": defect_types,
        "model_used": model_name,
        "confidence_threshold": confidence_threshold,
        "operator": operator,
        "status": status,
    }

    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


def clear_inspection_log() -> None:
    """Efface le journal d'inspection."""
    if os.path.isfile(LOG_PATH):
        os.remove(LOG_PATH)


def export_log_as_csv() -> str:
    """Exporte le journal d'inspection au format CSV.

    Returns
    -------
    str
        Contenu CSV en chaine de caracteres.
    """
    df = load_inspection_log()
    if df.empty:
        return ""
    return df.to_csv(index=False)


def generate_pdf_report(df: pd.DataFrame) -> bytes | None:
    """Genere un rapport PDF a partir des donnees d'inspection.

    Parameters
    ----------
    df : pd.DataFrame
        Donnees d'inspection a inclure dans le rapport.

    Returns
    -------
    bytes | None
        Contenu PDF en bytes, ou None si reportlab n'est pas
        installe.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    elements: list = []

    # Titre
    elements.append(
        Paragraph("AI Visual Inspection -- Rapport de tracabilite", styles["Title"])
    )
    elements.append(Spacer(1, 10 * mm))

    # Metadata
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(
        Paragraph(f"Date de generation : {now}", styles["Normal"])
    )
    elements.append(
        Paragraph(f"Nombre d'enregistrements : {len(df)}", styles["Normal"])
    )
    elements.append(Spacer(1, 8 * mm))

    # Table
    if not df.empty:
        cols = [
            "inspection_id",
            "timestamp",
            "image_name",
            "nb_defects",
            "defect_types",
            "status",
        ]
        available_cols = [c for c in cols if c in df.columns]
        table_data = [available_cols] + df[available_cols].values.tolist()

        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#004b87")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f2f6")]),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        elements.append(table)

    doc.build(elements)
    return buffer.getvalue()
