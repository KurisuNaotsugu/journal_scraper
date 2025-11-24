# gemini_operator.py
import os
import json
import re
import google.genai as genai

PROMPT_TEMPLATE = """
次のアブストラクトから以下の5項目を抽出し、各項目に 2-3 文で要約してください。

出力は必ず **純粋な JSON（コードブロック不可・前後の説明文禁止）** とします。

出力形式:
{{
  "目的": "",
  "サンプル": "",
  "解析手法": "",
  "結果": "",
  "結論": ""
}}

アブストラクト内に記載がない項目は "記載なし" としてください。

【アブストラクト】
{abstract}
"""

def build_prompt(template: str, **kwargs) -> str:
    """指定されたテンプレート文字列の {var} を動的に置換する

    Args:
        template (str): プロンプトのテンプレート
        **kwargs: テンプレートに埋め込む変数

    Returns:
        str: 完成したプロンプト
    """
    return template.format(**kwargs)


def request_gemini_json(gemini_client, prompt: str, model: str="gemini-2.5-flash"):
    """Geminiにプロンプトを送り、レスポンスからJSONを抽出して返す。

    Args:
        gemini_client: Geminiクライアントインスタンス
        prompt (str): APIへ送るプロンプト
        model (str, optional): 使用するモデル (Defaults to "gemini-2.5-flash")

    Returns:
        dict: Geminiレスポンスから抽出したJSON。抽出できない場合は:
              {
                "error": True,
                "raw_response": "元のレスポンス文字列"
              }
    """
    try:
        response = gemini_client.models.generate_content(model=model, contents=prompt)
        raw = response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        return {"error": True, "message": f"Gemini API error: {str(e)}"}

    parsed = extract_json_from_gemini(raw)

    if parsed is None:
        return {
            "error": True,
            "raw_response": raw
        }

    return parsed


def summarize_dict(gemini_client, data_dict):
    """辞書形式のデータを順に要約して同一キーの辞書形式で返す
    Args:
        gemini_client: Geminiクライアントインスタンス
        data_dict (dict): {key: text}形式の辞書データ
    Returns:
        dict: {key: summary}形式の要約辞書
    """
    summaries = {}

    for key, text in data_dict.items():
        summaries[key] = request_gemini_json(gemini_client, text)

    return summaries

def extract_json_from_gemini(text: str):
    """Geminiの出力からJSONを安全に抽出してdictで返す。
    Geminiの出力は必ずしも純粋なJSONではないため、複数のパターンに対応するためのフォーマット検出

    Args:
        text (str): Geminiの出力テキスト
    Returns:
        dict or None: 抽出したJSONデータ、または None
    """

    if not text:
        return None

    # 1) ```json ... ``` のようなコードブロックがある場合
    codeblock_match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if codeblock_match:
        try:
            return json.loads(codeblock_match.group(1).strip())
        except:
            pass

    # 2) 通常の { ... } の JSON を正規表現で抽出
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except:
            pass

    # 3) fallback：最初の { から最後の } までを抽出
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except:
        return None



# ---------------------------
# ここからメイン関数
# ---------------------------
def main():
    """メイン関数"""

    # Gemini client の生成
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # 要約したいデータ（デモ）
    sample_data = {
        "paper1": "これはサンプルのアブストラクトです。機械学習によって□□を分析し...",
        "paper2": "この論文では新しいアルゴリズムを提案し、従来手法よりも△△の精度が向上した...",
        "paper3": "",
    }

    summaries = {}

    for key, abstract in sample_data.items():

        if not abstract.strip():
            summaries[key] = "アブストラクトなし"
            continue

        # プロンプト生成（汎用ビルダーを使用）
        prompt = build_prompt(
            PROMPT_TEMPLATE ,
            abstract=abstract
        )

        # Gemini で処理
        summary = request_gemini_json(gemini_client, prompt)
        summaries[key] = summary

    # 結果出力
    print("\n=== 抽出結果（構造化要約） ===")
    for key, summary in summaries.items():
        print(f"\n[{key}]")
        print(summary)

if __name__ == "__main__":
    main()
