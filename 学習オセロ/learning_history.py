import json
import os
import pygame
from datetime import datetime
from collections import deque

class LearningHistory:
    def __init__(self, max_history=100, save_file="learning_history.json"):
        self.max_history = max_history
        self.save_file = save_file
        self.history = deque(maxlen=max_history)
        self.load_history()
    
    def add_record(self, game_count, ai_learn_count, ai_win_count, ai_lose_count, 
                   ai_draw_count, ai_total_reward, ai_avg_reward, qtable_size):
        """学習記録を追加"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "game_count": game_count,
            "ai_learn_count": ai_learn_count,
            "ai_win_count": ai_win_count,
            "ai_lose_count": ai_lose_count,
            "ai_draw_count": ai_draw_count,
            "ai_total_reward": ai_total_reward,
            "ai_avg_reward": ai_avg_reward,
            "qtable_size": qtable_size,
            "win_rate": self._calculate_win_rate(ai_win_count, ai_lose_count, ai_draw_count)
        }
        self.history.append(record)
        self.save_history()
    
    def _calculate_win_rate(self, wins, losses, draws):
        """勝率を計算"""
        total = wins + losses + draws
        return (wins / total * 100) if total > 0 else 0
    
    def save_history(self):
        """履歴をファイルに保存"""
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.history), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"学習履歴の保存エラー: {e}")
    
    def load_history(self):
        """履歴をファイルから読み込み"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = deque(data, maxlen=self.max_history)
        except Exception as e:
            print(f"学習履歴の読み込みエラー: {e}")
            self.history = deque(maxlen=self.max_history)
    
    def get_latest_stats(self):
        """最新の統計を取得"""
        if not self.history:
            return None
        return self.history[-1]
    
    def get_win_rate_history(self):
        """勝率の履歴を取得"""
        return [record["win_rate"] for record in self.history]
    
    def get_avg_reward_history(self):
        """平均報酬の履歴を取得"""
        return [record["ai_avg_reward"] for record in self.history]
    
    def get_learn_count_history(self):
        """学習回数の履歴を取得"""
        return [record["ai_learn_count"] for record in self.history]

class LearningGraph:
    def __init__(self, screen, x, y, width, height):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colors = {
            "background": (240, 240, 240),
            "grid": (200, 200, 200),
            "win_rate": (0, 128, 0),
            "avg_reward": (0, 0, 255),
            "learn_count": (255, 128, 0),
            "text": (0, 0, 0)
        }
    
    def draw_graph(self, history_manager, graph_type="win_rate"):
        """グラフを描画"""
        if not history_manager.history:
            return
        
        # 背景を描画
        pygame.draw.rect(self.screen, self.colors["background"], 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (self.x, self.y, self.width, self.height), 2)
        
        # データを取得
        if graph_type == "win_rate":
            data = history_manager.get_win_rate_history()
            color = self.colors["win_rate"]
            title = "勝率推移"
            y_max = 100
        elif graph_type == "avg_reward":
            data = history_manager.get_avg_reward_history()
            color = self.colors["avg_reward"]
            title = "平均報酬推移"
            y_max = max(data) if data else 10
        elif graph_type == "learn_count":
            data = history_manager.get_learn_count_history()
            color = self.colors["learn_count"]
            title = "学習回数推移"
            y_max = max(data) if data else 1000
        
        if not data:
            return
        
        # タイトルを描画
        try:
            font = pygame.font.Font(None, 20)
            title_surface = font.render(title, True, self.colors["text"])
            self.screen.blit(title_surface, (self.x + 5, self.y + 5))
        except:
            pass
        
        # グリッドを描画
        self._draw_grid(y_max)
        
        # データポイントを描画
        self._draw_data_points(data, color, y_max)
    
    def _draw_grid(self, y_max):
        """グリッドを描画"""
        # 縦線（時間軸）
        for i in range(5):
            x = self.x + (self.width - 20) * i // 4 + 10
            pygame.draw.line(self.screen, self.colors["grid"], 
                           (x, self.y + 20), (x, self.y + self.height - 10))
        
        # 横線（値軸）
        for i in range(5):
            y = self.y + (self.height - 30) * i // 4 + 20
            pygame.draw.line(self.screen, self.colors["grid"], 
                           (self.x + 10, y), (self.x + self.width - 10, y))
    
    def _draw_data_points(self, data, color, y_max):
        """データポイントを描画"""
        if len(data) < 2:
            return
        
        points = []
        for i, value in enumerate(data):
            x = self.x + 10 + (self.width - 20) * i / (len(data) - 1)
            y = self.y + self.height - 10 - (self.height - 30) * value / y_max
            points.append((x, y))
        
        # 線で接続
        if len(points) > 1:
            pygame.draw.lines(self.screen, color, False, points, 2)
        
        # ポイントを描画
        for point in points:
            pygame.draw.circle(self.screen, color, (int(point[0]), int(point[1])), 3)

def create_learning_graphs(screen, history_manager):
    """学習グラフを作成・表示"""
    # グラフの配置
    graph_width = 200
    graph_height = 120
    margin = 10
    
    # 勝率グラフ
    win_rate_graph = LearningGraph(screen, margin, margin, graph_width, graph_height)
    win_rate_graph.draw_graph(history_manager, "win_rate")
    
    # 平均報酬グラフ
    avg_reward_graph = LearningGraph(screen, margin + graph_width + margin, margin, 
                                   graph_width, graph_height)
    avg_reward_graph.draw_graph(history_manager, "avg_reward")
    
    # 学習回数グラフ
    learn_count_graph = LearningGraph(screen, margin, margin + graph_height + margin, 
                                    graph_width, graph_height)
    learn_count_graph.draw_graph(history_manager, "learn_count") 