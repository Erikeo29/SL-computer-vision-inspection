"""Traductions et gestion de la langue -- AI Visual Inspection."""
import streamlit as st

TRANSLATIONS: dict[str, dict[str, str | list[str]]] = {
    "fr": {
        # --- Sidebar ---
        "sidebar_title": "AI Visual Inspection",
        "lang_label": "Langue",
        "confidence_label": "Seuil de confiance",
        "confidence_help": (
            "Les detections en dessous de ce seuil seront ignorees."
        ),
        "version_info": (
            "**v{version}** -- {date}\n\n"
            "© Eric QUEAU -- Licence MIT"
        ),
        # --- Pages ---
        "page_inspection": "Inspection en direct",
        "page_dashboard": "Tableau de bord",
        "page_traceability": "Tracabilite",
        "page_guide": "Guide",
        # --- Inspection page ---
        "inspection_title": "Inspection visuelle par IA",
        "inspection_subtitle": (
            "Detection de defauts sur PCB, microconnecteurs et assemblages "
            "de biocapteurs."
        ),
        "input_mode": "Source d'image",
        "mode_camera": "Camera",
        "mode_upload": "Telechargement",
        "mode_sample": "Image exemple",
        "camera_prompt": "Prenez une photo de la piece a inspecter.",
        "upload_prompt": "Chargez une image (PNG, JPG, BMP).",
        "sample_prompt": "Selectionnez une image d'exemple pour la demonstration.",
        "no_sample_images": (
            "Aucune image d'exemple trouvee dans data/sample_images/."
        ),
        "btn_inspect": "LANCER L'INSPECTION",
        "btn_clear": "EFFACER",
        "results_header": "Resultats de l'inspection",
        "no_defects": "Aucun defaut detecte.",
        "defects_found": "{count} defaut(s) detecte(s).",
        "confidence": "Confiance",
        "class_label": "Classe",
        "bbox": "Coordonnees",
        "demo_mode_warning": (
            "**Mode demonstration** : le modele pretraine COCO est utilise. "
            "Les resultats sont illustratifs. Pour une detection reelle de "
            "defauts PCB, placez votre modele personnalise dans `models/`."
        ),
        "custom_model_active": (
            "Modele personnalise charge : `{model_name}`."
        ),
        "annotated_image": "Image annotee",
        "detection_table": "Tableau des detections",
        "save_result": "Enregistrer le resultat",
        "result_saved": "Resultat enregistre dans le journal d'inspection.",
        # --- Dashboard page ---
        "dashboard_title": "Tableau de bord des inspections",
        "dashboard_subtitle": "Statistiques et tendances des defauts.",
        "no_log_data": (
            "Aucune donnee d'inspection disponible. "
            "Effectuez des inspections pour alimenter le tableau de bord."
        ),
        "total_inspections": "Inspections totales",
        "total_defects": "Defauts totaux",
        "defect_rate": "Taux de defauts",
        "most_common": "Defaut le plus frequent",
        "defects_by_category": "Defauts par categorie",
        "defects_over_time": "Defauts dans le temps",
        "confidence_distribution": "Distribution des scores de confiance",
        "recent_inspections": "Inspections recentes",
        "clear_log": "Effacer le journal",
        "log_cleared": "Journal d'inspection efface.",
        # --- Traceability page ---
        "traceability_title": "Tracabilite et conformite",
        "traceability_subtitle": (
            "Enregistrements d'inspection pour la conformite "
            "reglementaire (FDA 21 CFR Part 11 / ISO 13485)."
        ),
        "export_csv": "Exporter CSV",
        "export_pdf": "Generer rapport PDF",
        "pdf_not_available": (
            "La generation PDF necessite reportlab. "
            "Installez-le avec : pip install reportlab."
        ),
        "inspection_id": "ID inspection",
        "timestamp": "Horodatage",
        "image_name": "Nom de l'image",
        "nb_defects": "Nb defauts",
        "defect_types": "Types de defauts",
        "model_used": "Modele utilise",
        "confidence_threshold": "Seuil de confiance",
        "operator": "Operateur",
        "status": "Statut",
        "status_pass": "CONFORME",
        "status_fail": "NON CONFORME",
        "filter_status": "Filtrer par statut",
        "filter_all": "Tous",
        "date_range": "Periode",
        # --- Guide page ---
        "guide_title": "Guide d'utilisation",
        # --- Defect categories (DeepPCB) ---
        "defect_open": "Circuit ouvert",
        "defect_short": "Court-circuit",
        "defect_mousebite": "Grignotage",
        "defect_spur": "Excroissance",
        "defect_spurious_copper": "Cuivre parasite",
        "defect_pin_hole": "Trou / void",
        # --- Severity ---
        "severity_critical": "CRITIQUE",
        "severity_minor": "MINEUR",
    },
    "en": {
        # --- Sidebar ---
        "sidebar_title": "AI Visual Inspection",
        "lang_label": "Language",
        "confidence_label": "Confidence threshold",
        "confidence_help": (
            "Detections below this threshold will be ignored."
        ),
        "version_info": (
            "**v{version}** -- {date}\n\n"
            "© Eric QUEAU -- MIT License"
        ),
        # --- Pages ---
        "page_inspection": "Live inspection",
        "page_dashboard": "Dashboard",
        "page_traceability": "Traceability",
        "page_guide": "Guide",
        # --- Inspection page ---
        "inspection_title": "AI visual inspection",
        "inspection_subtitle": (
            "Defect detection on PCBs, microconnectors and biosensor "
            "assemblies."
        ),
        "input_mode": "Image source",
        "mode_camera": "Camera",
        "mode_upload": "Upload",
        "mode_sample": "Sample image",
        "camera_prompt": "Take a photo of the part to inspect.",
        "upload_prompt": "Upload an image (PNG, JPG, BMP).",
        "sample_prompt": "Select a sample image for the demo.",
        "no_sample_images": (
            "No sample images found in data/sample_images/."
        ),
        "btn_inspect": "RUN INSPECTION",
        "btn_clear": "CLEAR",
        "results_header": "Inspection results",
        "no_defects": "No defects detected.",
        "defects_found": "{count} defect(s) detected.",
        "confidence": "Confidence",
        "class_label": "Class",
        "bbox": "Coordinates",
        "demo_mode_warning": (
            "**Demo mode**: the pretrained COCO model is being used. "
            "Results are illustrative only. For actual PCB defect detection, "
            "place your custom model in `models/`."
        ),
        "custom_model_active": (
            "Custom model loaded: `{model_name}`."
        ),
        "annotated_image": "Annotated image",
        "detection_table": "Detection table",
        "save_result": "Save result",
        "result_saved": "Result saved to inspection log.",
        # --- Dashboard page ---
        "dashboard_title": "Inspection dashboard",
        "dashboard_subtitle": "Defect statistics and trends.",
        "no_log_data": (
            "No inspection data available. "
            "Run inspections to populate the dashboard."
        ),
        "total_inspections": "Total inspections",
        "total_defects": "Total defects",
        "defect_rate": "Defect rate",
        "most_common": "Most common defect",
        "defects_by_category": "Defects by category",
        "defects_over_time": "Defects over time",
        "confidence_distribution": "Confidence score distribution",
        "recent_inspections": "Recent inspections",
        "clear_log": "Clear log",
        "log_cleared": "Inspection log cleared.",
        # --- Traceability page ---
        "traceability_title": "Traceability and compliance",
        "traceability_subtitle": (
            "Inspection records for regulatory compliance "
            "(FDA 21 CFR Part 11 / ISO 13485)."
        ),
        "export_csv": "Export CSV",
        "export_pdf": "Generate PDF report",
        "pdf_not_available": (
            "PDF generation requires reportlab. "
            "Install with: pip install reportlab."
        ),
        "inspection_id": "Inspection ID",
        "timestamp": "Timestamp",
        "image_name": "Image name",
        "nb_defects": "Nb defects",
        "defect_types": "Defect types",
        "model_used": "Model used",
        "confidence_threshold": "Confidence threshold",
        "operator": "Operator",
        "status": "Status",
        "status_pass": "PASS",
        "status_fail": "FAIL",
        "filter_status": "Filter by status",
        "filter_all": "All",
        "date_range": "Date range",
        # --- Guide page ---
        "guide_title": "User guide",
        # --- Defect categories (DeepPCB) ---
        "defect_open": "Open circuit",
        "defect_short": "Short circuit",
        "defect_mousebite": "Mouse bite",
        "defect_spur": "Spur",
        "defect_spurious_copper": "Spurious copper",
        "defect_pin_hole": "Pin hole / void",
        # --- Severity ---
        "severity_critical": "CRITICAL",
        "severity_minor": "MINOR",
    },
}

