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
        padding: 0.55rem 0.72rem 0.85rem !important;
        background: linear-gradient(180deg, rgba(39, 44, 52, 0.98), rgba(29, 33, 40, 0.99));
        box-shadow: none;
        transition: border-color 140ms ease, background 140ms ease;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #6b727d !important;
        background: linear-gradient(180deg, rgba(45, 50, 59, 0.99), rgba(32, 36, 43, 0.99));
    }

    div[data-testid="stMetric"] {
        background: #23272e;
        border: 1px solid #444a54;
        border-radius: 9px;
        padding: 0.75rem 0.9rem;
        min-height: 96px;
    }

    div[data-testid="stMetricLabel"] {
        font-family: "IBM Plex Mono", monospace;
        color: var(--muted);
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    div[data-testid="stMetricValue"] {
        color: var(--orange);
        font-family: "Bebas Neue", "Arial Narrow", sans-serif;
        font-size: 2.6rem;
        font-weight: 400;
        letter-spacing: 0.035em;
    }

    div[data-testid="stMetricValue"] div,
    div[data-testid="stMetricValue"] span {
        color: var(--orange) !important;
        -webkit-text-fill-color: var(--orange) !important;
    }

    div[data-testid="stSelectbox"], div[data-testid="stMultiSelect"] {
        border: 1px solid #4c525d;
        border-radius: 9px;
        padding: 0.58rem 0.7rem 0.68rem;
        background: #23272e;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label {
        font-family: "IBM Plex Mono", monospace !important;
        color: #b5bac2 !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    div[data-baseweb="select"] > div {
        border: 1px solid #646b76 !important;
        border-radius: 999px !important;
        min-height: 2.55rem;
        background-color: #30353d !important;
        box-shadow: none;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] div {
        color: #f3f4ed !important;
        -webkit-text-fill-color: #f3f4ed !important;
        opacity: 1 !important;
    }

    div[data-baseweb="select"] svg {
        fill: var(--orange) !important;
        color: var(--orange) !important;
    }

    div[data-baseweb="popover"], ul[role="listbox"] {
        background-color: #30353d !important;
        color: #f3f4ed !important;
    }

    li[role="option"], li[role="option"] * {
        color: #f3f4ed !important;
        -webkit-text-fill-color: #f3f4ed !important;
        background-color: #30353d !important;
    }

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #474d57 !important;
    }

    div[data-baseweb="tag"] {
        background-color: #474d57 !important;
        color: #fff !important;
        border: 1px solid #6b727d;
    }

    section[data-testid="stSidebar"] {
        background: #191c22;
        border-right: 1px solid #444a54;
    }

    section[data-testid="stSidebar"] h1 {
        color: var(--orange) !important;
        font-size: 2.25rem !important;
        line-height: 1 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stRadio"] {
        border: 0;
        border-radius: 0;
        padding: 0.25rem 0;
        background: transparent;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border: 1px solid #4c525d;
        border-radius: 999px;
        padding: 0.48rem 0.7rem;
        margin-bottom: 0.42rem;
        background: #24282f;
        transition: background 140ms ease, border-color 140ms ease;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: #333841;
        border-color: #707782;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: var(--orange);
        border-color: var(--orange);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: #111318 !important;
        font-weight: 700;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #4c525d;
        border-radius: 8px;
        overflow: hidden;
        background: #23272e;
    }

    button[kind="header"], button[kind="secondary"] {
        border-color: #6b727d !important;
        border-radius: 999px !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #4c525d;
        border-radius: 8px;
        background: #23272e;
    }

    hr { border-color: #444a54 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "data" / "legendary_league.db"
FALLBACK_DB_PATH = Path(
    "/Users/noahceremony/PycharmProjects/Fantasy_App_2.0/data/legendary_league.db"
)
if not DB_PATH.exists() and FALLBACK_DB_PATH.exists():
    DB_PATH = FALLBACK_DB_PATH


@st.cache_data(show_spinner=False)
def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as connection:
        connection.executescript(
            """
            CREATE TEMP VIEW standings AS
            SELECT * FROM main.standings
            WHERE TRIM(COALESCE(team_owner, '')) <> '--hidden--';

            CREATE TEMP VIEW matchups AS
            SELECT * FROM main.matchups
            WHERE TRIM(COALESCE(team1_owner, '')) <> '--hidden--'
              AND TRIM(COALESCE(team2_owner, '')) <> '--hidden--';

            CREATE TEMP VIEW rosters AS
            SELECT * FROM main.rosters
            WHERE TRIM(COALESCE(team_owner, '')) <> '--hidden--';

            CREATE TEMP VIEW champions AS
            SELECT c.*
            FROM main.champions c
            WHERE EXISTS (
                SELECT 1
                FROM main.standings s
                WHERE s.year = c.year
                  AND s.team_key = c.team_key
                  AND TRIM(COALESCE(s.team_owner, '')) <> '--hidden--'
            );
            """
        )
        return pd.read_sql_query(query, connection, params=params)


def display_label(value: str) -> str:
    return str(value).replace("_", " ").strip().title()


def format_table(data: pd.DataFrame) -> None:
    display_data = data.copy()
    float_columns = display_data.select_dtypes(include=["float", "float32", "float64"]).columns
    display_data[float_columns] = display_data[float_columns].round(2)
    display_data = display_data.rename(
        columns={column: display_label(column) for column in display_data.columns}
    )
    styled = display_data.style.set_properties(
        **{
            "background-color": "#23272E",
            "color": "#F0F1F3",
            "border-color": "#444A54",
            "font-family": "Inter, sans-serif",
        }
    ).format(precision=2).set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("background-color", HEADER_GOLD),
                    ("color", "#111318"),
                    ("font-weight", "850"),
                    ("font-size", "1.05rem"),
                    ("border-color", "#E5A650"),
                ],
            }
        ]
    )
    st.dataframe(styled, width="stretch", hide_index=True)


