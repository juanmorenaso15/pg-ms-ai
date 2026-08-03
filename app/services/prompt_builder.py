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
    """Construye el prompt para generar un plan nutricional con detalles completos"""
    
    restricciones = contexto.get('restriccionesDieteticas', [])
    restricciones_texto = ", ".join(restricciones) if restricciones else "Ninguna"
    
    alergias = contexto.get('alergias', [])
    alergias_texto = ", ".join(alergias) if alergias else "Ninguna"
    
    prompt = f"""
Eres un nutricionista experto en deporte y fitness especializado en planes personalizados.

DATOS DEL SOCIO:
- Nombre: {contexto.get('nombre', 'No especificado')}
- Edad: {contexto.get('edad', 0)} años
- Peso: {contexto.get('peso', 'No especificado')} kg
- Estatura: {contexto.get('estatura', 'No especificado')} cm
- Objetivo principal: {contexto.get('objetivoPrincipal', 'No especificado')}
- Nivel de experiencia: {contexto.get('nivelExperiencia', 'No especificado')}
- Porcentaje grasa: {contexto.get('porcentajeGrasa', 'No especificado')}%
- Condiciones médicas: {contexto.get('condicionesCronicas', 'Ninguna')}
- Alergias: {alergias_texto}
- Restricciones dietéticas: {restricciones_texto}
- Días de entrenamiento: {contexto.get('diasEntrenamiento', 0)}
- Objetivo específico: {contexto.get('objetivoEspecifico', 'Mejorar condición física')}

**INSTRUCCIONES IMPORTANTES:**

1. Las restricciones dietéticas del socio son: {restricciones_texto}
   - Si NO hay restricciones, el campo `restricciones_dieteticas` debe ser una lista vacía `[]`
   - Si HAY restricciones (ej: vegetariano, vegano, sin gluten), deben aparecer en la lista

2. **CADA SUGERENCIA DE COMIDA DEBE TENER TODOS ESTOS CAMPOS OBLIGATORIOS:**
   - `nombre`: Nombre del plato (ej: "Avena con frutas y almendras")
   - `descripcion`: Breve descripción del plato y sus beneficios (ej: "Desayuno energético rico en fibra y proteínas")
   - `ingredientes`: Lista detallada de ingredientes separados por coma (ej: "Avena, leche de almendras, plátano, fresas, almendras")
   - `preparacion`: Instrucciones claras de preparación (ej: "Cocinar la avena con leche de almendras, añadir frutas picadas y almendras")
   - `calorias`: Número entero
   - `proteinas`, `carbohidratos`, `grasas`: Números decimales

3. **NO DEJES NINGÚN CAMPO COMO null - TODOS DEBEN TENER VALOR**

4. **FORMATO DE RESPUESTA - SOLO JSON válido, sin markdown, sin texto adicional:**

{{
    "calorias_diarias": 2200,
    "proteinas_g": 150.0,
    "carbohidratos_g": 250.0,
    "grasas_g": 70.0,
    "restricciones_dieteticas": [],
    "sugerencias_comidas": {{
        "desayuno": [
            {{
                "nombre": "Avena con frutas y almendras",
                "descripcion": "Desayuno energético rico en fibra y proteínas para empezar el día con energía",
                "ingredientes": "Avena, leche de almendras, plátano, fresas, almendras picadas",
                "preparacion": "Cocinar la avena con leche de almendras a fuego medio durante 5 minutos. Añadir frutas picadas y almendras por encima",
                "calorias": 350,
                "proteinas": 10.0,
                "carbohidratos": 50.0,
                "grasas": 8.0
            }}
        ],
        "almuerzo": [
            {{
                "nombre": "Pechuga de pollo con quinoa",
                "descripcion": "Almuerzo completo con proteínas magras y carbohidratos complejos",
                "ingredientes": "Pechuga de pollo, quinoa, brócoli, zanahoria, aceite de oliva",
                "preparacion": "Cocinar la pechuga a la plancha. Cocer la quinoa. Saltear verduras. Servir con aceite de oliva",
                "calorias": 600,
                "proteinas": 40.0,
                "carbohidratos": 60.0,
                "grasas": 15.0
            }}
        ],
        "cena": [
            {{
                "nombre": "Salmón con espárragos",
                "descripcion": "Cena ligera rica en omega-3 y antioxidantes",
                "ingredientes": "Salmón, espárragos, limón, ajo, aceite de oliva",
                "preparacion": "Hornear el salmón con espárragos a 180°C durante 20 minutos. Aliñar con limón y ajo",
                "calorias": 450,
                "proteinas": 35.0,
                "carbohidratos": 10.0,
                "grasas": 20.0
            }}
        ],
        "colaciones": [
            {{
                "nombre": "Batido de proteínas y frutas",
                "descripcion": "Colación nutritiva para recuperación muscular",
                "ingredientes": "Leche de almendras, plátano, proteína de suero, miel",
                "preparacion": "Licuar todos los ingredientes hasta obtener una mezcla homogénea",
                "calorias": 200,
                "proteinas": 20.0,
                "carbohidratos": 25.0,
                "grasas": 5.0
            }}
        ]
    }},
    "explicacion_ia": "Explicación detallada de por qué este plan es adecuado para el socio"
}}

**RESPONDE SOLO CON JSON VÁLIDO. TODOS LOS CAMPOS DEBEN TENER VALOR. NINGÚN CAMPO PUEDE SER null.**
"""
    return prompt