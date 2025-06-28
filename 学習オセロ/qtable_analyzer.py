import pickle
import os
from collections import Counter

def analyze_qtable(qtable_path="qtable.pkl"):
    """Qテーブルの分析を行う"""
    if not os.path.exists(qtable_path):
        print("Qテーブルファイルが見つかりません。")
        return
    
    with open(qtable_path, "rb") as f:
        qtable = pickle.load(f)
    
    print("=== Qテーブル分析結果 ===")
    print(f"総エントリ数: {len(qtable)}")
    
    # Q値の統計
    q_values = list(qtable.values())
    if q_values:
        print(f"Q値の範囲: {min(q_values):.2f} ~ {max(q_values):.2f}")
        print(f"Q値の平均: {sum(q_values)/len(q_values):.2f}")
        
        # 正のQ値と負のQ値の分布
        positive_q = [q for q in q_values if q > 0]
        negative_q = [q for q in q_values if q < 0]
        print(f"正のQ値: {len(positive_q)}個 ({len(positive_q)/len(q_values)*100:.1f}%)")
        print(f"負のQ値: {len(negative_q)}個 ({len(negative_q)/len(q_values)*100:.1f}%)")
    
    # 状態の分析
    states = set()
    actions = set()
    for (state, action) in qtable.keys():
        states.add(state)
        actions.add(action)
    
    print(f"学習された状態数: {len(states)}")
    print(f"学習された行動数: {len(actions)}")
    
    # 最も高いQ値を持つ行動トップ10
    print("\n=== 最も高いQ値を持つ行動トップ10 ===")
    sorted_actions = sorted(qtable.items(), key=lambda x: x[1], reverse=True)
    for i, ((state, action), q_value) in enumerate(sorted_actions[:10]):
        print(f"{i+1}. Q値: {q_value:.2f}, 行動: {action}")
    
    # 最も低いQ値を持つ行動トップ10
    print("\n=== 最も低いQ値を持つ行動トップ10 ===")
    sorted_actions_low = sorted(qtable.items(), key=lambda x: x[1])
    for i, ((state, action), q_value) in enumerate(sorted_actions_low[:10]):
        print(f"{i+1}. Q値: {q_value:.2f}, 行動: {action}")

def compare_qtables(qtable1_path, qtable2_path):
    """2つのQテーブルを比較する"""
    if not os.path.exists(qtable1_path) or not os.path.exists(qtable2_path):
        print("Qテーブルファイルが見つかりません。")
        return
    
    with open(qtable1_path, "rb") as f:
        qtable1 = pickle.load(f)
    with open(qtable2_path, "rb") as f:
        qtable2 = pickle.load(f)
    
    print("=== Qテーブル比較 ===")
    print(f"Qテーブル1のエントリ数: {len(qtable1)}")
    print(f"Qテーブル2のエントリ数: {len(qtable2)}")
    
    # 共通の状態-行動ペア
    common_keys = set(qtable1.keys()) & set(qtable2.keys())
    print(f"共通の状態-行動ペア数: {len(common_keys)}")
    
    if common_keys:
        # 共通部分でのQ値の変化
        q_changes = []
        for key in common_keys:
            change = qtable2[key] - qtable1[key]
            q_changes.append(change)
        
        print(f"Q値の平均変化: {sum(q_changes)/len(q_changes):.2f}")
        print(f"Q値の最大変化: {max(q_changes):.2f}")
        print(f"Q値の最小変化: {min(q_changes):.2f}")

if __name__ == "__main__":
    # 現在のQテーブルを分析
    analyze_qtable()
    
    # バックアップファイルがあれば比較
    if os.path.exists("qtable_backup.pkl"):
        print("\n" + "="*50)
        compare_qtables("qtable_backup.pkl", "qtable.pkl") 