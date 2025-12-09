#!/bin/bash

# スクリプトのあるディレクトリ（＝プロジェクトルート）
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==== Weekly Search Script Start ===="

# 固定のコマンドのみ実行
poetry run python "${BASE_DIR}/cli/weekly_search.py" \
    --input "${BASE_DIR}/cli/keywords.json"

echo "==== Weekly Search Script Finished ===="
