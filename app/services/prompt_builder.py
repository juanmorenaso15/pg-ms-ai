from typing import Dict, Any, List

def build_prompt(contexto: Dict[str, Any]) -> str:
    """
    Construye el prompt optimizado para Groq basado en el contexto del socio,
    garantizando alta variedad de ejercicios y progresión real por semanas.
    """
    
    ejercicios_disponibles = contexto.get("ejerciciosDisponibles", [])
    equipos_disponibles = contexto.get("equiposDisponibles", [])
    dias_por_semana = contexto.get('diasPorSemana', 3)
    duracion_semanas = contexto.get('duracionSemanas', 4)
    
    prompt = f"""
Eres un entrenador personal de élite, especialista en programación del entrenamiento, biomecánica y periodización avanzada para hipertrofia y fuerza. Tu meta es evitar rutinas aburridas o repetitivas.

DATOS DEL SOCIO:
- Nombre: {contexto.get('nombre', 'No especificado')}
- Edad: {contexto.get('edad', 0)} años
- Peso: {contexto.get('peso', 'No especificado')} kg
- Estatura: {contexto.get('estatura', 'No especificado')} cm
- Nivel: {contexto.get('nivelExperiencia', 'No especificado')}
- Objetivo: {contexto.get('objetivoPrincipal', 'No especificado')}
- Lesiones o limitaciones (EVITAR EJERCICIOS QUE AFECTEN ESTO): {contexto.get('lesionesPrevias', 'Ninguna')}
- Condiciones médicas: {contexto.get('condicionesCronicas', 'Ninguna')}
- Días por semana: {dias_por_semana}
- Duración total: {duracion_semanas} semanas
- Incluir Cardio: {contexto.get('incluirCardio', True)}

LISTADO DE EJERCICIOS DISPONIBLES EN EL SISTEMA ({len(ejercicios_disponibles)} totales):
Selecciona exclusivamente ejercicios de esta lista o variantes coherentes con los equipos disponibles.
"""
    
    for ej in ejercicios_disponibles[:60]:
        prompt += f"- ID/Nombre: {ej.get('nombre')} | Grupo Muscular: {ej.get('grupoMuscular')} | Equipo: {ej.get('equipoNecesario', 'Sin equipo')}\n"
    
    prompt += f"""

EQUIPOS DISPONIBLES EN EL GIMNASIO ({len(equipos_disponibles)}):
"""
    
    for eq in equipos_disponibles[:40]:
        prompt += f"- {eq.get('nombre')} ({eq.get('marca', '')} {eq.get('modelo', '')})\n"
    
    prompt += f"""

**INSTRUCCIONES CRÍTICAS PARA EVITAR RUTINAS MONÓTONAS:**
1. **VARIEDAD OBLIGATORIA ENTRE SEMANAS:** Prohibido copiar exactamente la misma estructura de ejercicios de la Semana 1 en la Semana 2, 3 o 4. Modifica variantes de ejercicios (ej: si en la semana 1 usas press plano con barra, en la semana siguiente usa press inclinado o con mancuernas) y aplica una **progresión lógica de cargas o repeticiones** semana a semana.
2. **ESTRUCTURA POR SEMANAS Y DÍAS:** Debes generar una rutina detallada que cubra obligatoriamente las {duracion_semanas} semanas. Incluye los días seleccionados (del día 1 al {dias_por_semana}) para la **Semana 1**, luego para la **Semana 2**, y así sucesivamente hasta la semana {duracion_semanas}.
3. **CANTIDAD DE EJERCICIOS:** Cada día de entrenamiento debe tener **MÍNIMO 4 A 6 EJERCICIOS DIFERENTES** bien distribuidos (compuestos y accesorios).
4. **EQUIPAMIENTO REAL:** CADA EJERCICIO DEBE INCLUIR EL EQUIPO NECESARIO (`equipoRequerido`) basándote estrictamente en las listas provistas. Si no requiere equipo, indica "Sin equipo".
5. **CAMPOS OBLIGATORIOS:** El campo `semana` (1, 2, 3...), `diaSemana` (1 a {dias_por_semana}) y `orden` (1, 2, 3...) deben estructurarse de forma impecable en el JSON. **NINGÚN EJERCICIO DEBE TENER `semana` COMO null**.

RESPONDE SOLO CON JSON VÁLIDO. SIN MARKDOWN. SIN ```json. SIN TEXTO ADICIONAL ANTES O DESPUÉS.

EL JSON DEBE TENER EXACTAMENTE ESTA ESTRUCTURA DE ARRAY EN "detalles":
{{
    "nombre": "Rutina avanzada de {duracion_semanas} semanas - Enfoque Dinámico",
    "descripcion": "Rutina periodizada enfocada en {contexto.get('objetivoPrincipal', 'fitness')} con variaciones semanales para evitar estancamiento.",
    "explicacionIA": "Explicación detallada de la progresión de cargas, la selección de ejercicios y por qué esta variación por semanas optimiza los resultados del socio.",
    "detalles": [
        {{
            "semana": 1,
            "diaSemana": 1,
            "orden": 1,
            "nombreEjercicio": "Nombre exacto del ejercicio",
            "series": 4,
            "repeticionesMin": 8,
            "repeticionesMax": 10,
            "pesoSugerido": 20.0,
            "descansoSegundos": 90,
            "notas": "Semana 1: Establecer base de fuerza con técnica perfecta.",
            "equipoRequerido": "Nombre del equipo"
        }}
    ]
}}
"""
    return prompt

