import pygame
import sys
import random
import time
import pickle  # Qテーブル保存・読み込み用
import os      # ファイル存在確認用
from typing import Optional  # 型ヒント用

# ゲーム定数
BOARD_SIZE = 8
SQUARE_SIZE = 60 # 各マスのピクセルサイズ
BOARD_OFFSET_X = 50 # 盤面左上のXオフセット
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

# グローバル変数
ai_learn_count = 0
game_count = 0  # 何ゲーム目か
move_count = 0  # 何手目か
last_move_count = 0  # 前回の手数（チカチカ防止用）
win_black = 0  # AI同士の対戦での黒AI勝利回数
win_white = 0  # AI同士の対戦での白AI勝利回数

# モード管理
MODE_HUMAN_TRAIN = 0  # 人間vsAIで学習
MODE_AI_PRETRAIN = 1  # AI同士で訓練→人間vsAI
current_mode = None
pretrain_total = 10  # デフォルト訓練回数
pretrain_now = 0
pretrain_in_progress = False
ai_speed = 60  # AI同士の対戦の処理速度（ミリ秒）- 高速化
fast_mode = True  # AI同士の対戦を高速モードで実行
draw_mode = True  # AI同士の対戦の描画モード（True=描画する、False=描画しない）

# デバッグモード管理
DEBUG_MODE = False  # デバッグモードのフラグ

