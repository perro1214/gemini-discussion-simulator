#!/usr/bin/env python3
import asyncio
import os
import time
import json
import google.generativeai as genai
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Assuming DiscussionSystem and Agent classes are in src/
from src.discussion_system import DiscussionSystem
from src.agent_classes import Agent

async def main():
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return

    # Create discussion system
    system = DiscussionSystem(api_key)

    # Set topic
    topic = "AIが教育現場で果たすべき役割について"

    system.set_topic(topic)

    # Add agents with different perspectives
    # Using example agents from README for simplicity
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
        # Conduct discussion
        messages = await system.conduct_discussion(rounds=3)

        print("\n" + "="*50)
        print("GENERATING SUMMARY...")
        print("="*50)

        # Generate summary
        summary = await system.summarize_discussion()
        print("\nDISCUSSION SUMMARY:\n")
        print("-" * 20)
        print(summary)

        # Save discussion
        timestamp = int(time.time())
        filename = f"results/discussion_{timestamp}.json"
        system.save_discussion(filename)
        print(f"\nDiscussion saved to: {filename}")

    except Exception as e:
        print(f"Error during discussion: {str(e)}")

if __name__ == "__main__":
    print("=== Gemini Multi-Agent Discussion System ===")
    print(f"トピック: AIが教育現場で果たすべき役割について")
    print(f"参加者: 田中先生, 佐藤博士, 山田さん")
    print("==================================================")
    asyncio.run(main())
    print("\n✅ 議論システムのテストが完了しました！")
