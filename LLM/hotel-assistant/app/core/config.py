from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ES_URL: str
    ES_INDEX: str
    # ES_USER: str
    # ES_PASS: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"  # Loads variables from your .env file automatically

settings = Settings()  # type: ignore
