"""Intelligent parser for free text workout input."""

from __future__ import annotations

import re

from met_calculator.core.models import Exercise, ParsedLine
from met_calculator.core.text_utils import normalize_text
from met_calculator.data.exercises import EXERCISES

SERIES_REPS_X_PATTERN = re.compile(
    r"(?P<series_min>\d+)(?:\s*-\s*(?P<series_max>\d+))?\s*x\s*"
    r"(?P<reps_min>\d+)(?:\s*-\s*(?P<reps_max>\d+))?"
)
SERIES_PATTERN = re.compile(
    r"(?P<series_min>\d+)(?:\s*-\s*(?P<series_max>\d+))?\s*"
    r"(?:serie|series|s)\b"
)
REPS_PATTERN = re.compile(
    r"(?P<reps_min>\d+)(?:\s*-\s*(?P<reps_max>\d+))?\s*"
    r"(?:rep|reps|repeticao|repeticoes)\b"
)
DURATION_MIN_PATTERN = re.compile(
    r"(?P<minutes>\d+(?:[.,]\d+)?)\s*(?:min|minuto|minutos|m)\b"
)
DURATION_CLOCK_PATTERN = re.compile(r"(?P<minutes>\d+)'\s*(?P<seconds>\d{1,2})?''?")
ISOMETRY_PATTERN = re.compile(
    r"(?P<min>\d+)(?:\s*-\s*(?P<max>\d+))?\s*s(?:eg)?\s*isometria"
)
DETAIL_LINE_HINT_PATTERN = re.compile(
    r"\b(x|serie|series|rep|reps|min|minuto|minutos|isometria)\b"
)

ABBREVIATIONS: dict[str, str] = {
    "hack": "hack machine",
    "step-up": "step up",
    "extensora": "extensora",
    "abducao": "abducao quadril",
    "aducao": "adutora maquina",
    "panturrilha": "panturrilha em pe",
}

FALLBACK_KEYWORDS: dict[str, str] = {
    "hack": "hack machine",
    "hack squat": "hack machine",
    "scott": "rosca direta",
    "remada unilateral": "remada unilateral halter",
    "pull": "pull down",
    "voador": "crucifixo",
    "triceps": "triceps testa",
    "tricep": "triceps testa",
    "abdom": "sit up",
}


def _resolve_series_value(min_value: str, max_value: str | None) -> int:
    """Resolve series range using the highest value."""
    low = int(min_value)
    if max_value is None:
        return low
    high = int(max_value)
    return max(low, high)


def _resolve_repetitions_value(min_value: str, max_value: str | None) -> int:
    """Resolve repetition range using rounded average."""
    low = int(min_value)
    if max_value is None:
        return low
    high = int(max_value)
    if high < low:
        low, high = high, low
    return int((low + high) / 2.0 + 0.5)


def _line_looks_like_detail(normalized_line: str) -> bool:
    """Check whether a line is likely a details line."""
    return bool(DETAIL_LINE_HINT_PATTERN.search(normalized_line))


def _is_non_relevant_line(normalized_line: str) -> bool:
    """Ignore headers, comments, and plain section titles."""
    if not normalized_line:
        return True
    if normalized_line.startswith("#"):
        return True
    if "treino" in normalized_line and not any(ch.isdigit() for ch in normalized_line):
        return True
    if normalized_line.startswith("obs"):
        return True
    if normalized_line.startswith("comentario"):
        return True
    if normalized_line.startswith("ou "):
        return True
    return False


def _extract_series_and_reps(normalized_text: str) -> tuple[int, int, bool]:
    """Extract series and repetitions, supporting x and textual formats."""
    x_match = SERIES_REPS_X_PATTERN.search(normalized_text)
    if x_match:
        return (
            _resolve_series_value(x_match.group("series_min"), x_match.group("series_max")),
            _resolve_repetitions_value(x_match.group("reps_min"), x_match.group("reps_max")),
            True,
        )

    series = 3
    reps = 10
    found = False

    s_match = SERIES_PATTERN.search(normalized_text)
    if s_match:
        series = _resolve_series_value(s_match.group("series_min"), s_match.group("series_max"))
        found = True

    r_match = REPS_PATTERN.search(normalized_text)
    if r_match:
        reps = _resolve_repetitions_value(r_match.group("reps_min"), r_match.group("reps_max"))
        found = True

    return series, reps, found


