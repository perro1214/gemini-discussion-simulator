#!/usr/bin/env python3
"""
Agent presets for different discussion perspectives
"""

from typing import List, Dict, Any
from src.agent_classes import Agent

# 教育関連のプリセット
EDUCATION_AGENTS = [
    Agent("田中先生", "ベテラン教師", "実践的で、生徒の学習効果を最優先に考える"),
    Agent("佐藤博士", "AI研究者", "技術的な可能性に詳しく、革新的なアプローチを提案する"),
    Agent("山田さん", "保護者代表", "子どもの安全とプライバシーを心配している"),
    Agent("鈴木校長", "学校管理者", "予算と実現可能性を重視し、制度的な観点から考える"),
    Agent("青木学生", "高校生代表", "実際に学ぶ立場から率直な意見を述べる"),
    Agent("中村先生", "IT教育専門家", "デジタル教育の実践経験が豊富で、現場の課題に詳しい"),
    Agent("伊藤教授", "教育心理学者", "子どもの発達や学習理論の観点から分析する")
]

# ビジネス関連のプリセット
BUSINESS_AGENTS = [
    Agent("高橋CEO", "スタートアップ経営者", "革新的で迅速な意思決定を好む、リスクテイカー"),
    Agent("渡辺部長", "大企業管理職", "安定性と実績を重視し、慎重なアプローチを取る"),
    Agent("加藤CFO", "財務責任者", "コストと収益性を最優先に考える数字重視の視点"),
    Agent("斉藤マネージャー", "プロジェクトマネージャー", "実行可能性とスケジュールを重視する実務派"),
    Agent("小林アナリスト", "市場調査専門家", "データと市場トレンドに基づいて冷静に分析する"),
    Agent("森川CTO", "技術責任者", "技術的な実現可能性と革新性を重視する"),
    Agent("岡田営業", "営業責任者", "顧客ニーズと市場性を最優先に考える現場派")
]

# 社会問題関連のプリセット
SOCIAL_AGENTS = [
    Agent("松本議員", "政治家", "政策的な観点から社会全体への影響を考える"),
    Agent("吉田弁護士", "法律専門家", "法的な問題点とリスクを指摘する慎重派"),
    Agent("石川医師", "医療従事者", "健康と安全を最優先に考える専門家"),
    Agent("木村記者", "ジャーナリスト", "社会への影響と透明性を重視し、批判的な視点を持つ"),
    Agent("大野NGO", "NPO活動家", "社会的弱者の立場から問題を捉える理想主義者"),
    Agent("福田研究員", "社会学者", "社会構造や文化的な影響を学術的に分析する"),
    Agent("池田市民", "一般市民", "日常生活への影響を素朴な視点で考える")
]

# 技術関連のプリセット
TECH_AGENTS = [
    Agent("村上エンジニア", "ソフトウェア開発者", "技術的な実装可能性と効率性を重視する"),
    Agent("清水研究者", "AI研究者", "最新の技術動向と学術的な観点から分析する"),
    Agent("横山デザイナー", "UXデザイナー", "ユーザー体験と使いやすさを最優先に考える"),
    Agent("長谷川セキュリティ", "セキュリティ専門家", "セキュリティリスクと対策を重視する"),
    Agent("藤井PM", "プロダクトマネージャー", "ユーザーニーズと技術のバランスを取る実用主義者"),
    Agent("三浦アーキテクト", "システムアーキテクト", "スケーラビリティと保守性を重視する設計思考"),
    Agent("野村データサイエンティスト", "データ分析専門家", "データドリブンな意思決定を重視する")
]

# 環境・持続可能性関連のプリセット
SUSTAINABILITY_AGENTS = [
    Agent("川口環境学者", "環境科学者", "環境負荷と持続可能性を科学的に分析する"),
    Agent("山本活動家", "環境活動家", "地球環境を守るための急進的な変革を求める"),
    Agent("金子企業", "グリーン企業経営者", "環境配慮と経済性の両立を目指す"),
    Agent("内田政策", "環境政策担当者", "規制と政策的なアプローチで問題解決を図る"),
    Agent("竹内消費者", "環境意識の高い消費者", "日常の選択で環境への影響を考える"),
    Agent("平野科学者", "再生可能エネルギー研究者", "技術革新による環境問題解決を目指す"),
    Agent("柴田農家", "持続可能農業実践者", "実践的な環境配慮の経験を持つ現場の声")
]

