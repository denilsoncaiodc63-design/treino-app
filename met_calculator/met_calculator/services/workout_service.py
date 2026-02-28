"""Service that orchestrates parser and calculator for workout summaries."""

from __future__ import annotations

import re
from datetime import datetime

from met_calculator.core.calculator import (
    calculate_calories,
    detect_activity_type,
    estimate_duration_minutes,
    estimate_fat_loss_kg,
    resolve_met,
)
from met_calculator.core.models import WorkoutItem, WorkoutSummary
from met_calculator.core.parser import parse_workout_text
from met_calculator.core.text_utils import normalize_text

DURATION_PATTERN = re.compile(r"(?P<minutes>\d+(?:[.,]\d+)?)\s*(?:min|mins|m|minutos?)")


def _extract_duration_minutes(raw_line: str) -> float | None:
    """Extract duration in minutes from free text line."""
    normalized = normalize_text(raw_line)
    match = DURATION_PATTERN.search(normalized)
    if not match:
        return None
    minutes_text = match.group("minutes").replace(",", ".")
    return float(minutes_text)


def _duration_line_met_and_name(raw_line: str) -> tuple[str, float, str] | None:
    """Map duration based lines to activity type, met, and display name."""
    normalized = normalize_text(raw_line)

    if "hiit" in normalized:
        return "hiit", 9.5, "HIIT"
    if "bike" in normalized or "bicicleta" in normalized:
        return "cardio", 7.0, "Bicicleta"
    if "esteira" in normalized:
        return "cardio", 8.5, "Esteira"
    if "corrida" in normalized:
        return "cardio", 8.5, "Corrida"
    if "eliptico" in normalized:
        return "cardio", 6.8, "Eliptico"
    if "remo" in normalized:
        return "cardio", 7.0, "Remo"
    if "cardio" in normalized:
        return "cardio", 7.0, "Cardio"

    return None


class WorkoutService:
    """High level use case for free text workout calculation."""

    def calculate_workout_from_text(self, weight_kg: float, workout_text: str) -> WorkoutSummary:
        """Create one complete workout summary from free text input."""
        parsed_items, ignored_lines = parse_workout_text(workout_text)

        items: list[WorkoutItem] = []
        total_duration = 0.0
        total_calories = 0.0
        total_fat = 0.0
        consumed_lines: set[str] = set()

        for parsed in parsed_items:
            activity_type = detect_activity_type(
                raw_line=parsed.raw_line,
                muscle_group=parsed.exercise.muscle_group,
            )
            met = resolve_met(
                activity_type=activity_type,
                raw_line=parsed.raw_line,
                fallback_met=parsed.exercise.met,
            )
            if parsed.is_conjugated:
                multiplier = 1.0 + (0.3 * max(0, parsed.conjugated_count - 1))
                met = min(met * multiplier, 10.0)

            duration_minutes = parsed.explicit_duration_minutes
            if duration_minutes is None:
                duration_minutes = estimate_duration_minutes(
                    series=parsed.series,
                    repetitions=parsed.repetitions,
                    seconds_per_rep=parsed.exercise.seconds_per_rep,
                    activity_type=activity_type,
                )
            if parsed.isometry_seconds > 0:
                duration_minutes += (parsed.isometry_seconds * parsed.series) / 60.0
            calories = calculate_calories(
                met=met,
                weight_kg=weight_kg,
                duration_minutes=duration_minutes,
            )
            fat_loss_kg = estimate_fat_loss_kg(calories)

            total_duration += duration_minutes
            total_calories += calories
            total_fat += fat_loss_kg

            items.append(
                WorkoutItem(
                    raw_line=parsed.raw_line,
                    exercise_name=parsed.exercise.name,
                    muscle_group=parsed.exercise.muscle_group,
                    series=parsed.series,
                    repetitions=parsed.repetitions,
                    met=met,
                    seconds_per_rep=parsed.exercise.seconds_per_rep,
                    duration_minutes=duration_minutes,
                    calories=calories,
                    fat_loss_kg=fat_loss_kg,
                )
            )
            consumed_lines.add(parsed.raw_line)

        for raw_line in workout_text.splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped in consumed_lines:
                continue

            minutes = _extract_duration_minutes(stripped)
            if minutes is None or minutes <= 0:
                continue

            mapped = _duration_line_met_and_name(stripped)
            if mapped is None:
                continue

            activity_type, base_met, display_name = mapped
            met = resolve_met(
                activity_type=activity_type,
                raw_line=stripped,
                fallback_met=base_met,
            )
            duration_minutes = minutes
            calories = calculate_calories(
                met=met,
                weight_kg=weight_kg,
                duration_minutes=duration_minutes,
            )
            fat_loss_kg = estimate_fat_loss_kg(calories)

            total_duration += duration_minutes
            total_calories += calories
            total_fat += fat_loss_kg

            items.append(
                WorkoutItem(
                    raw_line=stripped,
                    exercise_name=display_name,
                    muscle_group="Cardio" if activity_type != "strength" else "Strength",
                    series=1,
                    repetitions=int(round(minutes)),
                    met=met,
                    seconds_per_rep=60.0,
                    duration_minutes=duration_minutes,
                    calories=calories,
                    fat_loss_kg=fat_loss_kg,
                )
            )
            consumed_lines.add(stripped)

        final_ignored_lines = [line for line in ignored_lines if line not in consumed_lines]

        return WorkoutSummary(
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            weight_kg=weight_kg,
            source_text=workout_text,
            items=items,
            ignored_lines=final_ignored_lines,
            total_duration_minutes=total_duration,
            total_calories=total_calories,
            total_fat_loss_kg=total_fat,
        )