def build_prompt_nutricional(contexto: Dict[str, Any]) -> str:
    """Construye el prompt para generar un plan nutricional con detalles completos y alta variedad"""
    
    restricciones = contexto.get('restricciones_dieteticas', [])
    restricciones_texto = ", ".join(restricciones) if restricciones else "Ninguna"
    
    alergias = contexto.get('alergias', [])
    alergias_texto = ", ".join(alergias) if alergias else "Ninguna"
    
    id_socio = contexto.get('id_socio', 1)
    
    prompt = f"""
Eres un nutricionista deportivo de élite, creativo y altamente especializado en romper la monotonía de las dietas.

DATOS DEL SOCIO (ID: {id_socio}):
- Nombre: {contexto.get('nombre', 'No especificado')}
- Edad: {contexto.get('edad', 0)} años
- Peso: {contexto.get('peso', 'No especificado')} kg
- Estatura: {contexto.get('estatura', 'No especificado')} cm
- Objetivo principal: {contexto.get('objetivoPrincipal', 'No especificado')}
- Nivel de experiencia: {contexto.get('nivelExperiencia', 'No especificado')}
- Condiciones médicas: {contexto.get('condicionesCronicas', 'Ninguna')}
- Alergias (EVITAR ABSOLUTAMENTE): {alergias_texto}
- Restricciones dietéticas: {restricciones_texto}
- Días de entrenamiento: {contexto.get('diasEntrenamiento', 0)}
- Objetivo específico: {contexto.get('objetivoEspecifico', 'Mejorar condición física')}

**INSTRUCCIONES CRÍTICAS PARA EVITAR DIETAS REPETITIVAS:**
1. **PROHIBIDO RECICLAR EL MENÚ ESTÁNDAR:** No uses siempre avena con plátano en el desayuno, ni pechuga con quinoa en el almuerzo, ni salmón con espárragos en la cena a menos que el perfil lo exija estrictamente. Varía las fuentes de carbohidratos (ej. batata, yuca, arroz basmati, pasta integral, tortitas de arroz, pan de centeno), proteínas (ej. lomo de cerdo magro, atún, huevos, pavo, tofu, legumbres) y grasas (ej. aguacate, mantequilla de maní -si no hay alergia-, aceite de oliva, semillas de chía/girasol).
2. **CREATIVIDAD Y VARIEDAD:** Diseña sugerencias culinarias atractivas, funcionales y adaptadas de forma única a este requerimiento.
3. Las restricciones dietéticas del socio son: {restricciones_texto}. Respétalas al 100%.
4. **CADA SUGERENCIA DE COMIDA DEBE TENER TODOS ESTOS CAMPOS OBLIGATORIOS:**
   - `nombre`: Nombre creativo del plato.
   - `descripcion`: Beneficios nutricionales específicos.
   - `ingredientes`: Lista detallada de ingredientes separados por coma.
   - `preparacion`: Instrucciones claras de preparación paso a paso.
   - `calorias`: Número entero.
   - `proteinas`, `carbohidratos`, `grasas`: Números decimales.

5. **FORMATO DE RESPUESTA - SOLO JSON válido, sin markdown, sin texto adicional:**

{{
    "calorias_diarias": 2200,
    "proteinas_g": 150.0,
    "carbohidratos_g": 250.0,
    "grasas_g": 70.0,
    "restricciones_dieteticas": {restricciones},
    "sugerencias_comidas": {{
        "desayuno": [
            {{
                "nombre": "Ejemplo dinámico (crea uno nuevo y original)",
                "descripcion": "Descripción adaptada",
                "ingredientes": "Ingredientes variados",
                "preparacion": "Pasos de preparación",
                "calorias": 350,
                "proteinas": 10.0,
                "carbohidratos": 50.0,
                "grasas": 8.0
            }}
        ],
        "almuerzo": [
            {{
                "nombre": "Plato de almuerzo alternativo y creativo",
                "descripcion": "Descripción adaptada",
                "ingredientes": "Ingredientes variados",
                "preparacion": "Pasos de preparación",
                "calorias": 600,
                "proteinas": 40.0,
                "carbohidratos": 60.0,
                "grasas": 15.0
            }}
        ],
        "cena": [
            {{
                "nombre": "Plato de cena ligero y alternativo",
                "descripcion": "Descripción adaptada",
                "ingredientes": "Ingredientes variados",
                "preparacion": "Pasos de preparación",
                "calorias": 450,
                "proteinas": 35.0,
                "carbohidratos": 10.0,
                "grasas": 20.0
            }}
        ],
        "colaciones": [
            {{
                "nombre": "Snack o colación funcional",
                "descripcion": "Descripción adaptada",
                "ingredientes": "Ingredientes variados",
                "preparacion": "Pasos de preparación",
                "calorias": 200,
                "proteinas": 20.0,
                "carbohidratos": 25.0,
                "grasas": 5.0
            }}
        ]
    }},
    "explicacion_ia": "Explicación detallada de por qué este plan específico y variado se adapta al socio."
}}

**RESPONDE SOLO CON JSON VÁLIDO. NO REPITAS LOS MISMOS PLATOS DE PRUEBAS ANTERIORES.**
"""
    return prompt