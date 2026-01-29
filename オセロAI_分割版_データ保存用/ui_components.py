import pygame
from constants import *
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

def get_japanese_font(size):
    """
    日本語フォントを優先的に取得（Windows対応強化）
    """
    font_names = [
        "Meiryo", "Yu Gothic", "MS Gothic", "MS PGothic", "Yu Mincho", "MS Mincho",
        "Noto Sans CJK JP", "Noto Sans JP", "TakaoGothic", "TakaoPGothic", "VL Gothic",
        "IPAexGothic", "IPAexMincho", "Arial Unicode MS", "SimHei", "AppleGothic"
    ]
    for font_name in font_names:
        try:
            return pygame.font.SysFont(font_name, size)
        except Exception:
            continue
    # どの日本語フォントも見つからない場合はデフォルト
    return pygame.font.Font(None, size)

def get_emoji_font(size):
    """絵文字対応フォントを取得"""
    # Windows 10/11で絵文字を表示できるフォントを優先
    emoji_font_names = [
        "Segoe UI Emoji",  # Windows 10/11の絵文字フォント
        "Segoe UI Symbol",  # シンボルフォント
        "Noto Color Emoji",  # Google Noto絵文字フォント
        "Apple Color Emoji",  # macOS用（Windowsでは使用されない）
        "Yu Gothic",  # 日本語フォント（一部絵文字対応）
        "Yu Gothic UI",  # 日本語UIフォント
        "Meiryo",  # 日本語フォント
        "MS Gothic"  # 日本語フォント
    ]
    
    for font_name in emoji_font_names:
        try:
            return pygame.font.SysFont(font_name, size)
        except Exception:
            pass
    
    # フォールバック: 通常の日本語フォント
    return get_japanese_font(size)

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
    """現在のプレイヤー表示（右上のみ）"""
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
    # 白のスコアをオセロ盤の右下に表示
    screen.blit(white_text, (BOARD_OFFSET_X + BOARD_PIXEL_SIZE - white_text.get_width(), BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 10))

def display_ai_reward(screen, reward):
    """AIの最新報酬を表示（右側に配置）"""
    reward_text = get_japanese_font(20).render(f"AI報酬: {reward}", True, BLACK)
    screen.blit(reward_text, (WINDOW_WIDTH - 180, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 35))

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
    """AI学習回数を表示（左側に配置）"""
    text = font.render(f"AI学習回数: {ai_learn_count}", True, (0,0,0))
    screen.blit(text, (BOARD_OFFSET_X, BOARD_PIXEL_SIZE + BOARD_OFFSET_Y + 60))

def draw_reset_button(screen, font, mouse_pos, mouse_down):
    """リセットボタンを描画"""
    x = WINDOW_WIDTH//2 - BUTTON_WIDTH//2
    y = WINDOW_HEIGHT - BUTTON_HEIGHT - 20  # 画面下部から20px上
    rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    is_hover = rect.collidepoint(mouse_pos)
    color = (180, 180, 255) if is_hover else (200, 200, 200)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    # 絵文字とテキストを分けて表示
    emoji_font = get_emoji_font(16)
    text_font = get_japanese_font(16)
    
    # 絵文字を描画
    emoji_surface = emoji_font.render("🔄", True, (0, 0, 0))
    emoji_rect = emoji_surface.get_rect(center=(rect.centerx - 30, rect.centery))
    screen.blit(emoji_surface, emoji_rect)
    
    # テキストを描画
    text_surface = text_font.render("リセット", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(rect.centerx + 20, rect.centery))
    screen.blit(text_surface, text_rect)
    
    return is_hover and mouse_down

def draw_back_button(screen, font, mouse_pos, mouse_down):
    """戻るボタンを描画"""
    x = WINDOW_WIDTH//2 + BUTTON_WIDTH//2 + 20
    y = WINDOW_HEIGHT - BUTTON_HEIGHT - 20  # 画面下部から20px上
    rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    is_hover = rect.collidepoint(mouse_pos)
    color = (180, 180, 255) if is_hover else (200, 200, 200)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    # 絵文字とテキストを分けて表示
    emoji_font = get_emoji_font(16)
    text_font = get_japanese_font(16)
    
    # 絵文字を描画
    emoji_surface = emoji_font.render("🔙", True, (0, 0, 0))
    emoji_rect = emoji_surface.get_rect(center=(rect.centerx - 20, rect.centery))
    screen.blit(emoji_surface, emoji_rect)
    
    # テキストを描画
    text_surface = text_font.render("戻る", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(rect.centerx + 20, rect.centery))
    screen.blit(text_surface, text_rect)
    
    return is_hover and mouse_down

