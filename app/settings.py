from pydantic import BaseModel

class Settings(BaseModel):
    db_path: str = "q4_rescue.sqlite3"

settings = Settings()
