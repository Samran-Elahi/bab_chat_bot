# Conversational Retrieval System

This project utilizes LangChain, Qdrant, and FastAPI to create a sophisticated conversational retrieval chain. It manages interactions with external APIs for fetching and handling category and product data, and leverages a vector store for efficient querying.

## Prerequisites

- Python 3.10+
- pip (Python package installer)
- Virtual environment (recommended)

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

To start the application, use the following command:
```bash
uvicorn main:BaB_chatbot --host 0.0.0.0 --port 3000
```





