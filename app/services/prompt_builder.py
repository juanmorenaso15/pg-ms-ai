from typing import Dict, Any, List, Tuple

GRUPOS_VALIDOS = ["PECHO", "ESPALDA", "PIERNA", "HOMBRO", "BRAZO", "CORE", "CARDIO"]

# Split profesional de entrenamiento según los días/semana disponibles.
# Cada día es una lista de (grupo_muscular, énfasis_opcional).
# Sigue esquemas reales de entrenador (Full Body, Upper/Lower, Push/Pull/Legs, Bro split)
# y evita repetir el mismo grupo principal en días consecutivos para permitir recuperación.
SPLITS_POR_DIA: Dict[int, List[List[Tuple[str, str]]]] = {
    1: [
        [("PECHO", ""), ("ESPALDA", ""), ("PIERNA", ""), ("HOMBRO", ""), ("BRAZO", ""), ("CORE", "")],
    ],
    2: [
        [("PECHO", ""), ("ESPALDA", ""), ("HOMBRO", ""), ("BRAZO", "")],
        [("PIERNA", ""), ("CORE", "")],
    ],
    3: [
        [("PIERNA", ""), ("CORE", "")],
        [("HOMBRO", ""), ("PECHO", "")],
        [("ESPALDA", ""), ("BRAZO", "")],
    ],
    4: [
        [("PIERNA", ""), ("CORE", "")],
        [("PECHO", ""), ("BRAZO", "énfasis tríceps")],
        [("HOMBRO", ""), ("CORE", "")],
        [("ESPALDA", ""), ("BRAZO", "énfasis bíceps")],
    ],
    5: [
        [("PIERNA", "")],
        [("PECHO", "")],
        [("ESPALDA", "")],
        [("HOMBRO", "")],
        [("BRAZO", ""), ("CORE", "")],
    ],
    6: [
        [("PIERNA", ""), ("CORE", "")],
        [("PECHO", ""), ("HOMBRO", "")],
        [("ESPALDA", ""), ("BRAZO", "énfasis bíceps")],
        [("PIERNA", ""), ("CORE", "")],
        [("PECHO", ""), ("BRAZO", "énfasis tríceps")],
        [("ESPALDA", ""), ("HOMBRO", "")],
    ],
    7: [
        [("PIERNA", ""), ("CORE", "")],
        [("PECHO", ""), ("HOMBRO", "")],
        [("ESPALDA", ""), ("BRAZO", "énfasis bíceps")],
        [("PIERNA", ""), ("CORE", "")],
        [("PECHO", ""), ("BRAZO", "énfasis tríceps")],
        [("ESPALDA", ""), ("HOMBRO", "")],
        [("CORE", ""), ("CARDIO", "recuperación activa")],
    ],
}

# Palabras clave para emparejar el NOMBRE REAL de cada equipo de la sede (texto libre en BD)
# con el/los grupo(s) muscular(es) que trabaja. Se hace en Python (no se le deja la inferencia
# al modelo) porque los equipos NO tienen un campo grupoMuscular en la base de datos.
PALABRAS_CLAVE_GRUPO = {
    "PIERNA": ["sentadilla", "squat", "prensa", "pierna", "cuadriceps", "cuádriceps", "isquio",
               "zancada", "camilla", "aductor", "abductor", "pantorrilla", "gemelo", "hack squat",
               "peso muerto", "femoral"],
    "PECHO": ["pecho", "press banca", "press de banca", "press inclinado", "press plano", "pec deck",
              "banco plano", "banco inclinado", "press pecho", "pres inclinado", "pres plano",
              "pres banca", "fondos"],
    "ESPALDA": ["espalda", "jalon", "jalón", "dorsal", "remo", "lat pulldown", "polea alta", "polea baja",
                "dominada"],
    "HOMBRO": ["hombro", "press militar", "elevacion lateral", "elevación lateral", "deltoide",
               "press hombro", "press de hombro"],
    "BRAZO": ["biceps", "bíceps", "triceps", "tríceps", "curl", "scott", "barra z"],
    "CORE": ["abdominal", "core", "abdominales", "rueda abdominal", "banco romano"],
    "CARDIO": ["caminadora", "cinta de correr", "trotadora", "bicicleta", "eliptica", "elíptica",
               "spinning", "escaladora", "remadora", "cardio"],
}


