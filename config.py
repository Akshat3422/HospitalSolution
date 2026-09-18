from dotenv import load_dotenv
import os       

load_dotenv()  # Load environment variables from .env file


POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")  # Get the PostgreSQL password from environment variables
DB_STRING=os.getenv("DATABASE_URL")  # Get the database URL from environment variables