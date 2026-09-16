from typing import Dict, Any, List

def build_prompt(contexto: Dict[str, Any]) -> str:
    """
    Construye el prompt optimizado para Groq basado en el contexto del socio,
    los equipos disponibles en su sede y los ejercicios existentes en la BD.
    """
    
    ejercicios_disponibles = contexto.get("ejerciciosDisponibles", [])
    equipos_disponibles = contexto.get("equiposDisponibles", [])
    dias_por_semana = contexto.get('diasPorSemana', 3)
    
    prompt = f"""
Eres un entrenador personal de élite, especialista en programación del entrenamiento, hipertrofia y acondicionamiento físico (CrossFit/Funcional).

DATOS DEL SOCIO:
- Nombre: {contexto.get('nombre', 'No especificado')}
- Edad: {contexto.get('edad', 0)} años
- Peso: {contexto.get('peso', 'No especificado')} kg
- Estatura: {contexto.get('estatura', 'No especificado')} cm
- Nivel: {contexto.get('nivelExperiencia', 'No especificado')}
- Objetivo: {contexto.get('objetivoPrincipal', 'No especificado')}
- Lesiones o limitaciones (EVITAR): {contexto.get('lesionesPrevias', 'Ninguna')}
- Condiciones médicas: {contexto.get('condicionesCronicas', 'Ninguna')}
- Días por semana a entrenar: {dias_por_semana}
- Duración total: EXACTAMENTE 1 SEMANA (semana 1 únicamente).
- Incluir Cardio: {contexto.get('incluirCardio', True)}

EQUIPOS DISPONIBLES EN LA SEDE DEL GIMNASIO ({len(equipos_disponibles)} total):
"""
    if equipos_disponibles:
        for eq in equipos_disponibles[:50]:
            prompt += f"- {eq.get('nombre')} (Ubicación: {eq.get('ubicacion')})\n"
    else:
        prompt += "- No hay equipos registrados en la sede (enfocarse en peso corporal/calistenia).\n"

    prompt += f"\nLISTADO DE EJERCICIOS EXISTENTES EN LA BASE DE DATOS ({len(ejercicios_disponibles)} totales):\n"
    if ejercicios_disponibles:
        for ej in ejercicios_disponibles[:60]:
            prompt += f"- Nombre: {ej.get('nombre')} | Grupo: {ej.get('grupoMuscular')} | Equipo: {ej.get('equipoNecesario', 'Sin equipo')}\n"
    else:
        prompt += "No hay ejercicios registrados previamente.\n"
    
    prompt += f"""

**INSTRUCCIONES CRÍTICAS Y OBLIGATORIAS:**
1. **DURACIÓN DE UNA SEMANA:** Genera la rutina exclusivamente para la **Semana 1**.
2. **DÍAS Y CANTIDAD DE EJERCICIOS:** Genera exactamente {dias_por_semana} días de entrenamiento (del día 1 al {dias_por_semana}). Cada día debe contener **MÍNIMO 5 EJERCICIOS DIFERENTES**.
3. **INVENTAR / CREAR EJERCICIOS NUEVOS (CRÍTICO):** Puedes reutilizar los ejercicios de la base de datos, **PERO TAMBIÉN PUEDES CREAR Y PROPONER EJERCICIOS NUEVOS** (tanto usando las máquinas de los equipos disponibles como ejercicios libres, funcionales, de calistenia o estilo CrossFit, ej. sentadilla búlgara, flexiones diamante, burpees, clean and jerk, etc.) para ofrecer la mejor variedad posible.
4. **GRUPO MUSCULAR OBLIGATORIO:** CADA ejercicio DEBE incluir su `grupoMuscular` exacto entre: "PECHO", "ESPALDA", "PIERNA", "HOMBRO", "BRAZO", "CORE", "CARDIO". **PROHIBIDO dejarlo vacío**.
5. **EQUIPAMIENTO REQUERIDO:** Indica claramente el `equipoRequerido` para cada ejercicio (puede ser una máquina de la lista de equipos, peso corporal, mancuernas, barra, etc.).
6. **CAMPOS OBLIGATORIOS:** `semana` = `1`, `diaSemana` de 1 al {dias_por_semana}, y `orden` correlativo por día.

RESPONDE SOLO CON JSON VÁLIDO. SIN MARKDOWN. SIN ```json. SIN TEXTO ADICIONAL.

EL JSON DEBE TENER EXACTAMENTE ESTA ESTRUCTURA:
{{
    "nombre": "Rutina personalizada de 1 semana",
    "descripcion": "Rutina enfocada en {contexto.get('objetivoPrincipal', 'fitness')} con {dias_por_semana} días de entrenamiento.",
    "explicacionIA": "Explicación detallada de la selección de ejercicios y combinación de equipos.",
    "detalles": [
        {{
            "semana": 1,
            "diaSemana": 1,
            "orden": 1,
            "nombreEjercicio": "Nombre exacto y creativo del ejercicio",
            "grupoMuscular": "PIERNA",
            "series": 4,
            "repeticionesMin": 8,
            "repeticionesMax": 12,
            "pesoSugerido": 0.0,
            "descansoSegundos": 60,
            "notas": "Mantener la espalda recta.",
            "equipoRequerido": "Peso corporal"
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