def _clasificar_equipo(nombre_equipo: str) -> List[str]:
    """Devuelve los grupos musculares que probablemente trabaja un equipo, según su nombre."""
    nombre = (nombre_equipo or "").lower()
    return [grupo for grupo, palabras in PALABRAS_CLAVE_GRUPO.items() if any(p in nombre for p in palabras)]


def _normalizar_dias(dias_por_semana: Any) -> int:
    try:
        dias = int(dias_por_semana)
    except (TypeError, ValueError):
        dias = 3
    if dias not in SPLITS_POR_DIA:
        dias = 3
    return dias


def _formatear_grupos(grupos: List[Tuple[str, str]]) -> str:
    partes = [f"{grupo} ({enfasis})" if enfasis else grupo for grupo, enfasis in grupos]
    return " + ".join(partes)


GUIA_POR_NIVEL = {
    "PRINCIPIANTE": "técnica simple y controlada, 3 series por ejercicio, EVITA movimientos muy técnicos o de alto riesgo (levantamientos olímpicos, pliometría intensa, pistol squat sin asistencia); prioriza aprender bien el patrón de movimiento.",
    "INTERMEDIO": "volumen moderado (3-4 series), puedes incluir superseries ocasionales y progresión de carga.",
    "AVANZADO": "mayor volumen e intensidad (4-5 series), puedes usar técnicas avanzadas (drop sets, tempo controlado, superseries, rangos de repetición más exigentes).",
}


def _guia_nivel(nivel_experiencia: str) -> str:
    clave = (nivel_experiencia or "").strip().upper()
    return GUIA_POR_NIVEL.get(clave, "ajusta la dificultad y el volumen de forma coherente con el nivel indicado del socio.")


def _guia_objetivo(objetivo_principal: str) -> str:
    o = (objetivo_principal or "").lower()
    if any(k in o for k in ["ganar peso", "masa", "hipertrofia", "volumen", "musculo", "músculo"]):
        return ("prioriza ejercicios compuestos con CARGA EXTERNA (máquinas, mancuernas, barra) en 8-12 repeticiones "
                "y descansos de 60-90s; el peso corporal solo permite sobrecarga progresiva limitada, así que redúcelo "
                "al mínimo posible en los días donde haya equipo disponible para ese grupo muscular.")
    if any(k in o for k in ["perder peso", "bajar de peso", "grasa", "definicion", "definición", "adelgazar"]):
        return ("prioriza descansos cortos (30-45s), mayor densidad (circuitos, superseries) y repeticiones de 12-20; "
                "combina fuerza con el finisher de cardio cuando aplique.")
    if "fuerza" in o:
        return "prioriza ejercicios básicos compuestos con barra/máquina, repeticiones bajas (4-6) y descansos largos (90-150s)."
    if any(k in o for k in ["resistencia", "acondicionamiento"]):
        return "prioriza repeticiones altas (15-25), descansos cortos y una estructura tipo circuito."
    return "ajusta series, repeticiones y descansos de forma coherente con este objetivo específico."


def _es_valor_vacio(valor: Any) -> bool:
    if not valor:
        return True
    return str(valor).strip().lower() in ("", "ninguna", "ninguno", "no", "n/a", "none")


def build_prompt(contexto: Dict[str, Any]) -> str:
    """
    Construye el prompt optimizado para Groq basado en el contexto del socio,
    los equipos disponibles en su sede y los ejercicios existentes en la BD.
    """

    ejercicios_disponibles = contexto.get("ejerciciosDisponibles", [])
    equipos_disponibles = contexto.get("equiposDisponibles", [])
    dias_por_semana = _normalizar_dias(contexto.get('diasPorSemana', 3))
    hay_equipos = len(equipos_disponibles) > 0

    preferencias_grupos = contexto.get('preferenciasGruposMusculares') or []
    preferencias_equipo = contexto.get('preferenciasEquipamiento') or []
    evitar_ejercicios = contexto.get('evitarEjercicios') or []

    split = SPLITS_POR_DIA[dias_por_semana]

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
"""

    if preferencias_grupos:
        prompt += f"- Grupos musculares que el socio/entrenador pidió priorizar: {', '.join(preferencias_grupos)}\n"
    if preferencias_equipo:
        prompt += f"- Equipamiento que el socio/entrenador pidió priorizar: {', '.join(preferencias_equipo)}\n"
    if evitar_ejercicios:
        prompt += f"- Ejercicios PROHIBIDOS (no incluir bajo ninguna circunstancia): {', '.join(evitar_ejercicios)}\n"

    # Empareja cada equipo real de la sede con los grupos musculares que trabaja,
    # para poder decirle al modelo EXACTAMENTE qué máquina usar en cada día (sin dejárselo a su inferencia).
    equipos_por_grupo: Dict[str, List[str]] = {}
    equipos_sin_clasificar: List[str] = []
    for eq in equipos_disponibles:
        nombre_eq = eq.get('nombre')
        grupos_eq = _clasificar_equipo(nombre_eq)
        if grupos_eq:
            for g in grupos_eq:
                equipos_por_grupo.setdefault(g, [])
                if nombre_eq not in equipos_por_grupo[g]:
                    equipos_por_grupo[g].append(nombre_eq)
        else:
            equipos_sin_clasificar.append(nombre_eq)

    prompt += f"""
