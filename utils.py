from imports import *
from constants import Const


class Utility:
    responses = []
    category_names = []
    
    @staticmethod
    def save_response_to_file(data, filename):
        """Saves JSON data to a file if the file does not already exist.

        Args:
            data: The data to be saved.
            filename: The name of the file where data will be saved.

        Returns:
            None
        """
        with open(filename, 'w') as f:
            
            json.dump(data, f, indent=4)
        print(f"Response saved to {filename}")
        
    @staticmethod
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
    
    @staticmethod
    def combine_chunk():
        """Combines chunks from product and category JSON files.

        Returns:
            A list combining chunks from both product and category JSON files.
        """
        chunks_products = Utility.chunk_json('product_responses.json', 2000, 300)
        chunks_categories = Utility.chunk_json('category_responses.json', 6000, 500)
        return chunks_categories + chunks_products

    @staticmethod
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
            qdrant = qdrant.from_texts(Utility.combine_chunk(), embeddings, url=Const.QDRANT_URL, prefer_grpc=True, api_key=Const.QDRANT_API_KEY, collection_name=Const.COLLECTION_NAME)
        return qdrant

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
                found = Utility.find_category(item['childs'], category_name)
                if found:
                    return found
        return None

    @staticmethod
    def extract_category_names(data):
        """Extracts category names from the given data recursively.

        Args:
            data: The data from which to extract category names.

        Returns:
            None
        """
        for item in data:
            Utility.category_names.append(item['categoryName'])
            if 'childs' in item and item['childs']:
                Utility.extract_category_names(item['childs'])

    @staticmethod
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

    @staticmethod
    def hit_all_product_api():
        """Hits the product API for all category IDs and saves the responses to a file.

        Returns:
            None
        """
        results = []
        category_result = Utility.hit_category_API(Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, Const.LANG, Const.CATEGORY_API)
        ids = Utility.process_ids(category_result)
        for id in ids:
            result = Utility.hit_product_API(Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, Const.LANG, Const.PRODUCT_API, id, None)
            results.append(result)
        Utility.save_response_to_file(results, 'product_responses.json')
