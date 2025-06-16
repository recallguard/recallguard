import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    pg_host: str = 'localhost'
    pg_port: int = 5432
    pg_user: str = 'recallguard'
    pg_pass: str = 'recallguard'
    pg_db: str = 'recallguard'
    env: str = 'dev'

    model_config = {
        'extra': 'ignore'
    }

    @property
    def database_url(self) -> str:
        override = getattr(self, 'database_url_override', None) or os.getenv('DATABASE_URL')
        if override:
            return override
        return f"postgresql+psycopg2://{self.pg_user}:{self.pg_pass}@{self.pg_host}/{self.pg_db}"

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
