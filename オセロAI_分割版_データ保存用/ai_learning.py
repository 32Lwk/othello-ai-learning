import json
import os
from datetime import datetime
from collections import deque
import pickle
import random
from constants import *
import pygame
import sys
import time
import glob
from typing import Optional
from ui_components import draw_ai_battle_progress_graphs, draw_board, draw_stones, display_message, display_score, draw_progress_bar, draw_learn_count, draw_game_count, draw_current_player_indicator

class LearningHistory:
    def __init__(self, max_history=100, save_file="learning_history.json"):
        self.max_history = max_history
        self.save_file = save_file
        self.history = deque(maxlen=max_history)
        self.load_history()
    
    def add_record(self, game_count, ai_learn_count, ai_win_count, ai_lose_count, 
                   ai_draw_count, ai_total_reward, ai_avg_reward, qtable_size, black_score=0, white_score=0, game_type="unknown"):
        record = {
            "timestamp": datetime.now().isoformat(),
            "game_count": game_count,  # 累積の総対戦回数
            "ai_learn_count": ai_learn_count,
            "ai_win_count": ai_win_count,
            "ai_lose_count": ai_lose_count,
            "ai_draw_count": ai_draw_count,
            "ai_total_reward": ai_total_reward,
            "ai_avg_reward": ai_avg_reward,
            "qtable_size": qtable_size,
            "black_score": black_score,
            "white_score": white_score,
            "win_rate": self._calculate_win_rate(ai_win_count, ai_lose_count, ai_draw_count),
            "total_games": ai_win_count + ai_lose_count + ai_draw_count,  # 勝敗記録の合計（検証用）
            "game_type": game_type  # 対戦タイプ: "human_vs_ai", "ai_vs_ai", "unknown"
        }
        
        self.history.append(record)
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
    
    def get_qtable_size_history(self):
        return [record["qtable_size"] for record in self.history]
    
    def get_learn_count_history(self):
        return [record["ai_learn_count"] for record in self.history]
    
    def get_latest_stats(self):
        if not self.history:
            return None
        return self.history[-1]
    
    def save_history_to_file(self, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(list(self.history), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"学習履歴の保存エラー ({filename}): {e}")
    
    def load_history_from_file(self, filename):
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = deque(data, maxlen=self.max_history)
            else:
                self.history = deque(maxlen=self.max_history)
        except Exception as e:
            print(f"学習履歴の読み込みエラー ({filename}): {e}")
            self.history = deque(maxlen=self.max_history)

    def get_cumulative_stats(self):
        """履歴全体の累積値から統計を算出（履歴全体から正確に計算）"""
        if not self.history:
            return None
        
        # 履歴全体から累積値を計算
        total_learn = 0
        total_win = 0
        total_lose = 0
        total_draw = 0
        total_reward = 0
        total_games = 0
        
        # 各記録の増分を計算して累積値を算出
        prev_learn = 0
        prev_win = 0
        prev_lose = 0
        prev_draw = 0
        prev_reward = 0
        prev_games = 0
        
        for record in self.history:
            # 現在の記録値
            curr_learn = record.get("ai_learn_count", 0)
            curr_win = record.get("ai_win_count", 0)
            curr_lose = record.get("ai_lose_count", 0)
            curr_draw = record.get("ai_draw_count", 0)
            curr_reward = record.get("ai_total_reward", 0)
            curr_games = record.get("total_games", 0)
            
            # 増分を計算（前回との差分）
            learn_increment = max(0, curr_learn - prev_learn)
            win_increment = max(0, curr_win - prev_win)
            lose_increment = max(0, curr_lose - prev_lose)
            draw_increment = max(0, curr_draw - prev_draw)
            reward_increment = max(0, curr_reward - prev_reward)
            games_increment = max(0, curr_games - prev_games)
            
            # 累積値に加算
            total_learn += learn_increment
            total_win += win_increment
            total_lose += lose_increment
            total_draw += draw_increment
            total_reward += reward_increment
            total_games += games_increment
            
            # 前回値を更新
            prev_learn = curr_learn
            prev_win = curr_win
            prev_lose = curr_lose
            prev_draw = curr_draw
            prev_reward = curr_reward
            prev_games = curr_games
        
        # 平均報酬と勝率を計算
        avg_reward = (total_reward / total_learn) if total_learn > 0 else 0
        win_rate = (total_win / (total_win + total_lose + total_draw) * 100) if (total_win + total_lose + total_draw) > 0 else 0
        
        # 最新のQテーブルサイズを取得
        latest_qtable_size = self.history[-1].get("qtable_size", 0) if self.history else 0
        
        return {
            "ai_learn_count": total_learn,
            "ai_win_count": total_win,
            "ai_lose_count": total_lose,
            "ai_draw_count": total_draw,
            "ai_total_reward": total_reward,
            "ai_avg_reward": avg_reward,
            "win_rate": win_rate,
            "total_games": total_games,
            "qtable_size": latest_qtable_size
        }

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

# Qテーブルの保存・読み込み

def save_qtable(qtable):
    """Qテーブルを保存 - othello-ai-learning参考版"""
    try:
        with open(QTABLE_PATH, "wb") as f:
            pickle.dump(qtable, f)
        print(f"Qテーブルを保存しました: {len(qtable)}エントリ")
    except Exception as e:
        print(f"Qテーブルの保存エラー: {e}")

def load_qtable():
    """Qテーブルを読み込み - othello-ai-learning参考版"""
    try:
        if os.path.exists(QTABLE_PATH):
            with open(QTABLE_PATH, "rb") as f:
                qtable = pickle.load(f)
                print(f"Qテーブルを読み込みました: {len(qtable)}エントリ")
                return qtable
    except Exception as e:
        print(f"Qテーブルの読み込みエラー: {e}")
    return {}

# AIの手番実行（Q学習）
def ai_qlearning_move(game, qtable, learn=True, player=None, ai_learn_count=0):
    if player is None:
        player = game.current_player
    state_key = game.get_board_state_key()
    valid_moves = game.get_valid_moves(player)
    if not valid_moves:
        return False
    
    # --- 自己対戦用のε-greedy探索率（より洗練された減衰） ---
    initial_epsilon = 0.3  # 初期値（0.4→0.3に調整、より安定）
    min_epsilon = 0.05     # 最小値（0.03→0.05に調整、より探索的）
    decay_rate = 0.999     # 減衰率（維持）
    current_epsilon = max(min_epsilon, initial_epsilon * (decay_rate ** ai_learn_count))
    
    # 自己対戦時は探索率を少し下げる（より戦略的な行動）
    if learn:
        current_epsilon *= 0.8  # 0.7→0.8に調整、より探索的
    
    # --- 新規追加：動的ε調整 ---
    # 学習回数に応じて探索率を動的に調整
    if ai_learn_count > 1000:
        current_epsilon *= 0.9  # 1000回以上学習したら探索率を下げる（0.8→0.9に調整）
    elif ai_learn_count > 500:
        current_epsilon *= 0.95  # 500回以上学習したら探索率を少し下げる（0.9→0.95に調整）
    
    # ε-greedy法
    if random.random() < current_epsilon:
        action = random.choice(valid_moves)
    else:
        best_move = None
        best_q_value = float('-inf')
        for move in valid_moves:
            action_key = f"{state_key}_{move[0]}_{move[1]}"
            q_value = qtable.get(action_key, 0.0)
            if q_value > best_q_value:
                best_q_value = q_value
                best_move = move
        action = best_move if best_move is not None else random.choice(valid_moves)
    
    r, c = action
    flipped = game._get_flipped_stones(r, c, player)
    reward = len(flipped) * REWARD_FLIP_PER_STONE
    
    # --- 戦略的報酬の計算（自己対戦強化版） ---
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
    
    # 位置による報酬（自己対戦強化版）
    # 盤面の外側から内側に向かって報酬が増加
    distance_from_edge = min(r, 7-r, c, 7-c)
    reward += distance_from_edge * REWARD_POSITIONAL
    
    # モビリティ（合法手の数）の報酬
    opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
    opponent_moves_before = len(game.get_valid_moves(opponent))
    
    game.make_move(r, c, player)
    
    opponent_moves_after = len(game.get_valid_moves(opponent))
    mobility_change = opponent_moves_before - opponent_moves_after
    reward += mobility_change * REWARD_MOBILITY
    
    # --- 自己対戦特有の報酬設計 ---
    # 相手の選択肢を制限する手への追加報酬
    if opponent_moves_after == 0:
        reward += REWARD_PASS_FORCE  # 相手のパスを強制した場合のボーナス
    
    # 終盤での石の数の重要性を増加
    total_moves = sum(1 for row in game.board for cell in row if cell != 0)
    if total_moves > 50:  # 終盤（50手以降）
        reward *= 1.3  # 報酬を30%増加（1.2→1.3に強化）
    
    # --- 新規追加：より高度な戦略的報酬 ---
    # 1. 石の安定性評価
    stability_bonus = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if game.board[nr][nc] == player:
                    stability_bonus += 0.5  # 隣接する味方の石による安定性
    reward += stability_bonus
    
    # 2. 相手の石を囲む手へのボーナス
    surrounding_bonus = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if game.board[nr][nc] == opponent:
                    surrounding_bonus += 1.0  # 相手の石を囲む手
    reward += surrounding_bonus
    
    # 3. 盤面の支配力評価
    player_stones = sum(1 for row in game.board for cell in row if cell == player)
    opponent_stones = sum(1 for row in game.board for cell in row if cell == opponent)
    dominance = (player_stones - opponent_stones) / (player_stones + opponent_stones + 1)
    reward += dominance * 2.0  # 支配力による報酬
    
    # 4. 終盤での石の数の重要性をさらに強化
    if total_moves > 55:  # 非常に終盤（55手以降）
        reward *= 1.5  # 報酬を50%増加
    elif total_moves > 45:  # 中盤後半（45手以降）
        reward *= 1.2  # 報酬を20%増加
    
    # --- 終局報酬の追加 ---
    game.check_game_over()
    if game.game_over:
        black_score, white_score = game.get_score()
        if player == PLAYER_WHITE:  # AI（白）の場合
            if white_score > black_score:
                reward += REWARD_WIN
            elif black_score > white_score:
                reward += REWARD_LOSE
            else:
                reward += REWARD_DRAW
        else:  # AI（黒）の場合
            if black_score > white_score:
                reward += REWARD_WIN
            elif white_score > black_score:
                reward += REWARD_LOSE
            else:
                reward += REWARD_DRAW
    else:
        # ゲーム終了前のパリティ（石の数の差）による報酬
        black_score, white_score = game.get_score()
        if player == PLAYER_WHITE:
            parity = white_score - black_score
        else:
            parity = black_score - white_score
        reward += parity * 0.1  # パリティによる小さな報酬
    
    # AIが石を置いた位置を記録
    if player == PLAYER_WHITE:  # AI（白）の場合のみ
        game.last_ai_move = (r, c)
    
    if learn:
        next_state_key = game.get_board_state_key()
        next_player = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
        next_valid_moves = game.get_valid_moves(next_player)
        max_next_q = 0.0
        if next_valid_moves:
            max_next_q = max(qtable.get(f"{next_state_key}_{move[0]}_{move[1]}", 0.0) for move in next_valid_moves)
        action_key = f"{state_key}_{action[0]}_{action[1]}"
        current_q = qtable.get(action_key, 0.0)
        new_q = current_q + ALPHA * (reward + GAMMA * max_next_q - current_q)
        qtable[action_key] = new_q
    
    return True, reward

# 学習データ管理機能
def save_learning_data(qtable, learning_history, screen, font):
    """
    学習データを保存（エラーハンドリング・デバッグ強化）
    """
    save_name = show_save_name_input(screen, font)
    if not save_name:
        print("[保存] キャンセルされました")
        return
    try:
        qtable_filename = f"qtable_{save_name}.pkl"
        history_filename = f"learning_history_{save_name}.json"
        print(f"[保存] Qテーブル保存先: {qtable_filename}")
        print(f"[保存] 履歴保存先: {history_filename}")
        save_qtable_to_file(qtable, qtable_filename)
        learning_history.save_history_to_file(history_filename)
        show_save_complete_message(screen, font, save_name)
        print(f"[保存] 学習データ '{save_name}' を保存しました")
    except Exception as e:
        import traceback
        print(f"[保存エラー] {e}")
        traceback.print_exc()
        show_save_error_message(screen, font, str(e))

def overwrite_learning_data(qtable, learning_history, screen, font):
    """
    学習データを上書き保存（既存データの選択・上書き）
    """
    # 保存済みデータの一覧を取得
    saved_data = get_saved_data_list()
    if not saved_data:
        print("[上書き保存] 保存済みデータがありません。新規保存を使用してください。")
        show_no_saved_data_message(screen, font)
        return
    
    # 上書き対象選択画面を表示
    selected_data = show_data_selection_screen(screen, font, saved_data, "上書きするデータを選択")
    if not selected_data:
        print("[上書き保存] キャンセルされました")
        return
    
    # 上書き確認メッセージを表示
    if show_confirm_overwrite_message(screen, font, selected_data):
        try:
            qtable_filename = f"qtable_{selected_data}.pkl"
            history_filename = f"learning_history_{selected_data}.json"
            print(f"[上書き保存] Qテーブル保存先: {qtable_filename}")
            print(f"[上書き保存] 履歴保存先: {history_filename}")
            save_qtable_to_file(qtable, qtable_filename)
            learning_history.save_history_to_file(history_filename)
            show_overwrite_complete_message(screen, font, selected_data)
            print(f"[上書き保存] 学習データ '{selected_data}' を上書き保存しました")
        except Exception as e:
            import traceback
            print(f"[上書き保存エラー] {e}")
            traceback.print_exc()
            show_save_error_message(screen, font, str(e))

def create_new_learning_data(qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, screen, font):
    """新しい学習データを作成"""
    # 新規作成名入力画面を表示
    new_name = show_new_data_name_input(screen, font)
    if not new_name:
        return  # キャンセルされた場合
    
    # 確認メッセージを表示
    if show_confirm_new_data_message(screen, font, new_name):
        try:
            # データをリセット
            qtable.clear()
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

def load_learning_data(qtable, learning_history, screen, font):
    """
    学習データを読み込み（エラーハンドリング・デバッグ強化・値返却）
    """
    saved_data = get_saved_data_list()
    if not saved_data:
        print("[読み込み] 保存済みデータがありません")
        show_no_saved_data_message(screen, font)
        return None
    selected_data = show_data_selection_screen(screen, font, saved_data)
    if not selected_data:
        print("[読み込み] キャンセルされました")
        return None
    try:
        qtable_filename = f"qtable_{selected_data}.pkl"
        history_filename = f"learning_history_{selected_data}.json"
        print(f"[読み込み] Qテーブル読み込み元: {qtable_filename}")
        print(f"[読み込み] 履歴読み込み元: {history_filename}")
        qtable.clear()
        qtable.update(load_qtable_from_file(qtable_filename))
        learning_history.load_history_from_file(history_filename)
        latest = learning_history.get_latest_stats()
        show_load_complete_message(screen, font, selected_data)
        print(f"[読み込み] 学習データ '{selected_data}' を読み込みました")
        if latest:
            return (
                latest['game_count'],
                latest['ai_learn_count'],
                latest['ai_win_count'],
                latest['ai_lose_count'],
                latest['ai_draw_count'],
                latest['ai_total_reward'],
                latest['ai_avg_reward']
            )
        else:
            return None
    except Exception as e:
        import traceback
        print(f"[読み込みエラー] {e}")
        traceback.print_exc()
        show_load_error_message(screen, font, str(e))
        return None

def confirm_delete_learning_data(screen, font):
    """学習データ削除の確認"""
    # 保存済みデータの一覧を取得
    saved_data = get_saved_data_list()
    if not saved_data:
        show_no_saved_data_message(screen, font)
        return
    
    # 削除対象選択画面を表示
    selected_data = show_data_selection_screen(screen, font, saved_data, "削除するデータを選択")
    if not selected_data:
        return  # キャンセルされた場合
    
    # 確認メッセージを表示
    if show_confirm_delete_message(screen, font, selected_data):
        try:
            # ファイルを削除
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
    with open(filename, 'wb') as f:
        pickle.dump(qtable_data, f)

def load_qtable_from_file(filename):
    """Qテーブルを指定ファイルから読み込み"""
    with open(filename, 'rb') as f:
        return pickle.load(f)

def show_save_name_input(screen, font):
    """保存名入力画面を表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    return input_text if input_text.strip() else None
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    # 英数字とアンダースコアのみ許可
                    if event.unicode.isalnum() or event.unicode == '_':
                        input_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if save_button.collidepoint(mouse_pos):
                    return input_text if input_text.strip() else None
                elif cancel_button.collidepoint(mouse_pos):
                    return None
        
        # 入力テキストを再描画
        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, (100, 100, 100), input_box, 2)
        text_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 10))
        
        pygame.display.flip()
    
    return None

def show_new_data_name_input(screen, font):
    """新規データ名入力画面を表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
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
    pygame.draw.rect(screen, (100, 200, 100), create_button)
    pygame.draw.rect(screen, (50, 150, 50), create_button, 2)
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    return input_text if input_text.strip() else None
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    # 英数字とアンダースコアのみ許可
                    if event.unicode.isalnum() or event.unicode == '_':
                        input_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if create_button.collidepoint(mouse_pos):
                    return input_text if input_text.strip() else None
                elif cancel_button.collidepoint(mouse_pos):
                    return None
        
        # 入力テキストを再描画
        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, (100, 100, 100), input_box, 2)
        text_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 10))
        
        pygame.display.flip()
    
    return None

