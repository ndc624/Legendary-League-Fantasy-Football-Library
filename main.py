#!/usr/bin/env python3
"""Update Yahoo fantasy football roster, matchup, standings, and champions CSVs."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2


DEFAULT_LEAGUE_ID = "461.l.77825"
DEFAULT_ROSTER_WEEKS = [16]
DEFAULT_MATCHUP_WEEKS = [17]
DEFAULT_PROJECT_DIR = Path("/Users/noahceremony/PycharmProjects/Fantasy_App_2.0")
DEFAULT_DATA_DIR = DEFAULT_PROJECT_DIR / "data"
DEFAULT_OAUTH_FILE = DEFAULT_PROJECT_DIR / "oauth2.json"

ROSTER_CSV = "all_rosters_master.csv"
MATCHUP_CSV = "matchups_master.csv"
STANDINGS_CSV = "standings_master.csv"
CHAMPIONS_CSV = "champions.csv"

ROSTER_FIELDS = [
    "year", "week", "team_name", "team_owner", "team_key",
    "player_name", "player_id", "points", "projected_points",
    "editorial_team_abbr", "position_type", "eligible_positions",
    "selected_position", "status", "is_undroppable",
]

MATCHUP_FIELDS = [
    "year", "week",
    "team1_key", "team1_owner", "team1_name", "team1_points",
    "team2_key", "team2_owner", "team2_name", "team2_points",
    "winner_team_key", "winner_owner", "playoffs",
]

CHAMPION_FIELDS = ["year", "team_key", "team_name", "wins", "losses"]


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def owner_from_details(details: dict[str, Any]) -> str:
    try:
        return details["managers"][0]["manager"]["nickname"]
    except (KeyError, IndexError, TypeError):
        return ""


def load_csv(path: Path, fields: list[str], key_func) -> dict[tuple, dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return {}

    rows: dict[tuple, dict[str, str]] = {}
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        for source_row in csv.DictReader(csv_file):
            row = {field: source_row.get(field, "") for field in fields}
            key = key_func(row)
            if all(str(part).strip() for part in key):
                rows[key] = row
    return rows


def write_csv(
    path: Path,
    fields: list[str],
    rows: Iterable[dict[str, Any]],
    sort_key,
    backup: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup and path.exists() and path.stat().st_size > 0:
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))

    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(rows, key=sort_key))
    os.replace(temp_path, path)


def roster_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("year", "")).strip(),
        str(row.get("week", "")).strip(),
        str(row.get("team_key", "")).strip(),
        str(row.get("player_id", "")).strip(),
    )


def matchup_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    team_keys = sorted([
        str(row.get("team1_key", "")).strip(),
        str(row.get("team2_key", "")).strip(),
    ])
    return (
        str(row.get("year", "")).strip(),
        str(row.get("week", "")).strip(),
        team_keys[0],
        team_keys[1],
    )


def champion_key(row: dict[str, Any]) -> tuple[str]:
    return (str(row.get("year", "")).strip(),)


def extract_projection(value: Any) -> float | str:
    if isinstance(value, list):
        for item in value:
            result = extract_projection(item)
            if result != "":
                return result
        return ""
    if isinstance(value, dict):
        for key in ("projected_total_points", "total_points", "total"):
            if key in value and value[key] not in (None, ""):
                return safe_float(value[key])
        for key in ("projected_points", "stats"):
            if key in value:
                result = extract_projection(value[key])
                if result != "":
                    return result
    return ""


def get_weekly_projection(league, player_id: Any, week: int) -> float | str:
    try:
        stats = league.player_stats(player_id, req_type="week", week=week)
        if stats and isinstance(stats[0], dict) and "projected_points" in stats[0]:
            projection = extract_projection(stats[0]["projected_points"])
            if projection != "":
                return projection
    except Exception:
        pass

    try:
        projected_stats = league.player_stats(
            player_id,
            req_type="week",
            week=week,
            params={"is_projected": "1"},
        )
        projection = extract_projection(projected_stats)
        if projection != "":
            return projection
    except Exception:
        pass
    return ""


def update_rosters(
    league,
    year: str,
    weeks: list[int],
    output_path: Path,
    owners_by_key: dict[str, str],
    backup: bool = True,
) -> dict[str, int]:
    rows = load_csv(output_path, ROSTER_FIELDS, roster_key)
    new_count = 0
    processed = 0

    for week in weeks:
        for team_key, metadata in league.teams().items():
            team = league.to_team(team_key)
            for player in team.roster(week=week):
                player_id = player.get("player_id")
                try:
                    stats = league.player_stats(player_id, req_type="week", week=week)
                    points = safe_float(stats[0].get("total_points")) if stats else 0.0
                except Exception:
                    points = 0.0

                row = {
                    "year": year,
                    "week": week,
                    "team_name": metadata.get("name", ""),
                    "team_owner": owners_by_key.get(team_key, ""),
                    "team_key": team_key,
                    "player_name": player.get("name", ""),
                    "player_id": player_id,
                    "points": points,
                    "projected_points": get_weekly_projection(league, player_id, week),
                    "editorial_team_abbr": player.get("editorial_team_abbr", ""),
                    "position_type": player.get("position_type", ""),
                    "eligible_positions": "|".join(player.get("eligible_positions") or []),
                    "selected_position": player.get("selected_position", ""),
                    "status": player.get("status", ""),
                    "is_undroppable": player.get("is_undroppable", ""),
                }
                key = roster_key(row)
                if key not in rows:
                    new_count += 1
                else:
                    existing_owner = rows[key].get("team_owner", "")
                    if not row["team_owner"]:
                        row["team_owner"] = existing_owner
                rows[key] = row
                processed += 1

        print(f"Roster week {week}: processed {processed} rows ({new_count} new so far).")

    write_csv(
        output_path,
        ROSTER_FIELDS,
        rows.values(),
        lambda row: (
            str(row.get("year", "")),
            int(row.get("week", 0) or 0),
            str(row.get("team_name", "")),
            str(row.get("player_name", "")),
        ),
        backup,
    )
    return {"processed": processed, "new": new_count}


def team_total(team_node: Any) -> float:
    try:
        return safe_float(team_node[1]["team_points"]["total"])
    except (KeyError, IndexError, TypeError):
        return 0.0


def update_matchups(
    league,
    year: str,
    weeks: list[int],
    output_path: Path,
    owners_by_key: dict[str, str],
    backup: bool = True,
) -> dict[str, int]:
    rows = load_csv(output_path, MATCHUP_FIELDS, matchup_key)
    new_count = 0
    processed = 0

    for week in weeks:
        raw = league.matchups(week=week)
        matchups = raw["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]

        for item_key, matchup in matchups.items():
            if item_key == "count":
                continue
            try:
                teams = matchup["matchup"]["0"]["teams"]
                team1 = teams["0"]["team"]
                team2 = teams["1"]["team"]
                team1_key = team1[0][0]["team_key"]
                team2_key = team2[0][0]["team_key"]
                team1_name = team1[0][2]["name"]
                team2_name = team2[0][2]["name"]
            except (KeyError, IndexError, TypeError):
                continue

            team1_points = team_total(team1)
            team2_points = team_total(team2)
            if team1_points > team2_points:
                winner_key = team1_key
            elif team2_points > team1_points:
                winner_key = team2_key
            else:
                winner_key = "Tie"

            row = {
                "year": year,
                "week": week,
                "team1_key": team1_key,
                "team1_owner": owners_by_key.get(team1_key, ""),
                "team1_name": team1_name,
                "team1_points": team1_points,
                "team2_key": team2_key,
                "team2_owner": owners_by_key.get(team2_key, ""),
                "team2_name": team2_name,
                "team2_points": team2_points,
                "winner_team_key": winner_key,
                "winner_owner": owners_by_key.get(winner_key, "") if winner_key != "Tie" else "",
                "playoffs": "no" if week <= 14 else "yes",
            }
            key = matchup_key(row)
            if key not in rows:
                new_count += 1
            else:
                for owner_field in ("team1_owner", "team2_owner", "winner_owner"):
                    if not row[owner_field]:
                        row[owner_field] = rows[key].get(owner_field, "")
            rows[key] = row
            processed += 1

        print(f"Matchup week {week}: processed {processed} rows ({new_count} new so far).")

    write_csv(
        output_path,
        MATCHUP_FIELDS,
        rows.values(),
        lambda row: (
            str(row.get("year", "")),
            int(row.get("week", 0) or 0),
            str(row.get("team1_name", "")),
        ),
        backup,
    )
    return {"processed": processed, "new": new_count}


def update_champion(
    league,
    year: str,
    matchup_path: Path,
    output_path: Path,
    backup: bool = True,
) -> dict[str, Any]:
    """Upsert the champion only after matchup weeks 1 through 17 are logged."""
    if not matchup_path.exists() or matchup_path.stat().st_size == 0:
        print(f"Champion {year}: skipped because {matchup_path.name} is empty or missing.")
        return {"year": year, "updated": False, "missing_weeks": list(range(1, 18))}

    with matchup_path.open("r", newline="", encoding="utf-8") as csv_file:
        logged_weeks = {
            int(row["week"])
            for row in csv.DictReader(csv_file)
            if str(row.get("year", "")).strip() == str(year)
            and str(row.get("week", "")).strip().isdigit()
        }

    missing_weeks = sorted(set(range(1, 18)) - logged_weeks)
    if missing_weeks:
        missing_text = ", ".join(str(week) for week in missing_weeks)
        print(f"Champion {year}: skipped; missing matchup weeks: {missing_text}.")
        return {"year": year, "updated": False, "missing_weeks": missing_weeks}

    standings = league.standings()
    if not standings:
        raise RuntimeError(f"Yahoo returned no standings for the {year} season.")

    first_place = standings[0]
    outcome_totals = first_place.get("outcome_totals") or {}
    champion = {
        "year": year,
        "team_key": first_place.get("team_key", ""),
        "team_name": first_place.get("name", ""),
        "wins": outcome_totals.get("wins", ""),
        "losses": outcome_totals.get("losses", ""),
    }
    if not champion["team_key"]:
        raise RuntimeError(f"Yahoo returned an incomplete first-place team for {year}.")

    rows = load_csv(output_path, CHAMPION_FIELDS, champion_key)
    was_new = champion_key(champion) not in rows
    rows[champion_key(champion)] = champion
    write_csv(
        output_path,
        CHAMPION_FIELDS,
        rows.values(),
        lambda row: str(row.get("year", "")),
        backup,
    )

    print(
        f"Champion {year}: {champion['team_name']} "
        f"({champion['wins']}-{champion['losses']})."
    )
    return {**champion, "new": was_new, "updated": True, "missing_weeks": []}


def last_non_empty(series: pd.Series) -> str:
    values = series.dropna().astype(str)
    values = values[values.str.strip() != ""]
    return values.iloc[-1] if len(values) else ""


def list_available_leagues(game) -> list[dict[str, str]]:
    """Return and print every NFL league available to the Yahoo account."""
    leagues: list[dict[str, str]] = []
    print("\nYahoo NFL leagues available to this account:")
    for league_id in game.league_ids():
        try:
            settings = game.to_league(league_id).settings()
            league = {
                "league_id": str(league_id),
                "season": str(settings.get("season", "Unknown")),
                "name": str(settings.get("name", "Unknown")),
            }
        except Exception as error:
            league = {
                "league_id": str(league_id),
                "season": "Unknown",
                "name": f"Unable to load settings: {error}",
            }
        leagues.append(league)

    leagues.sort(key=lambda item: (item["season"], item["name"], item["league_id"]))
    for item in leagues:
        print(f"  {item['season']} | {item['league_id']} | {item['name']}")
    print()
    return leagues


def build_standings(matchup_path: Path, standings_path: Path) -> int:
    matchups = pd.read_csv(matchup_path, dtype=str, quoting=csv.QUOTE_MINIMAL)
    missing = [field for field in MATCHUP_FIELDS if field not in matchups.columns]
    if missing:
        raise ValueError(f"Missing required columns in {matchup_path}: {missing}")

    matchups["team1_points"] = pd.to_numeric(matchups["team1_points"], errors="coerce")
    matchups["team2_points"] = pd.to_numeric(matchups["team2_points"], errors="coerce")
    matchups["is_playoff"] = matchups["playoffs"].astype(str).str.strip().str.lower().ne("no")

    winner_blank = matchups["winner_team_key"].fillna("").astype(str).str.strip().isin(["", "nan", "none"])
    valid_points = matchups["team1_points"].notna() & matchups["team2_points"].notna()
    inferred = np.where(
        ~valid_points,
        "",
        np.where(
            matchups["team1_points"] > matchups["team2_points"],
            matchups["team1_key"],
            np.where(
                matchups["team2_points"] > matchups["team1_points"],
                matchups["team2_key"],
                "Tie",
            ),
        ),
    )
    matchups.loc[winner_blank, "winner_team_key"] = inferred[winner_blank]

    side1 = matchups.assign(
        team_key=matchups["team1_key"],
        team_owner=matchups["team1_owner"],
    )
    side2 = matchups.assign(
        team_key=matchups["team2_key"],
        team_owner=matchups["team2_owner"],
    )
    games = pd.concat([side1, side2], ignore_index=True)
    winner = games["winner_team_key"].astype(str)
    is_tie = winner.eq("Tie")
    is_win = ~is_tie & games["team_key"].astype(str).eq(winner)
    is_loss = ~is_tie & ~is_win
    games["regular_win"] = (is_win & ~games["is_playoff"]).astype(int)
    games["playoff_win"] = (is_win & games["is_playoff"]).astype(int)
    games["regular_loss"] = (is_loss & ~games["is_playoff"]).astype(int)
    games["playoff_loss"] = (is_loss & games["is_playoff"]).astype(int)
    games["tie"] = is_tie.astype(int)

    standings = games.groupby(["year", "team_key"], as_index=False).agg(
        wins=("regular_win", "sum"),
        playoff_wins=("playoff_win", "sum"),
        losses=("regular_loss", "sum"),
        playoff_losses=("playoff_loss", "sum"),
        ties=("tie", "sum"),
        team_owner=("team_owner", last_non_empty),
    )
    standings["total_wins"] = standings["wins"] + standings["playoff_wins"]
    standings["total_losses"] = standings["losses"] + standings["playoff_losses"]
    standings = standings[[
        "year", "team_owner", "team_key", "wins", "playoff_wins",
        "total_wins", "losses", "playoff_losses", "total_losses", "ties",
    ]].sort_values(
        ["year", "total_wins", "wins", "total_losses", "team_owner"],
        ascending=[True, False, False, True, True],
    )
    standings.to_csv(standings_path, index=False)
    return len(standings)


def run_updates(
    data_dir: str | Path = DEFAULT_DATA_DIR,
    oauth_file: str | Path = DEFAULT_OAUTH_FILE,
    league_id: str = DEFAULT_LEAGUE_ID,
    roster_weeks: list[int] | None = None,
    matchup_weeks: list[int] | None = None,
    backup: bool = True,
) -> dict[str, Any]:
    data_path = Path(data_dir).expanduser().resolve()
    oauth_path = Path(oauth_file).expanduser()
    if not oauth_path.is_absolute():
        oauth_path = data_path / oauth_path

    oauth = OAuth2(None, None, from_file=str(oauth_path))
    game = yfa.Game(oauth, "nfl")
    available_leagues = list_available_leagues(game)

    available_ids = {item["league_id"] for item in available_leagues}
    if league_id not in available_ids:
        print(
            f"Warning: selected league {league_id} was not returned by "
            "Yahoo's league list. Attempting to use it anyway."
        )
    print(f"Selected league for CSV updates: {league_id}\n")

    league = game.to_league(league_id)
    year = str(league.settings()["season"])

    owners_by_key = {
        team_key: owner_from_details(league.to_team(team_key).details())
        for team_key in league.teams()
    }

    matchup_result = update_matchups(
        league,
        year,
        matchup_weeks or DEFAULT_MATCHUP_WEEKS,
        data_path / MATCHUP_CSV,
        owners_by_key,
        backup,
    )
    roster_result = update_rosters(
        league,
        year,
        roster_weeks or DEFAULT_ROSTER_WEEKS,
        data_path / ROSTER_CSV,
        owners_by_key,
        backup,
    )
    standings_count = build_standings(data_path / MATCHUP_CSV, data_path / STANDINGS_CSV)
    champion_result = update_champion(
        league,
        year,
        data_path / MATCHUP_CSV,
        data_path / CHAMPIONS_CSV,
        backup,
    )

    return {
        "year": year,
        "league_id": league_id,
        "available_leagues": available_leagues,
        "matchups": matchup_result,
        "rosters": roster_result,
        "standings_rows": standings_count,
        "champion": champion_result,
    }


def parse_weeks(value: str) -> list[int]:
    weeks: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = (int(item.strip()) for item in part.split("-", 1))
            weeks.update(range(start, end + 1))
        else:
            weeks.add(int(part))
    if not weeks or min(weeks) < 1:
        raise argparse.ArgumentTypeError("Weeks must be positive numbers, such as 17 or 1-17.")
    return sorted(weeks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        default=str(DEFAULT_DATA_DIR),
        help="Directory containing the four CSV files.",
    )
    parser.add_argument(
        "--oauth-file",
        default=str(DEFAULT_OAUTH_FILE),
        help="Yahoo OAuth JSON path.",
    )
    parser.add_argument("--league-id", default=DEFAULT_LEAGUE_ID)
    parser.add_argument("--roster-weeks", type=parse_weeks, default=DEFAULT_ROSTER_WEEKS)
    parser.add_argument("--matchup-weeks", type=parse_weeks, default=DEFAULT_MATCHUP_WEEKS)
    parser.add_argument("--no-backup", action="store_true", help="Do not create .bak files.")
    args = parser.parse_args()

    result = run_updates(
        data_dir=args.data_dir,
        oauth_file=args.oauth_file,
        league_id=args.league_id,
        roster_weeks=args.roster_weeks,
        matchup_weeks=args.matchup_weeks,
        backup=not args.no_backup,
    )
    champion_summary = (
        result["champion"]["team_name"]
        if result["champion"]["updated"]
        else "not updated (season incomplete)"
    )
    print(
        f"Finished {result['year']}: "
        f"{result['matchups']['processed']} matchups, "
        f"{result['rosters']['processed']} roster rows, "
        f"{result['standings_rows']} standings rows, "
        f"champion {champion_summary}."
    )


if __name__ == "__main__":
    main()
