import sys
from pathlib import Path
import os
import json
from datetime import date
from typing import List

# DB imports
from db.database import SessionLocal
from db.repositories.app_state import AppStateRepository
from db.repositories.search_config import SearchConfigRepository
from db.repositories.search_result import SearchResultRepository

# Import modules
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
import modules.gemini_operator as go
import modules.pubmed_operator as po

# --- Config DB操作 ---

def load_last_search_date():
    """前回検索実行日をDBから取得
    """
    with SessionLocal() as session:
        repo = AppStateRepository(session)
        state = repo.get_or_create()
        return state.last_search_date

def save_last_search_date(new_date: str):
    """検索実行日を更新
    """
    with SessionLocal() as session:
        repo = AppStateRepository(session)
        repo.update_last_search_date(new_date)
        session.commit()

def load_search_setting():
    """SearchConfig と KeywordConfig から検索メタデータを取得
    """
    with SessionLocal() as session:
        repo = SearchConfigRepository(session)
        results = []
        for cfg in repo.find_all():
            keywords = [k.keyword for k in cfg.keywords if k.enabled]
            results.append({
                "search_title": cfg.title,
                "keywords": keywords
            })
        return results
    
def save_search_results_to_db(results: list):
    """検索結果をDBに保存
    """
    with SessionLocal() as session:
        repo = SearchResultRepository(session)

        for r in results:
            repo.create_search_result(
                title=r["title"],
                search_period=r["search_period"],
                keywords=r["keywords"],
                papers=r["papers"],
            )

        session.commit()

# --- 論文検索と要約のメイン処理 ---

def search_papers(keywords: List[str], mindate: str = None, maxdate: str = None, max_results: int = 30) -> tuple[dict, dict]:
    """PubMedから論文情報とアブストラクトを取得
    Args:
        keywords (List[str]): 検索キーワードのリスト
        mindate (str, optional): 検索開始日 (YYYY/MM/DD). Defaults to None.
        maxdate (str, optional): 検索終了日 (YYYY/MM/DD). Defaults to None.
        max_results (int, optional): 最大取得論文数. Defaults to 10.
    Returns:
        tuple: esummary_list (dict), abstracts_dict (dict), mindate (str), maxdate (str)
    """
    print("(search_parpers) 論文開始...")
    mindate, maxdate = po.calculate_date_range(mindate, maxdate)

    # 論文IDを検索
    pmids = po.fetch_esearch(keywords, mindate, maxdate)
    if not pmids:
        print("(search_parpers) 該当する論文はありませんでした。")
        return {}, {}, mindate, maxdate
    
    if len(pmids) > max_results:
        print(f"(search_parpers) 論文数が指定上限({max_results})より多いため検索を終了します。")
        return {}, {}, mindate, maxdate
    
    print(f"(search_parpers) {len(pmids)} 件の論文がヒットしました。データ収集を開始します。")

    # 論文情報を取得
    esummary_xml = po.fetch_esummary(pmids)
    esummary_list = po.parse_esummary_xml(esummary_xml)
    print(f"(search_parpers) {len(pmids)} 件の論文を取得しました。")

    # アブストラクトを取得
    abstracts_dict = po.fetch_eFetch(pmids)
    print(f"(search_parpers) アブストラクトを取得しました。")

    return esummary_list, abstracts_dict, mindate, maxdate


def summarize_abstracts(abstracts_dict: dict) -> dict[str, str]:
    """Gemini を使ってアブストラクトを要約
    """
    print(f"(summarize_abstracts) Geminiによる要約を開始します...")
    gemini_client = go.genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    summaries = {}
    for pmid, abstract in abstracts_dict.items():

        if not abstract or abstract == "N/A" or not abstract.strip():
            summaries[pmid] = "No abstract exists."
            continue

        prompt = go.build_prompt(go.PROMPT_TEMPLATE, abstract=abstract)
        summary = go.request_gemini_json(gemini_client, prompt)
        summaries[pmid] = summary
    print(f"(summarize_abstracts) 要約が完了しました。")

    return summaries

def manual_search(input_json: list, mindate: str, maxdate: str):
    """Flaskからマニュアルサーチする際のメイン処理

    Args;
        input_json (list): 検索メタデータのリスト
        mindate (str): 検索開始日
        maxdate (str): 検索終了日 

    Returns:
        results (list): 各検索結果のリスト
    """
    print(f"(manual_search) 文献調査を開始します: 検索期間: {mindate} ～ {maxdate}")
    results = []
    for meta in input_json:
        search_title = meta.get("search_title", "Untitled search")
        keywords = meta.get("keywords", [])
        if not keywords:
            results.append({"error": f"{search_title}: keywords がありません。"})
            continue
        print(f"\n(manual_search) '{search_title}' の検索を開始します(キーワード: {keywords})")
        
        # 論文検索
        esummary_list, abstracts_dict, mindate, maxdate = search_papers(keywords, mindate, maxdate)
        if not esummary_list:
            results.append({
                "title": search_title,
                "keywords": keywords,
                "search_period": f"{mindate}-{maxdate}".replace("/", "-"),
                "paper_count": 0,
                "papers": []
            })
            continue

        # 要約生成
        summaries = summarize_abstracts(abstracts_dict)

        # 出力データ構築
        print(f"(manual_search) 出力データを構築します...")
        search_period = f"{mindate}-{maxdate}".replace("/", "-")
        output_data = {
            "title": search_title,
            "keywords": keywords,
            "search_period": search_period,
            "paper_count": len(esummary_list),
            "papers": []
        }
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
        results.append(output_data)

        print(f"(manual_search) '{search_title}' の処理が完了しました。")
    return results

def run_weekly_search(mindate: str, maxdate: str):
    """CLIエントリーポイント
    """
    # 検索期間処理
    if mindate is None:
        mindate = load_last_search_date()
    maxdate = maxdate or date.today().strftime("%Y/%m/%d")

    # 検索設定取得
    input_json = load_search_setting()
    if not input_json:
        print("[ERROR] 検索設定が存在しません。DBにSearchConfigを追加してください。")
        return

    #--- 検索と要約の実行 ---
    results = manual_search(input_json, mindate, maxdate)
    if not results:
        print("検索結果がありませんでした。")
        return
    
    # --- 結果保存 ---
    save_search_results_to_db(results)
    print("Search results saved to database.")

    # --- config更新 ---
    save_last_search_date(maxdate)
    print(f"\nUpdated last_search_date to {maxdate} in database.")
