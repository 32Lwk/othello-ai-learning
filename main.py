import pygame
import sys
import random
import time
import pickle
import os
import json
from typing import Optional
from datetime import datetime
from collections import deque
import math

# 定数とフォントをインポート
from constants import *

# 他のモジュールをインポート
from game_logic import OthelloGame
from ai_learning import (
    LearningHistory, LearningLogger, save_qtable, load_qtable,
    save_learning_data, create_new_learning_data, load_learning_data, 
    confirm_delete_learning_data
)
from ui_components import (
    draw_board, draw_stones, draw_current_player_indicator, 
    display_error_message, display_game_result, display_notice_message,
    display_message, display_score, display_ai_reward, draw_progress_bar,
    draw_learn_count, draw_pretrain_count, draw_game_count, draw_move_count,
    draw_learning_graphs, draw_reset_button, draw_back_button,
    draw_enhanced_button, draw_gradient_background, draw_decorative_elements,
    draw_quick_stats, draw_learning_data_screen, draw_battle_history_list,
    draw_ai_stats
)
from settings import settings_screen

# グローバル変数
ai_learn_count = 0
game_count = 0
move_count = 0
last_move_count = 0
win_black = 0
win_white = 0

# 学習統計用の変数
ai_total_reward = 0
ai_avg_reward = 0
ai_win_count = 0
ai_lose_count = 0
ai_draw_count = 0

# モード管理変数
current_mode = None
data_view_mode = False  # 学習データ表示モード
battle_history_mode = False  # 対戦記録表示モード
show_left_graphs = True  # 左側のグラフ表示制御
show_learning_progress = True  # 左側の学習進捗表示制御

# AI設定変数
ai_speed = 60
pretrain_total = 10
fast_mode = True
draw_mode = True
DEBUG_MODE = False

# 訓練関連変数
pretrain_in_progress = False
pretrain_now = 0

# 学習履歴管理オブジェクト
learning_history = LearningHistory(max_history=50)
learning_logger = LearningLogger()

# Qテーブル
qtable = load_qtable()

# ゲームオブジェクト
game = OthelloGame()

# フォント
font = get_japanese_font(36)
small_font = get_japanese_font(24)
tiny_font = get_japanese_font(20)

