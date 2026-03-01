"""Dataclasses used by parser, calculator, and history services."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Exercise:
    """Static exercise metadata from internal database."""

    name: str
    keywords: list[str]
    met: float
    seconds_per_rep: float
    muscle_group: str


@dataclass
class ParsedLine:
    """Structured parsed line extracted from free text."""

    raw_line: str
    normalized_line: str
    series: int
    repetitions: int
    exercise: Exercise
    explicit_duration_minutes: float | None = None
    isometry_seconds: float = 0.0
    is_conjugated: bool = False
    conjugated_count: int = 1


@dataclass
class WorkoutItem:
    """Calculated result for one recognized line."""

    raw_line: str
    exercise_name: str
    muscle_group: str
    series: int
    repetitions: int
    met: float
    seconds_per_rep: float
    duration_minutes: float
    calories: float
    fat_loss_kg: float


@dataclass
class WorkoutSummary:
    """Aggregated workout output for one full text input."""

    created_at: str
    weight_kg: float
    source_text: str
    items: list[WorkoutItem]
    ignored_lines: list[str]
    total_duration_minutes: float
    total_calories: float
    total_fat_loss_kg: float