def draw_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress=True):
    """学習進捗グラフを描画。ON/OFFボタンのRectを返す"""
    # グラフエリアを左側に配置
    graph_area_width = GRAPH_AREA_WIDTH
    graph_x = GRAPH_OFFSET_X
    graph_y = GRAPH_OFFSET_Y
    
    pygame.draw.rect(screen, (245, 245, 245), (graph_x, graph_y, graph_area_width, WINDOW_HEIGHT - graph_y))
    pygame.draw.rect(screen, (200, 200, 200), (graph_x, graph_y, graph_area_width, WINDOW_HEIGHT - graph_y), 2)

    # ON/OFFボタン
    button_font = get_japanese_font(12)  # フォントサイズを小さく
    btn_text = "進捗表示OFF" if show_learning_progress else "進捗表示ON"
    btn_color = (180, 220, 180) if show_learning_progress else (220, 180, 180)
    btn_rect = pygame.Rect(graph_x + graph_area_width - 100, graph_y + 10, 80, 25)  # ボタンサイズを小さく
    pygame.draw.rect(screen, btn_color, btn_rect, border_radius=6)
    pygame.draw.rect(screen, (100, 100, 100), btn_rect, 2, border_radius=6)
    text_surf = button_font.render(btn_text, True, (0, 0, 0))
    screen.blit(text_surf, (btn_rect.x + 5, btn_rect.y + 3))

    if not show_learning_progress:
        return btn_rect

    # --- 以降は従来の進捗描画 ---
    title_font = get_japanese_font(14)  # フォントサイズを小さく
    title_text = title_font.render("学習進捗", True, (0, 0, 0))
    screen.blit(title_text, (graph_x + 10, graph_y + 10))
    
    # 統計情報の表示（よりコンパクトに）
    stats_font = get_japanese_font(10)  # フォントサイズを小さく
    y_offset = graph_y + 30  # 開始位置を調整
    
    # ゲーム数
    game_text = stats_font.render(f"ゲーム数: {game_count}", True, (0, 0, 0))
    screen.blit(game_text, (graph_x + 10, y_offset))
    y_offset += 16  # 間隔を狭く
    
    # AI学習回数
    learn_text = stats_font.render(f"学習回数: {ai_learn_count}", True, (0, 0, 0))
    screen.blit(learn_text, (graph_x + 10, y_offset))
    y_offset += 16
    
    # 勝率
    win_rate = 0
    if ai_win_count + ai_lose_count + ai_draw_count > 0:
        win_rate = ai_win_count / (ai_win_count + ai_lose_count + ai_draw_count) * 100
        win_rate_text = stats_font.render(f"勝率: {win_rate:.1f}%", True, (0, 0, 0))
        screen.blit(win_rate_text, (graph_x + 10, y_offset))
        y_offset += 16
    
    # 平均報酬
    if ai_learn_count > 0:
        avg_reward_text = stats_font.render(f"平均報酬: {ai_avg_reward:.1f}", True, (0, 0, 0))
        screen.blit(avg_reward_text, (graph_x + 10, y_offset))
        y_offset += 16
    
    # Qテーブルサイズ
    qtable_size = len(qtable)
    qtable_text = stats_font.render(f"Qテーブル: {qtable_size}", True, (0, 0, 0))
    screen.blit(qtable_text, (graph_x + 10, y_offset))
    y_offset += 20
    
    # AI学習レベル
    ai_level = calculate_ai_level(win_rate, ai_avg_reward, ai_learn_count, qtable_size)
    level_description = get_level_description(ai_level)
    
    # レベル表示（目立つように）
    level_font = get_japanese_font(11)  # フォントサイズを小さく
    level_color = (255, 0, 0) if ai_level >= 8 else (255, 165, 0) if ai_level >= 6 else (0, 100, 200)
    level_text = level_font.render(f"AIレベル: {ai_level} ({level_description})", True, level_color)
    screen.blit(level_text, (graph_x + 10, y_offset))
    y_offset += 18
    
    # レベルプログレスバー
    progress_width = graph_area_width - 20
    progress_height = 10  # 高さを小さく
    progress_x = graph_x + 10
    progress_y = y_offset
    
    # プログレスバー背景
    pygame.draw.rect(screen, (200, 200, 200), (progress_x, progress_y, progress_width, progress_height))
    pygame.draw.rect(screen, (100, 100, 100), (progress_x, progress_y, progress_width, progress_height), 1)
    
    # レベルに応じたプログレス
    level_progress = (ai_level / 10) * progress_width
    if level_progress > 0:
        pygame.draw.rect(screen, level_color, (progress_x, progress_y, level_progress, progress_height))
    
    y_offset += 18
    
    # グラフエリアの開始位置を調整（より下に）
    graph_start_y = y_offset + 10
    
    # 簡易グラフ（勝率の推移）
    if len(learning_history.history) > 1:
        win_rates = learning_history.get_win_rate_history()
        if len(win_rates) > 1:
            graph_width = graph_area_width - 20
            graph_height = 60  # 高さを小さく
            graph_x_inner = graph_x + 10
            graph_y_inner = graph_start_y
            
            # グラフ背景
            pygame.draw.rect(screen, (255, 255, 255), (graph_x_inner, graph_y_inner, graph_width, graph_height))
            pygame.draw.rect(screen, (100, 100, 100), (graph_x_inner, graph_y_inner, graph_width, graph_height), 1)
            
            # グリッド線を描画
            grid_font = get_japanese_font(7)  # フォントサイズを小さく
            for i in range(5):
                # 水平グリッド線
                y_pos = graph_y_inner + (i * graph_height // 4)
                pygame.draw.line(screen, (220, 220, 220), (graph_x_inner, y_pos), (graph_x_inner + graph_width, y_pos), 1)
                
                # Y軸ラベル（勝率）
                label_value = 100 - (i * 25)
                label_text = grid_font.render(f"{label_value}%", True, (100, 100, 100))
                screen.blit(label_text, (graph_x_inner - 20, y_pos - 4))  # 位置を調整
            
            # 勝率グラフ
            if len(win_rates) > 1:
                points = []
                for i, rate in enumerate(win_rates):
                    x = graph_x_inner + (i / (len(win_rates) - 1)) * graph_width
                    y = graph_y_inner + graph_height - (rate / 100) * graph_height
                    points.append((x, y))
                
                if len(points) > 1:
                    # 太い線で折れ線グラフを描画
                    pygame.draw.lines(screen, (0, 100, 200), False, points, 2)  # 線を細く
                    
                    # 各データポイントを小さな円で表示
                    for point in points:
                        pygame.draw.circle(screen, (0, 100, 200), (int(point[0]), int(point[1])), 1)  # 円を小さく
                    
                    # 最新の点を強調
                    if points:
                        pygame.draw.circle(screen, (255, 0, 0), (int(points[-1][0]), int(points[-1][1])), 3)  # 円を小さく
                        pygame.draw.circle(screen, (255, 255, 255), (int(points[-1][0]), int(points[-1][1])), 1)
            
            # グラフラベル
            label_font = get_japanese_font(9)  # フォントサイズを小さく
            label_text = label_font.render("勝率推移", True, (0, 0, 0))
            screen.blit(label_text, (graph_x_inner, graph_y_inner - 12))
            
            # X軸ラベル（ゲーム数）
            if len(win_rates) > 1:
                x_label_text = grid_font.render(f"ゲーム数: {len(win_rates)}", True, (100, 100, 100))
                screen.blit(x_label_text, (graph_x_inner, graph_y_inner + graph_height + 3))
            
            graph_start_y += graph_height + 20
            
            # Qテーブル成長グラフを追加
            qtable_sizes = learning_history.get_qtable_size_history()
            if len(qtable_sizes) > 1:
                q_graph_width = graph_area_width - 20
                q_graph_height = 50  # 高さを小さく
                q_graph_x_inner = graph_x + 10
                q_graph_y_inner = graph_start_y
                
                # グラフ背景
                pygame.draw.rect(screen, (255, 255, 255), (q_graph_x_inner, q_graph_y_inner, q_graph_width, q_graph_height))
                pygame.draw.rect(screen, (100, 100, 100), (q_graph_x_inner, q_graph_y_inner, q_graph_width, q_graph_height), 1)
                
                # Qテーブルサイズグラフ
                points = []
                max_size = max(qtable_sizes) if qtable_sizes else 1
                for i, size in enumerate(qtable_sizes):
                    x = q_graph_x_inner + (i / (len(qtable_sizes) - 1)) * q_graph_width
                    y = q_graph_y_inner + q_graph_height - (size / max_size) * q_graph_height
                    points.append((x, y))
                
                # グリッド線を描画
                for i in range(5):
                    # 水平グリッド線
                    y_pos = q_graph_y_inner + (i * q_graph_height // 4)
                    pygame.draw.line(screen, (220, 220, 220), (q_graph_x_inner, y_pos), (q_graph_x_inner + q_graph_width, y_pos), 1)
                    
                    # Y軸ラベル（Qテーブルサイズ）
                    label_value = max_size - (i * max_size // 4)
                    label_text = grid_font.render(f"{label_value:,}", True, (100, 100, 100))
                    screen.blit(label_text, (q_graph_x_inner - 25, y_pos - 4))  # 位置を調整
                
                if len(points) > 1:
                    # 太い線で折れ線グラフを描画
                    pygame.draw.lines(screen, (100, 200, 100), False, points, 2)  # 緑色で線を細く
                    
                    # 各データポイントを小さな円で表示
                    for point in points:
                        pygame.draw.circle(screen, (100, 200, 100), (int(point[0]), int(point[1])), 1)  # 円を小さく
                    
                    # 最新の点を強調
                    if points:
                        pygame.draw.circle(screen, (255, 0, 0), (int(points[-1][0]), int(points[-1][1])), 3)  # 円を小さく
                        pygame.draw.circle(screen, (255, 255, 255), (int(points[-1][0]), int(points[-1][1])), 1)
                
                # グラフラベル
                label_font = get_japanese_font(9)  # フォントサイズを小さく
                label_text = label_font.render("Qテーブル成長", True, (0, 0, 0))
                screen.blit(label_text, (q_graph_x_inner, q_graph_y_inner - 12))
                
                # X軸ラベル（ゲーム数）
                if len(qtable_sizes) > 1:
                    x_label_text = grid_font.render(f"ゲーム数: {len(qtable_sizes)}", True, (100, 100, 100))
                    screen.blit(x_label_text, (q_graph_x_inner, q_graph_y_inner + q_graph_height + 3))
                
                graph_start_y += q_graph_height + 20
                
                # 平均報酬グラフを追加
                avg_rewards = learning_history.get_avg_reward_history()
                if len(avg_rewards) > 1:
                    r_graph_width = graph_area_width - 20
                    r_graph_height = 50  # 高さを小さく
                    r_graph_x_inner = graph_x + 10
                    r_graph_y_inner = graph_start_y
                    
                    # グラフ背景
                    pygame.draw.rect(screen, (255, 255, 255), (r_graph_x_inner, r_graph_y_inner, r_graph_width, r_graph_height))
                    pygame.draw.rect(screen, (100, 100, 100), (r_graph_x_inner, r_graph_y_inner, r_graph_width, r_graph_height), 1)
                    
                    # 平均報酬グラフ
                    r_points = []
                    max_reward = max(avg_rewards) if avg_rewards else 1
                    min_reward = min(avg_rewards) if avg_rewards else 0
                    reward_range = max_reward - min_reward if max_reward != min_reward else 1
                    
                    for i, reward in enumerate(avg_rewards):
                        x = r_graph_x_inner + (i / (len(avg_rewards) - 1)) * r_graph_width
                        y = r_graph_y_inner + r_graph_height - ((reward - min_reward) / reward_range) * r_graph_height
                        r_points.append((x, y))
                    
                    # グリッド線を描画
                    for i in range(5):
                        # 水平グリッド線
                        y_pos = r_graph_y_inner + (i * r_graph_height // 4)
                        pygame.draw.line(screen, (220, 220, 220), (r_graph_x_inner, y_pos), (r_graph_x_inner + r_graph_width, y_pos), 1)
                        
                        # Y軸ラベル（平均報酬）
                        label_value = max_reward - (i * reward_range // 4)
                        label_text = grid_font.render(f"{label_value:.1f}", True, (100, 100, 100))
                        screen.blit(label_text, (r_graph_x_inner - 20, y_pos - 4))
                    
                    if len(r_points) > 1:
                        # 太い線で折れ線グラフを描画
                        pygame.draw.lines(screen, (200, 100, 100), False, r_points, 2)  # 赤色で線を細く
                        
                        # 各データポイントを小さな円で表示
                        for point in r_points:
                            pygame.draw.circle(screen, (200, 100, 100), (int(point[0]), int(point[1])), 1)  # 円を小さく
                        
                        # 最新の点を強調
                        if r_points:
                            pygame.draw.circle(screen, (255, 0, 0), (int(r_points[-1][0]), int(r_points[-1][1])), 3)  # 円を小さく
                            pygame.draw.circle(screen, (255, 255, 255), (int(r_points[-1][0]), int(r_points[-1][1])), 1)
                        
                    # グラフラベル
                    label_font = get_japanese_font(9)  # フォントサイズを小さく
                    label_text = label_font.render("平均報酬推移", True, (0, 0, 0))
                    screen.blit(label_text, (r_graph_x_inner, r_graph_y_inner - 12))
                    
                    # X軸ラベル（ゲーム数）
                    if len(avg_rewards) > 1:
                        x_label_text = grid_font.render(f"ゲーム数: {len(avg_rewards)}", True, (100, 100, 100))
                        screen.blit(x_label_text, (r_graph_x_inner, r_graph_y_inner + r_graph_height + 3))

    return btn_rect

def draw_battle_history_list(screen, learning_history, font):
    # 対戦履歴リストを表示
    screen.fill((230, 240, 255))
    title = font.render("対戦履歴一覧", True, (30, 30, 60))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 30))
    history_font = get_emoji_font(14)  # 絵文字対応フォントを使用
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
    
    # アイコンとテキストを分けて表示
    emoji_font = get_emoji_font(20)  # 絵文字用フォント
    text_font = get_japanese_font(16)  # 日本語テキスト用フォント
    
    # アイコンを描画
    icon_surface = emoji_font.render(icon, True, (0, 0, 0))
    icon_rect = icon_surface.get_rect(center=(rect.centerx - 50, rect.centery))
    screen.blit(icon_surface, icon_rect)
    
    # テキストを描画
    text_surface = text_font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(rect.centerx + 20, rect.centery))
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
    
    # 盤面のグリッド線（中央に配置）
    grid_color = (0, 100, 0)
    grid_width = 3
    
    # 盤面の中央位置を計算
    board_center_x = WINDOW_WIDTH // 2
    board_center_y = WINDOW_HEIGHT // 2
    board_start_x = board_center_x - BOARD_PIXEL_SIZE // 2
    board_start_y = board_center_y - BOARD_PIXEL_SIZE // 2
    
    # 縦線
    for i in range(BOARD_SIZE + 1):
        x = board_start_x + i * SQUARE_SIZE
        pygame.draw.line(screen, grid_color, (x, board_start_y), 
                        (x, board_start_y + BOARD_PIXEL_SIZE), grid_width)
    
    # 横線
    for i in range(BOARD_SIZE + 1):
        y = board_start_y + i * SQUARE_SIZE
        pygame.draw.line(screen, grid_color, (board_start_x, y), 
                        (board_start_x + BOARD_PIXEL_SIZE, y), grid_width)

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
    """統計情報を描画（右側に表示）"""
    # 右側に統計情報を表示
    stats_panel_width = 300
    stats_panel_height = 80
    stats_panel_x = WINDOW_WIDTH - stats_panel_width - 20  # 右端から20px内側
    stats_panel_y = 20  # 上端から20px
    
    # パネル背景
    pygame.draw.rect(screen, (245, 245, 245), (stats_panel_x, stats_panel_y, stats_panel_width, stats_panel_height))
    pygame.draw.rect(screen, (200, 200, 200), (stats_panel_x, stats_panel_y, stats_panel_width, stats_panel_height), 2)
    
    # パネルタイトル
    title_font = get_japanese_font(14)
    title_text = title_font.render("📊 統計情報", True, (0, 0, 0))
    screen.blit(title_text, (stats_panel_x + 10, stats_panel_y + 5))
    
    # 統計情報
    stats_font = get_japanese_font(12)
    stats_text1 = stats_font.render(f"学習回数: {ai_learn_count:,}", True, (0, 0, 0))
    stats_text2 = stats_font.render(f"対戦回数: {game_count:,}", True, (0, 0, 0))
    
    screen.blit(stats_text1, (stats_panel_x + 10, stats_panel_y + 25))
    screen.blit(stats_text2, (stats_panel_x + 10, stats_panel_y + 45))

def draw_learning_data_screen(screen, font, learning_history, qtable, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, show_learning_progress=True):
    
    """学習データ管理画面を描画 + AI詳細統計・グラフ（大幅改善版）"""
    # グラデーション背景
    for y in range(WINDOW_HEIGHT):
        color_ratio = y / WINDOW_HEIGHT
        r = int(240 + (255 - 240) * color_ratio)
        g = int(245 + (255 - 245) * color_ratio)
        b = int(250 + (255 - 250) * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
    
    # タイトル（装飾付き）
    title_bg = pygame.Surface((WINDOW_WIDTH, 80))
    title_bg.set_alpha(180)
    title_bg.fill((100, 150, 255))
    screen.blit(title_bg, (0, 0))
    
    title = font.render("🤖 AI学習データ管理・詳細分析", True, (255, 255, 255))
    title_shadow = font.render("🤖 AI学習データ管理・詳細分析", True, (50, 50, 100))
    screen.blit(title_shadow, (WINDOW_WIDTH//2 - title.get_width()//2 + 2, 32))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 30))

    # --- AI詳細統計エリア（左側） ---
    stats_panel = pygame.Surface((350, 280))
    stats_panel.fill((255, 255, 255))
    pygame.draw.rect(stats_panel, (200, 200, 200), (0, 0, 350, 280), 3)
    pygame.draw.rect(stats_panel, (100, 150, 255), (0, 0, 350, 40))
    
    # パネルタイトル
    panel_title = get_japanese_font(18).render("📊 AI詳細統計", True, (255, 255, 255))
    stats_panel.blit(panel_title, (10, 10))
    screen.blit(stats_panel, (30, 100))

    stats_font = get_japanese_font(13)  # 16→13
    small_font = get_japanese_font(11)  # 14→11
    x0, y0 = 50, 150
    line_h = 19  # 28→19
    qtable_size = len(qtable)
    
    # 学習履歴から累積の統計情報を取得
    cumulative_stats = learning_history.get_cumulative_stats()
    if cumulative_stats:
        current_ai_learn_count = cumulative_stats.get('ai_learn_count', ai_learn_count)
        current_ai_win_count = cumulative_stats.get('ai_win_count', ai_win_count)
        current_ai_lose_count = cumulative_stats.get('ai_lose_count', ai_lose_count)
        current_ai_draw_count = cumulative_stats.get('ai_draw_count', ai_draw_count)
        current_ai_avg_reward = cumulative_stats.get('ai_avg_reward', ai_avg_reward)
        current_total_games = cumulative_stats.get('total_games', 0)
        current_win_rate = cumulative_stats.get('win_rate', 0)
        current_qtable_size = cumulative_stats.get('qtable_size', qtable_size)
    else:
        current_ai_learn_count = ai_learn_count
        current_ai_win_count = ai_win_count
        current_ai_lose_count = ai_lose_count
        current_ai_draw_count = ai_draw_count
        current_ai_avg_reward = ai_avg_reward
        current_total_games = 0
        current_win_rate = 0
        current_qtable_size = qtable_size
    
    # 勝率
    win_loss_draw_total = current_ai_win_count + current_ai_lose_count + current_ai_draw_count
    win_rate = current_win_rate if current_win_rate > 0 else ((current_ai_win_count / win_loss_draw_total * 100) if win_loss_draw_total > 0 else 0)
    ai_level = calculate_ai_level(win_rate, current_ai_avg_reward, current_ai_learn_count, qtable_size)
    level_desc = get_level_description(ai_level)
    
    # 統計情報（アイコン付き、より詳細な情報）
    stats = [
        ("📚", f"学習回数: {current_ai_learn_count:,}"),
        ("🎮", f"総対戦数: {current_total_games:,}"),
        ("🏆", f"勝利: {current_ai_win_count:,}  敗北: {current_ai_lose_count:,}  引き分け: {current_ai_draw_count:,}"),
        ("📊", f"勝率: {win_rate:.1f}%"),
        ("🧠", f"Qテーブルサイズ: {current_qtable_size:,}"),
        ("⭐", f"AIレベル: {ai_level}（{level_desc}）"),
        ("💰", f"平均報酬: {current_ai_avg_reward:.2f}"),
        ("📈", f"累積報酬: {cumulative_stats.get('ai_total_reward', 0):.2f}"),
        ("📅", f"記録数: {len(learning_history.history)}"),
        ("🕒", f"最新記録: {learning_history.history[-1]['timestamp'][:19] if learning_history.history else 'N/A'}")
    ]
    
    for i, (icon, text) in enumerate(stats):
        # アイコン
        icon_surf = small_font.render(icon, True, (100, 150, 255))
        screen.blit(icon_surf, (x0 - 25, y0 + i * line_h))
        # テキスト
        stat_surf = stats_font.render(text, True, (0, 0, 0))
        screen.blit(stat_surf, (x0, y0 + i * line_h))

    # --- 円グラフ（中央大きく） ---
    def draw_pie(surface, center, radius, start_angle, end_angle, color, steps=60):
        points = [center]
        for i in range(steps + 1):
            angle = start_angle + (end_angle - start_angle) * i / steps
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(surface, color, points)

    cx, cy, r = WINDOW_WIDTH // 2, 220, 110
    total = current_ai_win_count + current_ai_lose_count + current_ai_draw_count
    colors = [(0, 180, 0), (200, 0, 0), (120, 120, 120)]
    labels = ["勝利", "敗北", "引き分け"]
    counts = [current_ai_win_count, current_ai_lose_count, current_ai_draw_count]
    percents = [(count / total * 100) if total > 0 else 0 for count in counts]
    
    if total > 0:
        start_angle = 0
        for count, color, label, percent in zip(counts, colors, labels, percents):
            if count > 0:
                end_angle = start_angle + 2 * math.pi * count / total
                draw_pie(screen, (cx, cy), r, start_angle, end_angle, color)
                # セグメント中央に割合表示
                mid_angle = (start_angle + end_angle) / 2
                tx = cx + int(r * 0.7 * math.cos(mid_angle))
                ty = cy + int(r * 0.7 * math.sin(mid_angle))
                percent_text = get_japanese_font(18).render(f"{percent:.1f}%", True, color)
                screen.blit(percent_text, (tx - percent_text.get_width() // 2, ty - percent_text.get_height() // 2))
                start_angle = end_angle
        # 円の枠
        pygame.draw.circle(screen, (80, 80, 80), (cx, cy), r, 4)
        # 中央に総対戦数（累積値）
        center_text = get_japanese_font(22).render(f"総対戦数: {current_total_games}", True, (0, 0, 0))
        screen.blit(center_text, (cx - center_text.get_width() // 2, cy - 18))
        # 中央下に勝率
        win_loss_draw_total = current_ai_win_count + current_ai_lose_count + current_ai_draw_count
        win_rate = (current_ai_win_count / win_loss_draw_total * 100) if win_loss_draw_total > 0 else 0
        winrate_text = get_japanese_font(18).render(f"勝率: {win_rate:.1f}%", True, (0, 120, 0))
        screen.blit(winrate_text, (cx - winrate_text.get_width() // 2, cy + 18))
        # 凡例
        legend_y = cy + r + 30
        for i, (color, label, count) in enumerate(zip(colors, labels, counts)):
            pygame.draw.rect(screen, color, (cx - 100 + i * 120, legend_y, 22, 22))
            pygame.draw.rect(screen, (80, 80, 80), (cx - 100 + i * 120, legend_y, 22, 22), 2)
            label_surf = get_japanese_font(16).render(f"{label}: {count}", True, (0, 0, 0))
            screen.blit(label_surf, (cx - 70 + i * 120, legend_y + 2))
    else:
        no_data_surf = get_japanese_font(18).render("データ不足", True, (120, 120, 120))
        screen.blit(no_data_surf, (cx - 60, cy - 18))

    # --- 折れ線グラフ群（円グラフの下に横並び） ---
    graph_panel_y = cy + r + 70
    graph_panel_h = 170
    graph_panel_w = 320
    graph_margin = 30
    graph_titles = ["🏆 勝率推移", "💰 平均報酬推移", "🧠 Qテーブル成長"]
    graph_funcs = [learning_history.get_win_rate_history, learning_history.get_avg_reward_history, learning_history.get_qtable_size_history]
    graph_colors = [(0, 100, 200), (0, 200, 100), (150, 100, 200)]
    for i in range(3):
        gx = graph_margin + i * (graph_panel_w + graph_margin)
        gy = graph_panel_y
        # パネル
        pygame.draw.rect(screen, (255, 255, 255), (gx, gy, graph_panel_w, graph_panel_h))
        pygame.draw.rect(screen, (180, 180, 180), (gx, gy, graph_panel_w, graph_panel_h), 3)
        # タイトル
        title = get_japanese_font(15).render(graph_titles[i], True, (0, 0, 0))
        screen.blit(title, (gx + 10, gy + 8))
        # データ取得
        data = graph_funcs[i]()
        if len(data) > 1:
            max_val = max(data) if max(data) != 0 else 1
            min_val = min(data) if min(data) != max_val else 0
            # グリッド線
            for j in range(5):
                gy_grid = gy + 40 + (j * (graph_panel_h - 60) // 4)
                pygame.draw.line(screen, (230, 230, 230), (gx + 40, gy_grid), (gx + graph_panel_w - 10, gy_grid), 1)
                # Y軸ラベル
                val = max_val - (max_val - min_val) * j / 4
                label = get_japanese_font(10).render(f"{val:.1f}", True, (120, 120, 120))
                screen.blit(label, (gx + 5, gy_grid - 8))
            # 折れ線
            points = []
            for k, v in enumerate(data):
                px = gx + 40 + (k / (len(data) - 1)) * (graph_panel_w - 50)
                py = gy + 40 + (max_val - v) / (max_val - min_val + 1e-6) * (graph_panel_h - 60)
                points.append((px, py))
            if len(points) > 1:
                pygame.draw.lines(screen, graph_colors[i], False, points, 3)
                for pt in points:
                    pygame.draw.circle(screen, graph_colors[i], (int(pt[0]), int(pt[1])), 3)
                # 最新点強調
                pygame.draw.circle(screen, (255, 0, 0), (int(points[-1][0]), int(points[-1][1])), 6)
                pygame.draw.circle(screen, (255, 255, 255), (int(points[-1][0]), int(points[-1][1])), 2)
            # X軸ラベル
            x_label = get_japanese_font(10).render(f"ゲーム数: {len(data)}", True, (120, 120, 120))
            screen.blit(x_label, (gx + 40, gy + graph_panel_h - 18))
        else:
            no_data = get_japanese_font(12).render("データ不足", True, (120, 120, 120))
            screen.blit(no_data, (gx + graph_panel_w // 2 - 30, gy + graph_panel_h // 2))
            
    # --- 学習進捗グラフ（学習進捗表示がONの場合のみ） ---
    # 注：上記の折れ線グラフ群で表示済みのため、重複を避けてコメントアウト
    # if show_learning_progress:
    #     draw_enhanced_learning_graphs(screen, learning_history, total_games, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable)

    # --- ボタン配置（下部） ---
    button_width = 200
    button_height = 50
    button_spacing = 20
    start_y = 650  # 折れ線グラフの半分くらい下に下げる
    
    # ボタンの背景パネル
    button_panel = pygame.Surface((WINDOW_WIDTH - 60, 120))
    button_panel.fill((255, 255, 255))
    pygame.draw.rect(button_panel, (200, 200, 200), (0, 0, WINDOW_WIDTH - 60, 120), 3)
    pygame.draw.rect(button_panel, (100, 150, 255), (0, 0, WINDOW_WIDTH - 60, 40))
    panel_title = get_japanese_font(18).render("⚙️ データ管理", True, (255, 255, 255))
    button_panel.blit(panel_title, (10, 10))
    screen.blit(button_panel, (30, start_y - 50))
    
    # ボタンを横並びに配置
    total_button_width = button_width * 3 + button_spacing * 2
    start_x = (WINDOW_WIDTH - total_button_width) // 2
    
    # 保存ボタン
    save_button = pygame.Rect(start_x, start_y, button_width, button_height)
    pygame.draw.rect(screen, (100, 200, 100), save_button, border_radius=10)
    pygame.draw.rect(screen, (50, 150, 50), save_button, 3, border_radius=10)
    
    # 絵文字とテキストを分けて表示
    emoji_font = get_emoji_font(16)
    text_font = get_japanese_font(16)
    
    # 絵文字を描画
    emoji_surface = emoji_font.render("💾", True, (255, 255, 255))
    emoji_rect = emoji_surface.get_rect(center=(save_button.centerx - 30, save_button.centery))
    screen.blit(emoji_surface, emoji_rect)
    
    # テキストを描画
    save_text = text_font.render("保存", True, (255, 255, 255))
    save_text_rect = save_text.get_rect(center=(save_button.centerx + 20, save_button.centery))
    screen.blit(save_text, save_text_rect)
    
    # 上書き保存ボタン
    overwrite_button = pygame.Rect(start_x + button_width + button_spacing, start_y, button_width, button_height)
    pygame.draw.rect(screen, (200, 150, 100), overwrite_button, border_radius=10)
    pygame.draw.rect(screen, (150, 100, 50), overwrite_button, 3, border_radius=10)
    
    # 絵文字を描画
    emoji_surface = emoji_font.render("📝", True, (255, 255, 255))
    emoji_rect = emoji_surface.get_rect(center=(overwrite_button.centerx - 30, overwrite_button.centery))
    screen.blit(emoji_surface, emoji_rect)
    
    # テキストを描画
    overwrite_text = text_font.render("上書き保存", True, (255, 255, 255))
    overwrite_text_rect = overwrite_text.get_rect(center=(overwrite_button.centerx + 20, overwrite_button.centery))
    screen.blit(overwrite_text, overwrite_text_rect)
    
    # 読み込みボタン
    load_button = pygame.Rect(start_x + (button_width + button_spacing) * 2, start_y, button_width, button_height)
    pygame.draw.rect(screen, (200, 150, 100), load_button, border_radius=10)
    pygame.draw.rect(screen, (150, 100, 50), load_button, 3, border_radius=10)
    
    # 絵文字を描画
    emoji_surface = emoji_font.render("📂", True, (255, 255, 255))
    emoji_rect = emoji_surface.get_rect(center=(load_button.centerx - 20, load_button.centery))
    screen.blit(emoji_surface, emoji_rect)
    
    # テキストを描画
    load_text = text_font.render("読み込み", True, (255, 255, 255))
    load_text_rect = load_text.get_rect(center=(load_button.centerx + 25, load_button.centery))
    screen.blit(load_text, load_text_rect)
    
    # 新規作成ボタン
    new_button = pygame.Rect(start_x, start_y + button_height + 15, button_width, button_height)
    pygame.draw.rect(screen, (100, 150, 200), new_button, border_radius=10)
    pygame.draw.rect(screen, (50, 100, 150), new_button, 3, border_radius=10)
    
    # 絵文字を描画
    emoji_surface = emoji_font.render("🆕", True, (255, 255, 255))
    emoji_rect = emoji_surface.get_rect(center=(new_button.centerx - 25, new_button.centery))
    screen.blit(emoji_surface, emoji_rect)
    
    # テキストを描画
    new_text = text_font.render("新規作成", True, (255, 255, 255))
    new_text_rect = new_text.get_rect(center=(new_button.centerx + 25, new_button.centery))
    screen.blit(new_text, new_text_rect)
    
    # 削除ボタン
    delete_button = pygame.Rect(start_x + button_width + button_spacing, start_y + button_height + 15, button_width, button_height)
    pygame.draw.rect(screen, (200, 100, 100), delete_button, border_radius=10)
    pygame.draw.rect(screen, (150, 50, 50), delete_button, 3, border_radius=10)
    
    # 絵文字を描画
    emoji_surface = emoji_font.render("🗑️", True, (255, 255, 255))
    emoji_rect = emoji_surface.get_rect(center=(delete_button.centerx - 15, delete_button.centery))
    screen.blit(emoji_surface, emoji_rect)
    
    # テキストを描画
    delete_text = text_font.render("削除", True, (255, 255, 255))
    delete_text_rect = delete_text.get_rect(center=(delete_button.centerx + 20, delete_button.centery))
    screen.blit(delete_text, delete_text_rect)
    
    # 戻るボタン
    back_button = pygame.Rect(start_x + (button_width + button_spacing) * 2, start_y + button_height + 15, button_width, button_height)
    pygame.draw.rect(screen, (150, 150, 150), back_button, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), back_button, 3, border_radius=10)
    
    # 絵文字を描画
    emoji_surface = emoji_font.render("🔙", True, (255, 255, 255))
    emoji_rect = emoji_surface.get_rect(center=(back_button.centerx - 15, back_button.centery))
    screen.blit(emoji_surface, emoji_rect)
    
    # テキストを描画
    back_text = text_font.render("戻る", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=(back_button.centerx + 20, back_button.centery))
    screen.blit(back_text, back_text_rect)
    
    # 説明文
    info_font = get_japanese_font(14)
    info_text = info_font.render("学習データの保存・読み込み・管理とAIの詳細情報を確認できます", True, (100, 100, 100))
    screen.blit(info_text, (WINDOW_WIDTH//2 - info_text.get_width()//2, start_y + button_height * 2 + 35))
    
    # 学習進捗表示のON/OFFボタン
    progress_btn_rect = pygame.Rect(20, 20, 200, 40)
    pygame.draw.rect(screen, (100, 100, 200), progress_btn_rect, border_radius=8)
    pygame.draw.rect(screen, (50, 50, 150), progress_btn_rect, 2, border_radius=8)
    
    # 絵文字を描画
    emoji_surface = emoji_font.render("📊", True, (255, 255, 255))
    emoji_rect = emoji_surface.get_rect(center=(progress_btn_rect.centerx - 60, progress_btn_rect.centery))
    screen.blit(emoji_surface, emoji_rect)
    
    # テキストを描画
    progress_text = text_font.render("学習進捗: ON" if show_learning_progress else "学習進捗: OFF", True, (255, 255, 255))
    progress_text_rect = progress_text.get_rect(center=(progress_btn_rect.centerx + 10, progress_btn_rect.centery))
    screen.blit(progress_text, progress_text_rect)
    
    return save_button, overwrite_button, load_button, new_button, delete_button, back_button, progress_btn_rect

def draw_enhanced_learning_graphs(screen, learning_history, game_count, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable):
    """強化された学習進捗グラフを描画"""
    # グラフエリアの背景（左側のデータと重ならないように調整）
    graph_area_width = 450
    graph_area_height = WINDOW_HEIGHT - 100
    graph_x = WINDOW_WIDTH - graph_area_width - 20
    graph_y = 100
    
    # グラフエリアの背景パネル（半透明で見やすく）
    graph_panel = pygame.Surface((graph_area_width, graph_area_height))
    graph_panel.fill((255, 255, 255))
    graph_panel.set_alpha(240)  # 半透明に設定
    pygame.draw.rect(graph_panel, (200, 200, 200), (0, 0, graph_area_width, graph_area_height), 3)
    pygame.draw.rect(graph_panel, (100, 150, 255), (0, 0, graph_area_width, 40))
    
    # パネルタイトル
    panel_title = get_japanese_font(18).render("📈 学習進捗グラフ", True, (255, 255, 255))
    graph_panel.blit(panel_title, (10, 10))
    screen.blit(graph_panel, (graph_x, graph_y))
    
    # グラフ内の座標系
    inner_x = graph_x + 20
    inner_y = graph_y + 60
    inner_width = graph_area_width - 40
    inner_height = graph_area_height - 80
    
    if len(learning_history.history) > 1:
        # 1. 勝率推移グラフ
        draw_win_rate_graph(screen, learning_history, inner_x, inner_y, inner_width, inner_height // 4 - 10)
        
        # 2. 平均報酬推移グラフ
        draw_reward_graph(screen, learning_history, inner_x, inner_y + inner_height // 4, inner_width, inner_height // 4 - 10)
        
        # 3. Qテーブル成長グラフ
        draw_qtable_growth_graph(screen, learning_history, inner_x, inner_y + 2 * inner_height // 4, inner_width, inner_height // 4 - 10)
        
        # 4. 学習回数推移グラフ（新規追加）
        # draw_learn_count_graph(screen, learning_history, inner_x, inner_y + 3 * inner_height // 4, inner_width, inner_height // 4 - 10)
    else:
        # データ不足時の表示
        no_data_font = get_japanese_font(16)
        no_data_text = no_data_font.render("📊 学習データが不足しています", True, (100, 100, 100))
        no_data_text2 = no_data_font.render("対戦や訓練を行うと詳細なグラフが表示されます", True, (100, 100, 100))
        screen.blit(no_data_text, (inner_x + 50, inner_y + inner_height // 2 - 20))
        screen.blit(no_data_text2, (inner_x + 20, inner_y + inner_height // 2 + 10))

def draw_win_rate_graph(screen, learning_history, x, y, width, height):
    """勝率推移グラフを描画"""
    # タイトル
    title_font = get_japanese_font(14)
    title_text = title_font.render("　勝率推移", True, (0, 0, 0))
    screen.blit(title_text, (x, y - 20))
    
    win_rates = learning_history.get_win_rate_history()
    if len(win_rates) < 2:
        return
    
    # グラフエリア
    graph_width = width - 40
    graph_height = height - 40
    graph_x = x + 20
    graph_y = y + 20
    
    # 背景
    pygame.draw.rect(screen, (255, 255, 255), (graph_x, graph_y, graph_width, graph_height))
    pygame.draw.rect(screen, (100, 100, 100), (graph_x, graph_y, graph_width, graph_height), 2)
    
    # グリッド線
    for i in range(5):
        y_pos = graph_y + (i * graph_height // 4)
        pygame.draw.line(screen, (200, 200, 200), (graph_x, y_pos), (graph_x + graph_width, y_pos), 1)
    
    # データポイント
    if len(win_rates) > 1:
        points = []
        for i, rate in enumerate(win_rates):
            x_pos = graph_x + (i / (len(win_rates) - 1)) * graph_width
            y_pos = graph_y + graph_height - (rate / 100) * graph_height
            points.append((x_pos, y_pos))
        
        if len(points) > 1:
            pygame.draw.lines(screen, (0, 100, 200), False, points, 3)
            for point in points:
                pygame.draw.circle(screen, (0, 100, 200), (int(point[0]), int(point[1])), 3)

def draw_reward_graph(screen, learning_history, x, y, width, height):
    """平均報酬推移グラフを描画"""
    # タイトル
    title_font = get_japanese_font(14)
    title_text = title_font.render("　平均報酬推移", True, (0, 0, 0))
    screen.blit(title_text, (x, y - 20))
    
    avg_rewards = learning_history.get_avg_reward_history()
    if len(avg_rewards) > 1:
        max_reward = max(avg_rewards) if avg_rewards else 1
        if max_reward == 0:
            max_reward = 1
        
        # グリッド線
        for i in range(4):
            grid_y = y + (i * height // 3)
            pygame.draw.line(screen, (220, 220, 220), (x, grid_y), (x + width, grid_y), 1)
            
            # Y軸ラベル（報酬）
            label_value = max_reward - (i * max_reward // 3)
            label_font = get_japanese_font(10)
            label_text = label_font.render(f"{label_value:.1f}", True, (100, 100, 100))
            screen.blit(label_text, (x - 35, grid_y - 8))
        
        # 平均報酬グラフ
        points = []
        for i, reward in enumerate(avg_rewards):
            point_x = x + (i / (len(avg_rewards) - 1)) * width
            point_y = y + height - (reward / max_reward) * height
            points.append((point_x, point_y))
        
        if len(points) > 1:
            # グラフ線
            pygame.draw.lines(screen, (0, 200, 100), False, points, 3)
            
            # データポイント
            for point in points:
                pygame.draw.circle(screen, (0, 200, 100), (int(point[0]), int(point[1])), 2)
            
            # 最新の点を強調
            if points:
                pygame.draw.circle(screen, (255, 165, 0), (int(points[-1][0]), int(points[-1][1])), 4)
                pygame.draw.circle(screen, (255, 255, 255), (int(points[-1][0]), int(points[-1][1])), 2)
            
        # グラフラベル
        label_font = get_japanese_font(10)
        label_text = label_font.render("平均報酬推移", True, (0, 0, 0))
        screen.blit(label_text, (x, y - 15))
        
        # X軸ラベル（ゲーム数）
        if len(avg_rewards) > 1:
            x_label_text = label_font.render(f"ゲーム数: {len(avg_rewards)}", True, (100, 100, 100))
            screen.blit(x_label_text, (x, y + height + 5))

def draw_qtable_growth_graph(screen, learning_history, x, y, width, height):
    """Qテーブル成長グラフを描画"""
    # グラフ背景
    pygame.draw.rect(screen, (250, 250, 250), (x, y, width, height))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height), 2)
    
    # タイトル
    title_font = get_japanese_font(14)
    title = title_font.render("🧠 Qテーブル成長", True, (0, 0, 0))
    screen.blit(title, (x, y - 20))
    
    qtable_sizes = learning_history.get_qtable_size_history()
    if len(qtable_sizes) > 1:
        max_size = max(qtable_sizes) if qtable_sizes else 1
        if max_size == 0:
            max_size = 1
        
        # グリッド線
        for i in range(4):
            grid_y = y + (i * height // 3)
            pygame.draw.line(screen, (220, 220, 220), (x, grid_y), (x + width, grid_y), 1)
            
            # Y軸ラベル
            label_value = max_size - (i * max_size // 3)
            label_font = get_japanese_font(10)
            label_text = label_font.render(f"{label_value:,}", True, (100, 100, 100))
            screen.blit(label_text, (x - 40, grid_y - 8))
        
        # Qテーブルサイズグラフ
        points = []
        for i, size in enumerate(qtable_sizes):
            point_x = x + (i / (len(qtable_sizes) - 1)) * width
            point_y = y + height - (size / max_size) * height
            points.append((point_x, point_y))
        
        if len(points) > 1:
            # グラフ線
            pygame.draw.lines(screen, (150, 100, 200), False, points, 3)
            
            # データポイント
            for point in points:
                pygame.draw.circle(screen, (150, 100, 200), (int(point[0]), int(point[1])), 3)
            
            # 最新点を強調
            if points:
                pygame.draw.circle(screen, (255, 100, 100), (int(points[-1][0]), int(points[-1][1])), 6)
                pygame.draw.circle(screen, (255, 255, 255), (int(points[-1][0]), int(points[-1][1])), 2)
        
        # X軸ラベル
        x_label_font = get_japanese_font(10)
        x_label_text = x_label_font.render(f"ゲーム数: {len(qtable_sizes)}", True, (100, 100, 100))
        screen.blit(x_label_text, (x, y + height + 5))

def draw_battle_history_screen(screen, font):
    """対戦記録画面を描画（大幅改善版）"""
    # mainモジュールをインポートしてlearning_historyを取得
    import main
    learning_history = main.learning_history
    
    # グラデーション背景
    for y in range(WINDOW_HEIGHT):
        color_ratio = y / WINDOW_HEIGHT
        r = int(230 + (255 - 230) * color_ratio)
        g = int(240 + (255 - 240) * color_ratio)
        b = int(255 + (255 - 255) * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
    
    # タイトル（装飾付き）
    title_bg = pygame.Surface((WINDOW_WIDTH, 80))
    title_bg.set_alpha(180)
    title_bg.fill((150, 100, 255))
    screen.blit(title_bg, (0, 0))
    
    title = font.render("📋 対戦記録・詳細分析", True, (255, 255, 255))
    title_shadow = font.render("📋 対戦記録・詳細分析", True, (100, 50, 150))
    screen.blit(title_shadow, (WINDOW_WIDTH//2 - title.get_width()//2 + 2, 32))
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 30))
    
    # 履歴全体の累積統計を表示
    if learning_history.history:
        # 履歴全体から累積統計を取得
        cumulative_stats = learning_history.get_cumulative_stats()
        
        # 対戦タイプ別の統計を計算
        human_vs_ai_count = 0
        ai_vs_ai_count = 0
        unknown_count = 0
        
        for record in learning_history.history:
            game_type = record.get('game_type', 'unknown')
            if game_type == "human_vs_ai":
                human_vs_ai_count += 1
            elif game_type == "ai_vs_ai":
                ai_vs_ai_count += 1
            else:
                unknown_count += 1
        
        # 統計パネル（左側）
        stats_panel = pygame.Surface((400, 300))
        stats_panel.fill((255, 255, 255))
        pygame.draw.rect(stats_panel, (200, 200, 200), (0, 0, 400, 300), 3)
        pygame.draw.rect(stats_panel, (150, 100, 255), (0, 0, 400, 40))
        
        # パネルタイトル
        panel_title = get_japanese_font(18).render("📊 累積対戦統計", True, (255, 255, 255))
        stats_panel.blit(panel_title, (10, 10))
        screen.blit(stats_panel, (30, 100))
        
        # 統計情報
        stats_font = get_japanese_font(14)  # 16から14に縮小
        small_font = get_emoji_font(12)  # 絵文字対応フォントを使用
        x0, y0 = 50, 150
        line_h = 22  # 28から22に縮小
        
        # 履歴全体の累積統計情報
        if cumulative_stats:
            total_learn = cumulative_stats.get('ai_learn_count', 0)
            total_win = cumulative_stats.get('ai_win_count', 0)
            total_lose = cumulative_stats.get('ai_lose_count', 0)
            total_draw = cumulative_stats.get('ai_draw_count', 0)
            total_reward = cumulative_stats.get('ai_total_reward', 0)
            avg_reward = cumulative_stats.get('ai_avg_reward', 0)
            win_rate = cumulative_stats.get('win_rate', 0)
            total_games = cumulative_stats.get('total_games', 0)
            
            # 最新の記録からQテーブルサイズを取得
            latest = learning_history.history[-1]
            qtable_size = latest.get('qtable_size', 0)
            
            cumulative_stats_list = [
                ("📚", f"累積学習回数: {total_learn:,}"),
                ("🎮", f"累積対戦数: {total_games:,}"),
                ("👤", f"人間vsAI: {human_vs_ai_count}回"),
                ("🤖", f"AI同士: {ai_vs_ai_count}回"),
                ("🏆", f"累積勝利: {total_win:,}  累積敗北: {total_lose:,}  累積引き分け: {total_draw:,}"),
                ("📊", f"累積勝率: {win_rate:.1f}%"),
                ("💰", f"累積平均報酬: {avg_reward:.2f}"),
                ("📈", f"累積報酬: {total_reward:.2f}"),
                ("🧠", f"Qテーブルサイズ: {qtable_size:,}"),
                ("📅", f"記録数: {len(learning_history.history)}"),
                ("⭐", f"AIレベル: {calculate_ai_level(win_rate, avg_reward, total_learn, qtable_size)}"),
                ("🕒", f"最新記録: {latest.get('timestamp', 'N/A')[:19]}")
            ]
        else:
            # 累積統計が取得できない場合は最新の記録を使用
            latest = learning_history.history[-1]
            cumulative_stats_list = [
                ("📚", f"学習回数: {latest.get('ai_learn_count', 0):,}"),
                ("🎮", f"総対戦数: {latest.get('game_count', 0):,}"),
                ("👤", f"人間vsAI: {human_vs_ai_count}回"),
                ("🤖", f"AI同士: {ai_vs_ai_count}回"),
                ("🏆", f"勝利: {latest.get('ai_win_count', 0):,}  敗北: {latest.get('ai_lose_count', 0):,}  引き分け: {latest.get('ai_draw_count', 0):,}"),
                ("📊", f"勝率: {latest.get('win_rate', 0):.1f}%"),
                ("💰", f"平均報酬: {latest.get('ai_avg_reward', 0):.2f}"),
                ("📈", f"累積報酬: {latest.get('ai_total_reward', 0):.2f}"),
                ("🧠", f"Qテーブルサイズ: {latest.get('qtable_size', 0):,}"),
                ("📅", f"記録数: {len(learning_history.history)}"),
                ("⭐", f"AIレベル: {calculate_ai_level(latest.get('win_rate', 0), latest.get('ai_avg_reward', 0), latest.get('ai_learn_count', 0), latest.get('qtable_size', 0))}"),
                ("🕒", f"最新記録: {latest.get('timestamp', 'N/A')[:19]}")
            ]
        
        for i, (icon, text) in enumerate(cumulative_stats_list):
            # アイコン（絵文字フォントで表示）
            icon_surf = small_font.render(icon, True, (150, 100, 255))
            screen.blit(icon_surf, (x0 - 20, y0 + i * line_h))  # -25から-20に調整
            # テキスト（日本語フォントで表示）
            stat_surf = stats_font.render(text, True, (0, 0, 0))
            screen.blit(stat_surf, (x0, y0 + i * line_h))
        
        # 勝敗比率円グラフ（右側）- 位置を右に移動
        cx, cy, r = 600, 250, 70  # 500から600に移動
        if cumulative_stats:
            ai_win_count = cumulative_stats.get('ai_win_count', 0)
            ai_lose_count = cumulative_stats.get('ai_lose_count', 0)
            ai_draw_count = cumulative_stats.get('ai_draw_count', 0)
        else:
            ai_win_count = latest.get('ai_win_count', 0)
            ai_lose_count = latest.get('ai_lose_count', 0)
            ai_draw_count = latest.get('ai_draw_count', 0)
        
        total = ai_win_count + ai_lose_count + ai_draw_count
        
        if total > 0:
            start_angle = 0
            colors = [(0, 180, 0), (200, 0, 0), (120, 120, 120)]
            labels = ["AI勝利", "AI敗北", "引き分け"]
            counts = [ai_win_count, ai_lose_count, ai_draw_count]
            
            for count, color, label in zip(counts, colors, labels):
                if count > 0:
                    end_angle = start_angle + 360 * count / total
                    pygame.draw.arc(screen, color, (cx-r, cy-r, r*2, r*2),
                                    math.radians(start_angle), math.radians(end_angle), r)
                    start_angle = end_angle
        
            # 円の枠
            pygame.draw.circle(screen, (80, 80, 80), (cx, cy), r, 3)
            
            # 凡例
            legend_y = cy + r + 30
            for i, (color, label, count) in enumerate(zip(colors, labels, counts)):
                if count > 0:
                    # 色の四角
                    pygame.draw.rect(screen, color, (cx - 100 + i * 60, legend_y, 15, 15))
                    pygame.draw.rect(screen, (80, 80, 80), (cx - 100 + i * 60, legend_y, 15, 15), 1)
                    # ラベル（日本語フォントで表示）
                    label_surf = get_japanese_font(12).render(f"{label}: {count}", True, (0, 0, 0))
                    screen.blit(label_surf, (cx - 80 + i * 60, legend_y - 2))
        
        # 対戦履歴リスト（下部）
        history_panel = pygame.Surface((WINDOW_WIDTH - 60, 200))
        history_panel.fill((255, 255, 255))
        pygame.draw.rect(history_panel, (200, 200, 200), (0, 0, WINDOW_WIDTH - 60, 200), 3)
        pygame.draw.rect(history_panel, (150, 100, 255), (0, 0, WINDOW_WIDTH - 60, 40))
        
        # パネルタイトル
        history_title = get_japanese_font(18).render("📜 対戦履歴", True, (255, 255, 255))
        history_panel.blit(history_title, (10, 10))
        screen.blit(history_panel, (30, 420))
        
        # 履歴リスト
        history_font = get_japanese_font(14)  # 日本語フォントを使用
        emoji_font = get_emoji_font(14)  # 絵文字用フォント
        y_offset = 470
        
        # 最新10件の対戦記録を表示
        recent_history = list(learning_history.history)[-10:]
        for i, record in enumerate(reversed(recent_history)):
            if y_offset > WINDOW_HEIGHT - 100:
                break
                
            # 対戦記録の行
            timestamp = record.get('timestamp', 'N/A')[:19]
            black_score = record.get('black_score', 0)
            white_score = record.get('white_score', 0)
            win_rate = record.get('win_rate', 0)
            game_type = record.get('game_type', 'unknown')
            
            # 対戦タイプに応じたアイコンとテキスト
            if game_type == "human_vs_ai":
                type_icon = "👤"
                type_text = "人間vsAI"
            elif game_type == "ai_vs_ai":
                type_icon = "🤖"
                type_text = "AI同士"
            else:
                type_icon = "❓"
                type_text = "不明"
            
            # 背景色（交互に）
            bg_color = (245, 245, 245) if i % 2 == 0 else (255, 255, 255)
            pygame.draw.rect(screen, bg_color, (50, y_offset - 5, WINDOW_WIDTH - 100, 25))
            
            # 記録テキストを分割して表示
            x_pos = 60
            
            # 時刻アイコンと時刻
            emoji_surf = emoji_font.render("🕒", True, (100, 100, 100))
            screen.blit(emoji_surf, (x_pos, y_offset))
            x_pos += 20
            
            time_surf = history_font.render(timestamp, True, (0, 0, 0))
            screen.blit(time_surf, (x_pos, y_offset))
            x_pos += time_surf.get_width() + 10
            
            # 対戦タイプアイコンとテキスト
            type_icon_surf = emoji_font.render(type_icon, True, (150, 100, 255))
            screen.blit(type_icon_surf, (x_pos, y_offset))
            x_pos += 20
            
            type_text_surf = history_font.render(type_text, True, (0, 0, 0))
            screen.blit(type_text_surf, (x_pos, y_offset))
            x_pos += type_text_surf.get_width() + 10
            
            # スコア
            score_emoji = emoji_font.render("⚔️", True, (100, 100, 100))
            screen.blit(score_emoji, (x_pos, y_offset))
            x_pos += 20
            
            score_text = f"黒{black_score}-白{white_score}"
            score_surf = history_font.render(score_text, True, (0, 0, 0))
            screen.blit(score_surf, (x_pos, y_offset))
            x_pos += score_surf.get_width() + 10
            
            # 勝率
            win_emoji = emoji_font.render("🏆", True, (100, 100, 100))
            screen.blit(win_emoji, (x_pos, y_offset))
            x_pos += 20
            
            win_text = f"勝率{win_rate:.1f}%"
            win_surf = history_font.render(win_text, True, (0, 0, 0))
            screen.blit(win_surf, (x_pos, y_offset))
            x_pos += win_surf.get_width() + 10
            
            # 報酬
            reward_emoji = emoji_font.render("💰", True, (100, 100, 100))
            screen.blit(reward_emoji, (x_pos, y_offset))
            x_pos += 20
            
            reward_text = f"報酬{record.get('ai_avg_reward', 0):.2f}"
            reward_surf = history_font.render(reward_text, True, (0, 0, 0))
            screen.blit(reward_surf, (x_pos, y_offset))
            x_pos += reward_surf.get_width() + 10
            
            # 学習回数
            learn_emoji = emoji_font.render("📚", True, (100, 100, 100))
            screen.blit(learn_emoji, (x_pos, y_offset))
            x_pos += 20
            
            learn_text = f"学習{record.get('ai_learn_count', 0):,}"
            learn_surf = history_font.render(learn_text, True, (0, 0, 0))
            screen.blit(learn_surf, (x_pos, y_offset))
            
            y_offset += 30
        
        # データ不足時の表示
        if len(recent_history) == 0:
            no_data_text = get_japanese_font(14).render("📊 対戦記録がありません", True, (100, 100, 100))
            screen.blit(no_data_text, (60, y_offset))
    
    else:
        # データがない場合の表示
        no_data_font = get_japanese_font(20)
        no_data_text = no_data_font.render("📊 対戦記録がありません", True, (100, 100, 100))
        no_data_text2 = no_data_font.render("対戦を行うとここに記録が表示されます", True, (100, 100, 100))
        screen.blit(no_data_text, (WINDOW_WIDTH//2 - no_data_text.get_width()//2, WINDOW_HEIGHT//2 - 40))
        screen.blit(no_data_text2, (WINDOW_WIDTH//2 - no_data_text2.get_width()//2, WINDOW_HEIGHT//2))
    
    # 戻るボタン（装飾付き）
    back_button = pygame.Rect(WINDOW_WIDTH//2-120, WINDOW_HEIGHT-80, 240, 60)
    pygame.draw.rect(screen, (150, 150, 150), back_button, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), back_button, 3, border_radius=10)
    back_text = font.render("🔙 戻る", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_button.center)
    screen.blit(back_text, back_text_rect)

def draw_pretrain_count(screen, font, pretrain_now, pretrain_total):
    """AI訓練回数を表示（戻るボタンの右側に配置）"""
    # フォントサイズを小さくして画面内に収める
    small_font = get_japanese_font(20)  # フォントサイズを20に縮小
    text = small_font.render(f"AI訓練: {pretrain_now}/{pretrain_total}", True, (0,0,0))
    # 戻るボタンの右側に配置（画面下部から少し上に移動）
    back_button_x = WINDOW_WIDTH//2 + BUTTON_WIDTH//2 + 20
    text_x = back_button_x + BUTTON_WIDTH + 20
    text_y = WINDOW_HEIGHT - BUTTON_HEIGHT - 30 + (BUTTON_HEIGHT - text.get_height()) // 2  # 30px上に移動
    screen.blit(text, (text_x, text_y))

def draw_game_count(screen, font, game_count):
    """対戦回数を表示（戻るボタンの右側に配置）"""
    # フォントサイズを小さくして画面内に収める
    small_font = get_japanese_font(20)  # フォントサイズを20に縮小
    text = small_font.render(f"対戦回数: {game_count}", True, (0,0,0))
    # 戻るボタンの右側、AI訓練回数の下に配置（間隔を調整）
    back_button_x = WINDOW_WIDTH//2 + BUTTON_WIDTH//2 + 20
    text_x = back_button_x + BUTTON_WIDTH + 20
    text_y = WINDOW_HEIGHT - BUTTON_HEIGHT - 30 + BUTTON_HEIGHT + 5  # 30px上に移動、間隔5px
    screen.blit(text, (text_x, text_y))

def draw_move_count(screen, font, move_count, last_move_count):
    """手数を表示"""
    if move_count != last_move_count:
        text = font.render(f"手数: {move_count}", True, BLACK)
        x = BOARD_OFFSET_X + BOARD_PIXEL_SIZE - text.get_width()
        y = BOARD_OFFSET_Y // 2 - text.get_height() // 2
        screen.blit(text, (x, y))
        return move_count
    return last_move_count

def draw_ai_stats(screen, font, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward):
    """AI統計情報を描画（改善版）"""
    # 統計パネルの背景
    stats_panel = pygame.Surface((260, 120))  # 幅をさらに小さく
    stats_panel.fill((255, 255, 255))
    pygame.draw.rect(stats_panel, (200, 200, 200), (0, 0, 260, 120), 2)
    pygame.draw.rect(stats_panel, (100, 150, 255), (0, 0, 260, 25))
    
    # パネルタイトル
    title_font = get_japanese_font(14)
    title = title_font.render("🤖 AI統計", True, (255, 255, 255))
    stats_panel.blit(title, (10, 5))
    screen.blit(stats_panel, (WINDOW_WIDTH - 280, 20))  # 位置を調整
    
    # 統計情報
    stats_font = get_japanese_font(12)
    small_font = get_emoji_font(10)
    x0, y0 = WINDOW_WIDTH - 270, 50  # 位置を調整
    line_h = 18
    
    total_games = ai_win_count + ai_lose_count + ai_draw_count
    win_rate = (ai_win_count / total_games * 100) if total_games > 0 else 0
    
    # 統計情報（アイコン付き）
    stats = [
        ("　", f"勝利: {ai_win_count}"),
        ("　", f"敗北: {ai_lose_count}"),
        (" ", f"引き分け: {ai_draw_count}"),
        (" ", f"勝率: {win_rate:.1f}%"),
        (" ", f"平均報酬: {ai_avg_reward:.2f}")
    ]
    
    for i, (icon, text) in enumerate(stats):
        # アイコン
        icon_surf = small_font.render(icon, True, (100, 150, 255))
        screen.blit(icon_surf, (x0 - 15, y0 + i * line_h))
        # テキスト
        stat_surf = stats_font.render(text, True, (0, 0, 0))
        screen.blit(stat_surf, (x0, y0 + i * line_h))
    
    # 勝率プログレスバー
    progress_x = x0
    progress_y = y0 + 5 * line_h + 5
    progress_width = 240  # 幅を小さく
    progress_height = 8
    
    # プログレスバー背景
    pygame.draw.rect(screen, (200, 200, 200), (progress_x, progress_y, progress_width, progress_height))
    pygame.draw.rect(screen, (100, 100, 100), (progress_x, progress_y, progress_width, progress_height), 1)
    
    # 勝率に応じたプログレス
    if total_games > 0:
        progress_fill = (win_rate / 100) * progress_width
        if progress_fill > 0:
            color = (0, 200, 0) if win_rate >= 50 else (255, 165, 0) if win_rate >= 30 else (255, 0, 0)
            pygame.draw.rect(screen, color, (progress_x, progress_y, progress_fill, progress_height))

def draw_ai_battle_progress_graphs(screen, learning_history, current_game, total_games, ai_learn_count, ai_win_count, ai_lose_count, ai_draw_count, ai_avg_reward, qtable, show_learning_progress=True):
    """
    AI同士の対戦中のリアルタイム学習進捗グラフを描画
    """
    # グラフエリアの設定（人間とAIの対戦と同じ左側配置）
    graph_area_x = 50  # 左側に配置
    graph_area_y = 50
    graph_area_width = 320
    graph_area_height = 400
    
    # グラフエリアの背景
    pygame.draw.rect(screen, (245, 245, 245), (graph_area_x, graph_area_y, graph_area_width, graph_area_height))
    pygame.draw.rect(screen, (200, 200, 200), (graph_area_x, graph_area_y, graph_area_width, graph_area_height), 2)
    
    # タイトル
    title_font = get_japanese_font(18)
    title_surface = title_font.render("🤖 AI対戦進捗", True, (50, 50, 50))
    screen.blit(title_surface, (graph_area_x + 10, graph_area_y + 10))
    
    # 学習進捗ON/OFFボタン
    progress_btn_rect = pygame.Rect(graph_area_x + graph_area_width - 80, graph_area_y + 5, 70, 25)
    btn_color = (100, 200, 100) if show_learning_progress else (200, 100, 100)
    pygame.draw.rect(screen, btn_color, progress_btn_rect)
    pygame.draw.rect(screen, (100, 100, 100), progress_btn_rect, 1)
    
    btn_font = get_japanese_font(12)
    btn_text = "ON" if show_learning_progress else "OFF"
    btn_surface = btn_font.render(btn_text, True, (255, 255, 255))
    btn_text_rect = btn_surface.get_rect(center=progress_btn_rect.center)
    screen.blit(btn_surface, btn_text_rect)
    
    if not show_learning_progress:
        # 学習進捗がOFFの場合は簡易表示のみ
        simple_font = get_japanese_font(16)
        y_pos = graph_area_y + 50
        
        # 現在のゲーム数
        game_text = f"ゲーム: {current_game}/{total_games}"
        game_surface = simple_font.render(game_text, True, (50, 50, 50))
        screen.blit(game_surface, (graph_area_x + 10, y_pos))
        y_pos += 30
        
        # 学習回数
        learn_text = f"学習回数: {ai_learn_count}"
        learn_surface = simple_font.render(learn_text, True, (50, 50, 50))
        screen.blit(learn_surface, (graph_area_x + 10, y_pos))
        y_pos += 30
        
        # 勝敗状況
        total_games_played = ai_win_count + ai_lose_count + ai_draw_count
        if total_games_played > 0:
            win_rate = (ai_win_count / total_games_played) * 100
            win_text = f"勝率: {win_rate:.1f}%"
            win_surface = simple_font.render(win_text, True, (50, 50, 50))
            screen.blit(win_surface, (graph_area_x + 10, y_pos))
            y_pos += 30
        
        # Qテーブルサイズ
        qtable_text = f"Qテーブル: {len(qtable)}"
        qtable_surface = simple_font.render(qtable_text, True, (50, 50, 50))
        screen.blit(qtable_surface, (graph_area_x + 10, y_pos))
        
        return progress_btn_rect
    
    # 学習進捗がONの場合の詳細表示
    content_y = graph_area_y + 50
    content_height = graph_area_height - 60
    section_height = content_height // 6  # 6分割
    section_spacing = 15
    
    # 1. ゲーム進捗グラフ
    draw_game_progress_mini_graph(screen, current_game, total_games, 
                                 graph_area_x + 4, content_y, graph_area_width - 14, section_height - 9)
    # 2. 勝率グラフ
    draw_win_rate_mini_graph(screen, ai_win_count, ai_lose_count, ai_draw_count,
                            graph_area_x + 4, content_y + section_height + section_spacing, graph_area_width - 14, section_height - 9)
    # 3. 学習回数グラフ（高さ1.5倍）
    draw_learn_count_mini_graph(screen, ai_learn_count, current_game,
                               graph_area_x + 4, content_y + (section_height + section_spacing) * 2, graph_area_width - 14, int((section_height - 9) * 1.5))
    # 4. Qテーブル成長グラフ（高さ1.5倍）
    draw_qtable_mini_graph(screen, len(qtable), current_game,
                          graph_area_x + 4, content_y + (section_height + section_spacing) * 2 + int((section_height - 9) * 1.5) + section_spacing, graph_area_width - 14, int((section_height - 9) * 1.5))
    
    return progress_btn_rect

def draw_game_progress_mini_graph(screen, current_game, total_games, x, y, width, height):
    """ゲーム進捗のミニグラフ"""
    # タイトル
    title_font = get_japanese_font(12)
    title_surface = title_font.render("🎮 ゲーム進捗", True, (50, 50, 50))
    screen.blit(title_surface, (x, y))
    
    # プログレスバー
    bar_y = y + 20
    bar_height = 15
    progress_ratio = current_game / total_games if total_games > 0 else 0
    
    # 背景
    pygame.draw.rect(screen, (220, 220, 220), (x, bar_y, width, bar_height))
    pygame.draw.rect(screen, (150, 150, 150), (x, bar_y, width, bar_height), 1)
    
    # 進捗
    if progress_ratio > 0:
        progress_width = int(width * progress_ratio)
        pygame.draw.rect(screen, (100, 200, 100), (x, bar_y, progress_width, bar_height))
    
    # テキスト
    text_font = get_japanese_font(10)
    text = f"{current_game}/{total_games} ({progress_ratio*100:.1f}%)"
    text_surface = text_font.render(text, True, (50, 50, 50))
    screen.blit(text_surface, (x, bar_y + bar_height + 5))

def draw_win_rate_mini_graph(screen, ai_win_count, ai_lose_count, ai_draw_count, x, y, width, height):
    """勝率のミニグラフ"""
    # タイトル
    title_font = get_japanese_font(12)
    title_surface = title_font.render("🏆 勝率", True, (50, 50, 50))
    screen.blit(title_surface, (x, y))
    
    total_games = ai_win_count + ai_lose_count + ai_draw_count
    if total_games == 0:
        text_font = get_japanese_font(10)
        text_surface = text_font.render("まだ対戦なし", True, (150, 150, 150))
        screen.blit(text_surface, (x, y + 20))
        return
    
    win_rate = (ai_win_count / total_games) * 100
    
    # 円グラフ風の表示
    center_x = x + width // 2
    center_y = y + 35
    radius = min(width // 4, height - 30)
    
    # 背景円
    pygame.draw.circle(screen, (220, 220, 220), (center_x, center_y), radius)
    pygame.draw.circle(screen, (150, 150, 150), (center_x, center_y), radius, 1)
    
    # 勝率の円弧
    if win_rate > 0:
        angle = (win_rate / 100) * 2 * math.pi
        points = [(center_x, center_y)]
        for i in range(int(angle * 20) + 1):
            t = i / 20
            px = center_x + radius * math.cos(t - math.pi/2)
            py = center_y + radius * math.sin(t - math.pi/2)
            points.append((px, py))
        if len(points) > 2:
            pygame.draw.polygon(screen, (100, 200, 100), points)
    
    # テキスト
    text_font = get_japanese_font(10)
    text = f"{win_rate:.1f}% ({ai_win_count}勝/{total_games}戦)"
    text_surface = text_font.render(text, True, (50, 50, 50))
    screen.blit(text_surface, (x, y + height - 15))

def draw_learn_count_mini_graph(screen, ai_learn_count, current_game, x, y, width, height):
    """学習回数のミニグラフ（見やすさ改善版）"""
    # タイトル
    title_font = get_japanese_font(13)  # フォントサイズを大きく
    title_surface = title_font.render("⚡ 学習回数", True, (30, 30, 30))  # 色を濃く
    screen.blit(title_surface, (x, y))

    # 学習効率の計算
    learn_per_game = ai_learn_count / current_game if current_game > 0 else 0

    # 折れ線グラフ風の表示（Qテーブル成長グラフと同様のスタイル）
    graph_y = y + 22  # タイトル下の余白を少し増やす
    graph_width = width - 25  # 余白を少し増やす
    graph_height = height - 40  # 余白を少し増やす
    graph_x = x + 12

    # 背景（より濃い色でコントラスト向上）
    pygame.draw.rect(screen, (240, 240, 245), (graph_x, graph_y, graph_width, graph_height))
    pygame.draw.rect(screen, (180, 180, 180), (graph_x, graph_y, graph_width, graph_height), 2)

    # 目盛り（縦軸：学習回数）- フォントサイズを大きく
    tick_font = get_japanese_font(10)  # 9px → 10px
    max_learn = max(ai_learn_count, 100)
    for i in range(5):
        tick_y = graph_y + (i * graph_height // 4)
        pygame.draw.line(screen, (210, 210, 210), (graph_x, tick_y), (graph_x + graph_width, tick_y), 1)
        tick_val = max_learn - (i * max_learn // 4)
        tick_label = tick_font.render(f"{int(tick_val)}", True, (100, 100, 100))  # 色を濃く
        screen.blit(tick_label, (graph_x - 32, tick_y - 8))  # 位置調整

    # 横軸（ゲーム数）- フォントサイズを大きく
    if current_game > 1:
        for i in range(5):
            tick_x = graph_x + (i * graph_width // 4)
            pygame.draw.line(screen, (210, 210, 210), (tick_x, graph_y), (tick_x, graph_y + graph_height), 1)
            tick_val = int(i * current_game // 4)
            tick_label = tick_font.render(f"{tick_val}", True, (100, 100, 100))  # 色を濃く
            screen.blit(tick_label, (tick_x - 10, graph_y + graph_height + 1))  # 位置調整

    # 学習回数のライン（色を鮮明に、線を太く）
    if ai_learn_count > 0 and current_game > 1:
        # 直線（最初から現在まで）- 緑色で鮮明に
        start_x = graph_x
        end_x = graph_x + graph_width
        start_y = graph_y + graph_height
        end_y = graph_y + graph_height - (ai_learn_count / max_learn) * graph_height
        
        # グラデーション効果（線の太さを3pxに）
        for i in range(3):
            offset = i - 1
            line_color = (60, 200 + i*20, 60 + i*10)  # 緑系グラデーション
            pygame.draw.line(screen, line_color, 
                           (start_x + offset, start_y + offset), 
                           (end_x + offset, end_y + offset), 1)

    
    # 横軸ラベル（フォントサイズを大きく）
    x_label_font = get_japanese_font(10)  # 9px → 10px
    x_label = x_label_font.render("ゲーム数", True, (60, 60, 60))  # 色を濃く
    screen.blit(x_label, (graph_x + graph_width//2 - x_label.get_width()//2, graph_y + graph_height + 13))

    # テキスト（フォントサイズを大きく）
    text_font = get_japanese_font(11)  # 10px → 11px
    text = f"総学習: {ai_learn_count}回 (1ゲームあたり: {learn_per_game:.1f})"
    text_surface = text_font.render(text, True, (30, 30, 30))  # 色を濃く
    screen.blit(text_surface, (x, y + height - 18))

def draw_qtable_mini_graph(screen, qtable_size, current_game, x, y, width, height):
    """Qテーブル成長のミニグラフ（見やすさ改善版）"""
    # タイトル
    title_font = get_japanese_font(13)  # フォントサイズを大きく
    title_surface = title_font.render("🧠 Qテーブル成長", True, (30, 30, 30))  # 色を濃く
    screen.blit(title_surface, (x, y))
    
    # 成長率の計算
    growth_per_game = qtable_size / current_game if current_game > 0 else 0
    
    # 折れ線グラフ風の表示
    graph_y = y + 22  # タイトル下の余白を少し増やす
    graph_width = width - 25  # 余白を少し増やす
    graph_height = height - 40  # 余白を少し増やす
    graph_x = x + 12

    # 背景（より濃い色でコントラスト向上）
    pygame.draw.rect(screen, (240, 240, 245), (graph_x, graph_y, graph_width, graph_height))
    pygame.draw.rect(screen, (180, 180, 180), (graph_x, graph_y, graph_width, graph_height), 2)

    # 目盛り（縦軸：Qテーブルサイズ）- フォントサイズを大きく
    tick_font = get_japanese_font(1)  # 0px
    max_size = max(qtable_size, 100)
    for i in range(5):
        tick_y = graph_y + (i * graph_height // 4)
        pygame.draw.line(screen, (210, 210, 210), (graph_x, tick_y), (graph_x + graph_width, tick_y), 1)
        tick_val = max_size - (i * max_size // 4)
        tick_label = tick_font.render(f"{int(tick_val)}", True, (100, 100, 100))  # 色を濃く
        screen.blit(tick_label, (graph_x - 32, tick_y - 8))  # 位置調整

    # 横軸（ゲーム数）- フォントサイズを大きく
    if current_game > 1:
        for i in range(5):
            tick_x = graph_x + (i * graph_width // 4)
            pygame.draw.line(screen, (210, 210, 210), (tick_x, graph_y), (tick_x, graph_y + graph_height), 1)
            tick_val = int(i * current_game // 4)
            tick_label = tick_font.render(f"{tick_val}", True, (100, 100, 100))  # 色を濃く
            screen.blit(tick_label, (tick_x - 10, graph_y + graph_height + 3))  # 位置調整

    # 成長ライン（色を鮮明に、線を太く）
    if qtable_size > 0 and current_game > 1:
        # 直線（最初から現在まで）- オレンジ色で鮮明に
        start_x = graph_x
        end_x = graph_x + graph_width
        start_y = graph_y + graph_height
        end_y = graph_y + graph_height - (qtable_size / max_size) * graph_height
        
        # グラデーション効果（線の太さを2pxに）
        for i in range(2):
            offset = i - 1.5
            line_color = (255, 140, 60)
            pygame.draw.line(screen, line_color, 
                           (start_x + offset, start_y + offset), 
                           (end_x + offset, end_y + offset), 1)

    
    # 横軸ラベル（フォントサイズを大きく）
    x_label_font = get_japanese_font(9)  # 9px
    x_label = x_label_font.render("ゲーム数", True, (60, 60, 60))  # 色を濃く
    screen.blit(x_label, (graph_x + graph_width//2 - x_label.get_width()//2, graph_y + graph_height + 18))

    # テキスト（フォントサイズを大きく）
    text_font = get_japanese_font(9)  # 10px
    text = f"サイズ: {qtable_size} (成長率: {growth_per_game:.1f}/ゲーム)"
    text_surface = text_font.render(text, True, (30, 30, 30))  # 色を濃く
    screen.blit(text_surface, (x, y + height - 20))