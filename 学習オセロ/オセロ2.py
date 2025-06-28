import pygame
import sys
import random
import time
import pickle  # Qテーブル保存・読み込み用
import os      # ファイル存在確認用
import json    # 学習履歴保存用
from typing import Optional  # 型ヒント用
from datetime import datetime  # タイムスタンプ用
from collections import deque  # 履歴管理用

# 学習履歴管理クラスを定義
class LearningHistory:
    def __init__(self, max_history=100, save_file="learning_history.json"):
        self.max_history = max_history
        self.save_file = save_file
        self.history = deque(maxlen=max_history)
        self.load_history()
    
    def add_record(self, game_count, ai_learn_count, ai_win_count, ai_lose_count, 
                   ai_draw_count, ai_total_reward, ai_avg_reward, qtable_size, black_score=0, white_score=0):
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
            "black_score": black_score,
            "white_score": white_score,
            "win_rate": self._calculate_win_rate(ai_win_count, ai_lose_count, ai_draw_count)
        }
        
        self.history.append(record)
        
        # 最大履歴数を超えた場合、古い記録を削除
        if len(self.history) > self.max_history:
            # dequeのmaxlenを使用して自動的に古い記録を削除
            # 手動でのスライス操作は不要
            pass
        
        # 履歴を保存
        self.save_history()
    def _calculate_win_rate(self, wins, losses, draws):
        total = wins + losses + draws
        return (wins / total * 100) if total > 0 else 0
    
    def save_history(self):
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.history), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"学習履歴の保存エラー: {e}")
    
    def load_history(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = deque(data, maxlen=self.max_history)
        except Exception as e:
            print(f"学習履歴の読み込みエラー: {e}")
            self.history = deque(maxlen=self.max_history)
    
    def get_win_rate_history(self):
        return [record["win_rate"] for record in self.history]
    
    def get_avg_reward_history(self):
        return [record["ai_avg_reward"] for record in self.history]
    
    def get_learn_count_history(self):
        return [record["ai_learn_count"] for record in self.history]
    
    def get_latest_stats(self):
        """最新の統計を取得"""
        if not self.history:
            return None
        return self.history[-1]
    
    def save_history_to_file(self, filename):
        """指定されたファイルに学習履歴を保存"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(list(self.history), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"学習履歴の保存エラー ({filename}): {e}")
    
    def load_history_from_file(self, filename):
        """指定されたファイルから学習履歴を読み込み"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = deque(data, maxlen=self.max_history)
            else:
                # ファイルが存在しない場合は空の履歴で初期化
                self.history = deque(maxlen=self.max_history)
        except Exception as e:
            print(f"学習履歴の読み込みエラー ({filename}): {e}")
            self.history = deque(maxlen=self.max_history)

class LearningGraph:
    def __init__(self):
        pass
    
    def plot_learning_progress(self, history):
        # 簡易版のグラフ表示機能
        print("学習進捗グラフ表示機能は利用できません")

class LearningLogger:
    def __init__(self, log_file="learning_log.json"):
        self.log_file = log_file
        self.log_data = self.load_log()
    
    def load_log(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"sessions": []}
        return {"sessions": []}
    
    def log_session(self, session_data):
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
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, ensure_ascii=False, indent=2)

# ゲーム定数
BOARD_SIZE = 8
SQUARE_SIZE = 60 # 各マスのピクセルサイズ
GRAPH_AREA_WIDTH = 400  # グラフ表示エリアの幅
BOARD_OFFSET_X = GRAPH_AREA_WIDTH + 50  # 盤面左上のXオフセット（グラフエリアの右側）
BOARD_OFFSET_Y = 50 # 盤面左上のYオフセット
BOARD_PIXEL_SIZE = BOARD_SIZE * SQUARE_SIZE

# 色の定義 (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
LIGHT_GREEN = (0, 192, 0) # マウスオーバー時のハイライト用
GREY = (100, 100, 100)
RED = (255, 0, 0) # 無効な手のエラー表示用

# プレイヤーの定義
PLAYER_BLACK = 1 # 人間プレイヤー
PLAYER_WHITE = 2 # AIプレイヤー

# 報酬定数
REWARD_FLIP_PER_STONE = 1   # 裏返した石1つあたりの報酬
REWARD_WIN = 100            # 勝利時の報酬
REWARD_LOSE = -100          # 敗北時の報酬
REWARD_DRAW = 50            # 引き分け時の報酬
REWARD_INVALID_MOVE = -50   # 無効な手へのペナルティ (AIが打つことはないが念のため)

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

# グローバル変数
ai_learn_count = 0
game_count = 0  # 何ゲーム目か
move_count = 0  # 何手目か
last_move_count = 0  # 前回の手数（チカチカ防止用）
win_black = 0  # AI同士の対戦での黒AI勝利回数
win_white = 0  # AI同士の対戦での白AI勝利回数

# 学習統計用の変数を追加
ai_total_reward = 0
ai_avg_reward = 0    # AIの平均報酬
ai_win_count = 0     # AIの勝利回数
ai_lose_count = 0    # AIの敗北回数
ai_draw_count = 0    # AIの引き分け回数

# モード定数
MODE_HUMAN_TRAIN = 0  # 人間vsAIで学習
MODE_AI_PRETRAIN = 1  # AI同士で訓練→人間vsAI

# モード管理変数
current_mode = None

# AI設定変数
ai_speed = 60  # AIの思考速度（フレーム数）
pretrain_total = 10  # AI同士の対戦回数
fast_mode = True  # 高速モード
draw_mode = True  # 描画モード
DEBUG_MODE = False  # デバッグモード

# 訓練関連変数
pretrain_in_progress = False  # AI同士の訓練中かどうか
pretrain_now = 0  # 現在の訓練回数

# 学習履歴管理オブジェクト
learning_history = LearningHistory(max_history=50)
learning_logger = LearningLogger()

# 学習履歴の初期状態を確認
print(f"学習履歴の初期状態: {len(learning_history.history)}件のデータ")
if learning_history.history:
    latest = learning_history.get_latest_stats()
    if latest:
        print(f"最新データ: ゲーム数={latest['game_count']}, 学習回数={latest['ai_learn_count']}, 勝率={latest['win_rate']:.1f}%")
        print(f"平均報酬: {latest['ai_avg_reward']:.2f}, 累積報酬: {latest['ai_total_reward']}")

# --- ここでqtableを定義 ---
# qtable = load_qtable()

# Qテーブルの初期状態を確認
# print(f"Qテーブル初期状態: {len(qtable)}件のエントリ")
# if len(qtable) > 0:
#     sample_items = list(qtable.items())[:3]
#     for key, value in sample_items:
#         print(f"  Q値サンプル: {key} -> {value}")

# --- ここから追加 ---
class OthelloGame:
    def __init__(self):
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.board[3][3] = PLAYER_WHITE
        self.board[4][4] = PLAYER_WHITE
        self.board[3][4] = PLAYER_BLACK
        self.board[4][3] = PLAYER_BLACK
        self.current_player = PLAYER_BLACK
        self.game_over = False
        self.message = "黒の番です。"
        self.highlighted_square: Optional[tuple[int, int]] = None
        self.last_move_error = False
        self.ai_last_reward = 0
        self.last_ai_move = None
        self.game_over_displayed = False
        self.error_message = ""
        self.error_start_time = 0
        self.error_display_duration = 1000
        self.notice_message = ""
        self.notice_start_time = 0
        self.notice_display_duration = 1000
        global move_count
        move_count = 0

    def _get_flipped_stones(self, r, c, player):
        """指定された位置(r, c)にplayerが石を置いた場合に裏返せる石のリストを返す"""
        if self.board[r][c] != 0:
            return []

        flipped_stones = []
        opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK

        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            current_direction_flipped = []
            nr, nc = r + dr, c + dc

            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == opponent:
                current_direction_flipped.append((nr, nc))
                nr += dr
                nc += dc

            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == player and len(current_direction_flipped) > 0:
                flipped_stones.extend(current_direction_flipped)

        return flipped_stones

    def get_valid_moves(self, player):
        """指定されたプレイヤーの有効な手を取得"""
        valid_moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == 0 and self.is_valid_move(r, c, player):
                    valid_moves.append((r, c))
        return valid_moves

    def is_valid_move(self, row, col, player):
        """指定された位置が有効な手かどうかを判定"""
        if self.board[row][col] != 0:
            return False
        
        opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            if self._can_flip_in_direction(row, col, dr, dc, player, opponent):
                return True
        return False

    def _can_flip_in_direction(self, row, col, dr, dc, player, opponent):
        """指定された方向に石を裏返せるかどうかを判定"""
        r, c = row + dr, col + dc
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            return False
        if self.board[r][c] != opponent:
            return False
        
        r, c = r + dr, c + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if self.board[r][c] == 0:
                return False
            if self.board[r][c] == player:
                return True
            r, c = r + dr, c + dc
        return False

    def make_move(self, row, col, player):
        """指定された位置に石を置き、裏返しを実行"""
        if not self.is_valid_move(row, col, player):
            return False
        
        flipped_stones = self._get_flipped_stones(row, col, player)
        self.board[row][col] = player
        for fr, fc in flipped_stones:
            self.board[fr][fc] = player
        
        global move_count
        move_count += 1
        
        if player == PLAYER_WHITE:
            self.ai_last_reward = len(flipped_stones) * REWARD_FLIP_PER_STONE
        
        return len(flipped_stones)

    def _flip_in_direction(self, row, col, dr, dc, player, opponent):
        """指定された方向の石を裏返す"""
        to_flip = []
        r, c = row + dr, col + dc
        
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if self.board[r][c] == opponent:
                to_flip.append((r, c))
            elif self.board[r][c] == player:
                for flip_r, flip_c in to_flip:
                    self.board[flip_r][flip_c] = player
                return len(to_flip)
            else:
                break
            r, c = r + dr, c + dc
        return 0

    def switch_player(self):
        """プレイヤーを切り替え"""
        self.current_player = PLAYER_WHITE if self.current_player == PLAYER_BLACK else PLAYER_BLACK
        self.message = f"{'黒' if self.current_player == PLAYER_BLACK else '白'}の番です。"
        self.last_move_error = False

    def check_game_over(self):
        """ゲーム終了判定"""
        if self.game_over:
            return True

        black_moves = self.get_valid_moves(PLAYER_BLACK)
        white_moves = self.get_valid_moves(PLAYER_WHITE)

        if not black_moves and not white_moves:
            self.game_over = True
            black_score, white_score = self.get_score()
            if black_score > white_score:
                self.message = f"黒の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
            elif white_score > black_score:
                self.message = f"白の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
            else:
                self.message = f"引き分け！ (スコア: 黒{black_score} - 白{white_score})"
            return True
        
        if all(self.board[r][c] != 0 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)):
            self.game_over = True
            black_score, white_score = self.get_score()
            if black_score > white_score:
                self.message = f"黒の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
            elif white_score > black_score:
                self.message = f"白の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
            else:
                self.message = f"引き分け！ (スコア: 黒{black_score} - 白{white_score})"
            return True

        return False

    def get_score(self):
        """現在のスコア（石の数）を計算して返す"""
        black_count = sum(row.count(PLAYER_BLACK) for row in self.board)
        white_count = sum(row.count(PLAYER_WHITE) for row in self.board)
        return black_count, white_count

    def get_winner(self):
        """勝者を判定"""
        black_count = sum(row.count(PLAYER_BLACK) for row in self.board)
        white_count = sum(row.count(PLAYER_WHITE) for row in self.board)
        
        if black_count > white_count:
            return PLAYER_BLACK
        elif white_count > black_count:
            return PLAYER_WHITE
        else:
            return 0  # 引き分け

    def calculate_game_result_reward(self, player):
        """ゲーム終了時の最終報酬を計算する"""
        black_score, white_score = self.get_score()

        if player == PLAYER_BLACK:
            if black_score > white_score:
                return REWARD_WIN
            elif black_score < white_score:
                return REWARD_LOSE
            else:
                return REWARD_DRAW
        else:  # player == PLAYER_WHITE (AI)
            if white_score > black_score:
                return REWARD_WIN
            elif white_score < black_score:
                return REWARD_LOSE
            else:
                return REWARD_DRAW

    def get_board_state_key(self):
        """盤面状態を文字列キーに変換"""
        return ''.join(str(cell) for row in self.board for cell in row)

    def ai_qlearning_move(self, qtable, learn=True, player=None):
        """Q学習に基づくAIの手選び・Q値更新"""
        if player is None:
            player = self.current_player
            
        state_key = self.get_board_state_key()
        valid_moves = self.get_valid_moves(player)
        if not valid_moves:
            self.ai_last_reward = 0
            self.last_ai_move = None
            self.message = f"AI（{'黒' if player == PLAYER_BLACK else '白'}）はパスしました。"
            return False

        # ε-greedy法で行動選択
        if random.random() < EPSILON:
            action = random.choice(valid_moves)
        else:
            # Q値が最大の行動を選択
            best_move = None
            best_q_value = float('-inf')
            
            for move in valid_moves:
                action_key = f"{state_key}_{move[0]}_{move[1]}"
                q_value = qtable.get(action_key, 0.0)
                if q_value > best_q_value:
                    best_q_value = q_value
                    best_move = move
            
            if best_move is None:
                action = random.choice(valid_moves)
            else:
                action = best_move

        # 実際に手を打つ
        r, c = action
        flipped = self._get_flipped_stones(r, c, player)
        reward = len(flipped) * REWARD_FLIP_PER_STONE
        self.make_move(r, c, player)
        self.message = f"{'黒' if player == PLAYER_BLACK else '白'} (Q学習AI) が {chr(ord('A') + c)}{r+1} に置きました。(報酬: {reward})"
        self.ai_last_reward = reward
        self.last_ai_move = (r, c)

        # Q値更新
        if learn:
            next_state_key = self.get_board_state_key()
            next_player = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
            next_valid_moves = self.get_valid_moves(next_player)
            
            # 次の状態での最大Q値を計算
            max_next_q = 0.0
            if next_valid_moves:
                max_next_q = max(qtable.get(f"{next_state_key}_{move[0]}_{move[1]}", 0.0) 
                               for move in next_valid_moves)
            else:
                max_next_q = self.calculate_game_result_reward(player)
            
            # Q値を更新
            action_key = f"{state_key}_{action[0]}_{action[1]}"
            current_q = qtable.get(action_key, 0.0)
            new_q = current_q + ALPHA * (reward + GAMMA * max_next_q - current_q)
            qtable[action_key] = new_q
            
            global pretrain_in_progress, ai_learn_count, ai_total_reward, ai_avg_reward
            if not pretrain_in_progress:
                self.save_qtable()
            ai_learn_count += 1
            ai_total_reward += reward
            # ゼロ除算を防ぐ
            if ai_learn_count > 0:
                ai_avg_reward = ai_total_reward / ai_learn_count
            else:
                ai_avg_reward = ai_total_reward
        return True

    def get_ai_move(self):
        """AIの手番を決定"""
        valid_moves = self.get_valid_moves(PLAYER_WHITE)
        if not valid_moves:
            return None
        
        state_key = self.get_board_state_key()
        
        # ε-greedy法で行動選択
        if random.random() < EPSILON:
            return random.choice(valid_moves)
        
        # Q値が最大の行動を選択
        best_move = None
        best_q_value = float('-inf')
        
        for move in valid_moves:
            action_key = f"{state_key}_{move[0]}_{move[1]}"
            q_value = qtable.get(action_key, 0.0)
            if q_value > best_q_value:
                best_q_value = q_value
                best_move = move
        
        if best_move is None:
            best_move = random.choice(valid_moves)
        
        return best_move

    def update_q_value(self, state_key, action, reward, next_state_key, next_valid_moves):
        """Q値を更新"""
        action_key = f"{state_key}_{action[0]}_{action[1]}"
        
        # 現在のQ値
        current_q = qtable.get(action_key, 0.0)
        
        # 次の状態での最大Q値
        max_next_q = 0.0
        if next_valid_moves:
            max_next_q = max(qtable.get(f"{next_state_key}_{move[0]}_{move[1]}", 0.0) 
                           for move in next_valid_moves)
        
        # Q学習の更新式
        new_q = current_q + ALPHA * (reward + GAMMA * max_next_q - current_q)
        qtable[action_key] = new_q

    def save_qtable(self):
        """Qテーブルを保存"""
        try:
            with open(QTABLE_PATH, "wb") as f:
                pickle.dump(qtable, f)
        except Exception as e:
            print(f"Qテーブルの保存エラー: {e}")

    def reset_game(self):
        """ゲームをリセット"""
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.board[3][3] = PLAYER_WHITE
        self.board[4][4] = PLAYER_WHITE
        self.board[3][4] = PLAYER_BLACK
        self.board[4][3] = PLAYER_BLACK
        self.current_player = PLAYER_BLACK
        self.game_over = False
        self.message = "黒の番です。"
        self.highlighted_square = None
        self.last_move_error = False
        self.ai_last_reward = 0
        self.last_ai_move = None
        self.game_over_displayed = False
        self.error_message = ""
        self.error_start_time = 0
        global move_count
        move_count = 0

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

