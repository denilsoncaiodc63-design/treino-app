"""Plotly chart render functions for history visualizations."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from met_calculator.core.models import WorkoutItem, WorkoutSummary

GROUP_COLORS: dict[str, str] = {
    "Peito": "#F97316",
    "Costas": "#2563EB",
    "Ombro": "#F59E0B",
    "Triceps": "#22C55E",
    "Biceps": "#FB7185",
    "Antebraco": "#A16207",
    "Quadriceps": "#7C3AED",
    "Posterior": "#6B7280",
    "Gluteo": "#EC4899",
    "Adutor": "#111827",
    "Abdutor": "#374151",
    "Adutor Abdutor": "#4B5563",
    "Panturrilha": "#EAB308",
    "Cardio": "#DC2626",
    "Strength": "#0EA5E9",
}


def render_workout_group_chart(items: list[WorkoutItem]) -> None:
    """Render calories by muscle group for one workout."""
    calories_by_group: dict[str, float] = {}
    for item in items:
        calories_by_group[item.muscle_group] = calories_by_group.get(item.muscle_group, 0.0) + item.calories

    groups = list(calories_by_group.keys())
    calories = [calories_by_group[group] for group in groups]
    colors = [GROUP_COLORS.get(group, "#64748B") for group in groups]

    fig = go.Figure(
        data=[
            go.Bar(
                x=groups,
                y=calories,
                width=0.42,
                marker=dict(color=colors, line=dict(color="#0F172A", width=0.4)),
                hovertemplate="%{x}<br>%{y:.1f} kcal<extra></extra>",
                text=[f"{value:.1f}" for value in calories],
                textposition="outside",
            )
        ]
    )
    fig.update_layout(
        title="Calorias por grupo muscular",
        xaxis_title="Grupo muscular",
        yaxis_title="kcal",
        template="plotly_dark",
        plot_bgcolor="#111827",
        paper_bgcolor="#0b1020",
        font=dict(color="#E5E7EB"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_calories_history_chart(history: list[WorkoutSummary]) -> None:
    """Render bar chart with calories per workout."""
    labels = [f"Treino {index + 1}" for index, _ in enumerate(history)]
    calories = [item.total_calories for item in history]

    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=calories,
                width=0.45,
                marker=dict(
                    color=calories,
                    colorscale=[[0.0, "#1FAE78"], [1.0, "#FF8A00"]],
                    line=dict(color="#0F172A", width=0.5),
                ),
                text=[f"{value:.1f}" for value in calories],
                textposition="outside",
            )
        ]
    )
    fig.update_layout(
        title="Calorias por treino",
        xaxis_title="Treino",
        yaxis_title="kcal",
        template="plotly_dark",
        plot_bgcolor="#111827",
        paper_bgcolor="#0b1020",
        font=dict(color="#E5E7EB"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_fat_loss_history_chart(history: list[WorkoutSummary]) -> None:
    """Render cumulative fat estimate line chart."""
    labels = [f"Treino {index + 1}" for index, _ in enumerate(history)]

    cumulative_values: list[float] = []
    running = 0.0
    for entry in history:
        running += entry.total_fat_loss_kg
        cumulative_values.append(running)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=labels,
                y=cumulative_values,
                mode="lines+markers",
                line=dict(color="#16A34A", width=3),
                marker=dict(size=8, color="#FF8A00", line=dict(color="#14532D", width=1)),
                fill="tozeroy",
                fillcolor="rgba(34, 197, 94, 0.15)",
            )
        ]
    )
    fig.update_layout(
        title="Gordura estimada acumulada",
        xaxis_title="Treino",
        yaxis_title="kg",
        template="plotly_dark",
        plot_bgcolor="#111827",
        paper_bgcolor="#0b1020",
        font=dict(color="#E5E7EB"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
