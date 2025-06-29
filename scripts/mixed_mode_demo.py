#!/usr/bin/env python3
"""
Demo script for mixed genre mode - random selection from all categories
"""

import asyncio
import os
import sys
import inspect

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.discussion_system import DiscussionSystem
from src.agent_presets import select_random_agents_from_all


async def demo_mixed_mode():
    """ジャンル混合モードのデモ"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    system = DiscussionSystem(api_key)
    topic = "テクノロジーと社会の未来"
    system.set_topic(topic)
    
    # 文字数制限設定
    system.set_limits(180, 1200)
    
    # 全42種類から5人をランダム選択
    mixed_agents = select_random_agents_from_all(5)
    
    print("🌍 ジャンル混合モード デモ")
    print("=" * 50)
    print(f"トピック: {topic}")
    print(f"参加者: 全42種類からランダム選択")
    print(f"発言制限: 180文字、要約制限: 1200文字")
    print("\n選択されたエージェント:")
    
    categories_represented = []
    for i, agent in enumerate(mixed_agents, 1):
        # どのカテゴリーか特定
        category = ""
        from src.agent_presets import AGENT_PRESETS
        for cat_name, cat_agents in AGENT_PRESETS.items():
            if any(a.name == agent.name for a in cat_agents):
                category = cat_name
                break
        
        categories_represented.append(category)
        print(f"  {i}. {agent.name} ({agent.role}) [{category}]")
        print(f"     {agent.personality}")
        system.add_agent(agent.name, agent.role, agent.personality)
    
    print(f"\n代表カテゴリー: {', '.join(set(categories_represented))}")
    print("=" * 50)
    
    try:
        # 議論実行（3ラウンド）
        print("異分野コラボレーション議論開始...")
        messages = await system.conduct_discussion(rounds=3)
        
        print(f"\n要約生成中...")
        summary = await system.summarize_discussion()
        
        print(f"\n【異分野コラボレーション要約】")
        print("-" * 40)
        print(summary)
        
        # 統計情報
        print(f"\n" + "=" * 50)
        print("混合モード統計")
        print("=" * 50)
        print(f"総メッセージ数: {len(messages)}")
        print(f"代表カテゴリー数: {len(set(categories_represented))}")
        print(f"カテゴリー構成: {dict((cat, categories_represented.count(cat)) for cat in set(categories_represented))}")
        
        # 保存
        system.save_discussion("results/demo_mixed_mode.json")
        print(f"\n💾 保存完了: results/demo_mixed_mode.json")
        
        print("\n✅ ジャンル混合モードデモ完了！")
        
    except Exception as e:
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(demo_mixed_mode())
    except KeyboardInterrupt:
        print("\n\nデモを中断しました。")