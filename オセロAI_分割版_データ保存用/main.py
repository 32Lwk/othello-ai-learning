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
    confirm_delete_learning_data, overwrite_learning_data, enhanced_ai_self_play
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
analysis_mode = False  # 分析画面表示モード
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

# 画面サイズ変数（グローバル宣言）
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# 学習履歴管理オブジェクト
learning_history = LearningHistory(max_history=50)
learning_logger = LearningLogger()

# Qテーブル
qtable = load_qtable()

# ゲームオブジェクト
game = OthelloGame()

# ゲームメッセージ表示制御
show_new_game_message = False
new_game_message_start_time = 0

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
    global data_view_mode, battle_history_mode, analysis_mode, show_left_graphs, show_learning_progress
    global WINDOW_WIDTH, WINDOW_HEIGHT

    while True:
        # モード選択画面を表示し、current_modeがセットされるまでループ
        result = mode_select_screen(screen, font)
        if result == "mode_select" or current_mode is None:
            continue
        else:
            break

    if current_mode == MODE_AI_PRETRAIN:
        # current_mode = run_pretrain_mode(screen, font)  # 未定義のため一時的にコメントアウト
        # 事前学習完了後、人間vsAIモードに移行
        # if current_mode == MODE_HUMAN_TRAIN:
        #     game = OthelloGame()
        #     initialize_game_screen(game)
        # else:
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
                    save_button, overwrite_button, load_button, new_button, delete_button, back_button, progress_btn_rect = draw_learning_data_screen(
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
                        elif overwrite_button.collidepoint(mouse_pos):
                            overwrite_learning_data(qtable, learning_history, screen, font)
                        elif load_button.collidepoint(mouse_pos):
                            result = load_learning_data(qtable, learning_history, screen, font)
                            if result:
                                game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = result
                        elif new_button.collidepoint(mouse_pos):
                            create_new_learning_data(qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, screen, font)
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
                    # draw_battle_history_screen(screen, font)  # 未定義のため一時的にコメントアウト
                    # 戻るボタンのクリック判定
                    if mouse_down:
                        back_button_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
                        if back_button_rect.collidepoint(mouse_pos):
                            battle_history_mode = False
                            show_left_graphs = True  # 左側のグラフを再表示
                    pygame.display.flip()
                    pygame.time.Clock().tick(30)
                    continue
                
                # 分析画面表示モードの場合
                if analysis_mode:
                    show_left_graphs = False  # 左側のグラフを非表示
                    result = draw_analysis_screen(screen, font)
                    if result == "back":
                        analysis_mode = False
                        show_left_graphs = True  # 左側のグラフを再表示
                    pygame.display.flip()
                    pygame.time.Clock().tick(30)
                    continue
                
                # 通常のゲームモードの場合
                # 盤面クリック時のみ人間の手番なら石を置く
                # if game.current_player == PLAYER_BLACK and not show_new_game_message and not game.game_over:
                #     handle_mouse_click(event.pos)  # 未定義のため一時的にコメントアウト
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
                    # draw_reset_button(screen, font, (0, 0), False)
                    # draw_back_button(screen, font, (0, 0), False)
                    if show_left_graphs:
                        progress_btn_rect = draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress)
                # if draw_reset_button(screen, font, mouse_pos, True):
                #     reset_game()  # 未定義のため一時的にコメントアウト
                # if draw_back_button(screen, font, mouse_pos, True):
                #     ...
                #     if current_mode == MODE_AI_PRETRAIN:
                #         current_mode = run_pretrain_mode(screen, font)
                #         if current_mode == MODE_HUMAN_TRAIN:
                #             game = OthelloGame()
                #             initialize_game_screen(game)
                #     else:
                #         game = OthelloGame()
                #         initialize_game_screen(game)
            
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
                # draw_reset_button(screen, font, (0, 0), False)
                # draw_back_button(screen, font, (0, 0), False)
                if show_left_graphs:
                    progress_btn_rect = draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress)
                pygame.display.flip()
        
        # AIの手番は自動で進める
        if game.current_player == PLAYER_WHITE and not show_new_game_message and not game.game_over:
            # AIに有効な手があるかチェック
            if game.get_valid_moves(PLAYER_WHITE):
                result = game.ai_qlearning_move(qtable, learn=True, player=PLAYER_WHITE, ai_learn_count=ai_learn_count)
                if result:  # 手を打った場合
                    reward = game.ai_last_reward
                    ai_learn_count += 1
                    ai_total_reward += reward
                    ai_avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
                    # デバッグ出力
                    if DEBUG_MODE:
                        print(f"白の手: 報酬={reward}, 累積報酬={ai_total_reward}, 平均報酬={ai_avg_reward:.2f}, 学習回数={ai_learn_count}")
                    game.switch_player()
                    game.check_game_over()
                else:
                    # AIに有効な手がない場合はパス
                    game.message = "AI（白）はパスしました。"
                    game.switch_player()
                    game.check_game_over()
            else:
                # AIに有効な手がない場合はパス
                game.message = "AI（白）はパスしました。"
                game.switch_player()
                game.check_game_over()

        # 人間プレイヤー（黒）の手番で有効な手がない場合の処理
        if game.current_player == PLAYER_BLACK and not show_new_game_message and not game.game_over:
            if not game.get_valid_moves(PLAYER_BLACK):
                # 人間プレイヤーに有効な手がない場合はパス
                game.message = "黒は置ける場所がないためパスしました。"
                game.switch_player()
                game.check_game_over()

        # AI同士の訓練中はmainループでの描画をスキップし、enhanced_ai_self_play側の新UIのみ表示
        if not show_new_game_message and current_mode != MODE_AI_PRETRAIN:
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
    global current_mode, pretrain_total, DEBUG_MODE, ai_speed, draw_mode, data_view_mode, battle_history_mode, analysis_mode
    global ai_learn_count, game_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward
    global WINDOW_WIDTH, WINDOW_HEIGHT
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
        screen.blit(title_surface, title_rect)
        
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
                if event.key == pygame.K_ESCAPE and (data_view_mode or battle_history_mode or analysis_mode):
                    data_view_mode = False
                    battle_history_mode = False
                    analysis_mode = False
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
            save_button, overwrite_button, load_button, new_button, delete_button, back_button, progress_btn_rect = draw_learning_data_screen(
                screen, font, learning_history, qtable, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, False)
            # ボタンのクリック判定
            if mouse_down:
                if save_button.collidepoint(mouse_pos):
                    save_learning_data(qtable, learning_history, screen, font)
                elif overwrite_button.collidepoint(mouse_pos):
                    overwrite_learning_data(qtable, learning_history, screen, font)
                elif load_button.collidepoint(mouse_pos):
                    result = load_learning_data(qtable, learning_history, screen, font)
                    if result:
                        game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = result
                elif new_button.collidepoint(mouse_pos):
                    create_new_learning_data(qtable, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, screen, font)
                elif delete_button.collidepoint(mouse_pos):
                    confirm_delete_learning_data(screen, font)
                elif back_button.collidepoint(mouse_pos):
                    data_view_mode = False
            pygame.display.flip()
            pygame.time.Clock().tick(30)
            continue
        
        # 対戦記録表示モードの場合
        if battle_history_mode:
            # draw_battle_history_screen(screen, font)  # 未定義のため一時的にコメントアウト
            # 戻るボタンのクリック判定
            if mouse_down:
                back_button_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
                if back_button_rect.collidepoint(mouse_pos):
                    battle_history_mode = False
            pygame.display.flip()
            pygame.time.Clock().tick(30)
            continue
        
        # 分析画面表示モードの場合
        if analysis_mode:
            result = draw_analysis_screen(screen, font)
            if result == "back":
                analysis_mode = False
            pygame.display.flip()
            pygame.time.Clock().tick(30)
            continue
        
        # ボタンを描画（2列レイアウト）
        button_width = 340  # ボタン幅を大きく
        button_height = 80  # ボタン高さを大きく
        button_spacing_x = 50  # 列間の間隔も少し広く
        button_spacing_y = 90  # 行間の間隔も広く
        button_x_left = (WINDOW_WIDTH - button_width * 2 - button_spacing_x) // 2  # 左列の開始位置
        button_x_right = button_x_left + button_width + button_spacing_x  # 右列の開始位置
        button_y_start = 240  # 開始位置をボタン一つ分（90px）下に移動
        
        # 左列のボタン
        # 対戦モードボタン
        if draw_enhanced_button(screen, button_x_left, button_y_start, button_width, button_height, 
                              "対戦モード", "🎮", "人間プレイヤーとしてAIと直接対戦し、AIを学習させます", 
                              (100, 150, 255, 150), (150, 200, 255, 150), mouse_pos, mouse_down, font, animation_time):
            current_mode = MODE_HUMAN_TRAIN
            selecting = False
        
        # 事前訓練モードボタン
        if draw_enhanced_button(screen, button_x_left, button_y_start + button_spacing_y, button_width, button_height, 
                              "事前訓練", "🤖", "AI同士で事前訓練を行い、その後人間と対戦します", 
                              (255, 150, 100, 150), (255, 180, 130, 150), mouse_pos, mouse_down, font, animation_time):
            execute_pretrain_learning(screen, font, pretrain_total)
        
        # 強化学習モードボタン
        if draw_enhanced_button(screen, button_x_left, button_y_start + button_spacing_y * 2, button_width, button_height, 
                              "強化学習", "🚀", "AIを大幅に強化するための集中学習モード", 
                              (255, 100, 255, 150), (255, 130, 255, 150), mouse_pos, mouse_down, font, animation_time):
            run_enhanced_learning_mode(screen, font)
        
        # 評価改善モードボタン
        if draw_enhanced_button(screen, button_x_left, button_y_start + button_spacing_y * 3, button_width, button_height, 
                              "評価改善", "📈", "総合評価を改善するための戦略的学習モード", 
                              (255, 150, 50, 150), (255, 180, 80, 150), mouse_pos, mouse_down, font, animation_time):
            run_evaluation_improvement_mode(screen, font)
        
        # 右列のボタン
        # 学習データ確認ボタン
        if draw_enhanced_button(screen, button_x_right, button_y_start, button_width, button_height, 
                              "学習データ", "📊", "AIの学習進捗と統計データを詳細に確認できます", 
                              (100, 255, 150, 150), (130, 255, 180, 150), mouse_pos, mouse_down, font, animation_time):
            data_view_mode = True
        
        # 対戦記録ボタン
        if draw_enhanced_button(screen, button_x_right, button_y_start + button_spacing_y, button_width, button_height, 
                              "対戦記録", "📋", "過去の対戦結果と詳細な記録を確認できます", 
                              (255, 100, 150, 150), (255, 130, 180, 150), mouse_pos, mouse_down, font, animation_time):
            battle_history_mode = True
        
        # AI分析ボタン
        if draw_enhanced_button(screen, button_x_right, button_y_start + button_spacing_y * 2, button_width, button_height, 
                              "AI分析", "🔍", "AIの学習状況を詳細に分析し、改善提案を行います", 
                              (255, 200, 100, 150), (255, 220, 130, 150), mouse_pos, mouse_down, font, animation_time):
            analysis_mode = True
        
        # 設定ボタン
        if draw_enhanced_button(screen, button_x_right, button_y_start + button_spacing_y * 3, button_width, button_height, 
                              "設定", "⚙️", "AIや学習の各種設定を変更できます", 
                              (180, 180, 180, 150), (220, 220, 220, 150), mouse_pos, mouse_down, font, animation_time):
            result = settings_screen(screen, font, DEBUG_MODE, ai_speed, draw_mode, pretrain_total)
            if isinstance(result, tuple) and len(result) >= 9:
                # 設定画面から戻った場合、値をグローバル変数に反映
                DEBUG_MODE, ai_speed, draw_mode, new_pretrain_total, fast_mode, draw_mode, DEBUG_MODE, new_width, new_height = result[:9]
                
                print(f"main.py: 設定画面から受け取った値 - new_pretrain_total: {new_pretrain_total}")
                print(f"main.py: 現在のグローバル変数 - pretrain_total: {pretrain_total}")
                
                # 訓練回数の変更を反映
                if new_pretrain_total != pretrain_total:
                    pretrain_total = new_pretrain_total
                    print(f"main.py: 訓練回数を変更しました: {pretrain_total}")
                else:
                    print(f"main.py: 訓練回数は変更されていません")
                
                # 画面サイズが変更された場合
                if new_width != WINDOW_WIDTH or new_height != WINDOW_HEIGHT:
                    WINDOW_WIDTH, WINDOW_HEIGHT = new_width, new_height
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                    print(f"画面サイズを変更しました: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # 統計情報を描画（右側に表示、位置を調整）
        draw_quick_stats(screen, animation_time, ai_learn_count, game_count)
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def initialize_game_screen(game_obj):
    """ゲーム画面の初期化"""
    pass

def execute_enhanced_learning(screen, font, num_games, mode_name):
    """強化学習を実行"""
    global qtable, learning_history, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward
    
    print(f"🚀 {mode_name}学習開始: {num_games}ゲーム")
    
    # 学習画面を表示
    show_learning_progress_screen(screen, font, f"{mode_name}学習中...", "準備中...")
    
    # ゲームオブジェクトを作成
    game = OthelloGame()
    
    # 強化学習を実行
    try:
        ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = enhanced_ai_self_play(
            game, qtable, num_games, learn=True
        )
        
        # 学習履歴に記録
        learning_history.add_record(
            game_count=num_games,
            ai_learn_count=ai_learn_count,
            ai_win_count=ai_win_count,
            ai_lose_count=ai_lose_count,
            ai_draw_count=ai_draw_count,
            ai_total_reward=ai_total_reward,
            ai_avg_reward=ai_avg_reward,
            qtable_size=len(qtable),
            game_type="ai_vs_ai"
        )
        
        # Qテーブルを保存
        save_qtable(qtable)
        
        # 完了画面を表示
        show_learning_complete_screen(screen, font, mode_name, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward)
        
    except Exception as e:
        print(f"❌ 学習エラー: {e}")
        show_learning_error_screen(screen, font, str(e))

def execute_adaptive_learning(screen, font):
    """適応的学習を実行"""
    global qtable, learning_history, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward
    
    print(f"🔄 適応的学習開始")
    
    # 学習画面を表示
    show_learning_progress_screen(screen, font, "適応的学習中...", "準備中...")
    
    # ゲームオブジェクトを作成
    game = OthelloGame()
    
    # 適応的学習を実行（一時的にコメントアウト）
    try:
        # ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward = adaptive_learning_schedule(
        #     game, qtable, initial_games=50, max_games=300
        # )
        # 代わりに通常の自己対戦を実行
        ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = enhanced_ai_self_play(
            game, qtable, 100, learn=True, draw_mode=draw_mode, screen=screen, font=font
        )
        
        # 学習履歴に記録
        total_games = ai_win_count + ai_lose_count + ai_draw_count
        learning_history.add_record(
            game_count=total_games,
            ai_learn_count=ai_learn_count,
            ai_win_count=ai_win_count,
            ai_lose_count=ai_lose_count,
            ai_draw_count=ai_draw_count,
            ai_total_reward=ai_total_reward,
            ai_avg_reward=ai_avg_reward,
            qtable_size=len(qtable),
            game_type="ai_vs_ai"
        )
        
        # Qテーブルを保存
        save_qtable(qtable)
        
        # 完了画面を表示
        show_learning_complete_screen(screen, font, "適応的学習", ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward)
        
    except Exception as e:
        print(f"❌ 学習エラー: {e}")
        show_learning_error_screen(screen, font, str(e))

def show_learning_progress_screen(screen, font, title, status):
    """学習進捗画面を表示"""
    screen.fill((50, 50, 100))
    
    # タイトル
    title_surface = font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
    screen.blit(title_surface, title_rect)
    
    # ステータス
    status_font = get_japanese_font(24)
    status_surface = status_font.render(status, True, (200, 200, 200))
    status_rect = status_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
    screen.blit(status_surface, status_rect)
    
    pygame.display.flip()

def show_learning_complete_screen(screen, font, mode_name, wins, losses, draws, avg_reward):
    """学習完了画面を表示"""
    waiting = True
    animation_time = 0
    
    while waiting:
        current_time = pygame.time.get_ticks()
        animation_time = (current_time % 2000) / 2000
        
        # 背景
        draw_gradient_background(screen, animation_time)
        
        # タイトル
        title_font = get_japanese_font(48)
        title_surface = title_font.render("🎯 学習完了!", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 150))
        screen.blit(title_surface, title_rect)
        
        # 結果表示
        result_font = get_japanese_font(24)
        total_games = wins + losses + draws
        win_rate = (wins / total_games) * 100 if total_games > 0 else 0
        
        results = [
            f"学習モード: {mode_name}",
            f"総ゲーム数: {total_games}",
            f"AI勝利: {wins}",
            f"AI敗北: {losses}",
            f"引き分け: {draws}",
            f"勝率: {win_rate:.1f}%",
            f"平均報酬: {avg_reward:.2f}"
        ]
        
        for i, result in enumerate(results):
            result_surface = result_font.render(result, True, (255, 255, 255))
            result_rect = result_surface.get_rect(center=(WINDOW_WIDTH//2, 250 + i * 35))
            screen.blit(result_surface, result_rect)
        
        # 評価メッセージ
        if win_rate > 90:
            eval_text = "🏆 素晴らしい! AIが非常に強くなりました!"
        elif win_rate > 80:
            eval_text = "🎉 優秀! AIが大幅に強化されました!"
        elif win_rate > 70:
            eval_text = "👍 良好! AIが強化されました!"
        else:
            eval_text = "📈 学習継続が必要です"
        
        eval_surface = result_font.render(eval_text, True, (255, 255, 0))
        eval_rect = eval_surface.get_rect(center=(WINDOW_WIDTH//2, 500))
        screen.blit(eval_surface, eval_rect)
        
        # 続行ボタン
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                    waiting = False
        
        # 続行ボタン
        button_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 120, 200, 60)
        pygame.draw.rect(screen, (100, 200, 100), button_rect)
        pygame.draw.rect(screen, (150, 250, 150), button_rect, 3)
        
        button_font = get_japanese_font(20)
        button_text = "続行"
        button_surface = button_font.render(button_text, True, (255, 255, 255))
        button_text_rect = button_surface.get_rect(center=button_rect.center)
        screen.blit(button_surface, button_text_rect)
        
        if mouse_down and button_rect.collidepoint(mouse_pos):
            waiting = False
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def show_learning_error_screen(screen, font, error_message):
    """学習エラー画面を表示"""
    waiting = True
    
    while waiting:
        screen.fill((100, 50, 50))
        
        # エラーメッセージ
        error_font = get_japanese_font(24)
        error_surface = error_font.render("❌ 学習エラー", True, (255, 255, 255))
        error_rect = error_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        screen.blit(error_surface, error_rect)
        
        # 詳細メッセージ
        detail_font = get_japanese_font(18)
        detail_surface = detail_font.render(error_message, True, (255, 200, 200))
        detail_rect = detail_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
        screen.blit(detail_surface, detail_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                    waiting = False
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def calculate_ai_strength():
    """AIの強度を計算"""
    global ai_win_count, ai_lose_count, ai_draw_count, ai_learn_count
    
    total_games = ai_win_count + ai_lose_count + ai_draw_count
    if total_games == 0:
        return "未学習"
    
    win_rate = (ai_win_count / total_games) * 100
    
    if win_rate > 90:
        return "伝説級"
    elif win_rate > 80:
        return "マスター級"
    elif win_rate > 70:
        return "エキスパート級"
    elif win_rate > 60:
        return "上級者級"
    elif win_rate > 50:
        return "中級者級"
    else:
        return "初心者級"

def show_custom_games_input(screen, font):
    """カスタムゲーム数入力画面"""
    input_text = ""
    input_mode = True
    animation_time = 0
    
    while input_mode:
        current_time = pygame.time.get_ticks()
        animation_time = (current_time % 2000) / 2000
        
        # 背景
        draw_gradient_background(screen, animation_time)
        
        # タイトル
        title_font = get_japanese_font(36)
        title_surface = title_font.render("🎛️ カスタム強化学習", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 150))
        screen.blit(title_surface, title_rect)
        
        # 説明文
        desc_font = get_japanese_font(20)
        desc_surface = desc_font.render("学習するゲーム数を入力してください (10-1000)", True, (255, 255, 255))
        desc_rect = desc_surface.get_rect(center=(WINDOW_WIDTH//2, 200))
        screen.blit(desc_surface, desc_rect)
        
        # 推奨設定の表示
        recommend_font = get_japanese_font(16)
        recommendations = [
            "推奨設定:",
            "• 軽微な強化: 50-100ゲーム",
            "• 標準強化: 100-200ゲーム", 
            "• 大幅強化: 200-500ゲーム",
            "• 超強化: 500-1000ゲーム"
        ]
        
        for i, rec in enumerate(recommendations):
            rec_surface = recommend_font.render(rec, True, (200, 200, 200))
            rec_rect = rec_surface.get_rect(center=(WINDOW_WIDTH//2, 250 + i * 25))
            screen.blit(rec_surface, rec_rect)
        
        # 入力フィールド
        input_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, 400, 300, 50)
        pygame.draw.rect(screen, (255, 255, 255), input_rect)
        pygame.draw.rect(screen, (100, 100, 100), input_rect, 3)
        
        # 入力テキスト
        input_surface = font.render(input_text if input_text else "ゲーム数を入力", True, (0, 0, 0) if input_text else (150, 150, 150))
        input_text_rect = input_surface.get_rect(center=input_rect.center)
        screen.blit(input_surface, input_text_rect)
        
        # ボタン
        button_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, 500, 200, 50)
        pygame.draw.rect(screen, (100, 200, 100), button_rect)
        button_surface = font.render("開始", True, (255, 255, 255))
        button_text_rect = button_surface.get_rect(center=button_rect.center)
        screen.blit(button_surface, button_text_rect)
        
        # キャンセルボタン
        cancel_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, 570, 200, 50)
        pygame.draw.rect(screen, (200, 100, 100), cancel_rect)
        cancel_surface = font.render("キャンセル", True, (255, 255, 255))
        cancel_text_rect = cancel_surface.get_rect(center=cancel_rect.center)
        screen.blit(cancel_surface, cancel_text_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0
                elif event.key == pygame.K_RETURN:
                    try:
                        games = int(input_text)
                        if 10 <= games <= 1000:
                            return games
                    except ValueError:
                        pass
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isnumeric():
                    if len(input_text) < 4:  # 最大4桁まで
                        input_text += event.unicode
        
        # ボタンクリック判定
        if mouse_down:
            if button_rect.collidepoint(mouse_pos):
                try:
                    games = int(input_text)
                    if 10 <= games <= 1000:
                        return games
                except ValueError:
                    pass
            elif cancel_rect.collidepoint(mouse_pos):
                return 0
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    
    return 0

def draw_analysis_screen(screen, font):
    """
    AI学習分析画面を描画
    """
    global WINDOW_WIDTH, WINDOW_HEIGHT, learning_history, qtable
    
    running = True
    
    while running:
        # 背景を描画
        screen.fill((240, 248, 255))  # 薄い青の背景
        
        # タイトル
        title_font = get_japanese_font(36)
        title_surface = title_font.render("🤖 AI学習分析", True, (50, 50, 50))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 50))
        screen.blit(title_surface, title_rect)
        
        # 分析オプションボタン
        button_width = 280
        button_height = 60
        button_x = (WINDOW_WIDTH - button_width) // 2
        button_y_start = 120
        button_spacing = 80
        
        # マウス位置とクリック状態を取得
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
        
        # ボタンの矩形を定義
        detailed_button_rect = pygame.Rect(button_x, button_y_start, button_width, button_height)
        summary_button_rect = pygame.Rect(button_x, button_y_start + button_spacing, button_width, button_height)
        graph_button_rect = pygame.Rect(button_x, button_y_start + button_spacing * 2, button_width, button_height)
        recommend_button_rect = pygame.Rect(button_x, button_y_start + button_spacing * 3, button_width, button_height)
        back_button_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
        
        # ボタンを描画（シンプルな描画）
        buttons = [
            (detailed_button_rect, "詳細分析", "📊", (100, 150, 255)),
            (summary_button_rect, "成果サマリー", "🎯", (255, 150, 100)),
            (graph_button_rect, "グラフ分析", "📈", (255, 100, 255)),
            (recommend_button_rect, "推奨事項", "💡", (100, 255, 150)),
            (back_button_rect, "戻る", "←", (180, 180, 180))
        ]
        
        # ボタンを描画
        for button_rect, text, icon, color in buttons:
            # ホバー効果
            if button_rect.collidepoint(mouse_pos):
                hover_color = tuple(min(255, c + 30) for c in color)
                pygame.draw.rect(screen, hover_color, button_rect)
            else:
                pygame.draw.rect(screen, color, button_rect)
            
            # ボーダー
            pygame.draw.rect(screen, (50, 50, 50), button_rect, 2)
            
            # テキスト
            button_font = get_japanese_font(20)
            button_text = f"{icon} {text}"
            text_surface = button_font.render(button_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
        
        # マウスクリックの判定
        if mouse_down:
            if detailed_button_rect.collidepoint(mouse_pos):
                show_detailed_analysis(screen, font)
            elif summary_button_rect.collidepoint(mouse_pos):
                show_learning_summary_screen(screen, font)
            elif graph_button_rect.collidepoint(mouse_pos):
                show_graph_analysis(screen, font)
            elif recommend_button_rect.collidepoint(mouse_pos):
                show_recommendations_screen(screen, font)
            elif back_button_rect.collidepoint(mouse_pos):
                return "back"
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def show_detailed_analysis(screen, font):
    """
    詳細分析画面を表示
    """
    global learning_history, qtable, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward
    
    # 現在の統計を取得
    total_games = ai_win_count + ai_lose_count + ai_draw_count
    win_rate = (ai_win_count / total_games) * 100 if total_games > 0 else 0
    avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
    
    # 分析を実行
    from ai_learning import analyze_learning_progress
    score = analyze_learning_progress(ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, len(qtable), total_games)
    
    # 分析結果を画面に表示
    screen.fill((240, 248, 255))
    
    # タイトル
    title_font = get_japanese_font(32)
    title_surface = title_font.render("📊 詳細分析結果", True, (50, 50, 50))
    title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 40))
    screen.blit(title_surface, title_rect)
    
    # 分析結果をテキストで表示
    small_font = get_japanese_font(20)
    y_pos = 100
    line_height = 25
    
    results = [
        f"🎯 基本統計:",
        f"  総ゲーム数: {total_games}",
        f"  勝利: {ai_win_count} ({win_rate:.1f}%)",
        f"  敗北: {ai_lose_count} ({(ai_lose_count/total_games*100):.1f}%)" if total_games > 0 else "  敗北: 0 (0.0%)",
        f"  引き分け: {ai_draw_count} ({(ai_draw_count/total_games*100):.1f}%)" if total_games > 0 else "  引き分け: 0 (0.0%)",
        f"  総学習回数: {ai_learn_count}",
        f"  平均報酬: {avg_reward:.2f}",
        f"  Qテーブルサイズ: {len(qtable)}",
        "",
        f"⚡ 学習効率:",
        f"  ゲームあたりの学習回数: {(ai_learn_count/total_games):.1f}" if total_games > 0 else "  ゲームあたりの学習回数: 0.0",
        "",
        f"🏆 勝率評価:",
    ]
    
    # 勝率評価を追加
    if win_rate > 90:
        results.append("  🏅 卓越した強さ")
    elif win_rate > 80:
        results.append("  🥇 優秀な強さ")
    elif win_rate > 70:
        results.append("  🥈 良好な強さ")
    elif win_rate > 60:
        results.append("  🥉 平均的な強さ")
    elif win_rate > 50:
        results.append("  📊 標準的な強さ")
    else:
        results.append("  ⚠️ 改善が必要")
    
    results.extend([
        "",
        f"💰 報酬評価:",
    ])
    
    # 報酬評価を追加
    if avg_reward > 10:
        results.append("  🎉 非常に高い報酬")
    elif avg_reward > 5:
        results.append("  👍 高い報酬")
    elif avg_reward > 2:
        results.append("  📈 良好な報酬")
    elif avg_reward > 0:
        results.append("  📊 標準的な報酬")
    else:
        results.append("  ⚠️ 低い報酬")
    
    results.extend([
        "",
        f"🧠 Qテーブル成長:",
    ])
    
    # Qテーブル評価を追加
    if len(qtable) > 5000:
        results.append("  🧠 非常に豊富な知識")
    elif len(qtable) > 3000:
        results.append("  🧠 豊富な知識")
    elif len(qtable) > 2000:
        results.append("  🧠 良好な知識")
    elif len(qtable) > 1000:
        results.append("  🧠 標準的な知識")
    else:
        results.append("  🧠 限定的な知識")
    
    results.extend([
        "",
        f"🎯 総合評価:",
        f"  スコア: {score}/8",
    ])
    
    if score >= 7:
        results.append("  🌟 優秀")
    elif score >= 5:
        results.append("  👍 良好")
    elif score >= 3:
        results.append("  📈 改善中")
    else:
        results.append("  ⚠️ 要改善")
    
    # 結果を描画
    for line in results:
        if line.strip() == "":
            y_pos += line_height // 2
        else:
            text_surface = small_font.render(line, True, (50, 50, 50))
            screen.blit(text_surface, (50, y_pos))
            y_pos += line_height
    
    # 続行ボタン
    continue_button_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
    pygame.draw.rect(screen, (100, 150, 255), continue_button_rect)
    pygame.draw.rect(screen, (50, 100, 200), continue_button_rect, 3)
    
    button_font = get_japanese_font(24)
    button_text = button_font.render("続行", True, (255, 255, 255))
    button_text_rect = button_text.get_rect(center=continue_button_rect.center)
    screen.blit(button_text, button_text_rect)
    
    pygame.display.flip()
    
    # ボタンクリック待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if continue_button_rect.collidepoint(event.pos):
                    waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    waiting = False
        pygame.time.Clock().tick(30)

def show_learning_summary_screen(screen, font):
    """
    学習成果サマリー画面を表示
    """
    global ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, qtable
    
    total_games = ai_win_count + ai_lose_count + ai_draw_count
    win_rate = (ai_win_count / total_games) * 100 if total_games > 0 else 0
    avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
    
    screen.fill((240, 248, 255))
    
    # タイトル
    title_font = get_japanese_font(32)
    title_surface = title_font.render("🎯 学習成果サマリー", True, (50, 50, 50))
    title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 40))
    screen.blit(title_surface, title_rect)
    
    # 成果レベルを判定
    if win_rate > 80 and avg_reward > 5 and len(qtable) > 3000:
        level = "🏅 卓越した成果"
        description = "AIが非常に強くなりました!"
    elif win_rate > 70 and avg_reward > 3 and len(qtable) > 2000:
        level = "🥇 優秀な成果"
        description = "AIが大幅に強化されました!"
    elif win_rate > 60 and avg_reward > 2 and len(qtable) > 1500:
        level = "🥈 良好な成果"
        description = "AIが強化されました!"
    elif win_rate > 50 and avg_reward > 1 and len(qtable) > 1000:
        level = "🥉 改善が見られます"
        description = "さらなる学習で向上が期待できます!"
    else:
        level = "📈 学習継続が必要"
        description = "パラメータ調整を検討してください"
    
    # 成果を表示
    small_font = get_japanese_font(24)
    y_pos = 100
    line_height = 30
    
    results = [
        f"🏆 今回の学習成果:",
        f"  📊 ゲーム数: {total_games}",
        f"  🎯 勝率: {win_rate:.1f}%",
        f"  💰 平均報酬: {avg_reward:.2f}",
        f"  🧠 Qテーブルサイズ: {len(qtable)}",
        f"  ⚡ 学習回数: {ai_learn_count}",
        "",
        f"🌟 成果レベル:",
        f"  {level}",
        f"  {description}",
        "",
        f"💡 次のステップ:",
    ]
    
    # 次のステップを追加
    if win_rate > 70:
        results.extend([
            "  ✅ 人間との対戦で実力を確認",
            "  ✅ 学習データを保存",
            "  ✅ より高度な戦略の学習"
        ])
    elif win_rate > 50:
        results.extend([
            "  📈 学習ゲーム数を増やす",
            "  📈 学習パラメータを調整",
            "  📈 より多くの状況での学習"
        ])
    else:
        results.extend([
            "  🔧 学習率の見直し",
            "  🔧 報酬設計の調整",
            "  🔧 探索率の最適化"
        ])
    
    # 結果を描画
    for line in results:
        if line.strip() == "":
            y_pos += line_height // 2
        else:
            text_surface = small_font.render(line, True, (50, 50, 50))
            screen.blit(text_surface, (50, y_pos))
            y_pos += line_height
    
    # 続行ボタン
    continue_button_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
    pygame.draw.rect(screen, (100, 150, 255), continue_button_rect)
    pygame.draw.rect(screen, (50, 100, 200), continue_button_rect, 3)
    
    button_font = get_japanese_font(24)
    button_text = button_font.render("続行", True, (255, 255, 255))
    button_text_rect = button_text.get_rect(center=continue_button_rect.center)
    screen.blit(button_text, button_text_rect)
                        
    pygame.display.flip()
    
    # ボタンクリック待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if continue_button_rect.collidepoint(event.pos):
                    waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    waiting = False
        pygame.time.Clock().tick(30)

