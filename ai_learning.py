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
    try:
        with open(QTABLE_PATH, "wb") as f:
            pickle.dump(qtable, f)
    except Exception as e:
        print(f"Qテーブルの保存エラー: {e}")

def load_qtable():
    try:
        if os.path.exists(QTABLE_PATH):
            with open(QTABLE_PATH, "rb") as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Qテーブルの読み込みエラー: {e}")
    return {}

# AIの手番実行（Q学習）
def ai_qlearning_move(game, qtable, learn=True, player=None):
    if player is None:
        player = game.current_player
    state_key = game.get_board_state_key()
    valid_moves = game.get_valid_moves(player)
    if not valid_moves:
        return False
    # ε-greedy法
    if random.random() < EPSILON:
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
    game.make_move(r, c, player)
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
    return True 

# 学習データ管理機能
def save_learning_data(qtable, learning_history, screen, font):
    """学習データを保存"""
    # 保存名入力画面を表示
    save_name = show_save_name_input(screen, font)
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
        show_save_complete_message(screen, font, save_name)
        
        print(f"学習データ '{save_name}' を保存しました")
    except Exception as e:
        print(f"保存エラー: {e}")
        show_save_error_message(screen, font)

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

def load_learning_data(qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, screen, font):
    """学習データを読み込み"""
    # 保存済みデータの一覧を取得
    saved_data = get_saved_data_list()
    if not saved_data:
        show_no_saved_data_message(screen, font)
        return
    
    # データ選択画面を表示
    selected_data = show_data_selection_screen(screen, font, saved_data)
    if not selected_data:
        return  # キャンセルされた場合
    
    try:
        # 選択されたデータを読み込み
        qtable_filename = f"qtable_{selected_data}.pkl"
        history_filename = f"learning_history_{selected_data}.json"
        
        # Qテーブルを読み込み
        qtable.clear()
        qtable.update(load_qtable_from_file(qtable_filename))
        
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
        
        show_load_complete_message(screen, font, selected_data)
        print(f"学習データ '{selected_data}' を読み込みました")
    except Exception as e:
        print(f"読み込みエラー: {e}")
        show_load_error_message(screen, font)

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
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render("削除確認", True, (0, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
    
    message1 = font.render(f"学習データ '{data_name}' を削除しますか？", True, (0, 0, 0))
    screen.blit(message1, (WINDOW_WIDTH//2 - message1.get_width()//2, 200))
    
    message2 = font.render("この操作は取り消せません", True, (255, 0, 0))
    screen.blit(message2, (WINDOW_WIDTH//2 - message2.get_width()//2, 230))
    
    # ボタン
    delete_button = pygame.Rect(WINDOW_WIDTH//2 - 150, 280, 120, 40)
    pygame.draw.rect(screen, (255, 100, 100), delete_button)
    pygame.draw.rect(screen, (200, 50, 50), delete_button, 2)
    delete_text = font.render("削除", True, (0, 0, 0))
    delete_text_rect = delete_text.get_rect(center=delete_button.center)
    screen.blit(delete_text, delete_text_rect)
    
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
                if delete_button.collidepoint(mouse_pos):
                    return True
                elif cancel_button.collidepoint(mouse_pos):
                    return False
    
    return False

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

def show_load_error_message(screen, font):
    """読み込みエラーメッセージを表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render("読み込みエラー", True, (255, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render("学習データの読み込みに失敗しました", True, (0, 0, 0))
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

def show_save_error_message(screen, font):
    """保存エラーメッセージを表示"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WHITE = (255, 255, 255)
    
    screen.fill(WHITE)
    title = font.render("保存エラー", True, (255, 0, 0))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
    
    message = font.render("学習データの保存に失敗しました", True, (0, 0, 0))
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
    """日本語フォントを取得"""
    try:
        return pygame.font.Font("C:/Windows/Fonts/meiryo.ttc", size)
    except:
        try:
            return pygame.font.Font("C:/Windows/Fonts/msgothic.ttc", size)
        except:
            return pygame.font.SysFont(None, size) 