def roster_comparison_table(data: pd.DataFrame, position_order: list[str]) -> pd.DataFrame:
    table_data = data.copy()
    table_data["points"] = pd.to_numeric(table_data["points"], errors="coerce").round(2)
    table_data["team_label"] = (
        table_data["team_owner"].astype(str)
        + " - "
        + table_data["team_name"].astype(str)
    )
    table_data["position_sort"] = table_data["selected_position"].map(
        {position: index for index, position in enumerate(position_order)}
    )
    table_data["position_sort"] = table_data["position_sort"].fillna(len(position_order))
    table_data = table_data.sort_values(
        ["position_sort", "team_label", "points", "player_name"],
        ascending=[True, True, False, True],
    )
    table_data["slot"] = table_data.groupby(
        ["team_label", "selected_position"]
    ).cumcount()
    table_data["player_points"] = table_data.apply(
        lambda row: f"{row['player_name']} ({row['points']:.2f})",
        axis=1,
    )
    comparison = table_data.pivot_table(
        index=["position_sort", "selected_position", "slot"],
        columns="team_label",
        values="player_points",
        aggfunc="first",
    ).reset_index()
    comparison = comparison.sort_values(["position_sort", "slot"])
    comparison = comparison.drop(columns=["position_sort", "slot"])
    return comparison.rename(columns={"selected_position": "position"}).fillna("")


def dropdown_label(label: str) -> str:
    return f"Select {label}"


def ordered_bar_chart(
    data: pd.DataFrame,
    category: str,
    value: str,
    category_title: str,
    value_title: str,
    ascending: bool = False,
) -> None:
    chart_data = data.sort_values(value, ascending=ascending).reset_index(drop=True)
    value_is_float = pd.api.types.is_float_dtype(chart_data[value])
    if value_is_float:
        chart_data[value] = chart_data[value].round(2)
    category_order = chart_data[category].tolist()
    category_label = display_label(category_title)
    value_label = display_label(value_title)
    chart = (
        alt.Chart(chart_data)
        .mark_bar(
            color=PRIMARY_ORANGE,
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5,
            stroke="#F0A04B",
            strokeWidth=0.35,
        )
        .encode(
            x=alt.X(
                f"{category}:N",
                title=category_label,
                sort=category_order,
                axis=alt.Axis(
                    labelAngle=30,
                    labelOverlap=False,
                    labelLimit=180,
                    labelFontSize=11,
                    values=category_order,
                ),
            ),
            y=alt.Y(
                f"{value}:Q",
                title=value_label,
                axis=alt.Axis(format=".2f" if value_is_float else "d"),
            ),
            tooltip=[
                alt.Tooltip(f"{category}:N", title=category_label),
                alt.Tooltip(
                    f"{value}:Q",
                    title=value_label,
                    format=".2f" if value_is_float else "d",
                ),
            ],
        )
        .properties(height=390)
        .configure(background=CHART_BACKGROUND)
        .configure_view(fill=CHART_BACKGROUND, stroke="#4C525D", strokeWidth=0.7)
        .configure_axis(
            gridColor="#3B4049",
            domainColor="#6B727D",
            tickColor="#6B727D",
            labelColor="#E2E4E8",
            titleColor="#F0F1F3",
        )
    )
    st.altair_chart(chart, width="stretch")


def themed_line_chart(
    data: pd.DataFrame,
    x: str,
    series: list[str],
    x_title: str,
    y_title: str,
) -> None:
    values_are_float = any(pd.api.types.is_float_dtype(data[column]) for column in series)
    chart_data = data[[x, *series]].melt(
        id_vars=x,
        value_vars=series,
        var_name="series",
        value_name="value",
    )
    chart_data["value"] = pd.to_numeric(chart_data["value"], errors="coerce").round(2)
    chart_data["series"] = chart_data["series"].map(display_label)
    x_label = display_label(x_title)
    y_label = display_label(y_title)
    chart = (
        alt.Chart(chart_data)
        .mark_line(point=alt.OverlayMarkDef(size=42), strokeWidth=2.5)
        .encode(
            x=alt.X(f"{x}:N", title=x_label, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(
                "value:Q",
                title=y_label,
                axis=alt.Axis(format=".2f" if values_are_float else "d"),
            ),
            color=alt.Color(
                "series:N",
                scale=alt.Scale(range=CHART_COLORS),
                legend=alt.Legend(title=None, orient="top"),
            ),
            tooltip=[
                alt.Tooltip(f"{x}:N", title=x_label),
                alt.Tooltip("series:N", title="Series"),
                alt.Tooltip(
                    "value:Q",
                    title=y_label,
                    format=".2f" if values_are_float else "d",
                ),
            ],
        )
        .properties(height=360)
        .configure(background=CHART_BACKGROUND)
        .configure_view(fill=CHART_BACKGROUND, stroke="#4C525D", strokeWidth=0.7)
        .configure_axis(
            gridColor="#3B4049",
            domainColor="#6B727D",
            tickColor="#6B727D",
            labelColor="#E2E4E8",
            titleColor="#F0F1F3",
        )
        .configure_legend(labelColor="#E2E4E8")
    )
    st.altair_chart(chart, width="stretch")


def grouped_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    group: str,
    x_title: str,
    y_title: str,
    group_title: str,
    hover_column: str | None = None,
    hover_title: str = "Player Name",
) -> None:
    chart_data = data.copy()
    chart_data[y] = pd.to_numeric(chart_data[y], errors="coerce").round(2)
    x_order = chart_data[x].drop_duplicates().tolist()
    tooltip = [
        alt.Tooltip(f"{x}:N", title=display_label(x_title)),
    ]
    if hover_column and hover_column in chart_data.columns:
        tooltip.append(alt.Tooltip(f"{hover_column}:N", title=display_label(hover_title)))
    tooltip.append(alt.Tooltip(f"{y}:Q", title=display_label(y_title), format=".2f"))

    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(
                f"{x}:N",
                title=display_label(x_title),
                sort=x_order,
                axis=alt.Axis(
                    labelAngle=0,
                    labelOverlap=False,
                    labelLimit=120,
                    values=x_order,
                ),
            ),
            xOffset=alt.XOffset(f"{group}:N", title=display_label(group_title)),
            y=alt.Y(
                f"{y}:Q",
                title=display_label(y_title),
                axis=alt.Axis(format=".2f"),
            ),
            color=alt.Color(
                f"{group}:N",
                title=display_label(group_title),
                scale=alt.Scale(range=CHART_COLORS),
                legend=alt.Legend(orient="top"),
            ),
            tooltip=tooltip,
        )
        .properties(height=390)
        .configure(background=CHART_BACKGROUND)
        .configure_view(fill=CHART_BACKGROUND, stroke="#4C525D", strokeWidth=0.7)
        .configure_axis(
            gridColor="#3B4049",
            domainColor="#6B727D",
            tickColor="#6B727D",
            labelColor="#E2E4E8",
            titleColor="#F0F1F3",
        )
        .configure_legend(labelColor="#E2E4E8", titleColor="#F0F1F3")
    )
    st.altair_chart(chart, width="stretch")


