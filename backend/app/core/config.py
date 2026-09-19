import os

class Settings:
    PROJECT_NAME: str = "EkMat"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database configuration
    # Can be postgresql+psycopg2://postgres:postgres@localhost:5432/ekmat or sqlite:///./ekmat.db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ekmat.db")
    
    # AI/ML Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Weight formula: 0.50 semantic + 0.30 fuzzy + 0.20 attribute
    WEIGHT_SEMANTIC: float = 0.50
    WEIGHT_FUZZY: float = 0.30
    WEIGHT_ATTRIBUTE: float = 0.20
    
    # Confidence routing
    THRESHOLD_HIGH: float = 0.90
    THRESHOLD_MEDIUM: float = 0.60

settings = Settings()
