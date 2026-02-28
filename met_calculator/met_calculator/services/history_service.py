"""In memory history service for workout summaries."""

from __future__ import annotations

from met_calculator.core.models import WorkoutSummary


class HistoryService:
    """Store workout summaries in memory for current session."""

    _history: list[WorkoutSummary] = []

    def save_workout(self, workout: WorkoutSummary) -> None:
        """Append one workout summary to in memory history."""
        self._history.append(workout)

    def list_workouts(self) -> list[WorkoutSummary]:
        """Return a copy of current history list."""
        return list(self._history)
