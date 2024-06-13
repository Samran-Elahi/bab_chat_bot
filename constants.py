from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()
@dataclass(frozen=True)
class Const:
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    QDRANT_URL: str = os.getenv('QDRANT_URL')
    QDRANT_API_KEY: str = os.getenv('QDRANT_API_KEY')
    ENGLISH_COLLECTION_NAME: str = 'english_final_combine_category_and_products'
    ARABIC_COLLECTION_NAME: str = 'arabic_final_combine_category_and_products'
    DEVICE_ID: str = os.getenv('DEVICE_ID')
    EMAIL: str = os.getenv('EMAIL')
    PASSWORD: str = os.getenv('PASSWORD')
    SECURITY_CODE: str = os.getenv('SECURITY_CODE')
    CATEGORY_API: str = os.getenv('CATEGORY_API')
    PRODUCT_API: str = os.getenv('PRODUCT_API')
    TOGETHER_API_KEY: str = os.getenv('TOGETHER_API_KEY')
    TOGETHER_BASE_URL: str = os.getenv('TOGETHER_BASE_URL')
    ENGLISH_PRODUCTNAME_COLLECTION_NAME: str = 'english_product_names'
    ARABIC_PRODUCTNAME_COLLECTION_NAME: str = 'arabic_product_names'