def main_loop():
    global current_mode, game, qtable, ai_learn_count, game_count, move_count, last_move_count
    global win_black, win_white, ai_total_reward, ai_avg_reward, ai_win_count, ai_lose_count, ai_draw_count
    global pretrain_in_progress, pretrain_now, learning_history, learning_logger
    global ai_speed, pretrain_total, fast_mode, draw_mode, DEBUG_MODE
    global show_new_game_message, new_game_message_start_time
    global data_view_mode, battle_history_mode, show_left_graphs, show_learning_progress

    # モード選択画面を必ず表示
    mode_select_screen(screen, font)

    if current_mode == MODE_AI_PRETRAIN:
        current_mode = run_pretrain_mode(screen, font)
        # 事前学習完了後、人間vsAIモードに移行
        if current_mode == MODE_HUMAN_TRAIN:
            game = OthelloGame()
            initialize_game_screen(game)
    else:
        game = OthelloGame()
        initialize_game_screen(game)

    running = True
    clock = pygame.time.Clock()
    
    # アニメーション用変数
    animation_time = 0
    progress_btn_rect = None
    
    while running:
        current_time = pygame.time.get_ticks()
        animation_time = (current_time % 3000) / 3000  # 3秒周期のアニメーション
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    show_learning_progress = not show_learning_progress

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                
                # 学習進捗表示ON/OFFボタンのクリック判定
                if progress_btn_rect and progress_btn_rect.collidepoint(mouse_pos):
                    show_learning_progress = not show_learning_progress
                    continue
                
                # 学習データ表示モードの場合
                if data_view_mode:
                    show_left_graphs = False  # 左側のグラフを非表示
                    # ボタンの位置を先に取得
                    save_button, new_button, load_button, delete_button, back_button, progress_btn_rect = draw_learning_data_screen(
                        screen, font, learning_history, qtable, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, False)
                    # 進捗ON/OFFボタンのクリック判定
                    if progress_btn_rect and progress_btn_rect.collidepoint(mouse_pos):
                        show_learning_progress = not show_learning_progress
                        pygame.display.flip()
                        pygame.time.Clock().tick(30)
                        continue
                    # ボタンのクリック判定
                    if mouse_down:
                        if save_button.collidepoint(mouse_pos):
                            save_learning_data(qtable, learning_history, screen, font)
                        elif new_button.collidepoint(mouse_pos):
                            create_new_learning_data(qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, screen, font)
                        elif load_button.collidepoint(mouse_pos):
                            load_learning_data(qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, screen, font)
                        elif delete_button.collidepoint(mouse_pos):
                            confirm_delete_learning_data(screen, font)
                        elif back_button.collidepoint(mouse_pos):
                            data_view_mode = False
                            show_left_graphs = True  # 左側のグラフを再表示
                    pygame.display.flip()
                    pygame.time.Clock().tick(30)
                    continue
                
                # 対戦記録表示モードの場合
                if battle_history_mode:
                    show_left_graphs = False  # 左側のグラフを非表示
                    draw_battle_history_screen(screen, font)
                    # 戻るボタンのクリック判定
                    if mouse_down:
                        back_button_rect = pygame.Rect(WINDOW_WIDTH//2-100, WINDOW_HEIGHT-80, 200, 50)
                        if back_button_rect.collidepoint(mouse_pos):
                            battle_history_mode = False
                            show_left_graphs = True  # 左側のグラフを再表示
                    pygame.display.flip()
                    pygame.time.Clock().tick(30)
                    continue
                
                # 通常のゲームモードの場合
                # 盤面クリック時のみ人間の手番なら石を置く
                if game.current_player == PLAYER_BLACK and not show_new_game_message and not game.game_over:
                    handle_mouse_click(event.pos)
                # リセット・戻るボタン等の処理は従来通り
                if show_new_game_message:
                    show_new_game_message = False
                    screen.fill(WHITE)
                    draw_board(screen, game.board, game)
                    draw_stones(screen, game.board, game)
                    draw_current_player_indicator(screen, game.current_player)
                    display_message(screen, game.message, game.last_move_error)
                    black_score, white_score = game.get_score()
                    display_score(screen, black_score, white_score)
                    display_ai_reward(screen, game.ai_last_reward)
                    draw_learn_count(screen, font, ai_learn_count)
                    draw_pretrain_count(screen, font, pretrain_now, pretrain_total)
                    draw_game_count(screen, font, game_count)
                    last_move_count = draw_move_count(screen, font, move_count, last_move_count)
                    draw_reset_button(screen, font, (0, 0), False)
                    draw_back_button(screen, font, (0, 0), False)
                    if show_left_graphs:
                        progress_btn_rect = draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress)
                
                if draw_reset_button(screen, font, mouse_pos, True):
                    reset_game()
                
                if draw_back_button(screen, font, mouse_pos, True):
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
                    mode_select_screen(screen, font)
                    if current_mode == MODE_AI_PRETRAIN:
                        current_mode = run_pretrain_mode(screen, font)
                        if current_mode == MODE_HUMAN_TRAIN:
                            game = OthelloGame()
                            initialize_game_screen(game)
                    else:
                        game = OthelloGame()
                        initialize_game_screen(game)
            
            if event.type == pygame.KEYDOWN and show_new_game_message:
                show_new_game_message = False
                screen.fill(WHITE)
                draw_board(screen, game.board, game)
                draw_stones(screen, game.board, game)
                draw_current_player_indicator(screen, game.current_player)
                display_message(screen, game.message, game.last_move_error)
                black_score, white_score = game.get_score()
                display_score(screen, black_score, white_score)
                display_ai_reward(screen, game.ai_last_reward)
                draw_learn_count(screen, font, ai_learn_count)
                draw_pretrain_count(screen, font, pretrain_now, pretrain_total)
                draw_game_count(screen, font, game_count)
                last_move_count = draw_move_count(screen, font, move_count, last_move_count)
                draw_reset_button(screen, font, (0, 0), False)
                draw_back_button(screen, font, (0, 0), False)
                if show_left_graphs:
                    progress_btn_rect = draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress)
                pygame.display.flip()
        
        # AIの手番は自動で進める
        if game.current_player == PLAYER_WHITE and not show_new_game_message and not game.game_over:
            if game.get_valid_moves(PLAYER_WHITE):
                game.ai_qlearning_move(qtable, learn=True, player=PLAYER_WHITE)
                move_count += 1
                game.switch_player()
                game.check_game_over()

        update_learning_stats()
        
        if not show_new_game_message:
            screen.fill(WHITE)
            draw_board(screen, game.board, game)
            draw_stones(screen, game.board, game)
            draw_current_player_indicator(screen, game.current_player)
            display_message(screen, game.message, game.last_move_error)
            black_score, white_score = game.get_score()
            display_score(screen, black_score, white_score)
            display_ai_reward(screen, game.ai_last_reward)
            draw_learn_count(screen, font, ai_learn_count)
            draw_pretrain_count(screen, font, pretrain_now, pretrain_total)
            draw_game_count(screen, font, game_count)
            last_move_count = draw_move_count(screen, font, move_count, last_move_count)
            draw_ai_stats(screen, font, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward)
            draw_reset_button(screen, font, (0, 0), False)
            draw_back_button(screen, font, (0, 0), False)
            if show_left_graphs:
                progress_btn_rect = draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress)
        
        # 統計情報を描画（学習データ・対戦記録表示モード以外の場合のみ）
        if not data_view_mode and not battle_history_mode:
            draw_quick_stats(screen, animation_time, ai_learn_count, game_count)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