def show_graph_analysis(screen, font):
    """
    グラフ分析画面を表示
    """
    global learning_history, qtable
    
    try:
        # from ai_learning import visualize_learning_results
        # visualize_learning_results(learning_history, len(qtable))
        # 一時的にコメントアウト
        pass
    except Exception as e:
        # グラフ表示でエラーが発生した場合の代替表示
        screen.fill((240, 248, 255))
        
        title_font = get_japanese_font(32)
        title_surface = title_font.render("📈 グラフ分析", True, (50, 50, 50))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 40))
        screen.blit(title_surface, title_rect)
        
        small_font = get_japanese_font(20)
        y_pos = 120
        line_height = 25
        
        messages = [
            "グラフ分析機能は現在利用できません。",
            "",
            "代替機能として統計情報を表示します。",
            "",
            f"Qテーブルサイズ: {len(qtable)}",
            f"学習履歴件数: {len(learning_history.history)}",
        ]
        
        for line in messages:
            text_surface = small_font.render(line, True, (50, 50, 50))
            screen.blit(text_surface, (50, y_pos))
            y_pos += line_height
        
        # 続行ボタン
        continue_button_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
        pygame.draw.rect(screen, (100, 150, 255), continue_button_rect)
        pygame.draw.rect(screen, (50, 100, 200), continue_button_rect, 3)
        
        button_font = get_japanese_font(24)
        button_text = button_font.render("続行", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=continue_button_rect.center)
        screen.blit(button_text, button_text_rect)
        
        pygame.display.flip()
        
        # ボタンクリック待ち
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if continue_button_rect.collidepoint(event.pos):
                        waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        waiting = False
            pygame.time.Clock().tick(30)

