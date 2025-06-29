#!/usr/bin/env python3
"""
Dynamic Agent Management System
エージェントの動的管理システム
"""

import json
import os
import random
from typing import List, Dict, Any, Optional
from src.agent_classes import Agent


class AgentManager:
    def __init__(self, config_file: str = os.path.join(os.path.dirname(__file__), "agents_config.json")):
        self.config_file = config_file
        self.agents_data = self._load_agents()
    
    def _load_agents(self) -> Dict[str, List[Dict[str, str]]]:
        """エージェント設定を読み込む"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("categories", {})
        except FileNotFoundError:
            print(f"設定ファイル {self.config_file} が見つかりません。")
            return {}
        except json.JSONDecodeError as e:
            print(f"設定ファイルの形式が正しくありません: {e}")
            return {}
    
    def reload_agents(self) -> bool:
        """エージェント設定を再読み込み"""
        new_data = self._load_agents()
        if new_data:
            self.agents_data = new_data
            print("エージェント設定を再読み込みしました。")
            return True
        return False
    
    def get_categories(self) -> List[str]:
        """利用可能なカテゴリ一覧を取得"""
        return list(self.agents_data.keys())
    
    def get_agents_by_category(self, category: str) -> List[Agent]:
        """指定されたカテゴリのエージェント一覧を取得"""
        if category not in self.agents_data:
            return []
        
        agents = []
        for agent_data in self.agents_data[category]:
            agent = Agent(
                name=agent_data["name"],
                role=agent_data["role"],
                personality=agent_data["personality"]
            )
            agents.append(agent)
        return agents
    
    def get_all_agents(self) -> List[Agent]:
        """全エージェントを取得"""
        all_agents = []
        for category in self.agents_data:
            all_agents.extend(self.get_agents_by_category(category))
        return all_agents
    
    def list_agents_in_category(self, category: str) -> None:
        """指定されたカテゴリのエージェント一覧を表示"""
        agents = self.get_agents_by_category(category)
        if not agents:
            print(f"カテゴリ '{category}' にエージェントが見つかりません。")
            return
        
        print(f"\n{category}カテゴリのエージェント:")
        for i, agent in enumerate(agents, 1):
            print(f"{i}. {agent.name} ({agent.role})")
            print(f"   {agent.personality}")
    
    def select_agents_interactive(self, category: str, max_agents: int) -> List[Agent]:
        """対話的にエージェントを選択"""
        agents = self.get_agents_by_category(category)
        if not agents:
            print(f"カテゴリ '{category}' にエージェントが見つかりません。")
            return []
        
        self.list_agents_in_category(category)
        
        if len(agents) <= max_agents:
            print(f"\n全{len(agents)}人のエージェントを選択します。")
            return agents
        
        print(f"\n{max_agents}人のエージェントを選択してください。")
        print("番号をカンマ区切りで入力してください (例: 1,3,5)")
        print("何も入力しない場合、ランダムに選択します。")
        
        try:
            selection = input("選択: ").strip()
            
            if not selection:
                return random.sample(agents, max_agents)
            
            selected_agents = []
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            for idx in indices:
                if 0 <= idx < len(agents) and len(selected_agents) < max_agents:
                    selected_agents.append(agents[idx])
            
            if len(selected_agents) < max_agents:
                remaining = max_agents - len(selected_agents)
                available = [a for a in agents if a not in selected_agents]
                selected_agents.extend(random.sample(available, min(remaining, len(available))))
            
            return selected_agents[:max_agents]
            
        except (ValueError, IndexError):
            print(f"無効な入力です。ランダムに{max_agents}人を選択します。")
            return random.sample(agents, min(max_agents, len(agents)))
    
    def select_random_agents_from_all(self, num_agents: int) -> List[Agent]:
        """全カテゴリからランダムにエージェントを選択"""
        all_agents = self.get_all_agents()
        if len(all_agents) <= num_agents:
            return all_agents
        return random.sample(all_agents, num_agents)
    
    def add_agent(self, category: str, name: str, role: str, personality: str) -> bool:
        """新しいエージェントを追加"""
        if category not in self.agents_data:
            self.agents_data[category] = []
        
        # 重複チェック
        for agent_data in self.agents_data[category]:
            if agent_data["name"] == name:
                print(f"エージェント '{name}' は既に存在します。")
                return False
        
        self.agents_data[category].append({
            "name": name,
            "role": role,
            "personality": personality
        })
        
        return self._save_agents()
    
    def remove_agent(self, category: str, name: str) -> bool:
        """エージェントを削除"""
        if category not in self.agents_data:
            print(f"カテゴリ '{category}' が見つかりません。")
            return False
        
        original_length = len(self.agents_data[category])
        self.agents_data[category] = [
            agent for agent in self.agents_data[category] 
            if agent["name"] != name
        ]
        
        if len(self.agents_data[category]) == original_length:
            print(f"エージェント '{name}' が見つかりません。")
            return False
        
        return self._save_agents()
    
    def add_category(self, category: str) -> bool:
        """新しいカテゴリを追加"""
        if category in self.agents_data:
            print(f"カテゴリ '{category}' は既に存在します。")
            return False
        
        self.agents_data[category] = []
        return self._save_agents()
    
    def remove_category(self, category: str) -> bool:
        """カテゴリを削除"""
        if category not in self.agents_data:
            print(f"カテゴリ '{category}' が見つかりません。")
            return False
        
        del self.agents_data[category]
        return self._save_agents()
    
    def _save_agents(self) -> bool:
        """エージェント設定をファイルに保存"""
        try:
            data = {"categories": self.agents_data}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"設定ファイルの保存に失敗しました: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """エージェント統計情報を取得"""
        stats = {
            "total_categories": len(self.agents_data),
            "total_agents": len(self.get_all_agents()),
            "categories": {}
        }
        
        for category, agents in self.agents_data.items():
            stats["categories"][category] = len(agents)
        
        return stats
    
    def search_agents(self, query: str) -> List[Agent]:
        """エージェントを検索"""
        query_lower = query.lower()
        matching_agents = []
        
        for category in self.agents_data:
            for agent_data in self.agents_data[category]:
                if (query_lower in agent_data["name"].lower() or
                    query_lower in agent_data["role"].lower() or
                    query_lower in agent_data["personality"].lower()):
                    agent = Agent(
                        name=agent_data["name"],
                        role=agent_data["role"],
                        personality=agent_data["personality"]
                    )
                    matching_agents.append(agent)
        
        return matching_agents


# 既存のコードとの互換性を保つための関数
def get_available_categories() -> List[str]:
    manager = AgentManager()
    return manager.get_categories()

def get_agents_by_category(category: str) -> List[Agent]:
    manager = AgentManager()
    return manager.get_agents_by_category(category)

def list_agents_in_category(category: str) -> None:
    manager = AgentManager()
    manager.list_agents_in_category(category)

def select_agents_interactive(category: str, max_agents: int) -> List[Agent]:
    manager = AgentManager()
    return manager.select_agents_interactive(category, max_agents)

def select_random_agents_from_all(num_agents: int) -> List[Agent]:
    manager = AgentManager()
    return manager.select_random_agents_from_all(num_agents)

def get_all_agents() -> List[Agent]:
    manager = AgentManager()
    return manager.get_all_agents()


if __name__ == "__main__":
    # テスト実行
    manager = AgentManager()
    stats = manager.get_statistics()
    print("エージェント統計:")
    print(f"総カテゴリ数: {stats['total_categories']}")
    print(f"総エージェント数: {stats['total_agents']}")
    print("\nカテゴリ別エージェント数:")
    for category, count in stats["categories"].items():
        print(f"  {category}: {count}人")