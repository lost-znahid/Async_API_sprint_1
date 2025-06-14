from pydantic import BaseSettings


class Settings(BaseSettings):
    elastic_host: str = "localhost"
    elastic_port: int = 9200
    redis_host: str = "localhost"
    redis_port: int = 6379

    class Config:
        env_file = ".env"


settings = Settings()
