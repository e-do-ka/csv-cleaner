from groq import Groq
import os
import json
import pandas as pd

client = Groq(api_key=os.environ["AI_API_KEY"])

def clean_csv(df: pd.DataFrame) -> dict:
    csv_text = df.to_csv(index=False)
    missing = df.isnull().sum().to_dict()

    prompt = f"""
あなたはデータクレンジングの専門家です。
以下のCSVデータを分析し、必ず下記のJSON形式のみで回答してください。
余計な説明やマークダウンは一切不要です。JSONのみ返してください。

【CSVデータ】
{csv_text}

【欠損値情報】
{missing}

分析時に必ず以下を確認してください：
- メールアドレスの形式チェック（@の前後が必要）
- 日付フォーマットの統一（YYYY-MM-DD形式に統一）
- 数値列の異常値（マイナス値、極端に大きい値）
- 計算列の整合性チェック（例：合計=数量×単価）
- カテゴリ列の不正値（想定外のステータス値など）
- 欠損値の補完方法

anomaliesの検出例：
- row:2, column:メールアドレス, value:"suzuki@", reason:"@の後ろがない不正なメールアドレス", fix:"要確認"
- row:4, column:注文日, value:"2024/01/18", reason:"日付フォーマットが他と異なる(スラッシュ区切り)", fix:"2024-01-18"
- row:7, column:数量, value:"-1", reason:"数量が負の値", fix:"0または要確認"
- row:8, column:注文日, value:"20240122", reason:"日付フォーマットが他と異なる(区切りなし)", fix:"2024-01-22"
- row:9, column:合計金額, value:"99999", reason:"数量1×単価35000=35000のはずが99999になっている", fix:"35000"
必ずすべての異常値を検出してanomaliesに含めてください。

以下のJSON形式で返してください：
{{
  "summary": "データ全体の概要と主な問題点を3文で",
  "columns": [
    {{
      "name": "列名",
      "type": "データ型",
      "issues": "問題点（なければ「なし」）",
      "suggestion": "対処法（なければ「なし」）"
    }}
  ],
  "missing_values": [
    {{
      "column": "列名",
      "count": 欠損数,
      "pct": 欠損率,
      "action": "推奨対処法"
    }}
  ],
  "anomalies": [
    {{
      "row": 行番号（1始まり）,
      "column": "列名",
      "value": "問題のある値（文字列として）",
      "reason": "問題の理由",
      "fix": "修正後の値（文字列として）"
    }}
  ],
  "overall_score": 品質スコア0〜100の整数,
  "cleaned_csv": "クレンジング済みCSV文字列（全問題を修正したもの）"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "あなたはデータクレンジングの専門家です。必ずJSONのみで回答します。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=4096
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)