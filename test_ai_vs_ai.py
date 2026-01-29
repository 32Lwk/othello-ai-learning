#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_learning import LearningHistory, load_qtable, save_qtable
from game_logic import OthelloGame, PLAYER_BLACK, PLAYER_WHITE
import random

def test_ai_vs_ai():
    """AI同士の自己対戦をテストして対戦タイプを記録"""
    
    # 学習履歴とQテーブルを読み込み
    learning_history = LearningHistory()
    qtable = load_qtable()
    
    print("AI同士の自己対戦を開始します...")
    
    # ゲームを初期化
    game = OthelloGame()
    
    # 統計変数
    ai_learn_count = 0
    ai_total_reward = 0
    ai_avg_reward = 0
    
    # ゲームループ
    while not game.game_over:
        valid_moves = game.get_valid_moves(game.current_player)
        
        if not valid_moves:
            game.switch_player()
            continue
        
        if game.current_player == PLAYER_WHITE:
            # 白（AI）: Q学習で手を選択
            result = game.ai_qlearning_move(qtable, learn=True, player=PLAYER_WHITE, ai_learn_count=ai_learn_count)
            if result:
                reward = game.ai_last_reward
                ai_learn_count += 1
                ai_total_reward += reward
                ai_avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
        else:
            # 黒（同じAI）: 同じQテーブルを使用
            if random.random() < 0.1:  # 10%の確率でランダム行動
                action = random.choice(valid_moves)
            else:
                # Q学習で最適な手を選択
                state_key = game.get_board_state_key()
                best_move = None
                best_q_value = float('-inf')
                valid_moves_list = list(valid_moves) if valid_moves else []
                for move in valid_moves_list:
                    action_key = f"{state_key}_{move[0]}_{move[1]}"
                    q_value = qtable.get(action_key, 0.0)
                    if q_value > best_q_value:
                        best_q_value = q_value
                        best_move = move
                action = best_move if best_move is not None else random.choice(valid_moves)
            
            # 黒も実際に手を打って学習する
            result = game.ai_qlearning_move(qtable, learn=True, player=PLAYER_BLACK, ai_learn_count=ai_learn_count)
            if result:
                reward = game.ai_last_reward
                ai_learn_count += 1
                ai_total_reward += reward
                ai_avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
        
        game.switch_player()
        game.check_game_over()
    
    # 勝敗集計
    black_score, white_score = game.get_score()
    if black_score > white_score:
        ai_win_count = 0
        ai_lose_count = 1
        ai_draw_count = 0
    elif white_score > black_score:
        ai_win_count = 1
        ai_lose_count = 0
        ai_draw_count = 0
    else:
        ai_win_count = 0
        ai_lose_count = 0
        ai_draw_count = 1
    
    # 学習履歴に記録（AI同士の対戦として）
    learning_history.add_record(
        1, ai_learn_count, ai_win_count, ai_lose_count, 
        ai_draw_count, ai_total_reward, ai_avg_reward, len(qtable), black_score, white_score, "ai_vs_ai"
    )
    
    print(f"AI同士の対戦完了:")
    print(f"  結果: 黒{black_score} - 白{white_score}")
    print(f"  AI（白）勝利: {ai_win_count}回")
    print(f"  AI（黒）勝利: {ai_lose_count}回")
    print(f"  引き分け: {ai_draw_count}回")
    print(f"  学習回数: {ai_learn_count}")
    print(f"  平均報酬: {ai_avg_reward:.2f}")
    print(f"  対戦タイプ: ai_vs_ai")
    
    # Qテーブルを保存
    save_qtable(qtable)
    
    print("対戦記録が「AI同士」として保存されました。")

if __name__ == "__main__":
    test_ai_vs_ai() 