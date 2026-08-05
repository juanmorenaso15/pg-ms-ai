from typing import Dict, Any, List

def build_prompt(contexto: Dict[str, Any]) -> str:
    """
    Construye el prompt para Groq basado en el contexto del socio.
    """
    
    ejercicios_disponibles = contexto.get("ejerciciosDisponibles", [])
    
    prompt = f"""
Eres un entrenador personal experto en fitness y nutrición.

DATOS DEL SOCIO:
- Nombre: {contexto.get('nombre', 'No especificado')}
- Edad: {contexto.get('edad', 0)} años
- Peso: {contexto.get('peso', 'No especificado')} kg
- Estatura: {contexto.get('estatura', 'No especificado')} cm
- Nivel: {contexto.get('nivelExperiencia', 'No especificado')}
- Objetivo: {contexto.get('objetivoPrincipal', 'No especificado')}
- Lesiones: {contexto.get('lesionesPrevias', 'Ninguna')}
- Condiciones: {contexto.get('condicionesCronicas', 'Ninguna')}
- Días por semana: {contexto.get('diasPorSemana', 3)}
- Duración: {contexto.get('duracionSemanas', 4)} semanas
- Cardio: {contexto.get('incluirCardio', True)}

EJERCICIOS DISPONIBLES ({len(ejercicios_disponibles)}):
"""
    
    for ej in ejercicios_disponibles[:20]:
        prompt += f"- {ej.get('nombre')} ({ej.get('grupoMuscular')})\n"
    
    prompt += """

RESPONDE SOLO CON JSON. SIN MARKDOWN. SIN ```json.

EL JSON DEBE TENER EXACTAMENTE ESTA ESTRUCTURA:
{
    "nombre": "Nombre de la rutina",
    "descripcion": "Descripción breve",
    "explicacionIA": "Explicación de por qué esta rutina es adecuada",
    "detalles": [
        {
            "diaSemana": 1,
            "orden": 1,
            "nombreEjercicio": "Press de Banca",
            "series": 4,
            "repeticionesMin": 8,
            "repeticionesMax": 12,
            "pesoSugerido": 20.0,
            "descansoSegundos": 60,
            "notas": "Mantener la espalda plana"
        }
    ]
}

SOLO JSON. SIN TEXTO ADICIONAL.
"""
    
    return prompt

def build_prompt_nutricional(contexto: Dict[str, Any]) -> str:
    """Construye el prompt para generar un plan nutricional"""
    
    prompt = f"""
Eres un nutricionista experto en deporte y fitness.

DATOS DEL SOCIO:
- Nombre: {contexto.get('nombre', 'No especificado')}
- Edad: {contexto.get('edad', 0)} años
- Peso: {contexto.get('peso', 'No especificado')} kg
- Estatura: {contexto.get('estatura', 'No especificado')} cm
- Objetivo: {contexto.get('objetivoPrincipal', 'No especificado')}
- Nivel: {contexto.get('nivelExperiencia', 'No especificado')}
- Porcentaje grasa: {contexto.get('porcentajeGrasa', 'No especificado')}%
- Condiciones: {contexto.get('condicionesCronicas', 'Ninguna')}
- Alergias: {contexto.get('alergias', 'Ninguna')}
- Días entrenamiento: {contexto.get('diasEntrenamiento', 0)}
- Restricciones dietéticas: {contexto.get('restriccionesDieteticas', 'Ninguna')}
- Objetivo específico: {contexto.get('objetivoEspecifico', 'Mantener peso')}

RESPONDE SOLO CON JSON:
{{
    "calorias_diarias": 2200,
    "proteinas_g": 150.0,
    "carbohidratos_g": 250.0,
    "grasas_g": 70.0,
    "sugerencias_comidas": {{
        "desayuno": [
            {{"nombre": "Avena con frutas", "calorias": 350, "proteinas": 10, "carbohidratos": 50, "grasas": 8}}
        ],
        "almuerzo": [...],
        "cena": [...],
        "colaciones": [...]
    }},
    "explicacion_ia": "Explicación del plan"
}}
"""
    return prompt