def blend_hex_color(hex_color: str, blend_with: str, amount: float) -> str:
    base = hex_color.lstrip("#")
    target = blend_with.lstrip("#")
    base_rgb = [int(base[index : index + 2], 16) for index in (0, 2, 4)]
    target_rgb = [int(target[index : index + 2], 16) for index in (0, 2, 4)]
    mixed = [
        round(base_value + (target_value - base_value) * amount)
        for base_value, target_value in zip(base_rgb, target_rgb)
    ]
    return "#" + "".join(f"{value:02X}" for value in mixed)


def stacked_player_position_chart(data: pd.DataFrame, position_order: list[str]) -> None:
    chart_data = data.copy()
    chart_data["points"] = pd.to_numeric(chart_data["points"], errors="coerce").round(2)
    chart_data["player_name"] = chart_data["player_name"].fillna("Unknown Player")
    chart_data["player_rank"] = chart_data.groupby(
        ["team_owner", "selected_position"]
    ).cumcount()
    owners = chart_data["team_owner"].drop_duplicates().tolist()
    owner_colors = {
        owner: CHART_COLORS[index % len(CHART_COLORS)]
        for index, owner in enumerate(owners)
    }
    owner_legend_colors = {
        owner: blend_hex_color(owner_colors[owner], "#FFFFFF", 0.18)
        for owner in owners
    }
    chart_data["segment_color"] = chart_data.apply(
        lambda row: blend_hex_color(
            owner_colors[row["team_owner"]],
            "#FFFFFF",
            min(0.45, 0.08 + row["player_rank"] * 0.18),
        ),
        axis=1,
    )

    bars = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(
                "selected_position:N",
                title="Position",
                sort=position_order,
                axis=alt.Axis(
                    labelAngle=0,
                    labelOverlap=False,
                    labelLimit=120,
                    values=position_order,
                ),
            ),
            xOffset=alt.XOffset("team_owner:N", title="Owner"),
            y=alt.Y(
                "points:Q",
                title="Points",
                stack="zero",
                axis=alt.Axis(format=".2f"),
            ),
            color=alt.Color(
                "team_owner:N",
                title="Owner",
                scale=alt.Scale(
                    domain=owners,
                    range=[owner_legend_colors[owner] for owner in owners],
                ),
                legend=None,
            ),
            fill=alt.Fill(
                "segment_color:N",
                scale=None,
                legend=None,
            ),
            order=alt.Order("player_rank:Q"),
            tooltip=[
                alt.Tooltip("selected_position:N", title="Position"),
                alt.Tooltip("player_name:N", title="Player Name"),
                alt.Tooltip("points:Q", title="Points", format=".2f"),
            ],
        )
        .properties(height=430)
    )

    owner_legend = (
        alt.Chart(
            pd.DataFrame(
                {
                    "team_owner": owners,
                    "legend_color": [owner_legend_colors[owner] for owner in owners],
                }
            )
        )
        .mark_point(filled=True, size=180)
        .encode(
            x=alt.X(
                "team_owner:N",
                title="Owner",
                sort=owners,
                axis=alt.Axis(labelAngle=0, labelColor="#E2E4E8", titleColor="#F0F1F3"),
            ),
            color=alt.Color("legend_color:N", scale=None, legend=None),
            tooltip=[alt.Tooltip("team_owner:N", title="Owner")],
        )
        .properties(height=70)
    )

    chart = (
        alt.vconcat(owner_legend, bars, spacing=4)
        .configure(background=CHART_BACKGROUND)
        .configure_view(fill=CHART_BACKGROUND, stroke="#4C525D", strokeWidth=0.7)
        .configure_axis(
            gridColor="#3B4049",
            domainColor="#6B727D",
            tickColor="#6B727D",
            labelColor="#E2E4E8",
            titleColor="#F0F1F3",
        )
        .configure_legend(labelColor="#E2E4E8", titleColor="#F0F1F3")
    )
    st.altair_chart(chart, width="stretch")


def all_scores_cte() -> str:
    return """
        WITH all_scores AS (
            SELECT year, week, team1_owner AS team_owner, team1_points AS points
            FROM matchups
            UNION ALL
            SELECT year, week, team2_owner AS team_owner, team2_points AS points
            FROM matchups
        )
    """


def current_streak(results: pd.DataFrame) -> tuple[str, int]:
    if results.empty:
        return "-", 0
    latest_result = str(results.iloc[-1]["result"])
    length = 0
    for result in reversed(results["result"].astype(str).tolist()):
        if result != latest_result:
            break
        length += 1
    return latest_result, length


def filtered_biggest_result(games: pd.DataFrame, result: str) -> pd.DataFrame:
    """Return each selected owner's biggest win or loss from filtered games."""
    filtered = games[games["result"] == result].copy()
    if filtered.empty:
        margin_column = "victory_margin" if result == "W" else "loss_margin"
        return pd.DataFrame(
            columns=[
                "owner", "year", "week", "opponent",
                "points_for", "points_against", margin_column,
            ]
        )

    if result == "W":
        filtered["victory_margin"] = filtered["margin"].round(2)
        margin_column = "victory_margin"
    else:
        filtered["loss_margin"] = (-filtered["margin"]).round(2)
        margin_column = "loss_margin"

    biggest_margin = filtered.groupby("owner")[margin_column].transform("max")
    filtered = filtered[filtered[margin_column] == biggest_margin]
    return filtered[
        [
            "owner", "year", "week", "opponent",
            "points_for", "points_against", margin_column,
        ]
    ].sort_values([margin_column, "owner"], ascending=[False, True])