class OthelloGame:
    def __init__(self):
        # 盤面の初期化: 0=空, 1=黒石, 2=白石
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        # 初期配置
        self.board[3][3] = PLAYER_WHITE # 白石
        self.board[4][4] = PLAYER_WHITE # 白石
        self.board[3][4] = PLAYER_BLACK # 黒石
        self.board[4][3] = PLAYER_BLACK # 黒石

        self.current_player = PLAYER_BLACK # 黒が先手
        self.game_over = False
        self.message = "黒の番です。" # 画面に表示するメッセージ
        self.highlighted_square: Optional[tuple[int, int]] = None  # マウスオーバーでハイライトするマス
        self.last_move_error = False # 無効な手を打ったかどうかのフラグ
        self.ai_last_reward = 0 # AIが最後に得た報酬（デバッグ・表示用）
        self.last_ai_move = None  # 直前のAIの手
        self.game_over_displayed = False  # ゲーム終了表示済みフラグ
        global move_count
        move_count = 0  # 新しいゲーム開始時に手数をリセット
        
        # デバッグ: 最初のプレイヤーの有効な手を表示
        if DEBUG_MODE:
            valid_moves = self.get_valid_moves(self.current_player)
            if valid_moves:
                moves_str = ", ".join([f"({r+1},{c+1})" for r, c in valid_moves])
                print(f"黒の有効な手: {moves_str}")
            else:
                print("黒の有効な手: なし（パス）")

    def _get_flipped_stones(self, r, c, player):
        """
        指定された位置(r, c)にplayerが石を置いた場合に裏返せる石のリストを返す。
        リストの要素は(行, 列)のタプル。
        """
        if self.board[r][c] != 0: # 空いているマスでなければ裏返せる石はない
            return []

        flipped_stones = []
        opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK # 相手の石

        # 8方向の定義 (row_offset, col_offset)
        directions = [
            (-1, -1), (-1, 0), (-1, 1), # 上方向
            (0, -1),           (0, 1),  # 左右方向
            (1, -1), (1, 0), (1, 1)     # 下方向
        ]

        for dr, dc in directions:
            current_direction_flipped = [] # 現在の方向で裏返せる石のリスト
            nr, nc = r + dr, c + dc # 探索開始位置

            # 盤面内かつ相手の石が続く限り探索
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == opponent:
                current_direction_flipped.append((nr, nc))
                nr += dr
                nc += dc

            # 探索の終点が自分の石であり、かつ間に相手の石を挟んでいる場合
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == player and len(current_direction_flipped) > 0:
                flipped_stones.extend(current_direction_flipped) # 裏返せる石を追加

        # デバッグ用: 裏返せる石の数を表示
        # if len(flipped_stones) > 0 and DEBUG_MODE:
        #     print(f"裏返し可能: ({r},{c})に{player}を置くと{len(flipped_stones)}個の石を裏返せます")

        return flipped_stones

    def is_valid_move(self, r, c, player):
        """
        指定された位置(r, c)がplayerにとって有効な手であるかを判定する。
        """
        # 盤面内かつ空いているマスか
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE) or self.board[r][c] != 0:
            return False

        # 裏返せる石があるか
        return len(self._get_flipped_stones(r, c, player)) > 0

    def make_move(self, r, c, player):
        global move_count
        if not self.is_valid_move(r, c, player):
            return False
        flipped_stones = self._get_flipped_stones(r, c, player)
        if DEBUG_MODE:
            player_name = "黒" if player == PLAYER_BLACK else "白"
            print(f"{player_name}が({r+1},{c+1})に置きました")
            if len(flipped_stones) > 0:
                flipped_str = ", ".join([f"({fr+1},{fc+1})" for fr, fc in flipped_stones])
                print(f"  裏返した石: {flipped_str} ({len(flipped_stones)}個)")
            else:
                print(f"  裏返した石: なし")
        self.board[r][c] = player
        for fr, fc in flipped_stones:
            self.board[fr][fc] = player
        move_count += 1
        if player == PLAYER_WHITE:
            self.ai_last_reward = len(flipped_stones) * REWARD_FLIP_PER_STONE
        return True

    def switch_player(self):
        """手番を交代する。"""
        self.current_player = PLAYER_WHITE if self.current_player == PLAYER_BLACK else PLAYER_BLACK
        self.message = f"{'黒' if self.current_player == PLAYER_BLACK else '白'}の番です。"
        self.last_move_error = False # 手番が変わったのでエラーフラグをリセット
        
        # デバッグ: 次のプレイヤーの有効な手を表示
        if DEBUG_MODE:
            valid_moves = self.get_valid_moves(self.current_player)
            player_name = "黒" if self.current_player == PLAYER_BLACK else "白"
            if valid_moves:
                moves_str = ", ".join([f"({r+1},{c+1})" for r, c in valid_moves])
                print(f"{player_name}の有効な手: {moves_str}")
            else:
                print(f"{player_name}の有効な手: なし（パス）")

    def get_valid_moves(self, player):
        """
        現在のプレイヤーが置ける有効な手のリストを返す。
        リストの要素は(行, 列)のタプル。
        """
        valid_moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.is_valid_move(r, c, player):
                    valid_moves.append((r, c))
        return valid_moves

    def check_game_over(self):
        """
        ゲーム終了条件を判定する。
        両プレイヤーが有効な手がない場合、または盤面が全て埋まった場合にゲーム終了。
        """
        if self.game_over: # 既にゲーム終了している場合は再チェックしない
            return True

        black_moves = self.get_valid_moves(PLAYER_BLACK)
        white_moves = self.get_valid_moves(PLAYER_WHITE)

        if not black_moves and not white_moves:
            self.game_over = True
            # 勝敗を判定して記録
            black_score, white_score = self.get_score()
            if black_score > white_score:
                self.message = f"黒の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
            elif white_score > black_score:
                self.message = f"白の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
            else:
                self.message = f"引き分け！ (スコア: 黒{black_score} - 白{white_score})"
            return True
        
        # 全マスが埋まった場合もゲーム終了
        if all(self.board[r][c] != 0 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)):
            self.game_over = True
            # 勝敗を判定して記録
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
        """現在のスコア（石の数）を計算して返す。(黒石の数, 白石の数)"""
        black_count = sum(row.count(PLAYER_BLACK) for row in self.board)
        white_count = sum(row.count(PLAYER_WHITE) for row in self.board)
        return black_count, white_count

    def calculate_move_reward(self, r, c, player):
        """
        指定された手(r, c)をplayerが打った場合の即時報酬（裏返した石の数）を計算する。
        """
        # make_moveが呼ばれる前に報酬を計算するため、一時的にボードを変更して評価
        # そしてボードを元に戻す、という処理が必要。
        # または、_get_flipped_stones()がフリップ数を直接返すようにする。

        # 現状の_get_flipped_stonesは、そのマスが空である前提で動作するので、
        # ここではmake_move()が呼び出す前のフリップ数をそのまま報酬とする。
        # make_move()が成功した場合に、その中でai_last_rewardに設定している。
        # このメソッドは、AIが手を決定する際の評価関数として使うことを想定。
        
        # 仮に石を置いた場合の裏返し数を取得
        flipped_stones = self._get_flipped_stones(r, c, player)
        return len(flipped_stones) * REWARD_FLIP_PER_STONE

    def calculate_game_result_reward(self, player):
        """
        ゲーム終了時の最終報酬を計算する。
        playerがそのゲームで得た報酬を返す。
        """
        black_score, white_score = self.get_score()

        if player == PLAYER_BLACK:
            if black_score > white_score:
                return REWARD_WIN
            elif black_score < white_score:
                return REWARD_LOSE
            else:
                return REWARD_DRAW
        else: # player == PLAYER_WHITE (AI)
            if white_score > black_score:
                return REWARD_WIN
            elif white_score < black_score:
                return REWARD_LOSE
            else:
                return REWARD_DRAW

    def ai_qlearning_move(self, qtable, learn=True):
        """
        Q学習に基づくAIの手選び・Q値更新
        learn=TrueならQ値を更新する（対人戦で学習）
        """
        state_key = board_to_key(self.board, self.current_player)
        valid_moves = self.get_valid_moves(self.current_player)
        if not valid_moves:
            self.ai_last_reward = 0
            self.last_ai_move = None  # パス時は赤枠を解除
            self.message = "AI（白）はパスしました。"
            return False

        # ε-greedy法で行動選択
        if random.random() < EPSILON:
            action = random.choice(valid_moves)
        else:
            qvals = [qtable.get((state_key, a), 0) for a in valid_moves]
            maxq = max(qvals)
            best_actions = [a for a, q in zip(valid_moves, qvals) if q == maxq]
            action = random.choice(best_actions)

        # 実際に手を打つ
        r, c = action
        flipped = self._get_flipped_stones(r, c, self.current_player)
        reward = len(flipped) * REWARD_FLIP_PER_STONE
        self.make_move(r, c, self.current_player)
        self.message = f"{'黒' if self.current_player == PLAYER_BLACK else '白'} (Q学習AI) が {chr(ord('A') + c)}{r+1} に置きました。(報酬: {reward})"
        self.ai_last_reward = reward
        self.last_ai_move = (r, c)  # 直前のAIの手を記録

        # Q値更新
        if learn:
            next_state_key = board_to_key(self.board, PLAYER_BLACK)  # 次は人間の番
            next_valid_moves = self.get_valid_moves(PLAYER_BLACK)
            if next_valid_moves:
                next_qvals = [qtable.get((next_state_key, a), 0) for a in next_valid_moves]
                max_next_q = max(next_qvals)
            else:
                # ゲーム終了時は最終報酬
                max_next_q = self.calculate_game_result_reward(self.current_player)
            old_q = qtable.get((state_key, action), 0)
            qtable[(state_key, action)] = old_q + ALPHA * (reward + GAMMA * max_next_q - old_q)
            
            # AI同士の対戦中は保存頻度を削減（毎手保存しない）
            global pretrain_in_progress
            if not pretrain_in_progress:
                save_qtable(qtable)
            global ai_learn_count
            ai_learn_count += 1
        return True


