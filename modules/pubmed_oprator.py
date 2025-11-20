import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta
from typing import List, Optional

def calculate_date_range(mindate=None, maxdate=None, days=None): 
    """ 検索期間の計算
    
    - mindateとmaxdateを指定→その期間を使用
    - daysのみ指定:maxdateを今日として、そこからdays分遡る
    - mindateとdaysを指定:maxdateをmindate + daysとして決定
    - いずれも指定:今日から過去1週間とする

    Args:
        mindate: 'YYYY/MM/DD' 形式の文字列 または None 
        maxdate: 'YYYY/MM/DD' 形式の文字列 または None 
        days: int 日数, maxdateから遡る期間
    Returns: 
        (mindate_str, maxdate_str) の文字列タプル
    """
    # Get today's date
    today = datetime.today()

    # Determine maxdate
    if maxdate:
        max_date_obj = datetime.strptime(maxdate, '%Y/%m/%d')
    else:
        max_date_obj = today

    # Determine mindate
    if mindate:
        mindate_obj = datetime.strptime(mindate, '%Y/%m/%d')
    elif days:
        mindate_obj = max_date_obj - timedelta(days=days)
    else:
        mindate_obj = max_date_obj - timedelta(days=7) # デフォルト1週間

    # Convert back to string format
    mindate_str = mindate_obj.strftime('%Y/%m/%d')
    maxdate_str = max_date_obj.strftime('%Y/%m/%d')

    return mindate_str, maxdate_str

def fetch_esearch(keywords:list[str], min_date, max_date, retmax=100):
    '''PubMedでキーワードと日付に基づいて論文IDを検索する関数
    Args:
        keywords (list[str]): 検索キーワードのリスト
        min_date (str): 検索日付 (YYYY/MM/DD)
        Max_date (str): 検索日付 (YYYY/MM/DD)
        retmax (int, optional): 取得する最大論文数. Defaults to 100.
    Returns:
        list[str]: 検索で取得した論文IDのリスト
    '''
    search_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    query = ' AND '.join(keywords)

    search_params = {
        'db': 'pubmed',
        'term': query,
        'mindate': min_date,
        'maxdate': max_date,
        'retmode': 'xml',
        'retmax': retmax
    }
    response = requests.get(search_url, params=search_params)
    pmids = re.findall(r'<Id>(\d+)</Id>', response.text)
    return pmids

def fetch_esummary(pmids:list[str]) -> str:
    '''PubMedで論文IDに基づいて論文情報を取得する関数
    Args:
        ids (list[str]): 論文IDのリスト
    Returns:
        str: 論文情報を含むXML文字列
    '''
    if not pmids:
        return 'No results found.'

    summary_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
    summary_params = {
        'db': 'pubmed',
        'id': ','.join(pmids),
        'retmode': 'xml'
    }

    response = requests.get(summary_url, params=summary_params)
    return response.text

def parse_esummary_xml(xml_data:str) -> list[dict]:
    """ PubMedのXMLデータから論文情報を抽出する関数

    Args:
        xml_data (_type_): fetch_abstract関数で取得したXMLデータ

    Returns:
        list[dict]: 論文情報のリスト（各論文は辞書形式でタイトル、DOI、アブストラクトを含む）
    """
    root = ET.fromstring(xml_data)
    esummary = []
    for docsum in root.findall('.//DocSum'):
        title = docsum.find('Item[@Name="Title"]').text
        pubdate = docsum.find('Item[@Name="PubDate"]').text
        pmid = docsum.find('Item[@Name="ArticleIds"]/Item[@Name="pubmed"]').text

        doi_raw = docsum.find('Item[@Name="ELocationID"]').text if docsum.find('Item[@Name="ELocationID"]') is not None else 'N/A'
        doi = extract_doi(doi_raw)
        url = doi_to_url(doi)

        esummary.append({'pmid':pmid, 'Title': title, 'pubdate':pubdate, 'URL': url})
    return esummary

def extract_doi(text: str) -> str:
    """
    混在した ELocationID 文字列から DOI のみを抽出する関数。
    DOI がなければ 'N/A' を返す。
    """
    if not text:
        return "N/A"
    
    # DOI の一般的な正規表現（10. から始まる）
    doi_pattern = r"(10\.\d{4,9}/[^\s]+)"
    match = re.search(doi_pattern, text)

    return match.group(1) if match else "N/A"

def doi_to_url(doi: str) -> str:
    """
    DOI からリンク URL を生成する。
    DOI が無効または 'N/A' の場合は空文字を返す。
    """
    if not doi or doi == "N/A":
        return ""
    return f"https://doi.org/{doi}"


def fetch_eFetch(pmids: List[str]) -> dict[str, str]:
    """ PubMedから論文のアブストラクトを取得する関数
    Args:
        pmids (list[str]): 論文IDのリスト
    Returns:
        dict[str, str]: {pmid: abstract_text}
    """
    if not pmids:
        return {}

    efetch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
        "db=pubmed&retmode=xml&id=" + ",".join(pmids)
    )

    response = requests.get(efetch_url)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    abstracts = {}

    for article in root.findall(".//PubmedArticle"):
        pmid_elem = article.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else None

        abstract_elem = article.find(".//Abstract/AbstractText")
        abstract_text = (
            abstract_elem.text if abstract_elem is not None else "N/A"
        )

        if pmid:
            abstracts[pmid] = abstract_text

    return abstracts


# メイン処理 (ユーザー入力のキーワードで直近1週間の論文を取得)
if __name__ == '__main__':
    
    keywords_input = input('検索キーワードをカンマ区切りで入力してください: ')
    keywords = [kw.strip() for kw in keywords_input.split(',')]

    # 日付範囲の計算（デフォルトで直近1週間）
    mindate, maxdate = calculate_date_range()

    print(f'検索期間: {mindate} ～ {maxdate}')
    print(f'検索キーワード: {keywords}')

    # 論文IDを取得
    pmids = fetch_esearch(keywords, mindate, maxdate)
    if not pmids:
        print('該当する論文はありませんでした。')
    else:
        print(f'{len(pmids)} 件の論文を取得しました。')

        # 論文情報を取得
        esumary_xml = fetch_esummary(pmids)
        esumary_dict = parse_esummary_xml(esumary_xml)
        # アブストラクトを取得
        abstracts_dict = fetch_eFetch(pmids)

        # 論文情報を表示
        for i, paper in enumerate(esumary_dict, start=1):
            pmid = paper['pmid']
            abstract = abstracts_dict.get(pmid, "N/A")

            print(f"\n=== 論文 {i} ===")
            print(f"PMID: {pmid}")
            print(f"タイトル: {paper['Title']}")
            print(f"出版日: {paper['pubdate']}")
            print(f"URL: {paper['URL']}")
            print(f"アブストラクト: {abstract}")