# Mapping defect category keys to translation keys
DEFECT_CATEGORY_KEYS: dict[str, str] = {
    "open": "defect_open",
    "short": "defect_short",
    "mousebite": "defect_mousebite",
    "spur": "defect_spur",
    "spurious_copper": "defect_spurious_copper",
    "pin_hole": "defect_pin_hole",
}


def get_language() -> str:
    """Retourne la langue actuelle.

    Returns
    -------
    str
        Code langue ("fr" ou "en").
    """
    if "lang" not in st.session_state:
        st.session_state.lang = "fr"
    return st.session_state.lang


def t(key: str) -> str | list[str]:
    """Retourne la traduction pour la cle donnee.

    Parameters
    ----------
    key : str
        Cle de traduction.

    Returns
    -------
    str | list[str]
        Texte traduit ou la cle si introuvable.
    """
    lang = get_language()
    return TRANSLATIONS[lang].get(key, key)


def t_defect(category: str) -> str:
    """Retourne le nom traduit d'une categorie de defaut.

    Parameters
    ----------
    category : str
        Identifiant de la categorie (ex. "solder_void").

    Returns
    -------
    str
        Nom traduit de la categorie.
    """
    lang = get_language()
    tkey = DEFECT_CATEGORY_KEYS.get(category, "")
    if tkey:
        return TRANSLATIONS[lang].get(tkey, category)
    return category.replace("_", " ").title()