QUERY_LIBRARY = {
    "Career wins (including playoffs)": """
        SELECT team_owner, SUM(total_wins) AS career_wins
        FROM standings
        GROUP BY team_owner
        ORDER BY career_wins DESC, team_owner
    """,
    "Career wins (regular season)": """
        SELECT team_owner, SUM(wins) AS regular_season_wins
        FROM standings
        GROUP BY team_owner
        ORDER BY regular_season_wins DESC, team_owner
    """,
    "Career losses (including playoffs)": """
        SELECT team_owner, SUM(total_losses) AS career_losses
        FROM standings
        GROUP BY team_owner
        ORDER BY career_losses DESC, team_owner
    """,
    "Career losses (regular season)": """
        SELECT team_owner, SUM(losses) AS regular_season_losses
        FROM standings
        GROUP BY team_owner
        ORDER BY regular_season_losses DESC, team_owner
    """,
    "Career win rate (minimum 3 seasons)": """
        SELECT
            team_owner,
            COUNT(DISTINCT year) AS seasons_played,
            SUM(total_wins) AS career_wins,
            SUM(total_losses) AS career_losses,
            SUM(ties) AS career_ties,
            ROUND(
                1.0 * SUM(total_wins) /
                NULLIF(SUM(total_wins) + SUM(total_losses) + SUM(ties), 0),
                3
            ) AS career_win_rate
        FROM standings
        GROUP BY team_owner
        HAVING COUNT(DISTINCT year) >= 3
        ORDER BY career_win_rate DESC, team_owner
    """,
    "Seasons played": """
        SELECT team_owner, COUNT(DISTINCT year) AS seasons_played
        FROM standings
        GROUP BY team_owner
        ORDER BY seasons_played DESC, team_owner
    """,
    "Championships": """
        SELECT s.team_owner, COUNT(*) AS championships
        FROM champions c
        JOIN standings s ON c.year = s.year AND c.team_key = s.team_key
        GROUP BY s.team_owner
        ORDER BY championships DESC, s.team_owner
    """,
    "Playoff wins": """
        SELECT team_owner, SUM(playoff_wins) AS playoff_wins
        FROM standings
        GROUP BY team_owner
        ORDER BY playoff_wins DESC, team_owner
    """,
    "Playoff losses": """
        SELECT team_owner, SUM(playoff_losses) AS playoff_losses
        FROM standings
        GROUP BY team_owner
        ORDER BY playoff_losses DESC, team_owner
    """,
    "Average wins per season": """
        SELECT
            team_owner,
            COUNT(DISTINCT year) AS seasons_played,
            SUM(total_wins) AS career_wins,
            ROUND(1.0 * SUM(total_wins) / COUNT(DISTINCT year), 2) AS avg_wins_per_season
        FROM standings
        GROUP BY team_owner
        ORDER BY avg_wins_per_season DESC, team_owner
    """,
    "Average weekly score by season": all_scores_cte() + """
        SELECT year, team_owner, ROUND(AVG(points), 2) AS avg_weekly_score
        FROM all_scores
        GROUP BY year, team_owner
        ORDER BY year DESC, avg_weekly_score DESC
    """,
    "Highest weekly score by owner and season": all_scores_cte() + """
        SELECT year, team_owner, week, points AS highest_weekly_score
        FROM all_scores scores
        WHERE points = (
            SELECT MAX(other.points)
            FROM all_scores other
            WHERE other.year = scores.year AND other.team_owner = scores.team_owner
        )
        ORDER BY year DESC, highest_weekly_score DESC
    """,
    "Lowest weekly score by owner and season": all_scores_cte() + """
        SELECT year, team_owner, week, points AS lowest_weekly_score
        FROM all_scores scores
        WHERE points = (
            SELECT MIN(other.points)
            FROM all_scores other
            WHERE other.year = scores.year AND other.team_owner = scores.team_owner
        )
        ORDER BY year DESC, lowest_weekly_score
    """,
    "Score by week": all_scores_cte() + """
        SELECT year, week, team_owner, points
        FROM all_scores
        ORDER BY year DESC, team_owner, week
    """,
    "Weekly scoring change": all_scores_cte() + """,
        weekly_change AS (
            SELECT
                year,
                week,
                team_owner,
                points,
                LAG(points) OVER (
                    PARTITION BY year, team_owner ORDER BY week
                ) AS previous_week_points
            FROM all_scores
        )
        SELECT
            year,
            week,
            team_owner,
            points,
            previous_week_points,
            ROUND(points - previous_week_points, 2) AS week_to_week_change
        FROM weekly_change
        ORDER BY year DESC, team_owner, week
    """,
    "Season total scoring trend": all_scores_cte() + """,
        yearly_totals AS (
            SELECT year, team_owner, ROUND(SUM(points), 2) AS total_points
            FROM all_scores
            GROUP BY year, team_owner
        )
        SELECT
            year,
            team_owner,
            total_points,
            ROUND(
                total_points - LAG(total_points) OVER (
                    PARTITION BY team_owner ORDER BY year
                ),
                2
            ) AS year_over_year_change
        FROM yearly_totals
        ORDER BY team_owner, year
    """,
    "Season average scoring trend": all_scores_cte() + """,
        yearly_averages AS (
            SELECT year, team_owner, ROUND(AVG(points), 2) AS avg_weekly_score
            FROM all_scores
            GROUP BY year, team_owner
        )
        SELECT
            year,
            team_owner,
            avg_weekly_score,
            ROUND(
                avg_weekly_score - LAG(avg_weekly_score) OVER (
                    PARTITION BY team_owner ORDER BY year
                ),
                2
            ) AS year_over_year_change
        FROM yearly_averages
        ORDER BY team_owner, year
    """,
    "Head-to-head records": """
        WITH games AS (
            SELECT team1_owner AS owner, team2_owner AS opponent,
                   team1_points AS points_for, team2_points AS points_against
            FROM matchups
            UNION ALL
            SELECT team2_owner, team1_owner, team2_points, team1_points
            FROM matchups
        )
        SELECT
            owner,
            opponent,
            COUNT(*) AS games_played,
            SUM(points_for > points_against) AS wins,
            SUM(points_for < points_against) AS losses,
            SUM(points_for = points_against) AS ties,
            ROUND(AVG(points_for), 2) AS avg_points_for,
            ROUND(AVG(points_against), 2) AS avg_points_against,
            ROUND(AVG(points_for - points_against), 2) AS avg_margin
        FROM games
        GROUP BY owner, opponent
        ORDER BY owner, wins DESC
    """,
    "Biggest win by owner": """
        WITH games AS (
            SELECT year, week, team1_owner AS owner, team2_owner AS opponent,
                   team1_points AS points_for, team2_points AS points_against,
                   team1_points - team2_points AS margin
            FROM matchups WHERE team1_points > team2_points
            UNION ALL
            SELECT year, week, team2_owner, team1_owner,
                   team2_points, team1_points, team2_points - team1_points
            FROM matchups WHERE team2_points > team1_points
        ), ranked AS (
            SELECT *, RANK() OVER (PARTITION BY owner ORDER BY margin DESC) AS rank_number
            FROM games
        )
        SELECT owner, year, week, opponent, points_for, points_against,
               ROUND(margin, 2) AS victory_margin
        FROM ranked
        WHERE rank_number = 1
        ORDER BY victory_margin DESC
    """,
    "Biggest loss by owner": """
        WITH games AS (
            SELECT year, week, team1_owner AS owner, team2_owner AS opponent,
                   team1_points AS points_for, team2_points AS points_against,
                   team2_points - team1_points AS margin
            FROM matchups WHERE team1_points < team2_points
            UNION ALL
            SELECT year, week, team2_owner, team1_owner,
                   team2_points, team1_points, team1_points - team2_points
            FROM matchups WHERE team2_points < team1_points
        ), ranked AS (
            SELECT *, RANK() OVER (PARTITION BY owner ORDER BY margin DESC) AS rank_number
            FROM games
        )
        SELECT owner, year, week, opponent, points_for, points_against,
               ROUND(margin, 2) AS loss_margin
        FROM ranked
        WHERE rank_number = 1
        ORDER BY loss_margin DESC
    """,
    "Closest matchup by opponent pair": """
        WITH games AS (
            SELECT year, week, team1_owner AS owner, team2_owner AS opponent,
                   team1_points AS points_for, team2_points AS points_against,
                   ABS(team1_points - team2_points) AS margin
            FROM matchups
            UNION ALL
            SELECT year, week, team2_owner, team1_owner,
                   team2_points, team1_points, ABS(team2_points - team1_points)
            FROM matchups
        ), ranked AS (
            SELECT *, RANK() OVER (
                PARTITION BY owner, opponent ORDER BY margin
            ) AS rank_number
            FROM games
        )
        SELECT owner, opponent, year, week, points_for, points_against,
               ROUND(margin, 2) AS closest_margin
        FROM ranked
        WHERE rank_number = 1
        ORDER BY owner, closest_margin
    """,
    "Last meeting by opponent pair": """
        WITH games AS (
            SELECT year, week, team1_owner AS owner, team2_owner AS opponent,
                   team1_points AS points_for, team2_points AS points_against
            FROM matchups
            UNION ALL
            SELECT year, week, team2_owner, team1_owner,
                   team2_points, team1_points
            FROM matchups
        ), ranked AS (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY owner, opponent ORDER BY year DESC, week DESC
            ) AS row_number
            FROM games
        )
        SELECT owner, opponent, year, week, points_for, points_against,
               CASE WHEN points_for > points_against THEN 'W'
                    WHEN points_for < points_against THEN 'L' ELSE 'T' END AS result
        FROM ranked
        WHERE row_number = 1
        ORDER BY owner, opponent
    """,
    "Current average vs career average": all_scores_cte() + """,
        career_average AS (
            SELECT team_owner, AVG(points) AS career_avg
            FROM all_scores GROUP BY team_owner
        ), current_average AS (
            SELECT team_owner, AVG(points) AS current_avg
            FROM all_scores
            WHERE year = (SELECT MAX(year) FROM all_scores)
            GROUP BY team_owner
        )
        SELECT
            current.team_owner,
            ROUND(current.current_avg, 2) AS current_avg,
            ROUND(career.career_avg, 2) AS career_avg,
            ROUND(current.current_avg - career.career_avg, 2) AS difference_from_career_avg
        FROM current_average current
        JOIN career_average career ON current.team_owner = career.team_owner
        ORDER BY difference_from_career_avg DESC
    """,
    "Current season rank vs owner history": all_scores_cte() + """,
        season_averages AS (
            SELECT year, team_owner, ROUND(AVG(points), 2) AS avg_score
            FROM all_scores GROUP BY year, team_owner
        ), ranked_seasons AS (
            SELECT *,
                   RANK() OVER (PARTITION BY team_owner ORDER BY avg_score DESC) AS season_rank,
                   COUNT(*) OVER (PARTITION BY team_owner) AS total_seasons
            FROM season_averages
        )
        SELECT team_owner, year AS current_year, avg_score AS current_avg_score,
               season_rank, total_seasons,
               season_rank || ' of ' || total_seasons AS current_rank_vs_history
        FROM ranked_seasons
        WHERE year = (SELECT MAX(year) FROM all_scores)
        ORDER BY season_rank, team_owner
    """,
}


