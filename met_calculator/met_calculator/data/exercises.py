"""Internal exercise database used by parser and calculator."""

from __future__ import annotations

from met_calculator.core.models import Exercise
from met_calculator.core.text_utils import normalize_text


def _k(values: list[str]) -> list[str]:
    """Normalize keyword list once at import time."""
    return [normalize_text(value) for value in values]


EXERCISES: list[Exercise] = [
    # PEITO
    Exercise("Supino reto", _k(["supino reto", "supino"]), 6.0, 3.0, "Peito"),
    Exercise("Supino inclinado", _k(["supino inclinado"]), 6.5, 3.0, "Peito"),
    Exercise("Supino declinado", _k(["supino declinado"]), 6.3, 3.0, "Peito"),
    Exercise("Supino com halteres", _k(["supino com halteres", "supino halter"]), 6.2, 3.0, "Peito"),
    Exercise("Cross over", _k(["cross over", "crossover"]), 5.2, 3.2, "Peito"),
    Exercise("Peck deck", _k(["peck deck"]), 5.0, 3.0, "Peito"),
    Exercise("Flexao", _k(["flexao", "flexao de braco", "push up"]), 8.0, 2.2, "Peito"),
    Exercise("Flexao diamante", _k(["flexao diamante", "diamond push up"]), 8.5, 2.2, "Peito"),
    Exercise("Flexao com apoio elevado", _k(["flexao com apoio elevado", "decline push up"]), 8.3, 2.2, "Peito"),
    Exercise("Paralelas para peito", _k(["paralelas para peito"]), 8.0, 2.4, "Peito"),
    Exercise("Crucifixo", _k(["crucifixo", "fly"]), 5.5, 3.2, "Peito"),

    # COSTAS
    Exercise("Barra fixa", _k(["barra fixa"]), 8.5, 2.5, "Costas"),
    Exercise("Remada curvada", _k(["remada curvada"]), 6.5, 3.0, "Costas"),
    Exercise("Remada cavalinho", _k(["remada cavalinho", "t bar row"]), 6.8, 3.0, "Costas"),
    Exercise("Remada unilateral halter", _k(["remada unilateral halter", "serrote"]), 6.2, 3.0, "Costas"),
    Exercise("Puxada frente", _k(["puxada frente"]), 5.5, 3.0, "Costas"),
    Exercise("Puxada aberta", _k(["puxada aberta"]), 5.8, 3.0, "Costas"),
    Exercise("Puxada pegada inversa", _k(["puxada pegada inversa"]), 5.8, 3.0, "Costas"),
    Exercise("Pull down", _k(["pull down", "pulldown"]), 5.5, 3.0, "Costas"),
    Exercise("Levantamento terra", _k(["levantamento terra", "deadlift"]), 8.0, 3.5, "Costas"),
    Exercise("Pullover", _k(["pullover"]), 5.2, 3.2, "Costas"),

    # OMBRO
    Exercise("Desenvolvimento", _k(["desenvolvimento", "shoulder press"]), 5.5, 2.8, "Ombro"),
    Exercise("Arnold press", _k(["arnold press"]), 5.8, 2.8, "Ombro"),
    Exercise("Desenvolvimento halter", _k(["desenvolvimento halter"]), 5.6, 2.8, "Ombro"),
    Exercise("Elevacao lateral", _k(["elevacao lateral"]), 5.0, 2.5, "Ombro"),
    Exercise("Elevacao lateral inclinada", _k(["elevacao lateral inclinada"]), 5.0, 2.5, "Ombro"),
    Exercise("Elevacao frontal", _k(["elevacao frontal"]), 4.8, 2.5, "Ombro"),
    Exercise("Crucifixo invertido", _k(["crucifixo invertido", "reverse fly"]), 5.0, 2.8, "Ombro"),
    Exercise("Face pull", _k(["face pull"]), 4.8, 2.6, "Ombro"),
    Exercise("Remada alta", _k(["remada alta", "upright row"]), 5.6, 2.8, "Ombro"),

    # TRICEPS
    Exercise("Triceps testa", _k(["triceps testa"]), 5.2, 2.8, "Triceps"),
    Exercise("Triceps corda", _k(["triceps corda"]), 5.0, 2.5, "Triceps"),
    Exercise("Triceps frances", _k(["triceps frances"]), 5.0, 2.8, "Triceps"),
    Exercise("Triceps banco", _k(["triceps banco"]), 6.2, 2.3, "Triceps"),
    Exercise("Triceps coice", _k(["triceps coice", "kickback"]), 4.8, 2.8, "Triceps"),
    Exercise("Paralelas para triceps", _k(["paralelas para triceps"]), 8.5, 2.3, "Triceps"),
    Exercise("Triceps barra reta", _k(["triceps barra reta"]), 5.1, 2.5, "Triceps"),
    Exercise("Mergulho banco", _k(["mergulho banco", "mergulho"]), 6.5, 2.2, "Triceps"),

    # BICEPS
    Exercise("Rosca direta", _k(["rosca direta"]), 5.0, 2.6, "Biceps"),
    Exercise("Rosca alternada", _k(["rosca alternada"]), 5.1, 2.8, "Biceps"),
    Exercise("Rosca concentrada", _k(["rosca concentrada"]), 4.8, 3.0, "Biceps"),
    Exercise("Rosca martelo", _k(["rosca martelo", "martelo"]), 5.2, 2.8, "Biceps"),
    Exercise("Rosca 21", _k(["rosca 21"]), 5.6, 3.0, "Biceps"),
    Exercise("Rosca spider", _k(["rosca spider", "spider curl"]), 5.0, 2.8, "Biceps"),
    Exercise("Rosca inclinada", _k(["rosca inclinada"]), 5.1, 2.8, "Biceps"),
    Exercise("Rosca no cabo", _k(["rosca no cabo", "cable curl"]), 5.0, 2.8, "Biceps"),

    # ANTEBRACO
    Exercise("Rosca punho", _k(["rosca punho"]), 3.8, 2.2, "Antebraco"),
    Exercise("Rosca inversa", _k(["rosca inversa"]), 4.2, 2.6, "Antebraco"),
    Exercise("Extensao de punho", _k(["extensao de punho"]), 3.6, 2.2, "Antebraco"),
    Exercise("Pegada isometrica", _k(["pegada isometrica"]), 4.0, 4.0, "Antebraco"),
    Exercise("Dead hang", _k(["dead hang"]), 5.5, 4.0, "Antebraco"),
    Exercise("Farmer walk", _k(["farmer walk", "farmer"]), 7.0, 3.5, "Antebraco"),

    # QUADRICEPS
    Exercise("Agachamento", _k(["agachamento", "squat"]), 5.0, 3.0, "Quadriceps"),
    Exercise("Agachamento salto", _k(["agachamento salto", "jump squat"]), 8.5, 2.2, "Quadriceps"),
    Exercise("Agachamento frontal", _k(["agachamento frontal", "front squat"]), 6.0, 3.0, "Quadriceps"),
    Exercise("Agachamento sumo", _k(["agachamento sumo", "sumo squat"]), 5.8, 3.0, "Quadriceps"),
    Exercise("Hack machine", _k(["hack machine", "hack squat"]), 5.8, 3.0, "Quadriceps"),
    Exercise("Leg press", _k(["leg press"]), 5.5, 3.0, "Quadriceps"),
    Exercise("Extensora", _k(["extensora", "cadeira extensora"]), 5.0, 2.8, "Quadriceps"),
    Exercise("Cadeira extensora unilateral", _k(["cadeira extensora unilateral", "extensora unilateral"]), 5.1, 2.8, "Quadriceps"),
    Exercise("Afundo", _k(["afundo", "split squat"]), 6.0, 2.8, "Quadriceps"),

    # POSTERIOR
    Exercise("Stiff", _k(["stiff", "levantamento romeno"]), 6.0, 3.0, "Posterior"),
    Exercise("Mesa flexora", _k(["mesa flexora", "flexora"]), 4.8, 2.8, "Posterior"),
    Exercise("Good morning", _k(["good morning"]), 5.5, 3.0, "Posterior"),
    Exercise("Stiff unilateral", _k(["stiff unilateral"]), 6.2, 3.0, "Posterior"),
    Exercise("Nordic curl", _k(["nordic curl"]), 7.5, 3.0, "Posterior"),
    Exercise("Flexora em pe", _k(["flexora em pe"]), 4.9, 2.8, "Posterior"),
    Exercise("Flexora unilateral", _k(["flexora unilateral"]), 4.9, 2.8, "Posterior"),

    # GLUTEO
    Exercise("Avanco", _k(["avanco", "passada", "lunge"]), 6.0, 2.8, "Gluteo"),
    Exercise("Elevacao pelvica", _k(["elevacao pelvica", "hip thrust"]), 5.2, 3.0, "Gluteo"),
    Exercise("Subida na caixa", _k(["subida na caixa", "step up", "caixa"]), 8.0, 2.5, "Gluteo"),
    Exercise("Glute bridge", _k(["glute bridge"]), 5.0, 3.0, "Gluteo"),
    Exercise("Abducao quadril", _k(["abducao quadril"]), 4.2, 2.6, "Gluteo"),
    Exercise("Kickback no cabo", _k(["kickback no cabo", "cable kickback"]), 4.6, 2.8, "Gluteo"),
    Exercise("Step up", _k(["step up"]), 8.0, 2.5, "Gluteo"),
    Exercise("Agachamento bulgaro", _k(["agachamento bulgaro", "bulgarian split squat"]), 6.3, 2.8, "Gluteo"),

    # ADUTOR / ABDUTOR
    Exercise("Adutora maquina", _k(["adutora maquina", "adutora"]), 4.0, 2.6, "Adutor"),
    Exercise("Abducao maquina", _k(["abducao maquina", "abdutora"]), 4.0, 2.6, "Abdutor"),
    Exercise("Abducao elastico", _k(["abducao elastico"]), 4.4, 2.6, "Abdutor"),
    Exercise("Sumo deadlift", _k(["sumo deadlift", "terra sumo"]), 7.8, 3.2, "Adutor Abdutor"),
    Exercise("Adutor unilateral", _k(["adutor unilateral"]), 4.2, 2.6, "Adutor"),

    # PANTURRILHA
    Exercise("Panturrilha em pe", _k(["panturrilha em pe", "panturrilha pe"]), 4.0, 2.0, "Panturrilha"),
    Exercise("Panturrilha sentado", _k(["panturrilha sentado", "panturrilha sentada"]), 3.8, 2.0, "Panturrilha"),
    Exercise("Panturrilha no leg press", _k(["panturrilha no leg press"]), 4.1, 2.0, "Panturrilha"),
    Exercise("Panturrilha unilateral", _k(["panturrilha unilateral"]), 4.2, 2.0, "Panturrilha"),
    Exercise("Panturrilha no smith", _k(["panturrilha no smith"]), 4.1, 2.0, "Panturrilha"),
    Exercise("Saltos pliometricos", _k(["saltos pliometricos", "plyo jump"]), 10.0, 1.8, "Panturrilha"),

    # CARDIO
    Exercise("Caminhada inclinada", _k(["caminhada inclinada"]), 6.5, 2.0, "Cardio"),
    Exercise("Corrida leve", _k(["corrida leve", "trote"]), 8.3, 2.0, "Cardio"),
    Exercise("Corrida intensa", _k(["corrida intensa"]), 11.0, 1.6, "Cardio"),
    Exercise("HIIT corrida", _k(["hiit corrida"]), 12.0, 1.3, "Cardio"),
    Exercise("Escada", _k(["escada", "stair climber"]), 8.8, 2.0, "Cardio"),
    Exercise("Eliptico", _k(["eliptico", "elliptical"]), 7.0, 2.0, "Cardio"),
    Exercise("Remo", _k(["remo", "rowing"]), 7.0, 2.2, "Cardio"),
    Exercise("Bicicleta", _k(["bicicleta", "bike"]), 7.5, 2.5, "Cardio"),
    Exercise("Pular corda", _k(["pular corda"]), 12.0, 1.0, "Cardio"),
    Exercise("Box jump", _k(["box jump"]), 9.5, 1.8, "Cardio"),
    Exercise("Mountain climber", _k(["mountain climber"]), 8.0, 1.2, "Cardio"),
    Exercise("Polichinelo", _k(["polichinelo", "jumping jack"]), 8.0, 1.4, "Cardio"),
    Exercise("Sprint", _k(["sprint"]), 11.5, 1.2, "Cardio"),
    Exercise("Burpee", _k(["burpee"]), 10.0, 3.5, "Cardio"),
]
