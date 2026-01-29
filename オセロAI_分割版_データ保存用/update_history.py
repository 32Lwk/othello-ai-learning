#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def update_learning_history():
    """既存の学習履歴ファイルに対戦タイプを追加"""
    
    history_file = "learning_history.json"
    
    if not os.path.exists(history_file):
        print(f"学習履歴ファイル {history_file} が見つかりません。")
        return
    
    try:
        # 既存の履歴を読み込み
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        print(f"既存の履歴データ: {len(history)}件")
        
        # 各記録に対戦タイプを追加
        updated_count = 0
        for record in history:
            if 'game_type' not in record:
                # 既存のデータは人間vsAIとして扱う（過去のデータのため）
                record['game_type'] = 'human_vs_ai'
                updated_count += 1
        
        # 更新された履歴を保存
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        print(f"対戦タイプを追加しました: {updated_count}件")
        print("既存の履歴データは全て「人間vsAI」として分類されました。")
        
    except Exception as e:
        print(f"履歴ファイルの更新中にエラーが発生しました: {e}")

if __name__ == "__main__":
    update_learning_history() 