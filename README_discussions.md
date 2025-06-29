# 議論ログ管理システム

議論ログの検索・要約・管理を行うためのシステムです。

## ディレクトリ構造

```
results/
├── discussions/     # 整理された議論ログ
├── summaries/       # 議論の要約ファイル（JSON形式）
├── full_summaries/  # 生成された要約テキスト（テキスト形式）
├── archive/         # アーカイブ
└── [その他のデモファイル]
```

## 使用方法

### 1. 議論一覧を表示
```bash
python3 discussion_search.py list
```

### 2. 議論を検索
```bash
# 全体検索
python3 discussion_search.py search --query "生成AI"

# トピックのみ検索
python3 discussion_search.py search --query "レポート" --search-in topic

# 議論内容から検索
python3 discussion_search.py search --query "倫理" --search-in content

# エージェント名から検索
python3 discussion_search.py search --query "Dr. Tech" --search-in agents
```

### 3. 議論の詳細を表示
```bash
python3 discussion_search.py detail --filename "discussion_20250629_142947.json"
```

### 4. 議論ログを整理
```bash
python3 discussion_search.py organize
```

### 5. 生成された要約テキストを保存
```bash
# 基本的な保存
python3 discussion_search.py save-summary --summary-text "要約内容..."

# トピック付きで保存
python3 discussion_search.py save-summary --summary-text "要約内容..." --topic "AI利用について"

# 簡単保存（スクリプト使用）
python3 save_summary.py "要約内容..." "AI利用について"
```

### 6. 保存された要約の管理
```bash
# 要約一覧を表示
python3 discussion_search.py list-summaries

# 特定の要約を表示
python3 discussion_search.py show-summary --filename "summary_20250629_153045_AI利用について.txt"
```

## 機能

- **自動整理**: タイムスタンプベースのファイル名に変換
- **要約生成**: 各議論の要約を自動作成（全文保存）
- **検索機能**: トピック、内容、エージェント名での検索
- **詳細表示**: 議論の完全な内容を表示
- **動的エージェント管理**: JSONファイルでエージェントを追加・削除
- **拡張された制限**: 最大50人、100ラウンド、10000文字/発言まで対応

## エージェント管理

### エージェント一覧表示
```bash
python3 manage_agents.py stats                    # 統計情報
python3 manage_agents.py list-categories          # カテゴリ一覧
python3 manage_agents.py list-agents              # 全エージェント
python3 manage_agents.py list-agents --category "技術"  # 特定カテゴリ
```

### エージェント追加・削除
```bash
# エージェント追加
python3 manage_agents.py add-agent \
  --category "技術" \
  --name "新田AI専門家" \
  --role "AI研究開発者" \
  --personality "最新のAI技術トレンドに精通し、実用的な応用を重視する"

# エージェント削除
python3 manage_agents.py remove-agent --category "技術" --name "新田AI専門家"

# カテゴリ追加・削除
python3 manage_agents.py add-category --category "新カテゴリ"
python3 manage_agents.py remove-category --category "不要カテゴリ"
```

### エージェント検索
```bash
python3 manage_agents.py search --query "AI"      # AI関連エージェント検索
python3 manage_agents.py search --query "医療"    # 医療関連エージェント検索
```

### 対話モード
```bash
python3 manage_agents.py interactive              # 対話的にエージェント管理
python3 manage_agents.py                          # （引数なしでも対話モード）
```

## 要約ファイルの構造

各議論に対して以下の情報を含む要約が作成されます：

- ファイル名
- トピック
- 日時
- 参加エージェント
- メッセージ数
- 主要ポイント
- 最初と最後のメッセージ