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
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
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
    def combine_chunk(langId):
        """Combines chunks from product and category JSON files.

        Returns:
            A list combining chunks from both product and category JSON files.
        """
        if langId == '2':
            chunks_products = Utility.chunk_json('arabic_category_responses.json', 2000, 300)
            chunks_categories = Utility.chunk_json('arabic_product_responses.json', 6000, 500)
        else:
            chunks_products = Utility.chunk_json('english_category_responses.json', 2000, 300)
            chunks_categories = Utility.chunk_json('english_product_responses.json', 6000, 500)
        return chunks_categories + chunks_products

    @staticmethod
    def get_vectorstore(langId, new_vectorstore=False):
        """Initializes and returns a Qdrant vector store based on language id.

        Args:
            new_vectorstore: A boolean flag to indicate whether a new vector store should be created.

        Returns:
            An instance of Qdrant vector store.
        """
        embeddings = OpenAIEmbeddings(api_key=Const.OPENAI_API_KEY)
        client = QdrantClient(url=Const.QDRANT_URL, headers={"Authorization": f"Bearer {Const.QDRANT_API_KEY}"})
       
        if langId == '2':
            collection_name = Const.ARABIC_COLLECTION_NAME
            productName_collection_name = Const.ARABIC_PRODUCTNAME_COLLECTION_NAME
            chunk_productName = Utility.extract_product_names('arabic_product_responses.json')
        else:
            collection_name = Const.ENGLISH_COLLECTION_NAME
            productName_collection_name = Const.ENGLISH_PRODUCTNAME_COLLECTION_NAME
            chunk_productName = Utility.extract_product_names('english_product_responses.json')
        
        if new_vectorstore:
        
            chunks = Utility.combine_chunk(langId)
            qdrant = Qdrant(client, collection_name, embeddings).from_texts(
            chunks,
            embeddings,
            url=Const.QDRANT_URL,
            prefer_grpc=True,
            api_key=Const.QDRANT_API_KEY,
            collection_name=collection_name
        )
            product_qdrant = Qdrant(client, productName_collection_name, embeddings).from_texts(
            chunk_productName,
            embeddings,
            url=Const.QDRANT_URL,
            prefer_grpc=True,
            api_key=Const.QDRANT_API_KEY,
            collection_name=productName_collection_name
        )
        
        else:
            qdrant = Qdrant(client, collection_name, embeddings)
            product_qdrant = Qdrant(client, productName_collection_name, embeddings)

        return qdrant, product_qdrant

    @staticmethod
    def get_conversation_chain(vectorstore, llm):
        """Creates and returns a conversational retrieval chain.

        Args:
            vectorstore: The vector store to be used as a retriever.

        Returns:
            An instance of ConversationalRetrievalChain.
        """
        memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={'k': 3}),
            memory=memory,
            response_if_no_docs_found="I don't have this information rightnow. Please provide more context to answer your query.",
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
    def hit_all_product_api(langId):
        """Hits the product API for all category IDs and saves the responses to a file.

        Returns:
            None
        """
        results = []
        category_result = Utility.hit_category_API(Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, langId, Const.CATEGORY_API)
        ids = Utility.process_ids(category_result)
        for id in ids:
            result = Utility.hit_product_API(Const.DEVICE_ID, Const.EMAIL, Const.PASSWORD, Const.SECURITY_CODE, langId, Const.PRODUCT_API, id, None)
            results.append(result)
        if langId == '2':
            Utility.save_response_to_file(results, 'arabic_product_responses.json')
        else:
            Utility.save_response_to_file(results, 'english_product_responses.json')
    
    @staticmethod
    def extract_product_names(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")

        product_names = []
        for item in data:
            if item.get("response") == 1 and "data" in item:
                for product in item["data"]:
                    product_names.append(product["productName"])
        return product_names

    @staticmethod
    def get_product_id_by_name(file_path, product_name):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")

        for item in data:
            if item.get("response") == 1 and "data" in item:
                for product in item["data"]:
                    if product_name.lower() in (product["productName"]).lower():
                        return product["productId"]
        return None

    @staticmethod
    def get_product_name(data):
        """
        Extracts product names from the response string where each product is listed on a new line
        starting with a dash and space ('- ').
        
        Args:
        response (str): The response string containing the product names.
        
        Returns:
        list: A list of product names.
        """
            # Define markers for start and end of product names
        start_marker = "START_PRODUCT_NAMES"
        end_marker = "END_PRODUCT_NAMES"
        
        # Find indices for start and end markers
        start_index = data.find(start_marker) + len(start_marker)
        end_index = data.find(end_marker)
        
        # Check if both markers are found
        if start_index - len(start_marker) == -1 or end_index == -1:
            return []  # Return an empty list if any marker is not found

        # Extract the product names segment and strip any leading/trailing whitespace
        product_names_segment = data[start_index:end_index].strip()
        
        # Split the product names by comma and strip whitespace from each product name
        product_names = [name.strip() for name in product_names_segment.split(',')]
        
        return product_names
    
    @staticmethod
    def create_json_structure(type_value, body_text=None, text=None, product_ids=None,  mediaType=None, mimeType=None, url=None):
        data = {}
        
        if body_text is not None:
            data['body'] = body_text
        if text is not None:
            data['text'] = text
        if product_ids is not None:
            if isinstance(product_ids, list):
                data['productIds'] = product_ids
            else:
                data['productId'] = product_ids
        
        if mediaType is not None or mimeType is not None or url is not None:
            data['mediaType'] = mediaType
            data['mimeType'] = mimeType
            if isinstance(url, list):
                data['urls'] = url
            else:
                data['url'] = url
            
        json_structure = {
            "type": type_value,
            "data": data
        }
        
        return json_structure
    
    @staticmethod
    def extract_urls(text):
        # Regular expression pattern to find URLs starting with http and ending with typical URL endings
        url_pattern = r'https?://[^\s\)]+(?:\.png|\.jpg|\.jpeg|\.gif|\.bmp|\.webp|\.svg|\.pdf|\.html|\.htm|\.php|\.asp|\.aspx|\.js|\.css|\.json|\.xml|/)?'
        urls = re.findall(url_pattern, text)
        return urls

    @staticmethod
    def check_image_urls(image_urls):
        non_png_mime_types = set()
        
        for url in image_urls:
            mime_type,_ = mimetypes.guess_type(url)
            non_png_mime_types.add(mime_type)
        
        return non_png_mime_types
