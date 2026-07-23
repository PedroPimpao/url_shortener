import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise RuntimeError(
        "A variavel de ambiente DATABASE_URL nao foi definida. "
        "Crie um arquivo .env com base no .env.example."
    )