def show_data_selection_screen(screen, font, data_list, title_text="データを選択"):
    """データ選択画面を表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render(title_text, True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
    
    # データリストを表示
    list_font = get_japanese_font(14)
    y_offset = 150
    button_rects = []
    
    for i, data_name in enumerate(data_list):
        button_rect = pygame.Rect(WINDOW_WIDTH//2 - 200, y_offset, 400, 40)
        button_rects.append(button_rect)
        
        # ボタン背景
        pygame.draw.rect(screen, (240, 240, 240), button_rect)
        pygame.draw.rect(screen, (100, 100, 100), button_rect, 2)
        
        # データ名
        text_surface = list_font.render(data_name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
        
        y_offset += 50
    
    # キャンセルボタン
    cancel_button = pygame.Rect(WINDOW_WIDTH//2 - 100, y_offset + 20, 200, 40)
    pygame.draw.rect(screen, (200, 200, 200), cancel_button)
    pygame.draw.rect(screen, (100, 100, 100), cancel_button, 2)
    cancel_text = font.render("キャンセル", True, (0, 0, 0))
    cancel_text_rect = cancel_text.get_rect(center=cancel_button.center)
    screen.blit(cancel_text, cancel_text_rect)
    
    help_text = font.render("ESCキーでキャンセル", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, y_offset + 80))
    
    pygame.display.flip()
    
    # 選択処理
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if cancel_button.collidepoint(mouse_pos):
                    return None
                
                # データボタンのクリック判定
                for i, button_rect in enumerate(button_rects):
                    if button_rect.collidepoint(mouse_pos):
                        return data_list[i]
    
    return None

def show_save_complete_message(screen, font, save_name):
    """保存完了メッセージを表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render("保存完了", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render(f"学習データ '{save_name}' を保存しました", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 320))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                return

