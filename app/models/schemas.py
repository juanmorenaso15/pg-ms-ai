from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class DetalleEjercicioRequest(BaseModel):
    """Modelo para un ejercicio dentro de la rutina"""
    nombre_ejercicio: str
    series: int = 3
    repeticiones_min: Optional[int] = None
    repeticiones_max: Optional[int] = None
    peso_sugerido: Optional[float] = None
    descanso_segundos: Optional[int] = 60
    notas: Optional[str] = None

class DiaRutinaRequest(BaseModel):
    """Modelo para un día de entrenamiento"""
    dia: int
    nombre_dia: str
    ejercicios: List[DetalleEjercicioRequest]

class RutinaGeneracionRequest(BaseModel):
    """Request para generar una rutina"""
    id_socio: int
    dias_por_semana: int = 3
    duracion_semanas: int = 4
    preferencias_equipamiento: Optional[List[str]] = None
    evitar_ejercicios: Optional[List[str]] = None
    preferencias_grupos_musculares: Optional[List[str]] = None
    objetivo_especifico: Optional[str] = None
    incluir_cardio: bool = True

class RutinaGeneracionResponse(BaseModel):
    """Response con la rutina generada"""
    nombre: str
    descripcion: str
    explicacion_ia: str
    dias: List[DiaRutinaRequest]

class PlanNutricionalGeneracionRequest(BaseModel):
    id_socio: int
    restricciones_dieteticas: Optional[List[str]] = None
    alergias: Optional[List[str]] = None
    intolerancias: Optional[List[str]] = None
    objetivo_especifico: Optional[str] = None

class SugerenciaComida(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    calorias: float
    proteinas: Optional[float] = None
    carbohidratos: Optional[float] = None
    grasas: Optional[float] = None
    ingredientes: Optional[str] = None
    preparacion: Optional[str] = None

class PlanNutricionalGeneracionResponse(BaseModel):
    calorias_diarias: int
    proteinas_g: float
    carbohidratos_g: float
    grasas_g: float
    restricciones_dieteticas: Optional[List[str]] = None
    sugerencias_comidas: Dict[str, List[SugerenciaComida]]
    explicacion_ia: str