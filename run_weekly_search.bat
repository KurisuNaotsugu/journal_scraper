@echo off
SETLOCAL

echo ==== Weekly Search Script Start ====

REM このバッチのあるパス＝プロジェクトルート
SET BASE_DIR=%~dp0

poetry run python "%BASE_DIR%cli\weekly_search.py" ^
    --input "%BASE_DIR%cli\keywords.json"

echo ==== Weekly Search Script Finished ====

ENDLOCAL
pause
