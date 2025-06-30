# syntax=docker/dockerfile:1
FROM python:3.11-slim

# 作業ディレクトリ作成
WORKDIR /app

# 依存ファイルをコピー
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . .

# 環境変数（Flask用）
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# ポート公開
EXPOSE 8080

# Flask起動（gunicorn推奨の場合は下記コメント参照）
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
# 例: gunicornで起動する場合
# CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
