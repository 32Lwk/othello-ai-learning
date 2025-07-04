#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_logic import OthelloGame
from ai_learning import load_qtable, save_qtable, LearningHistory, enhanced_ai_self_play
from constants import *

def main():
    print("🚀 強化版AI自己対戦プログラム")
    print("=" * 50)
    
    # ゲームとQテーブルの初期化
    game = OthelloGame()
    qtable = load_qtable()
    learning_history = LearningHistory()
    
    print(f"📊 現在のQテーブルサイズ: {len(qtable)}")
    
    # 学習モード選択
    print("\n🎯 学習モードを選択してください:")
    print("1. 標準自己対戦 (100ゲーム)")
    print("2. 強化自己対戦 (200ゲーム)")
    print("3. 超強化学習 (500ゲーム)")
    print("4. デバッグテスト (10ゲーム)")
    
    try:
        choice = input("選択 (1-4): ").strip()
        print(f"選択されたオプション: {choice}")
        
        if choice == "1":
            num_games = 100
            print(f"\n🤖 標準自己対戦開始: {num_games}ゲーム")
            ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = enhanced_ai_self_play(
                game, qtable, num_games, learn=True
            )
            
        elif choice == "2":
            num_games = 200
            print(f"\n🔥 強化自己対戦開始: {num_games}ゲーム")
            ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = enhanced_ai_self_play(
                game, qtable, num_games, learn=True
            )
            
        elif choice == "3":
            num_games = 500
            print(f"\n💪 超強化学習開始: {num_games}ゲーム")
            ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = enhanced_ai_self_play(
                game, qtable, num_games, learn=True
            )
            
        elif choice == "4":
            num_games = 10
            print(f"\n🔍 デバッグテスト開始: {num_games}ゲーム")
            print("詳細な学習過程を表示します...")
            ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = enhanced_ai_self_play(
                game, qtable, num_games, learn=True
            )
            
        else:
            print("❌ 無効な選択です。標準自己対戦を実行します。")
            num_games = 100
            ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = enhanced_ai_self_play(
                game, qtable, num_games, learn=True
            )
        
        # 結果の表示
        total_games = ai_win_count + ai_lose_count + ai_draw_count
        win_rate = (ai_win_count / total_games) * 100 if total_games > 0 else 0
        
        print(f"\n🎯 学習完了!")
        print(f"📊 結果:")
        print(f"  総ゲーム数: {total_games}")
        print(f"  AI勝利: {ai_win_count}")
        print(f"  AI敗北: {ai_lose_count}")
        print(f"  引き分け: {ai_draw_count}")
        print(f"  勝率: {win_rate:.1f}%")
        print(f"  総学習回数: {ai_learn_count}")
        print(f"  平均報酬: {ai_avg_reward:.2f}")
        print(f"  Qテーブルサイズ: {len(qtable)}")
        
        # 学習履歴に記録
        learning_history.add_record(
            game_count=total_games,
            ai_learn_count=ai_learn_count,
            ai_win_count=ai_win_count,
            ai_lose_count=ai_lose_count,
            ai_draw_count=ai_draw_count,
            ai_total_reward=ai_total_reward,
            ai_avg_reward=ai_avg_reward,
            qtable_size=len(qtable),
            game_type="ai_vs_ai"
        )
        
        # Qテーブルを保存
        save_qtable(qtable)
        print(f"\n💾 Qテーブルを保存しました")
        
        # 強化効果の評価
        if win_rate > 90:
            print(f"🏆 素晴らしい! AIが非常に強くなりました (勝率: {win_rate:.1f}%)")
        elif win_rate > 80:
            print(f"🎉 優秀! AIが大幅に強化されました (勝率: {win_rate:.1f}%)")
        elif win_rate > 70:
            print(f"👍 良好! AIが強化されました (勝率: {win_rate:.1f}%)")
        elif win_rate > 50:
            print(f"📈 改善が見られます (勝率: {win_rate:.1f}%)")
        else:
            print(f"⚠️ 学習継続が必要です (勝率: {win_rate:.1f}%)")
            print(f"💡 ヒント: 学習パラメータの調整を検討してください")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 学習を中断しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 