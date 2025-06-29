# Gemini Multi-Agent Discussion System

複数のGemini 2.5 Flash Liteエージェントが話し合いを行い、Gemini 2.5 Flashが内容をまとめるシステムです。

## セットアップ

1. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

2. Gemini API キーを設定:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

## 使用方法

### インタラクティブ版（推奨）
```bash
python scripts/interactive_discussion.py
```
設定を対話的に選択して議論を実行

### シンプル版
```bash
python scripts/run_discussion.py
```
プリセットされた設定で即座に実行

### デモ版
```bash
python scripts/demo_discussion.py
```
3つのカテゴリーで連続デモを実行

### ジャンル混合デモ
```bash
python scripts/mixed_mode_demo.py
```
全カテゴリーからランダム選択したエージェントでの議論

## 機能

- **多様なエージェント**: 6カテゴリー、42種類の豊富なエージェントプリセット
- **柔軟な参加者設定**: 参加者数とラウンド数のカスタマイズ（2-7人、1-10回）
- **ジャンル混合モード**: 全42種類からランダム選択で異分野コラボレーション
- **文字数制限**: エージェント発言（50-500文字）と要約（500-3000文字）の制限設定
- **ランダム選択**: 空欄入力で自動選択機能
- **高品質な議論**: `models/gemini-2.5-flash-lite-preview-06-17`で効率的な議論、`models/gemini-2.5-flash`で高品質な要約
- **完全日本語対応**: エージェントの発言も要約も日本語
- **結果保存**: 議論の内容をJSONファイルでresultsディレクトリに保存

## エージェントカテゴリー

### 教育（7人）
教師、研究者、保護者、校長、学生、IT専門家、教育心理学者

### ビジネス（7人）  
CEO、部長、CFO、PM、アナリスト、CTO、営業

### 社会問題（7人）
政治家、弁護士、医師、記者、NPO、社会学者、市民

### 技術（7人）
エンジニア、研究者、デザイナー、セキュリティ、PM、アーキテクト、データサイエンティスト

### 環境・持続可能性（7人）
環境学者、活動家、企業経営者、政策担当者、消費者、再エネ研究者、農家

### 医療・健康（7人）
臨床医、研究者、看護師、薬剤師、患者、保険担当者、公衆衛生専門家

## ディレクトリ構造

```
discussion/
├── scripts/
│   ├── demo_discussion.py           # カテゴリー別デモ
│   ├── interactive_discussion.py    # インタラクティブ版
│   ├── mixed_mode_demo.py           # ジャンル混合デモ
│   └── run_discussion.py            # シンプル実行版
├── src/
│   ├── agent_classes.py             # エージェントクラス定義
│   ├── agent_manager.py             # エージェント管理システム
│   ├── agent_presets.py             # 42種類のエージェントプリセット
│   ├── discussion_system.py         # メインシステム
│   └── ... (その他のsrcファイル)
├── tests/
│   ├── test_discussion.py           # 基本テスト
│   └── test_enhanced_discussion.py  # 拡張機能テスト
├── requirements.txt                 # 依存パッケージ
├── README.md                        # このファイル
└── results/                         # 議論結果保存ディレクトリ
    ├── discussion_*.json            # 議論ログ
    ├── demo_*.json                  # デモ結果
    └── test_*.json                  # テスト結果
```

## 出力

- リアルタイムでの議論内容表示
- 議論終了後の詳細な要約
- JSON形式での議論ログ保存（resultsディレクトリ）
- 実行統計情報（メッセージ数、実行時間、文字数チェックなど）