font = get_japanese_font(36)
small_font = get_japanese_font(24)
tiny_font = get_japanese_font(20)

def load_qtable():
    try:
        if os.path.exists(QTABLE_PATH):
            with open(QTABLE_PATH, "rb") as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Qテーブルの読み込みエラー: {e}")
    return {}

def save_qtable(qtable):
    try:
        with open(QTABLE_PATH, "wb") as f:
            pickle.dump(qtable, f)
    except Exception as e:
        print(f"Qテーブルの保存エラー: {e}")

# 盤面をQテーブルのキーとして使えるように変換
def board_to_key(board, player):
    return tuple(tuple(row) for row in board), player

qtable = load_qtable()
print(f"Qテーブル初期状態: {len(qtable)}件のエントリ")
if len(qtable) > 0:
    sample_items = list(qtable.items())[:3]
    for key, value in sample_items:
        print(f"  Q値サンプル: {key} -> {value}")

game = OthelloGame()
# --- ここまで追加 --- 

# --- 盤面・石・手番・エラーメッセージ描画 ---
def draw_board(screen, game_board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            x = c * SQUARE_SIZE + BOARD_OFFSET_X
            y = r * SQUARE_SIZE + BOARD_OFFSET_Y
            pygame.draw.rect(screen, GREEN, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.rect(screen, BLACK, (x, y, SQUARE_SIZE, SQUARE_SIZE), 1)

            # マウスオーバーしているマスをハイライト
            if game.highlighted_square == (r, c):
                pygame.draw.rect(screen, LIGHT_GREEN, (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)

            # 直前のAIの手を赤枠でハイライト
            if game.last_ai_move == (r, c):
                pygame.draw.rect(screen, RED, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

            # 有効な手を薄い点で表示 (人間プレイヤーの番のみ)
            if (r, c) in game.get_valid_moves(PLAYER_BLACK) and game.current_player == PLAYER_BLACK:
                 pygame.draw.circle(screen, GREY, (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2), 5)

def draw_stones(screen, game_board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            stone = game_board[r][c]
            if stone != 0:
                center_x = c * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_X
                center_y = r * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_Y
                radius = SQUARE_SIZE // 2 - 5
                color = BLACK if stone == PLAYER_BLACK else WHITE
                pygame.draw.circle(screen, color, (center_x, center_y), radius)

def draw_current_player_indicator(screen, current_player):
    indicator_x = WINDOW_WIDTH - 120
    indicator_y = 20
    indicator_size = 40
    pygame.draw.rect(screen, (240, 240, 240), (indicator_x, indicator_y, 100, indicator_size))
    pygame.draw.rect(screen, (100, 100, 100), (indicator_x, indicator_y, 100, indicator_size), 2)
    stone_color = BLACK if current_player == PLAYER_BLACK else WHITE
    stone_center_x = indicator_x + 20
    stone_center_y = indicator_y + indicator_size // 2
    pygame.draw.circle(screen, stone_color, (stone_center_x, stone_center_y), 15)
    player_text = "黒" if current_player == PLAYER_BLACK else "白"
    text_surface = tiny_font.render(f"{player_text}の番", True, (0, 0, 0))
    screen.blit(text_surface, (indicator_x + 45, indicator_y + 10))

def display_error_message(screen, message):
    if not message:
        return
    overlay = pygame.Surface((BOARD_PIXEL_SIZE, BOARD_PIXEL_SIZE))
    overlay.set_alpha(200)
    overlay.fill((255, 255, 255))
    screen.blit(overlay, (BOARD_OFFSET_X, BOARD_OFFSET_Y))
    error_font = get_japanese_font(28)
    text_surface = error_font.render(message, True, RED)
    text_rect = text_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2))
    screen.blit(text_surface, text_rect)

def display_game_result(screen, result_message, ai_reward=0):
    """ゲーム結果を盤面の最前面に表示"""
    # 半透明のオーバーレイ
    overlay = pygame.Surface((BOARD_PIXEL_SIZE, BOARD_PIXEL_SIZE))
    overlay.set_alpha(180)
    overlay.fill((255, 255, 255))
    screen.blit(overlay, (BOARD_OFFSET_X, BOARD_OFFSET_Y))
    
    # 結果メッセージ
    result_font = get_japanese_font(32)
    result_surface = result_font.render(result_message, True, (255, 0, 0))
    result_rect = result_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2 - 30))
    screen.blit(result_surface, result_rect)
    
    # AI報酬（ある場合）
    if ai_reward != 0:
        reward_font = get_japanese_font(24)
        reward_text = f"AI最終報酬: {ai_reward}"
        reward_surface = reward_font.render(reward_text, True, (0, 0, 255))
        reward_rect = reward_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2 + 10))
        screen.blit(reward_surface, reward_rect)
    
    # 次の対戦への案内
    next_font = get_japanese_font(20)
    next_text = "盤面をクリックして次の対戦へ"
    next_surface = next_font.render(next_text, True, (0, 0, 0))
    next_rect = next_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2 + 50))
    screen.blit(next_surface, next_rect)

def display_notice_message(screen, message, start_time, duration=1000):
    """注意メッセージを1秒間のみ表示"""
    current_time = pygame.time.get_ticks()
    if current_time - start_time > duration:
        return False  # 表示終了
    
    # 半透明のオーバーレイ
    overlay = pygame.Surface((BOARD_PIXEL_SIZE, BOARD_PIXEL_SIZE))
    overlay.set_alpha(150)
    overlay.fill((255, 255, 255))
    screen.blit(overlay, (BOARD_OFFSET_X, BOARD_OFFSET_Y))
    
    # 注意メッセージ
    notice_font = get_japanese_font(26)
    text_surface = notice_font.render(message, True, RED)
    text_rect = text_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2))
    screen.blit(text_surface, text_rect)
    
    return True  # 表示中

def display_message(screen, message, is_error=False):
    """画面下部にメッセージを表示する"""
    color = RED if is_error else BLACK
    max_width = WINDOW_WIDTH - 40
    lines = []
    words = message.split(' ')
    line = ''
    for word in words:
        test_line = line + (' ' if line else '') + word
        test_surface = font.render(test_line, True, color)
        if test_surface.get_width() > max_width:
            if line:
                lines.append(line)
            line = word
        else:
            line = test_line
    if line:
        lines.append(line)
    
    for i, l in enumerate(lines):
        text_surface = font.render(l, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 40 + i * 36))
        screen.blit(text_surface, text_rect)

def display_score(screen, black_score, white_score):
    """スコアを表示する"""
    black_text = small_font.render(f"黒: {black_score}", True, BLACK)
    white_text = small_font.render(f"白: {white_score}", True, BLACK)
    screen.blit(black_text, (BOARD_OFFSET_X, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 10))
    screen.blit(white_text, (WINDOW_WIDTH - BOARD_OFFSET_X - white_text.get_width(), BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 10))

def display_ai_reward(screen, reward):
    """AIの最新報酬を表示する"""
    reward_text = tiny_font.render(f"AI報酬: {reward}", True, BLACK)
    screen.blit(reward_text, (BOARD_OFFSET_X + 10, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 35))

