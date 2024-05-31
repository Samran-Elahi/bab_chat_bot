from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dataclasses import dataclass
import os
import requests
import json
import uvicorn

load_dotenv()

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

class Utility:
    @staticmethod
    def save_response_to_file(data, filename):
        """Saves JSON data to a file if the file does not already exist.

        Args:
            data: The data to be saved.
            filename: The name of the file where data will be saved.

        Returns:
            None
        """
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Response saved to {filename}")
        else:
            print(f"File {filename} already exists. No action taken.")

def chunk_json(file_path: str, chunk_size: int, overlap: int) -> list:
    """Splits a JSON file content into chunks of specified size with overlap.

    Args:
        file_path: The path to the JSON file.
        chunk_size: The size of each chunk.
        overlap: The number of characters each chunk overlaps with the next.

    Returns:
        A list of string chunks.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        json_string = file.read()
    chunks = [json_string[i:i+chunk_size] for i in range(0, len(json_string) - overlap, chunk_size)]
    return chunks

def combine_chunk():
    """Combines chunks from product and category JSON files.

    Returns:
        A list combining chunks from both product and category JSON files.
    """
    chunks_products = chunk_json('product_responses.json', 2000, 300)
    chunks_categories = chunk_json('category_response.json', 6000, 500)
    return chunks_categories + chunks_products

def get_vectorstore(new_vectorstore=False):
    """Initializes and returns a Qdrant vector store.

    Args:
        new_vectorstore: A boolean flag to indicate whether a new vector store should be created.

    Returns:
        An instance of Qdrant vector store.
    """
    embeddings = OpenAIEmbeddings(api_key=Const.OPENAI_API_KEY)
    client = QdrantClient(url=Const.QDRANT_URL, headers={"Authorization": f"Bearer {Const.QDRANT_API_KEY}"})
    qdrant = Qdrant(client, Const.COLLECTION_NAME, embeddings)
    if new_vectorstore == True:
        qdrant.from_texts(combine_chunk(), embeddings, url=Const.QDRANT_URL, prefer_grpc=True, api_key=Const.QDRANT_API_KEY, collection_name=Const.COLLECTION_NAME)
    return qdrant

def get_conversation_chain(vectorstore):
    """Creates and returns a conversational retrieval chain.

    Args:
        vectorstore: The vector store to be used as a retriever.

    Returns:
        An instance of ConversationalRetrievalChain.
    """
    llm = ChatOpenAI(max_tokens=500)
    memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={'k': 5}),
        memory=memory,
        response_if_no_docs_found="I don't have this information",
        rephrase_question=False,
        return_source_documents=True,
    )
    return conversation_chain

def hit_category_API(deviceId, email, password, securityCode, langId, url):
    """Sends a POST request to the category API and returns the response.

    Args:
        deviceId: The device ID.
        email: The email address.
        password: The password.
        securityCode: The security code.
        langId: The language ID.
        url: The URL of the category API.

    Returns:
        The JSON response from the API or plain text if JSON decoding fails.
    """
    headers = {
        'proxy-auth': 'Bearer HJfDtvMjWxQAGlnZUraguiwGYLnYECkBieHdsAFosFiNTpcIjd',
        'X-Target-Server': 'https://taxes.like4app.com'
    }
    payload = {
        'deviceId': deviceId,
        'email': email,
        'password': password,
        'securityCode': securityCode,
        'langId': langId
    }
    response = requests.post(url, headers=headers, data=payload)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return response.text

def hit_product_API(deviceId, email, password, securityCode, langId, url, categoryid=None, ids=None):
    """Sends a POST request to the product API and returns the response.

    Args:
        deviceId: The device ID.
        email: The email address.
        password: The password.
        securityCode: The security code.
        langId: The language ID.
        url: The URL of the product API.
        categoryid: The category ID (optional).
        ids: The product IDs (optional).

    Returns:
        The JSON response from the API or plain text if JSON decoding fails.
    """
    headers = {
        'proxy-auth': 'Bearer HJfDtvMjWxQAGlnZUraguiwGYLnYECkBieHdsAFosFiNTpcIjd',
        'X-Target-Server': 'https://taxes.like4app.com'
    }
    payload = {
        'deviceId': deviceId,
        'email': email,
        'password': password,
        'securityCode': securityCode,
        'langId': langId
    }
    if categoryid:
        payload['categoryId'] = categoryid
    if ids:
        payload['ids[]'] = ids if isinstance(ids, list) else [ids]
    if not categoryid and not ids:
        raise ValueError("Either 'categoryid' or 'ids' must be provided")
    response = requests.post(url, headers=headers, data=payload)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return response.text

def find_category(data, category_name):
    """Recursively searches for a category by name in the given data.

    Args:
        data: The data to search through.
        category_name: The name of the category to find.

    Returns:
        The category item if found, otherwise None.
    """
    for item in data:
        if item['categoryName'].lower() == category_name.lower():
            return item
        if 'childs' in item and item['childs']:
            found = find_category(item['childs'], category_name)
            if found:
                return found
    return None

def extract_category_names(data):
    """Extracts category names from the given data recursively.

    Args:
        data: The data from which to extract category names.

    Returns:
        None
    """
    for item in data:
        category_names.append(item['categoryName'])
        if 'childs' in item and item['childs']:
            extract_category_names(item['childs'])

def process_ids(data):
    """Extracts all 'id' values from the given JSON data.

    Args:
        data: The JSON data from which to extract IDs.

    Returns:
        A list of IDs.
    """
    ids =[]
    def extract_ids(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'id':
                    ids.append(value)
                elif isinstance(value, dict) or isinstance(value, list):
                    extract_ids(value)
        elif isinstance(data, list):
            for item in data:
                extract_ids(item)
    extract_ids(data['data'])
    return ids

def hit_all_product_api():
    """Hits the product API for all category IDs and saves the responses to a file.

    Returns:
        None
    """
    results = []
    category_result = hit_category_API(Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, Const.LANG, Const.CATEGORY_API)
    ids = process_ids(category_result)
    for id in ids:
        result = hit_product_API(Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, Const.LANG, Const.PRODUCT_API, id, None)
        results.append(result)
    Utility.save_response_to_file(results, 'product_responses.json')


app = FastAPI()

responses = []
category_names = []

@app.post("/save-all-products")
async def save_all_products():
    return hit_all_product_api()

@app.post("/list-mentioned-products")
async def list_mentioned_products(id=None, category=None):
    return hit_product_API(Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, Const.LANG, Const.PRODUCT_API, id, category)

@app.post("/list-categories")
async def call_external_api():
    """Endpoint to call the external category API.

    Args:
        request: The request body containing deviceId, email, password, securityCode, and langId.

    Returns:
        The response from the category API.
    """
    result = hit_category_API(
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
    for response in responses:
        if 'data' in response:
            found_item = find_category(response['data'], category_name)
            if found_item:
                return found_item
    raise HTTPException(status_code=404, detail="Category not found")

@app.get("/all_category_names")
async def get_all_category_names():
    """Endpoint to retrieve all category names.

    Returns:
        A list of all category names extracted from the stored responses.
    """
    category_names.clear()
    for response in responses:
        if 'data' in response:
            extract_category_names(response['data'])
    return category_names

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
    main_conversation = get_conversation_chain(get_vectorstore())
    uvicorn.run(app, host="0.0.0.0", port=3000)