def render_overview() -> None:
    latest_year = int(run_query("SELECT MAX(year) AS year FROM standings").iloc[0]["year"])
    standings = run_query(
        """
        WITH names_raw AS (
            SELECT year, team1_key AS team_key, team1_name AS team_name
            FROM matchups
            UNION ALL
            SELECT year, team2_key AS team_key, team2_name AS team_name
            FROM matchups
        ), team_names AS (
            SELECT year, team_key, MAX(team_name) AS team_name
            FROM names_raw
            GROUP BY year, team_key
        )
        SELECT s.team_owner, COALESCE(n.team_name, '') AS team_name,
               s.wins, s.losses, s.playoff_wins, s.playoff_losses,
               s.total_wins, s.total_losses, s.ties
        FROM standings s
        LEFT JOIN team_names n ON s.year = n.year AND s.team_key = n.team_key
        WHERE s.year = ?
        ORDER BY s.wins DESC, s.losses, s.team_owner
        """,
        (latest_year,),
    )
    champion_count = int(run_query("SELECT COUNT(*) AS count FROM champions").iloc[0]["count"])
    matchup_count = int(run_query("SELECT COUNT(*) AS count FROM matchups").iloc[0]["count"])

    st.title("The Legendary League")
    st.caption(f"League history through the {latest_year} season")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest season", latest_year)
    col2.metric("Seasons", champion_count)
    col3.metric("Owners", len(run_query("SELECT DISTINCT team_owner FROM standings")))
    col4.metric("Matchups", f"{matchup_count:,}")

    left, right = st.columns([1.5, 1])
    with left:
        with st.container(border=True):
            st.subheader(f"{latest_year} standings")
            format_table(standings)
    with right:
        with st.container(border=True):
            st.subheader("League champions")
            champions = run_query(
                """
                SELECT c.year, s.team_owner, c.team_name, c.wins, c.losses
                FROM champions c
                LEFT JOIN standings s ON c.year = s.year AND c.team_key = s.team_key
                ORDER BY c.year DESC
                """
            )
            format_table(champions)

    with st.container(border=True):
        st.subheader("All-time wins")
        career_wins = run_query(QUERY_LIBRARY["Career wins (including playoffs)"])
        career_wins = career_wins.sort_values(
            "career_wins", ascending=False
        ).reset_index(drop=True)
        ordered_bar_chart(
            career_wins,
            category="team_owner",
            value="career_wins",
            category_title="Owner",
            value_title="Career wins",
        )


