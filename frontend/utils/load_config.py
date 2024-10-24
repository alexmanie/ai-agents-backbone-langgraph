import os
from dotenv import load_dotenv
import yaml
from openai import AzureOpenAI
from pyprojroot import here

print("Environment variables are loaded:", load_dotenv())

class LoadConfig:
    def __init__(self) -> None:
        frontend_path = here() / "."
        config_file = frontend_path / "config/app_config.yml"
        with open(config_file) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        self.load_api_configs(app_config=app_config)
        self.load_llm_config(app_config=app_config)
        # self.load_openai_config()

    def load_api_configs(self, app_config):
        # self.api_url = app_config["api_config"]["api_url"]
        # self.api_key = app_config["api_config"]["api_key"]
        self.api_url = app_config["api_config"]["api_url"]
        
    def load_llm_config(self, app_config):
        self.agent_llm_system_role = app_config["llm_config"]["agent_llm_system_role"]
        # self.rag_llm_system_role = app_config["llm_config"]["rag_llm_system_role"]
        self.deployment = app_config["llm_config"]["deployment"]
        self.temperature = app_config["llm_config"]["temperature"]
        # self.embedding_model_name = os.getenv("embed_deployment_name")
    
    # def load_openai_config(self):
    #     azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    #     azure_openai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
    #     # This will be used for the GPT and embedding models
    #     self.azure_openai_client = AzureOpenAI(
    #         api_key=azure_openai_api_key,
    #         api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    #         azure_endpoint=azure_openai_endpoint,
    #         max_retries=0
    #     )
    
    