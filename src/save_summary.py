#!/usr/bin/env python3
"""
議論要約の簡単保存スクリプト
議論中に生成された要約テキストを簡単に保存するためのユーティリティ
"""

import sys
from discussion_search import DiscussionManager

def main():
    if len(sys.argv) < 2:
        print("使用法: python3 save_summary.py <要約テキスト> [トピック]")
        print("例: python3 save_summary.py '議論の要約内容...' 'AI利用について'")
        sys.exit(1)
    
    summary_text = sys.argv[1]
    topic = sys.argv[2] if len(sys.argv) > 2 else ""
    
    manager = DiscussionManager()
    filepath = manager.save_full_summary(summary_text, topic)
    
    if filepath:
        print(f"要約が保存されました: {filepath}")
    else:
        print("要約の保存に失敗しました。")

if __name__ == "__main__":
    main()