def show_recommendations_screen(screen, font):
    """
    推奨事項画面を表示
    """
    global ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, qtable
    
    total_games = ai_win_count + ai_lose_count + ai_draw_count
    win_rate = (ai_win_count / total_games) * 100 if total_games > 0 else 0
    avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
    learning_efficiency = ai_learn_count / total_games if total_games > 0 else 0
    
    screen.fill((240, 248, 255))
    
    # タイトル
    title_font = get_japanese_font(32)
    title_surface = title_font.render("💡 推奨事項", True, (50, 50, 50))
    title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 40))
    screen.blit(title_surface, title_rect)
    
    # 推奨事項を生成
    small_font = get_japanese_font(20)
    y_pos = 100
    line_height = 25
    
    recommendations = [
        f"📊 現在の状況:",
        f"  勝率: {win_rate:.1f}%",
        f"  平均報酬: {avg_reward:.2f}",
        f"  学習効率: {learning_efficiency:.1f}",
        f"  Qテーブルサイズ: {len(qtable)}",
        "",
        f"💡 推奨事項:",
    ]
    
    # 勝率に基づく推奨
    if win_rate < 60:
        recommendations.extend([
            f"  • 学習ゲーム数を増やす (現在: {total_games}ゲーム)",
            "  • 学習率を調整する",
            "  • より多くの状況での学習を促進"
        ])
    
    # 報酬に基づく推奨
    if avg_reward < 2:
        recommendations.extend([
            "  • 報酬設計を見直す",
            "  • 探索率を調整する",
            "  • 学習パラメータの最適化"
        ])
    
    # Qテーブルサイズに基づく推奨
    if len(qtable) < 2000:
        recommendations.extend([
            "  • より多くの状況での学習を促進",
            "  • 学習ゲーム数を増やす",
            "  • 多様な戦略の学習"
        ])
    
    # 学習効率に基づく推奨
    if learning_efficiency < 20:
        recommendations.extend([
            "  • 学習頻度を上げる",
            "  • 学習パラメータの調整",
            "  • より効率的な学習方法の採用"
        ])
    
    # 高成績の場合の推奨
    if win_rate > 70:
        recommendations.extend([
            "  • 人間との対戦で実力を確認",
            "  • 学習データを保存",
            "  • より高度な戦略の学習"
        ])
    
    # 結果を描画
    for line in recommendations:
        if line.strip() == "":
            y_pos += line_height // 2
        else:
            text_surface = small_font.render(line, True, (50, 50, 50))
            screen.blit(text_surface, (50, y_pos))
            y_pos += line_height
    
    # 続行ボタン
    continue_button_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
    pygame.draw.rect(screen, (100, 150, 255), continue_button_rect)
    pygame.draw.rect(screen, (50, 100, 200), continue_button_rect, 3)
    
    button_font = get_japanese_font(24)
    button_text = button_font.render("続行", True, (255, 255, 255))
    button_text_rect = button_text.get_rect(center=continue_button_rect.center)
    screen.blit(button_text, button_text_rect)
    
    pygame.display.flip()
    
    # ボタンクリック待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if continue_button_rect.collidepoint(event.pos):
                    waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    waiting = False
        pygame.time.Clock().tick(30)