def render_owner_history() -> None:
    st.title("Owner History")
    owners = run_query(
        "SELECT DISTINCT team_owner FROM standings WHERE team_owner <> '' ORDER BY team_owner"
    )["team_owner"].tolist()
    with st.container(border=True):
        st.caption("OWNER FILTER")
        selected_owner = st.selectbox(dropdown_label("owner"), owners)

    summary = run_query(
        """
        SELECT
            COUNT(DISTINCT year) AS seasons,
            SUM(total_wins) AS wins,
            SUM(total_losses) AS losses,
            SUM(ties) AS ties,
            SUM(playoff_wins) AS playoff_wins,
            SUM(playoff_losses) AS playoff_losses
        FROM standings WHERE team_owner = ?
        """,
        (selected_owner,),
    ).iloc[0]
    titles = run_query(
        """
        SELECT COUNT(*) AS titles
        FROM champions c JOIN standings s
          ON c.year = s.year AND c.team_key = s.team_key
        WHERE s.team_owner = ?
        """,
        (selected_owner,),
    ).iloc[0]["titles"]

    cols = st.columns(6)
    cols[0].metric("Seasons", int(summary["seasons"]))
    cols[1].metric("Wins", int(summary["wins"]))
    cols[2].metric("Losses", int(summary["losses"]))
    cols[3].metric("Playoff wins", int(summary["playoff_wins"]))
    cols[4].metric("Playoff losses", int(summary["playoff_losses"]))
    cols[5].metric("Championships", int(titles))

    history = run_query(
        """
        SELECT year, wins, losses, playoff_wins, playoff_losses,
               total_wins, total_losses, ties
        FROM standings WHERE team_owner = ? ORDER BY year
        """,
        (selected_owner,),
    )
    left, right = st.columns([1.2, 1])
    with left:
        with st.container(border=True):
            st.subheader("Season results")
            season_chart = history[["year", "wins", "total_wins"]].copy()
            season_chart["year"] = season_chart["year"].astype(str)
            themed_line_chart(
                season_chart,
                x="year",
                series=["wins", "total_wins"],
                x_title="Season",
                y_title="Wins",
            )
    with right:
        with st.container(border=True):
            st.subheader("Season-by-season record")
            format_table(history)

    with st.container(border=True):
        st.subheader("Career leaderboards")
        leaderboard = st.selectbox(
            dropdown_label("leaderboard"),
            [
                "Career win rate (minimum 3 seasons)",
                "Career wins (including playoffs)",
                "Career losses (including playoffs)",
                "Seasons played",
                "Championships",
                "Playoff wins",
                "Playoff losses",
                "Average wins per season",
            ],
        )
        format_table(run_query(QUERY_LIBRARY[leaderboard]))


def render_scoring_history() -> None:
    st.title("Scoring History")
    years = run_query("SELECT DISTINCT year FROM matchups ORDER BY year DESC")["year"].tolist()
    owners = run_query(
        """
        SELECT owner FROM (
            SELECT team1_owner AS owner FROM matchups
            UNION SELECT team2_owner FROM matchups
        ) WHERE owner <> '' ORDER BY owner
        """
    )["owner"].tolist()
    with st.container(border=True):
        st.caption("SCORING FILTERS")
        col1, col2 = st.columns([1, 2])
        selected_year = col1.selectbox(
            dropdown_label("season"), years, key="scoring_chart_season"
        )
        default_owners = owners[: min(5, len(owners))]
        selected_owners = col2.multiselect(
            dropdown_label("one or more owners"),
            owners,
            default=default_owners,
            key="scoring_chart_owners",
        )

    placeholders = ",".join("?" for _ in selected_owners)
    if selected_owners:
        scores = run_query(
            all_scores_cte()
            + f"""
            SELECT year, week, team_owner, points
            FROM all_scores
            WHERE year = ? AND team_owner IN ({placeholders})
            ORDER BY week, team_owner
            """,
            (selected_year, *selected_owners),
        )
        chart = scores.pivot_table(index="week", columns="team_owner", values="points")
        with st.container(border=True):
            st.subheader(f"Weekly scores: {selected_year}")
            weekly_chart = chart.reset_index()
            themed_line_chart(
                weekly_chart,
                x="week",
                series=chart.columns.tolist(),
                x_title="Week",
                y_title="Points",
            )

    with st.container(border=True):
        st.subheader("Scoring records")
        record_query = st.selectbox(
            dropdown_label("scoring record"),
            [
                "Average weekly score by season",
                "Highest weekly score by owner and season",
                "Lowest weekly score by owner and season",
                "Weekly scoring change",
                "Season total scoring trend",
                "Season average scoring trend",
            ],
            key="scoring_record_type",
        )
        record_filters = st.columns(2)
        record_year = record_filters[0].selectbox(
            dropdown_label("record season"),
            ["All seasons", *years],
            key="scoring_record_season",
        )
        record_owner = record_filters[1].selectbox(
            dropdown_label("record owner"),
            ["All owners", *owners],
            key="scoring_record_owner",
        )

        record_data = run_query(QUERY_LIBRARY[record_query])
        if record_year != "All seasons" and "year" in record_data.columns:
            record_data = record_data[record_data["year"] == record_year]
        if record_owner != "All owners" and "team_owner" in record_data.columns:
            record_data = record_data[record_data["team_owner"] == record_owner]

        st.caption(f"{len(record_data):,} matching rows")
        format_table(record_data)