# Pygameの初期化
pygame.init()

# ウィンドウのサイズ設定 (盤面 + 余白)
WINDOW_WIDTH = BOARD_PIXEL_SIZE + BOARD_OFFSET_X * 2
WINDOW_HEIGHT = BOARD_PIXEL_SIZE + BOARD_OFFSET_Y * 2 + 100 # メッセージ表示エリアの追加
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("オセロゲーム")

# フォントの設定
try:
    font = pygame.font.Font("NotoSansCJKjp-Regular.otf", 36)
    small_font = pygame.font.Font("NotoSansCJKjp-Regular.otf", 24)
    tiny_font = pygame.font.Font("NotoSansCJKjp-Regular.otf", 20)
except:
    # フォントファイルが見つからない場合はシステムフォントを試行
    try:
        # pygameのシステムフォント機能を使用
        available_fonts = pygame.font.get_fonts()
        japanese_fonts = [f for f in available_fonts if any(char in f.lower() for char in ['japanese', 'gothic', 'mincho', 'yu', 'hiragino', 'noto'])]
        
        if japanese_fonts:
            # 日本語フォントが見つかった場合
            font_name = japanese_fonts[0]
            font = pygame.font.SysFont(font_name, 36)
            small_font = pygame.font.SysFont(font_name, 24)
            tiny_font = pygame.font.SysFont(font_name, 20)
        else:
            # システムフォントのパスを直接試行
            try:
                # Windowsの場合
                font = pygame.font.Font("C:/Windows/Fonts/msgothic.ttc", 36)
                small_font = pygame.font.Font("C:/Windows/Fonts/msgothic.ttc", 24)
                tiny_font = pygame.font.Font("C:/Windows/Fonts/msgothic.ttc", 20)
            except:
                try:
                    # macOSの場合
                    font = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 36)
                    small_font = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 24)
                    tiny_font = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 20)
                except:
                    try:
                        # Linuxの場合
                        font = pygame.font.Font("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", 36)
                        small_font = pygame.font.Font("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", 24)
                        tiny_font = pygame.font.Font("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", 20)
                    except:
                        # 最後の手段としてデフォルトフォントを使用
                        font = pygame.font.Font(None, 36)
                        small_font = pygame.font.Font(None, 24)
                        tiny_font = pygame.font.Font(None, 20)
    except:
        # 最後の手段としてデフォルトフォントを使用
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        tiny_font = pygame.font.Font(None, 20)