def run_evaluation_improvement_mode(screen, font):
    """
    総合評価改善モード（クラッシュ対策版）
    """
    global qtable, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward
    
    try:
        # 戦略選択画面
        strategy = show_strategy_selection_screen(screen, font)
        if not strategy:
            return
        
        # ゲーム数選択
        num_games = show_games_selection_screen(screen, font)
        if not num_games:
            return
        
        # 学習実行前の確認
        show_learning_progress_screen(screen, font, "評価改善学習", "戦略的学習を開始しています...")
        
        try:
            # from ai_learning import enhanced_learning_strategy
            from game_logic import OthelloGame
            
            # 新しいゲームインスタンスを作成
            game = OthelloGame()
            
            # 学習実行（エラーハンドリング付き）
            print(f"🎯 学習開始: {strategy}戦略, {num_games}ゲーム")
            
            # ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward = enhanced_learning_strategy(
            #     game, qtable, num_games, strategy
            # )
            # 代わりに通常の自己対戦を実行
            ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = enhanced_ai_self_play(
                game, qtable, num_games, learn=True, draw_mode=draw_mode, screen=screen, font=font
            )
            
            # 平均報酬を計算（既に計算済みの場合は不要）
            # ai_avg_reward = ai_total_reward / ai_learn_count if ai_learn_count > 0 else 0
            
            # 学習履歴に記録
            try:
                learning_history.add_record(
                    num_games, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count,
                    ai_total_reward, ai_avg_reward, len(qtable), game_type="evaluation_improvement"
                )
            except Exception as record_error:
                print(f"⚠️ 学習履歴記録エラー: {record_error}")
            
            # 完了画面を表示
            show_learning_complete_screen(screen, font, f"評価改善学習 ({strategy})", 
                                        ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward)
            
        except ImportError as import_error:
            error_msg = f"必要なモジュールの読み込みに失敗しました: {str(import_error)}"
            show_learning_error_screen(screen, font, error_msg)
        except Exception as learning_error:
            error_msg = f"学習中にエラーが発生しました: {str(learning_error)}"
            print(f"❌ {error_msg}")
            show_learning_error_screen(screen, font, error_msg)
    
    except Exception as mode_error:
        error_msg = f"評価改善モードでエラーが発生しました: {str(mode_error)}"
        print(f"❌ {error_msg}")
        show_learning_error_screen(screen, font, error_msg)

