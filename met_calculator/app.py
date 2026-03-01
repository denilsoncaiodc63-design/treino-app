import re
import unicodedata
from dataclasses import dataclass

import plotly.graph_objects as go
import streamlit as st

from met_calculator.data.exercises import EXERCISES as INTERNAL_EXERCISES

st.set_page_config(page_title="Calculadora de Gasto Calorico", layout="centered")


@dataclass(frozen=True)
class ExerciseDef:
    name: str
    aliases: tuple[str, ...]
    primary_group: str
    secondary_group: str | None
    met_min: float
    met_max: float
    sec_per_rep: float
    ex_type: str


def normalize(text: str) -> str:
    text = (
        text.replace("\u00e2\u20ac\u201c", "-")
        .replace("\u00e2\u20ac\u201d", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
        .replace("\u00d7", "x")
    )
    ascii_text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return " ".join(ascii_text.lower().split())


EXERCISES_DATA = [
    {"name": "Remada curvada com barra", "aliases": ["remada barra", "barbell row", "bent over row"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 5.5, "met_max": 7.5, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Remada cavalinho", "aliases": ["t-bar row", "remada tbar"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 5.5, "met_max": 7.5, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Barra fixa", "aliases": ["pull up", "chin up", "barra"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 6.0, "met_max": 8.5, "seg_por_rep": 4, "tipo": "composto"},
    {"name": "Pullover com halter", "aliases": ["pullover halter"], "grupo_primario": "Costas", "grupo_secundario": "Peito", "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 3, "tipo": "isolado"},
    {"name": "Remada na maquina", "aliases": ["remada articulada"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 5.0, "met_max": 7.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Puxada neutra", "aliases": ["puxada pegada neutra"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Remada baixa", "aliases": ["low row"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 5.0, "met_max": 7.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Face pull", "aliases": ["facepull"], "grupo_primario": "Ombros", "grupo_secundario": "Costas", "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 3, "tipo": "isolado"},
    {"name": "Supino reto com barra", "aliases": ["supino barra", "bench press"], "grupo_primario": "Peito", "grupo_secundario": "Triceps", "met_min": 5.5, "met_max": 7.5, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Supino inclinado com halteres", "aliases": ["incline dumbbell press"], "grupo_primario": "Peito", "grupo_secundario": "Ombros", "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Supino declinado", "aliases": ["decline bench"], "grupo_primario": "Peito", "grupo_secundario": "Triceps", "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Crossover na polia", "aliases": ["cross over", "crossover"], "grupo_primario": "Peito", "grupo_secundario": "Ombros", "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 3, "tipo": "isolado"},
    {"name": "Crucifixo reto com halteres", "aliases": ["dumbbell fly"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 3, "tipo": "isolado"},
    {"name": "Peck deck", "aliases": ["voador maquina"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 3, "tipo": "isolado"},
    {"name": "Desenvolvimento com barra", "aliases": ["military press", "shoulder press"], "grupo_primario": "Ombros", "grupo_secundario": "Triceps", "met_min": 5.5, "met_max": 7.5, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Desenvolvimento com halteres", "aliases": ["dumbbell shoulder press"], "grupo_primario": "Ombros", "grupo_secundario": "Triceps", "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Elevacao lateral", "aliases": ["lateral raise"], "grupo_primario": "Ombros", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Elevacao frontal", "aliases": ["front raise"], "grupo_primario": "Ombros", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Arnold press", "aliases": ["arnold"], "grupo_primario": "Ombros", "grupo_secundario": "Triceps", "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Encolhimento com barra", "aliases": ["shrug"], "grupo_primario": "Ombros", "grupo_secundario": "Costas", "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Agachamento livre", "aliases": ["squat", "agachamento barra"], "grupo_primario": "Pernas", "grupo_secundario": "Pernas", "met_min": 6.0, "met_max": 8.5, "seg_por_rep": 4, "tipo": "composto"},
    {"name": "Agachamento frontal", "aliases": ["front squat"], "grupo_primario": "Pernas", "grupo_secundario": "Pernas", "met_min": 6.0, "met_max": 8.5, "seg_por_rep": 4, "tipo": "composto"},
    {"name": "Leg press 45", "aliases": ["legpress"], "grupo_primario": "Pernas", "grupo_secundario": "Pernas", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Avanco", "aliases": ["lunge"], "grupo_primario": "Pernas", "grupo_secundario": "Pernas", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Afundo bulgaro", "aliases": ["bulgarian split squat"], "grupo_primario": "Pernas", "grupo_secundario": "Pernas", "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 4, "tipo": "composto"},
    {"name": "Stiff com barra", "aliases": ["romanian deadlift", "rdl"], "grupo_primario": "Pernas", "grupo_secundario": "Pernas", "met_min": 6.0, "met_max": 8.5, "seg_por_rep": 4, "tipo": "composto"},
    {"name": "Levantamento terra", "aliases": ["deadlift"], "grupo_primario": "Pernas", "grupo_secundario": "Costas", "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 4, "tipo": "composto"},
    {"name": "Mesa flexora", "aliases": ["leg curl"], "grupo_primario": "Pernas", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 3, "tipo": "isolado"},
    {"name": "Hip thrust", "aliases": ["elevacao pelvica"], "grupo_primario": "Pernas", "grupo_secundario": "Pernas", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Panturrilha em pe", "aliases": ["calf raise em pe"], "grupo_primario": "Pernas", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Panturrilha sentado", "aliases": ["calf seated"], "grupo_primario": "Pernas", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Rosca direta com barra", "aliases": ["biceps curl barra"], "grupo_primario": "Biceps", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Rosca alternada", "aliases": ["alternating curl"], "grupo_primario": "Biceps", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Rosca martelo", "aliases": ["hammer curl"], "grupo_primario": "Biceps", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Rosca concentrada", "aliases": ["concentration curl"], "grupo_primario": "Biceps", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.0, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Triceps na polia", "aliases": ["triceps pushdown"], "grupo_primario": "Triceps", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Mergulho em banco", "aliases": ["bench dip"], "grupo_primario": "Triceps", "grupo_secundario": "Peito", "met_min": 5.0, "met_max": 6.5, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Supino fechado", "aliases": ["close grip bench"], "grupo_primario": "Triceps", "grupo_secundario": "Peito", "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 3, "tipo": "composto"},
    {"name": "Prancha", "aliases": ["plank"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 3.5, "met_max": 5.0, "seg_por_rep": 1, "tipo": "isometrico"},
    {"name": "Abdominal supra", "aliases": ["crunch"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Abdominal infra", "aliases": ["leg raise"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Abdominal obliquo", "aliases": ["russian twist"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2, "tipo": "isolado"},
    {"name": "Prancha lateral", "aliases": ["prancha obliqua"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 3.8, "met_max": 5.0, "seg_por_rep": 1.0, "tipo": "isometrico"},
    {"name": "Prancha lateral com elevacao de perna", "aliases": ["prancha lateral avancada"], "grupo_primario": "Core", "grupo_secundario": "Gluteo", "met_min": 4.2, "met_max": 5.5, "seg_por_rep": 1.2, "tipo": "isometrico"},
    {"name": "Prancha com toque no ombro", "aliases": ["prancha alternando bracos"], "grupo_primario": "Core", "grupo_secundario": "Ombros", "met_min": 5.0, "met_max": 6.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Prancha dinamica", "aliases": ["prancha movimento"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 5.0, "met_max": 6.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Abdominal bicicleta", "aliases": ["abdominal alternado"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 5.0, "met_max": 6.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Abdominal canivete", "aliases": ["abdominal em v"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Abdominal declinado", "aliases": ["abdominal banco declinado"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Abdominal na polia", "aliases": ["abdominal no cabo"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 5.0, "met_max": 6.5, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Elevacao de pernas na barra", "aliases": ["abdominal suspenso"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Elevacao de joelhos na barra", "aliases": ["joelho na barra"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 5.5, "met_max": 7.5, "seg_por_rep": 2.8, "tipo": "composto"},
    {"name": "Abdominal infra no banco", "aliases": ["infra banco"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 5.0, "met_max": 6.5, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Abdominal supra no solo", "aliases": ["abdominal tradicional"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Rotacao de tronco na polia", "aliases": ["rotacao no cabo"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Prancha com elevacao alternada de braco e perna", "aliases": ["prancha cruzada"], "grupo_primario": "Core", "grupo_secundario": "Gluteo", "met_min": 5.0, "met_max": 6.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Supino na maquina", "aliases": ["press peitoral maquina"], "grupo_primario": "Peito", "grupo_secundario": "Triceps", "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Supino com halteres alternado", "aliases": ["supino alternado"], "grupo_primario": "Peito", "grupo_secundario": "Core", "met_min": 5.8, "met_max": 7.2, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Crucifixo inclinado com halteres", "aliases": ["crucifixo inclinado"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 3.0, "tipo": "isolado"},
    {"name": "Flexao arqueiro", "aliases": ["flexao unilateral"], "grupo_primario": "Peito", "grupo_secundario": "Triceps", "met_min": 7.5, "met_max": 9.5, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Flexao explosiva", "aliases": ["flexao com salto"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 8.5, "met_max": 10.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Flexao com palmas", "aliases": ["flexao pliometrica"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 9.0, "met_max": 11.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Supino com pausa", "aliases": ["supino pausado"], "grupo_primario": "Peito", "grupo_secundario": "Triceps", "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 4.0, "tipo": "composto"},
    {"name": "Supino pegada aberta", "aliases": ["supino aberto"], "grupo_primario": "Peito", "grupo_secundario": "Ombros", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Remada unilateral na polia", "aliases": ["remada um braco"], "grupo_primario": "Costas", "grupo_secundario": "Core", "met_min": 5.8, "met_max": 7.2, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Puxada unilateral na polia", "aliases": ["puxada um braco"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 5.8, "met_max": 7.2, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Barra fixa pegada aberta", "aliases": ["barra aberta"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 3.5, "tipo": "composto"},
    {"name": "Barra fixa pegada neutra", "aliases": ["barra neutra"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 6.8, "met_max": 8.8, "seg_por_rep": 3.5, "tipo": "composto"},
    {"name": "Barra fixa com peso", "aliases": ["barra com carga"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 8.0, "met_max": 10.0, "seg_por_rep": 3.5, "tipo": "composto"},
    {"name": "Levantamento terra deficit", "aliases": ["terra elevado"], "grupo_primario": "Posterior", "grupo_secundario": "Costas", "met_min": 7.5, "met_max": 9.5, "seg_por_rep": 4.0, "tipo": "composto"},
    {"name": "Levantamento terra no rack", "aliases": ["terra parcial"], "grupo_primario": "Posterior", "grupo_secundario": "Costas", "met_min": 7.5, "met_max": 9.5, "seg_por_rep": 4.0, "tipo": "composto"},
    {"name": "Desenvolvimento no smith", "aliases": ["ombro no smith"], "grupo_primario": "Ombros", "grupo_secundario": "Triceps", "met_min": 5.8, "met_max": 7.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Desenvolvimento unilateral com halter", "aliases": ["ombro um braco"], "grupo_primario": "Ombros", "grupo_secundario": "Core", "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Elevacao lateral na polia", "aliases": ["lateral no cabo"], "grupo_primario": "Ombros", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.5, "tipo": "isolado"},
    {"name": "Crucifixo invertido na maquina", "aliases": ["posterior maquina"], "grupo_primario": "Ombros", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.8, "tipo": "isolado"},
    {"name": "Parada de maos na parede", "aliases": ["equilibrio invertido"], "grupo_primario": "Ombros", "grupo_secundario": "Core", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 4.0, "tipo": "isometrico"},
    {"name": "Flexao em parada de maos", "aliases": ["flexao invertida"], "grupo_primario": "Ombros", "grupo_secundario": "Triceps", "met_min": 8.5, "met_max": 10.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Agachamento no smith", "aliases": ["agachamento guiado"], "grupo_primario": "Pernas", "grupo_secundario": "Gluteo", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.5, "tipo": "composto"},
    {"name": "Agachamento com pausa", "aliases": ["agachamento pausado"], "grupo_primario": "Pernas", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 4.0, "tipo": "composto"},
    {"name": "Agachamento na caixa", "aliases": ["agachamento box"], "grupo_primario": "Pernas", "grupo_secundario": "Gluteo", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.5, "tipo": "composto"},
    {"name": "Leg press unilateral", "aliases": ["leg um lado"], "grupo_primario": "Quadriceps", "grupo_secundario": "Gluteo", "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Passada andando", "aliases": ["afundo andando"], "grupo_primario": "Pernas", "grupo_secundario": "Gluteo", "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Afundo com pe elevado", "aliases": ["afundo bulgaro"], "grupo_primario": "Quadriceps", "grupo_secundario": "Gluteo", "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Elevacao de quadril unilateral", "aliases": ["ponte unilateral"], "grupo_primario": "Gluteo", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Flexora nordica", "aliases": ["nordico"], "grupo_primario": "Posterior", "grupo_secundario": None, "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Panturrilha no hack", "aliases": ["panturrilha guiada"], "grupo_primario": "Panturrilha", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2.0, "tipo": "isolado"},
    {"name": "Rosca scott com barra", "aliases": ["rosca banco scott"], "grupo_primario": "Biceps", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.8, "tipo": "isolado"},
    {"name": "Rosca concentrada", "aliases": ["rosca unilateral sentado"], "grupo_primario": "Biceps", "grupo_secundario": None, "met_min": 4.2, "met_max": 5.8, "seg_por_rep": 2.8, "tipo": "isolado"},
    {"name": "Rosca alternada com giro", "aliases": ["rosca com supinacao"], "grupo_primario": "Biceps", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.8, "tipo": "isolado"},
    {"name": "Triceps testa com halter", "aliases": ["extensao de cotovelo deitado"], "grupo_primario": "Triceps", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.8, "tipo": "isolado"},
    {"name": "Triceps no banco", "aliases": ["mergulho no banco"], "grupo_primario": "Triceps", "grupo_secundario": None, "met_min": 5.0, "met_max": 6.5, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Triceps unilateral na polia", "aliases": ["triceps um braco"], "grupo_primario": "Triceps", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.8, "tipo": "isolado"},
    {"name": "Agachamento overhead", "aliases": ["agachamento acima da cabeca"], "grupo_primario": "Pernas", "grupo_secundario": "Ombros", "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 3.5, "tipo": "composto"},
    {"name": "Agachamento pistol", "aliases": ["agachamento unilateral completo"], "grupo_primario": "Quadriceps", "grupo_secundario": "Gluteo", "met_min": 8.5, "met_max": 10.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Salto no caixote", "aliases": ["salto na caixa"], "grupo_primario": "Pernas", "grupo_secundario": "Cardio", "met_min": 8.5, "met_max": 10.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Salto horizontal", "aliases": ["salto a frente"], "grupo_primario": "Pernas", "grupo_secundario": None, "met_min": 8.0, "met_max": 10.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Avanco com salto", "aliases": ["afundo com salto"], "grupo_primario": "Pernas", "grupo_secundario": "Cardio", "met_min": 9.0, "met_max": 11.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Levantamento olimpico puxada alta", "aliases": ["puxada alta olimpica"], "grupo_primario": "Posterior", "grupo_secundario": "Ombros", "met_min": 8.5, "met_max": 10.5, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Arremesso de bola medicinal no solo", "aliases": ["bola medicinal no chao"], "grupo_primario": "Core", "grupo_secundario": "Ombros", "met_min": 9.0, "met_max": 11.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Arremesso de bola medicinal frontal", "aliases": ["arremesso frontal"], "grupo_primario": "Core", "grupo_secundario": "Peito", "met_min": 8.5, "met_max": 10.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Balanco com kettlebell", "aliases": ["balanco russo"], "grupo_primario": "Posterior", "grupo_secundario": "Gluteo", "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Agachamento goblet", "aliases": ["agachamento com kettlebell"], "grupo_primario": "Pernas", "grupo_secundario": "Gluteo", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Levantamento terra com kettlebell", "aliases": ["terra kettlebell"], "grupo_primario": "Posterior", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Avanco com kettlebell", "aliases": ["passada kettlebell"], "grupo_primario": "Pernas", "grupo_secundario": "Gluteo", "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Desenvolvimento com kettlebell", "aliases": ["ombro kettlebell"], "grupo_primario": "Ombros", "grupo_secundario": "Triceps", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Remada com kettlebell", "aliases": ["remada kettlebell"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Empurrar treno", "aliases": ["treno pesado"], "grupo_primario": "Pernas", "grupo_secundario": "Cardio", "met_min": 9.0, "met_max": 11.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Puxar treno", "aliases": ["treno puxando"], "grupo_primario": "Pernas", "grupo_secundario": "Cardio", "met_min": 9.0, "met_max": 11.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Corda naval alternada", "aliases": ["corda naval"], "grupo_primario": "Cardio", "grupo_secundario": "Ombros", "met_min": 9.0, "met_max": 11.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Bicicleta ergometrica intensa", "aliases": ["bicicleta forte"], "grupo_primario": "Cardio", "grupo_secundario": None, "met_min": 8.5, "met_max": 10.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Corrida com tiro curto", "aliases": ["sprint curto"], "grupo_primario": "Cardio", "grupo_secundario": None, "met_min": 9.5, "met_max": 11.5, "seg_por_rep": 1.5, "tipo": "composto"},
    {"name": "Corrida em escada", "aliases": ["subida escada"], "grupo_primario": "Cardio", "grupo_secundario": None, "met_min": 9.0, "met_max": 11.0, "seg_por_rep": 1.5, "tipo": "composto"},
    {"name": "Caminhada com carga", "aliases": ["caminhada carregando peso"], "grupo_primario": "Core", "grupo_secundario": "Cardio", "met_min": 7.5, "met_max": 9.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Carregada de fazendeiro", "aliases": ["farmer walk"], "grupo_primario": "Core", "grupo_secundario": "Antebraco", "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Mobilidade toracica no solo", "aliases": ["rotacao toracica"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.5, "met_max": 3.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Mobilidade de quadril em quatro apoios", "aliases": ["quadril quatro apoios"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.5, "met_max": 3.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Alongamento posterior de coxa em pe", "aliases": ["alongamento isquiotibial"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.0, "met_max": 3.0, "seg_por_rep": 1.0, "tipo": "isometrico"},
    {"name": "Alongamento de peitoral na parede", "aliases": ["peitoral parede"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.0, "met_max": 3.0, "seg_por_rep": 1.0, "tipo": "isometrico"},
    {"name": "Alongamento flexor de quadril ajoelhado", "aliases": ["flexor quadril"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.0, "met_max": 3.0, "seg_por_rep": 1.0, "tipo": "isometrico"},
    {"name": "Rotacao externa de ombro com elastico", "aliases": ["ombro elastico"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.5, "met_max": 3.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Gato e camelo", "aliases": ["coluna mobilidade"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.5, "met_max": 3.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Alongamento global dinamico", "aliases": ["alongamento completo"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 3.0, "met_max": 4.0, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Barra australiana", "aliases": ["remada invertida"], "grupo_primario": "Costas", "grupo_secundario": "Biceps", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Musculo na barra", "aliases": ["subida completa na barra"], "grupo_primario": "Costas", "grupo_secundario": "Peito", "met_min": 9.5, "met_max": 11.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Parada de maos livre", "aliases": ["equilibrio invertido livre"], "grupo_primario": "Ombros", "grupo_secundario": "Core", "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 4.0, "tipo": "isometrico"},
    {"name": "Elevacao de pernas em paralelas", "aliases": ["abdominal paralelas"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Agachamento sumo com halter", "aliases": ["agachamento sumo"], "grupo_primario": "Pernas", "grupo_secundario": "Gluteo", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Levantamento terra sumo", "aliases": ["terra sumo"], "grupo_primario": "Posterior", "grupo_secundario": "Gluteo", "met_min": 7.5, "met_max": 9.5, "seg_por_rep": 4.0, "tipo": "composto"},
    {"name": "Extensora unilateral", "aliases": ["extensora um lado"], "grupo_primario": "Quadriceps", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.8, "tipo": "isolado"},
    {"name": "Flexora unilateral", "aliases": ["flexora um lado"], "grupo_primario": "Posterior", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.8, "tipo": "isolado"},
    {"name": "Panturrilha unilateral em pe", "aliases": ["panturrilha um pe"], "grupo_primario": "Panturrilha", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2.0, "tipo": "isolado"},
    {"name": "Remada curvada pegada aberta", "aliases": ["remada aberta"], "grupo_primario": "Costas", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.5, "tipo": "composto"},
    {"name": "Remada curvada pegada fechada", "aliases": ["remada fechada"], "grupo_primario": "Costas", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.5, "tipo": "composto"},
    {"name": "Puxada frente pegada aberta", "aliases": ["puxada aberta"], "grupo_primario": "Costas", "grupo_secundario": None, "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Puxada frente pegada fechada", "aliases": ["puxada fechada"], "grupo_primario": "Costas", "grupo_secundario": None, "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Puxada frente pegada neutra", "aliases": ["puxada neutra"], "grupo_primario": "Costas", "grupo_secundario": None, "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Supino inclinado na maquina", "aliases": ["press inclinado maquina"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Supino declinado com halteres", "aliases": ["supino declinado"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Crucifixo na maquina", "aliases": ["voador maquina"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.8, "tipo": "isolado"},
    {"name": "Elevacao lateral unilateral", "aliases": ["lateral um lado"], "grupo_primario": "Ombros", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2.5, "tipo": "isolado"},
    {"name": "Elevacao frontal com halter", "aliases": ["frontal halter"], "grupo_primario": "Ombros", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2.5, "tipo": "isolado"},
    {"name": "Encolhimento com barra", "aliases": ["encolhimento trapezio"], "grupo_primario": "Ombros", "grupo_secundario": None, "met_min": 5.0, "met_max": 6.5, "seg_por_rep": 2.5, "tipo": "isolado"},
    {"name": "Prancha com deslocamento lateral", "aliases": ["prancha andando"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Prancha alta com rotacao", "aliases": ["prancha com giro"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 5.5, "met_max": 7.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Abdominal obliquo no solo", "aliases": ["abdominal lateral"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Abdominal infra suspenso", "aliases": ["infra na barra"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Burpee completo", "aliases": ["burpee tradicional"], "grupo_primario": "Cardio", "grupo_secundario": None, "met_min": 10.0, "met_max": 12.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Burpee com salto alto", "aliases": ["burpee explosivo"], "grupo_primario": "Cardio", "grupo_secundario": None, "met_min": 10.5, "met_max": 12.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Polichinelo", "aliases": ["salto abrindo pernas"], "grupo_primario": "Cardio", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 1.5, "tipo": "composto"},
    {"name": "Corrida estacionaria", "aliases": ["simulacao de corrida"], "grupo_primario": "Cardio", "grupo_secundario": None, "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 1.5, "tipo": "composto"},
    {"name": "Subida no banco alternada", "aliases": ["step alternado"], "grupo_primario": "Pernas", "grupo_secundario": "Cardio", "met_min": 7.0, "met_max": 9.0, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Alongamento de gluteo sentado", "aliases": ["gluteo sentado"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.0, "met_max": 3.0, "seg_por_rep": 1.0, "tipo": "isometrico"},
    {"name": "Alongamento de adutor", "aliases": ["borboleta"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.0, "met_max": 3.0, "seg_por_rep": 1.0, "tipo": "isometrico"},
    {"name": "Alongamento de panturrilha na parede", "aliases": ["panturrilha parede"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.0, "met_max": 3.0, "seg_por_rep": 1.0, "tipo": "isometrico"},
    {"name": "Mobilidade de tornozelo", "aliases": ["tornozelo mobilidade"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.5, "met_max": 3.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Rotacao de tronco em pe", "aliases": ["tronco dinamico"], "grupo_primario": "Mobilidade", "grupo_secundario": None, "met_min": 2.5, "met_max": 3.5, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Remada alta com barra", "aliases": ["remada alta"], "grupo_primario": "Ombros", "grupo_secundario": None, "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Levantamento terra romeno unilateral", "aliases": ["terra romeno um lado"], "grupo_primario": "Posterior", "grupo_secundario": "Gluteo", "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Agachamento com salto", "aliases": ["agachamento pliometrico"], "grupo_primario": "Pernas", "grupo_secundario": "Cardio", "met_min": 9.0, "met_max": 11.0, "seg_por_rep": 2.0, "tipo": "composto"},
    {"name": "Afundo lateral", "aliases": ["passada lateral"], "grupo_primario": "Quadriceps", "grupo_secundario": "Gluteo", "met_min": 6.0, "met_max": 8.0, "seg_por_rep": 3.0, "tipo": "composto"},
    {"name": "Cadeira abdutora", "aliases": ["abdutora"], "grupo_primario": "Gluteo", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2.5, "tipo": "isolado"},
    {"name": "Cadeira adutora", "aliases": ["adutora"], "grupo_primario": "Adutor", "grupo_secundario": None, "met_min": 4.0, "met_max": 5.5, "seg_por_rep": 2.5, "tipo": "isolado"},
    {"name": "Flexao diamante", "aliases": ["flexao pegada fechada"], "grupo_primario": "Peito", "grupo_secundario": "Triceps", "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Flexao inclinada", "aliases": ["flexao apoio alto"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 4.5, "met_max": 6.0, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Flexao declinada", "aliases": ["flexao pes elevados"], "grupo_primario": "Peito", "grupo_secundario": None, "met_min": 6.5, "met_max": 8.5, "seg_por_rep": 2.5, "tipo": "composto"},
    {"name": "Prancha isometrica tradicional", "aliases": ["prancha frontal"], "grupo_primario": "Core", "grupo_secundario": None, "met_min": 3.5, "met_max": 5.0, "seg_por_rep": 1.0, "tipo": "isometrico"},
]


def build_exercise_bank() -> tuple[ExerciseDef, ...]:
    bank: list[ExerciseDef] = []
    seen: set[str] = set()
    latest_items: dict[str, dict] = {}

    for item in EXERCISES_DATA:
        key = normalize(item["name"])
        latest_items[key] = item

    for key, item in latest_items.items():
        seen.add(key)
        bank.append(
            ExerciseDef(
                name=item["name"],
                aliases=tuple(normalize(alias) for alias in item["aliases"]),
                primary_group=item["grupo_primario"],
                secondary_group=item["grupo_secundario"],
                met_min=float(item["met_min"]),
                met_max=float(item["met_max"]),
                sec_per_rep=float(item["seg_por_rep"]),
                ex_type=item["tipo"],
            )
        )

    for ex in INTERNAL_EXERCISES:
        key = normalize(ex.name)
        if key in seen:
            continue
        bank.append(
            ExerciseDef(
                name=ex.name,
                aliases=tuple(ex.keywords),
                primary_group=ex.muscle_group,
                secondary_group=None,
                met_min=max(3.0, float(ex.met) * 0.9),
                met_max=min(12.0, float(ex.met) * 1.15),
                sec_per_rep=float(ex.seconds_per_rep),
                ex_type="composto" if ex.met >= 5.5 else "isolado",
            )
        )
        seen.add(key)

    return tuple(bank)


EXERCISES: tuple[ExerciseDef, ...] = build_exercise_bank()

CARDIO_HINTS = ("bike", "bicicleta", "corrida", "esteira", "eliptico", "remo", "caminhada")
HIIT_HINTS = ("hiit", "sprint", "intervalado")

# Calibracao para manter estimativas realistas em treinos de musculacao.
SET_SECONDS_COMPOUND = 60.0
SET_SECONDS_ISOLATION = 48.0
SET_SECONDS_ISOMETRIC = 40.0
REST_SECONDS_SINGLE = 90.0
REST_SECONDS_CONJUGATE = 75.0
TRANSITION_SECONDS = 45.0

SERIES_RANGE_RE = re.compile(r"(\d+)\s*[-]\s*(\d+)\s*(?:serie|series)\b")
SERIES_SINGLE_RE = re.compile(r"(\d+)\s*(?:serie|series)\b")
X_FORMAT_RE = re.compile(r"(\d+)\s*[-]?\s*(\d+)?\s*x\s*(\d+)\s*[-]?\s*(\d+)?")
REPS_RANGE_RE = re.compile(r"(\d+)\s*[-]\s*(\d+)\s*(?:rep|reps|repeticao|repeticoes)\b")
REPS_SINGLE_RE = re.compile(r"(\d+)\s*(?:rep|reps|repeticao|repeticoes)\b")
DURATION_MIN_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:min|minuto|minutos)\b")
DURATION_CLOCK_RE = re.compile(r"(\d+)'\s*(\d{1,2})?\"?")
ISOMETRY_RE = re.compile(r"(\d+)\s*[-]?\s*(\d+)?\s*s(?:eg)?\s*isometria")


def clean_text_for_match(text: str) -> str:
    cleaned = normalize(text)
    cleaned = cleaned.replace("-", " ")
    cleaned = re.sub(r"\([^)]*\)", " ", cleaned)
    for noise in ("com halteres", "com barra", "por lado"):
        cleaned = cleaned.replace(noise, "")
    cleaned = " ".join(cleaned.split())
    alias_map = {
        "step up baixo": "step up",
        "stepup baixo": "step up",
        "aducao com bola isometrica": "adutora maquina",
        "aducao com bola": "adutora maquina",
        "abducao": "abducao maquina",
        "aducao": "adutora maquina",
        "panturrilha": "panturrilha em pe",
        "crucifixo inverso": "crucifixo invertido",
        "rosca scott": "rosca scott com barra",
        "coice na polia para triceps": "triceps coice",
        "coice na polia triceps": "triceps coice",
        "coice polia triceps": "triceps coice",
        "coice para triceps": "triceps coice",
        "coice triceps": "triceps coice",
        "triceps coice na polia": "triceps coice",
        "kickback na polia": "triceps coice",
    }
    if cleaned in alias_map:
        cleaned = alias_map[cleaned]
    for old, new in alias_map.items():
        cleaned = cleaned.replace(old, new)
    if "remada unilateral" in cleaned and "polia" not in cleaned:
        cleaned = cleaned.replace("remada unilateral", "remada unilateral halter")
    if "coice" in cleaned and "triceps" in cleaned:
        cleaned = cleaned.replace("coice", "triceps coice")
    return " ".join(cleaned.split())


def identify_exercise(text: str) -> ExerciseDef | None:
    normalized = clean_text_for_match(text)
    best: tuple[int, ExerciseDef] | None = None
    for ex in EXERCISES:
        keys = (normalize(ex.name), *ex.aliases)
        for kw in keys:
            if kw and kw in normalized:
                size = len(kw)
                if best is None or size > best[0]:
                    best = (size, ex)
    return best[1] if best else None


def is_header_or_comment(line: str) -> bool:
    lowered = normalize(line)
    if not lowered:
        return True
    if lowered.startswith(("obs", "comentario", "#", "ou ")):
        return True
    if "treino" in lowered and not any(ch.isdigit() for ch in lowered):
        return True
    return False


def extract_series(line: str, default: int = 3) -> int:
    lowered = normalize(line)
    x_match = X_FORMAT_RE.search(lowered)
    if x_match:
        first = int(x_match.group(1))
        second = int(x_match.group(2)) if x_match.group(2) else first
        return max(first, second)
    range_match = SERIES_RANGE_RE.search(lowered)
    if range_match:
        return max(int(range_match.group(1)), int(range_match.group(2)))
    single_match = SERIES_SINGLE_RE.search(lowered)
    if single_match:
        return int(single_match.group(1))
    return default


def extract_reps(line: str, default: int = 10) -> int:
    lowered = normalize(line)
    x_match = X_FORMAT_RE.search(lowered)
    if x_match:
        first = int(x_match.group(3))
        second = int(x_match.group(4)) if x_match.group(4) else first
        return int(round((first + second) / 2.0))
    range_match = REPS_RANGE_RE.search(lowered)
    if range_match:
        first = int(range_match.group(1))
        second = int(range_match.group(2))
        return int(round((first + second) / 2.0))
    single_match = REPS_SINGLE_RE.search(lowered)
    if single_match:
        return int(single_match.group(1))
    return default


def extract_duration_min(line: str) -> float | None:
    lowered = normalize(line)
    min_match = DURATION_MIN_RE.search(lowered)
    if min_match:
        return float(min_match.group(1).replace(",", "."))
    clock_match = DURATION_CLOCK_RE.search(lowered)
    if clock_match:
        minute = float(clock_match.group(1))
        second = float(clock_match.group(2) or 0.0)
        return minute + (second / 60.0)
    return None


def extract_isometry_seconds(line: str) -> float:
    lowered = normalize(line)
    match = ISOMETRY_RE.search(lowered)
    if not match:
        return 0.0
    low = float(match.group(1))
    high = float(match.group(2) or low)
    if high < low:
        low, high = high, low
    base = (low + high) / 2.0
    if "inicio" in lowered and "final" in lowered:
        return base * 2.0
    return base


def detect_type(line: str) -> str:
    lowered = normalize(line)
    if any(word in lowered for word in HIIT_HINTS):
        return "hiit"
    if any(word in lowered for word in CARDIO_HINTS):
        return "cardio"
    return "musculacao"


def is_detail_line(line: str) -> bool:
    lowered = normalize(line)
    if detect_type(line) in {"cardio", "hiit"}:
        return False
    if "serie" in lowered or "rep" in lowered or "isometria" in lowered:
        return True
    if extract_duration_min(line) is not None and identify_exercise(line) is None:
        return True
    return False


def parse_treino(texto: str):
    blocks: list[dict] = []
    ignored: list[str] = []
    warnings: list[str] = []
    last_block_index: int | None = None

    for raw_line in texto.splitlines():
        line = raw_line.strip()
        if is_header_or_comment(line):
            continue

        if is_detail_line(line):
            if last_block_index is None:
                continue
            block = blocks[last_block_index]
            nline = normalize(line)
            has_series = bool(SERIES_RANGE_RE.search(nline) or SERIES_SINGLE_RE.search(nline) or X_FORMAT_RE.search(nline))
            has_reps = bool(REPS_RANGE_RE.search(nline) or REPS_SINGLE_RE.search(nline) or X_FORMAT_RE.search(nline))
            if has_series:
                block["series"] = extract_series(line, block["series"])
            if has_reps:
                block["reps"] = extract_reps(line, block["reps"])
            duration = extract_duration_min(line)
            if duration is not None:
                block["duration_min"] = duration
            iso = extract_isometry_seconds(line)
            if iso > 0:
                block["isometry_seconds"] = iso
            continue

        parts = [part.strip() for part in raw_line.split("+") if part.strip()]
        if not parts:
            ignored.append(raw_line)
            last_block_index = None
            continue

        recognized: list[ExerciseDef] = []
        block_type = detect_type(raw_line)
        for part in parts:
            ex = identify_exercise(part)
            if ex:
                recognized.append(ex)

        if not recognized:
            if block_type in {"cardio", "hiit"}:
                pseudo = ExerciseDef(
                    name=raw_line.strip(),
                    aliases=(normalize(raw_line),),
                    primary_group="Cardio",
                    secondary_group=None,
                    met_min=7.0 if block_type == "cardio" else 9.0,
                    met_max=8.0 if block_type == "cardio" else 10.0,
                    sec_per_rep=2.0,
                    ex_type="cardio",
                )
                recognized.append(pseudo)
            else:
                ignored.append(raw_line)
                last_block_index = None
                continue

        block = {
            "raw_line": raw_line.strip(),
            "type": block_type,
            "exercises": recognized,
            "series": extract_series(raw_line),
            "reps": extract_reps(raw_line),
            "duration_min": extract_duration_min(raw_line),
            "isometry_seconds": extract_isometry_seconds(raw_line),
        }
        blocks.append(block)
        last_block_index = len(blocks) - 1

        if block_type in {"cardio", "hiit"} and block["duration_min"] is None:
            warnings.append(f"Linha sem tempo explicito: {raw_line.strip()}")

    return blocks, ignored, warnings


def estimate_block_duration_min(block: dict) -> float:
    if block["duration_min"] is not None:
        return float(block["duration_min"])

    if block["type"] in {"cardio", "hiit"}:
        return max(8.0, block["series"] * 4.0)

    cycles = block["series"]
    reps = block["reps"]
    exec_times = []
    for ex in block["exercises"]:
        if ex.ex_type == "isometrico":
            floor_seconds = SET_SECONDS_ISOMETRIC
        elif ex.ex_type == "isolado":
            floor_seconds = SET_SECONDS_ISOLATION
        else:
            floor_seconds = SET_SECONDS_COMPOUND
        exec_times.append(max(ex.sec_per_rep * reps, floor_seconds))

    cycle_exec = sum(exec_times)
    rest_per_cycle = REST_SECONDS_CONJUGATE if len(block["exercises"]) > 1 else REST_SECONDS_SINGLE
    total_rest = max(0.0, (cycles - 1) * rest_per_cycle)
    iso_total = block["isometry_seconds"] * cycles
    return ((cycle_exec * cycles) + total_rest + iso_total + TRANSITION_SECONDS) / 60.0


def estimate_block_met(block: dict) -> float:
    mets = [((ex.met_min + ex.met_max) / 2.0) for ex in block["exercises"]]
    base = sum(mets) / len(mets)

    # Calibracao por densidade da serie
    reps_factor = (block["reps"] - 10) * 0.008
    series_factor = (block["series"] - 3) * 0.03
    intensity = 1.0 + max(-0.1, min(0.15, reps_factor + series_factor))

    if len(block["exercises"]) > 1:
        base *= 1.0 + (0.08 * (len(block["exercises"]) - 1))

    if block["isometry_seconds"] > 0:
        base *= 1.03

    if block["type"] == "cardio":
        base = max(base, 7.0)
    if block["type"] == "hiit":
        base = max(base, 9.0)

    return min(base * intensity, 10.2)


def distribute_group_kcal(groups: dict[str, float], exercise: ExerciseDef, kcal: float) -> None:
    if exercise.secondary_group:
        groups[exercise.primary_group] = groups.get(exercise.primary_group, 0.0) + (kcal * 0.7)
        groups[exercise.secondary_group] = groups.get(exercise.secondary_group, 0.0) + (kcal * 0.3)
    else:
        groups[exercise.primary_group] = groups.get(exercise.primary_group, 0.0) + kcal


def calcular_calorias(blocks: list[dict], peso: float):
    total_kcal = 0.0
    total_minutes = 0.0
    group_kcal: dict[str, float] = {}
    details: list[dict] = []

    for block in blocks:
        duration_min = estimate_block_duration_min(block)
        met = estimate_block_met(block)
        kcal_min = (met * 3.5 * peso) / 200.0
        block_kcal = kcal_min * duration_min

        per_exercise_kcal = block_kcal / len(block["exercises"])
        for ex in block["exercises"]:
            distribute_group_kcal(group_kcal, ex, per_exercise_kcal)

        total_kcal += block_kcal
        total_minutes += duration_min

        details.append(
            {
                "exercicios": " + ".join(ex.name for ex in block["exercises"]),
                "tipo": block["type"],
                "series": block["series"],
                "reps": block["reps"],
                "met": met,
                "duracao_min": duration_min,
                "kcal": block_kcal,
            }
        )

    if total_minutes > 60.0:
        scale = 60.0 / total_minutes
        total_minutes = 60.0
        total_kcal *= scale
        for key in list(group_kcal.keys()):
            group_kcal[key] *= scale
        for item in details:
            item["kcal"] *= scale
            item["duracao_min"] *= scale

    if total_kcal > 600.0:
        scale = 600.0 / total_kcal
        total_kcal = 600.0
        for key in list(group_kcal.keys()):
            group_kcal[key] *= scale
        for item in details:
            item["kcal"] *= scale

    return total_kcal, group_kcal, total_minutes, details


def grafico_grupos(groups: dict[str, float]) -> None:
    labels = list(groups.keys())
    values = [groups[k] for k in labels]
    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=values,
                width=0.42,
                marker=dict(color=values, colorscale="Turbo"),
                hovertemplate="%{x}<br>%{y:.1f} kcal<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="Calorias por Grupo Muscular",
        xaxis_title="Grupo",
        yaxis_title="kcal",
        template="plotly_dark",
        plot_bgcolor="#111827",
        paper_bgcolor="#0b1020",
        font=dict(color="#E5E7EB"),
    )
    st.plotly_chart(fig, use_container_width=True)


def grafico_total(total_kcal: float) -> None:
    fig = go.Figure(
        data=[
            go.Bar(
                x=["Total do treino"],
                y=[total_kcal],
                width=0.35,
                marker=dict(color="#22C55E"),
                text=[f"{total_kcal:.0f} kcal"],
                textposition="outside",
            )
        ]
    )
    fig.update_layout(
        title="Total de Calorias do Treino",
        yaxis_title="kcal",
        template="plotly_dark",
        plot_bgcolor="#111827",
        paper_bgcolor="#0b1020",
        font=dict(color="#E5E7EB"),
    )
    st.plotly_chart(fig, use_container_width=True)


def grafico_comparativo_treinos(history: list[dict]) -> None:
    labels = [f"Treino {idx + 1}" for idx, _ in enumerate(history)]
    totals = [entry["total_kcal"] for entry in history]
    focus_values = [entry["focus_kcal"] for entry in history]
    focus_groups = [entry["focus_group"] for entry in history]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Total do treino",
            x=labels,
            y=totals,
            width=0.38,
            marker=dict(color="#FB923C"),
            text=[f"{value:.0f}" for value in totals],
            textposition="outside",
            customdata=focus_groups,
            hovertemplate="Treino: %{x}<br>Total: %{y:.1f} kcal<br>Foco: %{customdata}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Gasto no grupo foco",
            x=labels,
            y=focus_values,
            width=0.28,
            marker=dict(color="#60A5FA"),
            text=[f"{value:.0f}" for value in focus_values],
            textposition="outside",
            customdata=focus_groups,
            hovertemplate="Treino: %{x}<br>Grupo foco: %{customdata}<br>Gasto: %{y:.1f} kcal<extra></extra>",
        )
    )
    fig.update_layout(
        title="Comparacao de Gasto Entre Treinos",
        xaxis_title="Treinos",
        yaxis_title="kcal",
        barmode="group",
        template="plotly_dark",
        plot_bgcolor="#111827",
        paper_bgcolor="#0b1020",
        font=dict(color="#E5E7EB"),
    )
    st.plotly_chart(fig, use_container_width=True)


def detectar_foco(groups: dict[str, float]) -> str:
    muscle_groups = {k: v for k, v in groups.items() if normalize(k) != "cardio"}
    if muscle_groups:
        return max(muscle_groups, key=muscle_groups.get)
    return max(groups, key=groups.get)


def clear_workout_text() -> None:
    st.session_state["workout_text"] = ""


def clear_history() -> None:
    st.session_state["workout_history"] = []


st.markdown(
    """
    <style>
    .stApp { background-color: #0b1020; color: #e5e7eb; }
    .stButton button {
        background: linear-gradient(90deg, #ff7f0f, #22c55e);
        color: white;
        font-size: 16px;
        border: 0;
        border-radius: 8px;
        font-weight: 600;
    }
    .stTextArea textarea { background-color: #111827; color: #e5e7eb; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Calcule seu treino")
st.caption(f"Base ativa: {len(EXERCISES)} exercicios e variacoes")

if "workout_text" not in st.session_state:
    st.session_state.workout_text = ""
if "workout_history" not in st.session_state:
    st.session_state.workout_history = []

peso = st.number_input("Seu peso (kg):", min_value=0.0, max_value=300.0, value=0.0, step=0.1, format="%.1f")
texto = st.text_area("Digite seu treino:", height=300, key="workout_text")

col1, col2 = st.columns(2)
with col1:
    calcular = st.button("Calcular")
with col2:
    st.button("Limpar treino", on_click=clear_workout_text)

st.button("Limpar historico de comparacao", on_click=clear_history)

if calcular:
    if peso <= 0:
        st.error("Informe seu peso para calcular o treino.")
    else:
        blocks, ignored, warnings = parse_treino(texto)
        if not blocks:
            st.error("Nenhum exercicio reconhecido.")
        else:
            total_kcal, groups, total_minutes, details = calcular_calorias(blocks, peso)
            st.success(f"Gasto estimado: {total_kcal:.0f} kcal")
            st.write(f"Tempo estimado de treino: {total_minutes:.0f} minutos")

            c1, c2 = st.columns(2)
            with c1:
                grafico_grupos(groups)
            with c2:
                grafico_total(total_kcal)

            foco = detectar_foco(groups)
            foco_kcal = groups.get(foco, 0.0)
            st.session_state["workout_history"].append(
                {
                    "total_kcal": float(total_kcal),
                    "focus_group": foco,
                    "focus_kcal": float(foco_kcal),
                    "duration_min": float(total_minutes),
                }
            )
            st.info(f"Treino com foco em {foco}")

            st.subheader("Comparacao entre treinos")
            grafico_comparativo_treinos(st.session_state["workout_history"])
            if len(st.session_state["workout_history"]) >= 2:
                best_index, best_item = max(
                    enumerate(st.session_state["workout_history"], start=1),
                    key=lambda row: row[1]["total_kcal"],
                )
                st.caption(
                    f"Maior gasto ate agora: Treino {best_index} "
                    f"({best_item['focus_group']}) com {best_item['total_kcal']:.0f} kcal."
                )

            st.subheader("Detalhe do calculo")
            rows = [
                {
                    "Exercicios": item["exercicios"],
                    "Tipo": item["tipo"],
                    "Series": item["series"],
                    "Reps": item["reps"],
                    "MET": round(item["met"], 2),
                    "Duracao (min)": round(item["duracao_min"], 2),
                    "kcal": round(item["kcal"], 1),
                }
                for item in details
            ]
            st.dataframe(rows, hide_index=True, use_container_width=True)

        if warnings:
            st.warning("Avisos:")
            for line in warnings:
                st.write("-", line)

        if ignored:
            st.warning("Linhas ignoradas:")
            for line in ignored:
                st.write("-", line)