# Qテーブルの初期化・読み込み
def load_qtable():
    try:
        if os.path.exists(QTABLE_PATH):
            with open(QTABLE_PATH, "rb") as f:
                return pickle.load(f)
    except (pickle.PickleError, IOError, EOFError) as e:
        print(f"Qテーブルの読み込みエラー: {e}")
        print("新しいQテーブルを作成します。")
    return {}

def save_qtable(qtable):
    try:
        with open(QTABLE_PATH, "wb") as f:
            pickle.dump(qtable, f)
    except IOError as e:
        print(f"Qテーブルの保存エラー: {e}")

# 盤面をQテーブルのキーとして使えるように変換
def board_to_key(board, player):
    # 盤面と手番をタプル化
    return tuple(tuple(row) for row in board), player

def draw_board(screen, game_board):
    """盤面とマス目を描画する"""
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
    """石を描画する"""
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            stone = game_board[r][c]
            if stone != 0:
                center_x = c * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_X
                center_y = r * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_Y
                radius = SQUARE_SIZE // 2 - 5 # 石の半径

                color = BLACK if stone == PLAYER_BLACK else WHITE
                pygame.draw.circle(screen, color, (center_x, center_y), radius)


def display_message(screen, message, is_error=False):
    """画面下部にメッセージを表示する（はみ出さないように折り返し対応）"""
    color = RED if is_error else BLACK
    max_width = WINDOW_WIDTH - 40  # 両端に余白
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
    # 複数行を中央揃えで描画
    for i, l in enumerate(lines):
        text_surface = font.render(l, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 40 + i * 36))
    screen.blit(text_surface, text_rect)

def display_score(screen, black_score, white_score):
    """スコアを表示する（はみ出さないように位置調整）"""
    black_text = small_font.render(f"黒: {black_score}", True, BLACK)
    white_text = small_font.render(f"白: {white_score}", True, BLACK)
    # 盤面の下、左右に余白を持たせて表示
    screen.blit(black_text, (BOARD_OFFSET_X, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 10))
    screen.blit(white_text, (WINDOW_WIDTH - BOARD_OFFSET_X - white_text.get_width(), BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 10))

def display_ai_reward(screen, reward):
    """AIの最新報酬を表示する（はみ出さないように位置調整）"""
    reward_text = tiny_font.render(f"AI報酬 (直近): {reward}", True, BLACK)
    screen.blit(reward_text, (BOARD_OFFSET_X + 10, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 60))


def reset_game():
    """ゲームをリセットする（学習データは保持）"""
    global game, game_count, move_count
    game = OthelloGame() # 新しいゲームインスタンスを作成
    game.message = "新しいゲームが始まりました。黒の番です。"
    game_count += 1  # 対戦回数をカウントアップ
    move_count = 0   # 手数をリセット
    # 学習データ（qtable）は保持したまま


# --- ボタン描画・判定関数 ---
def draw_button(screen, x, y, w, h, text, font, mouse_pos, mouse_down):
    rect = pygame.Rect(x, y, w, h)
    is_hover = rect.collidepoint(mouse_pos)
    color = BUTTON_HOVER_COLOR if is_hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    # テキストがボタンに収まるかチェック
    text_surface = font.render(text, True, BUTTON_TEXT_COLOR)
    text_width = text_surface.get_width()
    
    # テキストがボタン幅を超える場合の処理
    if text_width > w - 10:  # 10ピクセルの余白を確保
        # フォントサイズを小さくして再試行（日本語フォントを使用）
        text_surface = small_font.render(text, True, BUTTON_TEXT_COLOR)
        text_width = text_surface.get_width()
        
        # それでも収まらない場合は、さらに小さくする
        if text_width > w - 10:
            text_surface = tiny_font.render(text, True, BUTTON_TEXT_COLOR)
            text_width = text_surface.get_width()
            
            # それでも収まらない場合は、テキストを省略
            if text_width > w - 10:
                # テキストを短縮して「...」を追加
                while len(text) > 3 and text_width > w - 10:
                    text = text[:-1]
                    text_surface = tiny_font.render(text + "...", True, BUTTON_TEXT_COLOR)
                    text_width = text_surface.get_width()
    
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    return is_hover and mouse_down

# --- リセットボタン ---
def draw_reset_button(screen, font, mouse_pos, mouse_down):
    x = WINDOW_WIDTH//2 - BUTTON_WIDTH//2
    y = BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 90
    return draw_button(screen, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, "リセット", font, mouse_pos, mouse_down)

# --- 戻るボタン ---
def draw_back_button(screen, font, mouse_pos, mouse_down):
    x = WINDOW_WIDTH//2 + BUTTON_WIDTH//2 + 20
    y = BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 90
    return draw_button(screen, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, "戻る", font, mouse_pos, mouse_down)

