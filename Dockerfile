# syntax=docker/dockerfile:1
FROM python:3.10-slim

# 環境変数でPYTHONPATHを設定し、srcディレクトリをPythonの検索パスに追加
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# 作業ディレクトリを設定
WORKDIR /app

# 必要なライブラリを先にインストールしてキャッシュを効かせる
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# Gunicornを起動するための設定
# Cloud Runが提供するPORT環境変数をリッスンする
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
