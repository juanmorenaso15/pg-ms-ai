import json
import re
from typing import Dict, Any, List

def parse_response(respuesta: str) -> Dict[str, Any]:
    """
    Parsea la respuesta de Groq y la convierte a un diccionario.
    Maneja rutinas (con "dias"/"detalles") y planes nutricionales (con "calorias_diarias").
    """
    
    if not respuesta:
        return _respuesta_por_defecto("Respuesta vacía")
    
    respuesta = respuesta.strip()
    print(f"Respuesta original (primeros 200 chars): {respuesta[:200]}...")
    
    cleaned = re.sub(r'```json\s*', '', respuesta)
    cleaned = re.sub(r'```\s*', '', cleaned)
    cleaned = cleaned.strip()
    
    if cleaned != respuesta:
        print("Limpiado markdown")
        try:
            return _procesar_json(json.loads(cleaned))
        except json.JSONDecodeError:
            pass
    
    json_block_pattern = r'```json\s*([\s\S]*?)```'
    match = re.search(json_block_pattern, respuesta)
    
    if match:
        json_str = match.group(1).strip()
        print("JSON extraído de bloque markdown")
        try:
            return _procesar_json(json.loads(json_str))
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON del bloque: {e}")
    
    json_pattern = r'\{[\s\S]*\}'
    match = re.search(json_pattern, respuesta)
    
    if match:
        json_str = match.group()
        print("JSON extraído del texto")
        try:
            return _procesar_json(json.loads(json_str))
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
    
    try:
        print("Intentando parsear directamente")
        return _procesar_json(json.loads(respuesta))
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON: {e}")
        print(f"Respuesta problemática: {respuesta[:300]}...")
        return _respuesta_por_defecto(f"Error al parsear JSON: {str(e)}")


