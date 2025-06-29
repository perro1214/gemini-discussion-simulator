#!/usr/bin/env python3
"""
Interactive Discussion System with Agent Presets and Customizable Settings
"""

import asyncio
import os
import sys
import inspect
import time
from typing import List

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.discussion_system import DiscussionSystem
from src.agent_manager import (
    get_available_categories, 
    get_agents_by_category,
    list_agents_in_category,
    select_agents_interactive,
    select_random_agents_from_all,
    get_all_agents
)


def get_discussion_settings():
    """議論の設定を取得"""
    print("=== Gemini Multi-Agent Discussion System ===")
    print("議論の設定を行います\n")
    
    # トピック設定
    print("1. 議論のトピックを入力してください:")
    topic = input("トピック: ").strip()
    if not topic:
        topic = "AIの未来について"
        print(f"デフォルトトピック: {topic}")
    
    # カテゴリー選択
    print("\n2. エージェントの選択方法を選んでください:")
    categories = get_available_categories()
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")
    print(f"{len(categories) + 1}. ジャンル混合（全カテゴリーから無作為選択）")
    
    try:
        cat_choice = int(input("選択番号: ")) - 1
        if cat_choice == len(categories):
            # ジャンル混合モード
            selected_category = "ジャンル混合"
            is_mixed_mode = True
        elif 0 <= cat_choice < len(categories):
            selected_category = categories[cat_choice]
            is_mixed_mode = False
        else:
            selected_category = "教育"
            is_mixed_mode = False
            print(f"無効な選択です。デフォルト: {selected_category}")
    except ValueError:
        selected_category = "教育"
        is_mixed_mode = False
        print(f"無効な入力です。デフォルト: {selected_category}")
    
    # 参加者数設定
    print(f"\n3. 参加者数を設定してください (2-50人, デフォルト: 3人):")
    try:
        num_agents = int(input("参加者数: "))
        if not (2 <= num_agents <= 50):
            num_agents = 3
            print(f"範囲外です。デフォルト: {num_agents}人")
    except ValueError:
        num_agents = 3
        print(f"無効な入力です。デフォルト: {num_agents}人")
    
    # エージェント選択
    if is_mixed_mode:
        all_agents_count = len(get_all_agents())
        print(f"\n4. 全{all_agents_count}種類のエージェントから{num_agents}人をランダムに選択します:")
        agents = select_random_agents_from_all(num_agents)
        print(f"選択されたエージェント:")
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. {agent.name} ({agent.role}) - {agent.personality}")
    else:
        print(f"\n4. {selected_category}カテゴリーからエージェントを選択してください:")
        agents = select_agents_interactive(selected_category, num_agents)
    
    # ラウンド数設定
    print(f"\n5. 議論のラウンド数を設定してください (1-100回, デフォルト: 3回):")
    try:
        rounds = int(input("ラウンド数: "))
        if not (1 <= rounds <= 100):
            rounds = 3
            print(f"範囲外です。デフォルト: {rounds}回")
    except ValueError:
        rounds = 3
        print(f"無効な入力です。デフォルト: {rounds}回")
    
    # エージェント発言文字数制限設定
    print(f"\n6. エージェント1人当たりの発言文字数制限を設定してください (50-10000文字, デフォルト: 500文字):")
    try:
        agent_max_chars = int(input("文字数制限: "))
        if not (50 <= agent_max_chars <= 10000):
            agent_max_chars = 500
            print(f"範囲外です。デフォルト: {agent_max_chars}文字")
    except ValueError:
        agent_max_chars = 500
        print(f"無効な入力です。デフォルト: {agent_max_chars}文字")
    
    # 要約文字数制限設定（実際には制限しないが、プロンプトの指標として使用）
    print(f"\n7. 議論要約の目安文字数を設定してください (500-50000文字, デフォルト: 3000文字):")
    print("   ※実際の要約は全文保存されますが、生成時の目安として使用されます")
    try:
        summary_max_chars = int(input("要約目安文字数: "))
        if not (500 <= summary_max_chars <= 50000):
            summary_max_chars = 3000
            print(f"範囲外です。デフォルト: {summary_max_chars}文字")
    except ValueError:
        summary_max_chars = 3000
        print(f"無効な入力です。デフォルト: {summary_max_chars}文字")
    
    return topic, agents, rounds, agent_max_chars, summary_max_chars


