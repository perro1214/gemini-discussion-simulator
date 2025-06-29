#!/usr/bin/env python3
"""
Quick test run of the discussion system with a predefined topic
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


async def main():
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    # Create discussion system
    system = DiscussionSystem(api_key)
    
    # Set predefined topic for testing
    topic = "AIが教育現場で果たすべき役割について"
    system.set_topic(topic)
    
    # Add agents with different perspectives
    system.add_agent(
        name="田中先生",
        role="ベテラン教師",
        personality="実践的で、生徒の学習効果を最優先に考える"
    )
    
    system.add_agent(
        name="佐藤博士",
        role="AI研究者",
        personality="技術的な可能性に詳しく、革新的なアプローチを提案する"
    )
    
    system.add_agent(
        name="山田さん",
        role="保護者代表",
        personality="子どもの安全とプライバシーを心配している"
    )
    
    try:
        print("=== Gemini Multi-Agent Discussion System ===")
        print(f"トピック: {topic}")
        print(f"参加者: {', '.join([agent.name for agent in system.agents])}")
        print("=" * 50)
        
        # Conduct discussion
        messages = await system.conduct_discussion(rounds=2)
        
        print("\n" + "="*50)
        print("要約を生成中...")
        print("="*50)
        
        # Generate summary
        summary = await system.summarize_discussion()
        print("\n議論の要約:")
        print("-" * 20)
        print(summary)
        
        # Save discussion
        system.save_discussion("results/discussion_result.json")
        print(f"\n議論の内容を discussion_result.json に保存しました")
        
        print("\n✅ 議論システムのテストが完了しました！")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())