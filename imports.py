from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import ChatVectorDBChain
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Qdrant
from langchain.chat_models import ChatOpenAI
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import requests
import uvicorn
import re
import mimetypes
