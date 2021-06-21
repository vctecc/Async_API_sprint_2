from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field("127.0.0.1", env="ELASTIC_HOST")
    es_port: str = Field("9200", env="ELASTIC_PORT")
    es_wait_time: int = Field(300, env="ES_WAIT_TIME")
    es_snapshot_repo: str = Field("es-snapshots")
    es_snapshot_loc: str = Field("/usr/share/elasticsearch/backup", env="path.repo")

    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: str = Field("6379", env="REDIS_PORT")
    redis_wait_time: int = Field(300, env="REDIS_WAIT_TIME")

    api_url: str = Field("/api/v1", env="API_URL")
    service_url: str = Field("127.0.0.1:8000", env="SERVICE_URL")

    expected_response_dir = Field("tests/functional/testdata/expected_response")
