"""Formulas for duration, calories, and fat estimate."""

from __future__ import annotations

from met_calculator.core.text_utils import normalize_text

KCAL_PER_KG_FAT = 7700.0
DEFAULT_SET_SECONDS = 52.5
DEFAULT_REST_SECONDS = 75.0
DEFAULT_TRANSITION_SECONDS = 15.0
DEFAULT_EXERCISE_BUFFER_SECONDS = 60.0


def detect_activity_type(raw_line: str, muscle_group: str) -> str:
    """Detect activity type from text and muscle group metadata."""
    normalized = normalize_text(raw_line)
    if "hiit" in normalized:
        return "hiit"
    if any(word in normalized for word in ["sprint", "intervalado", "interval"]):
        return "hiit"
    if normalize_text(muscle_group) == "cardio":
        return "cardio"
    return "strength"


def resolve_met(activity_type: str, raw_line: str, fallback_met: float) -> float:
    """Return realistic MET by activity type and text keywords."""
    normalized = normalize_text(raw_line)

    if activity_type == "strength":
        return 5.8

    if activity_type == "hiit":
        return 9.5

    if "corrida" in normalized or "esteira" in normalized:
        return 8.5
    if "bike" in normalized or "bicicleta" in normalized:
        return 7.0
    if "caminhada" in normalized:
        return 6.5
    if "remo" in normalized:
        return 7.0
    if "eliptico" in normalized:
        return 6.8

    if activity_type == "cardio":
        return 7.0

    return fallback_met


def estimate_duration_minutes(
    series: int,
    repetitions: int,
    seconds_per_rep: float,
    activity_type: str,
    rest_seconds: float = DEFAULT_REST_SECONDS,
    min_set_seconds: float = DEFAULT_SET_SECONDS,
) -> float:
    """Estimate exercise duration in minutes with realistic set and rest time."""
    if activity_type in {"hiit", "cardio"}:
        total_seconds = float(series * repetitions) * seconds_per_rep
        return total_seconds / 60.0

    work_per_set_seconds = max(float(repetitions) * seconds_per_rep, min_set_seconds)
    work_total_seconds = float(series) * work_per_set_seconds
    rest_total_seconds = max(0.0, float(series - 1) * rest_seconds)
    transition_seconds = float(series) * DEFAULT_TRANSITION_SECONDS
    total_seconds = (
        work_total_seconds
        + rest_total_seconds
        + transition_seconds
        + DEFAULT_EXERCISE_BUFFER_SECONDS
    )
    return total_seconds / 60.0


def calculate_calories(met: float, weight_kg: float, duration_minutes: float) -> float:
    """Calculate calories with ACSM MET based equation."""
    kcal_per_min = (met * 3.5 * weight_kg) / 200.0
    return kcal_per_min * duration_minutes


def estimate_fat_loss_kg(calories: float) -> float:
    """Estimate fat loss equivalent using 7700 kcal per kg."""
    return calories / KCAL_PER_KG_FAT
