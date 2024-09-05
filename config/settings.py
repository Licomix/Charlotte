from dotenv import load_dotenv
import os

load_dotenv()


LOG_DIR = os.getenv("LOG_DIR")
SEND_INTERVAL_MIN = os.getenv("SEND_INTERVAL_MIN")
USE_AD = os.getenv("USE_AD")
