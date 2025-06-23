import os
from dotenv import load_dotenv

env = os.getenv("ENV", "development")  
load_dotenv(".env", override=True)

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY")

settings = Settings()