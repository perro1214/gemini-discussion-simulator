#!/usr/bin/env python3
"""
Test script for the enhanced discussion system with character limits and random selection
"""

import asyncio
import os
import sys
import inspect
import random

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.discussion_system import DiscussionSystem
from src.agent_presets import get_agents_by_category


async def test_enhanced_features():
    """Enhanced featuresのテスト"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    print("🧪 Enhanced Discussion System Test")
    print("=" * 50)
    
    # システム作成
    system = DiscussionSystem(api_key)
    
    # テスト設定
    topic = "フレックスタイム制の導入について"
    system.set_topic(topic)
    
    # 文字数制限設定
    agent_limit = 150  # 短めに設定
    summary_limit = 800  # 短めに設定
    system.set_limits(agent_limit, summary_limit)
    
    # ビジネスカテゴリーからランダムに3人選択
    business_agents = get_agents_by_category("ビジネス")
    selected_agents = random.sample(business_agents, 3)
    
    print(f"トピック: {topic}")
    print(f"エージェント発言制限: {agent_limit}文字")
    print(f"要約文字制限: {summary_limit}文字")
    print(f"ランダム選択された参加者:")
    for i, agent in enumerate(selected_agents, 1):
        print(f"  {i}. {agent.name} ({agent.role})")
        system.add_agent(agent.name, agent.role, agent.personality)
    
    print("\n" + "=" * 50)
    
    try:
        # 議論実行（2ラウンド）
        print("議論開始...")
        messages = await system.conduct_discussion(rounds=2)
        
        print("\n要約生成中...")
        summary = await system.summarize_discussion()
        
        print(f"\n【議論要約】（{len(summary)}文字）")
        print("-" * 30)
        print(summary)
        
        # 統計情報
        print(f"\n" + "=" * 50)
        print("統計情報")
        print("=" * 50)
        print(f"総メッセージ数: {len(messages)}")
        
        # 各エージェントの発言文字数チェック
        for msg in messages:
            if msg.agent_name != "System":
                char_count = len(msg.content)
                status = "✅" if char_count <= agent_limit else "❌"
                print(f"{msg.agent_name}: {char_count}文字 {status}")
        
        summary_char_count = len(summary)
        summary_status = "✅" if summary_char_count <= summary_limit else "❌"
        print(f"要約: {summary_char_count}文字 {summary_status}")
        
        # 保存
        system.save_discussion("results/test_enhanced.json")
        print(f"\n💾 保存完了: test_enhanced.json")
        
        print("\n✅ Enhanced features test completed!")
        
    except Exception as e:
        print(f"❌ テスト失敗: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(test_enhanced_features())
    except KeyboardInterrupt:
        print("\n\nテストを中断しました。")