def render_head_to_head() -> None:
    st.title("Head-to-Head")
    owners = run_query(
        """
        SELECT owner FROM (
            SELECT team1_owner AS owner FROM matchups
            UNION SELECT team2_owner FROM matchups
        ) WHERE owner <> '' ORDER BY owner
        """
    )["owner"].tolist()
    years = run_query("SELECT DISTINCT year FROM matchups ORDER BY year DESC")["year"].tolist()
    with st.container(border=True):
        st.caption("MATCHUP FILTERS")
        col1, col2, col3 = st.columns(3)
        owner = col1.selectbox(
            dropdown_label("owner"),
            ["All", *owners],
            index=0,
            key="head_to_head_owner",
        )
        opponents = owners if owner == "All" else [name for name in owners if name != owner]
        opponent = col2.selectbox(
            dropdown_label("opponent"),
            ["All", *opponents],
            index=0,
            key="head_to_head_opponent",
        )
        selected_year = col3.selectbox(
            dropdown_label("meeting history year"),
            ["All years", *years],
            index=0,
            key="head_to_head_year",
        )

    games = run_query(
        """
        WITH games AS (
            SELECT year, week, team1_owner AS owner, team2_owner AS opponent,
                   team1_points AS points_for, team2_points AS points_against,
                   playoffs
            FROM matchups
            UNION ALL
            SELECT year, week, team2_owner, team1_owner,
                   team2_points, team1_points, playoffs
            FROM matchups
        )
        SELECT *,
               CASE WHEN points_for > points_against THEN 'W'
                    WHEN points_for < points_against THEN 'L' ELSE 'T' END AS result,
               ROUND(points_for - points_against, 2) AS margin
        FROM games
        ORDER BY year DESC, week DESC
        """
    )
    if owner != "All":
        games = games[games["owner"] == owner]
    if opponent != "All":
        games = games[games["opponent"] == opponent]
    if selected_year != "All years":
        games = games[games["year"] == selected_year]

    wins = int((games["result"] == "W").sum()) if not games.empty else 0
    losses = int((games["result"] == "L").sum()) if not games.empty else 0
    ties = int((games["result"] == "T").sum()) if not games.empty else 0
    win_label = f"{owner} wins" if owner != "All" else "Selected wins"
    if opponent != "All":
        loss_label = f"{opponent} wins"
    elif owner != "All":
        loss_label = f"{owner} losses"
    else:
        loss_label = "Selected losses"
    cols = st.columns(5)
    cols[0].metric("Games", len(games))
    cols[1].metric(win_label, wins)
    cols[2].metric(loss_label, losses)
    cols[3].metric("Ties", ties)
    cols[4].metric("Average margin", f"{games['margin'].mean():.2f}" if not games.empty else "-")

    with st.container(border=True):
        st.subheader("Meeting history")
        format_table(games)

    with st.container(border=True):
        st.subheader("Matchup records")
        record_query = st.selectbox(
            dropdown_label("matchup record"),
            [
                "Head-to-head records",
                "Biggest win by owner",
                "Biggest loss by owner",
                "Closest matchup by opponent pair",
                "Last meeting by opponent pair",
            ],
            key="head_to_head_record_type",
        )
        if record_query == "Biggest win by owner":
            record_data = filtered_biggest_result(games, "W")
        elif record_query == "Biggest loss by owner":
            record_data = filtered_biggest_result(games, "L")
        else:
            record_data = run_query(QUERY_LIBRARY[record_query])
            if owner != "All" and "owner" in record_data.columns:
                record_data = record_data[record_data["owner"] == owner]
            if opponent != "All" and "opponent" in record_data.columns:
                record_data = record_data[record_data["opponent"] == opponent]

        st.caption(f"{len(record_data):,} matching rows")
        format_table(record_data)


def render_roster_matchups() -> None:
    st.title("Roster Matchups")
    owners = run_query(
        """
        SELECT owner FROM (
            SELECT team1_owner AS owner FROM matchups
            UNION SELECT team2_owner FROM matchups
        ) WHERE owner <> '' ORDER BY owner
        """
    )["owner"].tolist()
    years = run_query("SELECT DISTINCT year FROM matchups ORDER BY year DESC")["year"].tolist()

    with st.container(border=True):
        st.caption("ROSTER MATCHUP FILTERS")
        col1, col2, col3 = st.columns(3)
        selected_owner = col1.selectbox(
            dropdown_label("owner"),
            ["All", *owners],
            key="roster_matchup_owner",
        )
        opponent_options = (
            owners
            if selected_owner == "All"
            else [owner for owner in owners if owner != selected_owner]
        )
        selected_opponent = col2.selectbox(
            dropdown_label("opponent"),
            ["All", *opponent_options],
            key="roster_matchup_opponent",
        )
        selected_year = col3.selectbox(
            dropdown_label("year"),
            years,
            key="roster_matchup_year",
        )

    matchups = run_query(
        """
        SELECT
            year, week,
            team1_key, team1_owner, team1_name, team1_points,
            team2_key, team2_owner, team2_name, team2_points,
            winner_owner, playoffs
        FROM matchups
        WHERE year = ?
          AND EXISTS (
              SELECT 1
              FROM rosters r1
              WHERE r1.year = matchups.year
                AND r1.week = matchups.week
                AND r1.team_key = matchups.team1_key
                AND COALESCE(r1.selected_position, '') NOT IN ('BN', 'IR')
          )
          AND EXISTS (
              SELECT 1
              FROM rosters r2
              WHERE r2.year = matchups.year
                AND r2.week = matchups.week
                AND r2.team_key = matchups.team2_key
                AND COALESCE(r2.selected_position, '') NOT IN ('BN', 'IR')
          )
        ORDER BY week DESC, team1_owner, team2_owner
        """,
        (selected_year,),
    )
    if selected_owner != "All":
        matchups = matchups[
            (matchups["team1_owner"] == selected_owner)
            | (matchups["team2_owner"] == selected_owner)
        ]
    if selected_opponent != "All":
        matchups = matchups[
            (matchups["team1_owner"] == selected_opponent)
            | (matchups["team2_owner"] == selected_opponent)
        ]

    if matchups.empty:
        st.warning("No matchups found for those filters.")
        return

    matchups = matchups.reset_index(drop=True)
    matchup_labels = [
        (
            f"{int(row.week)} | {row.team1_owner} {row.team1_points:.2f} "
            f"vs {row.team2_owner} {row.team2_points:.2f}"
        )
        for row in matchups.itertuples()
    ]
    selected_label = st.selectbox(
        dropdown_label("week matchup"),
        matchup_labels,
        key="roster_matchup_game",
    )
    selected_matchup = matchups.iloc[matchup_labels.index(selected_label)]

    roster_detail = run_query(
        """
        SELECT
            year, week, team_owner, team_name, team_key,
            selected_position, player_name, points
        FROM rosters
        WHERE year = ?
          AND week = ?
          AND team_key IN (?, ?)
          AND COALESCE(selected_position, '') != 'IR'
        ORDER BY team_owner, selected_position, points DESC, player_name
        """,
        (
            int(selected_matchup["year"]),
            int(selected_matchup["week"]),
            selected_matchup["team1_key"],
            selected_matchup["team2_key"],
        ),
    )

    if roster_detail.empty:
        st.warning("No roster rows found for this matchup.")
        return

    starter_detail = roster_detail[roster_detail["selected_position"] != "BN"].copy()
    chart_detail = roster_detail[
        ["team_owner", "selected_position", "player_name", "points"]
    ].copy()

    if starter_detail.empty:
        st.warning("No starting roster rows found for this matchup.")
        return

    position_order = ["QB", "RB", "WR", "TE", "W/R/T", "K", "DEF", "BN"]

    score_cols = st.columns(3)
    score_cols[0].metric("Week", int(selected_matchup["week"]))
    score_cols[1].metric(
        selected_matchup["team1_owner"],
        f"{selected_matchup['team1_points']:.2f}",
    )
    score_cols[2].metric(
        selected_matchup["team2_owner"],
        f"{selected_matchup['team2_points']:.2f}",
    )

    with st.container(border=True):
        st.subheader("Position scoring comparison")
        stacked_player_position_chart(chart_detail, position_order)

    with st.container(border=True):
        st.subheader("Starting roster detail")
        comparison = roster_comparison_table(
            roster_detail[
                ["team_owner", "team_name", "selected_position", "player_name", "points"]
            ],
            position_order,
        )
        format_table(comparison)


