from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    log_level: str = "INFO"
    log_directory: str = "/var/log/engati/meta-hackathon-finance"
    # log_directory: str = "/Users/jaymehta/Desktop/PycharmProjects/meta-hackathon-finance/logs"
    log_max_history: int = 7
    mongo_atlas_connection_uri: str = "<mongo_atlas_collection_uri>"
    mongo_atlas_db_name: str = "<mmongo_atlas_db_name>"
    mongo_atlas_vector_index_name: str = "<mongo_atlas_vector_index_name>"
    mongo_atlas_text_index_name: str = "<mongo_atlas_text_index_name>"
    mongo_atlas_collection_name: str = "nivesh-saathi"
    mongo_atlas_history_collection_name: str = "history"
    answers_base_url: str = "<answers_base_uri>"
    bing_api_key: str = "<bing_api_key>"
    aws_access_key_id: str = '<aws_access_key_id>'
    aws_access_key_secret: str = '<aws_access_key_secret>'
    aws_region_name: str = "us-east-1"
    aws_credentials_profile_name: str = "bedrock-runtime"
    aws_llm_model_id: str = "us.meta.llama3-2-90b-instruct-v1:0"
    openai_api_key: str = "<openai_api_key>" #ada-embedding
    breakpoint_threashold_type: str = "gradient"



    class Config:
        '''
        Configs will be overridden by the following environment specific file
        '''
        env_file = ".env"