def _extract_duration_minutes(normalized_text: str) -> float | None:
    """Extract duration in minutes from textual formats."""
    min_match = DURATION_MIN_PATTERN.search(normalized_text)
    if min_match:
        return float(min_match.group("minutes").replace(",", "."))

    clock_match = DURATION_CLOCK_PATTERN.search(normalized_text)
    if not clock_match:
        return None

    minutes = float(clock_match.group("minutes"))
    seconds = float(clock_match.group("seconds") or 0.0)
    return minutes + (seconds / 60.0)


def _extract_isometry_seconds(normalized_text: str) -> float:
    """Extract isometry hold seconds from patterns like 5-10s isometria."""
    match = ISOMETRY_PATTERN.search(normalized_text)
    if not match:
        return 0.0

    low = float(match.group("min"))
    high_text = match.group("max")
    if high_text is None:
        base = low
    else:
        high = float(high_text)
        if high < low:
            low, high = high, low
        base = (low + high) / 2.0

    repeats = 1.0
    if "inicio" in normalized_text and "final" in normalized_text:
        repeats = 2.0

    return base * repeats


def _expand_abbreviations(normalized_text: str) -> str:
    """Expand known abbreviations before matching against exercise DB."""
    expanded = normalized_text
    for short, full in ABBREVIATIONS.items():
        if short in expanded:
            expanded = expanded.replace(short, full)
    return expanded


def _find_exercise(normalized_line: str, exercises: list[Exercise]) -> Exercise | None:
    """Find best exercise using longest keyword match in line text."""
    best_exercise: Exercise | None = None
    best_keyword_size = -1

    for exercise in exercises:
        for keyword in exercise.keywords:
            if keyword in normalized_line:
                size = len(keyword)
                if size > best_keyword_size:
                    best_keyword_size = size
                    best_exercise = exercise

    if best_exercise is not None:
        return best_exercise

    # Fallback path for partial names and common aliases.
    for alias, canonical in FALLBACK_KEYWORDS.items():
        if alias in normalized_line:
            for exercise in exercises:
                if canonical in normalize_text(exercise.name):
                    return exercise

    return best_exercise


def parse_workout_text(workout_text: str) -> tuple[list[ParsedLine], list[str]]:
    """Parse workout text into recognized lines and ignored raw lines."""
    parsed_items: list[ParsedLine] = []
    ignored_lines: list[str] = []

    lines = workout_text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue

        normalized_line = normalize_text(
            line.replace("\u2013", "-").replace("\u2014", "-")
        )
        normalized_line = _expand_abbreviations(normalized_line)
        if _is_non_relevant_line(normalized_line):
            index += 1
            continue

        detail_line = ""
        detail_normalized = ""
        if index + 1 < len(lines):
            candidate = lines[index + 1].strip()
            candidate_normalized = normalize_text(
                candidate.replace("\u2013", "-").replace("\u2014", "-")
            )
            if _line_looks_like_detail(candidate_normalized):
                detail_line = candidate
                detail_normalized = candidate_normalized
                index += 1

        metrics_text = normalized_line
        if detail_normalized:
            metrics_text = f"{normalized_line} | {detail_normalized}"

        series, repetitions, has_series_reps = _extract_series_and_reps(metrics_text)
        explicit_duration = _extract_duration_minutes(metrics_text)
        isometry_seconds = _extract_isometry_seconds(metrics_text)
        if series <= 0 or repetitions <= 0:
            ignored_lines.append(line)
            index += 1
            continue

        split_items = [part.strip() for part in normalized_line.split("+") if part.strip()]
        if not split_items:
            split_items = [normalized_line]

        raw_source = line
        found_any = False
        is_conjugated = len(split_items) > 1
        conjugated_count = len(split_items)

        for split_item in split_items:
            exercise = _find_exercise(split_item, EXERCISES)
            if exercise is None:
                continue

            # Keep duration-driven cardio lines for the dedicated service path.
            if explicit_duration is not None and not has_series_reps and exercise.muscle_group == "Cardio":
                continue

            parsed_items.append(
                ParsedLine(
                    raw_line=raw_source,
                    normalized_line=split_item,
                    series=series,
                    repetitions=repetitions,
                    exercise=exercise,
                    explicit_duration_minutes=explicit_duration,
                    isometry_seconds=isometry_seconds,
                    is_conjugated=is_conjugated,
                    conjugated_count=conjugated_count,
                )
            )
            found_any = True

        if not found_any:
            ignored_lines.append(line)

        index += 1

    return parsed_items, ignored_lines
