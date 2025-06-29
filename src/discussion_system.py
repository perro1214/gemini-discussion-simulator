#!/usr/bin/env python3
"""
Gemini Multi-Agent Discussion System

This system uses multiple Gemini 2.5 Flash Lite instances to conduct discussions
and Gemini 2.5 Flash to summarize the discussion results.
"""

import asyncio
import os
import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass
import google.generativeai as genai
from agent_classes import Agent, Message


@dataclass
class DiscussionAgent(Agent):
    """Discussion agent with model configuration"""
    model_name: str = "gemini-2.0-flash-lite"


class DiscussionSystem:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.agents: List[DiscussionAgent] = []
        self.messages: List[Message] = []
        self.discussion_topic = ""
        self.agent_max_chars = 200
        self.summary_max_chars = 1500
        
    def add_agent(self, name: str, role: str, personality: str):
        """Add an agent to the discussion"""
        agent = DiscussionAgent(name=name, role=role, personality=personality)
        self.agents.append(agent)
        
    def set_topic(self, topic: str):
        """Set the discussion topic"""
        self.discussion_topic = topic
        
    def set_limits(self, agent_max_chars: int, summary_max_chars: int):
        """Set character limits for agents and summary"""
        self.agent_max_chars = agent_max_chars
        self.summary_max_chars = summary_max_chars
        
    async def _generate_response(self, agent: Agent, conversation_history: str) -> str:
        """Generate response from a specific agent"""
        model = genai.GenerativeModel(agent.model_name)
        
        system_prompt = f"""
あなたは{agent.name}として、{agent.role}の立場で発言してください。
あなたの性格・特徴: {agent.personality}

議論テーマ: {self.discussion_topic}

以下の会話履歴を踏まえて、あなたの視点から意見を述べてください。
- {self.agent_max_chars}文字以内で簡潔に回答してください
- キャラクターを保って発言してください
- 建設的で議論に価値を加える内容にしてください
- 必ず日本語で回答してください

会話履歴:
{conversation_history}

{agent.name}としての回答:
"""
        
        try:
            response = await model.generate_content_async(system_prompt)
            text = response.text.strip()
            # 文字数制限を適用
            if len(text) > self.agent_max_chars:
                text = text[:self.agent_max_chars] + "..."
            return text
        except Exception as e:
            return f"[Error from {agent.name}: {str(e)}]"
    
    def _format_conversation_history(self) -> str:
        """Format the conversation history for context"""
        if not self.messages:
            return "No previous messages."
        
        history = []
        for msg in self.messages[-10:]:  # Last 10 messages for context
            history.append(f"{msg.agent_name}: {msg.content}")
        
        return "\n".join(history)
    
    async def conduct_discussion(self, rounds: int = 3) -> List[Message]:
        """Conduct a multi-round discussion"""
        print(f"Starting discussion on: {self.discussion_topic}")
        print(f"Participants: {', '.join([agent.name for agent in self.agents])}")
        print("-" * 50)
        
        # Initial prompt to start discussion
        initial_message = Message(
            agent_name="System",
            content=f"Discussion topic: {self.discussion_topic}",
            timestamp=time.time()
        )
        self.messages.append(initial_message)
        print(f"System: {initial_message.content}")
        
        for round_num in range(rounds):
            print(f"\n=== Round {round_num + 1} ===")
            
            # All agents respond in parallel
            tasks = []
            conversation_history = self._format_conversation_history()
            
            for agent in self.agents:
                task = self._generate_response(agent, conversation_history)
                tasks.append((agent, task))
            
            # Wait for all responses
            responses = await asyncio.gather(*[task for _, task in tasks])
            
            # Add responses to conversation
            for (agent, _), response in zip(tasks, responses):
                message = Message(
                    agent_name=agent.name,
                    content=response,
                    timestamp=time.time()
                )
                self.messages.append(message)
                print(f"{agent.name}: {response}")
            
            # Small delay between rounds
            await asyncio.sleep(1)
        
        return self.messages
    
    async def summarize_discussion(self) -> str:
        """Summarize the discussion using Gemini 2.5 Flash"""
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Format all messages for summarization
        discussion_text = []
        for msg in self.messages:
            if msg.agent_name != "System":
                discussion_text.append(f"{msg.agent_name}: {msg.content}")
        
        full_discussion = "\n".join(discussion_text)
        
        summary_prompt = f"""
以下の「{self.discussion_topic}」についての議論を日本語で要約してください。

以下の項目を含む包括的で詳細な要約を提供してください：
1. 議論された主なポイント
2. 提示された異なる観点
3. 合意点と相違点
4. 重要な洞察と結論
5. 提案された次のステップや行動（もしあれば）

議論内容：
{full_discussion}

詳細な要約：
"""
        
        try:
            response = await model.generate_content_async(summary_prompt)
            text = response.text.strip()
            # 要約の全文を返す（文字数制限を適用しない）
            return text
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def save_discussion(self, filename: str):
        """Save the discussion to a JSON file"""
        data = {
            "topic": self.discussion_topic,
            "agents": [
                {
                    "name": agent.name,
                    "role": agent.role,
                    "personality": agent.personality
                }
                for agent in self.agents
            ],
            "messages": [
                {
                    "agent_name": msg.agent_name,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in self.messages
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


async def main():
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    # Create discussion system
    system = DiscussionSystem(api_key)
    
    # Set topic
    topic = input("Enter discussion topic: ").strip()
    if not topic:
        topic = "The future of artificial intelligence in education"
    
    system.set_topic(topic)
    
    # Add agents with different perspectives
    system.add_agent(
        name="Dr. Tech",
        role="Technology Expert",
        personality="Analytical, focused on technical feasibility and innovation"
    )
    
    system.add_agent(
        name="Prof. Ethics",
        role="Ethics Professor",
        personality="Thoughtful, concerned about moral implications and social impact"
    )
    
    system.add_agent(
        name="Ms. Practical",
        role="Business Consultant",
        personality="Pragmatic, focused on real-world implementation and costs"
    )
    
    system.add_agent(
        name="Alex Student",
        role="Student Representative",
        personality="Curious, asks questions from a learner's perspective"
    )
    
    try:
        # Conduct discussion
        messages = await system.conduct_discussion(rounds=3)
        
        print("\n" + "="*50)
        print("GENERATING SUMMARY...")
        print("="*50)
        
        # Generate summary
        summary = await system.summarize_discussion()
        print("\nDISCUSSION SUMMARY:")
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
    asyncio.run(main())