def show_confirm_new_data_message(screen, font, new_name):
    """新規データ作成確認メッセージを表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render("新規データ作成確認", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
    
    message1 = font.render(f"新しい学習データ '{new_name}' を作成しますか？", True, (0, 0, 0))
    screen.blit(message1, (WINDOW_WIDTH//2 - message1.get_width()//2, 200))
    
    message2 = font.render("現在のデータはすべてリセットされます", True, (255, 0, 0))
    screen.blit(message2, (WINDOW_WIDTH//2 - message2.get_width()//2, 230))
    
    # ボタン
    confirm_button = pygame.Rect(WINDOW_WIDTH//2 - 150, 280, 120, 40)
    pygame.draw.rect(screen, (255, 100, 100), confirm_button)
    pygame.draw.rect(screen, (200, 50, 50), confirm_button, 2)
    confirm_text = font.render("作成", True, (0, 0, 0))
    confirm_text_rect = confirm_text.get_rect(center=confirm_button.center)
    screen.blit(confirm_text, confirm_text_rect)
    
    cancel_button = pygame.Rect(WINDOW_WIDTH//2 + 30, 280, 120, 40)
    pygame.draw.rect(screen, (200, 200, 200), cancel_button)
    pygame.draw.rect(screen, (100, 100, 100), cancel_button, 2)
    cancel_text = font.render("キャンセル", True, (0, 0, 0))
    cancel_text_rect = cancel_text.get_rect(center=cancel_button.center)
    screen.blit(cancel_text, cancel_text_rect)
    
    pygame.display.flip()
    
    # 選択処理
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if confirm_button.collidepoint(mouse_pos):
                    return True
                elif cancel_button.collidepoint(mouse_pos):
                    return False
    
    return False

def show_confirm_delete_message(screen, font, data_name):
    """削除確認メッセージを表示"""
    screen.fill((30, 60, 80))
    
    # タイトル
    title_text = font.render("削除確認", True, (255, 255, 255))
    screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 200))
    
    # メッセージ
    message_font = get_japanese_font(24)
    message_text = message_font.render(f"学習データ '{data_name}' を削除しますか？", True, (255, 255, 255))
    screen.blit(message_text, (WINDOW_WIDTH//2 - message_text.get_width()//2, 250))
    
    warning_text = message_font.render("この操作は取り消せません", True, (255, 200, 200))
    screen.blit(warning_text, (WINDOW_WIDTH//2 - warning_text.get_width()//2, 290))
    
    # ボタン
    button_font = get_japanese_font(20)
    
    # 削除ボタン
    delete_button = pygame.Rect(WINDOW_WIDTH//2 - 200, 350, 150, 50)
    pygame.draw.rect(screen, (200, 50, 50), delete_button)
    pygame.draw.rect(screen, (255, 255, 255), delete_button, 2)
    delete_text = button_font.render("削除", True, (255, 255, 255))
    delete_text_rect = delete_text.get_rect(center=delete_button.center)
    screen.blit(delete_text, delete_text_rect)
    
    # キャンセルボタン
    cancel_button = pygame.Rect(WINDOW_WIDTH//2 + 50, 350, 150, 50)
    pygame.draw.rect(screen, (100, 100, 100), cancel_button)
    pygame.draw.rect(screen, (255, 255, 255), cancel_button, 2)
    cancel_text = button_font.render("キャンセル", True, (255, 255, 255))
    cancel_text_rect = cancel_text.get_rect(center=cancel_button.center)
    screen.blit(cancel_text, cancel_text_rect)
    
    pygame.display.flip()
    
    # ユーザー入力を待つ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if delete_button.collidepoint(mouse_pos):
                    return True
                elif cancel_button.collidepoint(mouse_pos):
                    return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_RETURN:
                    return True

def show_confirm_overwrite_message(screen, font, data_name):
    """上書き確認メッセージを表示"""
    screen.fill((30, 60, 80))
    
    # タイトル
    title_text = font.render("上書き確認", True, (255, 255, 255))
    screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 200))
    
    # メッセージ
    message_font = get_japanese_font(24)
    message_text = message_font.render(f"学習データ '{data_name}' を上書きしますか？", True, (255, 255, 255))
    screen.blit(message_text, (WINDOW_WIDTH//2 - message_text.get_width()//2, 250))
    
    warning_text = message_font.render("既存のデータは失われます", True, (255, 200, 200))
    screen.blit(warning_text, (WINDOW_WIDTH//2 - warning_text.get_width()//2, 290))
    
    # ボタン
    button_font = get_japanese_font(20)
    
    # 上書きボタン
    overwrite_button = pygame.Rect(WINDOW_WIDTH//2 - 200, 350, 150, 50)
    pygame.draw.rect(screen, (200, 150, 50), overwrite_button)
    pygame.draw.rect(screen, (255, 255, 255), overwrite_button, 2)
    overwrite_text = button_font.render("上書き", True, (255, 255, 255))
    overwrite_text_rect = overwrite_text.get_rect(center=overwrite_button.center)
    screen.blit(overwrite_text, overwrite_text_rect)
    
    # キャンセルボタン
    cancel_button = pygame.Rect(WINDOW_WIDTH//2 + 50, 350, 150, 50)
    pygame.draw.rect(screen, (100, 100, 100), cancel_button)
    pygame.draw.rect(screen, (255, 255, 255), cancel_button, 2)
    cancel_text = button_font.render("キャンセル", True, (255, 255, 255))
    cancel_text_rect = cancel_text.get_rect(center=cancel_button.center)
    screen.blit(cancel_text, cancel_text_rect)
    
    pygame.display.flip()
    
    # ユーザー入力を待つ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if overwrite_button.collidepoint(mouse_pos):
                    return True
                elif cancel_button.collidepoint(mouse_pos):
                    return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_RETURN:
                    return True

def show_overwrite_complete_message(screen, font, data_name):
    """上書き完了メッセージを表示"""
    screen.fill((30, 60, 80))
    
    # タイトル
    title_text = font.render("上書き完了", True, (255, 255, 255))
    screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 200))
    
    # メッセージ
    message_font = get_japanese_font(24)
    message_text = message_font.render(f"学習データ '{data_name}' を上書き保存しました", True, (255, 255, 255))
    screen.blit(message_text, (WINDOW_WIDTH//2 - message_text.get_width()//2, 250))
    
    # ボタン
    button_font = get_japanese_font(20)
    ok_button = pygame.Rect(WINDOW_WIDTH//2 - 100, 350, 200, 50)
    pygame.draw.rect(screen, (50, 200, 50), ok_button)
    pygame.draw.rect(screen, (255, 255, 255), ok_button, 2)
    ok_text = button_font.render("OK", True, (255, 255, 255))
    ok_text_rect = ok_text.get_rect(center=ok_button.center)
    screen.blit(ok_text, ok_text_rect)
    
    pygame.display.flip()
    
    # ユーザー入力を待つ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if ok_button.collidepoint(mouse_pos):
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                    return

def show_no_saved_data_message(screen, font):
    """保存済みデータなしメッセージを表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render("保存済みデータなし", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render("保存済みの学習データが見つかりません", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 320))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                return

