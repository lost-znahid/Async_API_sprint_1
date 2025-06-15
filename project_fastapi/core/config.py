from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    elastic_host: str = "localhost"
    elastic_port: int = 9200
    redis_host: str = "localhost"
    redis_port: int = 6379

    @property
    def elastic_url(self) -> str:
        return f"http://{self.elastic_host}:{self.elastic_port}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    class Config:
        env_file = ".env"


settings = Settings()
