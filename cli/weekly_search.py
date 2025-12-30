# cli/weekly_search.py
# Usage example: python cli/weekly_search.py --input settings/settings.json

# Standard library imports
import sys
import argparse
from pathlib import Path

# Modules import
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
import modules.search_executer as se


def main():
    """CLIエントリーポイント
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
