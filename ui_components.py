import pygame
from constants import *
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

def get_japanese_font(size):
    try:
        return pygame.font.Font("msgothic.ttc", size)
    except:
        return pygame.font.SysFont("msgothic", size)

def draw_board(screen, game_board, game):
    """盤面を描画"""
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

def draw_stones(screen, game_board, game):
    """石を描画"""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if game_board[row][col] != 0:
                x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                y = BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
                color = BLACK if game_board[row][col] == PLAYER_BLACK else WHITE
                pygame.draw.circle(screen, color, (x, y), SQUARE_SIZE // 2 - 5)
    
    # AIが最後に置いた石を赤い枠で囲む
    if game and game.last_ai_move:
        last_r, last_c = game.last_ai_move
        if game_board[last_r][last_c] != 0:  # 石が存在する場合
            x = BOARD_OFFSET_X + last_c * SQUARE_SIZE
            y = BOARD_OFFSET_Y + last_r * SQUARE_SIZE
            pygame.draw.rect(screen, (255, 0, 0), (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)

def draw_current_player_indicator(screen, current_player):
    """現在のプレイヤー表示"""
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
    text_surface = get_japanese_font(20).render(f"{player_text}の番", True, (0, 0, 0))
    screen.blit(text_surface, (indicator_x + 45, indicator_y + 10))

def display_error_message(screen, message):
    """エラーメッセージを表示"""
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

def display_game_result(screen, result_message, ai_reward=0, black_score=0, white_score=0, ai_learn_count=0):
    """ゲーム結果を表示"""
    overlay = pygame.Surface((BOARD_PIXEL_SIZE, BOARD_PIXEL_SIZE))
    overlay.set_alpha(180)
    overlay.fill((255, 255, 255))
    screen.blit(overlay, (BOARD_OFFSET_X, BOARD_OFFSET_Y))
    
    # 結果メッセージ
    result_font = get_japanese_font(36)
    result_surface = result_font.render(result_message, True, (255, 0, 0))
    result_rect = result_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2 - 80))
    screen.blit(result_surface, result_rect)
    
    # スコア表示
    score_font = get_japanese_font(24)
    score_text = f"黒: {black_score}  白: {white_score}"
    score_surface = score_font.render(score_text, True, (0, 0, 0))
    score_rect = score_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2 - 40))
    screen.blit(score_surface, score_rect)
    
    # AI学習データ表示
    if ai_learn_count > 0:
        learn_font = get_japanese_font(20)
        learn_text = f"AI学習回数: {ai_learn_count}"
        learn_surface = learn_font.render(learn_text, True, (0, 0, 255))
        learn_rect = learn_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2))
        screen.blit(learn_surface, learn_rect)
    
    # AI報酬表示
    if ai_reward != 0:
        reward_font = get_japanese_font(20)
        reward_text = f"AI最終報酬: {ai_reward}"
        reward_surface = reward_font.render(reward_text, True, (0, 0, 255))
        reward_rect = reward_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2 + 30))
        screen.blit(reward_surface, reward_rect)
    
    # 次の対戦への案内
    next_font = get_japanese_font(18)
    next_text = "盤面をクリックして次の対戦へ"
    next_surface = next_font.render(next_text, True, (0, 0, 0))
    next_rect = next_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2 + 70))
    screen.blit(next_surface, next_rect)