def print_discussion_summary(topic: str, agents: List, rounds: int, agent_max_chars: int, summary_max_chars: int):
    """議論の設定を要約表示"""
    print("\n" + "="*60)
    print("議論設定の確認")
    print("="*60)
    print(f"トピック: {topic}")
    print(f"参加者数: {len(agents)}人")
    print(f"ラウンド数: {rounds}回")
    print(f"発言文字数制限: {agent_max_chars}文字")
    print(f"要約文字数制限: {summary_max_chars}文字")
    print("\n参加者:")
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.name} ({agent.role})")
        print(f"   {agent.personality}")
    print("="*60)
    
    input("\nEnterキーを押すと議論を開始します...")


async def main():
    # API key確認
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    try:
        # 設定取得
        topic, agents, rounds, agent_max_chars, summary_max_chars = get_discussion_settings()
        
        if not agents:
            print("エージェントが選択されていません。終了します。")
            return
        
        # 設定確認
        print_discussion_summary(topic, agents, rounds, agent_max_chars, summary_max_chars)
        
        # ディスカッションシステム作成
        system = DiscussionSystem(api_key)
        system.set_topic(topic)
        system.set_limits(agent_max_chars, summary_max_chars)
        
        # エージェント追加
        for agent in agents:
            system.add_agent(agent.name, agent.role, agent.personality)
        
        print(f"\n議論開始: {topic}")
        print(f"参加者: {', '.join([agent.name for agent in agents])}")
        print("-" * 60)
        
        # 議論実行
        start_time = time.time()
        messages = await system.conduct_discussion(rounds=rounds)
        discussion_time = time.time() - start_time
        
        print(f"\n" + "="*60)
        print("要約を生成中...")
        print("="*60)
        
        # 要約生成
        summary_start = time.time()
        summary = await system.summarize_discussion()
        summary_time = time.time() - summary_start
        
        print(f"\n【議論の要約】")
        print("-" * 30)
        print(summary)
        
        # 結果保存
        timestamp = int(time.time())
        filename = f"results/discussion_{timestamp}.json"
        system.save_discussion(filename)
        
        # 要約テキストも保存
        try:
            from src.discussion_search import DiscussionManager
            manager = DiscussionManager()
            summary_filepath = manager.save_full_summary(summary, topic, str(timestamp))
            print(f"要約も保存されました: {summary_filepath}")
        except Exception as e:
            print(f"要約の保存でエラーが発生しました: {e}")
        
        # 統計情報
        print(f"\n" + "="*60)
        print("実行統計")
        print("="*60)
        print(f"総メッセージ数: {len(messages)}")
        print(f"議論時間: {discussion_time:.1f}秒")
        print(f"要約生成時間: {summary_time:.1f}秒")
        print(f"保存ファイル: {filename}")
        print("="*60)
        
        print("\n✅ 議論が完了しました！")
        print("\n📋 管理コマンド:")
        print("  - 議論一覧: python3 discussion_search.py list")
        print("  - 要約一覧: python3 discussion_search.py list-summaries")
        print(f"  - この議論の詳細: python3 discussion_search.py detail --filename discussion_{timestamp}.json")
        
        # 議論ログの自動整理を提案
        print("\n🔧 議論ログを整理しますか？ (y/n): ", end="")
        try:
            organize_choice = input().strip().lower()
            if organize_choice in ['y', 'yes', 'はい']:
                from src.discussion_search import DiscussionManager
                manager = DiscussionManager()
                print("\n議論ログを整理中...")
                manager.organize_discussions()
                print("✅ 整理が完了しました！")
        except Exception as e:
            print(f"整理中にエラーが発生しました: {e}")
        
    except KeyboardInterrupt:
        print("\n\n議論が中断されました。")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nプログラムを終了します。")