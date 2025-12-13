#!/bin/bash
#how to use: sh launch_app.sh

# スクリプトのあるディレクトリ（＝プロジェクトルート）
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==== Launch Journal scraper ===="

# app.pyを実行
poetry run python "${BASE_DIR}/app.py" 

