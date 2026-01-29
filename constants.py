import pygame
import os

# ゲーム定数
BOARD_SIZE = 8
SQUARE_SIZE = 60  # 各マスのピクセルサイズ
GRAPH_AREA_WIDTH = 360  # グラフ表示エリアの幅（400から10%小さく）
BOARD_PIXEL_SIZE = BOARD_SIZE * SQUARE_SIZE

# 画面サイズを先に定義（中央配置のため）
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# グラフエリアを左側に配置
GRAPH_OFFSET_X = 20  # 左端から20px
GRAPH_OFFSET_Y = 20  # 上端から20px

# 盤面を中央に配置（グラフエリアの右側）
BOARD_OFFSET_X = GRAPH_OFFSET_X + GRAPH_AREA_WIDTH + 50  # グラフエリアの右側から50px
BOARD_OFFSET_Y = (WINDOW_HEIGHT - BOARD_PIXEL_SIZE) // 2  # 盤面を中央に配置

# 色の定義 (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
LIGHT_GREEN = (0, 192, 0)  # マウスオーバー時のハイライト用
GREY = (100, 100, 100)
RED = (255, 0, 0)  # 無効な手のエラー表示用

# プレイヤーの定義
PLAYER_BLACK = 1  # 人間プレイヤー
PLAYER_WHITE = 2  # AIプレイヤー

# 報酬定数
REWARD_FLIP_PER_STONE = 1   # 裏返した石1つあたりの報酬
REWARD_WIN = 200            # 勝利時の報酬
REWARD_LOSE = -200          # 敗北時の報酬
REWARD_DRAW = 100            # 引き分け時の報酬
REWARD_INVALID_MOVE = -50   # 無効な手へのペナルティ

# 戦略的報酬（自己対戦最適化版）
REWARD_CORNER = 70          # 角を取った時の報酬（60→70に増加）
REWARD_EDGE = -20           # エッジを取った時のペナルティ（-15→-20に強化）
REWARD_STABLE_STONE = 4     # 安定石（角に隣接する石）の報酬（3→4に増加）
REWARD_MOBILITY = 1.0       # 合法手の数に応じた報酬（0.8→1.0に増加）
REWARD_TERRITORY = 0.7      # 盤面の中心部を取った時の報酬（0.5→0.7に増加）
REWARD_POSITIONAL = 0.3     # 位置による報酬（0.2→0.3に増加）
REWARD_PASS_FORCE = 5       # 相手のパスを強制した場合のボーナス（新規追加）

# Q学習用定数（自己対戦最適化）
QTABLE_PATH = "qtable.pkl"  # Qテーブル保存ファイル名
ALPHA = 0.12                # 学習率（0.15→0.12に調整、より安定した学習）
GAMMA = 0.98                # 割引率（0.95→0.98に増加、より長期的視点）
EPSILON = 0.1               # ε-greedy法のランダム行動確率

# ボタン関連の定数
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 50
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (180, 180, 255)
BUTTON_TEXT_COLOR = (0, 0, 0)

# 学習履歴関連の定数
LEARNING_STATS_PATH = "learning_stats.json"  # 学習統計保存ファイル名
HISTORY_SAVE_INTERVAL = 10  # 何ゲームごとに履歴を保存するか

# モード定数
MODE_HUMAN_TRAIN = 0  # 人間vsAIで学習
MODE_AI_PRETRAIN = 1  # AI同士で訓練→人間vsAI

# Pygame初期化・フォント・画面サイズ
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("オセロゲーム")

def get_japanese_font(size):
    font_path = os.path.join(os.path.dirname(__file__), "NotoSansCJKjp-Regular.otf")
    if os.path.exists(font_path):
        return pygame.font.Font(font_path, size)
    win_font = "C:/Windows/Fonts/msgothic.ttc"
    if os.path.exists(win_font):
        return pygame.font.Font(win_font, size)
    for name in ["msgothic", "meiryo", "yugothic", "msmincho", "noto", "hiragino"]:
        try:
            return pygame.font.SysFont(name, size)
        except:
            continue
    return pygame.font.Font(None, size) 