def render_current_season() -> None:
    latest_year = int(run_query("SELECT MAX(year) AS year FROM matchups").iloc[0]["year"])
    st.title(f"Current Season: {latest_year}")

    current = run_query(
        """
        WITH names_raw AS (
            SELECT year, team1_key AS team_key, team1_name AS team_name
            FROM matchups
            UNION ALL
            SELECT year, team2_key AS team_key, team2_name AS team_name
            FROM matchups
        ), team_names AS (
            SELECT year, team_key, MAX(team_name) AS team_name
            FROM names_raw
            GROUP BY year, team_key
        )
        SELECT s.team_owner, COALESCE(n.team_name, '') AS team_name,
               s.wins, s.losses, s.ties,
               s.wins || '-' || s.losses || '-' || s.ties AS record
        FROM standings s
        LEFT JOIN team_names n ON s.year = n.year AND s.team_key = n.team_key
        WHERE s.year = ?
        ORDER BY s.wins DESC, s.losses, s.team_owner
        """,
        (latest_year,),
    )
    averages = run_query(
        all_scores_cte()
        + """
        SELECT team_owner, ROUND(AVG(points), 2) AS current_avg_score
        FROM all_scores WHERE year = ?
        GROUP BY team_owner
        """,
        (latest_year,),
    )
    comparison = run_query(QUERY_LIBRARY["Current average vs career average"])
    streaks = run_query(
        """
        WITH games AS (
            SELECT year, week, team1_owner AS owner,
                   CASE WHEN team1_points > team2_points THEN 'W'
                        WHEN team1_points < team2_points THEN 'L' ELSE 'T' END AS result
            FROM matchups
            UNION ALL
            SELECT year, week, team2_owner,
                   CASE WHEN team2_points > team1_points THEN 'W'
                        WHEN team2_points < team1_points THEN 'L' ELSE 'T' END
            FROM matchups
        )
        SELECT owner, week, result FROM games
        WHERE year = ? ORDER BY owner, week
        """,
        (latest_year,),
    )
    streak_rows = []
    for owner, owner_games in streaks.groupby("owner"):
        result, length = current_streak(owner_games.sort_values("week"))
        streak_rows.append({"team_owner": owner, "current_streak": f"{result}{length}"})
    streak_view = pd.DataFrame(streak_rows)

    season_view = current.merge(averages, on="team_owner", how="left").merge(
        comparison[["team_owner", "career_avg", "difference_from_career_avg"]],
        on="team_owner",
        how="left",
    )
    season_view = season_view.merge(streak_view, on="team_owner", how="left")
    season_view = season_view[
        [
            "team_owner", "team_name", "wins", "losses", "ties", "record",
            "current_streak",
            "current_avg_score", "career_avg", "difference_from_career_avg",
        ]
    ]
    with st.container(border=True):
        st.subheader("Current standings and scoring")
        format_table(season_view)

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("Average score")
            ordered_bar_chart(
                season_view,
                category="team_owner",
                value="current_avg_score",
                category_title="Owner",
                value_title="Average score",
            )
    with right:
        with st.container(border=True):
            st.subheader("Current season vs owner history")
            format_table(run_query(QUERY_LIBRARY["Current season rank vs owner history"]))

def render_query_library() -> None:
    st.title("Query Library")
    st.write("Browse the full set of league-history queries from your SQL document.")
    with st.container(border=True):
        query_name = st.selectbox(dropdown_label("query"), list(QUERY_LIBRARY))
        result = run_query(QUERY_LIBRARY[query_name])
        st.caption(f"{len(result):,} rows")
        format_table(result)
        with st.expander("View SQL"):
            st.code(QUERY_LIBRARY[query_name].strip(), language="sql")


if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()

st.sidebar.title("The Legendary League")
page = st.sidebar.radio(
    "Choose dashboard section",
    [
        "League Overview",
        "Current Season",
        "Owner History",
        "Scoring History",
        "Head-to-Head",
        "Roster Matchups",
        "Query Library",
    ],
)
st.sidebar.caption(f"Database: {DB_PATH.name}")

if page == "League Overview":
    render_overview()
elif page == "Owner History":
    render_owner_history()
elif page == "Scoring History":
    render_scoring_history()
elif page == "Head-to-Head":
    render_head_to_head()
elif page == "Roster Matchups":
    render_roster_matchups()
elif page == "Current Season":
    render_current_season()
else:
    render_query_library()
