"""AI Visual Inspection -- Application Streamlit.

Detection de defauts sur PCB, microconnecteurs et assemblages de
biocapteurs par vision par ordinateur (YOLO).
"""
from __future__ import annotations

import os

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- Configuration de la page (DOIT etre en premier) ---
st.set_page_config(
    page_title="AI Visual Inspection",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Authentification ---
_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
with open(_cfg_path) as _f:
    _auth_config = yaml.load(_f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    _auth_config["credentials"],
    _auth_config["cookie"]["name"],
    _auth_config["cookie"]["key"],
    _auth_config["cookie"]["expiry_days"],
)

authenticator.login()

if not st.session_state.get("authentication_status"):
    if st.session_state.get("authentication_status") is False:
        st.error("Identifiants incorrects / Invalid credentials")
    else:
        st.info("Entrez vos identifiants / Enter your credentials")
    st.stop()

# --- Imports locaux ---
from config import ASSETS_PATH, CSS_PATH, ROOT_DIR, VERSION, VERSION_DATE
from utils.translations import TRANSLATIONS, get_language, t


# ═══════════════════════════════════════════════════════════════════════
#  CSS et navigation flottante
# ═══════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def _load_css(path: str) -> str:
    """Charge le fichier CSS."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def _inject_css_and_nav() -> None:
    """Injecte le CSS et les boutons de navigation flottants."""
    css = _load_css(CSS_PATH)
    nav_html = """
<a href="#top" class="nav-button back-to-top" title="Back to top">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
        <path d="M12 4l-8 8h5v8h6v-8h5z"/>
    </svg>
</a>
<a href="#bottom" class="nav-button scroll-to-bottom" title="Go to bottom">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
        <path d="M12 20l8-8h-5V4h-6v8H4z"/>
    </svg>
</a>
<div id="top"></div>
"""
    st.markdown(f"<style>{css}</style>{nav_html}", unsafe_allow_html=True)


_inject_css_and_nav()


# ═══════════════════════════════════════════════════════════════════════
#  Session state
# ═══════════════════════════════════════════════════════════════════════

if "lang" not in st.session_state:
    st.session_state.lang = "fr"

if "confidence_threshold" not in st.session_state:
    st.session_state.confidence_threshold = 0.5


# ═══════════════════════════════════════════════════════════════════════
#  Sidebar
# ═══════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title(t("sidebar_title"))
    authenticator.logout(location="sidebar")
    st.divider()

    # Selecteur de langue
    old_lang = st.session_state.lang
    lang_selection = st.radio(
        t("lang_label"),
        ["Francais", "English"],
        horizontal=True,
        index=0 if old_lang == "fr" else 1,
        label_visibility="collapsed",
    )
    new_lang = "fr" if "Francais" in lang_selection else "en"
    if new_lang != old_lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.divider()

    # Seuil de confiance
    st.session_state.confidence_threshold = st.slider(
        t("confidence_label"),
        min_value=0.1,
        max_value=1.0,
        value=st.session_state.confidence_threshold,
        step=0.05,
        help=t("confidence_help"),
        key="sidebar_confidence_slider",
    )

    st.divider()

    # Version
    st.markdown(
        t("version_info").format(version=VERSION, date=VERSION_DATE)
    )
    st.markdown("")
    st.markdown(
        "© 2026 Eric QUEAU -- "
        "[MIT License](https://opensource.org/licenses/MIT)"
    )


# ═══════════════════════════════════════════════════════════════════════
#  Fonctions de page
# ═══════════════════════════════════════════════════════════════════════

def page_inspection() -> None:
    """Page d'inspection en direct."""
    st.title(t("inspection_title"))
    st.markdown(t("inspection_subtitle"))
    st.divider()

    from components.camera_feed import get_current_image, render_image_input
    from components.detection import render_detection_results

    # Acquisition d'image (fragment pour eviter le rechargement complet)
    with st.container(border=True):
        render_image_input()

    # Detection : lire l'image depuis le session state
    image_bgr = get_current_image()
    if image_bgr is not None:
        st.divider()
        with st.container(border=True):
            render_detection_results(
                image_bgr=image_bgr,
                confidence_threshold=st.session_state.confidence_threshold,
            )


def page_dashboard() -> None:
    """Page du tableau de bord."""
    from components.dashboard import render_dashboard

    render_dashboard()


def page_traceability() -> None:
    """Page de tracabilite."""
    from components.traceability import render_traceability

    render_traceability()


def page_guide() -> None:
    """Page du guide d'utilisation."""
    st.title(t("guide_title"))
    st.divider()

    lang = get_language()
    guide_path = os.path.join(ROOT_DIR, "docs", lang, "guide.md")

    if os.path.isfile(guide_path):
        with open(guide_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(content)
    else:
        st.warning(f"Guide not found: {guide_path}")


# ═══════════════════════════════════════════════════════════════════════
#  Navigation st.navigation + st.Page
# ═══════════════════════════════════════════════════════════════════════

pages = st.navigation(
    [
        st.Page(
            page_inspection,
            title=t("page_inspection"),
            icon=":material/search:",
            default=True,
        ),
        st.Page(
            page_dashboard,
            title=t("page_dashboard"),
            icon=":material/bar_chart:",
        ),
        st.Page(
            page_traceability,
            title=t("page_traceability"),
            icon=":material/description:",
        ),
        st.Page(
            page_guide,
            title=t("page_guide"),
            icon=":material/menu_book:",
        ),
    ]
)

pages.run()

# --- Ancre de fin de page ---
st.markdown('<div id="bottom"></div>', unsafe_allow_html=True)
