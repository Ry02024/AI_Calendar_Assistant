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

## 知識ファイル（knowledge/ ディレクトリ）について
- `knowledge/` ディレクトリ内のテキストファイル（例: `user_profile_life_pattern.txt`）は、AIアシスタントの知識として自動的にプロンプトに注入されます。
- 生活パターンやユーザープロファイルなど、AIに反映したい情報を自由に追加できます。
- 個人情報を含む場合は `.gitignore` で `knowledge/*` を管理対象外にしています（リポジトリには含まれません）。

### 例: user_profile_life_pattern.txt
```
【全体的な印象】
知的好奇心と探求心が非常に強く、テクノロジー、学術、エンターテイメント、社会問題など、多岐にわたる分野に関心を持っているアクティブな人物像。日常生活にもしっかりと向き合い、情報収集や問題解決を積極的に行っている。東京都江東区とその周辺に居住している可能性が高い。

【生活パターン例（推測）】
■日時パターン（平日例）
7:00-8:00 起床・朝食／8:00-9:00 通勤／9:00-12:00 仕事・学習／12:00-13:00 昼食／13:00-17:00 仕事・学習／17:00-18:00 退勤・帰宅／18:00-19:00 夕食／19:00-22:00 自由時間（エンタメ・趣味）／22:00-23:00 リラックス・就寝準備／23:00 就寝
■週次パターン
平日: 上記繰り返し。土曜: 午前趣味・午後外出・夜外食や自宅エンタメ。日曜: 午前家事・午後学習や散策・夜準備。
■月次パターン
月初: サブスクや明細確認、新コンテンツ探し。月中: イベントや新店検索。月末: 振り返り・翌月計画・まとめ買い。
■年次パターン
年初: 目標設定・初売り。春: 外出増。夏: 自宅時間増・季節イベント。秋: 趣味没頭・紅葉。年末: 特番視聴・大掃除・準備。
```

## ディレクトリ構成例
```
AI_Calendar_Assistant/
├── main.py
├── requirements.txt
├── .env
├── .gitignore
├── credentials.json (非公開)
├── token.json (非公開)
├── config.py
├── knowledge/
│   └── user_profile_life_pattern.txt
├── src/
│   └── calendar_agent/
│       ├── agent.py
│       ├── tools.py
│       ├── knowledge_handler.py
│       └── __init__.py
└── ...
```

---

ご質問・要望はIssueまたはPRでどうぞ！
