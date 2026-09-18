from dotenv import load_dotenv
import os       

load_dotenv()  # Load environment variables from .env file


DB_STRING=os.getenv("DATABASE_URL")  # Get the database URL from environment variables