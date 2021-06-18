from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field("127.0.0.1", env="ELASTIC_HOST")
    es_port: str = Field("9200", env="ELASTIC_PORT")
    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: str = Field("6379", env="REDIS_PORT")
    api_url: str = Field("/api/v1", env="API_URL")
    service_url: str = Field("127.0.0.1", env="SERVICE_URL")
