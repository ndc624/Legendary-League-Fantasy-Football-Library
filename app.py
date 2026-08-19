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
