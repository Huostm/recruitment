import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_ollama import OllamaEmbeddings


class LLMService:
    def __init__(self):
        load_dotenv()  # 加载 .env 文件

        # 禁用代理，避免 Ollama 本地连接走代理
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
        os.environ['no_proxy'] = 'localhost,127.0.0.1'

        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.model_name = os.getenv("MODEL_NAME")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        self.embedding_model = os.getenv("OLLAMA_MODEL")

        self.llm = init_chat_model(
            model_provider=os.getenv("MODEL_PROVIDER"),
            model=self.model_name,
            api_key=self.deepseek_api_key,
            temperature=0.7
        )

        self.embeddings = OllamaEmbeddings(
            model=self.embedding_model,
            base_url=self.ollama_base_url
        )

    def get_llm(self):
        return self.llm

    def get_embeddings(self):
        return self.embeddings