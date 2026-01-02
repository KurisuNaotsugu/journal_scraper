# modules/search_executer.py

# Import libraries
import os
import sys
from pathlib import Path
from datetime import date
from typing import List

# Import DB repositories
from db.database import SessionLocal
from db.repositories.app_state import AppStateRepository
from db.repositories.search_config import SearchConfigRepository
from db.repositories.search_result import SearchResultRepository

# Import modules
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
import modules.gemini_operator as go
import modules.pubmed_operator as po


##############################################################################################################################
# ヘルパー関数群
##############################################################################################################################

def load_last_search_date():
    """DBから取得前回検索実行日を取得

    Returns:
        str: 前回検索実行日 (YYYY/MM/DD)
    """
    with SessionLocal() as session:
        repo = AppStateRepository(session)
        state = repo.get_or_create()
        return state.last_search_date

def update_search_date(new_date: str):
    """DBに検索実行日(last_search_date)を更新

    Args:
        new_date (str): 検索実行日 (YYYY/MM/DD) 
    """
    with SessionLocal() as session:
        repo = AppStateRepository(session)
        repo.update_last_search_date(new_date)
        session.commit()

def load_search_setting():
    """検索メタデータをDBから取得
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

##############################################################################################################################
# 論文検索と要約のメイン処理 
##############################################################################################################################

class PaperSearchError(Exception):
    """論文検索に関する基底例外"""
    pass

class NoPaperFoundError(PaperSearchError):
    pass

class TooManyResultsError(PaperSearchError):
    pass

def search_papers(keywords: List[str], mindate: str = None, maxdate: str = None, max_results: int = 30) -> tuple[dict, dict]:
    """PubMedから論文情報とアブストラクトを取得
    Args:
        keywords (List[str]): 検索キーワードのリスト
        mindate (str): 検索開始日 (YYYY/MM/DD). 
        maxdate (str): 検索終了日 (YYYY/MM/DD). 
        max_results (int): 最大取得論文数.

    Returns:
        esummary_list (dict)
        abstracts_dict (dict)
    """
    print("(search_parpers) 論文検索開始...")
    mindate, maxdate = po.calculate_date_range(mindate, maxdate)

    # 論文IDを検索
    pmids = po.fetch_esearch(keywords, mindate, maxdate)
    if not pmids:
        raise NoPaperFoundError("該当する論文はありませんでした。")

    if len(pmids) > max_results:
        raise TooManyResultsError(f"論文数が上限({max_results})を超えています: {len(pmids)} 件。検索キーワードを絞り込んで再検索してください")

    # 論文情報を取得
    esummary_xml = po.fetch_esummary(pmids)
    esummary_list = po.parse_esummary_xml(esummary_xml)
    print(f"{len(pmids)} 件の論文情報を取得しました。")

    # アブストラクトを取得
    abstracts_dict = po.fetch_eFetch(pmids)
    print(f"取得した論文のアブストラクトを取得しました。")

    return esummary_list, abstracts_dict


def summarize_abstracts(abstracts_dict: dict) -> dict[str, str]:
    """Gemini を使ってアブストラクトを要約

    Args:
        abstracts_dict (dict): {pmid: abstract} の辞書
    Returns:
        dict[str, str]: {pmid: summary} の辞書
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
    print(f"要約が完了しました。")

    return summaries

##############################################################################################################################
# 論文検索と要約の実行関数
##############################################################################################################################

class NoKeywordsError(PaperSearchError):
    pass

class TooManyResultsError(PaperSearchError):
    pass

class NoSettingsError(PaperSearchError):
    pass

def manual_search(search_meta_info: list, mindate: str, maxdate: str):
    """Flaskからマニュアルサーチする際のメイン処理

    Args;
        search_meta_info (list): 検索メタデータのリスト
        mindate (str): 検索開始日
        maxdate (str): 検索終了日 

    Returns:
        results (list): 各検索結果のリスト
    """
    print(f"(manual_search) 文献調査を開始します: 検索期間: {mindate} ～ {maxdate}")
    results = []
    for meta in search_meta_info:
        # 検索メタデータ取得
        search_title = meta.get("search_title", "Untitled search")
        keywords = meta.get("keywords", [])
        if not keywords:
            raise NoKeywordsError(f"{search_title}: keywords がありません。")
        print(f"'{search_title}' の検索を開始します(キーワード: {keywords})")
        
        # 論文検索
        esummary_list, abstracts_dict = search_papers(keywords, mindate, maxdate)
        search_period = f"{mindate}-{maxdate}".replace("/", "-")

        # 要約生成
        print(f"要約を生成します...")
        summaries = summarize_abstracts(abstracts_dict)

        # 出力データ構築
        print(f"出力データを構築します...")
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

    print(f"manual_searchの処理が完了しました。")
    return results

def run_weekly_search(mindate: str, maxdate: str):
    """CLIエントリーポイント
    - 指定された検索期間に基づいてPubmed検索を実行する。
    - 検索結果キーワードの取得および結果の保存はデータベース上に行う。

    Args:
        mindate (str): 検索開始日 (YYYY/MM/DD)
        maxdate (str): 検索終了日 (YYYY/MM/DD) 
    
    """
    # 検索期間処理
    if mindate is None:
        mindate = load_last_search_date()
    maxdate = maxdate or date.today().strftime("%Y/%m/%d")

    # 検索設定取得
    search_meta_info = load_search_setting()
    if not search_meta_info:
        raise NoSettingsError("検索設定が存在しません。DBに検索条件を追加してください。")

    # 検索と要約の実行
    results = manual_search(search_meta_info, mindate, maxdate)
    
    # DB更新
    save_search_results_to_db(results)
    print("Search results saved to database.")
    
    update_search_date(maxdate)
    print(f"Updated last_search_date to {maxdate} in database.")
