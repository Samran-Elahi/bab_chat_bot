# BaB Chatbot System

This project utilizes LangChain, Qdrant, and FastAPI to create a sophisticated conversational retrieval chain. It manages interactions with external APIs for fetching and handling category and product data, and leverages a vector store for efficient querying.

## Prerequisites

- Python 3.10+
- pip (Python package installer)
- Virtual environment (recommended)

## API End-Points

- POST /list-categories: Fetches category data from the external API.
- GET /search_category: Searches for categories by name.
- GET /all_category_names: Lists all category names from stored data.
- POST /send_chat: Handles chat queries and provides AI-generated responses.
- POST /save-all-products: Hit the products api for each categoryId.
- POST /list-mentioned-products: list your desired mentioned product by productId or catgeoryId

## Parameters 

In order to get answer in Arabic you need to provide langId as '2', and if you are running celery_worker.py file with it, then use new_vectorstore paramater as 'False', because celery fil will update all the files, every hour including the vector store.  

## Installation

### Clone the Repository

To get started, clone this repository to your local machine:

```bash
git clone https://github.com/Samran-Elahi/bab_chat_bot
cd <repository-directory>
```
install the required dependencies by running:
```bash
pip install -r requirements.txt
```

Create an .env file at the root of your project directory. Populate it with necessary configurations such as API keys:

```bash
OPENAI_API_KEY='your_openai_api_key_here'
```
After running the BaB_chatbot file, you need to run the celery, for that you need to use 3 different terminal in which you have to run these:

```bash
redis-server --port 6380
```
```bash
celery -A celery_worker worker --loglevel=info
```
```bash
celery -A celery_worker beat --loglevel=info

```
For making a docker image, run this command in your terminal:
```bash
docker-compose up --build
```
Note: In order to run all these files you must be residing in your current directory.