# 医療・健康関連のプリセット
HEALTHCARE_AGENTS = [
    Agent("橋本医師", "臨床医", "患者の安全と治療効果を最優先に考える"),
    Agent("坂本研究者", "医学研究者", "科学的エビデンスに基づいた判断を重視する"),
    Agent("田村看護師", "看護師", "患者ケアの質と実現可能性を現場目線で考える"),
    Agent("中島薬剤師", "薬剤師", "薬事法規と安全性を重視する専門家"),
    Agent("井上患者", "患者代表", "治療を受ける立場から率直な意見を述べる"),
    Agent("原田保険", "医療保険担当者", "医療費とコスト効率性を重視する"),
    Agent("菅野公衆衛生", "公衆衛生専門家", "社会全体の健康増進を考える予防重視派")
]

AGENT_PRESETS = {
    "教育": EDUCATION_AGENTS,
    "ビジネス": BUSINESS_AGENTS,
    "社会問題": SOCIAL_AGENTS,
    "技術": TECH_AGENTS,
    "環境・持続可能性": SUSTAINABILITY_AGENTS,
    "医療・健康": HEALTHCARE_AGENTS
}

def get_available_categories() -> List[str]:
    """利用可能なカテゴリー一覧を取得"""
    return list(AGENT_PRESETS.keys())

def get_all_agents() -> List[Agent]:
    """全カテゴリーから全エージェントを取得"""
    all_agents = []
    for agents in AGENT_PRESETS.values():
        all_agents.extend(agents)
    return all_agents

def select_random_agents_from_all(num_agents: int) -> List[Agent]:
    """全カテゴリーからランダムにエージェントを選択"""
    import random
    all_agents = get_all_agents()
    return random.sample(all_agents, min(num_agents, len(all_agents)))

def get_agents_by_category(category: str) -> List[Agent]:
    """カテゴリー別にエージェント一覧を取得"""
    return AGENT_PRESETS.get(category, [])

def list_agents_in_category(category: str) -> None:
    """カテゴリー内のエージェント一覧を表示"""
    agents = get_agents_by_category(category)
    if not agents:
        print(f"カテゴリー '{category}' は存在しません")
        return
    
    print(f"\n=== {category}カテゴリーのエージェント ===")
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.name} ({agent.role})")
        print(f"   性格: {agent.personality}")
    print()

def select_agents_interactive(category: str, max_agents: int = 5) -> List[Agent]:
    """インタラクティブにエージェントを選択"""
    import random
    
    agents = get_agents_by_category(category)
    if not agents:
        print(f"カテゴリー '{category}' は存在しません")
        return []
    
    list_agents_in_category(category)
    
    selected_agents = []
    print(f"最大{max_agents}人まで選択できます。番号をカンマ区切りで入力してください（例: 1,3,5）:")
    print(f"何も入力しなければ、{max_agents}人をランダムに選択します。")
    
    try:
        selection = input("選択: ").strip()
        if not selection:
            # ランダムで指定人数を選択
            selected_agents = random.sample(agents, min(max_agents, len(agents)))
            print(f"ランダムに選択されたエージェント: {', '.join([agent.name for agent in selected_agents])}")
            return selected_agents
        
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        for idx in indices:
            if 0 <= idx < len(agents) and len(selected_agents) < max_agents:
                selected_agents.append(agents[idx])
        
    except (ValueError, IndexError):
        print(f"無効な入力です。ランダムに{max_agents}人を選択します。")
        return random.sample(agents, min(max_agents, len(agents)))
    
    return selected_agents if selected_agents else random.sample(agents, min(max_agents, len(agents)))