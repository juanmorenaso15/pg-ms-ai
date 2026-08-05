import json
import re
from typing import Dict, Any

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
        return data
    
    if "detalles" in data and data["detalles"]:
        print(f"JSON ya tiene 'detalles' con {len(data['detalles'])} ejercicios")
        return data
    
    if "dias" in data and data["dias"]:
        print("Transformando 'dias' a 'detalles'")
        data["detalles"] = []
        for dia in data.get("dias", []):
            for ejercicio in dia.get("ejercicios", []):
                detalle = {
                    "diaSemana": dia.get("dia", 1),
                    "orden": ejercicio.get("orden", len(data["detalles"]) + 1),
                    "nombreEjercicio": ejercicio.get("nombre_ejercicio", ""),
                    "series": ejercicio.get("series", 3),
                    "repeticionesMin": ejercicio.get("repeticiones_min"),
                    "repeticionesMax": ejercicio.get("repeticiones_max"),
                    "pesoSugerido": ejercicio.get("peso_sugerido"),
                    "descansoSegundos": ejercicio.get("descanso_segundos", 60),
                    "notas": ejercicio.get("notas", "")
                }
                data["detalles"].append(detalle)
        
        del data["dias"]
        print(f"Transformados {len(data['detalles'])} ejercicios a 'detalles'")
        return data
    
    if "ejercicios" in data and data["ejercicios"]:
        print("Convirtiendo 'ejercicios' directamente a 'detalles'")
        data["detalles"] = []
        for ejercicio in data.get("ejercicios", []):
            detalle = {
                "diaSemana": 1,
                "orden": ejercicio.get("orden", len(data["detalles"]) + 1),
                "nombreEjercicio": ejercicio.get("nombre", ejercicio.get("nombre_ejercicio", "")),
                "series": ejercicio.get("series", 3),
                "repeticionesMin": ejercicio.get("repeticiones_min"),
                "repeticionesMax": ejercicio.get("repeticiones_max"),
                "pesoSugerido": ejercicio.get("peso_sugerido"),
                "descansoSegundos": ejercicio.get("descanso_segundos", 60),
                "notas": ejercicio.get("notas", "")
            }
            data["detalles"].append(detalle)
        
        del data["ejercicios"]
        print(f"Convertidos {len(data['detalles'])} ejercicios a 'detalles'")
        return data
    
    print("No se encontraron ni ejercicios ni plan nutricional en la respuesta")
    return data


def _respuesta_por_defecto(motivo: str) -> Dict[str, Any]:
    """Retorna una respuesta por defecto cuando el parsing falla"""
    return {
        "nombre": "Rutina Personalizada",
        "descripcion": "Rutina generada automáticamente",
        "explicacionIA": f"No se pudo parsear la respuesta. Motivo: {motivo}",
        "detalles": []
    }