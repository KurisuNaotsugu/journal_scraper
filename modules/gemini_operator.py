# gemini_operator.py
import os
import google.genai as genai

PROMPT_TEMPLATE = """
次のアブストラクトから以下の5つを抽出してください：
- 背景
- 目的
- 方法
- 結果
- 結論

アブストラクト内に記載がない場合は「記載なし」としてください。

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


def summarize_text(gemini_client, prompt, model: str="gemini-2.5-flash"):
    """任意のテキストを箇条書きで要約
    Args:
        gemini_client: Geminiクライアントインスタンス
        prompt (str): 要約したいテキスト
        model (str, optional): 使用するGeminiモデル. Defaults to "gemini-2.5-flash".
    Returns:
        str: 要約結果のテキスト
    """
    try:
        response = gemini_client.models.generate_content(model=model, contents=prompt)
        return response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        return f"要約生成に失敗: {str(e)}"


def summarize_dict(gemini_client, data_dict):
    """辞書形式のデータを要約する関数
    Args:
        gemini_client: Geminiクライアントインスタンス
        data_dict (dict): {key: text}形式の辞書データ
    Returns:
        dict: {key: summary}形式の要約辞書
    """
    summaries = {}

    for key, text in data_dict.items():
        summaries[key] = summarize_text(gemini_client, text)

    return summaries



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
        summary = summarize_text(gemini_client, prompt)
        summaries[key] = summary

    # 結果出力
    print("\n=== 抽出結果（構造化要約） ===")
    for key, summary in summaries.items():
        print(f"\n[{key}]")
        print(summary)

if __name__ == "__main__":
    main()