def mode_select_screen(screen, font):
    """モード選択画面"""
    global current_mode, pretrain_total, DEBUG_MODE, ai_speed, draw_mode, data_view_mode, battle_history_mode
    selecting = True
    input_mode = False
    speed_input_mode = False
    input_text = "10"
    speed_input_text = str(ai_speed)
    
    # アニメーション用変数
    animation_time = 0
    
    while selecting:
        current_time = pygame.time.get_ticks()
        animation_time = (current_time % 3000) / 3000  # 3秒周期のアニメーション
        
        # 背景を描画
        draw_gradient_background(screen, animation_time)
        
        # 装飾要素を描画
        draw_decorative_elements(screen, animation_time)
        
        # タイトル
        title_font = get_japanese_font(48)
        title_surface = title_font.render("AIオセロ対戦", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 80))
        
        # タイトルに影を追加
        title_shadow = title_font.render("AIオセロ対戦", True, (0, 0, 0))
        screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title_surface, title_rect)
        
        # マウス位置とクリック状態を取得
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
                elif event.key == pygame.K_TAB:
                    pass  # Tabキー機能を無効化
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
            # ボタンの位置を先に取得
            save_button, new_button, load_button, delete_button, back_button, progress_btn_rect = draw_learning_data_screen(
                screen, font, learning_history, qtable, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, False)
            # ボタンのクリック判定
            if mouse_down:
                if save_button.collidepoint(mouse_pos):
                    save_learning_data(qtable, learning_history, screen, font)
                elif new_button.collidepoint(mouse_pos):
                    create_new_learning_data(qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, screen, font)
                elif load_button.collidepoint(mouse_pos):
                    load_learning_data(qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, screen, font)
                elif delete_button.collidepoint(mouse_pos):
                    confirm_delete_learning_data(screen, font)
                elif back_button.collidepoint(mouse_pos):
                    data_view_mode = False
            pygame.display.flip()
            pygame.time.Clock().tick(30)
            continue
        
        # 対戦記録表示モードの場合
        if battle_history_mode:
            draw_battle_history_screen(screen, font)
            # 戻るボタンのクリック判定
            if mouse_down:
                back_button_rect = pygame.Rect(WINDOW_WIDTH//2-100, WINDOW_HEIGHT-80, 200, 50)
                if back_button_rect.collidepoint(mouse_pos):
                    battle_history_mode = False
            pygame.display.flip()
            pygame.time.Clock().tick(30)
            continue
        
        # ボタンを描画
        button_y_start = 180
        button_spacing = 85
        
        # 対戦モードボタン
        if draw_enhanced_button(screen, WINDOW_WIDTH//2-150, button_y_start, 300, 65, 
                              "対戦モード", "⚔", "人間プレイヤーとしてAIと直接対戦し、AIを学習させます", 
                              (100, 150, 255, 180), (150, 200, 255, 180), mouse_pos, mouse_down, font, animation_time):
            current_mode = MODE_HUMAN_TRAIN
            selecting = False
        
        # 事前訓練モードボタン
        if draw_enhanced_button(screen, WINDOW_WIDTH//2-150, button_y_start + button_spacing, 300, 65, 
                              "事前訓練", "🎯", "AI同士で事前訓練を行い、その後人間と対戦します", 
                              (255, 150, 100, 180), (255, 180, 130, 180), mouse_pos, mouse_down, font, animation_time):
            current_mode = MODE_AI_PRETRAIN
            selecting = False
        
        # 学習データ確認ボタン
        if draw_enhanced_button(screen, WINDOW_WIDTH//2-150, button_y_start + button_spacing * 2, 300, 65, 
                              "学習データ", "📊", "AIの学習進捗と統計データを詳細に確認できます", 
                              (100, 255, 150, 180), (130, 255, 180, 180), mouse_pos, mouse_down, font, animation_time):
            data_view_mode = True
        
        # 対戦記録ボタン
        if draw_enhanced_button(screen, WINDOW_WIDTH//2-150, button_y_start + button_spacing * 3, 300, 65, 
                              "対戦記録", "📋", "過去の対戦結果と詳細な記録を確認できます", 
                              (255, 100, 150, 180), (255, 130, 180, 180), mouse_pos, mouse_down, font, animation_time):
            battle_history_mode = True
        
        # 統計情報を描画
        draw_quick_stats(screen, animation_time, ai_learn_count, game_count)
        
        # 設定ボタンを追加
        settings_button_y = button_y_start + button_spacing * 4
        if draw_enhanced_button(screen, WINDOW_WIDTH//2-150, settings_button_y, 300, 65, 
                              "設定", "⚙", "AIや学習の各種設定を変更できます", 
                              (180, 180, 180, 180), (220, 220, 220, 180), mouse_pos, mouse_down, font, animation_time):
            DEBUG_MODE, ai_speed, draw_mode, pretrain_total = settings_screen(screen, font, DEBUG_MODE, ai_speed, draw_mode, pretrain_total)
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def initialize_game_screen(game_obj):
    global game, game_count, move_count, last_move_count
    game = game_obj
    move_count = 0
    last_move_count = 0
    screen.fill(WHITE)
    draw_board(screen, game.board, game)
    draw_stones(screen, game.board, game)
    draw_current_player_indicator(screen, game.current_player)
    display_message(screen, game.message, game.last_move_error)
    black_score, white_score = game.get_score()
    display_score(screen, black_score, white_score)
    display_ai_reward(screen, game.ai_last_reward)
    draw_learn_count(screen, font, ai_learn_count)
    draw_pretrain_count(screen, font, pretrain_now, pretrain_total)
    draw_game_count(screen, font, game_count)
    last_move_count = draw_move_count(screen, font, move_count, last_move_count)
    draw_reset_button(screen, font, (0, 0), False)
    draw_back_button(screen, font, (0, 0), False)
    if show_left_graphs:
        progress_btn_rect = draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress)
    pygame.display.flip()
    return progress_btn_rect if show_left_graphs else None

