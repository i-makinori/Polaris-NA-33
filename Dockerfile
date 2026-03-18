# 1. ベースイメージ
FROM python:3.12-slim

# 2. 作業ディレクトリの設定
WORKDIR /app

# 3. 依存ライブラリのインストール
# 事前に pip freeze > requirements.txt を実行しておいてください
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 全ファイルをコピー
COPY . .

# 5. PYTHONPATH を設定して、hostディレクトリ内のインポートを解決する
ENV PYTHONPATH=/app/host

# 6. server.py を実行
# host/server.py がエントリーポイント
CMD ["python", "host/server.py"]