def _procesar_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa el JSON parseado.
    Detecta si es plan nutricional (tiene calorias_diarias) o rutina (tiene detalles/dias).
    """
    
    if "calorias_diarias" in data or "caloriasDiarias" in data:
        print("Plan nutricional detectado")
        
        if "caloriasDiarias" in data and "calorias_diarias" not in data:
            data["calorias_diarias"] = data["caloriasDiarias"]
            del data["caloriasDiarias"]
        if "proteinasG" in data and "proteinas_g" not in data:
            data["proteinas_g"] = data["proteinasG"]
            del data["proteinasG"]
        if "carbohidratosG" in data and "carbohidratos_g" not in data:
            data["carbohidratos_g"] = data["carbohidratosG"]
            del data["carbohidratosG"]
        if "grasasG" in data and "grasas_g" not in data:
            data["grasas_g"] = data["grasasG"]
            del data["grasasG"]
        if "explicacionIA" in data and "explicacion_ia" not in data:
            data["explicacion_ia"] = data["explicacionIA"]
            del data["explicacionIA"]
        if "sugerenciasComidas" in data and "sugerencias_comidas" not in data:
            data["sugerencias_comidas"] = data["sugerenciasComidas"]
            del data["sugerenciasComidas"]
        
        data = _procesar_plan_nutricional(data)
        
        return data
    
    if "detalles" in data and data["detalles"]:
        print(f"JSON ya tiene 'detalles' con {len(data['detalles'])} ejercicios")
        
        for idx, detalle in enumerate(data["detalles"]):
            if "equipoRequerido" not in detalle or detalle["equipoRequerido"] is None:
                detalle["equipoRequerido"] = "Sin equipo específico"
            
            if "grupoMuscular" not in detalle or detalle["grupoMuscular"] is None:
                detalle["grupoMuscular"] = detalle.get("grupo_muscular", "GENERAL")
            if not detalle["grupoMuscular"]:
                detalle["grupoMuscular"] = "GENERAL"
            
            dia_actual = detalle.get("diaSemana", 1)
            if dia_actual is None:
                detalle["diaSemana"] = 1
                
            detalle["semana"] = 1
                
        return data
    
    if "dias" in data and data["dias"]:
        print("Transformando 'dias' a 'detalles'")
        data["detalles"] = []
        for dia in data.get("dias", []):
            for ejercicio in dia.get("ejercicios", []):
                detalle = {
                    "semana": 1,
                    "diaSemana": dia.get("dia", 1),
                    "orden": ejercicio.get("orden", len(data["detalles"]) + 1),
                    "nombreEjercicio": ejercicio.get("nombre_ejercicio", ejercicio.get("nombreEjercicio", "")),
                    "grupoMuscular": ejercicio.get("grupoMuscular", ejercicio.get("grupo_muscular", "GENERAL")),
                    "series": ejercicio.get("series", 3),
                    "repeticionesMin": ejercicio.get("repeticiones_min", ejercicio.get("repeticionesMin")),
                    "repeticionesMax": ejercicio.get("repeticiones_max", ejercicio.get("repeticionesMax")),
                    "pesoSugerido": ejercicio.get("peso_sugerido", ejercicio.get("pesoSugerido")),
                    "descansoSegundos": ejercicio.get("descanso_segundos", ejercicio.get("descansoSegundos", 60)),
                    "notas": ejercicio.get("notas", ""),
                    "equipoRequerido": ejercicio.get("equipo_requerido", ejercicio.get("equipoRequerido", "Sin equipo específico"))
                }
                data["detalles"].append(detalle)
        
        if "dias" in data:
            del data["dias"]
        print(f"Transformados {len(data['detalles'])} ejercicios a 'detalles'")
        return data
    
    if "ejercicios" in data and data["ejercicios"]:
        print("Convirtiendo 'ejercicios' directamente a 'detalles'")
        data["detalles"] = []
        for ejercicio in data.get("ejercicios", []):
            detalle = {
                "semana": 1,
                "diaSemana": 1,
                "orden": ejercicio.get("orden", len(data["detalles"]) + 1),
                "nombreEjercicio": ejercicio.get("nombre", ejercicio.get("nombre_ejercicio", "")),
                "grupoMuscular": ejercicio.get("grupoMuscular", ejercicio.get("grupo_muscular", "GENERAL")),
                "series": ejercicio.get("series", 3),
                "repeticionesMin": ejercicio.get("repeticiones_min", ejercicio.get("repeticionesMin")),
                "repeticionesMax": ejercicio.get("repeticiones_max", ejercicio.get("repeticionesMax")),
                "pesoSugerido": ejercicio.get("peso_sugerido", ejercicio.get("pesoSugerido")),
                "descansoSegundos": ejercicio.get("descanso_segundos", ejercicio.get("descansoSegundos", 60)),
                "notas": ejercicio.get("notas", ""),
                "equipoRequerido": ejercicio.get("equipo_requerido", ejercicio.get("equipoRequerido", "Sin equipo específico"))
            }
            data["detalles"].append(detalle)
        
        if "ejercicios" in data:
            del data["ejercicios"]
        print(f"Convertidos {len(data['detalles'])} ejercicios a 'detalles'")
        return data
    
    print("No se encontraron ni ejercicios ni plan nutricional en la respuesta")
    return data


def _procesar_plan_nutricional(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa y valida un plan nutricional, asegurando que todos los campos tengan valor.
    """
    
    if "restricciones_dieteticas" not in data or data["restricciones_dieteticas"] is None:
        data["restricciones_dieteticas"] = []
    
    if "explicacion_ia" not in data or data["explicacion_ia"] is None:
        data["explicacion_ia"] = "Plan nutricional personalizado adaptado a las necesidades del socio."
    
    if "sugerencias_comidas" in data and data["sugerencias_comidas"]:
        for comida, items in data["sugerencias_comidas"].items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        if "descripcion" not in item or item["descripcion"] is None or item["descripcion"] == "":
                            item["descripcion"] = f"{item.get('nombre', 'Plato')} - Opción nutritiva y balanceada"
                        
                        if "ingredientes" not in item or item["ingredientes"] is None or item["ingredientes"] == "":
                            item["ingredientes"] = "Ingredientes frescos y saludables"
                        
                        if "preparacion" not in item or item["preparacion"] is None or item["preparacion"] == "":
                            item["preparacion"] = "Preparar los ingredientes, cocinar al gusto y servir"
    else:
        data["sugerencias_comidas"] = {
            "desayuno": [
                {
                    "nombre": "Avena con frutas",
                    "descripcion": "Desayuno energético rico en fibra y nutrientes",
                    "ingredientes": "Avena, leche, plátano, fresas",
                    "preparacion": "Cocinar la avena con leche y añadir frutas picadas",
                    "calorias": 350,
                    "proteinas": 10.0,
                    "carbohidratos": 50.0,
                    "grasas": 8.0
                }
            ],
            "almuerzo": [
                {
                    "nombre": "Pollo con verduras",
                    "descripcion": "Almuerzo completo con proteínas y vegetales",
                    "ingredientes": "Pechuga de pollo, brócoli, zanahoria, aceite de oliva",
                    "preparacion": "Cocinar el pollo a la plancha y saltear las verduras",
                    "calorias": 500,
                    "proteinas": 35.0,
                    "carbohidratos": 30.0,
                    "grasas": 15.0
                }
            ],
            "cena": [
                {
                    "nombre": "Pescado con espárragos",
                    "descripcion": "Cena ligera rica en omega-3",
                    "ingredientes": "Salmón, espárragos, limón",
                    "preparacion": "Hornear el salmón con espárragos a 180°C por 20 minutos",
                    "calorias": 400,
                    "proteinas": 30.0,
                    "carbohidratos": 10.0,
                    "grasas": 20.0
                }
            ],
            "colaciones": [
                {
                    "nombre": "Batido de proteínas",
                    "descripcion": "Colación para recuperación muscular",
                    "ingredientes": "Leche, proteína, plátano",
                    "preparacion": "Licuar todos los ingredientes",
                    "calorias": 200,
                    "proteinas": 20.0,
                    "carbohidratos": 25.0,
                    "grasas": 5.0
                }
            ]
        }
    
    print(f"Plan nutricional procesado: {data.get('calorias_diarias')} calorías, {len(data.get('sugerencias_comidas', {}))} categorías de comidas")
    return data


def _respuesta_por_defecto(motivo: str) -> Dict[str, Any]:
    """Retorna una respuesta por defecto cuando el parsing falla"""
    return {
        "nombre": "Rutina Personalizada",
        "descripcion": "Rutina generada automáticamente",
        "explicacionIA": f"No se pudo parsear la respuesta. Motivo: {motivo}",
        "detalles": []
    }