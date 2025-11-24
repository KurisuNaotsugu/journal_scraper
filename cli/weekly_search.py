import modules.gemini_operator as go
import modules.pubmed_operator as po

from typing import List
import os
import json
import argparse
from pathlib import Path


def search_papers(keywords: List[str], mindate: str, maxdate: str) -> list[dict]:
    for keyword in keywords:
        print(f"\n=== キーワード: {keyword} ===")

        # 論文検索
        mindate, maxdate = po.calculate_date_range()

        print(f'検索期間: {mindate} ～ {maxdate}')
        print(f'検索キーワード: {keywords}')

        pmids = po.fetch_esearch(keywords, mindate, maxdate)

        if not pmids:
            print('該当する論文はありませんでした。')
            exit()

        print(f'{len(pmids)} 件の論文を取得しました。')

        # 論文情報を取得
        esummary_xml = po.fetch_esummary(pmids)
        esummary_dict = po.parse_esummary_xml(esummary_xml)

        # アブストラクトを取得
        abstracts_dict = po.fetch_eFetch(pmids)

        return esummary_dict, abstracts_dict
    
def summarize_abstracts(abstracts_dict: dict) -> dict[str, str]:
    """アブストラクト辞書を要約する関数
    pmidをキー、pubmedから取得したabstractを値とする辞書を受け取り、
    Geminiを用いて要約を生成する。

    Args:
        abstracts_dict (dict): {pmid: abstract}形式のアブストラクト辞書
    Returns:
        dict: {pmid: summary}形式の要約辞書
    """

    gemini_client = go.genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    abst_summaries = {}
    for pmid, abstract in abstracts_dict.items():

        if abstract == "N/A" or not abstract.strip():
            abst_summaries[pmid] = "No abstract exists."
            continue

        # プロンプト生成
        prompt = go.build_prompt(
            go.PROMPT_TEMPLATE ,
            abstract=abstract
        )

        # Gemini で処理
        summary = go.summarize_text(gemini_client, prompt)
        abst_summaries[pmid] = summary

    return abst_summaries
    
def main():
    parser = argparse.ArgumentParser(description="PubMed search and summarize tool")
    
    parser.add_argument(
        "--input",
        type=str,
        default="keywords.json",
        help="入力キーワードファイル（JSON）"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="result.json",
        help="出力ファイル名（JSON）"
    )
    
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"[ERROR] 入力ファイルが存在しません: {input_path}")
        return

    # ---- JSON 読み込み ----
    with open(input_path, "r") as f:
        meta = json.load(f)

    search_title = meta.get("search_title", "Untitled search")
    keywords = meta.get("keywords", [])

    if not keywords:
        print("[ERROR] JSON に keywords がありません。")
        return

    print(f"=== {search_title} ===")
    print(f"キーワード: {keywords}")

    # ---- PubMed 検索 ----
    esummary_dict, abstracts_dict = search_papers(
        keywords=keywords,
        mindate=None,
        maxdate=None
    )

    # ---- アブストラクト要約 ----
    summaries = summarize_abstracts(abstracts_dict)

    # ---- 保存用 JSON データ作成 ----
    output_data = {
        "title": search_title,
        "keywords": keywords,
        "paper_count": len(esummary_dict),
        "papers": []
    }

    for pmid, info in esummary_dict.items():
        output_data["papers"].append({
            "pmid": pmid,
            "title": info.get("Title"),
            "pubdate": info.get("pubdate"),
            "url": info.get("URL"),
            "abstract": abstracts_dict.get(pmid),
            "summary": summaries.get(pmid)
        })

    # ---- JSON 保存 ----
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nDONE! → {output_path}")


if __name__ == '__main__':
    main()