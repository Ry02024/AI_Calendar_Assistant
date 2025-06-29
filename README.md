# AI Calendar Assistant

日本語で自然に「予定の追加・確認・削除・編集」ができるGoogleカレンダーAIアシスタントです。

## 特徴
- Gemini/Google Generative AIとGoogle Calendar APIを連携
- Function Calling非対応環境でもAI返答のJSONをパースしカレンダー操作
- 予定の追加・確認・削除・編集を日本語で柔軟に対話
- 期間や予定の表示も日本語で分かりやすく
- 複数候補時は「詳細」コマンドでIDや説明・場所も確認可能

## セットアップ
1. **Google CloudでAPI認証情報を作成し、`credentials.json`を配置**
2. `requirements.txt`の依存パッケージをインストール
   ```sh
   pip install -r requirements.txt
   ```
3. `.env`にGemini APIキーなどを記載
4. 初回実行時はGoogle認証フローが表示されます

## 使い方
```sh
python main.py
```
- 例: 「6月28日の土曜出勤を削除」「今年の予定を確認」「晩餐の予定の詳細にオーガニック、場所は帝国ホテルを追記」など
- 「詳細」と入力すると直前の候補リストの詳細を表示
- 「終了」で終了

## 注意
- `token.json`や`credentials.json`は.gitignoreで管理し、公開しないでください
- Google Calendar APIの利用にはGoogleアカウントが必要です

## ディレクトリ構成例
```
AI_Calendar_Assistant/
├── main.py
├── requirements.txt
├── .env
├── .gitignore
├── credentials.json (非公開)
├── token.json (非公開)
└── src/
    └── calendar_agent/
        ├── agent.py
        └── tools.py
```

---

ご質問・要望はIssueまたはPRでどうぞ！
