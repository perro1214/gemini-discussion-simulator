#!/usr/bin/env python3
"""
議論ログの検索・要約・管理システム
Discussion Log Search, Summary, and Management System
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse


class DiscussionManager:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        self.discussions_dir = os.path.join(results_dir, "discussions")
        self.summaries_dir = os.path.join(results_dir, "summaries")
        self.archive_dir = os.path.join(results_dir, "archive")
        self.full_summaries_dir = os.path.join(results_dir, "full_summaries")
        
        # ディレクトリを作成
        os.makedirs(self.discussions_dir, exist_ok=True)
        os.makedirs(self.summaries_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        os.makedirs(self.full_summaries_dir, exist_ok=True)

    def get_all_discussions(self) -> List[Dict[str, Any]]:
        """全ての議論ファイルを取得"""
        discussions = []
        
        # resultsディレクトリ直下の議論ファイル
        for filename in os.listdir(self.results_dir):
            if filename.endswith('.json') and 'discussion' in filename:
                filepath = os.path.join(self.results_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['filename'] = filename
                        data['filepath'] = filepath
                        discussions.append(data)
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        
        # discussionsディレクトリ内のファイル
        if os.path.exists(self.discussions_dir):
            for filename in os.listdir(self.discussions_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.discussions_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            data['filename'] = filename
                            data['filepath'] = filepath
                            discussions.append(data)
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
        
        return discussions

    def search_discussions(self, query: str, search_in: str = "all") -> List[Dict[str, Any]]:
        """議論を検索"""
        discussions = self.get_all_discussions()
        results = []
        
        query_lower = query.lower()
        
        for discussion in discussions:
            match = False
            
            # トピックで検索
            if search_in in ["all", "topic"] and "topic" in discussion:
                if query_lower in discussion["topic"].lower():
                    match = True
            
            # 議論内容で検索
            if search_in in ["all", "content"] and "discussion" in discussion:
                for message in discussion["discussion"]:
                    if query_lower in message.get("content", "").lower():
                        match = True
                        break
            
            # エージェント名で検索
            if search_in in ["all", "agents"] and "agents" in discussion:
                for agent in discussion["agents"]:
                    if query_lower in agent.get("name", "").lower() or \
                       query_lower in agent.get("role", "").lower():
                        match = True
                        break
            
            if match:
                results.append(discussion)
        
        return results

    def create_summary(self, discussion: Dict[str, Any]) -> Dict[str, Any]:
        """議論の要約を作成"""
        summary = {
            "filename": discussion.get("filename", ""),
            "topic": discussion.get("topic", ""),
            "date": discussion.get("timestamp", ""),
            "agents": [agent.get("name", "") for agent in discussion.get("agents", [])],
            "total_messages": len(discussion.get("discussion", [])),
            "key_points": []
        }
        
        # 主要なポイントを抽出（簡単な実装）
        messages = discussion.get("discussion", [])
        if messages:
            # 最初と最後のメッセージ（全文保存）
            summary["first_message"] = messages[0].get("content", "")
            summary["last_message"] = messages[-1].get("content", "")
            
            # 全てのメッセージを主要ポイントとして保存（全文）
            for msg in messages:
                content = msg.get("content", "")
                if content:  # 空でない場合のみ
                    summary["key_points"].append({
                        "speaker": msg.get("speaker", ""),
                        "content": content  # 全文保存
                    })
        
        return summary

    def organize_discussions(self):
        """議論ファイルを整理"""
        discussions = self.get_all_discussions()
        
        for discussion in discussions:
            # ファイル名からタイムスタンプを抽出
            filename = discussion["filename"]
            if "discussion_" in filename and filename.endswith(".json"):
                timestamp_str = filename.replace("discussion_", "").replace(".json", "")
                if timestamp_str.isdigit():
                    timestamp = int(timestamp_str)
                    date = datetime.fromtimestamp(timestamp)
                    new_filename = f"discussion_{date.strftime('%Y%m%d_%H%M%S')}.json"
                else:
                    new_filename = filename
            else:
                new_filename = filename
            
            # discussionsディレクトリに移動
            new_path = os.path.join(self.discussions_dir, new_filename)
            if discussion["filepath"] != new_path:
                try:
                    os.rename(discussion["filepath"], new_path)
                    print(f"Moved {filename} to {new_filename}")
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
            
            # 要約を作成
            summary = self.create_summary(discussion)
            summary_filename = new_filename.replace(".json", "_summary.json")
            summary_path = os.path.join(self.summaries_dir, summary_filename)
            
            try:
                with open(summary_path, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
                print(f"Created summary: {summary_filename}")
            except Exception as e:
                print(f"Error creating summary for {filename}: {e}")

    def list_discussions(self) -> None:
        """議論一覧を表示"""
        discussions = self.get_all_discussions()
        
        print(f"\n=== 議論一覧 ({len(discussions)}件) ===")
        for i, discussion in enumerate(discussions, 1):
            topic = discussion.get("topic", "No topic")
            filename = discussion.get("filename", "")
            agents = [agent.get("name", "") for agent in discussion.get("agents", [])]
            message_count = len(discussion.get("discussion", []))
            
            print(f"{i}. {topic}")
            print(f"   ファイル: {filename}")
            print(f"   エージェント: {', '.join(agents)}")
            print(f"   メッセージ数: {message_count}")
            print()

    def show_discussion_detail(self, filename: str) -> None:
        """議論の詳細を表示"""
        discussions = self.get_all_discussions()
        
        for discussion in discussions:
            if discussion["filename"] == filename:
                print(f"\n=== 議論詳細: {filename} ===")
                print(f"トピック: {discussion.get('topic', 'No topic')}")
                print(f"タイムスタンプ: {discussion.get('timestamp', 'N/A')}")
                
                print("\nエージェント:")
                for agent in discussion.get("agents", []):
                    print(f"  - {agent.get('name', '')}: {agent.get('role', '')}")
                
                print(f"\n議論内容 ({len(discussion.get('discussion', []))}メッセージ):")
                for i, msg in enumerate(discussion.get("discussion", []), 1):
                    speaker = msg.get("speaker", "Unknown")
                    content = msg.get("content", "")
                    print(f"\n{i}. {speaker}:")
                    # 全文表示（長い場合は改行で見やすく）
                    if len(content) > 200:
                        print(f"   {content[:200]}...")
                        print(f"   [メッセージが長いため省略。全文は要約ファイルを参照]")
                    else:
                        print(f"   {content}")
                
                return
        
        print(f"Discussion {filename} not found.")


    def save_full_summary(self, summary_text: str, topic: str = "", timestamp: str = "") -> str:
        """生成された要約テキストを保存"""
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            # Unix timestamp から日時文字列に変換
            if timestamp.isdigit():
                try:
                    dt = datetime.fromtimestamp(int(timestamp))
                    timestamp = dt.strftime("%Y%m%d_%H%M%S")
                except:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # ファイル名を生成
        if topic:
            # トピックから安全なファイル名を作成
            safe_topic = re.sub(r'[^\w\s-]', '', topic)[:50]
            safe_topic = re.sub(r'[-\s]+', '_', safe_topic)
            filename = f"summary_{timestamp}_{safe_topic}.txt"
        else:
            filename = f"summary_{timestamp}.txt"
        
        filepath = os.path.join(self.full_summaries_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"議論要約 - {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                if topic:
                    f.write(f"トピック: {topic}\n\n")
                f.write(summary_text)
            
            print(f"要約を保存しました: {filename}")
            return filepath
        except Exception as e:
            print(f"要約の保存でエラーが発生しました: {e}")
            return ""

    def list_full_summaries(self) -> None:
        """保存された要約一覧を表示"""
        if not os.path.exists(self.full_summaries_dir):
            print("要約ファイルが見つかりません。")
            return
        
        files = [f for f in os.listdir(self.full_summaries_dir) if f.endswith('.txt')]
        if not files:
            print("保存された要約がありません。")
            return
        
        files.sort(reverse=True)  # 新しい順
        
        print(f"\n=== 保存された要約一覧 ({len(files)}件) ===")
        for i, filename in enumerate(files, 1):
            # ファイル名から情報を抽出
            parts = filename.replace('.txt', '').split('_')
            if len(parts) >= 3:
                date_part = parts[1]
                time_part = parts[2]
                topic_part = '_'.join(parts[3:]) if len(parts) > 3 else "トピック不明"
                
                # 日時を読みやすい形式に変換
                try:
                    dt = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
                    date_str = dt.strftime("%Y年%m月%d日 %H:%M")
                except:
                    date_str = "日時不明"
                
                print(f"{i}. {topic_part} ({date_str})")
                print(f"   ファイル: {filename}")
            else:
                print(f"{i}. {filename}")
            print()

    def show_full_summary(self, filename: str) -> None:
        """保存された要約を表示"""
        filepath = os.path.join(self.full_summaries_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"要約ファイル '{filename}' が見つかりません。")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
        except Exception as e:
            print(f"要約ファイルの読み込みでエラーが発生しました: {e}")


def main():
    parser = argparse.ArgumentParser(description="Discussion Management System")
    parser.add_argument("command", choices=["list", "search", "organize", "detail", "save-summary", "list-summaries", "show-summary"], 
                       help="Command to execute")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--search-in", choices=["all", "topic", "content", "agents"], 
                       default="all", help="Search scope")
    parser.add_argument("--filename", "-f", help="Filename for detail view")
    parser.add_argument("--summary-text", help="Summary text to save")
    parser.add_argument("--topic", help="Topic for the summary")
    
    args = parser.parse_args()
    
    manager = DiscussionManager()
    
    if args.command == "list":
        manager.list_discussions()
    
    elif args.command == "search":
        if not args.query:
            print("Error: --query is required for search command")
            return
        
        results = manager.search_discussions(args.query, args.search_in)
        print(f"\n=== 検索結果: '{args.query}' ({len(results)}件) ===")
        
        for i, discussion in enumerate(results, 1):
            topic = discussion.get("topic", "No topic")
            filename = discussion.get("filename", "")
            print(f"{i}. {topic} ({filename})")
    
    elif args.command == "organize":
        print("Organizing discussions...")
        manager.organize_discussions()
        print("Organization complete!")
    
    elif args.command == "detail":
        if not args.filename:
            print("Error: --filename is required for detail command")
            return
        
        manager.show_discussion_detail(args.filename)
    
    elif args.command == "save-summary":
        if not args.summary_text:
            print("Error: --summary-text is required for save-summary command")
            return
        
        manager.save_full_summary(args.summary_text, args.topic or "")
    
    elif args.command == "list-summaries":
        manager.list_full_summaries()
    
    elif args.command == "show-summary":
        if not args.filename:
            print("Error: --filename is required for show-summary command")
            return
        
        manager.show_full_summary(args.filename)


if __name__ == "__main__":
    main()