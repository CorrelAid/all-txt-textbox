from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiKey(BaseModel):
    prefix: str = Field(default="alltxt")


class Cors(BaseModel):
    allow_origins: list[str] = Field(default=["*"])
    allow_credentials: bool = Field(default=True)
    allow_methods: list[str] = Field(default=["*"])
    allow_headers: list[str] = Field(default=["*"])


class Database(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    user: SecretStr = Field(default=SecretStr("all_txt"))
    password: SecretStr = Field(default=SecretStr("pass"))
    database: str = Field(default="all_txt")

    @property
    def dsn(self) -> str:
        return f"postgresql+psycopg_async://{self.user.get_secret_value()}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"


class Redis(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    password: SecretStr = Field(default=SecretStr("pass"))

    @property
    def dsn(self) -> str:
        return f"redis://:{self.password.get_secret_value()}@{self.host}:{self.port}/0"


class Session(BaseModel):
    valid_for: int = Field(default=360)  # in minutes


class Settings(BaseSettings):

    session: Session = Session()
    cors: Cors = Cors()
    database: Database = Database()
    migration: Database = Database()
    redis: Redis = Redis()
    api_key: ApiKey = ApiKey()

    model_config = SettingsConfigDict(
        env_prefix="ALL_TXT_BACKEND_",
        secrets_dir="/run/secrets",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


settings = Settings()
