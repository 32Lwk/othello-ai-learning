import random
import pickle
from typing import Optional
from constants import *
from ai_learning import LearningHistory, LearningLogger

# グローバル変数
qtable = {}

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
        return list(valid_moves)

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
        
        # 次のプレイヤーに有効な手がない場合はパス
        next_player = self.current_player
        if not self.get_valid_moves(next_player):
            # パスメッセージを設定
            if next_player == PLAYER_BLACK:
                self.message = "黒は置ける場所がないためパスしました。"
            else:
                self.message = f"AI（{'黒' if next_player == PLAYER_BLACK else '白'}）はパスしました。"
            
            # さらに次のプレイヤーもチェック
            next_next_player = PLAYER_WHITE if next_player == PLAYER_BLACK else PLAYER_BLACK
            if not self.get_valid_moves(next_next_player):
                # 両プレイヤーとも置けない場合はゲーム終了
                self.game_over = True
                black_score, white_score = self.get_score()
                if black_score > white_score:
                    self.message = f"黒の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
                elif white_score > black_score:
                    self.message = f"白の勝ち！ (スコア: 黒{black_score} - 白{white_score})"
                else:
                    self.message = f"引き分け！ (スコア: 黒{black_score} - 白{white_score})"
            else:
                # 次の次のプレイヤーに手がある場合は、そのプレイヤーに切り替え
                self.current_player = next_next_player
                self.message = f"{'黒' if self.current_player == PLAYER_BLACK else '白'}の番です。"
        else:
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

    def ai_qlearning_move(self, qtable, learn=True, player=None, ai_learn_count=0):
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

        # --- ε-greedy探索率を減衰させる ---
        initial_epsilon = 0.2  # 初期値
        min_epsilon = 0.01     # 最小値
        decay_rate = 0.995     # 減衰率
        current_epsilon = max(min_epsilon, initial_epsilon * (decay_rate ** ai_learn_count))

        # ε-greedy法で行動選択
        if random.random() < current_epsilon:
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
        
        # --- 戦略的報酬の計算 ---
        # 角を取った場合の報酬
        corners = [(0,0), (0,7), (7,0), (7,7)]
        if (r, c) in corners:
            reward += REWARD_CORNER
        
        # エッジを取った場合のペナルティ（角の隣は危険）
        edges = [(0,1), (0,6), (1,0), (1,7), (6,0), (6,7), (7,1), (7,6)]
        if (r, c) in edges:
            reward += REWARD_EDGE
        
        # 安定石の報酬（角に隣接する石）
        stable_positions = [(0,1), (1,0), (1,1), (0,6), (1,6), (1,7), (6,0), (6,1), (7,1), (6,6), (6,7), (7,6)]
        if (r, c) in stable_positions:
            reward += REWARD_STABLE_STONE
        
        # 中心部の報酬
        center_positions = [(3,3), (3,4), (4,3), (4,4)]
        if (r, c) in center_positions:
            reward += REWARD_TERRITORY
        
        # モビリティ（合法手の数）の報酬
        opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
        opponent_moves_before = len(self.get_valid_moves(opponent))
        
        self.make_move(r, c, player)
        
        opponent_moves_after = len(self.get_valid_moves(opponent))
        mobility_change = opponent_moves_before - opponent_moves_after
        reward += mobility_change * REWARD_MOBILITY
        
        self.message = f"{'黒' if player == PLAYER_BLACK else '白'} (Q学習AI) が {chr(ord('A') + c)}{r+1} に置きました。(報酬: {reward})"
        self.ai_last_reward = reward
        self.last_ai_move = (r, c)

        # Q値更新
        if learn:
            next_state_key = self.get_board_state_key()
            next_player = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
            next_valid_moves = self.get_valid_moves(next_player)
            max_next_q = 0.0
            if next_valid_moves:
                max_next_q = max(qtable.get(f"{next_state_key}_{move[0]}_{move[1]}", 0.0) 
                               for move in next_valid_moves)
            else:
                max_next_q = self.calculate_game_result_reward(player)
            action_key = f"{state_key}_{action[0]}_{action[1]}"
            current_q = qtable.get(action_key, 0.0)
            new_q = current_q + ALPHA * (reward + GAMMA * max_next_q - current_q)
            qtable[action_key] = new_q
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