PLAN DE DIVISIÓN MUSCULAR POR DÍA (split profesional ya calculado - DEBES SEGUIRLO EXACTAMENTE):
"""
    for idx, grupos_dia in enumerate(split, start=1):
        prompt += f"- Día {idx}: {_formatear_grupos(grupos_dia)}\n"
        if hay_equipos:
            equipos_dia: List[str] = []
            for grupo, _ in grupos_dia:
                for nombre_eq in equipos_por_grupo.get(grupo, []):
                    if nombre_eq not in equipos_dia:
                        equipos_dia.append(nombre_eq)
            if equipos_dia:
                prompt += f"  Equipos de la sede a usar ESTE día (obligatorio, al menos uno por ejercicio principal): {', '.join(equipos_dia)}\n"
            else:
                prompt += "  (Ningún equipo de la sede coincide con este grupo muscular; usa mancuernas/barra libre/peso corporal aquí.)\n"

    prompt += f"""
EQUIPOS DISPONIBLES EN LA SEDE DEL GIMNASIO ({len(equipos_disponibles)} total):
"""
    if hay_equipos:
        for eq in equipos_disponibles[:50]:
            prompt += f"- {eq.get('nombre')} (Ubicación: {eq.get('ubicacion')})\n"
        if equipos_sin_clasificar:
            prompt += f"\nEquipos sin grupo muscular claro por su nombre (úsalos donde tengan sentido, o como apoyo general): {', '.join(equipos_sin_clasificar)}\n"
    else:
        prompt += "- No hay equipos registrados en la sede (enfocarse en peso corporal/calistenia).\n"

    ejercicios_por_grupo: Dict[str, List[Dict[str, Any]]] = {}
    for ej in ejercicios_disponibles:
        grupo = (ej.get('grupoMuscular') or 'GENERAL').upper()
        ejercicios_por_grupo.setdefault(grupo, []).append(ej)

    # Dentro de cada grupo, los ejercicios que YA usan un equipo real van primero.
    # Si el grupo tiene más ejercicios que el límite mostrado, esto evita que el truncado
    # deje afuera justo los que usan máquina (que en la BD suelen estar al final del listado).
    def _es_peso_corporal(ej: Dict[str, Any]) -> bool:
        equipo = (ej.get('equipoNecesario') or '').strip().lower()
        return equipo in ('', 'peso corporal', 'sin equipo', 'sin equipo específico')

    for grupo in ejercicios_por_grupo:
        ejercicios_por_grupo[grupo].sort(key=_es_peso_corporal)

    LIMITE_POR_GRUPO = 18

    prompt += f"\nLISTADO DE EJERCICIOS EXISTENTES EN LA BASE DE DATOS ({len(ejercicios_disponibles)} totales), agrupados por grupo muscular para que los reutilices en el día correspondiente (los que ya usan equipo real se listan primero):\n"
    if ejercicios_disponibles:
        for grupo in GRUPOS_VALIDOS:
            ejercicios_grupo = ejercicios_por_grupo.get(grupo, [])
            if not ejercicios_grupo:
                continue
            prompt += f"\n{grupo}:\n"
            for ej in ejercicios_grupo[:LIMITE_POR_GRUPO]:
                prompt += f"  - {ej.get('nombre')} | Equipo: {ej.get('equipoNecesario', 'Sin equipo')}\n"
        otros_grupos = set(ejercicios_por_grupo) - set(GRUPOS_VALIDOS)
        for grupo in otros_grupos:
            prompt += f"\n{grupo}:\n"
            for ej in ejercicios_por_grupo[grupo][:LIMITE_POR_GRUPO]:
                prompt += f"  - {ej.get('nombre')} | Equipo: {ej.get('equipoNecesario', 'Sin equipo')}\n"
    else:
        prompt += "No hay ejercicios registrados previamente.\n"

    instruccion_equipos = ""
    if hay_equipos:
        instruccion_equipos = f"""
