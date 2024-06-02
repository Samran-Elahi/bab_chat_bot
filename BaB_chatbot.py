from imports import *
from utils import Utility
from constants import Const
from celery_worker import call_periodic_task

load_dotenv()

app = FastAPI()

@app.post("/save-all-products")
async def save_all_products():
    return Utility.hit_all_product_api()

@app.post("/list-mentioned-products")
async def list_mentioned_products(id=None, category=None):
    return Utility.hit_product_API(Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, Const.LANG, Const.PRODUCT_API, id, category)

@app.post("/list-categories")
async def call_external_api():
    """Endpoint to call the external category API.

    Args:
        request: The request body containing deviceId, email, password, securityCode, and langId.

    Returns:
        The response from the category API.
    """
    result = Utility.hit_category_API(
       Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, Const.LANG, Const.CATEGORY_API
    )
    Utility.save_response_to_file(result, 'category_responses.json')
    return result

@app.get("/search_category")
async def search_category_name(category_name: str):
    """Endpoint to search for a category by name.

    Args:
        category_name: The name of the category to search for.

    Returns:
        The found category item, or raises a 404 HTTPException if not found.
    """
    for response in Utility.responses:
        if 'data' in response:
            found_item = Utility.find_category(response['data'], category_name)
            if found_item:
                return found_item
    raise HTTPException(status_code=404, detail="Category not found")

@app.get("/all_category_names")
async def get_all_category_names():
    """Endpoint to retrieve all category names.

    Returns:
        A list of all category names extracted from the stored responses.
    """
    Utility.category_names.clear()
    for response in Utility.responses:
        if 'data' in response:
            Utility.extract_category_names(response['data'])
    return Utility.category_names

@app.post("/send_chat")
async def chat_query(query: str):
    """Endpoint to process a chat query using the conversation chain.

    Args:
        query: The chat query string.

    Returns:
        The response from the conversation chain.
    """
    result = main_conversation({"question": query})
    return result.get('answer')

if __name__ == "__main__":
    main_conversation = Utility.get_conversation_chain(Utility.get_vectorstore())
    uvicorn.run(app, host="0.0.0.0", port=3000)
