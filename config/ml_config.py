import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MLConfig:
    # Cross-platform paths using your existing structure
    BASE_DIR = Path(__file__).parent.parent
    MODELS_DIR = BASE_DIR / "trained_models" 
    DATASETS_DIR = BASE_DIR / "datasets"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Ensure directories exist
    for dir_path in [MODELS_DIR, DATASETS_DIR, LOGS_DIR]:
        dir_path.mkdir(exist_ok=True)
    
    # Model configurations
    BERT_MODEL = os.getenv("BERT_MODEL", "bert-base-uncased")
    MAX_SEQUENCE_LENGTH = int(os.getenv("MAX_SEQUENCE_LENGTH", "512"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "16"))
    
    # Use your existing database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///aptitude_exam.db")
    
    # Difficulty mapping
    DIFFICULTY_LABELS = {'Easy': 0, 'Medium': 1, 'Hard': 2}