4. **USO OBLIGATORIO DE EQUIPOS DISPONIBLES (CRÍTICO, PRIORIDAD MÁXIMA — por encima de la regla 6 de reutilización):** La sede SÍ tiene {len(equipos_disponibles)} equipos registrados.
   Arriba, en "PLAN DE DIVISIÓN MUSCULAR POR DÍA", te digo EXACTAMENTE qué equipo de la sede corresponde a cada día según su grupo muscular.
   Para cada día que tenga equipos listados: **TODOS los ejercicios de ese día deben usar uno de esos equipos exactos** (nombre EXACTO en `equipoRequerido`),
   generando ejercicios reales con ellos (ej. si el día dice "Máquina de Prensa" -> "Prensa de piernas en Máquina de Prensa"; si dice "Pres inclinado" -> "Press inclinado en Pres inclinado").
   Se permite **como máximo 1 ejercicio de "Peso corporal" por día** (ej. un finisher de core o cardio) — nunca más de 1 si el día tiene equipos asignados.
   Esta regla NO es opcional ni depende de la edad, nivel o condiciones médicas del socio (asma, principiante, etc. NO son motivo para evitar máquinas de fuerza; solo LESIONES específicas listadas abajo lo son).
   **PROHIBIDO generar un día con 2 o más ejercicios de peso corporal si ese día tiene equipos de la sede listados arriba. Revisa esto ANTES de responder.**
"""
    else:
        instruccion_equipos = """
4. **SIN EQUIPOS DISPONIBLES:** La sede no tiene equipos registrados, por lo que la rutina debe basarse
   en ejercicios de peso corporal, calistenia y trabajo funcional (sentadillas, flexiones, plancha,
   zancadas, burpees, dominadas, etc.).
"""

    nivel_raw = contexto.get('nivelExperiencia', '')
    objetivo_raw = contexto.get('objetivoPrincipal', '')
    lesiones_raw = contexto.get('lesionesPrevias')
    condiciones_raw = contexto.get('condicionesCronicas')

    instruccion_adaptacion = f"""
5. **ADAPTA LA RUTINA AL PERFIL REAL DEL SOCIO (CRÍTICO, no uses estos datos solo de forma decorativa):**
   - Nivel ({nivel_raw or 'No especificado'}): {_guia_nivel(nivel_raw)}
   - Objetivo ({objetivo_raw or 'No especificado'}): {_guia_objetivo(objetivo_raw)}
"""
    if not _es_valor_vacio(lesiones_raw):
        instruccion_adaptacion += (
            f'   - Lesiones/limitaciones: "{lesiones_raw}". EXCLUYE por completo cualquier ejercicio que cargue '
            f'o comprometa esa zona, y sustitúyelo por una alternativa segura del mismo grupo muscular.\n'
        )
    if not _es_valor_vacio(condiciones_raw):
        instruccion_adaptacion += (
            f'   - Condiciones médicas: "{condiciones_raw}". Ajusta intensidad y descansos en consecuencia '
            f'(ej. más descanso entre series o evitar esfuerzos isométricos máximos si hay temas '
            f'cardiorrespiratorios), pero SIN eliminar el uso de equipo salvo que la condición lo justifique '
            f'explícitamente para un ejercicio puntual.\n'
        )

    instruccion_preferencias = ""
    if preferencias_grupos or preferencias_equipo or evitar_ejercicios:
        instruccion_preferencias = "\n8. **PREFERENCIAS DEL SOCIO/ENTRENADOR (ajuste fino sobre el split anterior):**\n"
        if preferencias_grupos:
            instruccion_preferencias += f"   - Da volumen extra (1-2 ejercicios adicionales) a los grupos priorizados: {', '.join(preferencias_grupos)}, sin romper el split ni el orden de los días.\n"
        if preferencias_equipo:
            instruccion_preferencias += f"   - Prioriza usar este equipamiento siempre que el grupo muscular del día lo permita: {', '.join(preferencias_equipo)}.\n"
        if evitar_ejercicios:
            instruccion_preferencias += f"   - NUNCA incluyas estos ejercicios: {', '.join(evitar_ejercicios)}.\n"

    # El ejemplo del JSON usa un día de PIERNA, así que los equipos de ejemplo deben ser
    # los que realmente se clasificaron como PIERNA (nunca un equipo de otro grupo, ej. cardio).
    equipos_ejemplo_pierna = equipos_por_grupo.get('PIERNA', [])
    if equipos_ejemplo_pierna:
        ejemplo_equipo_1 = equipos_ejemplo_pierna[0]
        ejemplo_equipo_2 = equipos_ejemplo_pierna[1] if len(equipos_ejemplo_pierna) > 1 else equipos_ejemplo_pierna[0]
    elif hay_equipos:
        ejemplo_equipo_1 = equipos_disponibles[0].get('nombre')
        ejemplo_equipo_2 = equipos_disponibles[1].get('nombre') if len(equipos_disponibles) > 1 else ejemplo_equipo_1
    else:
        ejemplo_equipo_1 = "Máquina de Prensa"
        ejemplo_equipo_2 = "Máquina de Prensa"

    nombre_socio = contexto.get('nombre') or 'el socio'
    ejemplo_explicacion = (
        f"¡Hola {nombre_socio}! Diseñé esta rutina pensando en tu objetivo de "
        f"{contexto.get('objetivoPrincipal', 'mejorar tu condición física')}, priorizando las máquinas de tu sede "
        f"para que avances más rápido. Tuve en cuenta tus lesiones/condiciones para que entrenes seguro. ¡Vamos con todo!"
    )

    prompt += f"""