def handle_mouse_click(pos):
    global game, move_count, last_move_count, ai_learn_count, ai_total_reward, ai_avg_reward
    global ai_win_count, ai_lose_count, ai_draw_count, show_new_game_message
    if current_mode != MODE_HUMAN_TRAIN or game.game_over:
        return
    x, y = pos
    # 盤面内か判定
    board_x = x - BOARD_OFFSET_X
    board_y = y - BOARD_OFFSET_Y
    if 0 <= board_x < BOARD_PIXEL_SIZE and 0 <= board_y < BOARD_PIXEL_SIZE:
        row = board_y // SQUARE_SIZE
        col = board_x // SQUARE_SIZE
        if game.current_player == PLAYER_BLACK:
            if game.is_valid_move(row, col, PLAYER_BLACK):
                game.make_move(row, col, PLAYER_BLACK)
                move_count += 1
                game.switch_player()
                game.check_game_over()
                
                # ゲーム終了時の処理
                if game.game_over and not show_new_game_message:
                    black_score, white_score = game.get_score()
                    
                    # 勝者判定
                    if black_score > white_score:
                        result_message = "黒の勝利！"
                        ai_lose_count += 1  # AIは白なので、黒の勝利はAIの敗北
                    elif white_score > black_score:
                        result_message = "白の勝利！"
                        ai_win_count += 1   # AIは白なので、白の勝利はAIの勝利
                    else:
                        result_message = "引き分け"
                        ai_draw_count += 1
                    
                    # 詳細な結果表示
                    display_game_result(screen, result_message, game.ai_last_reward, black_score, white_score, ai_learn_count)
                    show_new_game_message = True
                    new_game_message_start_time = pygame.time.get_ticks()
                    
                    # 学習履歴に記録
                    learning_history.add_record(
                        game_count, ai_learn_count, ai_win_count, ai_lose_count, 
                        ai_draw_count, ai_total_reward, ai_avg_reward, len(qtable), black_score, white_score
                    )
                    
                    # 学習データを保存
                    save_learning_data(qtable, learning_history, screen, font)
                    
                    pygame.display.flip()
                
                # AIの手番
                if game.current_player == PLAYER_WHITE:
                    game.ai_qlearning_move(qtable, learn=True, player=PLAYER_WHITE)
                    game.switch_player()

