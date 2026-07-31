import os

# Decoupled model configurations for 12-factor compliance
LLM_MODEL = os.getenv("HEALTHCARE_LLM_MODEL", "llama3")
EMBEDDING_MODEL = os.getenv("HEALTHCARE_EMBEDDING_MODEL", "nomic-embed-text")
