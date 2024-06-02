from dataclasses import dataclass
import os
@dataclass(frozen=True)
class Const:
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    QDRANT_URL: str = "https://e3bb5356-ec8a-46af-8af9-55905fcf50b4.us-east4-0.gcp.cloud.qdrant.io:6333/dashboard"
    QDRANT_API_KEY: str = "MdMc-TBQx2r3AXHw9qYlY61orvcwP6r__92nfrJauRC8q4JTrFSntg"
    COLLECTION_NAME: str = "final_combine_category_and_products"
    DEVICE_ID: str = '068b2b2a69357d7e36ce64f15819904c861a91540ff7ca52c9e33589c491db53'
    EMAIL: str = 'gameazy2018@gmail.com'
    PASSWORD: str = 'Gameazy@102030'
    SECURITY_CODE: str = 'f0ca85b01945cade674530b6567e23d2c9656a5dc8afe05a29b7f5637ac2239c'
    CATEGORY_API: str = "https://proxy-main-fxudoqoheq-ww.a.run.app/online/categories"
    PRODUCT_API: str = "https://proxy-main-fxudoqoheq-ww.a.run.app/online/products/"
    LANG: int = 1

