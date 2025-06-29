#!/usr/bin/env python3
"""
Demo script to showcase the enhanced discussion system with different presets
"""

import asyncio
import os
import sys
import inspect
import time

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.discussion_system import DiscussionSystem
from src.agent_presets import get_agents_by_category


async def demo_education_discussion():
    """教育カテゴリーのデモ"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    system = DiscussionSystem(api_key)
    topic = "学校でのスマートフォン使用について"
    system.set_topic(topic)
    
    # 教育カテゴリーから5人選択
    education_agents = get_agents_by_category("教育")[:5]
    
    for agent in education_agents:
        system.add_agent(agent.name, agent.role, agent.personality)
    
    print("=== 教育カテゴリーデモ ===")
    print(f"トピック: {topic}")
    print(f"参加者: {', '.join([agent.name for agent in education_agents])}")
    print("=" * 50)
    
    try:
        messages = await system.conduct_discussion(rounds=2)
        print(f"\n要約生成中...")
        summary = await system.summarize_discussion()
        print(f"\n【要約】\n{summary}")
        
        system.save_discussion("results/demo_education.json")
        print(f"\n💾 保存完了: demo_education.json")
        
    except Exception as e:
        print(f"❌ エラー: {e}")


async def demo_business_discussion():
    """ビジネスカテゴリーのデモ"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    system = DiscussionSystem(api_key)
    topic = "リモートワークの今後について"
    system.set_topic(topic)
    
    # ビジネスカテゴリーから4人選択
    business_agents = get_agents_by_category("ビジネス")[:4]
    
    for agent in business_agents:
        system.add_agent(agent.name, agent.role, agent.personality)
    
    print("\n=== ビジネスカテゴリーデモ ===")
    print(f"トピック: {topic}")
    print(f"参加者: {', '.join([agent.name for agent in business_agents])}")
    print("=" * 50)
    
    try:
        messages = await system.conduct_discussion(rounds=3)
        print(f"\n要約生成中...")
        summary = await system.summarize_discussion()
        print(f"\n【要約】\n{summary}")
        
        system.save_discussion("results/demo_business.json")
        print(f"\n💾 保存完了: demo_business.json")
        
    except Exception as e:
        print(f"❌ エラー: {e}")


async def demo_tech_discussion():
    """技術カテゴリーのデモ"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    system = DiscussionSystem(api_key)
    topic = "AIの倫理的な使用について"
    system.set_topic(topic)
    
    # 技術カテゴリーから3人選択
    tech_agents = get_agents_by_category("技術")[:3]
    
    for agent in tech_agents:
        system.add_agent(agent.name, agent.role, agent.personality)
    
    print("\n=== 技術カテゴリーデモ ===")
    print(f"トピック: {topic}")
    print(f"参加者: {', '.join([agent.name for agent in tech_agents])}")
    print("=" * 50)
    
    try:
        messages = await system.conduct_discussion(rounds=4)
        print(f"\n要約生成中...")
        summary = await system.summarize_discussion()
        print(f"\n【要約】\n{summary}")
        
        system.save_discussion("results/demo_tech.json")
        print(f"\n💾 保存完了: demo_tech.json")
        
    except Exception as e:
        print(f"❌ エラー: {e}")


def show_all_presets():
    """全プリセットを表示"""
    from src.agent_presets import AGENT_PRESETS
    
    print("=" * 60)
    print("利用可能なエージェントプリセット")
    print("=" * 60)
    
    for category, agents in AGENT_PRESETS.items():
        print(f"\n【{category}】({len(agents)}人)")
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. {agent.name} ({agent.role})")
            print(f"     {agent.personality}")
    
    print("\n" + "=" * 60)


async def main():
    print("🤖 Gemini Multi-Agent Discussion System - Enhanced Demo")
    print("=" * 60)
    
    # 全プリセット表示
    show_all_presets()
    
    print("\n3つの異なるカテゴリーでデモを実行します...")
    print("各デモは数分かかる場合があります。")
    
    # 各カテゴリーのデモを順次実行
    await demo_education_discussion()
    await asyncio.sleep(2)  # 少し間を空ける
    
    await demo_business_discussion()
    await asyncio.sleep(2)
    
    await demo_tech_discussion()
    
    print("\n" + "=" * 60)
    print("✅ 全てのデモが完了しました！")
    print("以下のファイルが生成されました:")
    print("- demo_education.json (教育カテゴリー)")
    print("- demo_business.json (ビジネスカテゴリー)")
    print("- demo_tech.json (技術カテゴリー)")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nデモを中断しました。")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")