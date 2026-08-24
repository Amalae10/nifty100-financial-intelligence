import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME", "nifty100.db")
DATA_DIR = os.getenv("DATA_DIR", "data/raw")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")