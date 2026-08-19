from __future__ import annotations

import sqlite3
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


PRIMARY_ORANGE = "#DF7F22"
CHAMPIONSHIP_GOLD = "#DF7F22"
CHART_COLORS = [
    "#DF7F22", "#AAB2BD", "#F0A04B", "#7F8C99", "#D86D4A",
    "#C1C7CE", "#9A7653", "#E6B35A", "#687480", "#BE8260",
]
CHART_BACKGROUND = "#24282E"
HEADER_GOLD = "#D8892C"
STARTER_POSITION_ORDER = ["QB", "RB", "WR", "TE", "W/R/T", "K", "DEF"]
ROSTER_POSITION_ORDER = [*STARTER_POSITION_ORDER, "BN"]


st.set_page_config(
    page_title="The Legendary League",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --field: #111318;
        --field-2: #191c22;
        --surface: #23272e;
        --surface-raised: #2d323a;
        --orange: #df7f22;
        --orange-soft: #d8892c;
        --ink: #f0f1f3;
        --muted: #a9afb8;
        --line: #444a54;
    }

    html, body, [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #191c22 0%, var(--field) 42%, #0d0f13 100%);
        color: var(--ink);
    }

    .stApp p, .stApp label, .stApp li,
    .stApp span:not([data-baseweb="tag"] span) {
        color: #e2e4e8;
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1.8rem;
        padding-bottom: 4rem;
    }

    h1 {
        font-family: "Bebas Neue", "Arial Narrow", sans-serif !important;
        color: var(--orange) !important;
        font-size: clamp(3rem, 5vw, 5.1rem) !important;
        line-height: 0.95 !important;
        letter-spacing: 0.025em !important;
        font-weight: 400 !important;
        text-transform: uppercase;
    }

    h1 span, h1 a {
        color: var(--orange) !important;
        -webkit-text-fill-color: var(--orange) !important;
    }

    h2, h3 {
        color: var(--ink) !important;
        letter-spacing: -0.015em;
    }

    h3 {
        font-weight: 700 !important;
    }

    [data-testid="stCaptionContainer"], .stCaption {
        font-family: "IBM Plex Mono", monospace !important;
        color: var(--muted) !important;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        font-size: 0.72rem !important;
        font-weight: 500;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
