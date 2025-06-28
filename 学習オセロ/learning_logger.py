import json
import os
from datetime import datetime

class LearningLogger:
    def __init__(self, log_file="learning_log.json"):
        self.log_file = log_file
        self.log_data = self.load_log()
    
    def load_log(self):
        """既存のログを読み込む"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"sessions": []}
        return {"sessions": []}
    
    def log_session(self, session_data):
        """学習セッションを記録"""
        session = {
            "timestamp": datetime.now().isoformat(),
            "game_count": session_data.get("game_count", 0),
            "ai_learn_count": session_data.get("ai_learn_count", 0),
            "ai_win_count": session_data.get("ai_win_count", 0),
            "ai_lose_count": session_data.get("ai_lose_count", 0),
            "ai_draw_count": session_data.get("ai_draw_count", 0),
            "ai_total_reward": session_data.get("ai_total_reward", 0),
            "ai_avg_reward": session_data.get("ai_avg_reward", 0),
            "qtable_size": session_data.get("qtable_size", 0)
        }
        
        self.log_data["sessions"].append(session)
        self.save_log()
    
    def save_log(self):
        """ログを保存"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, ensure_ascii=False, indent=2)
    
    def get_learning_progress(self):
        """学習の進行状況を取得"""
        if not self.log_data["sessions"]:
            return None
        
        sessions = self.log_data["sessions"]
        latest = sessions[-1]
        
        # 勝率の計算
        total_games = latest["ai_win_count"] + latest["ai_lose_count"] + latest["ai_draw_count"]
        win_rate = (latest["ai_win_count"] / total_games * 100) if total_games > 0 else 0
        
        return {
            "total_sessions": len(sessions),
            "total_games": latest["game_count"],
            "total_learning": latest["ai_learn_count"],
            "win_rate": win_rate,
            "avg_reward": latest["ai_avg_reward"],
            "qtable_size": latest["qtable_size"]
        }
    
    def print_summary(self):
        """学習状況のサマリーを表示"""
        progress = self.get_learning_progress()
        if not progress:
            print("学習ログがありません。")
            return
        
        print("=== AI学習状況サマリー ===")
        print(f"総セッション数: {progress['total_sessions']}")
        print(f"総ゲーム数: {progress['total_games']}")
        print(f"総学習回数: {progress['total_learning']}")
        print(f"AI勝率: {progress['win_rate']:.1f}%")
        print(f"AI平均報酬: {progress['avg_reward']:.1f}")
        print(f"Qテーブルサイズ: {progress['qtable_size']}")
        
        # 学習の傾向を分析
        if len(self.log_data["sessions"]) > 1:
            first = self.log_data["sessions"][0]
            latest = self.log_data["sessions"][-1]
            
            print("\n=== 学習の進歩 ===")
            print(f"学習回数の増加: {latest['ai_learn_count'] - first['ai_learn_count']}")
            print(f"Qテーブルサイズの増加: {latest['qtable_size'] - first['qtable_size']}")
            
            # 勝率の変化
            first_total = first["ai_win_count"] + first["ai_lose_count"] + first["ai_draw_count"]
            first_win_rate = (first["ai_win_count"] / first_total * 100) if first_total > 0 else 0
            win_rate_change = progress['win_rate'] - first_win_rate
            print(f"勝率の変化: {win_rate_change:+.1f}%")

if __name__ == "__main__":
    logger = LearningLogger()
    logger.print_summary() 