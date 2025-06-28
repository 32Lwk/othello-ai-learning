import pygame
import os

# ゲーム定数
BOARD_SIZE = 8
SQUARE_SIZE = 60  # 各マスのピクセルサイズ
GRAPH_AREA_WIDTH = 400  # グラフ表示エリアの幅
BOARD_OFFSET_X = GRAPH_AREA_WIDTH + 50  # 盤面左上のXオフセット（グラフエリアの右側）
BOARD_OFFSET_Y = 50  # 盤面左上のYオフセット
BOARD_PIXEL_SIZE = BOARD_SIZE * SQUARE_SIZE

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
REWARD_WIN = 100            # 勝利時の報酬
REWARD_LOSE = -100          # 敗北時の報酬
REWARD_DRAW = 50            # 引き分け時の報酬
REWARD_INVALID_MOVE = -50   # 無効な手へのペナルティ

# Q学習用定数
QTABLE_PATH = "qtable.pkl"  # Qテーブル保存ファイル名
ALPHA = 0.1                 # 学習率
GAMMA = 0.9                 # 割引率
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
WINDOW_WIDTH = GRAPH_AREA_WIDTH + BOARD_PIXEL_SIZE + BOARD_OFFSET_X + 50
WINDOW_HEIGHT = BOARD_PIXEL_SIZE + BOARD_OFFSET_Y * 2 + 200
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