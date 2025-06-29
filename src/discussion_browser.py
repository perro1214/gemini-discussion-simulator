#!/usr/bin/env python3
"""
議論ログブラウザ - 過去の議論を検索・閲覧するためのツール
"""

import os
import json
import datetime
from typing import List, Dict, Any, Optional
from results_manager import ResultsManager, DiscussionSummary
import google.generativeai as genai


class DiscussionBrowser:
    def __init__(self, results_dir: str = "results"):
        self.manager = ResultsManager(results_dir)
        
        # Gemini API設定
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
            print("Warning: GEMINI_API_KEY not set. AI summary features will be disabled.")
    
    def generate_detailed_summary(self, discussion_data: Dict) -> str:
        """AIを使用して詳細な要約を生成"""
        if not self.model:
            return "AI要約機能は無効です（GEMINI_API_KEYが設定されていません）"
        
        try:
            # メッセージからコンテンツを抽出
            messages = discussion_data.get('messages', [])
            content_parts = []
            
            for msg in messages:
                if msg.get('agent_name') != 'System':
                    content_parts.append(f"【{msg.get('agent_name')}】: {msg.get('content', '')}")
            
            discussion_text = "\n".join(content_parts)
            
            prompt = f"""
以下の議論ログを要約してください。日本語で回答してください。

議論トピック: {discussion_data.get('topic', 'Unknown')}

議論内容:
{discussion_text}

以下の形式で要約してください：
1. 議論の概要
2. 主要な論点
3. 各参加者の立場
4. 議論の結論・合意点
5. 残された課題

要約は500-1000文字程度でお願いします。
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"AI要約生成エラー: {str(e)}"
    
    def search_with_ai(self, query: str) -> List[Dict]:
        """AI検索機能 - クエリに最も関連する議論を見つける"""
        discussions = self.manager.get_all_discussions()
        results = []
        
        for discussion in discussions:
            # 基本検索も実行
            basic_match = self._basic_text_search(discussion, query)
            
            # 詳細データを取得
            details = self.manager.get_discussion_details(discussion.filename)
            if not details:
                continue
            
            # AIによる関連度スコアリング（簡易版）
            relevance_score = self._calculate_relevance(details, query)
            
            if basic_match or relevance_score > 0.3:
                results.append({
                    'discussion': discussion,
                    'details': details,
                    'relevance_score': relevance_score,
                    'basic_match': basic_match
                })
        
        # 関連度でソート
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results
    
    def _basic_text_search(self, discussion: DiscussionSummary, query: str) -> bool:
        """基本的なテキスト検索"""
        query_lower = query.lower()
        searchable_text = (
            discussion.topic.lower() + " " +
            " ".join(discussion.agents).lower() + " " +
            " ".join(discussion.categories).lower() + " " +
            discussion.summary_preview.lower()
        )
        return query_lower in searchable_text
    
    def _calculate_relevance(self, discussion_data: Dict, query: str) -> float:
        """簡易的な関連度計算"""
        query_words = query.lower().split()
        
        # メッセージからテキストを抽出
        all_text = discussion_data.get('topic', '').lower()
        messages = discussion_data.get('messages', [])
        
        for msg in messages:
            if msg.get('agent_name') != 'System':
                all_text += " " + msg.get('content', '').lower()
        
        # 単語マッチング数を計算
        matches = sum(1 for word in query_words if word in all_text)
        return matches / len(query_words) if query_words else 0
    
    def get_topic_trends(self) -> Dict[str, List[DiscussionSummary]]:
        """トピック別の議論を分類"""
        discussions = self.manager.get_all_discussions()
        trends = {}
        
        # 簡易的なキーワード分類
        keywords = {
            'AI・技術': ['AI', 'ai', '人工知能', '技術', 'テクノロジー', 'tech', 'プログラミング'],
            'ビジネス': ['ビジネス', '経営', '会社', '企業', 'マネジメント', '戦略'],
            '教育': ['教育', '学習', '学校', '大学', '研究', '教師', '学生'],
            '社会': ['社会', '政治', '法律', '政策', '市民', '公共'],
            '環境': ['環境', '持続可能', 'エコ', '再生可能', '気候'],
            '健康・医療': ['健康', '医療', '病院', '治療', '患者', '医師'],
            'その他': []
        }
        
        for discussion in discussions:
            classified = False
            text = (discussion.topic + " " + " ".join(discussion.categories)).lower()
            
            for category, category_keywords in keywords.items():
                if category == 'その他':
                    continue
                
                if any(keyword in text for keyword in category_keywords):
                    if category not in trends:
                        trends[category] = []
                    trends[category].append(discussion)
                    classified = True
                    break
            
            if not classified:
                if 'その他' not in trends:
                    trends['その他'] = []
                trends['その他'].append(discussion)
        
        return trends
    
    def export_markdown_summary(self, output_file: str = "results/discussion_summary.md"):
        """議論の要約をマークダウン形式でエクスポート"""
        discussions = self.manager.get_all_discussions()
        trends = self.get_topic_trends()
        
        content = []
        content.append("# 議論ログ要約")
        content.append(f"生成日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # 統計情報
        content.append("## 統計情報")
        content.append(f"- 総議論数: {len(discussions)}")
        content.append(f"- トピック分類数: {len(trends)}")
        
        # カテゴリー統計
        categories = {}
        for d in discussions:
            for cat in d.categories:
                if cat != 'Unknown':
                    categories[cat] = categories.get(cat, 0) + 1
        
        content.append(f"- エージェントカテゴリー: {len(categories)}")
        content.append("")
        
        # トピック別要約
        content.append("## トピック別議論")
        for topic, topic_discussions in trends.items():
            if topic_discussions:
                content.append(f"### {topic} ({len(topic_discussions)}件)")
                for d in topic_discussions[:5]:  # 最新5件のみ
                    date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%Y-%m-%d')
                    content.append(f"- **{d.topic}** ({date_str})")
                    content.append(f"  - 参加者: {', '.join(d.agents)}")
                    content.append(f"  - 要約: {d.summary_preview}")
                    content.append("")
                
                if len(topic_discussions) > 5:
                    content.append(f"  *...他{len(topic_discussions) - 5}件*")
                content.append("")
        
        # 最新の議論詳細
        content.append("## 最新の議論 (詳細)")
        for i, d in enumerate(discussions[:3], 1):
            content.append(f"### {i}. {d.topic}")
            date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%Y-%m-%d %H:%M')
            content.append(f"**日時:** {date_str}")
            content.append(f"**参加者:** {', '.join(d.agents)}")
            content.append(f"**カテゴリー:** {', '.join(d.categories)}")
            content.append(f"**ラウンド数:** {d.rounds}")
            content.append("")
            
            # AI要約を生成
            details = self.manager.get_discussion_details(d.filename)
            if details and self.model:
                ai_summary = self.generate_detailed_summary(details)
                content.append("**AI要約:**")
                content.append(ai_summary)
            else:
                content.append(f"**要約:** {d.summary_preview}")
            
            content.append("")
            content.append("---")
            content.append("")
        
        # ファイルに保存
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
        
        print(f"マークダウン要約を {output_file} に保存しました")
    
    def interactive_search(self):
        """インタラクティブ検索メニュー"""
        while True:
            print("\n🔍 議論ログブラウザ")
            print("1. キーワード検索")
            print("2. AI検索（関連度順）")
            print("3. トピック別表示")
            print("4. 詳細表示")
            print("5. マークダウン要約生成")
            print("6. HTML一覧生成")
            print("0. 戻る")
            
            choice = input("\n選択してください: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self._keyword_search()
            elif choice == "2":
                self._ai_search()
            elif choice == "3":
                self._show_topic_trends()
            elif choice == "4":
                self._show_detailed_view()
            elif choice == "5":
                self.export_markdown_summary()
            elif choice == "6":
                self.manager.export_summary_html()
            else:
                print("無効な選択です。")
    
    def _keyword_search(self):
        """キーワード検索"""
        query = input("検索キーワードを入力: ").strip()
        if not query:
            return
        
        results = self.manager.search_discussions(query)
        
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
    
    def _ai_search(self):
        """AI検索"""
        if not self.model:
            print("AI検索機能は利用できません（GEMINI_API_KEYが設定されていません）")
            return
        
        query = input("検索クエリを入力（自然言語で質問してください）: ").strip()
        if not query:
            return
        
        print("AI検索中...")
        results = self.search_with_ai(query)
        
        if not results:
            print(f"'{query}' に関連する議論が見つかりませんでした。")
            return
        
        print(f"\n🤖 AI検索結果: '{query}' ({len(results)}件)")
        print("-" * 60)
        
        for i, result in enumerate(results[:10], 1):  # 上位10件
            d = result['discussion']
            score = result['relevance_score']
            date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%Y-%m-%d %H:%M')
            
            print(f"{i}. [{date_str}] {d.topic} (関連度: {score:.2f})")
            print(f"   参加者: {', '.join(d.agents)}")
            print(f"   {d.summary_preview}")
            print()
    
    def _show_topic_trends(self):
        """トピック別表示"""
        trends = self.get_topic_trends()
        
        print("\n📊 トピック別議論")
        print("-" * 60)
        
        for topic, discussions in trends.items():
            if discussions:
                print(f"\n{topic} ({len(discussions)}件)")
                for d in discussions[:3]:  # 上位3件
                    date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%m-%d %H:%M')
                    print(f"  • [{date_str}] {d.topic}")
                
                if len(discussions) > 3:
                    print(f"  ... 他{len(discussions) - 3}件")
    
    def _show_detailed_view(self):
        """詳細表示"""
        discussions = self.manager.get_all_discussions()
        
        if not discussions:
            print("議論ログが見つかりません。")
            return
        
        print("\n議論を選択してください:")
        for i, d in enumerate(discussions[:10], 1):
            date_str = datetime.datetime.fromtimestamp(d.timestamp).strftime('%m-%d %H:%M')
            print(f"{i:2d}. [{date_str}] {d.topic}")
        
        try:
            choice = int(input("番号を選択: ")) - 1
            if 0 <= choice < min(10, len(discussions)):
                selected = discussions[choice]
                details = self.manager.get_discussion_details(selected.filename)
                
                if details:
                    self._display_discussion_detail(selected, details)
                else:
                    print("議論の詳細を読み込めませんでした。")
            else:
                print("無効な選択です。")
        
        except ValueError:
            print("無効な入力です。")
    
    def _display_discussion_detail(self, summary: DiscussionSummary, details: Dict):
        """議論の詳細を表示"""
        print(f"\n📋 議論詳細: {summary.topic}")
        print("=" * 80)
        print(f"日時: {datetime.datetime.fromtimestamp(summary.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"参加者: {', '.join(summary.agents)}")
        print(f"カテゴリー: {', '.join(summary.categories)}")
        print(f"ラウンド数: {summary.rounds}")
        print(f"メッセージ数: {summary.total_messages}")
        print(f"ファイル: {summary.filename}")
        print("")
        
        # AI要約を生成
        if self.model:
            print("AI要約生成中...")
            ai_summary = self.generate_detailed_summary(details)
            print("📝 AI要約:")
            print(ai_summary)
            print("\n" + "=" * 80)
        
        # メッセージの表示
        print("\n💬 議論内容:")
        messages = details.get('messages', [])
        for msg in messages:
            if msg.get('agent_name') == 'System':
                continue
            print(f"\n【{msg.get('agent_name', 'Unknown')}】")
            print(msg.get('content', ''))
        
        print("\n" + "=" * 80)


def main():
    """メインメニュー"""
    browser = DiscussionBrowser()
    browser.interactive_search()


if __name__ == "__main__":
    main()