from dotenv import load_dotenv
from langchain_ollama import ChatOllama
import os

load_dotenv()

MODEL_NAME = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b"
)

MAX_ITERATIONS = int(os.getenv(
    "MAX_ITERATION",
    "5"
))

model = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)