**INSTRUCCIONES CRÍTICAS Y OBLIGATORIAS:**
1. **DURACIÓN DE UNA SEMANA:** Genera la rutina exclusivamente para la **Semana 1**.
2. **DÍAS Y CANTIDAD DE EJERCICIOS:** Genera exactamente {dias_por_semana} días de entrenamiento (del día 1 al {dias_por_semana}). Cada día debe contener **ENTRE 5 Y 7 EJERCICIOS** (nunca menos de 5, nunca más de 7), sin importar si la semana tiene 3, 5 o 7 días de entrenamiento.
3. **RESPETA EL SPLIT DE GRUPOS MUSCULARES POR DÍA (CRÍTICO):** El campo `grupoMuscular` de CADA ejercicio del Día N debe ser EXACTAMENTE uno de los grupos asignados a ese día en el "PLAN DE DIVISIÓN MUSCULAR POR DÍA".
   **PROHIBIDO mezclar grupos musculares que no correspondan al día** (ej. prohibido meter un ejercicio de PECHO en un día asignado solo a PIERNA y CORE).
   Única excepción: si "Incluir Cardio" es true, puedes añadir opcionalmente 1 ejercicio extra de CARDIO como finisher en algunos días (no cuenta para el mínimo de 5, y no es necesario en todos los días).
{instruccion_equipos}{instruccion_adaptacion}
6. **REUTILIZAR EJERCICIOS EXISTENTES, PERO NO CREAR MÁS DE PESO CORPORAL (PRIORIDAD MENOR QUE LA REGLA 4):** La base de datos YA tiene decenas de ejercicios de peso corporal — **NO crees más variantes nuevas de peso corporal ni de "Mancuernas" genéricas.**
   Para cada día con equipos asignados: primero busca en el listado agrupado un ejercicio existente que use uno de esos equipos y reutilízalo; si no hay suficientes, **crea ejercicios NUEVOS usando el equipo real de la sede asignado a ese día** (nunca peso corporal como salida fácil).
   Ignora por completo los ejercicios de peso corporal ya existentes en la BD para ese grupo muscular si el día tiene equipo asignado — no los reutilices, no te sirven para cumplir la regla 4.
7. **GRUPO MUSCULAR OBLIGATORIO:** CADA ejercicio DEBE incluir su `grupoMuscular` exacto entre: "PECHO", "ESPALDA", "PIERNA", "HOMBRO", "BRAZO", "CORE", "CARDIO". **PROHIBIDO dejarlo vacío**.
{instruccion_preferencias}
9. **EQUIPAMIENTO REQUERIDO (sin inventar equipo que no existe en la sede):** Usa el nombre EXACTO de un equipo de "EQUIPOS DISPONIBLES EN LA SEDE" en `equipoRequerido` para todo ejercicio de un día con equipos asignados (regla 4).
   Usa "Peso corporal" ÚNICAMENTE en: (a) el único ejercicio complementario permitido por día (regla 4), o (b) días donde NINGÚN equipo de la sede coincide con el grupo muscular (ver "PLAN DE DIVISIÓN MUSCULAR POR DÍA").
   **PROHIBIDO escribir "Mancuernas", "Barra" o cualquier otro equipo genérico como `equipoRequerido` salvo que ese nombre EXACTO aparezca en la lista "EQUIPOS DISPONIBLES EN LA SEDE"** — si no está en esa lista, esa sede no lo tiene, no lo inventes.