# --- 学習回数表示 ---
def draw_learn_count(screen, font):
    text = font.render(f"AI学習回数: {ai_learn_count}", True, (0,0,0))
    screen.blit(text, (BOARD_OFFSET_X, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 150))

# --- AI訓練回数表示 ---
def draw_pretrain_count(screen, font):
    text = font.render(f"AI訓練: {pretrain_now}/{pretrain_total}", True, (0,0,0))
    screen.blit(text, (BOARD_OFFSET_X, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 180))

# --- 対戦回数表示 ---
def draw_game_count(screen, font):
    text = font.render(f"対戦回数: {game_count}", True, (0,0,0))
    y = BOARD_OFFSET_Y // 2 - text.get_height() // 2
    screen.blit(text, (BOARD_OFFSET_X, y))

# --- 手数表示 ---
def draw_move_count(screen, font):
    """手数を表示する"""
    global move_count, last_move_count
    if move_count != last_move_count:
        text = font.render(f"手数: {move_count}", True, BLACK)
        x = BOARD_OFFSET_X + BOARD_PIXEL_SIZE - text.get_width()
        y = BOARD_OFFSET_Y // 2 - text.get_height() // 2
        screen.blit(text, (x, y))
        last_move_count = move_count

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

# --- モード選択画面 ---
def mode_select_screen(screen, font):
    global current_mode, pretrain_total, DEBUG_MODE, ai_speed, draw_mode
    selecting = True
    input_mode = False
    speed_input_mode = False
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
                if input_mode:
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
        if draw_button(screen, WINDOW_WIDTH//2-100, 150, 200, 50, "人間vsAIで学習", font, mouse_pos, mouse_down):
            current_mode = MODE_HUMAN_TRAIN
            selecting = False
        if draw_button(screen, WINDOW_WIDTH//2-120, 220, 240, 50, "AI同士で訓練→人間vsAI", font, mouse_pos, mouse_down):
            current_mode = MODE_AI_PRETRAIN
            selecting = False
        debug_text = "デバッグモード: ON" if DEBUG_MODE else "デバッグモード: OFF"
        if draw_button(screen, WINDOW_WIDTH//2-100, 290, 200, 40, debug_text, font, mouse_pos, mouse_down):
            DEBUG_MODE = not DEBUG_MODE
        draw_text = "AI描画: ON" if draw_mode else "AI描画: OFF"
        if draw_button(screen, WINDOW_WIDTH//2-100, 350, 200, 40, draw_text, font, mouse_pos, mouse_down):
            draw_mode = not draw_mode
        if draw_button(screen, WINDOW_WIDTH//2-100, 410, 200, 40, "カスタム入力", font, mouse_pos, mouse_down):
            input_mode = True
        speed_text = f"AI速度: {ai_speed}ms"
        if draw_button(screen, WINDOW_WIDTH//2-100, 470, 200, 40, speed_text, font, mouse_pos, mouse_down):
            speed_input_mode = True
        if input_mode:
            pygame.draw.rect(screen, (255, 255, 255), (WINDOW_WIDTH//2-100, 530, 200, 40))
            pygame.draw.rect(screen, (0, 0, 0), (WINDOW_WIDTH//2-100, 530, 200, 40), 2)
            input_surface = font.render(input_text, True, (0, 0, 0))
            screen.blit(input_surface, (WINDOW_WIDTH//2-90, 540))
            info = font.render("Enterで確定", True, (0, 0, 0))
            screen.blit(info, (WINDOW_WIDTH//2-info.get_width()//2, 580))
        elif speed_input_mode:
            pygame.draw.rect(screen, (255, 255, 255), (WINDOW_WIDTH//2-100, 530, 200, 40))
            pygame.draw.rect(screen, (0, 0, 0), (WINDOW_WIDTH//2-100, 530, 200, 40), 2)
            input_surface = font.render(speed_input_text, True, (0, 0, 0))
            screen.blit(input_surface, (WINDOW_WIDTH//2-90, 540))
            info = font.render("Enterで確定", True, (0, 0, 0))
            screen.blit(info, (WINDOW_WIDTH//2-info.get_width()//2, 580))
        else:
            info = font.render(f"訓練回数: {pretrain_total}", True, (0,0,0))
            screen.blit(info, (WINDOW_WIDTH//2-info.get_width()//2, 530))
        pygame.display.flip()
        pygame.time.Clock().tick(30)

def initialize_game_screen(game_obj):
    """ゲーム画面を初期化して描画する共通処理"""
    screen.fill(WHITE)
    draw_board(screen, game_obj.board)
    draw_stones(screen, game_obj.board)
    display_message(screen, game_obj.message, game_obj.last_move_error)
    black_score, white_score = game_obj.get_score()
    display_score(screen, black_score, white_score)
    display_ai_reward(screen, game_obj.ai_last_reward)
    draw_learn_count(screen, font)
    draw_game_count(screen, font)
    draw_move_count(screen, font)
    draw_reset_button(screen, font, (0, 0), False)
    draw_back_button(screen, font, (0, 0), False)
    pygame.display.flip()

# Qテーブルの初期化・読み込み
qtable = load_qtable()

# ゲームオブジェクトの作成
game = OthelloGame()

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
        initialize_game_screen(game)
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

# --- メインゲームループ ---
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
            
            # リセットボタンのクリック処理
            if draw_reset_button(screen, font, mouse_pos, mouse_down):
                # 現在のゲームをリセットして新しいゲームを開始
                game = OthelloGame()
                game_count += 1
                move_count = 0
                last_move_count = 0
                ai_speed = 60
                fast_mode = True
                draw_mode = True
                DEBUG_MODE = False
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
                # モード選択画面に戻る
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
                    initialize_game_screen(game)
                else:
                    # 人間vsAIモード
                    game = OthelloGame()
                    game_count += 1
                    initialize_game_screen(game)
                continue

    # AI同士の対戦処理
    if pretrain_in_progress:
        # AI同士の対戦中
        if not game.game_over:
            # 現在のプレイヤーの有効な手を取得
            valid_moves = game.get_valid_moves(game.current_player)
            if valid_moves:
                # AIの手を実行
                if game.ai_qlearning_move(qtable, learn=True):
                    game.switch_player()
                    game.check_game_over()
                else:
                    # パスの場合
                    game.message = f"{'黒' if game.current_player == PLAYER_BLACK else '白'}AIはパスしました。"
                    game.switch_player()
                    game.check_game_over()
            else:
                # 有効な手がない場合
                game.message = f"{'黒' if game.current_player == PLAYER_BLACK else '白'}AIはパスしました。"
                game.switch_player()
                game.check_game_over()
        else:
            # ゲーム終了時の処理
            black_score, white_score = game.get_score()
            if black_score > white_score:
                win_black += 1
            elif white_score > black_score:
                win_white += 1
            # 引き分けの場合は再戦（カウントしない）
            
            # 次の対戦に進むか、すべての対戦が終了したかチェック
            if win_black + win_white < pretrain_total:
                # 次の対戦を開始
                pretrain_now += 1
                game = OthelloGame()
                game_count += 1
                move_count = 0
                last_move_count = 0
                if draw_mode:
                    initialize_game_screen(game)
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
                # すべての対戦が終了 - Qテーブルを保存
                save_qtable(qtable)
                pretrain_in_progress = False
                
                # 訓練結果を表示
                screen.fill(WHITE)
                title = font.render("AI同士の訓練完了", True, (0, 0, 0))
                screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
                
                black_win_text = font.render(f"黒側AI勝利: {win_black}回", True, (0, 0, 0))
                screen.blit(black_win_text, (WINDOW_WIDTH//2 - black_win_text.get_width()//2, 150))
                
                white_win_text = font.render(f"白側AI勝利: {win_white}回", True, (0, 0, 0))
                screen.blit(white_win_text, (WINDOW_WIDTH//2 - white_win_text.get_width()//2, 180))
                
                total_text = font.render(f"総対戦数: {win_black + win_white}回", True, (0, 0, 0))
                screen.blit(total_text, (WINDOW_WIDTH//2 - total_text.get_width()//2, 210))
                
                click_text = font.render("クリックして人間vsAIモードへ", True, (0, 0, 255))
                screen.blit(click_text, (WINDOW_WIDTH//2 - click_text.get_width()//2, 280))
                
                pygame.display.flip()
                
                # ユーザーのクリックを待つ
                waiting_for_click = True
                while waiting_for_click:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            waiting_for_click = False
                
                # 人間vsAIモードに移行
                current_mode = MODE_HUMAN_TRAIN
                game = OthelloGame()
                game_count += 1
                ai_speed = 60
                fast_mode = True
                draw_mode = True
                DEBUG_MODE = False
                initialize_game_screen(game)
        
        # AI同士の対戦中の画面更新（最適化版）
        if draw_mode:
            # 描画モードON：盤面を描画
            if not fast_mode:
                # 通常モード：詳細な画面更新
                screen.fill(WHITE)
                draw_board(screen, game.board)
                draw_stones(screen, game.board)
                
                # 簡素化された情報表示
                black_score, white_score = game.get_score()
                display_score(screen, black_score, white_score)
                
                # 現在の対戦状況を表示
                count_text = font.render(f"AI同士の対戦: {pretrain_now} / {pretrain_total}", True, (0, 0, 255))
                screen.blit(count_text, (WINDOW_WIDTH//2 - count_text.get_width()//2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 50))
                
                # 勝敗状況を表示
                win_text = font.render(f"黒AI: {win_black}勝  白AI: {win_white}勝", True, (0, 0, 0))
                screen.blit(win_text, (WINDOW_WIDTH//2 - win_text.get_width()//2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 80))
                
                # 進行状況を表示
                progress_text = font.render(f"進行中...", True, (255, 0, 0))
                screen.blit(progress_text, (WINDOW_WIDTH//2 - progress_text.get_width()//2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 110))
                
                pygame.display.flip()
            else:
                # 高速モード：毎手描画（駒を置くごと）
                screen.fill(WHITE)
                draw_board(screen, game.board)
                draw_stones(screen, game.board)
                
                # 最小限の情報表示
                count_text = font.render(f"高速訓練: {pretrain_now}/{pretrain_total} - {win_black}:{win_white}", True, (0, 0, 255))
                screen.blit(count_text, (WINDOW_WIDTH//2 - count_text.get_width()//2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 50))
                
                # 現在の手数を表示
                move_text = font.render(f"手数: {move_count}", True, (0, 0, 0))
                screen.blit(move_text, (WINDOW_WIDTH//2 - move_text.get_width()//2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 80))
                
                pygame.display.flip()
        else:
            # 描画モードOFF：プログレスバーのみ表示（5手に1回更新）
            if move_count % 5 == 0 or game.game_over:
                screen.fill(WHITE)
                
                # タイトル
                title = font.render("AI同士の訓練中", True, (0, 0, 0))
                screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
                
                # 現在の対戦状況
                current_text = font.render(f"対戦 {pretrain_now} / {pretrain_total}", True, (0, 0, 0))
                screen.blit(current_text, (WINDOW_WIDTH//2 - current_text.get_width()//2, 150))
                
                # 勝敗状況
                win_text = font.render(f"黒AI: {win_black}勝  白AI: {win_white}勝", True, (0, 0, 0))
                screen.blit(win_text, (WINDOW_WIDTH//2 - win_text.get_width()//2, 180))
                
                # プログレスバー（対戦全体の進捗）
                draw_progress_bar(screen, pretrain_now - 1, pretrain_total, 
                                WINDOW_WIDTH//2 - 150, 220, 300, 40)
                
                # 現在のゲームの手数
                move_text = font.render(f"現在の手数: {move_count}", True, (0, 0, 0))
                screen.blit(move_text, (WINDOW_WIDTH//2 - move_text.get_width()//2, 280))
                
                # 高速処理中メッセージ
                speed_text = font.render("高速処理中...", True, (255, 0, 0))
                screen.blit(speed_text, (WINDOW_WIDTH//2 - speed_text.get_width()//2, 320))
                
                pygame.display.flip()
        
        # 高速モードの場合は待機時間を短縮
        if fast_mode:
            if draw_mode:
                pygame.time.wait(ai_speed // 4)  # 描画モードON：高速モードではさらに短縮
            else:
                pygame.time.wait(ai_speed // 8)  # 描画モードOFF：さらに短縮
        else:
            pygame.time.wait(ai_speed // 2)  # AIの思考時間を半分に短縮
        continue

    # ゲームが終了していない場合の盤面クリック処理
    if not game.game_over:
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            if (BOARD_OFFSET_X <= mouse_pos[0] < BOARD_OFFSET_X + BOARD_PIXEL_SIZE and
                BOARD_OFFSET_Y <= mouse_pos[1] < BOARD_OFFSET_Y + BOARD_PIXEL_SIZE):
                col = (mouse_pos[0] - BOARD_OFFSET_X) // SQUARE_SIZE
                row = (mouse_pos[1] - BOARD_OFFSET_Y) // SQUARE_SIZE
                game.highlighted_square = (row, col)
            else:
                game.highlighted_square = None
        
        # 人間プレイヤー（黒）の番の場合の盤面クリック処理
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game.current_player == PLAYER_BLACK:
            if (BOARD_OFFSET_X <= mouse_pos[0] < BOARD_OFFSET_X + BOARD_PIXEL_SIZE and
                BOARD_OFFSET_Y <= mouse_pos[1] < BOARD_OFFSET_Y + BOARD_PIXEL_SIZE):
                col = (mouse_pos[0] - BOARD_OFFSET_X) // SQUARE_SIZE
                row = (mouse_pos[1] - BOARD_OFFSET_Y) // SQUARE_SIZE
                if game.make_move(row, col, game.current_player):
                    # 一手目の裏返しを確実に描画するため、即座に画面を更新
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
                    draw_reset_button(screen, font, mouse_pos, False)
                    draw_back_button(screen, font, mouse_pos, False)
                    pygame.display.flip()
                    
                    game.switch_player()
                    game.check_game_over()
                else:
                    game.message = "そこには置けません！別の場所を選んでください。"
                    game.last_move_error = True
            else:
                game.message = "盤面内をクリックしてください。"
                game.last_move_error = True
            if not game.get_valid_moves(PLAYER_BLACK):
                game.message = "プレイヤー（黒）はパスしました。"
                game.switch_player()
                game.check_game_over()
        else:
            # ゲーム終了時のクリックで次の対戦に移行
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 新しいゲームを開始
                game = OthelloGame()
                game_count += 1
                move_count = 0
                last_move_count = 0
                ai_speed = 60
                fast_mode = True
                draw_mode = True
                DEBUG_MODE = False
                initialize_game_screen(game)

    # AIの番の処理（人間vsAIモード）
    if not game.game_over and game.current_player == PLAYER_WHITE and not pretrain_in_progress:
        pygame.time.wait(500)
        valid_moves = game.get_valid_moves(game.current_player)
        if valid_moves:
            if game.ai_qlearning_move(qtable, learn=True):
                game.switch_player()
                game.check_game_over()
            else:
                game.message = "AI（白）はパスしました。"
                game.ai_last_reward = 0
                game.last_ai_move = None
                game.switch_player()
                game.check_game_over()
        else:
            game.message = "AI（白）はパスしました。"
            game.ai_last_reward = 0
            game.last_ai_move = None
            game.switch_player()
            game.check_game_over()

    # ゲーム終了時の勝敗表示処理（最優先で処理）
    if game.game_over and not game.game_over_displayed and not pretrain_in_progress:
        # ゲーム終了時の最終報酬計算
        ai_final_reward = game.calculate_game_result_reward(PLAYER_WHITE)
        black_score, white_score = game.get_score()
        
        # 勝敗判定とメッセージ作成
        if black_score > white_score:
            final_message = f"黒の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
            game.message = final_message
        elif white_score > black_score:
            final_message = f"白の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
            game.message = final_message
        else:
            final_message = f"引き分け！ (スコア: 黒{black_score} - 白{white_score})"
            game.message = final_message
        
        # AIの最終報酬を表示
        game.ai_last_reward = ai_final_reward
        
        # ゲーム終了表示フラグを設定（重複表示を防ぐ）
        game.game_over_displayed = True
        
        # 勝敗結果を一時的に大きく表示
        screen.fill(WHITE)
        draw_board(screen, game.board)
        draw_stones(screen, game.board)
        
        # 勝敗メッセージを大きく表示（日本語フォントを使用）
        try:
            result_font = pygame.font.Font("NotoSansCJKjp-Regular.otf", 48)
        except:
            try:
                result_font = pygame.font.SysFont("msgothic", 48)
            except:
                result_font = pygame.font.Font(None, 48)
        
        result_surface = result_font.render(final_message, True, (255, 0, 0))
        result_rect = result_surface.get_rect(center=(WINDOW_WIDTH//2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 50))
        screen.blit(result_surface, result_rect)
        
        # AI最終報酬を表示
        reward_text = f"AI最終報酬: {ai_final_reward}"
        reward_surface = font.render(reward_text, True, (0, 0, 255))
        reward_rect = reward_surface.get_rect(center=(WINDOW_WIDTH//2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 80))
        screen.blit(reward_surface, reward_rect)
        
        # クリックでリスタートの指示
        restart_text = "盤面をクリックして次の対戦へ"
        restart_surface = font.render(restart_text, True, (0, 0, 0))
        restart_rect = restart_surface.get_rect(center=(WINDOW_WIDTH//2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 110))
        screen.blit(restart_surface, restart_rect)
        
        # スコア表示
        display_score(screen, black_score, white_score)
        display_ai_reward(screen, game.ai_last_reward)
        draw_learn_count(screen, font)
        draw_game_count(screen, font)
        draw_move_count(screen, font)
        draw_reset_button(screen, font, mouse_pos, False)
        draw_back_button(screen, font, mouse_pos, False)
        pygame.display.flip()
        
        # 勝敗表示を少し待つ（ユーザーが結果を確認できるように）
        pygame.time.wait(2000)
        
        # ゲーム終了時の表示が完了したら、通常の画面更新をスキップ
        continue

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
    draw_reset_button(screen, font, mouse_pos, False)
    draw_back_button(screen, font, mouse_pos, False)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()