from imports import *
from utils import Utility
from constants import Const
from celery_worker import call_periodic_task

load_dotenv()

app = FastAPI()

@app.post("/save-all-products")
async def save_all_products(langId):
    return Utility.hit_all_product_api(langId)

@app.post("/list-mentioned-products")
async def list_mentioned_products(langId, id=None, category=None):
    return Utility.hit_product_API(Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, langId, Const.PRODUCT_API, id, category)
    

@app.post("/list-categories")
async def call_external_api(langId):
    """Endpoint to call the external category API.

    Args:
        request: The request body containing deviceId, email, password, securityCode, and langId.

    Returns:
        The response from the category API.
    """
    result = Utility.hit_category_API(
       Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, langId, Const.CATEGORY_API
    )

    if langId == '2':
        Utility.save_response_to_file(result, 'arabic_category_responses.json')
    else:
        Utility.save_response_to_file(result, 'english_category_responses.json')
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


@app.get("/all-product-names")
async def get_allproduct_names(langId):
    if langId == '1':
        return Utility.extract_product_names('english_product_responses.json')
    else:
        return Utility.extract_product_names('arabic_product_responses.json')

@app.get("/productId-by-productName")
async def get_productId_by_productNames(langId, productName):
    if langId == '1':
        return Utility.get_product_id_by_name('english_product_responses.json', productName)
    else:
        return Utility.get_product_id_by_name('arabic_product_responses.json', productName)

@app.post("/send_chat")
async def chat_query(query: str, langId, new_vectorstore: bool=False):
    """Endpoint to process a chat query using the conversation chain.

    Args:
        query: The chat query string.

    Returns:
        The response from the conversation chain.
    """
    llm = ChatOpenAI(model_name="gpt-4")
    
    combine_vectorstore = Utility.get_vectorstore(langId, new_vectorstore)[0]
    productName_vectorstore = Utility.get_vectorstore(langId, new_vectorstore)[1]
    
    main_conversation = Utility.get_conversation_chain(combine_vectorstore, llm = ChatOpenAI(max_tokens=500))
    product_conversation = Utility.get_conversation_chain(productName_vectorstore, llm = ChatOpenAI(model_name="gpt-4" , max_tokens=500))
    
    if langId == '2':
        prompt = f"""You are an Arabic chatbot which replies any query in Arabic Language. Here is the query which you need to answer based on the context you have, Query: {query}"""
        result = main_conversation({"question": prompt})
    else:
        result = main_conversation({"question": query})
        
        product_prompt = f"""
        Response: {result.get('answer')}
        
        Return all the product names that have been identified from the above response and matched the list of product names semantically.
        Format your response with 'START_PRODUCT_NAMES' before listing the product names and 'END_PRODUCT_NAMES' after the list.
        Example response format:
        START_PRODUCT_NAMES
        Product Name 1, Product Name 2, Product Name 3
        END_PRODUCT_NAMES

        The structured format will assist in the direct mapping and extraction of Product Names for subsequent processing steps.
    """

        product_result = product_conversation({"question": product_prompt})
        productNames = Utility.get_product_name(product_result.get('answer'))
        
    classification_prompt = f"""
        Classify the response into one of the following categories using a single designated word:

        - "media" if the response contains any type of image URL.
        - "catalogue" if the response lists multiple product names.
        - "single product" if it contains details of a single product name.
        - "simple text" if it does not involve any product name from the provided list.

        Product names to consider: {productNames}

        Response: {result.get('answer')}
        """

    answer = llm.invoke(classification_prompt)
    
    classification_tokens = Utility.get_tokens(answer.content+classification_prompt)
    response_tokens = Utility.get_tokens(result.get('answer')+query)
    product_tokens = Utility.get_tokens(product_result.get('answer')+product_prompt)
    total_tokens = classification_tokens + response_tokens + product_tokens
    
    product_id = []

    for product_name in productNames:
        id_by_productName = Utility.get_product_id_by_name('english_product_responses.json', product_name)
        product_id.append(id_by_productName)
    print(productNames)
    
    if 'single product' in answer.content:
        return {'WhatsApp Structure': Utility.create_json_structure(answer.content, body_text=result.get('answer'), text=None, product_ids=product_id[0]), 'tokens':total_tokens}
    
    elif 'catalogue' in answer.content :
        return  {'WhatsApp Structure': Utility.create_json_structure(answer.content, body_text=result.get('answer'), text=None, product_ids=product_id), 'tokens':total_tokens}
    
    elif 'media' in answer.content:
        image_urls = Utility.extract_urls(result.get('answer'))
        mime_type = Utility.check_image_urls(image_urls)
        return {'WhatsApp Structure': Utility.create_json_structure(answer.content, body_text=None, text=None, product_ids=None, mediaType='Images', mimeType=mime_type, url=image_urls), 'tokens':total_tokens}
    
    else:
        return {'WhatsApp Structure': Utility.create_json_structure(answer.content, body_text=None, text=result.get('answer'), product_ids=None), 'tokens':total_tokens}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)