10. **CAMPOS OBLIGATORIOS:** `semana` = `1`, `diaSemana` de 1 al {dias_por_semana}, y `orden` correlativo por día.
11. **AUTOVERIFICACIÓN ANTES DE RESPONDER (obligatoria):** Por cada día que tenga equipos asignados en el "PLAN DE DIVISIÓN MUSCULAR POR DÍA", cuenta cuántos ejercicios de ese día tienen `equipoRequerido` = "Peso corporal". Si hay más de 1, reemplaza los excedentes por ejercicios que usen los equipos reales de la sede ANTES de generar la respuesta final. Verifica también que ningún `equipoRequerido` sea "Mancuernas"/"Barra" a menos que estén literalmente en la lista de equipos, y que ningún día tenga menos de 5 ni más de 7 ejercicios.
12. **EXPLICACIÓN FINAL AMIGABLE (`explicacionIA`):** Escríbela dirigida directamente al socio, en tono cercano, cálido y motivador — como un entrenador que lo conoce, no como un informe técnico. Llámalo por su nombre, menciona brevemente su objetivo principal y, si tiene lesiones o condiciones médicas relevantes, comenta en una frase cómo se tuvieron en cuenta al armar la rutina. Máximo 3-4 frases (sé breve para no gastar tokens), pero que se sienta personal y no genérico.

RESPONDE SOLO CON JSON VÁLIDO. SIN MARKDOWN. SIN ```json. SIN TEXTO ADICIONAL.

EL JSON DEBE TENER EXACTAMENTE ESTA ESTRUCTURA. El ejemplo de "detalles" muestra la PROPORCIÓN esperada
(equipo real de la sede en casi todos, máximo 1 de peso corporal como complemento) — no copies los nombres,
usa el equipo REAL de la lista de equipos y los ejercicios reales que generes para cada día. El ejemplo de
"explicacionIA" muestra el TONO esperado (cercano, con el nombre del socio) — no copies el texto literal,
escribe uno nuevo con los datos reales de este socio:
{{
    "nombre": "Rutina personalizada de 1 semana",
    "descripcion": "Rutina enfocada en {contexto.get('objetivoPrincipal', 'fitness')} con {dias_por_semana} días de entrenamiento.",
    "explicacionIA": "{ejemplo_explicacion}",
    "detalles": [
        {{
            "semana": 1,
            "diaSemana": 1,
            "orden": 1,
            "nombreEjercicio": "Ejercicio con equipo real de la sede, ej. usando '{ejemplo_equipo_1}'",
            "grupoMuscular": "PIERNA",
            "series": 4,
            "repeticionesMin": 8,
            "repeticionesMax": 12,
            "pesoSugerido": 20.0,
            "descansoSegundos": 60,
            "notas": "Mantener la espalda recta.",
            "equipoRequerido": "{ejemplo_equipo_1}"
        }},
        {{
            "semana": 1,
            "diaSemana": 1,
            "orden": 2,
            "nombreEjercicio": "Otro ejercicio con equipo real de la sede, ej. usando '{ejemplo_equipo_2}'",
            "grupoMuscular": "PIERNA",
            "series": 4,
            "repeticionesMin": 8,
            "repeticionesMax": 12,
            "pesoSugerido": 15.0,
            "descansoSegundos": 60,
            "notas": "Controlar el descenso.",
            "equipoRequerido": "{ejemplo_equipo_2}"
        }},
        {{
            "semana": 1,
            "diaSemana": 1,
            "orden": 3,
            "nombreEjercicio": "Ejercicio complementario de peso corporal (máximo 1 por día si el día tiene equipos)",
            "grupoMuscular": "PIERNA",
            "series": 3,
            "repeticionesMin": 10,
            "repeticionesMax": 15,
            "pesoSugerido": 0.0,
            "descansoSegundos": 45,
            "notas": "Ejemplo de complemento sin equipo.",
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