# cli/weekly_search.py

# Import libraries
import sys
import argparse
from pathlib import Path

# Import modules
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
import modules.search_executer as se

def main():
    """CLIエントリーポイント。引数に指定した検索期間に基づいてPubmed検索を実行する。
    検索結果キーワードの取得および結果の保存はデータベース上に行う。
    """
    parser = argparse.ArgumentParser(description="PubMed search and summarize tool")
    parser.add_argument("--mindate", type=str, default=None, help="検索開始日 (YYYY/MM/DD)")
    parser.add_argument("--maxdate", type=str, default=None, help="検索終了日 (YYYY/MM/DD)")
    args = parser.parse_args()
    
    se.run_weekly_search(
        mindate=args.mindate,
        maxdate=args.maxdate,
    )

if __name__ == "__main__":
    main()