def reset_game():
    global game, move_count, last_move_count, show_new_game_message
    game = OthelloGame()
    move_count = 0
    last_move_count = 0
    show_new_game_message = False
    initialize_game_screen(game)

def update_learning_stats():
    global ai_avg_reward
    if ai_learn_count > 0:
        ai_avg_reward = ai_total_reward / ai_learn_count
    else:
        ai_avg_reward = 0

# グローバル変数
show_new_game_message = False
new_game_message_start_time = 0

def run_pretrain_mode(screen, font):
    global pretrain_in_progress, pretrain_now, pretrain_total
    global win_black, win_white, ai_win_count, ai_lose_count, ai_draw_count
    global ai_learn_count, ai_total_reward, ai_avg_reward, game_count, move_count, last_move_count
    global qtable, game, learning_history, draw_mode

    pretrain_in_progress = True
    pretrain_now = 0
    win_black = 0
    win_white = 0
    ai_win_count = 0
    ai_lose_count = 0
    ai_draw_count = 0
    ai_learn_count = 0
    ai_total_reward = 0
    ai_avg_reward = 0
    game_count = 1
    move_count = 0
    last_move_count = 0
    qtable = load_qtable()
    game = OthelloGame()

    clock = pygame.time.Clock()
    running = True
    
    # 事前学習開始メッセージ
    screen.fill((30, 60, 80))
    start_text = font.render("事前学習を開始します", True, (255, 255, 255))
    screen.blit(start_text, (WINDOW_WIDTH//2 - start_text.get_width()//2, WINDOW_HEIGHT//2 - 60))
    info_text = get_japanese_font(24).render(f"訓練回数: {pretrain_total}", True, (255, 255, 255))
    screen.blit(info_text, (WINDOW_WIDTH//2 - info_text.get_width()//2, WINDOW_HEIGHT//2 - 20))
    pygame.display.flip()
    pygame.time.wait(1500)
    
    while running and pretrain_now < pretrain_total:
        # イベント処理を追加して固まるのを防ぐ
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
        
        if not running:
            break
            
        # 描画モードに応じて表示を切り替え
        if draw_mode:
            # 描画モードON: 通常のゲーム画面を表示
            screen.fill(WHITE)
            
            # 進捗バーを上部に表示
            progress = pretrain_now / pretrain_total
            bar_w = 600
            bar_h = 30
            bar_x = (WINDOW_WIDTH - bar_w) // 2
            bar_y = 20
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, int(bar_w*progress), bar_h))
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_w, bar_h), 3)
            
            # 進捗テキスト
            progress_text = get_japanese_font(18).render(f"訓練進捗: {pretrain_now}/{pretrain_total}", True, (0, 0, 0))
            screen.blit(progress_text, (bar_x + 20, bar_y + 5))
            
            # 現在の対戦番号を進捗バーの右側に表示
            battle_text = get_japanese_font(18).render(f"第{pretrain_now + 1}戦 / {pretrain_total}戦", True, (0, 0, 0))
            screen.blit(battle_text, (bar_x + bar_w + 20, bar_y + 5))
            
            draw_board(screen, game.board, game)
            draw_stones(screen, game.board, game)
            draw_current_player_indicator(screen, game.current_player)
            display_message(screen, game.message, game.last_move_error)
            black_score, white_score = game.get_score()
            display_score(screen, black_score, white_score)
            display_ai_reward(screen, game.ai_last_reward)
            draw_learn_count(screen, font, ai_learn_count)
            draw_pretrain_count(screen, font, pretrain_now, pretrain_total)
            draw_game_count(screen, font, game_count)
            last_move_count = draw_move_count(screen, font, move_count, last_move_count)
            draw_reset_button(screen, font, (0, 0), False)
            draw_back_button(screen, font, (0, 0), False)
            
            if show_left_graphs:
                progress_btn_rect = draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress)
        else:
            # 描画モードOFF: 進捗画面のみ表示
            screen.fill((30, 60, 80))
            
            # メインタイトル
            title_text = font.render("AI事前学習中", True, (255, 255, 255))
            screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 50))
            
            # 現在の対戦番号を大きく表示
            battle_text = font.render(f"第{pretrain_now + 1}戦 / {pretrain_total}戦", True, (255, 255, 255))
            screen.blit(battle_text, (WINDOW_WIDTH//2 - battle_text.get_width()//2, 100))
            
            # 進捗バー
            progress = pretrain_now / pretrain_total
            bar_w = 600
            bar_h = 40
            bar_x = (WINDOW_WIDTH - bar_w) // 2
            bar_y = WINDOW_HEIGHT // 2 - 60
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, int(bar_w*progress), bar_h))
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_w, bar_h), 3)
            
            # 進捗テキスト
            progress_text = font.render(f"訓練進捗: {pretrain_now}/{pretrain_total}", True, (255, 255, 255))
            screen.blit(progress_text, (bar_x + 20, bar_y - 50))
            
            # 統計情報
            stats_font = get_japanese_font(20)
            stats_y = bar_y + 120
            
            # 勝敗統計
            win_rate = 0
            if win_black + win_white > 0:
                win_rate = (win_white / (win_black + win_white)) * 100
            
            stats_text1 = stats_font.render(f"AI（白）勝利: {win_white}回", True, (255, 255, 255))
            stats_text2 = stats_font.render(f"AI（黒）勝利: {win_black}回", True, (255, 255, 255))
            stats_text3 = stats_font.render(f"AI（白）勝率: {win_rate:.1f}%", True, (255, 255, 255))
            
            screen.blit(stats_text1, (bar_x + 20, stats_y))
            screen.blit(stats_text2, (bar_x + 20, stats_y + 30))
            screen.blit(stats_text3, (bar_x + 20, stats_y + 60))
            
            # 学習統計
            if ai_learn_count > 0:
                avg_reward_text = stats_font.render(f"平均報酬: {ai_avg_reward:.1f}", True, (255, 255, 255))
                qtable_text = stats_font.render(f"Qテーブルサイズ: {len(qtable)}", True, (255, 255, 255))
                screen.blit(avg_reward_text, (bar_x + 20, stats_y + 90))
                screen.blit(qtable_text, (bar_x + 20, stats_y + 120))
        
        pygame.display.flip()
        clock.tick(30)  # フレームレートを30FPSに下げて描画を安定化

        # 1ゲーム分AI同士で自動対戦
        game = OthelloGame()
        move_count = 0
        game_move_count = 0  # ゲーム内の手数カウンター
        max_moves = 200  # 最大手数制限
        
        while not game.game_over and game_move_count < max_moves:
            # イベント処理を追加
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
            
            if not running:
                break
                
            valid_moves = game.get_valid_moves(game.current_player)
            if valid_moves:
                try:
                    if game.current_player == PLAYER_WHITE:
                        game.ai_qlearning_move(qtable, learn=True, player=PLAYER_WHITE)
                    else:
                        action = random.choice(valid_moves)
                        r, c = action
                        game.make_move(r, c, PLAYER_BLACK)
                    game.switch_player()
                    game.check_game_over()
                    game_move_count += 1
                    
                    # 描画モードONの場合は毎手描画更新
                    if draw_mode:
                        screen.fill(WHITE)
                        
                        # 進捗バーを上部に表示
                        progress = pretrain_now / pretrain_total
                        bar_w = 600
                        bar_h = 30
                        bar_x = (WINDOW_WIDTH - bar_w) // 2
                        bar_y = 20
                        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h))
                        pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, int(bar_w*progress), bar_h))
                        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_w, bar_h), 3)
                        
                        # 進捗テキスト
                        progress_text = get_japanese_font(18).render(f"訓練進捗: {pretrain_now}/{pretrain_total}", True, (0, 0, 0))
                        screen.blit(progress_text, (bar_x + 20, bar_y + 5))
                        
                        # 現在の対戦番号を進捗バーの右側に表示
                        battle_text = get_japanese_font(18).render(f"第{pretrain_now + 1}戦 / {pretrain_total}戦", True, (0, 0, 0))
                        screen.blit(battle_text, (bar_x + bar_w + 20, bar_y + 5))
                        
                        draw_board(screen, game.board, game)
                        draw_stones(screen, game.board, game)
                        draw_current_player_indicator(screen, game.current_player)
                        display_message(screen, game.message, game.last_move_error)
                        black_score, white_score = game.get_score()
                        display_score(screen, black_score, white_score)
                        display_ai_reward(screen, game.ai_last_reward)
                        draw_learn_count(screen, font, ai_learn_count)
                        draw_pretrain_count(screen, font, pretrain_now, pretrain_total)
                        draw_game_count(screen, font, game_count)
                        last_move_count = draw_move_count(screen, font, move_count, last_move_count)
                        draw_reset_button(screen, font, (0, 0), False)
                        draw_back_button(screen, font, (0, 0), False)
                        if show_left_graphs:
                            progress_btn_rect = draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress)
                        pygame.display.flip()
                        clock.tick(30)
                    # 描画モードOFFの場合は10手ごとに進捗更新
                    elif not fast_mode and game_move_count % 10 == 0:
                        # 現在のゲーム状況を簡易表示
                        screen.fill((30, 60, 80))
                        title_text = font.render("AI事前学習中", True, (255, 255, 255))
                        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 50))
                        
                        # 現在の対戦番号を大きく表示
                        battle_text = font.render(f"第{pretrain_now + 1}戦 / {pretrain_total}戦", True, (255, 255, 255))
                        screen.blit(battle_text, (WINDOW_WIDTH//2 - battle_text.get_width()//2, 100))
                        
                        # 進捗バー
                        progress = pretrain_now / pretrain_total
                        bar_w = 600
                        bar_h = 40
                        bar_x = (WINDOW_WIDTH - bar_w) // 2
                        bar_y = WINDOW_HEIGHT // 2 - 60
                        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h))
                        pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, int(bar_w*progress), bar_h))
                        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_w, bar_h), 3)
                        
                        # 現在のゲーム状況（手数）
                        game_text = get_japanese_font(20).render(f"手数: {game_move_count}", True, (255, 255, 255))
                        screen.blit(game_text, (bar_x + 20, bar_y + 60))
                        
                        pygame.display.flip()
                        clock.tick(30)
                except Exception as e:
                    print(f"ゲーム実行中にエラーが発生しました: {e}")
                    break
            else:
                game.switch_player()
                game.check_game_over()
                game_move_count += 1
        
        # 勝敗集計
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
        
        # 学習統計更新
        update_learning_stats()
        
        # 履歴記録
        learning_history.add_record(
            game_count, ai_learn_count, ai_win_count, ai_lose_count, 
            ai_draw_count, ai_total_reward, ai_avg_reward, len(qtable), black_score, white_score
        )
        
        pretrain_now += 1
        game_count += 1
    
    # 訓練終了
    save_qtable(qtable)
    pretrain_in_progress = False
    
    # 終了メッセージ
    screen.fill((30, 60, 80))
    complete_text = font.render("事前学習が完了しました！", True, (255, 255, 255))
    screen.blit(complete_text, (WINDOW_WIDTH//2 - complete_text.get_width()//2, WINDOW_HEIGHT//2 - 60))
    
    # 最終統計
    final_win_rate = 0
    if win_black + win_white > 0:
        final_win_rate = (win_white / (win_black + win_white)) * 100
    
    final_stats1 = get_japanese_font(24).render(f"最終勝率: {final_win_rate:.1f}%", True, (255, 255, 255))
    final_stats2 = get_japanese_font(24).render(f"Qテーブルサイズ: {len(qtable)}", True, (255, 255, 255))
    
    screen.blit(final_stats1, (WINDOW_WIDTH//2 - final_stats1.get_width()//2, WINDOW_HEIGHT//2 - 20))
    screen.blit(final_stats2, (WINDOW_WIDTH//2 - final_stats2.get_width()//2, WINDOW_HEIGHT//2 + 20))
    
    pygame.display.flip()
    pygame.time.wait(2000)
    
    # 人間vsAIモードへ遷移
    return MODE_HUMAN_TRAIN

def draw_battle_history_screen(screen, font):
    draw_battle_history_list(screen, learning_history, font)

if __name__ == "__main__":
    main_loop() 