def display_notice_message(screen, message, start_time, duration=1000):
    """注意メッセージを表示"""
    current_time = pygame.time.get_ticks()
    if current_time - start_time > duration:
        return False
    
    overlay = pygame.Surface((BOARD_PIXEL_SIZE, BOARD_PIXEL_SIZE))
    overlay.set_alpha(150)
    overlay.fill((255, 255, 255))
    screen.blit(overlay, (BOARD_OFFSET_X, BOARD_OFFSET_Y))
    
    notice_font = get_japanese_font(26)
    text_surface = notice_font.render(message, True, RED)
    text_rect = text_surface.get_rect(center=(BOARD_OFFSET_X + BOARD_PIXEL_SIZE // 2, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE // 2))
    screen.blit(text_surface, text_rect)
    
    return True

def display_message(screen, message, is_error=False):
    """画面下部にメッセージを表示"""
    color = RED if is_error else BLACK
    max_width = WINDOW_WIDTH - 40
    lines = []
    words = message.split(' ')
    line = ''
    for word in words:
        test_line = line + (' ' if line else '') + word
        test_surface = get_japanese_font(36).render(test_line, True, color)
        if test_surface.get_width() > max_width:
            if line:
                lines.append(line)
            line = word
        else:
            line = test_line
    if line:
        lines.append(line)
    
    for i, l in enumerate(lines):
        text_surface = get_japanese_font(36).render(l, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 40 + i * 36))
        screen.blit(text_surface, text_rect)

def display_score(screen, black_score, white_score):
    """スコアを表示"""
    black_text = get_japanese_font(24).render(f"黒: {black_score}", True, BLACK)
    white_text = get_japanese_font(24).render(f"白: {white_score}", True, BLACK)
    screen.blit(black_text, (BOARD_OFFSET_X, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 10))
    screen.blit(white_text, (WINDOW_WIDTH - BOARD_OFFSET_X - white_text.get_width(), BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 10))

def display_ai_reward(screen, reward):
    """AIの最新報酬を表示"""
    reward_text = get_japanese_font(20).render(f"AI報酬: {reward}", True, BLACK)
    screen.blit(reward_text, (BOARD_OFFSET_X + 10, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 35))

def draw_progress_bar(screen, current, total, x, y, width, height):
    """プログレスバーを描画"""
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height))
    pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height), 2)
    
    if total > 0:
        progress_width = int((current / total) * (width - 4))
        if progress_width > 0:
            pygame.draw.rect(screen, (0, 255, 0), (x + 2, y + 2, progress_width, height - 4))
    
    progress_text = f"{current}/{total}"
    text_surface = get_japanese_font(36).render(progress_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

def draw_learn_count(screen, font, ai_learn_count):
    """学習回数を表示"""
    text = font.render(f"AI学習回数: {ai_learn_count}", True, (0,0,0))
    screen.blit(text, (20, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 60))

def draw_pretrain_count(screen, font, pretrain_now, pretrain_total):
    """AI訓練回数を表示"""
    text = font.render(f"AI訓練: {pretrain_now}/{pretrain_total}", True, (0,0,0))
    screen.blit(text, (20, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 85))

def draw_game_count(screen, font, game_count):
    """対戦回数を表示"""
    text = font.render(f"対戦回数: {game_count}", True, (0,0,0))
    y = BOARD_OFFSET_Y // 2 - text.get_height() // 2
    screen.blit(text, (20, y))

def draw_ai_stats(screen, font, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward):
    """AI統計情報を表示"""
    # AI戦績
    stats_font = get_japanese_font(18)
    win_text = stats_font.render(f"AI勝利: {ai_win_count}", True, (0, 100, 0))
    lose_text = stats_font.render(f"AI敗北: {ai_lose_count}", True, (150, 0, 0))
    draw_text = stats_font.render(f"引き分け: {ai_draw_count}", True, (100, 100, 100))
    
    screen.blit(win_text, (20, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 110))
    screen.blit(lose_text, (20, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 130))
    screen.blit(draw_text, (20, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 150))
    
    # AI平均報酬
    if ai_avg_reward != 0:
        avg_reward_text = stats_font.render(f"AI平均報酬: {ai_avg_reward:.2f}", True, (0, 0, 150))
        screen.blit(avg_reward_text, (20, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 170))

def draw_move_count(screen, font, move_count, last_move_count):
    """手数を表示"""
    if move_count != last_move_count:
        text = font.render(f"手数: {move_count}", True, BLACK)
        x = BOARD_OFFSET_X + BOARD_PIXEL_SIZE - text.get_width()
        y = BOARD_OFFSET_Y // 2 - text.get_height() // 2
        screen.blit(text, (x, y))
        return move_count
    return last_move_count

def draw_reset_button(screen, font, mouse_pos, mouse_down):
    """リセットボタンを描画"""
    x = WINDOW_WIDTH//2 - BUTTON_WIDTH//2
    y = BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 120  # y位置を90から120に変更
    rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    is_hover = rect.collidepoint(mouse_pos)
    color = (180, 180, 255) if is_hover else (200, 200, 200)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    text_surface = font.render("リセット", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    
    return is_hover and mouse_down

def draw_back_button(screen, font, mouse_pos, mouse_down):
    """戻るボタンを描画"""
    x = WINDOW_WIDTH//2 + BUTTON_WIDTH//2 + 20
    y = BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 120  # y位置を90から120に変更
    rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    is_hover = rect.collidepoint(mouse_pos)
    color = (180, 180, 255) if is_hover else (200, 200, 200)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    text_surface = font.render("戻る", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    
    return is_hover and mouse_down

def draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress=True):
    """学習進捗グラフを描画。ON/OFFボタンのRectを返す"""
    graph_area_width = 400
    pygame.draw.rect(screen, (245, 245, 245), (0, 0, graph_area_width, WINDOW_HEIGHT))
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, graph_area_width, WINDOW_HEIGHT), 2)

    # ON/OFFボタン
    button_font = get_japanese_font(13)
    btn_text = "進捗表示OFF" if show_learning_progress else "進捗表示ON"
    btn_color = (180, 220, 180) if show_learning_progress else (220, 180, 180)
    btn_rect = pygame.Rect(280, 10, 100, 28)
    pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)
    pygame.draw.rect(screen, (100, 100, 100), btn_rect, 2, border_radius=8)
    text_surf = button_font.render(btn_text, True, (0, 0, 0))
    screen.blit(text_surf, (btn_rect.x + 10, btn_rect.y + 5))

    if not show_learning_progress:
        return btn_rect

    # --- 以降は従来の進捗描画 ---
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
    progress_width = graph_area_width - 20
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
            graph_width = graph_area_width - 20
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
        # データが1件以下の場合でも前向きなメッセージを表示
        debug_font = get_japanese_font(12)
        if len(learning_history.history) == 0:
            debug_text = debug_font.render("学習データがありません。対戦や訓練を行うとここに進捗が表示されます。", True, (100, 100, 100))
        else:
            debug_text = debug_font.render("データが少ないですが、学習は進行中です。", True, (100, 100, 100))
        screen.blit(debug_text, (10, graph_start_y))
        graph_start_y += 20
    
    # 平均報酬の推移グラフ
    if len(learning_history.history) > 1:
        avg_rewards = learning_history.get_avg_reward_history()
        if len(avg_rewards) > 1:
            graph_width = graph_area_width - 20
            graph_height = 60
            graph_x = 10
            graph_y = graph_start_y
            
            # グラフ背景
            pygame.draw.rect(screen, (255, 255, 255), (graph_x, graph_y, graph_width, graph_height))
            pygame.draw.rect(screen, (100, 100, 100), (graph_x, graph_y, graph_width, graph_height), 1)
            
            # グリッド線を描画
            grid_font = get_japanese_font(8)
            max_reward = max(avg_rewards) if avg_rewards else 1
            if max_reward == 0:
                max_reward = 1  # ゼロ除算を防ぐ
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

    # 最後にボタンのRectを返す
    return btn_rect

