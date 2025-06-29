#!/usr/bin/env python3
"""
Results Management System for Discussion Logs
"""

import os
import json
import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class DiscussionSummary:
    """議論の要約情報"""
    timestamp: int
    filename: str
    topic: str
    agents: List[str]
    categories: List[str]
    rounds: int
    total_messages: int
    summary_preview: str
    file_path: str


class ResultsManager:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        self.ensure_results_dir()
    
    def ensure_results_dir(self):
        """resultsディレクトリの存在確認と作成"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    def get_all_discussions(self) -> List[DiscussionSummary]:
        """全ての議論ファイルの要約を取得"""
        discussions = []
        
        for filename in os.listdir(self.results_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.results_dir, filename)
                try:
                    summary = self._load_discussion_summary(file_path, filename)
                    if summary:
                        discussions.append(summary)
                except Exception as e:
                    print(f"Warning: Failed to load {filename}: {e}")
        
        # タイムスタンプでソート（新しい順）
        discussions.sort(key=lambda x: x.timestamp, reverse=True)
        return discussions
    
    def _load_discussion_summary(self, file_path: str, filename: str) -> Optional[DiscussionSummary]:
        """議論ファイルから要約情報を抽出"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 基本情報の抽出
            topic = data.get('topic', 'Unknown Topic')
            agents_data = data.get('agents', [])
            messages = data.get('messages', [])
            
            # エージェント名とカテゴリーの抽出
            agent_names = [agent.get('name', 'Unknown') for agent in agents_data]
            categories = list(set([self._get_agent_category(agent.get('name', '')) for agent in agents_data]))
            categories = [cat for cat in categories if cat != 'Unknown']
            
            # ラウンド数の計算（システムメッセージを除く）
            non_system_messages = [msg for msg in messages if msg.get('agent_name') != 'System']
            rounds = len(non_system_messages) // len(agent_names) if agent_names else 0
            
            # 要約のプレビュー（最初の100文字）
            summary_preview = self._extract_summary_preview(data)
            
            # タイムスタンプの抽出
            timestamp = self._extract_timestamp(filename, messages)
            
            return DiscussionSummary(
                timestamp=timestamp,
                filename=filename,
                topic=topic,
                agents=agent_names,
                categories=categories,
                rounds=rounds,
                total_messages=len(messages),
                summary_preview=summary_preview,
                file_path=file_path
            )
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            return None
    
    def _get_agent_category(self, agent_name: str) -> str:
        """エージェント名からカテゴリーを推定"""
        from agent_presets import AGENT_PRESETS
        
        for category, agents in AGENT_PRESETS.items():
            if any(agent.name == agent_name for agent in agents):
                return category
        return 'Unknown'
    
    def _extract_summary_preview(self, data: Dict) -> str:
        """要約のプレビューを抽出"""
        # 要約情報がある場合は最初の100文字を取得
        if 'summary' in data:
            summary = data['summary']
            return summary[:100] + "..." if len(summary) > 100 else summary
        
        # メッセージから推測
        messages = data.get('messages', [])
        if messages:
            first_content = ""
            for msg in messages:
                if msg.get('agent_name') != 'System':
                    first_content = msg.get('content', '')
                    break
            return first_content[:100] + "..." if len(first_content) > 100 else first_content
        
        return "No summary available"
    
    def _extract_timestamp(self, filename: str, messages: List[Dict]) -> int:
        """タイムスタンプを抽出"""
        # ファイル名から抽出を試行
        timestamp_match = re.search(r'(\d{10})', filename)
        if timestamp_match:
            return int(timestamp_match.group(1))
        
        # メッセージから最初のタイムスタンプを使用
        if messages:
            for msg in messages:
                if 'timestamp' in msg:
                    return int(msg['timestamp'])
        
        # フォールバック：ファイル作成時刻
        return int(os.path.getctime(os.path.join(self.results_dir, filename)))
    
    def search_discussions(self, query: str) -> List[DiscussionSummary]:
        """議論を検索"""
        all_discussions = self.get_all_discussions()
        results = []
        
        query_lower = query.lower()
        
        for discussion in all_discussions:
            # トピック、エージェント名、カテゴリー、要約プレビューで検索
            searchable_text = (
                discussion.topic.lower() + " " +
                " ".join(discussion.agents).lower() + " " +
                " ".join(discussion.categories).lower() + " " +
                discussion.summary_preview.lower()
            )
            
            if query_lower in searchable_text:
                results.append(discussion)
        
        return results
    
    def filter_by_category(self, category: str) -> List[DiscussionSummary]:
        """カテゴリーで議論をフィルタ"""
        all_discussions = self.get_all_discussions()
        return [d for d in all_discussions if category in d.categories]
    
    def filter_by_agent(self, agent_name: str) -> List[DiscussionSummary]:
        """エージェント名で議論をフィルタ"""
        all_discussions = self.get_all_discussions()
        return [d for d in all_discussions if agent_name in d.agents]
    
    def filter_by_date_range(self, start_date: Optional[datetime.date] = None, 
                           end_date: Optional[datetime.date] = None) -> List[DiscussionSummary]:
        """日付範囲で議論をフィルタ"""
        all_discussions = self.get_all_discussions()
        results = []
        
        for discussion in all_discussions:
            discussion_date = datetime.date.fromtimestamp(discussion.timestamp)
            
            if start_date and discussion_date < start_date:
                continue
            if end_date and discussion_date > end_date:
                continue
            
            results.append(discussion)
        
        return results
    
    def get_discussion_details(self, filename: str) -> Optional[Dict]:
        """特定の議論の詳細を取得"""
        file_path = os.path.join(self.results_dir, filename)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None
    
    def export_summary_html(self, output_file: str = "results/discussion_index.html"):
        """議論の一覧をHTMLファイルにエクスポート"""
        discussions = self.get_all_discussions()
        
        html_content = self._generate_html_index(discussions)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML index exported to: {output_file}")
    
    def _generate_html_index(self, discussions: List[DiscussionSummary]) -> str:
        """HTML インデックスを生成"""
        html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Discussion System - 議論ログ一覧</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 8px; }
        .stat-item { text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #4CAF50; }
        .discussion-card { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; background: #fafafa; }
        .discussion-card:hover { background: #f0f0f0; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
        .topic { font-size: 1.2em; font-weight: bold; color: #333; margin-bottom: 8px; }
        .meta { color: #666; font-size: 0.9em; margin: 5px 0; }
        .agents { margin: 8px 0; }
        .agent-tag { display: inline-block; background: #e3f2fd; color: #1976d2; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 0.8em; }
        .category-tag { display: inline-block; background: #e8f5e8; color: #2e7d32; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 0.8em; }
        .preview { margin-top: 10px; font-style: italic; color: #555; }
        .search-box { width: 100%; padding: 10px; margin: 20px 0; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        .filter-buttons { margin: 10px 0; }
        .filter-btn { padding: 5px 15px; margin: 5px; border: 1px solid #4CAF50; background: white; color: #4CAF50; border-radius: 20px; cursor: pointer; }
        .filter-btn:hover, .filter-btn.active { background: #4CAF50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Gemini Discussion System - 議論ログ一覧</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_discussions}</div>
                <div>総議論数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{total_categories}</div>
                <div>使用カテゴリー数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{total_agents}</div>
                <div>参加エージェント数</div>
            </div>
        </div>
        
        <input type="text" class="search-box" id="searchBox" placeholder="議論を検索... (トピック、エージェント名、カテゴリー)" onkeyup="filterDiscussions()">
        
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterByCategory('all')">全て</button>
            {category_buttons}
        </div>
        
        <div id="discussionList">
            {discussion_cards}
        </div>
    </div>
    
    <script>
        function filterDiscussions() {{
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const cards = document.querySelectorAll('.discussion-card');
            
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(searchTerm) ? 'block' : 'none';
            }});
        }}
        
        function filterByCategory(category) {{
            const cards = document.querySelectorAll('.discussion-card');
            const buttons = document.querySelectorAll('.filter-btn');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            cards.forEach(card => {{
                if (category === 'all') {{
                    card.style.display = 'block';
                }} else {{
                    const categories = card.dataset.categories;
                    card.style.display = categories.includes(category) ? 'block' : 'none';
                }}
            }});
        }}
    </script>
</body>
</html>"""
        
        # 統計情報の計算
        total_discussions = len(discussions)
        all_categories = set()
        all_agents = set()
        
        for d in discussions:
            all_categories.update(d.categories)
            all_agents.update(d.agents)
        
        # カテゴリーボタンの生成
        category_buttons = ""
        for category in sorted(all_categories):
            if category != 'Unknown':
                category_buttons += f'<button class="filter-btn" onclick="filterByCategory(\'{category}\')">{category}</button>'
        
        # 議論カードの生成
        discussion_cards = ""
        for d in discussions:
            date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%Y-%m-%d %H:%M')
            
            agent_tags = "".join([f'<span class="agent-tag">{agent}</span>' for agent in d.agents])
            category_tags = "".join([f'<span class="category-tag">{cat}</span>' for cat in d.categories if cat != 'Unknown'])
            
            discussion_cards += f"""
            <div class="discussion-card" data-categories="{','.join(d.categories)}">
                <div class="topic">{d.topic}</div>
                <div class="meta">📅 {date_str} | 🔄 {d.rounds}ラウンド | 💬 {d.total_messages}メッセージ | 📁 {d.filename}</div>
                <div class="agents">{agent_tags}</div>
                <div class="categories">{category_tags}</div>
                <div class="preview">{d.summary_preview}</div>
            </div>"""
        
        return html.format(
            total_discussions=total_discussions,
            total_categories=len(all_categories),
            total_agents=len(all_agents),
            category_buttons=category_buttons,
            discussion_cards=discussion_cards
        )
    
    def print_summary(self):
        """議論の要約を表示"""
        discussions = self.get_all_discussions()
        
        print(f"\n📊 Gemini Discussion System - Results Summary")
        print("=" * 60)
        print(f"総議論数: {len(discussions)}")
        
        if discussions:
            # カテゴリー統計
            all_categories = {}
            for d in discussions:
                for cat in d.categories:
                    if cat != 'Unknown':
                        all_categories[cat] = all_categories.get(cat, 0) + 1
            
            print(f"\nカテゴリー別統計:")
            for cat, count in sorted(all_categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count}回")
            
            # 最近の議論
            print(f"\n最近の議論 (最新5件):")
            for i, d in enumerate(discussions[:5], 1):
                date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%m-%d %H:%M')
                print(f"  {i}. [{date_str}] {d.topic}")
                print(f"     参加者: {', '.join(d.agents)}")
        
        print("=" * 60)


def main():
    """メインメニュー"""
    manager = ResultsManager()
    
    while True:
        print(f"\n🤖 Gemini Discussion System - Results Manager")
        print("1. 全議論を表示")
        print("2. 議論を検索")
        print("3. カテゴリーで絞り込み")
        print("4. エージェントで絞り込み")
        print("5. 日付で絞り込み")
        print("6. 詳細を表示")
        print("7. HTML一覧を生成")
        print("8. 要約統計を表示")
        print("0. 終了")
        
        try:
            choice = input("\n選択してください: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                show_all_discussions(manager)
            elif choice == "2":
                search_discussions(manager)
            elif choice == "3":
                filter_by_category(manager)
            elif choice == "4":
                filter_by_agent(manager)
            elif choice == "5":
                filter_by_date(manager)
            elif choice == "6":
                show_discussion_details(manager)
            elif choice == "7":
                manager.export_summary_html()
            elif choice == "8":
                manager.print_summary()
            else:
                print("無効な選択です。")
        
        except KeyboardInterrupt:
            print("\n\n終了します。")
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")


def show_all_discussions(manager: ResultsManager):
    """全議論を表示"""
    discussions = manager.get_all_discussions()
    
    if not discussions:
        print("議論ログが見つかりません。")
        return
    
    print(f"\n📋 全議論一覧 ({len(discussions)}件)")
    print("-" * 80)
    
    for i, d in enumerate(discussions, 1):
        date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%Y-%m-%d %H:%M')
        print(f"{i:2d}. [{date_str}] {d.topic}")
        print(f"    参加者: {', '.join(d.agents)} ({', '.join(d.categories)})")
        print(f"    {d.rounds}ラウンド, {d.total_messages}メッセージ - {d.filename}")
        print()


def search_discussions(manager: ResultsManager):
    """議論を検索"""
    query = input("検索キーワードを入力: ").strip()
    if not query:
        return
    
    results = manager.search_discussions(query)
    
    if not results:
        print(f"'{query}' に関する議論が見つかりませんでした。")
        return
    
    print(f"\n🔍 検索結果: '{query}' ({len(results)}件)")
    print("-" * 60)
    
    for i, d in enumerate(results, 1):
        date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%Y-%m-%d %H:%M')
        print(f"{i}. [{date_str}] {d.topic}")
        print(f"   参加者: {', '.join(d.agents)}")
        print(f"   {d.summary_preview}")
        print()


def filter_by_category(manager: ResultsManager):
    """カテゴリーで絞り込み"""
    # 利用可能なカテゴリーを表示
    discussions = manager.get_all_discussions()
    categories = set()
    for d in discussions:
        categories.update(d.categories)
    categories.discard('Unknown')
    
    if not categories:
        print("利用可能なカテゴリーがありません。")
        return
    
    print("\n利用可能なカテゴリー:")
    for i, cat in enumerate(sorted(categories), 1):
        print(f"{i}. {cat}")
    
    try:
        choice = int(input("カテゴリー番号を選択: ")) - 1
        category_list = sorted(categories)
        if 0 <= choice < len(category_list):
            selected_category = category_list[choice]
            results = manager.filter_by_category(selected_category)
            
            print(f"\n📂 カテゴリー '{selected_category}' の議論 ({len(results)}件)")
            print("-" * 60)
            
            for i, d in enumerate(results, 1):
                date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%Y-%m-%d %H:%M')
                print(f"{i}. [{date_str}] {d.topic}")
                print(f"   参加者: {', '.join(d.agents)}")
                print()
        else:
            print("無効な選択です。")
    
    except ValueError:
        print("無効な入力です。")


def filter_by_agent(manager: ResultsManager):
    """エージェントで絞り込み"""
    agent_name = input("エージェント名を入力: ").strip()
    if not agent_name:
        return
    
    results = manager.filter_by_agent(agent_name)
    
    if not results:
        print(f"エージェント '{agent_name}' が参加した議論が見つかりませんでした。")
        return
    
    print(f"\n👤 エージェント '{agent_name}' の議論 ({len(results)}件)")
    print("-" * 60)
    
    for i, d in enumerate(results, 1):
        date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%Y-%m-%d %H:%M')
        print(f"{i}. [{date_str}] {d.topic}")
        print(f"   参加者: {', '.join(d.agents)}")
        print()


def filter_by_date(manager: ResultsManager):
    """日付で絞り込み"""
    print("日付範囲を指定してください（YYYY-MM-DD形式、空欄でスキップ）")
    
    start_input = input("開始日: ").strip()
    end_input = input("終了日: ").strip()
    
    start_date = None
    end_date = None
    
    try:
        if start_input:
            start_date = datetime.datetime.strptime(start_input, '%Y-%m-%d').date()
        if end_input:
            end_date = datetime.datetime.strptime(end_input, '%Y-%m-%d').date()
    except ValueError:
        print("無効な日付形式です。")
        return
    
    results = manager.filter_by_date_range(start_date, end_date)
    
    date_range_str = ""
    if start_date and end_date:
        date_range_str = f"{start_date} ～ {end_date}"
    elif start_date:
        date_range_str = f"{start_date} 以降"
    elif end_date:
        date_range_str = f"{end_date} 以前"
    else:
        date_range_str = "全期間"
    
    print(f"\n📅 日付範囲 '{date_range_str}' の議論 ({len(results)}件)")
    print("-" * 60)
    
    for i, d in enumerate(results, 1):
        date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%Y-%m-%d %H:%M')
        print(f"{i}. [{date_str}] {d.topic}")
        print(f"   参加者: {', '.join(d.agents)}")
        print()


def show_discussion_details(manager: ResultsManager):
    """議論の詳細を表示"""
    discussions = manager.get_all_discussions()
    
    if not discussions:
        print("議論ログが見つかりません。")
        return
    
    print("\n議論を選択してください:")
    for i, d in enumerate(discussions[:10], 1):  # 最新10件を表示
        date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%m-%d %H:%M')
        print(f"{i:2d}. [{date_str}] {d.topic}")
    
    try:
        choice = int(input("番号を選択: ")) - 1
        if 0 <= choice < min(10, len(discussions)):
            selected = discussions[choice]
            details = manager.get_discussion_details(selected.filename)
            
            if details:
                print(f"\n📋 議論詳細: {selected.topic}")
                print("=" * 60)
                print(f"日時: {datetime.datetime.fromtimestamp(selected.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"参加者: {', '.join(selected.agents)}")
                print(f"カテゴリー: {', '.join(selected.categories)}")
                print(f"ラウンド数: {selected.rounds}")
                print(f"メッセージ数: {selected.total_messages}")
                print(f"ファイル: {selected.filename}")
                print("\n" + "=" * 60)
                
                # メッセージの表示
                messages = details.get('messages', [])
                for msg in messages:
                    if msg.get('agent_name') == 'System':
                        continue
                    print(f"\n【{msg.get('agent_name', 'Unknown')}】")
                    print(msg.get('content', ''))
                
                print("\n" + "=" * 60)
            else:
                print("議論の詳細を読み込めませんでした。")
        else:
            print("無効な選択です。")
    
    except ValueError:
        print("無効な入力です。")


if __name__ == "__main__":
    main()