def draw_progress_bar(screen, current, total, x, y, width, height):
    """プログレスバーを描画する"""
    # 背景
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height))
    pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height), 2)
    
    # 進捗バー
    if total > 0:
        progress_width = int((current / total) * (width - 4))
        if progress_width > 0:
            pygame.draw.rect(screen, (0, 255, 0), (x + 2, y + 2, progress_width, height - 4))
    
    # 進捗テキスト
    progress_text = f"{current}/{total}"
    text_surface = font.render(progress_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

def draw_learn_count(screen, font):
    """学習回数を表示"""
    text = font.render(f"AI学習回数: {ai_learn_count}", True, (0,0,0))
    screen.blit(text, (BOARD_OFFSET_X, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 60))

def draw_pretrain_count(screen, font):
    """AI訓練回数を表示"""
    text = font.render(f"AI訓練: {pretrain_now}/{pretrain_total}", True, (0,0,0))
    screen.blit(text, (BOARD_OFFSET_X, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 85))

def draw_game_count(screen, font):
    """対戦回数を表示"""
    text = font.render(f"対戦回数: {game_count}", True, (0,0,0))
    y = BOARD_OFFSET_Y // 2 - text.get_height() // 2
    screen.blit(text, (BOARD_OFFSET_X, y))

def draw_move_count(screen, font):
    """手数を表示する"""
    global move_count, last_move_count
    if move_count != last_move_count:
        text = font.render(f"手数: {move_count}", True, BLACK)
        x = BOARD_OFFSET_X + BOARD_PIXEL_SIZE - text.get_width()
        y = BOARD_OFFSET_Y // 2 - text.get_height() // 2
        screen.blit(text, (x, y))
        last_move_count = move_count

# --- グラフ・ボタン・メインループ雛形 ---
def draw_learning_graphs(screen):
    # グラフエリアの背景
    pygame.draw.rect(screen, (245, 245, 245), (0, 0, GRAPH_AREA_WIDTH, WINDOW_HEIGHT))
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, GRAPH_AREA_WIDTH, WINDOW_HEIGHT), 2)
    
    # タイトル
    title_font = get_japanese_font(16)
    title_text = title_font.render("学習進捗", True, (0, 0, 0))
    screen.blit(title_text, (10, 10))
    
    # 統計情報の表示（よりコンパクトに）
    stats_font = get_japanese_font(11)
    y_offset = 35
    
    # ゲーム数
    game_text = stats_font.render(f"ゲーム数: {game_count}", True, (0, 0, 0))
    screen.blit(game_text, (10, y_offset))
    y_offset += 18
    
    # AI学習回数
    learn_text = stats_font.render(f"学習回数: {ai_learn_count}", True, (0, 0, 0))
    screen.blit(learn_text, (10, y_offset))
    y_offset += 18
    
    # 勝率
    win_rate = 0
    if ai_win_count + ai_lose_count + ai_draw_count > 0:
        win_rate = ai_win_count / (ai_win_count + ai_lose_count + ai_draw_count) * 100
        win_rate_text = stats_font.render(f"勝率: {win_rate:.1f}%", True, (0, 0, 0))
        screen.blit(win_rate_text, (10, y_offset))
        y_offset += 18
    
    # 平均報酬
    if ai_learn_count > 0:
        avg_reward_text = stats_font.render(f"平均報酬: {ai_avg_reward:.1f}", True, (0, 0, 0))
        screen.blit(avg_reward_text, (10, y_offset))
        y_offset += 18
    
    # Qテーブルサイズ
    qtable_size = len(qtable)
    qtable_text = stats_font.render(f"Qテーブル: {qtable_size}", True, (0, 0, 0))
    screen.blit(qtable_text, (10, y_offset))
    y_offset += 25
    
    # AI学習レベル
    ai_level = calculate_ai_level(win_rate, ai_avg_reward, ai_learn_count, qtable_size)
    level_description = get_level_description(ai_level)
    
    # レベル表示（目立つように）
    level_font = get_japanese_font(13)
    level_color = (255, 0, 0) if ai_level >= 8 else (255, 165, 0) if ai_level >= 6 else (0, 100, 200)
    level_text = level_font.render(f"AIレベル: {ai_level} ({level_description})", True, level_color)
    screen.blit(level_text, (10, y_offset))
    y_offset += 20
    
    # レベルプログレスバー
    progress_width = GRAPH_AREA_WIDTH - 20
    progress_height = 12
    progress_x = 10
    progress_y = y_offset
    
    # プログレスバー背景
    pygame.draw.rect(screen, (200, 200, 200), (progress_x, progress_y, progress_width, progress_height))
    pygame.draw.rect(screen, (100, 100, 100), (progress_x, progress_y, progress_width, progress_height), 1)
    
    # レベルに応じたプログレス
    level_progress = (ai_level / 10) * progress_width
    if level_progress > 0:
        pygame.draw.rect(screen, level_color, (progress_x, progress_y, level_progress, progress_height))
    
    y_offset += 20
    
    # グラフエリアの開始位置を調整（より下に）
    graph_start_y = y_offset + 10
    
    # 簡易グラフ（勝率の推移）
    if len(learning_history.history) > 1:
        win_rates = learning_history.get_win_rate_history()
        if len(win_rates) > 1:
            graph_width = GRAPH_AREA_WIDTH - 20
            graph_height = 70
            graph_x = 10
            graph_y = graph_start_y
            
            # グラフ背景
            pygame.draw.rect(screen, (255, 255, 255), (graph_x, graph_y, graph_width, graph_height))
            pygame.draw.rect(screen, (100, 100, 100), (graph_x, graph_y, graph_width, graph_height), 1)
            
            # グリッド線を描画
            grid_font = get_japanese_font(8)
            for i in range(5):
                # 水平グリッド線
                y_pos = graph_y + (i * graph_height // 4)
                pygame.draw.line(screen, (220, 220, 220), (graph_x, y_pos), (graph_x + graph_width, y_pos), 1)
                
                # Y軸ラベル（勝率）
                label_value = 100 - (i * 25)
                label_text = grid_font.render(f"{label_value}%", True, (100, 100, 100))
                screen.blit(label_text, (graph_x - 25, y_pos - 6))
            
            # 勝率グラフ
            if len(win_rates) > 1:
                points = []
                for i, rate in enumerate(win_rates):
                    x = graph_x + (i / (len(win_rates) - 1)) * graph_width
                    y = graph_y + graph_height - (rate / 100) * graph_height
                    points.append((x, y))
                
                if len(points) > 1:
                    # 太い線で折れ線グラフを描画
                    pygame.draw.lines(screen, (0, 100, 200), False, points, 3)
                    
                    # 各データポイントを小さな円で表示
                    for point in points:
                        pygame.draw.circle(screen, (0, 100, 200), (int(point[0]), int(point[1])), 2)
                    
                    # 最新の点を強調
                    if points:
                        pygame.draw.circle(screen, (255, 0, 0), (int(points[-1][0]), int(points[-1][1])), 4)
                        pygame.draw.circle(screen, (255, 255, 255), (int(points[-1][0]), int(points[-1][1])), 2)
            
            # グラフラベル
            label_font = get_japanese_font(10)
            label_text = label_font.render("勝率推移", True, (0, 0, 0))
            screen.blit(label_text, (graph_x, graph_y - 15))
            
            # X軸ラベル（ゲーム数）
            if len(win_rates) > 1:
                x_label_text = grid_font.render(f"ゲーム数: {len(win_rates)}", True, (100, 100, 100))
                screen.blit(x_label_text, (graph_x, graph_y + graph_height + 5))
            
            graph_start_y += graph_height + 25
    else:
        # デバッグ情報：データが不足している場合
        debug_font = get_japanese_font(10)
        debug_text = debug_font.render(f"履歴データ: {len(learning_history.history)}件", True, (100, 100, 100))
        screen.blit(debug_text, (10, graph_start_y))
        graph_start_y += 20
    
    # 平均報酬の推移グラフ
    if len(learning_history.history) > 1:
        avg_rewards = learning_history.get_avg_reward_history()
        if len(avg_rewards) > 1:
            graph_width = GRAPH_AREA_WIDTH - 20
            graph_height = 60
            graph_x = 10
            graph_y = graph_start_y
            
            # グラフ背景
            pygame.draw.rect(screen, (255, 255, 255), (graph_x, graph_y, graph_width, graph_height))
            pygame.draw.rect(screen, (100, 100, 100), (graph_x, graph_y, graph_width, graph_height), 1)
            
            # グリッド線を描画
            grid_font = get_japanese_font(8)
            max_reward = max(avg_rewards) if avg_rewards else 1
            for i in range(4):
                # 水平グリッド線
                y_pos = graph_y + (i * graph_height // 3)
                pygame.draw.line(screen, (220, 220, 220), (graph_x, y_pos), (graph_x + graph_width, y_pos), 1)
                
                # Y軸ラベル（報酬）
                label_value = max_reward - (i * max_reward // 3)
                label_text = grid_font.render(f"{label_value:.1f}", True, (100, 100, 100))
                screen.blit(label_text, (graph_x - 30, y_pos - 6))
            
            # 平均報酬グラフ
            if len(avg_rewards) > 1:
                points = []
                for i, reward in enumerate(avg_rewards):
                    x = graph_x + (i / (len(avg_rewards) - 1)) * graph_width
                    y = graph_y + graph_height - (reward / max_reward) * graph_height
                    points.append((x, y))
                
                if len(points) > 1:
                    # 太い線で折れ線グラフを描画
                    pygame.draw.lines(screen, (0, 200, 100), False, points, 3)
                    
                    # 各データポイントを小さな円で表示
                    for point in points:
                        pygame.draw.circle(screen, (0, 200, 100), (int(point[0]), int(point[1])), 2)
                    
                    # 最新の点を強調
                    if points:
                        pygame.draw.circle(screen, (255, 165, 0), (int(points[-1][0]), int(points[-1][1])), 4)
                        pygame.draw.circle(screen, (255, 255, 255), (int(points[-1][0]), int(points[-1][1])), 2)
            
            # グラフラベル
            label_font = get_japanese_font(10)
            label_text = label_font.render("平均報酬推移", True, (0, 0, 0))
            screen.blit(label_text, (graph_x, graph_y - 15))
            
            # X軸ラベル（ゲーム数）
            if len(avg_rewards) > 1:
                x_label_text = grid_font.render(f"ゲーム数: {len(avg_rewards)}", True, (100, 100, 100))
                screen.blit(x_label_text, (graph_x, graph_y + graph_height + 5))
            
            graph_start_y += graph_height + 25
    else:
        # デバッグ情報：データが不足している場合
        debug_font = get_japanese_font(10)
        debug_text = debug_font.render(f"報酬データ: {len(learning_history.history)}件", True, (100, 100, 100))
        screen.blit(debug_text, (10, graph_start_y))
        graph_start_y += 20
    
    # 学習回数の推移グラフ
    if len(learning_history.history) > 1:
        learn_counts = learning_history.get_learn_count_history()
        if len(learn_counts) > 1:
            graph_width = GRAPH_AREA_WIDTH - 20
            graph_height = 60
            graph_x = 10
            graph_y = graph_start_y
            
            # グラフ背景
            pygame.draw.rect(screen, (255, 255, 255), (graph_x, graph_y, graph_width, graph_height))
            pygame.draw.rect(screen, (100, 100, 100), (graph_x, graph_y, graph_width, graph_height), 1)
            
            # グリッド線を描画
            grid_font = get_japanese_font(8)
            max_count = max(learn_counts) if learn_counts else 1
            for i in range(4):
                # 水平グリッド線
                y_pos = graph_y + (i * graph_height // 3)
                pygame.draw.line(screen, (220, 220, 220), (graph_x, y_pos), (graph_x + graph_width, y_pos), 1)
                
                # Y軸ラベル（学習回数）
                label_value = max_count - (i * max_count // 3)
                label_text = grid_font.render(f"{int(label_value)}", True, (100, 100, 100))
                screen.blit(label_text, (graph_x - 35, y_pos - 6))
            
            # 学習回数グラフ
            if len(learn_counts) > 1:
                points = []
                for i, count in enumerate(learn_counts):
                    x = graph_x + (i / (len(learn_counts) - 1)) * graph_width
                    y = graph_y + graph_height - (count / max_count) * graph_height
                    points.append((x, y))
                
                if len(points) > 1:
                    # 太い線で折れ線グラフを描画
                    pygame.draw.lines(screen, (200, 100, 200), False, points, 3)
                    
                    # 各データポイントを小さな円で表示
                    for point in points:
                        pygame.draw.circle(screen, (200, 100, 200), (int(point[0]), int(point[1])), 2)
                    
                    # 最新の点を強調
                    if points:
                        pygame.draw.circle(screen, (255, 0, 255), (int(points[-1][0]), int(points[-1][1])), 4)
                        pygame.draw.circle(screen, (255, 255, 255), (int(points[-1][0]), int(points[-1][1])), 2)
            
            # グラフラベル
            label_font = get_japanese_font(10)
            label_text = label_font.render("学習回数推移", True, (0, 0, 0))
            screen.blit(label_text, (graph_x, graph_y - 15))
            
            # X軸ラベル（ゲーム数）
            if len(learn_counts) > 1:
                x_label_text = grid_font.render(f"ゲーム数: {len(learn_counts)}", True, (100, 100, 100))
                screen.blit(x_label_text, (graph_x, graph_y + graph_height + 5))
    else:
        # デバッグ情報：データが不足している場合
        debug_font = get_japanese_font(10)
        debug_text = debug_font.render(f"学習データ: {len(learning_history.history)}件", True, (100, 100, 100))
        screen.blit(debug_text, (10, graph_start_y))

def draw_button(screen, x, y, w, h, text, font, mouse_pos, mouse_down):
    """ボタンを描画"""
    rect = pygame.Rect(x, y, w, h)
    is_hover = rect.collidepoint(mouse_pos)
    color = (180, 180, 255) if is_hover else (200, 200, 200)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    # テキストのサイズを調整
    text_surface = font.render(text, True, (0, 0, 0))
    text_width = text_surface.get_width()
    text_height = text_surface.get_height()
    
    # テキストがボタンからはみ出る場合はフォントサイズを小さくする
    if text_width > w - 10:
        # フォントサイズを小さくして再描画
        # pygame.font.Fontオブジェクトのサイズを取得する方法
        try:
            # フォントサイズを推定（一般的なフォントサイズ）
            current_size = 24  # デフォルトサイズ
            smaller_font = get_japanese_font(max(12, current_size - 4))
        except:
            # エラーが発生した場合は元のフォントを使用
            smaller_font = font
        text_surface = smaller_font.render(text, True, (0, 0, 0))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
    
    # テキストを中央に配置
    text_x = x + (w - text_width) // 2
    text_y = y + (h - text_height) // 2
    screen.blit(text_surface, (text_x, text_y))
    
    return is_hover and mouse_down

def draw_buttons(screen, mouse_pos, mouse_down):
    """ボタンを描画"""
    button_y = WINDOW_HEIGHT - 120
    
    # リセットボタン
    reset_clicked = draw_button(screen, 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                               "リセット", small_font, mouse_pos, mouse_down)
    
    # 戻るボタン
    back_clicked = draw_button(screen, 10 + BUTTON_WIDTH + 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                              "戻る", small_font, mouse_pos, mouse_down)
    
    return reset_clicked, back_clicked

def draw_reset_button(screen, font, mouse_pos, mouse_down):
    """リセットボタンを描画"""
    x = WINDOW_WIDTH//2 - BUTTON_WIDTH//2
    y = BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 90
    return draw_button(screen, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, "リセット", font, mouse_pos, mouse_down)

def draw_back_button(screen, font, mouse_pos, mouse_down):
    """戻るボタンを描画"""
    x = WINDOW_WIDTH//2 + BUTTON_WIDTH//2 + 20
    y = BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 90
    return draw_button(screen, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, "戻る", font, mouse_pos, mouse_down)

def reset_game():
    """ゲームをリセットする（学習データは保持）"""
    global game, game_count, move_count, show_new_game_message, new_game_message_start_time
    game = OthelloGame()
    game.message = "新しいゲームが始まりました。黒の番です。"
    game_count += 1
    move_count = 0
    
    # 新しいゲーム開始メッセージの表示フラグを設定
    show_new_game_message = True
    new_game_message_start_time = pygame.time.get_ticks()

def draw_learning_data_screen(screen, font):
    """学習データ表示画面 - 新しいレイアウト"""
    screen.fill((255, 255, 255))
    
    # タイトル
    title = font.render("学習データ・対戦記録", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))
    
    # 最新の学習統計
    latest = learning_history.get_latest_stats()
    if latest:
        # 上部：基本統計（横並び）
        y_offset = 70
        small_font = get_japanese_font(16)
        
        # 左側の統計
        left_stats = [
            f"総ゲーム数: {latest['game_count']}",
            f"AI学習回数: {latest['ai_learn_count']}",
            f"AI勝率: {latest['win_rate']:.1f}%"
        ]
        
        left_x = 50
        for i, stat in enumerate(left_stats):
            text = small_font.render(stat, True, (0, 0, 0))
            screen.blit(text, (left_x, y_offset + i * 25))
        
        # 中央の統計
        center_stats = [
            f"AI勝利: {latest['ai_win_count']}回",
            f"AI敗北: {latest['ai_lose_count']}回", 
            f"引き分け: {latest['ai_draw_count']}回"
        ]
        
        center_x = WINDOW_WIDTH // 2 - 80
        for i, stat in enumerate(center_stats):
            text = small_font.render(stat, True, (0, 0, 0))
            screen.blit(text, (center_x, y_offset + i * 25))
        
        # 右側の統計
        right_stats = [
            f"平均報酬: {latest['ai_avg_reward']:.2f}",
            f"累積報酬: {latest['ai_total_reward']}",
            f"Qテーブル: {latest['qtable_size']}件"
        ]
        
        right_x = WINDOW_WIDTH - 200
        for i, stat in enumerate(right_stats):
            text = small_font.render(stat, True, (0, 0, 0))
            screen.blit(text, (right_x, y_offset + i * 25))
        
        # AIレベル情報（中央）
        ai_level = calculate_ai_level(latest['win_rate'], latest['ai_avg_reward'], 
                                    latest['ai_learn_count'], latest['qtable_size'])
        level_desc = get_level_description(ai_level)
        
        level_y = y_offset + 100
        level_text = small_font.render(f"AI学習レベル: {ai_level}/10 - {level_desc}", True, (0, 0, 255))
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH//2, level_y))
        screen.blit(level_text, level_rect)
        
        # 区切り線
        line_y = level_y + 30
        pygame.draw.line(screen, (200, 200, 200), (50, line_y), (WINDOW_WIDTH-50, line_y), 2)
        
        # 下部：グラフと対戦記録（横並び）
        bottom_y = line_y + 20
        
        # 左側：小さなグラフ
        graph_title = small_font.render("勝率推移", True, (0, 0, 0))
        graph_title_rect = graph_title.get_rect(center=(WINDOW_WIDTH//4, bottom_y))
        screen.blit(graph_title, graph_title_rect)
        
        draw_compact_learning_graph(screen, bottom_y + 20)
        
        # 右側：対戦記録
        record_title = small_font.render("最近の対戦", True, (0, 0, 0))
        record_title_rect = record_title.get_rect(center=(WINDOW_WIDTH * 3 // 4, bottom_y))
        screen.blit(record_title, record_title_rect)
        
        draw_compact_battle_records(screen, bottom_y + 20, small_font)
        
    else:
        no_data_text = font.render("学習データがありません", True, (100, 100, 100))
        screen.blit(no_data_text, (WINDOW_WIDTH//2 - no_data_text.get_width()//2, 200))
    
    # データ管理ボタン（上部）
    button_y = WINDOW_HEIGHT - 200  # 上に移動（160 → 200）
    button_width = 150
    button_height = 40
    
    # ボタン用の小さなフォント
    button_font = get_japanese_font(14)  # 文字サイズを小さく
    
    # 保存ボタン
    save_button = pygame.Rect(50, button_y, button_width, button_height)
    pygame.draw.rect(screen, (100, 200, 100), save_button)
    pygame.draw.rect(screen, (50, 150, 50), save_button, 2)
    save_text = button_font.render("データ保存", True, (0, 0, 0))
    save_text_rect = save_text.get_rect(center=save_button.center)
    screen.blit(save_text, save_text_rect)
    
    # 読み込みボタン
    load_button = pygame.Rect(220, button_y, button_width, button_height)
    pygame.draw.rect(screen, (255, 200, 100), load_button)
    pygame.draw.rect(screen, (200, 150, 50), load_button, 2)
    load_text = button_font.render("データ読み込み", True, (0, 0, 0))
    load_text_rect = load_text.get_rect(center=load_button.center)
    screen.blit(load_text, load_text_rect)
    
    # 新規作成ボタン
    new_button = pygame.Rect(390, button_y, button_width, button_height)
    pygame.draw.rect(screen, (100, 150, 255), new_button)
    pygame.draw.rect(screen, (50, 100, 200), new_button, 2)
    new_text = button_font.render("新規作成", True, (0, 0, 0))
    new_text_rect = new_text.get_rect(center=new_button.center)
    screen.blit(new_text, new_text_rect)
    
    # 削除ボタン
    delete_button = pygame.Rect(560, button_y, button_width, button_height)
    pygame.draw.rect(screen, (255, 100, 100), delete_button)
    pygame.draw.rect(screen, (200, 50, 50), delete_button, 2)
    delete_text = button_font.render("データ削除", True, (0, 0, 0))
    delete_text_rect = delete_text.get_rect(center=delete_button.center)
    screen.blit(delete_text, delete_text_rect)
    
    # 戻るボタン
    back_button_rect = pygame.Rect(WINDOW_WIDTH//2-100, WINDOW_HEIGHT-80, 200, 50)
    pygame.draw.rect(screen, (200, 200, 200), back_button_rect)
    pygame.draw.rect(screen, (100, 100, 100), back_button_rect, 2)
    back_text = font.render("戻る", True, (0, 0, 0))
    back_text_rect = back_text.get_rect(center=back_button_rect.center)
    screen.blit(back_text, back_text_rect)
    
    # 操作説明
    help_font = get_japanese_font(16)
    help_text = help_font.render("ESCキーまたは戻るボタンでモード選択に戻ります", True, (100, 100, 100))
    help_rect = help_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 120))
    screen.blit(help_text, help_rect)
    
    # 保存済みデータの一覧を表示
    saved_data = get_saved_data_list()
    if saved_data:
        data_list_y = WINDOW_HEIGHT - 200
        data_title = help_font.render("保存済みデータ:", True, (0, 0, 0))
        screen.blit(data_title, (50, data_list_y))
        
        data_list_y += 25
        import os, json
        for i, data_name in enumerate(saved_data[:5]):  # 最大5件まで表示
            # 各データのlearning_history_○○○.jsonから統計を取得
            hist_path = f"learning_history_{data_name}.json"
            win_rate = "-"
            learn_count = "-"
            level = "-"
            if os.path.exists(hist_path):
                try:
                    with open(hist_path, 'r', encoding='utf-8') as f:
                        hist = json.load(f)
                        if hist:
                            latest = hist[-1]
                            win_rate = f"{latest.get('win_rate', 0):.1f}%"
                            learn_count = f"{latest.get('ai_learn_count', 0)}回"
                            # AIレベル計算
                            level_val = calculate_ai_level(
                                latest.get('win_rate', 0),
                                latest.get('ai_avg_reward', 0),
                                latest.get('ai_learn_count', 0),
                                latest.get('qtable_size', 0)
                            )
                            level = f"Lv.{level_val}"
                except Exception as e:
                    pass
            data_text = help_font.render(f"• {data_name}  勝率:{win_rate}  学習:{learn_count}  {level}", True, (50, 50, 50))
            screen.blit(data_text, (70, data_list_y + i * 20))
        
        if len(saved_data) > 5:
            more_text = help_font.render(f"... 他 {len(saved_data) - 5}件", True, (100, 100, 100))
            screen.blit(more_text, (70, data_list_y + 5 * 20))
    else:
        data_list_y = WINDOW_HEIGHT - 200
        no_data_text = help_font.render("保存済みデータ: なし", True, (100, 100, 100))
        screen.blit(no_data_text, (50, data_list_y))

def draw_battle_history_screen(screen, font):
    """対戦記録表示画面"""
    screen.fill((255, 255, 255))
    
    # タイトル
    title = font.render("対戦記録", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))
    
    if not learning_history.history:
        no_data_text = font.render("対戦記録がありません", True, (100, 100, 100))
        screen.blit(no_data_text, (WINDOW_WIDTH//2 - no_data_text.get_width()//2, 200))
    else:
        # 最新の10件の対戦記録を表示
        recent_records = list(learning_history.history)[-10:]
        small_font = get_japanese_font(16)
        y_offset = 80
        
        # ヘッダー
        header_font = get_japanese_font(18)
        headers = ["ゲーム", "勝者", "黒駒", "白駒", "平均報酬", "累積報酬", "学習レベル"]
        header_x = 30
        for i, header in enumerate(headers):
            text = header_font.render(header, True, (0, 0, 255))
            x = header_x + i * 120
            if x + 120 <= WINDOW_WIDTH:  # 画面幅を超えないように
                screen.blit(text, (x, y_offset))
        
        y_offset += 40
        
        # 対戦記録
        for i, record in enumerate(reversed(recent_records)):
            if y_offset + 30 > WINDOW_HEIGHT - 200:  # 戻るボタンのスペースを確保
                break
                
            # 勝者判定
            if record['ai_win_count'] > record['ai_lose_count']:
                winner = "AI勝利"
                winner_color = (0, 0, 255)
            elif record['ai_lose_count'] > record['ai_win_count']:
                winner = "人間勝利"
                winner_color = (255, 0, 0)
            else:
                winner = "引き分け"
                winner_color = (100, 100, 100)
            
            # 学習レベル計算
            ai_level = calculate_ai_level(record['win_rate'], record['ai_avg_reward'], 
                                        record['ai_learn_count'], record['qtable_size'])
            
            # 記録データ
            game_num = record['game_count']
            black_stones = record.get('black_score', 0)  # 正しい駒数
            white_stones = record.get('white_score', 0)  # 正しい駒数
            avg_reward = record['ai_avg_reward']
            total_reward = record['ai_total_reward']
            
            # データ表示
            data = [
                f"{game_num}",
                winner,
                f"{black_stones}",
                f"{white_stones}",
                f"{avg_reward:.1f}",
                f"{total_reward}",
                f"Lv.{ai_level}"
            ]
            
            for j, item in enumerate(data):
                text = small_font.render(item, True, winner_color if j == 1 else (0, 0, 0))
                x = header_x + j * 120
                if x + 120 <= WINDOW_WIDTH:  # 画面幅を超えないように
                    screen.blit(text, (x, y_offset))
            
            y_offset += 30
        
        # 記録数表示
        record_count_text = small_font.render(f"表示中: 最新{len(recent_records)}件 / 総{len(learning_history.history)}件", True, (100, 100, 100))
        screen.blit(record_count_text, (30, y_offset + 20))
    
    # 戻るボタン
    back_button_rect = pygame.Rect(WINDOW_WIDTH//2-100, WINDOW_HEIGHT-80, 200, 50)
    pygame.draw.rect(screen, (200, 200, 200), back_button_rect)
    pygame.draw.rect(screen, (100, 100, 100), back_button_rect, 2)
    back_text = font.render("戻る", True, (0, 0, 0))
    back_text_rect = back_text.get_rect(center=back_button_rect.center)
    screen.blit(back_text, back_text_rect)
    
    # 操作説明（戻るボタンの上）
    help_font = get_japanese_font(16)
    help_text = help_font.render("ESCキーまたは戻るボタンでモード選択に戻ります", True, (100, 100, 100))
    help_rect = help_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 120))
    screen.blit(help_text, help_rect)

def mode_select_screen(screen, font):
    """モード選択画面"""
    global current_mode, pretrain_total, DEBUG_MODE, ai_speed, draw_mode
    selecting = True
    input_mode = False
    speed_input_mode = False
    data_view_mode = False  # 学習データ表示モード
    battle_history_mode = False  # 対戦記録表示モード
    input_text = "10"
    speed_input_text = str(ai_speed)
    
    while selecting:
        screen.fill((255, 255, 255))
        title = font.render("モード選択", True, (0, 0, 0))
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 80))
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and (data_view_mode or battle_history_mode):
                    data_view_mode = False
                    battle_history_mode = False
                elif input_mode:
                    if event.key == pygame.K_RETURN:
                        try:
                            pretrain_total = int(input_text)
                            input_mode = False
                        except ValueError:
                            pass
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isnumeric():
                        input_text += event.unicode
                elif speed_input_mode:
                    if event.key == pygame.K_RETURN:
                        try:
                            ai_speed = int(speed_input_text)
                            speed_input_mode = False
                        except ValueError:
                            pass
                    elif event.key == pygame.K_BACKSPACE:
                        speed_input_text = speed_input_text[:-1]
                    elif event.unicode.isnumeric():
                        speed_input_text += event.unicode
        
        # 学習データ表示モードの場合
        if data_view_mode:
            draw_learning_data_screen(screen, font)
            
            # ボタンのクリック判定
            button_y = WINDOW_HEIGHT - 200  # 実際のボタン位置と一致させる
            button_width = 150
            button_height = 40
            
            # 保存ボタン
            save_button = pygame.Rect(50, button_y, button_width, button_height)
            if mouse_down and save_button.collidepoint(mouse_pos):
                # データ保存処理
                save_learning_data()
            
            # 読み込みボタン
            load_button = pygame.Rect(220, button_y, button_width, button_height)
            if mouse_down and load_button.collidepoint(mouse_pos):
                # データ読み込み処理
                load_learning_data()
            
            # 新規作成ボタン
            new_button = pygame.Rect(390, button_y, button_width, button_height)
            if mouse_down and new_button.collidepoint(mouse_pos):
                # 新規作成処理
                create_new_learning_data()
            
            # 削除ボタン
            delete_button = pygame.Rect(560, button_y, button_width, button_height)
            if mouse_down and delete_button.collidepoint(mouse_pos):
                # 削除確認処理
                confirm_delete_learning_data()
            
            # 戻るボタンのクリック判定
            back_button_rect = pygame.Rect(WINDOW_WIDTH//2-100, WINDOW_HEIGHT-80, 200, 50)
            if mouse_down and back_button_rect.collidepoint(mouse_pos):
                data_view_mode = False
            
            pygame.display.flip()
            pygame.time.Clock().tick(30)
            continue
        
        # 対戦記録表示モードの場合
        if battle_history_mode:
            draw_battle_history_screen(screen, font)
            # 戻るボタンのクリック判定
            back_button_rect = pygame.Rect(WINDOW_WIDTH//2-100, WINDOW_HEIGHT-80, 200, 50)
            if mouse_down and back_button_rect.collidepoint(mouse_pos):
                battle_history_mode = False
            pygame.display.flip()
            pygame.time.Clock().tick(30)
            continue
        
        if draw_button(screen, WINDOW_WIDTH//2-100, 150, 200, 50, "人間vsAIで学習", font, mouse_pos, mouse_down):
            current_mode = MODE_HUMAN_TRAIN
            selecting = False
        if draw_button(screen, WINDOW_WIDTH//2-120, 220, 240, 50, "AI同士で訓練→人間vsAI", font, mouse_pos, mouse_down):
            current_mode = MODE_AI_PRETRAIN
            selecting = False
        
        # 学習データ参照ボタンを追加
        if draw_button(screen, WINDOW_WIDTH//2-100, 290, 200, 50, "学習データ参照", font, mouse_pos, mouse_down):
            data_view_mode = True
        
        # 対戦記録参照ボタンを追加
        if draw_button(screen, WINDOW_WIDTH//2-100, 360, 200, 50, "対戦記録参照", font, mouse_pos, mouse_down):
            battle_history_mode = True
        
        debug_text = "デバッグモード: ON" if DEBUG_MODE else "デバッグモード: OFF"
        if draw_button(screen, WINDOW_WIDTH//2-100, 430, 200, 40, debug_text, font, mouse_pos, mouse_down):
            DEBUG_MODE = not DEBUG_MODE
        draw_text = "AI描画: ON" if draw_mode else "AI描画: OFF"
        if draw_button(screen, WINDOW_WIDTH//2-100, 490, 200, 40, draw_text, font, mouse_pos, mouse_down):
            draw_mode = not draw_mode
        if draw_button(screen, WINDOW_WIDTH//2-100, 550, 200, 40, "カスタム入力", font, mouse_pos, mouse_down):
            input_mode = True
        speed_text = f"AI速度: {ai_speed}ms"
        if draw_button(screen, WINDOW_WIDTH//2-100, 610, 200, 40, speed_text, font, mouse_pos, mouse_down):
            speed_input_mode = True
        
        if input_mode:
            pygame.draw.rect(screen, (255, 255, 255), (WINDOW_WIDTH//2-100, 670, 200, 40))
            pygame.draw.rect(screen, (0, 0, 0), (WINDOW_WIDTH//2-100, 670, 200, 40), 2)
            input_surface = font.render(input_text, True, (0, 0, 0))
            screen.blit(input_surface, (WINDOW_WIDTH//2-90, 680))
            info = font.render("Enterで確定", True, (0, 0, 0))
            screen.blit(info, (WINDOW_WIDTH//2-info.get_width()//2, 720))
        elif speed_input_mode:
            pygame.draw.rect(screen, (255, 255, 255), (WINDOW_WIDTH//2-100, 670, 200, 40))
            pygame.draw.rect(screen, (0, 0, 0), (WINDOW_WIDTH//2-100, 670, 200, 40), 2)
            input_surface = font.render(speed_input_text, True, (0, 0, 0))
            screen.blit(input_surface, (WINDOW_WIDTH//2-90, 680))
            info = font.render("Enterで確定", True, (0, 0, 0))
            screen.blit(info, (WINDOW_WIDTH//2-info.get_width()//2, 720))
        else:
            info = font.render(f"訓練回数: {pretrain_total}", True, (0,0,0))
            screen.blit(info, (WINDOW_WIDTH//2-info.get_width()//2, 670))
        
        pygame.display.flip()
        pygame.time.Clock().tick(30)

def draw_simple_learning_graph(screen, start_y):
    """簡易学習グラフを描画"""
    if not learning_history.history:
        # データがない場合のメッセージ
        small_font = get_japanese_font(14)
        no_data_text = small_font.render("学習データが不足しています", True, (100, 100, 100))
        no_data_rect = no_data_text.get_rect(center=(WINDOW_WIDTH//2, start_y + 90))
        screen.blit(no_data_text, no_data_rect)
        return
    
    graph_width = min(500, WINDOW_WIDTH - 120)
    graph_height = 180
    graph_x = (WINDOW_WIDTH - graph_width) // 2
    graph_y = start_y
    
    # グラフ背景
    pygame.draw.rect(screen, (245, 245, 245), (graph_x, graph_y, graph_width, graph_height))
    pygame.draw.rect(screen, (200, 200, 200), (graph_x, graph_y, graph_width, graph_height), 2)
    
    # グリッド線
    for i in range(1, 5):
        y = graph_y + (i * graph_height // 5)
        pygame.draw.line(screen, (220, 220, 220), (graph_x, y), (graph_x + graph_width, y), 1)
    
    # 勝率の推移を描画
    win_rates = [record['win_rate'] for record in learning_history.history]
    if len(win_rates) > 0:
        points = []
        for i, rate in enumerate(win_rates):
            if len(win_rates) == 1:
                # データが1つだけの場合
                x = graph_x + graph_width // 2
            else:
                x = graph_x + (i / (len(win_rates) - 1)) * (graph_width - 40) + 20
            y = graph_y + graph_height - (rate / 100) * (graph_height - 40) - 20
            points.append((x, y))
        
        # 折れ線グラフを描画
        if len(points) > 1:
            pygame.draw.lines(screen, (0, 0, 255), False, points, 3)
        elif len(points) == 1:
            # データが1つの場合は点のみ表示
            point = points[0]
            pygame.draw.circle(screen, (0, 0, 255), (int(point[0]), int(point[1])), 6)
            pygame.draw.circle(screen, (255, 255, 255), (int(point[0]), int(point[1])), 3)
        
        # データポイントを描画
        for point in points:
            pygame.draw.circle(screen, (0, 0, 255), (int(point[0]), int(point[1])), 4)
            pygame.draw.circle(screen, (255, 255, 255), (int(point[0]), int(point[1])), 2)
    
    # 軸ラベル
    small_font = get_japanese_font(14)
    x_label = small_font.render("ゲーム数", True, (0, 0, 0))
    
    x_label_rect = x_label.get_rect(center=(graph_x + graph_width//2, graph_y + graph_height + 20))
    screen.blit(x_label, x_label_rect)
    
    # Y軸の目盛り
    for i in range(6):
        y = graph_y + (i * graph_height // 5)
        rate = 100 - (i * 20)
        rate_text = small_font.render(f"{rate}%", True, (100, 100, 100))
        screen.blit(rate_text, (graph_x - 35, y - 8))
    
    # データ数表示
    data_count_text = small_font.render(f"データ数: {len(win_rates)}", True, (100, 100, 100))
    screen.blit(data_count_text, (graph_x + graph_width - 80, graph_y - 20))
    
    # 最新の勝率表示
    if len(win_rates) > 0:
        latest_rate = win_rates[-1]
        latest_text = small_font.render(f"最新勝率: {latest_rate:.1f}%", True, (0, 0, 255))
        screen.blit(latest_text, (graph_x, graph_y - 20))

def initialize_game_screen(game_obj):
    """ゲーム画面を初期化して描画する共通処理"""
    global show_new_game_message
    screen.fill(WHITE)
    draw_board(screen, game_obj.board)
    draw_stones(screen, game_obj.board)
    
    # 新しいゲーム開始メッセージが表示されている場合は、通常のメッセージ表示をスキップ
    if not show_new_game_message:
        display_message(screen, game_obj.message, game_obj.last_move_error)
    
    black_score, white_score = game_obj.get_score()
    display_score(screen, black_score, white_score)
    display_ai_reward(screen, game_obj.ai_last_reward)
    draw_learn_count(screen, font)
    draw_game_count(screen, font)
    draw_move_count(screen, font)
    draw_reset_button(screen, font, (0, 0), False)
    draw_back_button(screen, font, (0, 0), False)
    
    # グラフの描画（常時表示）
    draw_learning_graphs(screen)
    
    # 新しいゲーム開始メッセージを表示
    display_new_game_message(screen, font)
    
    pygame.display.flip()

def handle_mouse_click(pos):
    """マウスクリックの処理"""
    if game.game_over:
        return
    
    # 盤面のクリック処理
    board_x = (pos[0] - BOARD_OFFSET_X) // SQUARE_SIZE
    board_y = (pos[1] - BOARD_OFFSET_Y) // SQUARE_SIZE
    
    if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE:
        if game.current_player == PLAYER_BLACK:  # 人間の手番
            if game.is_valid_move(board_y, board_x, PLAYER_BLACK):
                # 有効な手の場合
                flipped = game.make_move(board_y, board_x, PLAYER_BLACK)
                global move_count
                move_count += 1
                
                # プレイヤーを切り替え
                game.switch_player()
                
                # ゲーム終了チェック
                if game.check_game_over():
                    game.game_over = True
                    winner = game.get_winner()
                    if winner == PLAYER_BLACK:
                        game.message = "黒の勝利！"
                    elif winner == PLAYER_WHITE:
                        game.message = "白の勝利！"
                    else:
                        game.message = "引き分け！"
                else:
                    # AIの手番を実行
                    execute_ai_turn()
            else:
                # 無効な手の場合
                game.error_message = "そこには置けません"
                game.error_start_time = pygame.time.get_ticks()

def execute_ai_turn():
    """AIの手番を実行"""
    if game.current_player == PLAYER_WHITE and not game.game_over:
        # AIの手を決定
        ai_move = game.get_ai_move()
        
        if ai_move:
            # AIの手を記録
            game.last_ai_move = ai_move
            
            # AIの手を実行
            flipped = game.make_move(ai_move[0], ai_move[1], PLAYER_WHITE)
            global move_count
            move_count += 1
            
            # プレイヤーを切り替え
            game.switch_player()
            
            # ゲーム終了チェック
            if game.check_game_over():
                game.game_over = True
                winner = game.get_winner()
                if winner == PLAYER_BLACK:
                    game.message = "黒の勝利！"
                elif winner == PLAYER_WHITE:
                    game.message = "白の勝利！"
                else:
                    game.message = "引き分け！"
        else:
            # AIがパスする場合
            game.switch_player()

def update_learning_stats():
    """学習統計を更新"""
    global game_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, ai_learn_count
    
    if game.game_over and not game.game_over_displayed:
        game.game_over_displayed = True
        game_count += 1
        
        winner = game.get_winner()
        
        # ゲーム終了時の最終報酬を計算
        final_reward = 0
        if winner == PLAYER_WHITE:
            ai_win_count += 1
            final_reward = REWARD_WIN
        elif winner == PLAYER_BLACK:
            ai_lose_count += 1
            final_reward = REWARD_LOSE
        else:
            ai_draw_count += 1
            final_reward = REWARD_DRAW
        
        # 最終報酬をQ学習に反映
        if game.last_ai_move:
            current_state = game.get_board_state_key()
            game.update_q_value(current_state, game.last_ai_move, final_reward, current_state, [])
            ai_total_reward += final_reward
            # ゼロ除算を防ぐ
            if ai_learn_count > 0:
                ai_avg_reward = ai_total_reward / ai_learn_count
            else:
                ai_avg_reward = ai_total_reward
        
        # デバッグ情報を出力
        print(f"ゲーム終了: 勝者={'白AI' if winner == PLAYER_WHITE else '黒' if winner == PLAYER_BLACK else '引き分け'}")
        print(f"最終報酬: {final_reward}, 累積報酬: {ai_total_reward}, 平均報酬: {ai_avg_reward:.2f}")
        print(f"学習回数: {ai_learn_count}, Qテーブルサイズ: {len(qtable)}")
        
        # 最終スコアを取得
        black_score, white_score = game.get_score()
        
        # 学習履歴に記録（駒数も含める）
        learning_history.add_record(
            game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count,
            ai_total_reward, ai_avg_reward, len(qtable), black_score, white_score
        )
        
        # Qテーブルを保存
        game.save_qtable()

def main_loop():
    global current_mode, pretrain_in_progress, pretrain_now, win_black, win_white, game, game_count, move_count, last_move_count, draw_mode, pretrain_total, fast_mode, ai_speed, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, ai_learn_count, show_new_game_message
    
    # current_modeの初期化
    if current_mode is None:
        current_mode = None
    
    # モード選択画面を表示（current_modeがNoneの場合）
    if current_mode is None:
        mode_select_screen(screen, font)

    # モード選択後に適切なゲームを開始
    if current_mode == MODE_AI_PRETRAIN:
        # AI同士の対戦モードを開始
        pretrain_in_progress = True
        win_black = 0
        win_white = 0
        game = OthelloGame()
        game_count += 1
        move_count = 0
        last_move_count = 0
        pretrain_now = 1
        if draw_mode:
            # AI同士の対戦では新しいゲーム開始メッセージを表示しない
            screen.fill(WHITE)
            draw_board(screen, game.board)
            draw_stones(screen, game.board)
            display_message(screen, game.message, game.last_move_error)
            black_score, white_score = game.get_score()
            display_score(screen, black_score, white_score)
            display_ai_reward(screen, game.ai_last_reward)
            draw_learn_count(screen, font)
            draw_game_count(screen, font)
            draw_move_count(screen, font)
            draw_reset_button(screen, font, (0, 0), False)
            draw_back_button(screen, font, (0, 0), False)
            draw_learning_graphs(screen)
            pygame.display.flip()
        else:
            # 描画モードOFF時は最初の画面表示のみ
            screen.fill(WHITE)
            title = font.render("AI同士の訓練中", True, (0, 0, 0))
            screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
            current_text = font.render(f"対戦 {pretrain_now} / {pretrain_total}", True, (0, 0, 0))
            screen.blit(current_text, (WINDOW_WIDTH//2 - current_text.get_width()//2, 150))
            win_text = font.render(f"黒AI: {win_black}勝  白AI: {win_white}勝", True, (0, 0, 0))
            screen.blit(win_text, (WINDOW_WIDTH//2 - win_text.get_width()//2, 180))
            draw_progress_bar(screen, pretrain_now - 1, pretrain_total, 
                            WINDOW_WIDTH//2 - 150, 220, 300, 40)
            move_text = font.render(f"現在の手数: {move_count}", True, (0, 0, 0))
            screen.blit(move_text, (WINDOW_WIDTH//2 - move_text.get_width()//2, 280))
            speed_text = font.render("高速処理中...", True, (255, 0, 0))
            screen.blit(speed_text, (WINDOW_WIDTH//2 - speed_text.get_width()//2, 320))
            pygame.display.flip()
    else:
        # 人間vsAIモード
        game = OthelloGame()
        game_count += 1
        initialize_game_screen(game)

    running = True
    clock = pygame.time.Clock()
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                
                # 新しいゲーム開始メッセージが表示されている場合は、クリックで消す
                if show_new_game_message:
                    show_new_game_message = False
                    # 画面を再描画
                    screen.fill(WHITE)
                    draw_board(screen, game.board)
                    draw_stones(screen, game.board)
                    display_message(screen, game.message, game.last_move_error)
                    black_score, white_score = game.get_score()
                    display_score(screen, black_score, white_score)
                    display_ai_reward(screen, game.ai_last_reward)
                    draw_learn_count(screen, font)
                    draw_game_count(screen, font)
                    draw_move_count(screen, font)
                    draw_reset_button(screen, font, (0, 0), False)
                    draw_back_button(screen, font, (0, 0), False)
                    draw_learning_graphs(screen)
                    pygame.display.flip()
                    continue
                
                # リセットボタンのクリック処理
                if draw_reset_button(screen, font, mouse_pos, mouse_down):
                    reset_game()
                    initialize_game_screen(game)
                    continue
                
                # 戻るボタンのクリック処理
                if draw_back_button(screen, font, mouse_pos, mouse_down):
                    # 完全な初期化
                    game_count = 0
                    move_count = 0
                    ai_learn_count = 0
                    current_mode = None
                    pretrain_in_progress = False
                    pretrain_now = 0
                    pretrain_total = 10
                    ai_speed = 60
                    fast_mode = True
                    draw_mode = True
                    DEBUG_MODE = False
                    win_black = 0
                    win_white = 0
                    game = OthelloGame()
                    show_new_game_message = False
                    # モード選択画面に戻る
                    mode_select_screen(screen, font)
                    # モード選択後に適切なゲームを開始
                    if current_mode == MODE_AI_PRETRAIN:
                        pretrain_in_progress = True
                        win_black = 0
                        win_white = 0
                        game = OthelloGame()
                        game_count += 1
                        move_count = 0
                        last_move_count = 0
                        pretrain_now = 1
                        initialize_game_screen(game)
                    else:
                        game = OthelloGame()
                        game_count += 1
                        initialize_game_screen(game)
                    continue

            # キー入力で新しいゲーム開始メッセージを消す
            if event.type == pygame.KEYDOWN and show_new_game_message:
                show_new_game_message = False
                # 画面を再描画
                screen.fill(WHITE)
                draw_board(screen, game.board)
                draw_stones(screen, game.board)
                display_message(screen, game.message, game.last_move_error)
                black_score, white_score = game.get_score()
                display_score(screen, black_score, white_score)
                display_ai_reward(screen, game.ai_last_reward)
                draw_learn_count(screen, font)
                draw_game_count(screen, font)
                draw_move_count(screen, font)
                draw_reset_button(screen, font, (0, 0), False)
                draw_back_button(screen, font, (0, 0), False)
                draw_learning_graphs(screen)
                pygame.display.flip()
                continue

        # 新しいゲーム開始メッセージが表示されている場合は、他の処理をスキップ
        if show_new_game_message:
            pygame.display.flip()
            clock.tick(60)
            continue  # ←この位置

        # AI同士の対戦処理
        if pretrain_in_progress:
            # 無限ループ防止のための手数制限
            if move_count > 200:  # 200手を超えた場合は強制終了
                game.game_over = True
                black_score, white_score = game.get_score()
                if black_score > white_score:
                    win_black += 1
                    ai_lose_count += 1  # 白AIの敗北
                elif white_score > black_score:
                    win_white += 1
                    ai_win_count += 1   # 白AIの勝利
                else:
                    # 引き分けの場合は黒の勝ちとする
                    win_black += 1
                    ai_draw_count += 1  # 白AIの引き分け
                
                # 学習履歴に記録（AI同士の対戦でも記録）
                learning_history.add_record(
                    game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count,
                    ai_total_reward, ai_avg_reward, len(qtable), black_score, white_score
                )
                
                # 次の対戦に進む
                if win_black + win_white < pretrain_total:
                    pretrain_now += 1
                    game = OthelloGame()
                    game_count += 1
                    move_count = 0
                    last_move_count = 0
                    if draw_mode:
                        # AI同士の対戦では新しいゲーム開始メッセージを表示しない
                        screen.fill(WHITE)
                        draw_board(screen, game.board)
                        draw_stones(screen, game.board)
                        display_message(screen, game.message, game.last_move_error)
                        black_score, white_score = game.get_score()
                        display_score(screen, black_score, white_score)
                        display_ai_reward(screen, game.ai_last_reward)
                        draw_learn_count(screen, font)
                        draw_game_count(screen, font)
                        draw_move_count(screen, font)
                        draw_reset_button(screen, font, (0, 0), False)
                        draw_back_button(screen, font, (0, 0), False)
                        draw_learning_graphs(screen)
                        pygame.display.flip()
                    else:
                        # 描画モードOFF時は最初の画面表示のみ
                        screen.fill(WHITE)
                        title = font.render("AI同士の訓練中", True, (0, 0, 0))
                        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
                        current_text = font.render(f"対戦 {pretrain_now} / {pretrain_total}", True, (0, 0, 0))
                        screen.blit(current_text, (WINDOW_WIDTH//2 - current_text.get_width()//2, 150))
                        win_text = font.render(f"黒AI: {win_black}勝  白AI: {win_white}勝", True, (0, 0, 0))
                        screen.blit(win_text, (WINDOW_WIDTH//2 - win_text.get_width()//2, 180))
                        draw_progress_bar(screen, pretrain_now - 1, pretrain_total, 
                                        WINDOW_WIDTH//2 - 150, 220, 300, 40)
                        move_text = font.render(f"現在の手数: {move_count}", True, (0, 0, 0))
                        screen.blit(move_text, (WINDOW_WIDTH//2 - move_text.get_width()//2, 280))
                        speed_text = font.render("高速処理中...", True, (255, 0, 0))
                        screen.blit(speed_text, (WINDOW_WIDTH//2 - speed_text.get_width()//2, 320))
                        
                        # グラフの描画（常時表示）
                        draw_learning_graphs(screen)
                        
                        pygame.display.flip()
                continue
            
            if not game.game_over:
                # 現在のプレイヤーの有効な手を取得
                valid_moves = game.get_valid_moves(game.current_player)
                if valid_moves:
                    # AIの手を実行（白AIのみ学習対象）
                    if game.current_player == PLAYER_WHITE:
                        # 白AIの手（学習あり）
                        if game.ai_qlearning_move(qtable, learn=True, player=PLAYER_WHITE):
                            game.switch_player()
                            game.check_game_over()
                    else:
                        # 黒AIの手（学習なし、ランダム）
                        action = random.choice(valid_moves)
                        r, c = action
                        flipped = game._get_flipped_stones(r, c, PLAYER_BLACK)
                        reward = len(flipped) * REWARD_FLIP_PER_STONE
                        game.make_move(r, c, PLAYER_BLACK)
                        game.message = f"黒AIが {chr(ord('A') + c)}{r+1} に置きました。(報酬: {reward})"
                        game.switch_player()
                        game.check_game_over()
                else:
                    game.message = f"{'黒' if game.current_player == PLAYER_BLACK else '白'}AIはパスしました。"
                    game.switch_player()
                    game.check_game_over()
                
                # draw_modeがTrueの場合は画面を更新
                if draw_mode:
                    screen.fill(WHITE)
                    draw_board(screen, game.board)
                    draw_stones(screen, game.board)
                    display_message(screen, game.message, game.last_move_error)
                    black_score, white_score = game.get_score()
                    display_score(screen, black_score, white_score)
                    display_ai_reward(screen, game.ai_last_reward)
                    draw_learn_count(screen, font)
                    draw_game_count(screen, font)
                    draw_move_count(screen, font)
                    draw_reset_button(screen, font, (0, 0), False)
                    draw_back_button(screen, font, (0, 0), False)
                    draw_learning_graphs(screen)
                    pygame.display.flip()
                    
                    # AI速度に応じて待機
                    pygame.time.wait(ai_speed)
            else:
                # ゲーム終了時の処理
                black_score, white_score = game.get_score()
                if black_score > white_score:
                    win_black += 1
                    ai_lose_count += 1  # 白AIの敗北
                elif white_score > black_score:
                    win_white += 1
                    ai_win_count += 1   # 白AIの勝利
                else:
                    # 引き分けの場合は黒の勝ちとする
                    win_black += 1
                    ai_draw_count += 1  # 白AIの引き分け
                
                # 学習履歴に記録（AI同士の対戦でも記録）
                learning_history.add_record(
                    game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count,
                    ai_total_reward, ai_avg_reward, len(qtable), black_score, white_score
                )
                
                # 次の対戦に進む
                if win_black + win_white < pretrain_total:
                    pretrain_now += 1
                    game = OthelloGame()
                    game_count += 1
                    move_count = 0
                    last_move_count = 0
                    if draw_mode:
                        # AI同士の対戦では新しいゲーム開始メッセージを表示しない
                        screen.fill(WHITE)
                        draw_board(screen, game.board)
                        draw_stones(screen, game.board)
                        display_message(screen, game.message, game.last_move_error)
                        black_score, white_score = game.get_score()
                        display_score(screen, black_score, white_score)
                        display_ai_reward(screen, game.ai_last_reward)
                        draw_learn_count(screen, font)
                        draw_game_count(screen, font)
                        draw_move_count(screen, font)
                        draw_reset_button(screen, font, (0, 0), False)
                        draw_back_button(screen, font, (0, 0), False)
                        draw_learning_graphs(screen)
                        pygame.display.flip()
                    else:
                        # 描画モードOFF時は最初の画面表示のみ
                        screen.fill(WHITE)
                        title = font.render("AI同士の訓練中", True, (0, 0, 0))
                        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
                        current_text = font.render(f"対戦 {pretrain_now} / {pretrain_total}", True, (0, 0, 0))
                        screen.blit(current_text, (WINDOW_WIDTH//2 - current_text.get_width()//2, 150))
                        win_text = font.render(f"黒AI: {win_black}勝  白AI: {win_white}勝", True, (0, 0, 0))
                        screen.blit(win_text, (WINDOW_WIDTH//2 - win_text.get_width()//2, 180))
                        draw_progress_bar(screen, pretrain_now - 1, pretrain_total, 
                                        WINDOW_WIDTH//2 - 150, 220, 300, 40)
                        move_text = font.render(f"現在の手数: {move_count}", True, (0, 0, 0))
                        screen.blit(move_text, (WINDOW_WIDTH//2 - move_text.get_width()//2, 280))
                        speed_text = font.render("高速処理中...", True, (255, 0, 0))
                        screen.blit(speed_text, (WINDOW_WIDTH//2 - speed_text.get_width()//2, 320))
                        
                        # グラフの描画（常時表示）
                        draw_learning_graphs(screen)
                        
                        pygame.display.flip()
                else:
                    # 訓練完了
                    pretrain_in_progress = False
                    # 訓練完了メッセージを表示
                    screen.fill(WHITE)
                    title = font.render("AI訓練完了！", True, (0, 0, 0))
                    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
                    result_text = font.render(f"黒AI: {win_black}勝  白AI: {win_white}勝", True, (0, 0, 0))
                    screen.blit(result_text, (WINDOW_WIDTH//2 - result_text.get_width()//2, 150))
                    
                    # 人との対戦ボタンとモード選択ボタンを表示
                    button_y = 220
                    button_width = 200
                    button_height = 50
                    
                    # 人との対戦ボタン
                    human_vs_ai_button = pygame.Rect(WINDOW_WIDTH//2 - button_width - 20, button_y, button_width, button_height)
                    pygame.draw.rect(screen, (100, 200, 100), human_vs_ai_button)
                    pygame.draw.rect(screen, (50, 150, 50), human_vs_ai_button, 3)
                    human_text = font.render("人vsAIで対戦", True, (0, 0, 0))
                    human_text_rect = human_text.get_rect(center=human_vs_ai_button.center)
                    screen.blit(human_text, human_text_rect)
                    
                    # モード選択ボタン
                    mode_select_button = pygame.Rect(WINDOW_WIDTH//2 + 20, button_y, button_width, button_height)
                    pygame.draw.rect(screen, (200, 200, 200), mode_select_button)
                    pygame.draw.rect(screen, (100, 100, 100), mode_select_button, 3)
                    mode_text = font.render("モード選択", True, (0, 0, 0))
                    mode_text_rect = mode_text.get_rect(center=mode_select_button.center)
                    screen.blit(mode_text, mode_text_rect)
                    
                    help_text = font.render("ボタンをクリックするか、ESCキーでモード選択に戻ります", True, (100, 100, 100))
                    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, button_y + 80))
                    pygame.display.flip()
                    
                    # ボタンクリックまたはESCキーで処理
                    waiting_for_input = True
                    while waiting_for_input:
                        mouse_pos = pygame.mouse.get_pos()
                        mouse_down = False
                        
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                waiting_for_input = False
                            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                mouse_down = True
                            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                # モード選択に戻る
                                waiting_for_input = False
                                # 完全な初期化
                                game_count = 0
                                move_count = 0
                                ai_learn_count = 0
                                current_mode = None
                                pretrain_in_progress = False
                                pretrain_now = 0
                                pretrain_total = 10
                                ai_speed = 60
                                fast_mode = True
                                draw_mode = True
                                DEBUG_MODE = False
                                win_black = 0
                                win_white = 0
                                game = OthelloGame()
                                show_new_game_message = False
                                # モード選択画面に戻る
                                mode_select_screen(screen, font)
                                # モード選択後に適切なゲームを開始
                                if current_mode == MODE_AI_PRETRAIN:
                                    pretrain_in_progress = True
                                    win_black = 0
                                    win_white = 0
                                    game = OthelloGame()
                                    game_count += 1
                                    move_count = 0
                                    last_move_count = 0
                                    pretrain_now = 1
                                    initialize_game_screen(game)
                                else:
                                    game = OthelloGame()
                                    game_count += 1
                                    initialize_game_screen(game)
                        
                        # ボタンクリック判定
                        if mouse_down:
                            if human_vs_ai_button.collidepoint(mouse_pos):
                                # 人との対戦に移行
                                waiting_for_input = False
                                current_mode = MODE_HUMAN_TRAIN
                                # 人との対戦用に初期化
                                game_count = 0
                                move_count = 0
                                ai_learn_count = 0
                                pretrain_in_progress = False
                                pretrain_now = 0
                                pretrain_total = 10
                                ai_speed = 60
                                fast_mode = True
                                draw_mode = True
                                DEBUG_MODE = False
                                win_black = 0
                                win_white = 0
                                game = OthelloGame()
                                show_new_game_message = True
                                game_count += 1
                                initialize_game_screen(game)
                            elif mode_select_button.collidepoint(mouse_pos):
                                # モード選択に戻る
                                waiting_for_input = False
                                # 完全な初期化
                                game_count = 0
                                move_count = 0
                                ai_learn_count = 0
                                current_mode = None
                                pretrain_in_progress = False
                                pretrain_now = 0
                                pretrain_total = 10
                                ai_speed = 60
                                fast_mode = True
                                draw_mode = True
                                DEBUG_MODE = False
                                win_black = 0
                                win_white = 0
                                game = OthelloGame()
                                show_new_game_message = False
                                # モード選択画面に戻る
                                mode_select_screen(screen, font)
                                # モード選択後に適切なゲームを開始
                                if current_mode == MODE_AI_PRETRAIN:
                                    pretrain_in_progress = True
                                    win_black = 0
                                    win_white = 0
                                    game = OthelloGame()
                                    game_count += 1
                                    move_count = 0
                                    last_move_count = 0
                                    pretrain_now = 1
                                    initialize_game_screen(game)
                                else:
                                    game = OthelloGame()
                                    game_count += 1
                                    initialize_game_screen(game)
                        
                        clock.tick(60)
            continue
        
        # 人間vsAIモードの処理
        # マウスクリックの処理
        if mouse_down:
            handle_mouse_click(mouse_pos)
        
        # 学習統計の更新
        update_learning_stats()
        
        # 画面の更新
        screen.fill(WHITE)
        draw_board(screen, game.board)
        draw_stones(screen, game.board)
        display_message(screen, game.message, game.last_move_error)
        black_score, white_score = game.get_score()
        display_score(screen, black_score, white_score)
        display_ai_reward(screen, game.ai_last_reward)
        draw_learn_count(screen, font)
        draw_game_count(screen, font)
        draw_move_count(screen, font)
        draw_reset_button(screen, font, mouse_pos, mouse_down)
        draw_back_button(screen, font, mouse_pos, mouse_down)
        draw_learning_graphs(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    # ゲーム終了時の処理
    pygame.quit()
    sys.exit()

def calculate_ai_level(win_rate, avg_reward, learn_count, qtable_size):
    """AIの学習レベルを計算"""
    level = 1  # 基本レベル
    
    # 勝率によるレベルアップ
    if win_rate >= 80:
        level += 3
    elif win_rate >= 60:
        level += 2
    elif win_rate >= 40:
        level += 1
    
    # 平均報酬によるレベルアップ
    if avg_reward >= 10:
        level += 2
    elif avg_reward >= 5:
        level += 1
    
    # 学習回数によるレベルアップ
    if learn_count >= 1000:
        level += 2
    elif learn_count >= 500:
        level += 1
    
    # Qテーブルサイズによるレベルアップ
    if qtable_size >= 10000:
        level += 2
    elif qtable_size >= 5000:
        level += 1
    
    return min(level, 10)  # 最大レベル10

def get_level_description(level):
    """レベルに対応する説明を取得"""
    descriptions = {
        1: "初心者",
        2: "初級者", 
        3: "中級者",
        4: "上級者",
        5: "エキスパート",
        6: "マスター",
        7: "グランドマスター",
        8: "伝説",
        9: "神",
        10: "超越者"
    }
    return descriptions.get(level, "未知")

# グローバル変数の定義
# ... existing code ...
show_new_game_message = False
new_game_message_start_time = 0
# ... existing code ...

def display_new_game_message(screen, font):
    """新しいゲーム開始メッセージを盤面の上に表示"""
    global show_new_game_message, new_game_message_start_time
    
    if show_new_game_message:
        # 半透明の背景を作成
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (0, 0))
        
        # メッセージボックス（位置を上に移動）
        message_box_width = 400
        message_box_height = 120
        message_box_x = (WINDOW_WIDTH - message_box_width) // 2
        message_box_y = (WINDOW_HEIGHT - message_box_height) // 2 - 100  # 上に移動
        
        # メッセージボックスの背景
        pygame.draw.rect(screen, (240, 240, 240), 
                        (message_box_x, message_box_y, message_box_width, message_box_height))
        pygame.draw.rect(screen, (100, 100, 100), 
                        (message_box_x, message_box_y, message_box_width, message_box_height), 3)
        
        # メッセージテキスト
        message_font = get_japanese_font(20)
        message_text = message_font.render("新しいゲームが始まりました", True, (0, 0, 0))
        message_rect = message_text.get_rect(center=(WINDOW_WIDTH//2, message_box_y + message_box_height//2 - 20))
        screen.blit(message_text, message_rect)
        
        # 操作説明
        help_font = get_japanese_font(16)
        help_text = help_font.render("クリックまたはキー入力で開始", True, (100, 100, 100))
        help_rect = help_text.get_rect(center=(WINDOW_WIDTH//2, message_box_y + message_box_height//2 + 20))
        screen.blit(help_text, help_rect)

def draw_small_learning_graph(screen, start_y):
    """小さな学習グラフを描画"""
    if not learning_history.history:
        # データがない場合のメッセージ
        small_font = get_japanese_font(12)
        no_data_text = small_font.render("データ不足", True, (100, 100, 100))
        no_data_rect = no_data_text.get_rect(center=(WINDOW_WIDTH//4, start_y + 60))
        screen.blit(no_data_text, no_data_rect)
        return
    
    graph_width = 300  # 小さく
    graph_height = 120  # 小さく
    graph_x = (WINDOW_WIDTH//4) - (graph_width // 2)
    graph_y = start_y
    
    # グラフ背景
    pygame.draw.rect(screen, (245, 245, 245), (graph_x, graph_y, graph_width, graph_height))
    pygame.draw.rect(screen, (200, 200, 200), (graph_x, graph_y, graph_width, graph_height), 2)
    
    # グリッド線
    for i in range(1, 4):
        y = graph_y + (i * graph_height // 4)
        pygame.draw.line(screen, (220, 220, 220), (graph_x, y), (graph_x + graph_width, y), 1)
    
    # 勝率の推移を描画
    win_rates = [record['win_rate'] for record in learning_history.history]
    if len(win_rates) > 0:
        points = []
        for i, rate in enumerate(win_rates):
            if len(win_rates) == 1:
                # データが1つだけの場合
                x = graph_x + graph_width // 2
            else:
                x = graph_x + (i / (len(win_rates) - 1)) * (graph_width - 20) + 10
            y = graph_y + graph_height - (rate / 100) * (graph_height - 20) - 10
            points.append((x, y))
        
        # 折れ線グラフを描画
        if len(points) > 1:
            pygame.draw.lines(screen, (0, 0, 255), False, points, 2)
        elif len(points) == 1:
            # データが1つの場合は点のみ表示
            point = points[0]
            pygame.draw.circle(screen, (0, 0, 255), (int(point[0]), int(point[1])), 4)
            pygame.draw.circle(screen, (255, 255, 255), (int(point[0]), int(point[1])), 2)
        
        # データポイントを描画
        for point in points:
            pygame.draw.circle(screen, (0, 0, 255), (int(point[0]), int(point[1])), 3)
            pygame.draw.circle(screen, (255, 255, 255), (int(point[0]), int(point[1])), 1)
    
    # Y軸の目盛り（簡略化）
    small_font = get_japanese_font(10)
    for i in range(5):
        y = graph_y + (i * graph_height // 4)
        rate = 100 - (i * 25)
        rate_text = small_font.render(f"{rate}%", True, (100, 100, 100))
        screen.blit(rate_text, (graph_x - 25, y - 6))
    
    # データ数表示
    data_count_text = small_font.render(f"データ: {len(win_rates)}", True, (100, 100, 100))
    screen.blit(data_count_text, (graph_x + graph_width - 60, graph_y - 15))
    
    # 最新の勝率表示
    if len(win_rates) > 0:
        latest_rate = win_rates[-1]
        latest_text = small_font.render(f"最新: {latest_rate:.1f}%", True, (0, 0, 255))
        screen.blit(latest_text, (graph_x, graph_y - 15))

def draw_recent_battle_records(screen, start_y, font):
    """最近の対戦記録を右側に表示"""
    if not learning_history.history:
        return
    
    # 最新の5件の対戦記録を表示
    recent_records = list(learning_history.history)[-5:]
    small_font = get_japanese_font(14)
    
    # タイトル
    title = font.render("最近の対戦記録", True, (0, 0, 0))
    title_rect = title.get_rect(center=(WINDOW_WIDTH * 3 // 4, start_y))
    screen.blit(title, title_rect)
    
    y_offset = start_y + 30
    
    # ヘッダー
    header_font = get_japanese_font(12)
    headers = ["ゲーム", "勝者", "黒", "白", "レベル"]
    header_x = WINDOW_WIDTH * 3 // 4 - 100
    for i, header in enumerate(headers):
        text = header_font.render(header, True, (0, 0, 255))
        x = header_x + i * 40
        screen.blit(text, (x, y_offset))
    
    y_offset += 25
    
    # 対戦記録
    for i, record in enumerate(reversed(recent_records)):
        if y_offset + 20 > WINDOW_HEIGHT - 200:  # 戻るボタンのスペースを確保
            break
            
        # 勝者判定
        if record['ai_win_count'] > record['ai_lose_count']:
            winner = "AI"
            winner_color = (0, 0, 255)
        elif record['ai_lose_count'] > record['ai_win_count']:
            winner = "人間"
            winner_color = (255, 0, 0)
        else:
            winner = "引分"
            winner_color = (100, 100, 100)
        
        # 学習レベル計算
        ai_level = calculate_ai_level(record['win_rate'], record['ai_avg_reward'], 
                                    record['ai_learn_count'], record['qtable_size'])
        
        # 記録データ
        game_num = record['game_count']
        black_stones = record.get('black_score', 0)
        white_stones = record.get('white_score', 0)
        
        # データ表示
        data = [
            f"{game_num}",
            winner,
            f"{black_stones}",
            f"{white_stones}",
            f"Lv.{ai_level}"
        ]
        
        for j, item in enumerate(data):
            text = small_font.render(item, True, winner_color if j == 1 else (0, 0, 0))
            x = header_x + j * 40
            screen.blit(text, (x, y_offset))
        
        y_offset += 20
    
    # 記録数表示
    record_count_text = small_font.render(f"表示: {len(recent_records)}/総{len(learning_history.history)}", True, (100, 100, 100))
    screen.blit(record_count_text, (header_x, y_offset + 10))

def draw_compact_learning_graph(screen, start_y):
    """コンパクトな学習グラフを描画"""
    if not learning_history.history:
        # データがない場合のメッセージ
        small_font = get_japanese_font(14)
        no_data_text = small_font.render("データ不足", True, (100, 100, 100))
        no_data_rect = no_data_text.get_rect(center=(WINDOW_WIDTH//4, start_y + 60))
        screen.blit(no_data_text, no_data_rect)
        return
    
    graph_width = 350  # 大きく
    graph_height = 150  # 大きく
    graph_x = (WINDOW_WIDTH//4) - (graph_width // 2)
    graph_y = start_y
    
    # グラフ背景
    pygame.draw.rect(screen, (245, 245, 245), (graph_x, graph_y, graph_width, graph_height))
    pygame.draw.rect(screen, (200, 200, 200), (graph_x, graph_y, graph_width, graph_height), 2)
    
    # グリッド線
    for i in range(1, 4):
        y = graph_y + (i * graph_height // 4)
        pygame.draw.line(screen, (220, 220, 220), (graph_x, y), (graph_x + graph_width, y), 1)
    
    # 勝率の推移を描画
    win_rates = [record['win_rate'] for record in learning_history.history]
    if len(win_rates) > 0:
        points = []
        for i, rate in enumerate(win_rates):
            if len(win_rates) == 1:
                # データが1つだけの場合
                x = graph_x + graph_width // 2
            else:
                x = graph_x + (i / (len(win_rates) - 1)) * (graph_width - 30) + 15
            y = graph_y + graph_height - (rate / 100) * (graph_height - 30) - 15
            points.append((x, y))
        
        # 折れ線グラフを描画
        if len(points) > 1:
            pygame.draw.lines(screen, (0, 0, 255), False, points, 3)
        elif len(points) == 1:
            # データが1つの場合は点のみ表示
            point = points[0]
            pygame.draw.circle(screen, (0, 0, 255), (int(point[0]), int(point[1])), 4)
            pygame.draw.circle(screen, (255, 255, 255), (int(point[0]), int(point[1])), 2)
        
        # データポイントを描画
        for point in points:
            pygame.draw.circle(screen, (0, 0, 255), (int(point[0]), int(point[1])), 3)
            pygame.draw.circle(screen, (255, 255, 255), (int(point[0]), int(point[1])), 1)
    
    # Y軸の目盛り
    small_font = get_japanese_font(12)
    for i in range(5):
        y = graph_y + (i * graph_height // 4)
        rate = 100 - (i * 25)
        rate_text = small_font.render(f"{rate}%", True, (100, 100, 100))
        screen.blit(rate_text, (graph_x - 25, y - 8))
    
    # 最新の勝率表示
    if len(win_rates) > 0:
        latest_rate = win_rates[-1]
        latest_text = small_font.render(f"最新: {latest_rate:.1f}%", True, (0, 0, 255))
        screen.blit(latest_text, (graph_x, graph_y - 20))

def draw_compact_battle_records(screen, start_y, font):
    """コンパクトな対戦記録を右側に表示"""
    if not learning_history.history:
        return
    
    # 最新の10件の対戦記録を表示
    recent_records = list(learning_history.history)[-10:]
    small_font = get_japanese_font(14)  # フォントサイズを大きく
    
    y_offset = start_y
    
    # ヘッダー
    header_font = get_japanese_font(14)  # フォントサイズを大きく
    headers = ["ゲーム", "勝者", "黒", "白", "レベル"]
    header_x = WINDOW_WIDTH * 3 // 4 - 100  # 位置を調整
    for i, header in enumerate(headers):
        text = header_font.render(header, True, (0, 0, 255))
        x = header_x + i * 45  # 列幅を大きく
        screen.blit(text, (x, y_offset))
    
    y_offset += 25  # 行間を大きく
    
    # 対戦記録（10件表示）
    for i, record in enumerate(reversed(recent_records)):
        if y_offset + 20 > WINDOW_HEIGHT - 200:  # 戻るボタンのスペースを確保
            break
            
        # 勝者判定
        if record['ai_win_count'] > record['ai_lose_count']:
            winner = "AI"
            winner_color = (0, 0, 255)
        elif record['ai_lose_count'] > record['ai_win_count']:
            winner = "人間"
            winner_color = (255, 0, 0)
        else:
            winner = "引分"
            winner_color = (100, 100, 100)
        
        # 学習レベル計算
        ai_level = calculate_ai_level(record['win_rate'], record['ai_avg_reward'], 
                                    record['ai_learn_count'], record['qtable_size'])
        
        # 記録データ
        game_num = record['game_count']
        black_stones = record.get('black_score', 0)
        white_stones = record.get('white_score', 0)
        
        # データ表示
        data = [
            f"{game_num}",
            winner,
            f"{black_stones}",
            f"{white_stones}",
            f"Lv.{ai_level}"
        ]
        
        for j, item in enumerate(data):
            text = small_font.render(item, True, winner_color if j == 1 else (0, 0, 0))
            x = header_x + j * 45  # 列幅を大きく
            screen.blit(text, (x, y_offset))
        
        y_offset += 20  # 行間を大きく
    
    # 記録数表示
    record_count_text = small_font.render(f"表示: {len(recent_records)}/総{len(learning_history.history)}", True, (100, 100, 100))
    screen.blit(record_count_text, (header_x, y_offset + 10))

def save_learning_data():
    """学習データを保存"""
    global qtable, learning_history
    
    # 保存名入力画面を表示
    save_name = show_save_name_input()
    if not save_name:
        return  # キャンセルされた場合
    
    try:
        # ファイル名を生成
        qtable_filename = f"qtable_{save_name}.pkl"
        history_filename = f"learning_history_{save_name}.json"
        
        # Qテーブルを保存
        save_qtable_to_file(qtable, qtable_filename)
        
        # 学習履歴を保存
        learning_history.save_history_to_file(history_filename)
        
        # 保存完了メッセージを表示
        show_save_complete_message(save_name)
        
        print(f"学習データ '{save_name}' を保存しました")
    except Exception as e:
        print(f"保存エラー: {e}")
        show_save_error_message()

def create_new_learning_data():
    """新しい学習データを作成"""
    global qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward
    
    # 新規作成名入力画面を表示
    new_name = show_new_data_name_input()
    if not new_name:
        return  # キャンセルされた場合
    
    # 確認メッセージを表示
    if show_confirm_new_data_message(new_name):
        try:
            # データをリセット
            qtable = {}
            learning_history.history.clear()
            game_count = 0
            ai_learn_count = 0
            ai_win_count = 0
            ai_lose_count = 0
            ai_draw_count = 0
            ai_total_reward = 0
            ai_avg_reward = 0
            
            # 新しいQテーブルを保存
            qtable_filename = f"qtable_{new_name}.pkl"
            save_qtable_to_file(qtable, qtable_filename)
            
            # 学習履歴を保存
            history_filename = f"learning_history_{new_name}.json"
            learning_history.save_history_to_file(history_filename)
            
            print(f"新しい学習データ '{new_name}' を作成しました")
        except Exception as e:
            print(f"新規作成エラー: {e}")

def load_learning_data():
    """学習データを読み込み"""
    global qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward
    
    # 保存済みデータの一覧を取得
    saved_data = get_saved_data_list()
    if not saved_data:
        show_no_saved_data_message()
        return
    
    # データ選択画面を表示
    selected_data = show_data_selection_screen(saved_data)
    if not selected_data:
        return  # キャンセルされた場合
    
    try:
        # 選択されたデータを読み込み
        qtable_filename = f"qtable_{selected_data}.pkl"
        history_filename = f"learning_history_{selected_data}.json"
        
        # Qテーブルを読み込み
        qtable = load_qtable_from_file(qtable_filename)
        
        # 学習履歴を読み込み
        learning_history.load_history_from_file(history_filename)
        
        # 統計を更新
        latest = learning_history.get_latest_stats()
        if latest:
            game_count = latest['game_count']
            ai_learn_count = latest['ai_learn_count']
            ai_win_count = latest['ai_win_count']
            ai_lose_count = latest['ai_lose_count']
            ai_draw_count = latest['ai_draw_count']
            ai_total_reward = latest['ai_total_reward']
            ai_avg_reward = latest['ai_avg_reward']
        
        show_load_complete_message(selected_data)
        print(f"学習データ '{selected_data}' を読み込みました")
    except Exception as e:
        print(f"読み込みエラー: {e}")
        show_load_error_message()

def confirm_delete_learning_data():
    """学習データ削除の確認"""
    global qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward
    
    # 保存済みデータの一覧を取得
    saved_data = get_saved_data_list()
    if not saved_data:
        show_no_saved_data_message()
        return
    
    # 削除対象選択画面を表示
    selected_data = show_data_selection_screen(saved_data, "削除するデータを選択")
    if not selected_data:
        return  # キャンセルされた場合
    
    # 確認メッセージを表示
    if show_confirm_delete_message(selected_data):
        try:
            # ファイルを削除
            import os
            qtable_filename = f"qtable_{selected_data}.pkl"
            history_filename = f"learning_history_{selected_data}.json"
            
            if os.path.exists(qtable_filename):
                os.remove(qtable_filename)
            if os.path.exists(history_filename):
                os.remove(history_filename)
            
            print(f"学習データ '{selected_data}' を削除しました")
        except Exception as e:
            print(f"削除エラー: {e}")

def get_saved_data_list():
    """保存済みデータの一覧を取得"""
    import os
    import glob
    
    # qtableファイルからデータ名を抽出
    qtable_files = glob.glob("qtable_*.pkl")
    data_names = []
    
    for file in qtable_files:
        # "qtable_データ名.pkl" から "データ名" を抽出
        name = file.replace("qtable_", "").replace(".pkl", "")
        data_names.append(name)
    
    return sorted(data_names)

def save_qtable_to_file(qtable_data, filename):
    """Qテーブルを指定ファイルに保存"""
    import pickle
    with open(filename, 'wb') as f:
        pickle.dump(qtable_data, f)

def load_qtable_from_file(filename):
    """Qテーブルを指定ファイルから読み込み"""
    import pickle
    with open(filename, 'rb') as f:
        return pickle.load(f)

def show_save_name_input():
    """保存名入力画面を表示"""
    screen.fill(WHITE)
    title = font.render("学習データ保存", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
    
    message = font.render("保存名を入力してください:", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 200))
    
    # 入力ボックス
    input_box = pygame.Rect(WINDOW_WIDTH//2 - 150, 250, 300, 40)
    pygame.draw.rect(screen, (255, 255, 255), input_box)
    pygame.draw.rect(screen, (100, 100, 100), input_box, 2)
    
    # ボタン
    save_button = pygame.Rect(WINDOW_WIDTH//2 - 150, 320, 120, 40)
    pygame.draw.rect(screen, (100, 200, 100), save_button)
    pygame.draw.rect(screen, (50, 150, 50), save_button, 2)
    save_text = font.render("保存", True, (0, 0, 0))
    save_text_rect = save_text.get_rect(center=save_button.center)
    screen.blit(save_text, save_text_rect)
    
    cancel_button = pygame.Rect(WINDOW_WIDTH//2 + 30, 320, 120, 40)
    pygame.draw.rect(screen, (200, 200, 200), cancel_button)
    pygame.draw.rect(screen, (100, 100, 100), cancel_button, 2)
    cancel_text = font.render("キャンセル", True, (0, 0, 0))
    cancel_text_rect = cancel_text.get_rect(center=cancel_button.center)
    screen.blit(cancel_text, cancel_text_rect)
    
    help_text = font.render("ESCキーでキャンセル", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 380))
    
    pygame.display.flip()
            
    # 入力処理
    input_text = ""
    input_active = True
    
    while input_active:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    if input_text.strip():
                        return input_text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isprintable() and len(input_text) < 20:
                    input_text += event.unicode
        
        if mouse_down:
            if save_button.collidepoint(mouse_pos):
                if input_text.strip():
                    return input_text.strip()
            elif cancel_button.collidepoint(mouse_pos):
                return None
        
        # 入力テキストを表示
        screen.fill(WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
        screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 200))
        
        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, (100, 100, 100), input_box, 2)
        
        input_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))
        
        pygame.draw.rect(screen, (100, 200, 100), save_button)
        pygame.draw.rect(screen, (50, 150, 50), save_button, 2)
        screen.blit(save_text, save_text_rect)
        
        pygame.draw.rect(screen, (200, 200, 200), cancel_button)
        pygame.draw.rect(screen, (100, 100, 100), cancel_button, 2)
        screen.blit(cancel_text, cancel_text_rect)
        
        screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 380))
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    
    return None

def show_new_data_name_input():
    """新規データ名入力画面を表示"""
    screen.fill(WHITE)
    title = font.render("新規学習データ作成", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
    
    message = font.render("新規データ名を入力してください:", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 200))
    
    # 入力ボックス
    input_box = pygame.Rect(WINDOW_WIDTH//2 - 150, 250, 300, 40)
    pygame.draw.rect(screen, (255, 255, 255), input_box)
    pygame.draw.rect(screen, (100, 100, 100), input_box, 2)
    
    # ボタン
    create_button = pygame.Rect(WINDOW_WIDTH//2 - 150, 320, 120, 40)
    pygame.draw.rect(screen, (100, 150, 255), create_button)
    pygame.draw.rect(screen, (50, 100, 200), create_button, 2)
    create_text = font.render("作成", True, (0, 0, 0))
    create_text_rect = create_text.get_rect(center=create_button.center)
    screen.blit(create_text, create_text_rect)
    
    cancel_button = pygame.Rect(WINDOW_WIDTH//2 + 30, 320, 120, 40)
    pygame.draw.rect(screen, (200, 200, 200), cancel_button)
    pygame.draw.rect(screen, (100, 100, 100), cancel_button, 2)
    cancel_text = font.render("キャンセル", True, (0, 0, 0))
    cancel_text_rect = cancel_text.get_rect(center=cancel_button.center)
    screen.blit(cancel_text, cancel_text_rect)
    
    help_text = font.render("ESCキーでキャンセル", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 380))
    
    pygame.display.flip()
    
    # 入力処理
    input_text = ""
    input_active = True
    
    while input_active:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    if input_text.strip():
                        return input_text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isprintable() and len(input_text) < 20:
                    input_text += event.unicode
        
        if mouse_down:
            if create_button.collidepoint(mouse_pos):
                if input_text.strip():
                    return input_text.strip()
            elif cancel_button.collidepoint(mouse_pos):
                return None
        
        # 入力テキストを表示
        screen.fill(WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
        screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 200))
        
        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, (100, 100, 100), input_box, 2)
        
        input_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))
        
        pygame.draw.rect(screen, (100, 150, 255), create_button)
        pygame.draw.rect(screen, (50, 100, 200), create_button, 2)
        screen.blit(create_text, create_text_rect)
        
        pygame.draw.rect(screen, (200, 200, 200), cancel_button)
        pygame.draw.rect(screen, (100, 100, 100), cancel_button, 2)
        screen.blit(cancel_text, cancel_text_rect)
        
        screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 380))
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    
    return None

def show_data_selection_screen(data_list, title_text="データを選択"):
    """データ選択画面を表示"""
    screen.fill(WHITE)
    title = font.render(title_text, True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
    
    # データリストを表示
    y_offset = 150
    button_height = 50  # ボタンの高さを増やす
    buttons = []
    
    # 小さいフォント
    small_font = get_japanese_font(14)
    
    for i, data_name in enumerate(data_list):
        if y_offset + button_height > WINDOW_HEIGHT - 150:
            break
            
        button = pygame.Rect(100, y_offset, WINDOW_WIDTH - 200, button_height)
        buttons.append((button, data_name))
        
        pygame.draw.rect(screen, (240, 240, 240), button)
        pygame.draw.rect(screen, (100, 100, 100), button, 2)
        
        # データ名を表示
        name_text = font.render(data_name, True, (0, 0, 0))
        name_rect = name_text.get_rect(midleft=(button.x + 10, button.centery - 10))
        screen.blit(name_text, name_rect)
        
        # 各データの統計情報を取得して表示
        import os, json
        hist_path = f"learning_history_{data_name}.json"
        win_rate = "-"
        learn_count = "-"
        level = "-"
        if os.path.exists(hist_path):
            try:
                with open(hist_path, 'r', encoding='utf-8') as f:
                    hist = json.load(f)
                    if hist:
                        latest = hist[-1]
                        win_rate = f"{latest.get('win_rate', 0):.1f}%"
                        learn_count = f"{latest.get('ai_learn_count', 0)}回"
                        # AIレベル計算
                        level_val = calculate_ai_level(
                            latest.get('win_rate', 0),
                            latest.get('ai_avg_reward', 0),
                            latest.get('ai_learn_count', 0),
                            latest.get('qtable_size', 0)
                        )
                        level = f"Lv.{level_val}"
            except Exception as e:
                pass
        
        # 統計情報を表示
        stats_text = small_font.render(f"勝率:{win_rate}  学習:{learn_count}  {level}", True, (50, 50, 50))
        stats_rect = stats_text.get_rect(midleft=(button.x + 10, button.centery + 10))
        screen.blit(stats_text, stats_rect)
        
        y_offset += button_height + 10
    
    # キャンセルボタン
    cancel_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 100, 200, 40)
    pygame.draw.rect(screen, (200, 200, 200), cancel_button)
    pygame.draw.rect(screen, (100, 100, 100), cancel_button, 2)
    cancel_text = font.render("キャンセル", True, (0, 0, 0))
    cancel_text_rect = cancel_text.get_rect(center=cancel_button.center)
    screen.blit(cancel_text, cancel_text_rect)
    
    help_text = font.render("ESCキーでキャンセル", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, WINDOW_HEIGHT - 60))
    
    pygame.display.flip()
    
    # クリック処理
    waiting = True
    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
        
        if mouse_down:
            if cancel_button.collidepoint(mouse_pos):
                return None
            
            for button, data_name in buttons:
                if button.collidepoint(mouse_pos):
                    return data_name
        
        pygame.time.Clock().tick(60)
    
    return None

def show_save_complete_message(save_name):
    """保存完了メッセージを表示"""
    screen.fill(WHITE)
    title = font.render("保存完了", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render(f"学習データ '{save_name}' を保存しました", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 300))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.Clock().tick(60)

def show_confirm_new_data_message(new_name):
    """新規作成確認メッセージを表示"""
    screen.fill(WHITE)
    title = font.render("新規作成確認", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
    
    message = font.render(f"新しい学習データ '{new_name}' を作成しますか？", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 200))
    
    # ボタン
    yes_button = pygame.Rect(WINDOW_WIDTH//2 - 150, 250, 120, 40)
    pygame.draw.rect(screen, (100, 200, 100), yes_button)
    pygame.draw.rect(screen, (50, 150, 50), yes_button, 2)
    yes_text = font.render("はい", True, (0, 0, 0))
    yes_text_rect = yes_text.get_rect(center=yes_button.center)
    screen.blit(yes_text, yes_text_rect)
    
    no_button = pygame.Rect(WINDOW_WIDTH//2 + 30, 250, 120, 40)
    pygame.draw.rect(screen, (200, 200, 200), no_button)
    pygame.draw.rect(screen, (100, 100, 100), no_button, 2)
    no_text = font.render("いいえ", True, (0, 0, 0))
    no_text_rect = no_text.get_rect(center=no_button.center)
    screen.blit(no_text, no_text_rect)
    
    pygame.display.flip()
    
    # ボタンクリック待ち
    waiting = True
    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        
        if mouse_down:
            if yes_button.collidepoint(mouse_pos):
                return True
            elif no_button.collidepoint(mouse_pos):
                return False
        
        pygame.time.Clock().tick(60)

def show_confirm_delete_message(data_name):
    """削除確認メッセージを表示"""
    screen.fill(WHITE)
    title = font.render("削除確認", True, (255, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
    
    message = font.render(f"学習データ '{data_name}' を削除しますか？", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 200))
    
    warning = font.render("この操作は取り消せません", True, (255, 0, 0))
    screen.blit(warning, (WINDOW_WIDTH//2 - warning.get_width()//2, 230))
    
    # ボタン
    yes_button = pygame.Rect(WINDOW_WIDTH//2 - 150, 280, 120, 40)
    pygame.draw.rect(screen, (255, 100, 100), yes_button)
    pygame.draw.rect(screen, (200, 50, 50), yes_button, 2)
    yes_text = font.render("削除", True, (0, 0, 0))
    yes_text_rect = yes_text.get_rect(center=yes_button.center)
    screen.blit(yes_text, yes_text_rect)
    
    no_button = pygame.Rect(WINDOW_WIDTH//2 + 30, 280, 120, 40)
    pygame.draw.rect(screen, (200, 200, 200), no_button)
    pygame.draw.rect(screen, (100, 100, 100), no_button, 2)
    no_text = font.render("キャンセル", True, (0, 0, 0))
    no_text_rect = no_text.get_rect(center=no_button.center)
    screen.blit(no_text, no_text_rect)
    
    pygame.display.flip()
    
    # ボタンクリック待ち
    waiting = True
    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        
        if mouse_down:
            if yes_button.collidepoint(mouse_pos):
                return True
            elif no_button.collidepoint(mouse_pos):
                return False
        
        pygame.time.Clock().tick(60)

def show_no_saved_data_message():
    """保存済みデータがない場合のメッセージを表示"""
    screen.fill(WHITE)
    title = font.render("データなし", True, (100, 100, 100))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render("保存済みの学習データがありません", True, (100, 100, 100))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 300))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.Clock().tick(60)

def show_load_complete_message(data_name):
    """読み込み完了メッセージを表示"""
    screen.fill(WHITE)
    title = font.render("読み込み完了", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render(f"学習データ '{data_name}' を読み込みました", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 300))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.Clock().tick(60)

def show_load_error_message():
    """読み込みエラーメッセージを表示"""
    screen.fill(WHITE)
    title = font.render("読み込みエラー", True, (255, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render("学習データの読み込みに失敗しました", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 300))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.Clock().tick(60)

def show_save_error_message():
    """保存エラーメッセージを表示"""
    screen.fill(WHITE)
    title = font.render("保存エラー", True, (255, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render("学習データの保存に失敗しました", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 300))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.Clock().tick(60)

if __name__ == "__main__":
    main_loop() 