def draw_battle_history_list(screen, learning_history, font):
    # 対戦履歴リストを表示
    screen.fill((230, 240, 255))
    title = font.render("対戦履歴一覧", True, (30, 30, 60))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 30))
    history_font = get_japanese_font(18)
    y_offset = 100
    
    if learning_history.history:
        for rec in list(learning_history.history)[-15:][::-1]:
            text = f"{rec['timestamp'][:19]}  黒:{rec['black_score']} 白:{rec['white_score']} 勝率:{rec['win_rate']:.1f}% 平均報酬:{rec['ai_avg_reward']:.2f}"
            text_surface = history_font.render(text, True, (0, 0, 0))
            screen.blit(text_surface, (50, y_offset))
            y_offset += 28
    else:
        no_data_text = history_font.render("対戦記録がありません", True, (100, 100, 100))
        screen.blit(no_data_text, (50, y_offset))
    
    # 戻るボタン
    back_button = pygame.Rect(WINDOW_WIDTH//2-100, WINDOW_HEIGHT-80, 200, 50)
    pygame.draw.rect(screen, (200, 200, 200), back_button)
    back_text = history_font.render("戻る", True, (0, 0, 0))
    screen.blit(back_text, (back_button.x + 70, back_button.y + 10))

def calculate_ai_level(win_rate, avg_reward, learn_count, qtable_size):
    """AIレベルを計算"""
    level = 1
    
    if win_rate >= 80:
        level += 3
    elif win_rate >= 60:
        level += 2
    elif win_rate >= 40:
        level += 1
    
    if avg_reward >= 50:
        level += 2
    elif avg_reward >= 20:
        level += 1
    
    if learn_count >= 1000:
        level += 2
    elif learn_count >= 500:
        level += 1
    
    if qtable_size >= 1000:
        level += 2
    elif qtable_size >= 500:
        level += 1
    
    return min(10, max(1, level))

def get_level_description(level):
    """AIレベルの説明を取得"""
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

def draw_enhanced_button(screen, x, y, width, height, text, icon, description, color, hover_color, mouse_pos, mouse_down, font, animation_time):
    """強化されたボタンを描画（半透明、説明は下のみ）"""
    rect = pygame.Rect(x, y, width, height)
    is_hover = rect.collidepoint(mouse_pos)
    
    # ボタン背景（半透明）
    button_color = hover_color if is_hover else color
    pygame.draw.rect(screen, button_color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
    
    # アイコンとテキスト
    icon_text = f"{icon} {text}"
    text_surface = font.render(icon_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    
    # 説明テキスト（ボタンの下に表示）
    if is_hover:
        desc_font = get_japanese_font(14)
        desc_surface = desc_font.render(description, True, (255, 255, 255))
        desc_rect = desc_surface.get_rect(center=(rect.centerx, rect.bottom + 15))
        screen.blit(desc_surface, desc_rect)
    
    return is_hover and mouse_down

def draw_gradient_background(screen, animation_time):
    """オセロ盤面の背景を描画"""
    # オセロ盤の基本色（緑）
    board_color = (0, 128, 0)
    screen.fill(board_color)
    
    # 盤面のグリッド線
    grid_color = (0, 100, 0)
    grid_width = 3
    
    # 縦線
    for i in range(BOARD_SIZE + 1):
        x = BOARD_OFFSET_X + i * SQUARE_SIZE
        pygame.draw.line(screen, grid_color, (x, BOARD_OFFSET_Y), 
                        (x, BOARD_OFFSET_Y + BOARD_PIXEL_SIZE), grid_width)
    
    # 横線
    for i in range(BOARD_SIZE + 1):
        y = BOARD_OFFSET_Y + i * SQUARE_SIZE
        pygame.draw.line(screen, grid_color, (BOARD_OFFSET_X, y), 
                        (BOARD_OFFSET_X + BOARD_PIXEL_SIZE, y), grid_width)

def draw_decorative_elements(screen, animation_time):
    """装飾要素を描画"""
    # 石の装飾（アニメーション付き）
    for i in range(5):
        x = 50 + i * 100
        y = 150 + int(20 * math.sin(animation_time * 2 * math.pi + i))
        radius = 15 + int(5 * math.sin(animation_time * 2 * math.pi + i * 0.5))
        color = (255, 255, 255) if i % 2 == 0 else (0, 0, 0)
        pygame.draw.circle(screen, color, (x, y), radius)

def draw_quick_stats(screen, animation_time, ai_learn_count=0, game_count=0):
    """統計情報を描画"""
    # 簡易統計表示
    stats_font = get_japanese_font(16)
    stats_text = f"学習回数: {ai_learn_count} | 対戦回数: {game_count}"
    stats_surface = stats_font.render(stats_text, True, (255, 255, 255))
    screen.blit(stats_surface, (20, WINDOW_HEIGHT - 40))

def draw_learning_data_screen(screen, font, learning_history, qtable, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, show_learning_progress=True):
    """学習データ管理画面を描画 + AI詳細統計・グラフ"""
    screen.fill(WHITE)
    
    # タイトル
    title = font.render("学習データ管理・AI詳細", True, (30, 30, 60))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 30))

    # --- AI詳細統計エリア ---
    stats_font = get_japanese_font(22)
    small_font = get_japanese_font(16)
    x0, y0 = 60, 90
    line_h = 32
    qtable_size = len(qtable)
    total_games = ai_win_count + ai_lose_count + ai_draw_count
    win_rate = (ai_win_count / total_games * 100) if total_games > 0 else 0
    ai_level = calculate_ai_level(win_rate, ai_avg_reward, ai_learn_count, qtable_size)
    level_desc = get_level_description(ai_level)

    stats = [
        f"学習回数: {ai_learn_count}",
        f"勝ち: {ai_win_count}  負け: {ai_lose_count}  引き分け: {ai_draw_count}",
        f"勝率: {win_rate:.1f}%",
        f"Qテーブルサイズ: {qtable_size}",
        f"AIレベル: {ai_level}（{level_desc}）",
        f"平均報酬: {ai_avg_reward:.2f}"
    ]
    for i, text in enumerate(stats):
        stat_surf = stats_font.render(text, True, (0, 0, 0))
        screen.blit(stat_surf, (x0, y0 + i * line_h))

    # --- 勝敗比率円グラフ ---
    cx, cy, r = 420, 140, 48
    total = ai_win_count + ai_lose_count + ai_draw_count
    if total > 0:
        start_angle = 0
        for count, color in zip([ai_win_count, ai_lose_count, ai_draw_count], [(0,180,0), (200,0,0), (120,120,120)]):
            if count > 0:
                end_angle = start_angle + 360 * count / total
                pygame.draw.arc(screen, color, (cx-r, cy-r, r*2, r*2),
                                math.radians(start_angle), math.radians(end_angle), r)
                start_angle = end_angle
        # 円の枠
        pygame.draw.circle(screen, (80,80,80), (cx,cy), r, 2)
        # ラベル
        small = get_japanese_font(13)
        screen.blit(small.render("勝", True, (0,180,0)), (cx+r+8, cy-18))
        screen.blit(small.render("負", True, (200,0,0)), (cx+r+8, cy+2))
        screen.blit(small.render("引", True, (120,120,120)), (cx+r+8, cy+22))
    else:
        small = get_japanese_font(13)
        screen.blit(small.render("データ不足", True, (120,120,120)), (cx-30, cy-8))

    # --- 勝率・平均報酬推移グラフ（学習進捗表示がONの場合のみ） ---
    if show_learning_progress:
        draw_learning_graphs(screen, learning_history, total_games, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress)

    # --- 既存のボタン配置 ---
    button_width = 300
    button_height = 60
    button_spacing = 80
    start_y = 350
    # 保存ボタン
    save_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y, button_width, button_height)
    pygame.draw.rect(screen, (100, 200, 100), save_button)
    pygame.draw.rect(screen, (50, 150, 50), save_button, 3)
    save_text = font.render("学習データを保存", True, BLACK)
    save_text_rect = save_text.get_rect(center=save_button.center)
    screen.blit(save_text, save_text_rect)
    # 新規作成ボタン
    new_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing, button_width, button_height)
    pygame.draw.rect(screen, (100, 150, 200), new_button)
    pygame.draw.rect(screen, (50, 100, 150), new_button, 3)
    new_text = font.render("新規学習データ作成", True, BLACK)
    new_text_rect = new_text.get_rect(center=new_button.center)
    screen.blit(new_text, new_text_rect)
    # 読み込みボタン
    load_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 2, button_width, button_height)
    pygame.draw.rect(screen, (200, 150, 100), load_button)
    pygame.draw.rect(screen, (150, 100, 50), load_button, 3)
    load_text = font.render("学習データを読み込み", True, BLACK)
    load_text_rect = load_text.get_rect(center=load_button.center)
    screen.blit(load_text, load_text_rect)
    # 削除ボタン
    delete_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 3, button_width, button_height)
    pygame.draw.rect(screen, (200, 100, 100), delete_button)
    pygame.draw.rect(screen, (150, 50, 50), delete_button, 3)
    delete_text = font.render("学習データを削除", True, BLACK)
    delete_text_rect = delete_text.get_rect(center=delete_button.center)
    screen.blit(delete_text, delete_text_rect)
    # 戻るボタン
    back_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 4, button_width, button_height)
    pygame.draw.rect(screen, (150, 150, 150), back_button)
    pygame.draw.rect(screen, (100, 100, 100), back_button, 3)
    back_text = font.render("戻る", True, BLACK)
    back_text_rect = back_text.get_rect(center=back_button.center)
    screen.blit(back_text, back_text_rect)
    # 説明文
    info_font = get_japanese_font(14)
    info_text = info_font.render("学習データの保存・読み込み・管理とAIの詳細情報を確認できます", True, (100, 100, 100))
    screen.blit(info_text, (WINDOW_WIDTH//2 - info_text.get_width()//2, start_y + button_spacing * 5 + 20))
    
    # 学習進捗表示のON/OFFボタン（学習進捗表示がOFFの場合は表示しない）
    progress_btn_rect = None
    if show_learning_progress:
        progress_btn_rect = pygame.Rect(20, 20, 200, 40)
        pygame.draw.rect(screen, (100, 100, 200), progress_btn_rect)
        pygame.draw.rect(screen, (50, 50, 150), progress_btn_rect, 2)
        progress_text = get_japanese_font(16).render("学習進捗: ON", True, BLACK)
        screen.blit(progress_text, (30, 30))
    
    return save_button, new_button, load_button, delete_button, back_button, progress_btn_rect

def draw_battle_history_screen(screen, font):
    """対戦記録画面を描画"""
    import main
    screen.fill((230, 240, 255))
    title = font.render("対戦記録", True, (30, 30, 60))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 30))
    
    # 簡易的な対戦記録表示
    history_font = get_japanese_font(18)
    y_offset = 100
    
    # 最新の対戦記録を表示
    if main.learning_history.history:
        latest = main.learning_history.history[-1]
        records = [
            f"最終対戦: {latest.get('timestamp', 'N/A')}",
            f"スコア: 黒{latest.get('black_score', 0)} - 白{latest.get('white_score', 0)}",
            f"勝率: {latest.get('win_rate', 0):.1f}%",
            f"平均報酬: {latest.get('ai_avg_reward', 0):.2f}"
        ]
        
        for record in records:
            text_surface = history_font.render(record, True, (0, 0, 0))
            screen.blit(text_surface, (50, y_offset))
            y_offset += 25
    else:
        no_data_text = history_font.render("対戦記録がありません", True, (100, 100, 100))
        screen.blit(no_data_text, (50, y_offset))
    
    # 戻るボタン
    back_button = pygame.Rect(WINDOW_WIDTH//2-100, WINDOW_HEIGHT-80, 200, 50)
    pygame.draw.rect(screen, (200, 200, 200), back_button)
    back_text = history_font.render("戻る", True, (0, 0, 0))
    screen.blit(back_text, (back_button.x + 70, back_button.y + 10)) 