from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./comequeta.db"
    debug: bool = False

    # Auth / JWT. The default secret is for local development only; set a strong
    # value via the environment in any shared setting.
    jwt_secret_key: str = "dev-insecure-change-me-with-openssl-rand-hex-32"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Origins allowed to call the API from a browser (the Vite dev server and
    # the Capacitor app's webview).
    cors_origins: list[str] = [
        "http://localhost:5173",
        "capacitor://localhost",
        "http://localhost",
    ]


settings = Settings()
