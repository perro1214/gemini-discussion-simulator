#!/usr/bin/env python3
"""
Agent Management CLI Tool
エージェント管理用コマンドラインツール
"""

import argparse
import os
import sys
import inspect

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.agent_manager import AgentManager


def list_categories(manager: AgentManager):
    """カテゴリ一覧を表示"""
    categories = manager.get_categories()
    print(f"\n利用可能なカテゴリ ({len(categories)}個):")
    for i, category in enumerate(categories, 1):
        count = len(manager.get_agents_by_category(category))
        print(f"{i}. {category} ({count}人)")

def list_agents(manager: AgentManager, category: str = None):
    """エージェント一覧を表示"""
    if category:
        manager.list_agents_in_category(category)
    else:
        categories = manager.get_categories()
        for cat in categories:
            manager.list_agents_in_category(cat)
            print()

def add_agent(manager: AgentManager, category: str, name: str, role: str, personality: str):
    """エージェントを追加"""
    if manager.add_agent(category, name, role, personality):
        print(f"✅ エージェント '{name}' を {category} カテゴリに追加しました。")
    else:
        print(f"❌ エージェントの追加に失敗しました。")

def remove_agent(manager: AgentManager, category: str, name: str):
    """エージェントを削除"""
    if manager.remove_agent(category, name):
        print(f"✅ エージェント '{name}' を {category} カテゴリから削除しました。")
    else:
        print(f"❌ エージェントの削除に失敗しました。")

def add_category(manager: AgentManager, category: str):
    """カテゴリを追加"""
    if manager.add_category(category):
        print(f"✅ カテゴリ '{category}' を追加しました。")
    else:
        print(f"❌ カテゴリの追加に失敗しました。")

def remove_category(manager: AgentManager, category: str):
    """カテゴリを削除"""
    if manager.remove_category(category):
        print(f"✅ カテゴリ '{category}' を削除しました。")
    else:
        print(f"❌ カテゴリの削除に失敗しました。")

def search_agents(manager: AgentManager, query: str):
    """エージェントを検索"""
    results = manager.search_agents(query)
    print(f"\n検索結果: '{query}' ({len(results)}件)")
    for i, agent in enumerate(results, 1):
        print(f"{i}. {agent.name} ({agent.role})")
        print(f"   {agent.personality}")

def show_statistics(manager: AgentManager):
    """統計情報を表示"""
    stats = manager.get_statistics()
    print(f"\n=== エージェント統計 ===")
    print(f"総カテゴリ数: {stats['total_categories']}")
    print(f"総エージェント数: {stats['total_agents']}")
    print(f"\nカテゴリ別:")
    for category, count in stats["categories"].items():
        print(f"  {category}: {count}人")

def interactive_mode(manager: AgentManager):
    """対話モード"""
    print("\n=== エージェント管理ツール (対話モード) ===")
    print("利用可能なコマンド:")
    print("1. list-categories - カテゴリ一覧")
    print("2. list-agents [カテゴリ] - エージェント一覧")
    print("3. add-agent - エージェント追加")
    print("4. remove-agent - エージェント削除")
    print("5. add-category - カテゴリ追加")
    print("6. remove-category - カテゴリ削除")
    print("7. search - エージェント検索")
    print("8. stats - 統計情報")
    print("9. quit - 終了")
    
    while True:
        try:
            command = input("\nコマンド> ").strip()
            
            if command == "quit" or command == "exit":
                break
            elif command == "list-categories":
                list_categories(manager)
            elif command.startswith("list-agents"):
                parts = command.split()
                category = parts[1] if len(parts) > 1 else None
                list_agents(manager, category)
            elif command == "add-agent":
                category = input("カテゴリ: ").strip()
                name = input("名前: ").strip()
                role = input("役職: ").strip()
                personality = input("性格・特徴: ").strip()
                add_agent(manager, category, name, role, personality)
            elif command == "remove-agent":
                category = input("カテゴリ: ").strip()
                name = input("削除するエージェント名: ").strip()
                remove_agent(manager, category, name)
            elif command == "add-category":
                category = input("新しいカテゴリ名: ").strip()
                add_category(manager, category)
            elif command == "remove-category":
                category = input("削除するカテゴリ名: ").strip()
                remove_category(manager, category)
            elif command == "search":
                query = input("検索キーワード: ").strip()
                search_agents(manager, query)
            elif command == "stats":
                show_statistics(manager)
            else:
                print("不明なコマンドです。")
        
        except KeyboardInterrupt:
            print("\n終了します。")
            break

def main():
    parser = argparse.ArgumentParser(description="Agent Management Tool")
    parser.add_argument("command", nargs="?", choices=[
        "list-categories", "list-agents", "add-agent", "remove-agent",
        "add-category", "remove-category", "search", "stats", "interactive"
    ], help="実行するコマンド")
    
    parser.add_argument("--category", "-c", help="カテゴリ名")
    parser.add_argument("--name", "-n", help="エージェント名")
    parser.add_argument("--role", "-r", help="役職")
    parser.add_argument("--personality", "-p", help="性格・特徴")
    parser.add_argument("--query", "-q", help="検索クエリ")
    
    args = parser.parse_args()
    
    manager = AgentManager()
    
    if not args.command:
        interactive_mode(manager)
        return
    
    if args.command == "list-categories":
        list_categories(manager)
    
    elif args.command == "list-agents":
        list_agents(manager, args.category)
    
    elif args.command == "add-agent":
        if not all([args.category, args.name, args.role, args.personality]):
            print("エラー: --category, --name, --role, --personality が必要です")
            return
        add_agent(manager, args.category, args.name, args.role, args.personality)
    
    elif args.command == "remove-agent":
        if not all([args.category, args.name]):
            print("エラー: --category, --name が必要です")
            return
        remove_agent(manager, args.category, args.name)
    
    elif args.command == "add-category":
        if not args.category:
            print("エラー: --category が必要です")
            return
        add_category(manager, args.category)
    
    elif args.command == "remove-category":
        if not args.category:
            print("エラー: --category が必要です")
            return
        remove_category(manager, args.category)
    
    elif args.command == "search":
        if not args.query:
            print("エラー: --query が必要です")
            return
        search_agents(manager, args.query)
    
    elif args.command == "stats":
        show_statistics(manager)
    
    elif args.command == "interactive":
        interactive_mode(manager)


if __name__ == "__main__":
    main()