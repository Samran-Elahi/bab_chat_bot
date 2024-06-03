from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Const:
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    QDRANT_URL: str = os.getenv('QDRANT_URL')
    QDRANT_API_KEY: str = os.getenv('QDRANT_API_KEY')
    COLLECTION_NAME: str = os.getenv('COLLECTION_NAME')
    DEVICE_ID: str = os.getenv('DEVICE_ID')
    EMAIL: str = os.getenv('EMAIL')
    PASSWORD: str = os.getenv('PASSWORD')
    SECURITY_CODE: str = os.getenv('SECURITY_CODE')
    CATEGORY_API: str = os.getenv('CATEGORY_API')
    PRODUCT_API: str = os.getenv('PRODUCT_API')
    LANG: int = 1


