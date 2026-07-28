import logging
from typing import Dict, Any
from groq import Groq

from app.services.prompt_builder import build_prompt, build_prompt_nutricional
from app.config.settings import settings
from app.services.prompt_builder import build_prompt
from app.services.parser import parse_response

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.MODEL_NAME or "llama-3.3-70b-versatile"
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info(f"Groq configurado correctamente con el modelo: {self.model_name}")
            except Exception as e:
                logger.error(f"Error al configurar el cliente de Groq: {e}")
                self.client = None
        else:
            logger.warning("GROQ_API_KEY no configurada. Usando MODO SIMULACIÓN.")
            self.client = None
    
    def generar_rutina(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key or not self.client:
            logger.info("Usando MODO SIMULACIÓN para generar rutina")
            return self._generar_rutina_simulada(contexto)
        
        try:
            prompt = build_prompt(contexto)
            logger.info(f"Enviando prompt a Groq (tamaño: {len(prompt)} caracteres)")
            logger.info(f"Datos del socio: {contexto.get('nombre')} ({contexto.get('edad')} años)")
            logger.info(f"Ejercicios disponibles: {len(contexto.get('ejerciciosDisponibles', []))}")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_OUTPUT_TOKENS,
                top_p=settings.TOP_P,
                response_format={"type": "json_object"} 
            )
            
            respuesta_texto = chat_completion.choices[0].message.content
            logger.info(f"Respuesta recibida de Groq (tamaño: {len(respuesta_texto)} caracteres)")
            
            print(f"\n{'='*60}")
            print(f"RESPUESTA COMPLETA DE GROQ:")
            print(f"{'='*60}")
            print(respuesta_texto[:1500])
            if len(respuesta_texto) > 1500:
                print(f"... (truncado, total: {len(respuesta_texto)} caracteres)")
            print(f"{'='*60}\n")
            
            resultado = parse_response(respuesta_texto)
            
            if resultado.get("detalles") and len(resultado.get("detalles", [])) > 0:
                logger.info(f"Rutina parseada correctamente: {resultado.get('nombre')}")
                logger.info(f"Detalles generados: {len(resultado.get('detalles', []))}")
                return resultado
            else:
                if resultado.get("dias") and len(resultado.get("dias", [])) > 0:
                    logger.info("Transformando 'dias' a 'detalles' en groq_service")
                    detalles = []
                    for dia in resultado.get("dias", []):
                        for ejercicio in dia.get("ejercicios", []):
                            detalle = {
                                "diaSemana": dia.get("dia", 1),
                                "orden": ejercicio.get("orden", len(detalles) + 1),
                                "nombreEjercicio": ejercicio.get("nombre_ejercicio", ""),
                                "series": ejercicio.get("series", 3),
                                "repeticionesMin": ejercicio.get("repeticiones_min"),
                                "repeticionesMax": ejercicio.get("repeticiones_max"),
                                "pesoSugerido": ejercicio.get("peso_sugerido"),
                                "descansoSegundos": ejercicio.get("descanso_segundos", 60),
                                "notas": ejercicio.get("notas", "")
                            }
                            detalles.append(detalle)
                    
                    resultado["detalles"] = detalles
                    if "dias" in resultado:
                        del resultado["dias"]
                    logger.info(f"Transformados {len(detalles)} ejercicios a 'detalles'")
                    return resultado
                
                logger.warning("La respuesta no tiene ejercicios estructurados de forma válida. Usando simulación.")
                return self._generar_rutina_simulada(contexto)
            
        except Exception as e:
            logger.error(f"Error al llamar a Groq: {str(e)}")
            return self._generar_rutina_simulada(contexto)
    
    def _generar_rutina_simulada(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        dias = contexto.get('diasPorSemana', 3)
        nombre = contexto.get('nombre', 'Socio')
        objetivo = contexto.get('objetivoPrincipal', 'mejorar condición física')
        
        ejercicios = [
            {"nombre": "Sentadillas con peso corporal", "grupo": "PIERNAS"},
            {"nombre": "Flexiones de brazos", "grupo": "PECHO"},
            {"nombre": "Dominadas asistidas", "grupo": "ESPALDA"},
            {"nombre": "Plancha", "grupo": "CORE"},
            {"nombre": "Prensa de hombros con mancuernas", "grupo": "HOMBROS"},
            {"nombre": "Curl de bíceps con mancuernas", "grupo": "BRAZOS"},
            {"nombre": "Caminata en cinta", "grupo": "CARDIO"},
            {"nombre": "Peso muerto", "grupo": "ESPALDA"},
            {"nombre": "Zancadas", "grupo": "PIERNAS"},
            {"nombre": "Remo con barra", "grupo": "ESPALDA"},
        ]
        
        dias_rutina = []
        nombres_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        for i in range(min(dias, len(nombres_dias))):
            ejercicios_dia = []
            start_idx = (i * 3) % len(ejercicios)
            
            for j in range(3):
                idx = (start_idx + j) % len(ejercicios)
                ej = ejercicios[idx]
                ejercicios_dia.append({
                    "nombre_ejercicio": ej["nombre"],
                    "series": 3 + (i % 2),
                    "repeticiones_min": 8 if i < 2 else 10,
                    "repeticiones_max": 12 if i < 2 else 15,
                    "peso_sugerido": 0.0,
                    "descanso_segundos": 60,
                    "notas": f"Ejercicio para {ej['grupo']}. [MODO SIMULACIÓN]"
                })
            
            dias_rutina.append({
                "dia": i + 1,
                "nombre_dia": nombres_dias[i],
                "ejercicios": ejercicios_dia
            })
        
        if contexto.get('incluirCardio', True) and dias_rutina:
            cardio_ejercicio = {
                "nombre_ejercicio": "Cardio - Caminata/Trote",
                "series": 1,
                "repeticiones_min": 20,
                "repeticiones_max": 30,
                "peso_sugerido": 0.0,
                "descanso_segundos": 0,
                "notes": "Cardio al final del entrenamiento [MODO SIMULACIÓN]"
            }
            dias_rutina[-1]["ejercicios"].append(cardio_ejercicio)
        
        return {
            "nombre": f"Rutina de {objetivo} para {nombre}",
            "descripcion": f"Rutina personalizada de {dias} días para {objetivo}",
            "explicacion_ia": "[MODO SIMULACIÓN] Verifica tu conexión o credenciales de la API de Groq para habilitar el motor real.",
            "detalles": []
        }
    
    def generar_plan_nutricional(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un plan nutricional personalizado"""
        
        if not self.api_key or not self.client:
            logger.info("Usando MODO SIMULACIÓN para plan nutricional")
            return self._generar_plan_nutricional_simulado(contexto)
        
        try:
            prompt = build_prompt_nutricional(contexto)
            logger.info(f"Enviando prompt a Groq para nutrición (tamaño: {len(prompt)} caracteres)")
            
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_OUTPUT_TOKENS,
                top_p=settings.TOP_P,
                response_format={"type": "json_object"}
            )
            
            respuesta_texto = chat_completion.choices[0].message.content
            logger.info(f"Respuesta recibida de Groq (tamaño: {len(respuesta_texto)} caracteres)")
            
            print(f"\n{'='*60}")
            print(f"RESPUESTA PLAN NUTRICIONAL:")
            print(f"{'='*60}")
            print(respuesta_texto[:1500])
            if len(respuesta_texto) > 1500:
                print(f"... (truncado, total: {len(respuesta_texto)} caracteres)")
            print(f"{'='*60}\n")
            
            resultado = parse_response(respuesta_texto)
            
            if resultado.get("calorias_diarias") and resultado.get("sugerencias_comidas"):
                logger.info(f"Plan nutricional generado: {resultado.get('calorias_diarias')} calorías")
                return resultado
            else:
                logger.warning("La respuesta no tiene la estructura esperada. Usando simulación.")
                return self._generar_plan_nutricional_simulado(contexto)
            
        except Exception as e:
            logger.error(f"Error en plan nutricional: {str(e)}")
            return self._generar_plan_nutricional_simulado(contexto)

    def _generar_plan_nutricional_simulado(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Plan nutricional simulado"""
        nombre = contexto.get('nombre', 'Socio')
        objetivo = contexto.get('objetivoEspecifico', 'Mantener peso')
        
        return {
            "calorias_diarias": 2200,
            "proteinas_g": 150.0,
            "carbohidratos_g": 250.0,
            "grasas_g": 70.0,
            "restricciones_dieteticas": contexto.get('restriccionesDieteticas', []),
            "sugerencias_comidas": {
                "desayuno": [
                    {"nombre": "Avena con frutas y nueces", "calorias": 350, "proteinas": 10, "carbohidratos": 50, "grasas": 8}
                ],
                "almuerzo": [
                    {"nombre": "Pollo a la plancha con arroz integral", "calorias": 600, "proteinas": 40, "carbohidratos": 70, "grasas": 15}
                ],
                "cena": [
                    {"nombre": "Pescado con verduras al vapor", "calorias": 500, "proteinas": 35, "carbohidratos": 30, "grasas": 20}
                ],
                "colaciones": [
                    {"nombre": "Yogur con granola", "calorias": 200, "proteinas": 12, "carbohidratos": 25, "grasas": 5}
                ]
            },
            "explicacion_ia": f"[MODO SIMULACIÓN] Plan nutricional básico para {nombre} con objetivo: {objetivo}. Conecta la IA para planes personalizados."
        }