def show_load_complete_message(screen, font, data_name):
    """読み込み完了メッセージを表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render("読み込み完了", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render(f"学習データ '{data_name}' を読み込みました", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 320))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                return

def show_load_error_message(screen, font, error_message):
    """読み込みエラーメッセージを表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render("読み込みエラー", True, (255, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render(f"学習データの読み込みに失敗しました: {error_message}", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 320))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                return

def show_save_error_message(screen, font, error_message):
    """保存エラーメッセージを表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render("保存エラー", True, (255, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render(f"学習データの保存に失敗しました: {error_message}", True, (0, 0, 0))
    screen.blit(message, (WINDOW_WIDTH//2 - message.get_width()//2, 250))
    
    help_text = font.render("任意のキーで続行", True, (100, 100, 100))
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 320))
    
    pygame.display.flip()
    
    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                return

def get_japanese_font(size):
    """日本語フォントを取得 - othello-ai-learning参考版"""
    try:
        return pygame.font.Font("C:/Windows/Fonts/meiryo.ttc", size)
    except:
        try:
            return pygame.font.Font("C:/Windows/Fonts/msgothic.ttc", size)
        except:
            return pygame.font.SysFont(None, size)

def analyze_learning_progress(ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, qtable_size, game_count):
    """
    学習進捗の詳細分析と評価
    """
    total_games = ai_win_count + ai_lose_count + ai_draw_count
    win_rate = (ai_win_count / total_games) * 100 if total_games > 0 else 0
    avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
    
    print(f"\n📊 学習進捗詳細分析")
    print(f"=" * 50)
    
    # 基本統計
    print(f"🎯 基本統計:")
    print(f"  総ゲーム数: {total_games}")
    print(f"  勝利: {ai_win_count} ({win_rate:.1f}%)")
    if total_games > 0:
        print(f"  敗北: {ai_lose_count} ({(ai_lose_count/total_games*100):.1f}%)")
        print(f"  引き分け: {ai_draw_count} ({(ai_draw_count/total_games*100):.1f}%)")
    else:
        print(f"  敗北: {ai_lose_count} (0.0%)")
        print(f"  引き分け: {ai_draw_count} (0.0%)")
    print(f"  総学習回数: {ai_learn_count}")
    print(f"  平均報酬: {avg_reward:.2f}")
    print(f"  Qテーブルサイズ: {qtable_size}")
    
    # 学習効率の評価
    print(f"\n⚡ 学習効率:")
    learning_efficiency = ai_learn_count / total_games if total_games > 0 else 0
    print(f"  ゲームあたりの学習回数: {learning_efficiency:.1f}")
    
    if learning_efficiency > 50:
        print(f"  ✅ 非常に高い学習効率")
    elif learning_efficiency > 30:
        print(f"  👍 高い学習効率")
    elif learning_efficiency > 20:
        print(f"  📈 良好な学習効率")
    else:
        print(f"  ⚠️ 学習効率が低い")
    
    # 勝率の評価
    print(f"\n🏆 勝率評価:")
    if win_rate > 90:
        print(f"  🏅 卓越した強さ (勝率: {win_rate:.1f}%)")
        print(f"  💡 AIが非常に優秀な戦略を学習済み")
    elif win_rate > 80:
        print(f"  🥇 優秀な強さ (勝率: {win_rate:.1f}%)")
        print(f"  💡 AIが効果的な戦略を学習済み")
    elif win_rate > 70:
        print(f"  🥈 良好な強さ (勝率: {win_rate:.1f}%)")
        print(f"  💡 AIが基本的な戦略を学習済み")
    elif win_rate > 60:
        print(f"  🥉 平均的な強さ (勝率: {win_rate:.1f}%)")
        print(f"  💡 AIが学習を継続中")
    elif win_rate > 50:
        print(f"  📊 標準的な強さ (勝率: {win_rate:.1f}%)")
        print(f"  💡 さらなる学習が必要")
    else:
        print(f"  ⚠️ 改善が必要 (勝率: {win_rate:.1f}%)")
        print(f"  💡 学習パラメータの見直しを推奨")
    
    # 報酬の評価
    print(f"\n💰 報酬評価:")
    if avg_reward > 10:
        print(f"  🎉 非常に高い報酬 (平均: {avg_reward:.2f})")
        print(f"  💡 AIが効果的な行動を学習")
    elif avg_reward > 5:
        print(f"  👍 高い報酬 (平均: {avg_reward:.2f})")
        print(f"  💡 AIが良い行動を学習")
    elif avg_reward > 2:
        print(f"  📈 良好な報酬 (平均: {avg_reward:.2f})")
        print(f"  💡 AIが基本的な行動を学習")
    elif avg_reward > 0:
        print(f"  📊 標準的な報酬 (平均: {avg_reward:.2f})")
        print(f"  💡 学習継続が必要")
    else:
        print(f"  ⚠️ 低い報酬 (平均: {avg_reward:.2f})")
        print(f"  💡 報酬設計の見直しを推奨")
    
    # Qテーブルの成長評価
    print(f"\n🧠 Qテーブル成長:")
    if qtable_size > 5000:
        print(f"  🧠 非常に豊富な知識 (サイズ: {qtable_size})")
        print(f"  💡 AIが多くの状況を学習済み")
    elif qtable_size > 3000:
        print(f"  🧠 豊富な知識 (サイズ: {qtable_size})")
        print(f"  💡 AIが多くの状況を学習")
    elif qtable_size > 2000:
        print(f"  🧠 良好な知識 (サイズ: {qtable_size})")
        print(f"  💡 AIが基本的な状況を学習")
    elif qtable_size > 1000:
        print(f"  🧠 標準的な知識 (サイズ: {qtable_size})")
        print(f"  💡 さらなる学習が必要")
    else:
        print(f"  🧠 限定的な知識 (サイズ: {qtable_size})")
        print(f"  💡 大幅な学習が必要")
    
    # 総合評価
    print(f"\n🎯 総合評価:")
    score = 0
    if win_rate > 80: score += 3
    elif win_rate > 60: score += 2
    elif win_rate > 50: score += 1
    
    if avg_reward > 5: score += 2
    elif avg_reward > 2: score += 1
    
    if qtable_size > 3000: score += 2
    elif qtable_size > 2000: score += 1
    
    if learning_efficiency > 30: score += 1
    
    if score >= 7:
        print(f"  🌟 優秀 (スコア: {score}/8)")
        print(f"  💡 AIが非常に効果的に学習済み")
    elif score >= 5:
        print(f"  👍 良好 (スコア: {score}/8)")
        print(f"  💡 AIが効果的に学習中")
    elif score >= 3:
        print(f"  📈 改善中 (スコア: {score}/8)")
        print(f"  💡 学習継続でさらなる向上が期待")
    else:
        print(f"  ⚠️ 要改善 (スコア: {score}/8)")
        print(f"  💡 学習パラメータの見直しを推奨")
    
    # 推奨事項
    print(f"\n💡 推奨事項:")
    if win_rate < 60:
        print(f"  • 学習ゲーム数を増やす (現在: {game_count}ゲーム)")
        print(f"  • 学習率を調整する")
    if avg_reward < 2:
        print(f"  • 報酬設計を見直す")
        print(f"  • 探索率を調整する")
    if qtable_size < 2000:
        print(f"  • より多くの状況での学習を促進")
    if learning_efficiency < 20:
        print(f"  • 学習頻度を上げる")
    
    if score >= 5:
        print(f"  • 人間との対戦で実力を確認")
        print(f"  • 学習データを保存")
    
    return score

def enhanced_ai_self_play(game, qtable, num_games=100, learn=True, draw_mode=False, screen=None, font=None):
    """
    強化版AI同士の自己対戦（より効率的な学習）- othello-ai-learning参考版
    描画ON/OFF対応
    """
    ai_learn_count = 0
    ai_win_count = 0
    ai_lose_count = 0
    ai_draw_count = 0
    ai_total_reward = 0
    win_black = 0
    win_white = 0
    
    print(f"🤖 強化版AI自己対戦開始: {num_games}ゲーム")
    
    # 事前学習開始メッセージ
    if screen is not None and font is not None:
        screen.fill((30, 60, 80))
        start_text = font.render("事前学習を開始します", True, (255, 255, 255))
        screen.blit(start_text, (screen.get_width()//2 - start_text.get_width()//2, screen.get_height()//2 - 60))
        info_text = get_japanese_font(24).render(f"訓練回数: {num_games}", True, (255, 255, 255))
        screen.blit(info_text, (screen.get_width()//2 - info_text.get_width()//2, screen.get_height()//2 - 20))
        pygame.display.flip()
        pygame.time.wait(1500)
    
    for game_num in range(num_games):
        game.reset_game()
        game_reward = 0
        moves_in_game = 0
        max_moves = 200  # 最大手数制限
        
        # --- 盤面描画ON ---
        if draw_mode and screen is not None and font is not None:
            screen.fill((255,255,255))
            # 左側に進捗グラフ・統計
            draw_ai_battle_progress_graphs(
                screen, None, game_num + 1, num_games, ai_learn_count, 
                ai_win_count, ai_lose_count, ai_draw_count, 0, qtable, True
            )
            # 右側に盤面・石・進捗バー・勝敗など
            # タイトル
            title_font = get_japanese_font(32)
            title_surface = title_font.render("AI同士の訓練中", True, (0, 0, 0))
            screen.blit(title_surface, (BOARD_OFFSET_X + BOARD_PIXEL_SIZE//2 - title_surface.get_width()//2, BOARD_OFFSET_Y - 60))
            # 盤面・石
            draw_board(screen, game.board, game)
            draw_stones(screen, game.board, game)
            # 現在のプレイヤー表示
            draw_current_player_indicator(screen, game.current_player)
            # 進捗バー（盤面の下）
            # draw_progress_bar(screen, game_num + 1, num_games, BOARD_OFFSET_X, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE + 20, 200, 30)
            # 勝敗・手数
            info_font = get_japanese_font(22)
            info = [
                f"対戦 {game_num + 1} / {num_games}",
                f"黒AI: {win_black}勝　白AI: {win_white}勝　引き分け: {ai_draw_count}",
            ]
            for i, line in enumerate(info):
                surface = info_font.render(line, True, (0,0,0))
                screen.blit(surface, (BOARD_OFFSET_X + BOARD_PIXEL_SIZE//2 - surface.get_width()//2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE + 60 + i*30))
            draw_learn_count(screen, font, ai_learn_count)
            draw_game_count(screen, font, game_num + 1)
            pygame.display.flip()
            pygame.event.pump()
            pygame.time.wait(500)  # ゲーム開始を500ms表示
        # --- 盤面描画OFF ---
        elif not draw_mode and screen is not None and font is not None:
            screen.fill((30, 60, 80))
            
            # 左側にグラフエリアを表示
            draw_ai_battle_progress_graphs(
                screen, None, game_num + 1, num_games, ai_learn_count, 
                ai_win_count, ai_lose_count, ai_draw_count, 0, qtable, True
            )
            
            # 右側に進捗情報を表示
            # メインタイトル（自己対戦モード表示）
            title_text = font.render("AI自己対戦学習中", True, (255, 255, 255))
            title_x = GRAPH_OFFSET_X + GRAPH_AREA_WIDTH + 50 + (screen.get_width() - (GRAPH_OFFSET_X + GRAPH_AREA_WIDTH + 50) - title_text.get_width()) // 2
            screen.blit(title_text, (title_x, 50))
            
            # 現在の対戦番号を大きく表示
            battle_text = font.render(f"第{game_num + 1}戦 / {num_games}戦", True, (255, 255, 255))
            battle_x = GRAPH_OFFSET_X + GRAPH_AREA_WIDTH + 50 + (screen.get_width() - (GRAPH_OFFSET_X + GRAPH_AREA_WIDTH + 50) - battle_text.get_width()) // 2
            screen.blit(battle_text, (battle_x, 100))
            
            # 進捗バー
            progress = (game_num + 1) / num_games
            bar_w = 500  # バーの幅を少し小さく
            bar_h = 40
            bar_x = screen.get_width() - bar_w - 20  # 右端から20px内側
            bar_y = screen.get_height() // 2 - 60
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, int(bar_w*progress), bar_h))
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_w, bar_h), 3)
            
            # 進捗テキスト（自己対戦モード表示）
            progress_text = font.render(f"自己対戦訓練進捗: {game_num + 1}/{num_games}", True, (255, 255, 255))
            screen.blit(progress_text, (bar_x + 20, bar_y - 50))
            
            # 統計情報
            stats_font = get_japanese_font(20)
            stats_y = bar_y + 120
            
            # 勝敗統計（自己対戦特有の表示）
            win_rate = 0
            if win_black + win_white > 0:
                win_rate = (win_white / (win_black + win_white)) * 100
            
            stats_text1 = stats_font.render(f"AI（白）勝利: {win_white}回", True, (255, 255, 255))
            stats_text2 = stats_font.render(f"AI（黒）勝利: {win_black}回", True, (255, 255, 255))
            stats_text3 = stats_font.render(f"AI（白）勝率: {win_rate:.1f}%", True, (255, 255, 255))
            stats_text4 = stats_font.render("※同じAI同士の対戦", True, (200, 200, 200))
            
            screen.blit(stats_text1, (bar_x + 20, stats_y))
            screen.blit(stats_text2, (bar_x + 20, stats_y + 30))
            screen.blit(stats_text3, (bar_x + 20, stats_y + 60))
            screen.blit(stats_text4, (bar_x + 20, stats_y + 90))
            
            # 学習統計
            if ai_learn_count > 0:
                avg_reward = ai_total_reward / ai_learn_count
                avg_reward_text = stats_font.render(f"平均報酬: {avg_reward:.1f}", True, (255, 255, 255))
                qtable_text = stats_font.render(f"Qテーブルサイズ: {len(qtable)}", True, (255, 255, 255))
                screen.blit(avg_reward_text, (bar_x + 20, stats_y + 120))
                screen.blit(qtable_text, (bar_x + 20, stats_y + 150))
            
            pygame.display.flip()
            pygame.event.pump()
            pygame.time.wait(200)  # 進捗だけなので短め
        
        while not game.game_over and moves_in_game < max_moves:
            # イベント処理を追加して固まるのを防ぐ
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, 0
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, 0
            
            current_player = game.current_player
            valid_moves = game.get_valid_moves(current_player)
            
            if not valid_moves:
                # パス
                game.current_player = PLAYER_WHITE if current_player == PLAYER_BLACK else PLAYER_BLACK
                if draw_mode and screen is not None and font is not None:
                    # パス表示
                    display_message(screen, f"{'黒' if current_player == PLAYER_BLACK else '白'}AIがパスしました", False)
                    pygame.display.flip()
                    pygame.event.pump()
                    pygame.time.wait(300)
                continue
            
            # AIの手を決定（othello-ai-learningの方式を参考）
            try:
                if current_player == PLAYER_WHITE:
                    # 白（メインAI）: Q学習で学習
                    success, reward = ai_qlearning_move(game, qtable, learn=True, player=PLAYER_WHITE, ai_learn_count=ai_learn_count)
                    if success:  # 手を打った場合
                        ai_learn_count += 1
                        ai_total_reward += reward
                        game_reward += reward
                        moves_in_game += 1
                        # デバッグ出力
                        if DEBUG_MODE:
                            print(f"白の手: 報酬={reward}, 累積報酬={ai_total_reward}, 学習回数={ai_learn_count}")
                    game.switch_player()
                else:
                    # 黒（同じAI）: 同じQテーブルを使用して学習
                    # より戦略的な行動を取るため、ε値を調整
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
                    
                    # 黒も実際に手を打って学習する（自己対戦のため）
                    success, reward = ai_qlearning_move(game, qtable, learn=True, player=PLAYER_BLACK, ai_learn_count=ai_learn_count)
                    if success:  # 手を打った場合
                        ai_learn_count += 1
                        ai_total_reward += reward
                        game_reward += reward
                        moves_in_game += 1
                        # デバッグ出力
                        if DEBUG_MODE:
                            print(f"黒の手: 報酬={reward}, 累積報酬={ai_total_reward}, 学習回数={ai_learn_count}")
                    game.switch_player()
                
                game.check_game_over()
                
                # 描画ONの場合のみ盤面・進捗を描画（更新頻度を調整）
                if draw_mode and screen is not None and font is not None:
                    # 手数が少ない時は頻繁に更新、多い時は間引く
                    update_frequency = max(1, moves_in_game // 10)  # 10手ごとに更新頻度を調整
                    if moves_in_game <= 20 or moves_in_game % update_frequency == 0:
                        screen.fill((255,255,255))
                        # 盤面描画
                        draw_board(screen, game.board, game)
                        draw_stones(screen, game.board, game)
                        # 現在のプレイヤー表示
                        draw_current_player_indicator(screen, game.current_player)
                        display_message(screen, f"手数: {moves_in_game} ({'黒' if current_player == PLAYER_BLACK else '白'}AIの手)", False)
                        black_score, white_score = game.get_score()
                        display_score(screen, black_score, white_score)
                        # 進捗バー描画
                        # draw_progress_bar(screen, game_num + 1, num_games, BOARD_OFFSET_X, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE + 20, 200, 30)
                        draw_learn_count(screen, font, ai_learn_count)
                        draw_game_count(screen, font, game_num + 1)
                        # AI対戦進捗グラフを描画（リアルタイム更新）
                        ai_avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
                        progress_btn_rect = draw_ai_battle_progress_graphs(
                            screen, None, game_num + 1, num_games, ai_learn_count, 
                            ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, True
                        )
                        pygame.display.flip()
                        pygame.event.pump()
                        
                        # 待機時間を手数に応じて調整
                        if moves_in_game <= 10:
                            pygame.time.wait(200)  # 序盤はゆっくり
                        elif moves_in_game <= 30:
                            pygame.time.wait(100)  # 中盤は普通
                        else:
                            pygame.time.wait(50)   # 終盤は速く
                
                # 学習進捗の表示
                if game_num % 10 == 0 and moves_in_game % 10 == 0:
                    print(f"  ゲーム {game_num+1}/{num_games}, 手数: {moves_in_game}, 累積学習: {ai_learn_count}")
                    
            except Exception as e:
                print(f"ゲーム実行中にエラーが発生しました: {e}")
                break
        
        # ゲーム終了時の画面表示
        if draw_mode and screen is not None and font is not None:
            screen.fill((255,255,255))
            # 盤面描画
            draw_board(screen, game.board, game)
            draw_stones(screen, game.board, game)
            # 現在のプレイヤー表示
            draw_current_player_indicator(screen, game.current_player)
            black_score, white_score = game.get_score()
            display_score(screen, black_score, white_score)
            
            # ゲーム結果表示
            if black_score > white_score:
                result_msg = f"ゲーム {game_num + 1} 終了: 黒AI勝利 ({black_score}-{white_score})"
            elif white_score > black_score:
                result_msg = f"ゲーム {game_num + 1} 終了: 白AI勝利 ({black_score}-{white_score})"
            else:
                result_msg = f"ゲーム {game_num + 1} 終了: 引き分け ({black_score}-{white_score})"
            
            display_message(screen, result_msg, False)
            # 進捗バー描画
            # draw_progress_bar(screen, game_num + 1, num_games, BOARD_OFFSET_X, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE + 20, 200, 30)
            draw_learn_count(screen, font, ai_learn_count)
            draw_game_count(screen, font, game_num + 1)
            # AI対戦進捗グラフを描画（最終更新）
            ai_avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
            progress_btn_rect = draw_ai_battle_progress_graphs(
                screen, None, game_num + 1, num_games, ai_learn_count, 
                ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, True
            )
            # リセットボタンと戻るボタンを描画
            from ui_components import draw_reset_button, draw_back_button
            mouse_pos = pygame.mouse.get_pos()
            mouse_down = False
            draw_reset_button(screen, font, mouse_pos, mouse_down)
            draw_back_button(screen, font, mouse_pos, mouse_down)
            pygame.display.flip()
            pygame.event.pump()
            pygame.time.wait(800)  # ゲーム結果を800ms表示
        
        # ゲーム結果の処理（othello-ai-learningの方式を参考）
        black_score, white_score = game.get_score()
        if black_score > white_score:
            win_black += 1
            ai_lose_count += 1
        elif white_score > black_score:
            win_white += 1
            ai_win_count += 1
        else:
            win_black += 1
            ai_draw_count += 1
        
        if game_num % 10 == 0 or game_num < 5:
            print(f"  ゲーム{game_num+1}: 黒{black_score} - 白{white_score}, 勝者: {'黒' if black_score > white_score else '白' if white_score > black_score else '引き分け'}")
        
        ai_total_reward += game_reward
        
        # 自己対戦特有の統計情報（othello-ai-learningの方式を参考）
        if game_num % 10 == 0:  # 10戦ごとに詳細統計
            print(f"\n=== 自己対戦学習進捗（第{game_num + 1}戦） ===")
            print(f"総対戦数: {game_num + 1}")
            print(f"AI（白）勝利: {win_white}回")
            print(f"AI（黒）勝利: {win_black}回")
            print(f"勝率: {(win_white / (win_black + win_white)) * 100:.1f}%")
            print(f"Qテーブルサイズ: {len(qtable)}")
            print(f"平均報酬: {(ai_total_reward / ai_learn_count) if ai_learn_count > 0 else 0:.2f}")
            print("=" * 40)
        
        # 学習統計更新（othello-ai-learningの方式を参考）
        if ai_learn_count > 0:
            ai_avg_reward = ai_total_reward / ai_learn_count
        else:
            ai_avg_reward = 0
    
    total_games = ai_win_count + ai_lose_count + ai_draw_count
    final_win_rate = (ai_win_count / total_games) * 100 if total_games > 0 else 0
    final_avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
    
    print(f"🎯 自己対戦完了!")
    print(f"  総ゲーム数: {total_games}")
    print(f"  AI勝利: {ai_win_count}, AI敗北: {ai_lose_count}, 引き分け: {ai_draw_count}")
    print(f"  最終勝率: {final_win_rate:.1f}%")
    print(f"  総学習回数: {ai_learn_count}")
    print(f"  平均報酬: {final_avg_reward:.2f}")
    print(f"  Qテーブルサイズ: {len(qtable)}")
    
    analyze_learning_progress(ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, len(qtable), num_games)
    
    return ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, final_avg_reward

def enhanced_ai_move_with_strategy_safe(game, qtable, learn=True, player=None, ai_learn_count=0, alpha=None, epsilon=None):
    """
    戦略に基づいた強化AI手番（安全版）
    """
    try:
        if alpha is None:
            # Qテーブルサイズに応じて学習パラメータを調整
            if len(qtable) > 50000:  # 50,000エントリを超えたらメモリ効率モード
                alpha = 0.3  # 学習率を下げて新しい状態の追加を抑制
            else:
                alpha = ALPHA
        if epsilon is None:
            # Qテーブルサイズに応じて探索率を調整
            if len(qtable) > 50000:  # 50,000エントリを超えたらメモリ効率モード
                epsilon = 0.4  # 探索率を上げて既存の状態を活用
            else:
                epsilon = EPSILON
        
        # 現在の状態を取得
        state = get_board_state_safe(game.board)
        valid_moves = game.get_valid_moves(player)
        
        if not valid_moves:
            return False, 0
        
        # 戦略的アクション選択
        action = select_strategic_action_safe(state, valid_moves, qtable, epsilon, ai_learn_count)
        
        # 手を実行
        old_board = [row[:] for row in game.board]
        success = game.make_move(action[0], action[1], player)
        
        if not success:
            return False, REWARD_INVALID_MOVE
        
        # 報酬計算（強化版）
        reward = calculate_enhanced_reward_safe(game, old_board, action, player)
        
        # Q学習更新（エラーハンドリング付き）
        if learn:
            try:
                next_state = get_board_state_safe(game.board)
                next_valid_moves = game.get_valid_moves(player)
                
                # 次の状態での最大Q値を計算
                max_next_q = 0
                if next_valid_moves:
                    next_q_values = []
                    for move in next_valid_moves:
                        next_action = (move[0], move[1])
                        next_q_values.append(qtable.get((next_state, next_action), 0))
                    max_next_q = max(next_q_values) if next_q_values else 0
                
                # Q値の更新
                current_q = qtable.get((state, action), 0)
                new_q = current_q + alpha * (reward + GAMMA * max_next_q - current_q)
                qtable[(state, action)] = new_q
            except Exception as q_error:
                print(f"    ⚠️ Q学習更新エラー: {q_error}")
        
        return True, reward
    
    except Exception as e:
        print(f"    ⚠️ AI手番エラー: {e}")
        return False, 0

def get_board_state_safe(board):
    """
    盤面の状態を文字列として取得（最適化版）
    """
    try:
        # より効率的な状態表現
        state_parts = []
        for i in range(BOARD_SIZE):
            row_state = ""
            for j in range(BOARD_SIZE):
                if board[i][j] == PLAYER_BLACK:
                    row_state += "B"
                elif board[i][j] == PLAYER_WHITE:
                    row_state += "W"
                else:
                    row_state += "E"
            state_parts.append(row_state)
        
        # 状態の正規化（回転・反転を考慮）
        normalized_state = normalize_board_state(state_parts)
        return normalized_state
        
    except Exception as e:
        print(f"    ⚠️ 盤面状態取得エラー: {e}")
        return "E" * (BOARD_SIZE * BOARD_SIZE)  # デフォルト状態を返す

def normalize_board_state(state_parts):
    """
    盤面状態を正規化して重複を減らす
    """
    try:
        # 基本的な状態文字列を作成
        base_state = "".join(state_parts)
        
        # 状態の簡略化（角とエッジの情報を優先）
        simplified_state = ""
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if (i == 0 or i == BOARD_SIZE-1) and (j == 0 or j == BOARD_SIZE-1):
                    # 角の位置
                    simplified_state += base_state[i * BOARD_SIZE + j]
                elif i == 0 or i == BOARD_SIZE-1 or j == 0 or j == BOARD_SIZE-1:
                    # エッジの位置
                    simplified_state += base_state[i * BOARD_SIZE + j]
                else:
                    # 内側の位置（簡略化）
                    cell = base_state[i * BOARD_SIZE + j]
                    if cell != "E":
                        simplified_state += cell
                    else:
                        simplified_state += "E"
        
        return simplified_state
        
    except Exception as e:
        print(f"    ⚠️ 状態正規化エラー: {e}")
        return "E" * (BOARD_SIZE * BOARD_SIZE)

def select_strategic_action_safe(state, valid_moves, qtable, epsilon, ai_learn_count):
    """
    戦略的なアクション選択（安全版）
    """
    try:
        # ε-greedy法でアクション選択
        if random.random() < epsilon:
            return random.choice(valid_moves)
        
        # Q値に基づく選択
        best_q = float('-inf')
        best_moves = []
        
        for move in valid_moves:
            action = (move[0], move[1])
            q_value = qtable.get((state, action), 0)
            
            if q_value > best_q:
                best_q = q_value
                best_moves = [move]
            elif q_value == best_q:
                best_moves.append(move)
        
        # 複数の最適手がある場合は戦略的に選択
        if len(best_moves) > 1:
            return select_best_strategic_move_safe(best_moves)
        
        return best_moves[0] if best_moves else random.choice(valid_moves)
    
    except Exception as e:
        print(f"    ⚠️ アクション選択エラー: {e}")
        return random.choice(valid_moves) if valid_moves else None

def select_best_strategic_move_safe(moves):
    """
    複数の最適手から戦略的に選択（安全版）
    """
    try:
        # 角を優先
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        for move in moves:
            if move in corners:
                return move
        
        # エッジを避ける
        edges = [(0, 1), (0, 6), (1, 0), (1, 7), (6, 0), (6, 7), (7, 1), (7, 6)]
        non_edge_moves = [move for move in moves if move not in edges]
        
        if non_edge_moves:
            return random.choice(non_edge_moves)
        
        return random.choice(moves)
    
    except Exception as e:
        print(f"    ⚠️ 戦略的選択エラー: {e}")
        return random.choice(moves) if moves else None

def calculate_enhanced_reward_safe(game, old_board, action, player):
    """
    強化された報酬計算（安全版）
    """
    try:
        reward = 0
        
        # 基本的な石の裏返し報酬
        flipped_count = count_flipped_stones_safe(old_board, game.board, player)
        reward += flipped_count * REWARD_FLIP_PER_STONE
        
        # 戦略的報酬
        reward += calculate_strategic_rewards_safe(game, action, player)
        
        # ゲーム終了時の報酬
        if game.game_over:
            black_score, white_score = game.get_score()
            if player == PLAYER_BLACK:
                if black_score > white_score:
                    reward += REWARD_WIN
                elif white_score > black_score:
                    reward += REWARD_LOSE
                else:
                    reward += REWARD_DRAW
            else:  # PLAYER_WHITE
                if white_score > black_score:
                    reward += REWARD_WIN
                elif black_score > white_score:
                    reward += REWARD_LOSE
                else:
                    reward += REWARD_DRAW
        
        return reward
    
    except Exception as e:
        print(f"    ⚠️ 報酬計算エラー: {e}")
        return 0

def count_flipped_stones_safe(old_board, new_board, player):
    """
    裏返された石の数をカウント（安全版）
    """
    try:
        count = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if old_board[i][j] != new_board[i][j] and new_board[i][j] == player:
                    count += 1
        return count
    except Exception as e:
        print(f"    ⚠️ 石カウントエラー: {e}")
        return 0

def calculate_strategic_rewards_safe(game, action, player):
    """
    戦略的報酬を計算（安全版）
    """
    try:
        reward = 0
        row, col = action
        
        # 角の報酬
        if (row, col) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
            reward += REWARD_CORNER
        
        # エッジのペナルティ
        if (row, col) in [(0, 1), (0, 6), (1, 0), (1, 7), (6, 0), (6, 7), (7, 1), (7, 6)]:
            reward += REWARD_EDGE
        
        # 安定石の報酬（角に隣接する石）
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        for corner in corners:
            if abs(row - corner[0]) <= 1 and abs(col - corner[1]) <= 1:
                if game.board[corner[0]][corner[1]] == player:
                    reward += REWARD_STABLE_STONE
        
        # 合法手の数による報酬
        valid_moves = game.get_valid_moves(player)
        reward += len(valid_moves) * REWARD_MOBILITY
        
        # 位置による報酬
        center_distance = abs(row - 3.5) + abs(col - 3.5)
        reward += (7 - center_distance) * REWARD_POSITIONAL
        
        # パス強制の報酬
        opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
        opponent_moves = game.get_valid_moves(opponent)
        if len(opponent_moves) == 0 and len(valid_moves) > 0:
            reward += REWARD_PASS_FORCE
        
        return reward
    
    except Exception as e:
        print(f"    ⚠️ 戦略報酬計算エラー: {e}")
        return 0

# メモリ効率の良い学習パラメータ
MEMORY_EFFICIENT_ALPHA = 0.3  # 学習率を下げて新しい状態の追加を抑制
MEMORY_EFFICIENT_EPSILON = 0.4  # 探索率を上げて既存の状態を活用