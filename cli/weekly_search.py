# cli/weekly_search.py
# Usage example: python cli/weekly_search.py --input cli/keywords.json

import sys
from pathlib import Path
import os
import json
from datetime import date
import argparse
from typing import List

# プロジェクトルートのパスを追加して modules をインポート可能に
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import modules.gemini_operator as go
import modules.pubmed_operator as po

def search_papers(keywords: List[str], mindate: str = None, maxdate: str = None) -> tuple[dict, dict]:
    """
    PubMedから論文情報とアブストラクトを取得
    """
    mindate, maxdate = po.calculate_date_range(mindate, maxdate)

    pmids = po.fetch_esearch(keywords, mindate, maxdate)
    if not pmids:
        print("該当する論文はありませんでした。")
        return {}, {}

    print(f"{len(pmids)} 件の論文を取得しました。")

    # 論文情報を取得
    esummary_xml = po.fetch_esummary(pmids)
    esummary_list = po.parse_esummary_xml(esummary_xml)

    # アブストラクトを取得
    abstracts_dict = po.fetch_eFetch(pmids)

    return esummary_list, abstracts_dict, mindate, maxdate


def summarize_abstracts(abstracts_dict: dict) -> dict[str, str]:
    """
    Gemini を使ってアブストラクトを要約
    """
    gemini_client = go.genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    summaries = {}
    for pmid, abstract in abstracts_dict.items():
        if abstract == "N/A" or not abstract.strip():
            summaries[pmid] = "No abstract exists."
            continue

        prompt = go.build_prompt(go.PROMPT_TEMPLATE, abstract=abstract)
        summary = go.request_gemini_json(gemini_client, prompt)
        summaries[pmid] = summary

    return summaries

# ユーティリティ関数: config.json の読み書き
def load_config():
    config_path = ROOT / "cli" / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"config.json が見つかりません: {config_path}")

    with open(config_path, "r") as f:
        return json.load(f)


def save_config(new_date: str):
    config_path = ROOT / "cli" / "config.json"
    with open(config_path, "w") as f:
        json.dump({"last_search_date": new_date}, f, indent=2, ensure_ascii=False)


def main():
    """メイン関数
    Args:
        --input: 入力キーワードファイル（JSON形式）
    
    """
    parser = argparse.ArgumentParser(description="PubMed search and summarize tool")
    parser.add_argument("--input", type=str, default="keywords.json", help="入力キーワードファイル（JSON）")
    args = parser.parse_args()
    input_path = Path(args.input)

    # 入力ファイル存在チェック
    if not input_path.exists():
        print(f"[ERROR] 入力ファイルが存在しません: {input_path}")
        return
    
    # 検索期間設定
    config = load_config()
    mindate = config["last_search_date"]
    maxdate = date.today().strftime("%Y/%m/%d")

    print(f"\n>>> 検索期間: {mindate} ～ {maxdate}")

    # キーワードJSON 読み込み 
    with open(input_path, "r") as f:
        metas = json.load(f)

    if not isinstance(metas, list):
        print("[ERROR] JSONは配列形式で複数検索を指定してください。")
        return

    for meta in metas:
        search_title = meta.get("search_title", "Untitled search")
        keywords = meta.get("keywords", [])
        if not keywords:
            print(f"[WARNING] {search_title} に keywords がありません。スキップします。")
            continue

        print(f"\n=== {search_title} ===")
        print(f"キーワード: {keywords}")

        # 論文検索
        esummary_list, abstracts_dict, mindate, maxdate = search_papers(keywords, mindate, maxdate)
        if not esummary_list:
            continue

        # 検索期間文字列
        search_period = str(f"{mindate} - {maxdate}").replace("/", "-").replace(" ", "_")

        # 要約生成
        summaries = summarize_abstracts(abstracts_dict)

        # 出力データ構築
        output_data = {
            "title": search_title,
            "keywords": keywords,
            "search_period": search_period,
            "paper_count": len(esummary_list),
            "papers": []
        }
        # 論文情報の登録
        for esummary in esummary_list:
            pmid = esummary["pmid"]
            output_data["papers"].append({
                "pmid": pmid,
                "title": esummary["Title"],
                "pubdate": esummary["pubdate"],
                "url": esummary["URL"],
                "abstract": abstracts_dict.get(pmid),
                "summary": summaries.get(pmid)
            })
        # 出力ディレクトリ作成
        output_dir = Path(search_period)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 出力ファイル名生成
        search_title_for_save = search_title.replace(" ", "_").replace("/", "-")
        filename = f"{search_title_for_save}.json"

        # 出力パス生成
        output_path = output_dir / filename

        # ---- JSON 保存 ----
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nDONE! → {output_path}")
    
    # 検索終了後、config.json の last_search_date を更新
    save_config(new_date=maxdate) 
    print(f"\nUpdated last_search_date to {maxdate} in config.json")


if __name__ == "__main__":
    main()