def show_strategy_selection_screen(screen, font):
    """
    戦略選択画面
    """
    running = True
    
    while running:
        screen.fill((240, 248, 255))
        
        # タイトル
        title_font = get_japanese_font(32)
        title_surface = title_font.render("📈 戦略選択", True, (50, 50, 50))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 80))
        screen.blit(title_surface, title_rect)
        
        # 説明
        desc_font = get_japanese_font(20)
        desc_surface = desc_font.render("総合評価改善のための戦略を選択してください", True, (80, 80, 80))
        desc_rect = desc_surface.get_rect(center=(WINDOW_WIDTH//2, 120))
        screen.blit(desc_surface, desc_rect)
        
        # ボタン
        button_width = 300
        button_height = 80
        button_x = (WINDOW_WIDTH - button_width) // 2
        button_y_start = 180
        button_spacing = 100
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
        
        # バランス型戦略
        balanced_rect = pygame.Rect(button_x, button_y_start, button_width, button_height)
        if draw_enhanced_button(screen, button_x, button_y_start, button_width, button_height,
                              "バランス型", "⚖️", "攻撃と防御のバランスを重視した戦略",
                              (100, 150, 255, 150), (150, 200, 255, 150), mouse_pos, mouse_down, font, 0):
            return "balanced"
        
        # 攻撃的戦略
        aggressive_rect = pygame.Rect(button_x, button_y_start + button_spacing, button_width, button_height)
        if draw_enhanced_button(screen, button_x, button_y_start + button_spacing, button_width, button_height,
                              "攻撃的", "⚔️", "積極的な攻撃を重視した戦略",
                              (255, 100, 100, 150), (255, 130, 130, 150), mouse_pos, mouse_down, font, 0):
            return "aggressive"
        
        # 防御的戦略
        defensive_rect = pygame.Rect(button_x, button_y_start + button_spacing * 2, button_width, button_height)
        if draw_enhanced_button(screen, button_x, button_y_start + button_spacing * 2, button_width, button_height,
                              "防御的", "🛡️", "慎重な防御を重視した戦略",
                              (100, 255, 100, 150), (130, 255, 130, 150), mouse_pos, mouse_down, font, 0):
            return "defensive"
        
        # 戻るボタン
        back_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
        if draw_enhanced_button(screen, back_rect.x, back_rect.y, back_rect.width, back_rect.height,
                              "戻る", "←", "メインメニューに戻ります",
                              (180, 180, 180, 150), (220, 220, 220, 150), mouse_pos, mouse_down, font, 0):
            return None
        
        # マウスクリック判定
        if mouse_down:
            if balanced_rect.collidepoint(mouse_pos):
                return "balanced"
            elif aggressive_rect.collidepoint(mouse_pos):
                return "aggressive"
            elif defensive_rect.collidepoint(mouse_pos):
                return "defensive"
            elif back_rect.collidepoint(mouse_pos):
                return None
    
    pygame.display.flip()
    pygame.time.Clock().tick(30)
    
    return None

def show_games_selection_screen(screen, font):
    """
    ゲーム数選択画面
    """
    running = True
    selected_games = 200  # デフォルト値
    
    while running:
        screen.fill((240, 248, 255))
        
        # タイトル
        title_font = get_japanese_font(32)
        title_surface = title_font.render("🎮 ゲーム数選択", True, (50, 50, 50))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 80))
        screen.blit(title_surface, title_rect)
        
        # 説明
        desc_font = get_japanese_font(20)
        desc_surface = desc_font.render("学習するゲーム数を選択してください", True, (80, 80, 80))
        desc_rect = desc_surface.get_rect(center=(WINDOW_WIDTH//2, 120))
        screen.blit(desc_surface, desc_rect)
        
        # 選択されたゲーム数表示
        games_font = get_japanese_font(28)
        games_surface = games_font.render(f"選択: {selected_games}ゲーム", True, (50, 50, 50))
        games_rect = games_surface.get_rect(center=(WINDOW_WIDTH//2, 200))
        screen.blit(games_surface, games_rect)
        
        # ボタン
        button_width = 200
        button_height = 60
        button_x = (WINDOW_WIDTH - button_width * 2 - 50) // 2
        button_y = 280
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
        
        # ゲーム数選択ボタン
        if draw_enhanced_button(screen, button_x, button_y, button_width, button_height,
                              "100ゲーム", "📊", "軽量な学習",
                              (100, 150, 255, 150), (150, 200, 255, 150), mouse_pos, mouse_down, font, 0):
            selected_games = 100
        
        if draw_enhanced_button(screen, button_x + button_width + 50, button_y, button_width, button_height,
                              "200ゲーム", "📈", "標準的な学習",
                              (255, 150, 100, 150), (255, 180, 130, 150), mouse_pos, mouse_down, font, 0):
            selected_games = 200
        
        if draw_enhanced_button(screen, button_x, button_y + 80, button_width, button_height,
                              "300ゲーム", "🚀", "集中的な学習",
                              (255, 100, 255, 150), (255, 130, 255, 150), mouse_pos, mouse_down, font, 0):
            selected_games = 300
        
        if draw_enhanced_button(screen, button_x + button_width + 50, button_y + 80, button_width, button_height,
                              "500ゲーム", "🔥", "徹底的な学習",
                              (255, 200, 100, 150), (255, 220, 130, 150), mouse_pos, mouse_down, font, 0):
            selected_games = 500
        
        # 開始ボタン
        start_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-100, 240, 60)
        if draw_enhanced_button(screen, start_rect.x, start_rect.y, start_rect.width, start_rect.height,
                              "学習開始", "▶️", f"{selected_games}ゲームで学習を開始します",
                              (100, 255, 100, 150), (130, 255, 130, 150), mouse_pos, mouse_down, font, 0):
            return selected_games
        
        # 戻るボタン
        back_rect = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
        if draw_enhanced_button(screen, back_rect.x, back_rect.y, back_rect.width, back_rect.height,
                              "戻る", "←", "戦略選択に戻ります",
                              (180, 180, 180, 150), (220, 220, 220, 150), mouse_pos, mouse_down, font, 0):
            return None
        
        # マウスクリック判定
        if mouse_down:
            if start_rect.collidepoint(mouse_pos):
                return selected_games
            elif back_rect.collidepoint(mouse_pos):
                return None
        
        pygame.display.flip()
        pygame.time.Clock().tick(30)
    
    return None

def run_enhanced_learning_mode(screen, font):
    """強化学習モードの実行ラッパー"""
    # ゲーム数選択画面を表示（仮実装: 200回固定）
    num_games = 200
    mode_name = "強化学習"
    execute_enhanced_learning(screen, font, num_games, mode_name)

def execute_pretrain_learning(screen, font, num_games):
    """事前訓練（AI同士の自己対戦）を実行"""
    global qtable, learning_history, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward, draw_mode
    print(f"🤖 事前訓練開始: {num_games}ゲーム")
    show_learning_progress_screen(screen, font, "事前訓練中...", "準備中...")
    game = OthelloGame()
    try:
        ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_total_reward, ai_avg_reward = enhanced_ai_self_play(
            game, qtable, num_games, learn=True, draw_mode=draw_mode, screen=screen, font=font
        )
        learning_history.add_record(
            game_count=num_games,
            ai_learn_count=ai_learn_count,
            ai_win_count=ai_win_count,
            ai_lose_count=ai_lose_count,
            ai_draw_count=ai_draw_count,
            ai_total_reward=ai_total_reward,
            ai_avg_reward=ai_avg_reward,
            qtable_size=len(qtable),
            game_type="ai_vs_ai"
        )
        save_qtable(qtable)
        show_learning_complete_screen(screen, font, "事前訓練", ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward)
    except Exception as e:
        print(f"❌ 事前訓練エラー: {e}")
        show_learning_error_screen(screen, font, str(e))

if __name__ == "__main__":
    main_loop() 