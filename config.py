import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Gemini APIキー
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEYが.envファイルに設定されていません。")

# Google Calendar APIのスコープ
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]

# 使用するAIモデル名
MODEL_NAME = "gemini-2.5-pro"

# 認証情報ファイルのパス
GOOGLE_CREDS_FILE = os.path.abspath("credentials.json")
GOOGLE_TOKEN_FILE = os.path.abspath("token.json")
