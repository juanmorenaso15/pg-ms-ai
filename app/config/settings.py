import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuración del servicio de IA"""
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("MAX_OUTPUT_TOKENS", "4096"))
    TOP_P: float = float(os.getenv("TOP_P", "0.95"))

settings = Settings()

if not settings.GROQ_API_KEY:
    print("ADVERTENCIA: GROQ_API_KEY no configurada en el archivo .env")
    print("El servicio funcionará en MODO SIMULACIÓN")
else:
    print(f"Groq configurado con modelo: {settings.MODEL_NAME}")