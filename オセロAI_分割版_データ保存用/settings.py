import pygame
import sys
import json
import os
import math
from constants import *
from ui_components import get_japanese_font

# 画面サイズ設定ファイル
WINDOW_SIZE_CONFIG_FILE = "window_size_config.json"

def load_window_size_config():
    """画面サイズ設定を読み込み"""
    default_config = {
        "width": WINDOW_WIDTH,
        "height": WINDOW_HEIGHT
    }
    
    try:
        if os.path.exists(WINDOW_SIZE_CONFIG_FILE):
            with open(WINDOW_SIZE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("width", WINDOW_WIDTH), config.get("height", WINDOW_HEIGHT)
    except Exception as e:
        print(f"画面サイズ設定の読み込みエラー: {e}")
    
    return WINDOW_WIDTH, WINDOW_HEIGHT

def save_window_size_config(width, height):
    """画面サイズ設定を保存"""
    try:
        config = {
            "width": width,
            "height": height
        }
        with open(WINDOW_SIZE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"画面サイズ設定を保存しました: {width}x{height}")
    except Exception as e:
        print(f"画面サイズ設定の保存エラー: {e}")

def settings_screen(screen, font, debug_mode, ai_speed, draw_mode, pretrain_total):
    """設定画面 - 詳細で魅力的なUI版"""
    global WINDOW_WIDTH, WINDOW_HEIGHT
    
    print(f"設定画面: 初期化 - 受け取った値 - pretrain_total: {pretrain_total}")
    
    # 現在の画面サイズを読み込み
    current_width, current_height = load_window_size_config()
    
    # 設定項目の入力モード
    input_modes = {
        'ai_speed': False,
        'pretrain_total': False,
        'alpha': False,
        'gamma': False,
        'epsilon': False,
        'window_width': False,
        'window_height': False
    }
    
    # 入力テキスト
    input_texts = {
        'ai_speed': str(ai_speed),
        'pretrain_total': str(pretrain_total),
        'alpha': str(0.1),  # デフォルト値
        'gamma': str(0.9),  # デフォルト値
        'epsilon': str(0.1),  # デフォルト値
        'window_width': str(current_width),
        'window_height': str(current_height)
    }
    
    # ローカル変数として設定値を管理
    local_debug_mode = debug_mode
    local_ai_speed = ai_speed
    local_draw_mode = draw_mode
    local_pretrain_total = pretrain_total
    local_fast_mode = True  # デフォルト値
    local_alpha = 0.1  # デフォルト値
    local_gamma = 0.9  # デフォルト値
    local_epsilon = 0.1  # デフォルト値
    local_window_width = current_width
    local_window_height = current_height
    
    # プリセットサイズ
    preset_sizes = [
        ("小", 1000, 700),
        ("標準", 1200, 800),
        ("大", 1400, 900),
        ("ワイド", 1600, 800),
        ("スクエア", 1200, 1200)
    ]
    
    # スライダー用の変数
    slider_dragging = None
    slider_values = {
        'ai_speed': (ai_speed - 10) / (1000 - 10),  # 0-1の範囲に正規化
        'pretrain_total': (pretrain_total - 1) / (100 - 1),  # 1-100の範囲
        'alpha': 0.1,  # 0-1の範囲
        'gamma': 0.9,  # 0-1の範囲
        'epsilon': 0.1  # 0-1の範囲
    }
    
    # 入力テキストをスライダー値に合わせて更新
    input_texts['alpha'] = f"{slider_values['alpha']:.2f}"
    input_texts['gamma'] = f"{slider_values['gamma']:.2f}"
    input_texts['epsilon'] = f"{slider_values['epsilon']:.2f}"
    
    # タブ管理
    current_tab = 0
    tabs = ["🎮 ゲーム", "🤖 AI学習", "🖥️ 表示", "⚙️ 高度設定"]
    
    # アニメーション用変数
    animation_time = 0
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        animation_time += 1
        
        for event in pygame.event.get():
            global WINDOW_WIDTH, WINDOW_HEIGHT
            if event.type == pygame.QUIT:
                # 設定画面だけ閉じる
                break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                # タブクリック判定
                tab_clicked = handle_tab_click(mouse_pos, tabs, current_tab)
                if tab_clicked is not None:
                    current_tab = tab_clicked
                # カスタム入力フィールドのクリック判定
                for key in input_modes:
                    if key in ['ai_speed', 'pretrain_total', 'alpha', 'gamma', 'epsilon', 'window_width', 'window_height']:
                        input_rect = None  # 初期化
                        # 各設定項目の入力フィールドの位置を計算
                        if current_tab == 0:  # ゲーム設定タブ
                            if key == 'ai_speed':
                                input_rect = pygame.Rect(WINDOW_WIDTH - 170, 150, 150, 50)
                            elif key == 'pretrain_total':
                                input_rect = pygame.Rect(WINDOW_WIDTH - 170, 250, 150, 50)
                        elif current_tab == 1:  # AI学習設定タブ
                            if key == 'alpha':
                                input_rect = pygame.Rect(WINDOW_WIDTH - 170, 150, 150, 50)
                            elif key == 'gamma':
                                input_rect = pygame.Rect(WINDOW_WIDTH - 170, 250, 150, 50)
                            elif key == 'epsilon':
                                input_rect = pygame.Rect(WINDOW_WIDTH - 170, 350, 150, 50)
                        elif current_tab == 3:  # 高度設定タブ
                            if key == 'window_width':
                                input_rect = pygame.Rect(WINDOW_WIDTH - 170, 150, 150, 50)
                            elif key == 'window_height':
                                input_rect = pygame.Rect(WINDOW_WIDTH - 170, 250, 150, 50)
                        
                        # input_rectが定義されている場合のみクリック判定
                        if input_rect and input_rect.collidepoint(mouse_pos):
                            input_modes[key] = True
                            # 他の入力モードを無効化
                            for other_key in input_modes:
                                if other_key != key:
                                    input_modes[other_key] = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pass
            elif event.type == pygame.MOUSEMOTION:
                pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESCキーで戻る場合、現在の入力値を保存してから戻る
                    print(f"設定画面: ESCキーで戻る - 現在の値 - pretrain_total: {local_pretrain_total}")
                    # 設定値を返す
                    return local_debug_mode, local_ai_speed, local_draw_mode, local_pretrain_total, local_fast_mode, local_draw_mode, local_debug_mode, local_window_width, local_window_height
                elif event.key == pygame.K_RETURN:
                    # 現在の入力モードを終了
                    for key in input_modes:
                        if input_modes[key]:
                            try:
                                if key == 'ai_speed':
                                    local_ai_speed = int(input_texts[key])
                                    print(f"設定画面: AI思考速度を変更しました: {local_ai_speed}")
                                elif key == 'pretrain_total':
                                    local_pretrain_total = int(input_texts[key])
                                    print(f"設定画面: 事前訓練回数を変更しました: {local_pretrain_total}")
                                elif key == 'alpha':
                                    local_alpha = float(input_texts[key])
                                elif key == 'gamma':
                                    local_gamma = float(input_texts[key])
                                elif key == 'epsilon':
                                    local_epsilon = float(input_texts[key])
                                elif key == 'window_width':
                                    local_window_width = int(input_texts[key])
                                    # 画面サイズを即座に変更
                                    WINDOW_WIDTH = local_window_width
                                    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                                    save_window_size_config(WINDOW_WIDTH, WINDOW_HEIGHT)
                                    print(f"ウィンドウ幅を変更しました: {WINDOW_WIDTH}")
                                elif key == 'window_height':
                                    local_window_height = int(input_texts[key])
                                    # 画面サイズを即座に変更
                                    WINDOW_HEIGHT = local_window_height
                                    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                                    save_window_size_config(WINDOW_WIDTH, WINDOW_HEIGHT)
                                    print(f"ウィンドウ高さを変更しました: {WINDOW_HEIGHT}")
                            except ValueError:
                                # 無効な値の場合は元の値に戻す
                                if key == 'ai_speed':
                                    input_texts[key] = str(local_ai_speed)
                                elif key == 'pretrain_total':
                                    input_texts[key] = str(local_pretrain_total)
                                elif key == 'alpha':
                                    input_texts[key] = str(local_alpha)
                                elif key == 'gamma':
                                    input_texts[key] = str(local_gamma)
                                elif key == 'epsilon':
                                    input_texts[key] = str(local_epsilon)
                                elif key == 'window_width':
                                    input_texts[key] = str(local_window_width)
                                elif key == 'window_height':
                                    input_texts[key] = str(local_window_height)
                            input_modes[key] = False
                elif event.key == pygame.K_BACKSPACE:
                    # 現在の入力モードのテキストを編集
                    for key in input_modes:
                        if input_modes[key] and input_texts[key]:
                            input_texts[key] = input_texts[key][:-1]
                elif event.unicode.isnumeric() or event.unicode == '.':
                    # 現在の入力モードのテキストに追加
                    for key in input_modes:
                        if input_modes[key]:
                            # 小数点の重複を防ぐ
                            if event.unicode == '.' and '.' in input_texts[key]:
                                continue
                            input_texts[key] += event.unicode
        
        # 背景を描画（魅力的なグラデーション）
        draw_romantic_background(screen, animation_time)
        
        # タイトル
        draw_animated_title(screen, "⚙️ 設定センター", animation_time)
        
        # タブバーを描画
        draw_tab_bar(screen, tabs, current_tab, mouse_pos, mouse_down, font)
        
        # タブコンテンツを描画
        if current_tab == 0:  # ゲーム設定
            draw_game_settings_tab(screen, input_texts, input_modes, slider_values, 
                                 mouse_pos, mouse_down, font, animation_time)
        elif current_tab == 1:  # AI学習設定
            draw_ai_learning_tab(screen, input_texts, input_modes, slider_values, 
                               mouse_pos, mouse_down, font, animation_time)
        elif current_tab == 2:  # 表示設定
            local_draw_mode, local_fast_mode, local_debug_mode = draw_display_settings_tab(screen, local_draw_mode, local_fast_mode, local_debug_mode,
                                    preset_sizes, mouse_pos, mouse_down, font, animation_time)
        elif current_tab == 3:  # 高度設定
            draw_advanced_settings_tab(screen, input_texts, input_modes, slider_values,
                                     mouse_pos, mouse_down, font, animation_time)
        
        # ボタン群（下部）
        button_result = draw_romantic_button_group(screen, mouse_pos, mouse_down, font, animation_time)
        if button_result == "back":
            # 戻るボタンが押された場合、現在の値を保存してから戻る
            print(f"設定画面: 戻るボタンで戻る - 現在の値 - pretrain_total: {local_pretrain_total}")
            # 設定値を返す
            return local_debug_mode, local_ai_speed, local_draw_mode, local_pretrain_total, local_fast_mode, local_draw_mode, local_debug_mode, local_window_width, local_window_height
        elif button_result == "default":
            # デフォルトボタンが押された場合、デフォルト値にリセット
            local_ai_speed = 60
            local_draw_mode = True
            local_pretrain_total = 10
            local_fast_mode = True
            local_debug_mode = False
            local_alpha = 0.1
            local_gamma = 0.9
            local_epsilon = 0.1
            local_window_width = 1200
            local_window_height = 800
            # 入力テキストも更新
            input_texts['ai_speed'] = str(local_ai_speed)
            input_texts['pretrain_total'] = str(local_pretrain_total)
            input_texts['alpha'] = str(local_alpha)
            input_texts['gamma'] = str(local_gamma)
            input_texts['epsilon'] = str(local_epsilon)
            input_texts['window_width'] = str(local_window_width)
            input_texts['window_height'] = str(local_window_height)
            # 画面サイズも即座に変更
            WINDOW_WIDTH = local_window_width
            WINDOW_HEIGHT = local_window_height
            pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            save_window_size_config(WINDOW_WIDTH, WINDOW_HEIGHT)
            print("設定をデフォルト値にリセットしました")
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    
    # 設定値を返す
    print(f"設定画面: 返される値 - pretrain_total: {local_pretrain_total}")
    return local_debug_mode, local_ai_speed, local_draw_mode, local_pretrain_total, local_fast_mode, local_draw_mode, local_debug_mode, local_window_width, local_window_height

def draw_gradient_background(screen):
    """グラデーション風の背景を描画"""
    for y in range(WINDOW_HEIGHT):
        ratio = y / WINDOW_HEIGHT
        r = int(240 + (220 - 240) * ratio)
        g = int(240 + (230 - 240) * ratio)
        b = int(240 + (250 - 240) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

def draw_category_title(screen, title, y, x_offset=0):
    """カテゴリタイトルを描画"""
    font = get_japanese_font(24)
    text = font.render(title, True, (80, 80, 120))
    if x_offset == 0:
        screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, y))
    else:
        screen.blit(text, (x_offset, y))

def draw_enhanced_toggle_setting(screen, title, value, description, x, y, width, height, 
                               mouse_pos, mouse_down, font):
    """強化されたトグル設定項目を描画"""
    rect = pygame.Rect(x, y, width, height)
    is_hover = rect.collidepoint(mouse_pos)
    
    # 背景
    color = (220, 220, 240) if is_hover else (200, 200, 220)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 150), rect, 2)
    
    # アイコン（設定項目の種類を示す）
    icon_size = 20
    icon_x = x + 15
    icon_y = y + (height - icon_size) // 2
    
    # アイコンを描画（円形）
    icon_color = (50, 150, 200) if value else (150, 150, 150)
    pygame.draw.circle(screen, icon_color, (icon_x + icon_size//2, icon_y + icon_size//2), icon_size//2)
    pygame.draw.circle(screen, (30, 30, 30), (icon_x + icon_size//2, icon_y + icon_size//2), icon_size//2, 2)
    
    # タイトル（アイコンの右側）
    title_x = icon_x + icon_size + 15
    title_surface = font.render(title, True, (50, 50, 100))
    screen.blit(title_surface, (title_x, y + 8))
    
    # 説明（タイトルの下、短縮版）
    desc_font = get_japanese_font(10)  # 12から10に変更
    # 説明文を短縮して表示
    short_desc = description[:18] + "..." if len(description) > 18 else description
    desc_surface = desc_font.render(short_desc, True, (100, 100, 100))
    screen.blit(desc_surface, (title_x, y + 30))
    
    # ホバー時に詳細説明をツールチップで表示
    if is_hover and len(description) > 18:
        tooltip_font = get_japanese_font(10)
        tooltip_surface = tooltip_font.render(description, True, (255, 255, 255))
        tooltip_rect = tooltip_surface.get_rect()
        tooltip_rect.x = mouse_pos[0] + 10
        tooltip_rect.y = mouse_pos[1] - tooltip_rect.height - 10
        
        # ツールチップの背景
        tooltip_bg_rect = tooltip_rect.inflate(10, 5)
        pygame.draw.rect(screen, (50, 50, 50), tooltip_bg_rect)
        pygame.draw.rect(screen, (100, 100, 100), tooltip_bg_rect, 1)
        screen.blit(tooltip_surface, tooltip_rect)
    
    # トグルボタン（枠外の右側に配置）
    toggle_width = 50
    toggle_height = 30
    toggle_x = x + width + 20  # 枠外の右側に20px間隔
    toggle_y = y + (height - toggle_height) // 2  # 垂直中央
    
    toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_width, toggle_height)
    toggle_color = (50, 200, 50) if value else (200, 50, 50)
    pygame.draw.rect(screen, toggle_color, toggle_rect)
    pygame.draw.rect(screen, (30, 30, 30), toggle_rect, 2)
    
    # トグル状態のテキスト
    toggle_text = "ON" if value else "OFF"
    toggle_text_surface = get_japanese_font(14).render(toggle_text, True, (255, 255, 255))
    toggle_text_rect = toggle_text_surface.get_rect(center=toggle_rect.center)
    screen.blit(toggle_text_surface, toggle_text_rect)
    
    # クリックでトグル（トグルボタンのみ）
    if mouse_down and toggle_rect.collidepoint(mouse_pos):
        value = not value
    
    return value

def draw_button_group(screen, mouse_pos, mouse_down, font):
    """ボタン群を描画"""
    button_y = WINDOW_HEIGHT - 80
    
    # デフォルト値ボタン
    default_button = pygame.Rect(WINDOW_WIDTH//2 - 200, button_y, 120, 50)  # 高さを40から50に変更
    default_color = (180, 180, 200) if default_button.collidepoint(mouse_pos) else (160, 160, 180)
    pygame.draw.rect(screen, default_color, default_button)
    pygame.draw.rect(screen, (100, 100, 150), default_button, 2)
    default_text = font.render("デフォルト", True, (50, 50, 100))
    default_text_rect = default_text.get_rect(center=default_button.center)
    screen.blit(default_text, default_text_rect)
    
    # 戻るボタン
    back_button = pygame.Rect(WINDOW_WIDTH//2 + 80, button_y, 120, 50)  # 高さを40から50に変更
    back_color = (180, 180, 200) if back_button.collidepoint(mouse_pos) else (160, 160, 180)
    pygame.draw.rect(screen, back_color, back_button)
    pygame.draw.rect(screen, (100, 100, 150), back_button, 2)
    back_text = font.render("戻る", True, (50, 50, 100))
    back_text_rect = back_text.get_rect(center=back_button.center)
    screen.blit(back_text, back_text_rect)
    
    # 操作説明
    help_font = get_japanese_font(14)
    help_text = help_font.render("ESCキーまたは戻るボタンでモード選択に戻ります", True, (100, 100, 100))
    help_rect = help_text.get_rect(center=(WINDOW_WIDTH//2, button_y - 25))  # 位置を調整
    screen.blit(help_text, help_rect)
    
    # ボタンクリック判定
    if mouse_down:
        if default_button.collidepoint(mouse_pos):
            # デフォルト値にリセット
            pass  # 後で実装
        elif back_button.collidepoint(mouse_pos):
            return True  # 戻るボタンが押された
    
    return False

def draw_setting_item(screen, title, value, description, is_input_mode, x, y, width, height, 
                     mouse_pos, mouse_down, font, small_font, tiny_font):
    """設定項目を描画（旧版）"""
    rect = pygame.Rect(x, y, width, height)
    is_hover = rect.collidepoint(mouse_pos)
    
    # 背景
    color = (220, 220, 220) if is_hover else (200, 200, 200)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    # タイトル
    title_surface = font.render(title, True, (0, 0, 0))
    screen.blit(title_surface, (x + 10, y + 10))
    
    # 値
    value_color = (255, 0, 0) if is_input_mode else (0, 0, 0)
    value_surface = small_font.render(value, True, value_color)
    screen.blit(value_surface, (x + 10, y + 35))
    
    # 説明
    desc_surface = tiny_font.render(description, True, (100, 100, 100))
    screen.blit(desc_surface, (x + 10, y + 55))
    
    # クリックで入力モードに切り替え
    return mouse_down and is_hover

def draw_toggle_setting(screen, title, value, description, x, y, width, height, 
                       mouse_pos, mouse_down, font, small_font):
    """トグル設定項目を描画（旧版）"""
    rect = pygame.Rect(x, y, width, height)
    is_hover = rect.collidepoint(mouse_pos)
    
    # 背景
    color = (220, 220, 220) if is_hover else (200, 200, 200)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    # タイトル
    title_surface = font.render(title, True, (0, 0, 0))
    screen.blit(title_surface, (x + 10, y + 10))
    
    # 説明
    desc_surface = small_font.render(description, True, (100, 100, 100))
    screen.blit(desc_surface, (x + 10, y + 35))
    
    # トグルボタン
    toggle_x = x + width - 80
    toggle_y = y + 15
    toggle_width = 60
    toggle_height = 30
    
    toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_width, toggle_height)
    toggle_color = (0, 255, 0) if value else (255, 0, 0)
    pygame.draw.rect(screen, toggle_color, toggle_rect)
    pygame.draw.rect(screen, (0, 0, 0), toggle_rect, 2)
    
    # トグル状態のテキスト
    toggle_text = "ON" if value else "OFF"
    toggle_text_surface = small_font.render(toggle_text, True, (255, 255, 255))
    toggle_text_rect = toggle_text_surface.get_rect(center=toggle_rect.center)
    screen.blit(toggle_text_surface, toggle_text_rect)
    
    # クリックでトグル
    if mouse_down and toggle_rect.collidepoint(mouse_pos):
        value = not value
    
    return value

def draw_input_setting(screen, title, value, description, input_key, x, y, width, height, 
                       mouse_pos, mouse_down, font, input_modes):
    """ユーザー入力可能な設定項目を描画"""
    rect = pygame.Rect(x, y, width, height)
    is_hover = rect.collidepoint(mouse_pos)
    is_input_mode = input_modes.get(input_key, False)
    
    # 背景
    color = (220, 220, 240) if is_hover else (200, 200, 220)
    if is_input_mode:
        color = (255, 255, 200)  # 入力モード時は黄色っぽく
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 150), rect, 2)
    
    # タイトル
    title_surface = font.render(title, True, (50, 50, 100))
    screen.blit(title_surface, (x + 15, y + 8))
    
    # 値表示（入力モード時は強調、大きな文字で）
    value_font = get_japanese_font(20)  # 16から20に変更
    value_color = (255, 0, 0) if is_input_mode else (0, 0, 0)
    value_surface = value_font.render(value, True, value_color)
    screen.blit(value_surface, (x + 15, y + 35))  # y位置を調整
    
    # 説明（短縮版）
    desc_font = get_japanese_font(10)  # 11から10に変更
    # 説明文を短縮して表示
    short_desc = description[:20] + "..." if len(description) > 20 else description
    desc_surface = desc_font.render(short_desc, True, (100, 100, 100))
    screen.blit(desc_surface, (x + 15, y + 60))  # y位置を調整
    
    # ホバー時に詳細説明をツールチップで表示
    if is_hover and len(description) > 20:
        tooltip_font = get_japanese_font(10)
        tooltip_surface = tooltip_font.render(description, True, (255, 255, 255))
        tooltip_rect = tooltip_surface.get_rect()
        tooltip_rect.x = mouse_pos[0] + 10
        tooltip_rect.y = mouse_pos[1] - tooltip_rect.height - 10
        
        # ツールチップの背景
        tooltip_bg_rect = tooltip_rect.inflate(10, 5)
        pygame.draw.rect(screen, (50, 50, 50), tooltip_bg_rect)
        pygame.draw.rect(screen, (100, 100, 100), tooltip_bg_rect, 1)
        screen.blit(tooltip_surface, tooltip_rect)
    
    # 入力用アイコン（欄外の右側に配置）
    icon_size = 20  # 16から20に変更
    icon_x = x + width + 20  # 欄外の右側に20px間隔
    icon_y = y + (height - icon_size) // 2  # 垂直中央
    
    # アイコンを描画（編集アイコン - 鉛筆の形）
    if is_input_mode:
        # 入力モード時は強調色
        pygame.draw.rect(screen, (255, 200, 50), (icon_x, icon_y, icon_size, icon_size))
        pygame.draw.rect(screen, (200, 150, 0), (icon_x, icon_y, icon_size, icon_size), 2)
    else:
        # 通常時
        icon_color = (50, 150, 200) if is_hover else (150, 150, 150)
        pygame.draw.rect(screen, icon_color, (icon_x, icon_y, icon_size, icon_size))
        pygame.draw.rect(screen, (30, 30, 30), (icon_x, icon_y, icon_size, icon_size), 2)
    
    # 鉛筆の先端部分
    pencil_tip_x = icon_x + icon_size - 5
    pencil_tip_y = icon_y + 3
    pygame.draw.polygon(screen, (100, 100, 100), [
        (pencil_tip_x, pencil_tip_y),
        (pencil_tip_x + 5, pencil_tip_y + 2),
        (pencil_tip_x, pencil_tip_y + 5)
    ])
    
    # クリックで入力モードに切り替え
    if mouse_down and rect.collidepoint(mouse_pos):
        # 他の入力モードを全てオフにする
        for key in input_modes:
            input_modes[key] = False
        # この項目の入力モードをオンにする
        input_modes[input_key] = True

def draw_preset_size_buttons_improved(screen, preset_sizes, x, y, mouse_pos, mouse_down, font, input_texts, input_modes):
    """プリセットサイズボタンを描画"""
    button_width = 80
    button_height = 40
    button_spacing = 10
    
    # タイトル
    title_font = get_japanese_font(16)
    title = title_font.render("プリセットサイズ:", True, (50, 50, 100))
    screen.blit(title, (x, y))
    
    y += 30
    
    for i, (name, width, height) in enumerate(preset_sizes):
        button_x = x + (button_width + button_spacing) * (i % 3)
        button_y = y + (button_height + button_spacing) * (i // 3)
        
        # ボタンの背景
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (150, 200, 255), button_rect, border_radius=5)
            if mouse_down:
                # プリセットサイズを入力フィールドに設定
                input_texts['window_width'] = str(width)
                input_texts['window_height'] = str(height)
        else:
            pygame.draw.rect(screen, (200, 200, 200), button_rect, border_radius=5)
        
        pygame.draw.rect(screen, (100, 100, 100), button_rect, 2, border_radius=5)
        
        # ボタンテキスト
        button_text = font.render(name, True, (0, 0, 0))
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
        
        # サイズ表示
        size_text = get_japanese_font(12).render(f"{width}x{height}", True, (80, 80, 80))
        size_rect = size_text.get_rect(center=(button_rect.centerx, button_rect.bottom + 10))
        screen.blit(size_text, size_rect)
    
    # 次の項目のy位置を返す（2行分のボタンがある場合を考慮）
    return y + (button_height + button_spacing) * 2 + 20

def draw_improved_background(screen):
    """シンプルなグラデーション風の背景を描画"""
    for y in range(WINDOW_HEIGHT):
        ratio = y / WINDOW_HEIGHT
        r = int(240 + (220 - 240) * ratio)
        g = int(240 + (230 - 240) * ratio)
        b = int(240 + (250 - 240) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

def draw_romantic_section_header(screen, title, y, animation_time):
    """魅力的なセクションヘッダーを描画"""
    # 背景の装飾
    header_rect = pygame.Rect(50, y, WINDOW_WIDTH - 100, 40)
    wave = math.sin(animation_time * 0.05) * 0.2 + 0.8
    color = (int(40 * wave), int(60 * wave), int(100 * wave))
    pygame.draw.rect(screen, color, header_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 150, 255), header_rect, 2, border_radius=10)
    
    # タイトル
    title_font = get_japanese_font(24)
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=header_rect.center)
    screen.blit(title_surface, title_rect)

def draw_romantic_slider_setting(screen, title, value, display_value, description, y, mouse_pos, mouse_down, font, animation_time):
    """カスタム入力設定項目を描画"""
    rect = pygame.Rect(100, y, WINDOW_WIDTH - 200, 80)  # 高さを60から80に増加
    is_hover = rect.collidepoint(mouse_pos)
    
    # 背景（黒背景に合わせたグラデーション）
    for i in range(rect.height):
        ratio = i / rect.height
        wave = math.sin(animation_time * 0.03 + ratio * 3.14) * 0.1
        r = int(max(0, min(255, 30 + (50 - 30) * ratio + wave * 20)))
        g = int(max(0, min(255, 40 + (60 - 40) * ratio + wave * 15)))
        b = int(max(0, min(255, 50 + (70 - 50) * ratio + wave * 10)))
        pygame.draw.line(screen, (r, g, b), (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
    
    pygame.draw.rect(screen, (100, 150, 255), rect, 2, border_radius=8)
    
    # タイトル（左側）
    title_surface = font.render(title, True, (200, 220, 255))
    screen.blit(title_surface, (110, y + 10))
    
    # 説明（左側、タイトルの下）
    desc_font = get_japanese_font(12)
    desc_surface = desc_font.render(description, True, (180, 200, 255))
    screen.blit(desc_surface, (110, y + 35))
    
    # カスタム入力フィールド（右端）
    input_width = 150
    input_x = rect.x + rect.width - input_width - 20
    input_y = y + 15
    input_rect = pygame.Rect(input_x, input_y, input_width, 50)
    
    # 入力フィールドの背景
    input_color = (60, 80, 120) if is_hover else (50, 70, 110)
    pygame.draw.rect(screen, input_color, input_rect, border_radius=8)
    pygame.draw.rect(screen, (100, 150, 255), input_rect, 2, border_radius=8)
    
    # 入力テキスト
    text_surface = font.render(display_value, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=input_rect.center)
    screen.blit(text_surface, text_rect)
    
    return y + 100  # 次の項目のy位置を調整

def draw_romantic_toggle(screen, title, value, description, y, mouse_pos, mouse_down, font, animation_time):
    """魅力的なトグル設定項目を描画"""
    rect = pygame.Rect(WINDOW_WIDTH//2 - 200, y, 400, 70)  # 高さを60から70に増加
    is_hover = rect.collidepoint(mouse_pos)
    
    # 背景（黒背景に合わせたグラデーション）
    for i in range(rect.height):
        ratio = i / rect.height
        wave = math.sin(animation_time * 0.03 + ratio * 3.14) * 0.1
        r = int(max(0, min(255, 30 + (50 - 30) * ratio + wave * 20)))
        g = int(max(0, min(255, 40 + (60 - 40) * ratio + wave * 15)))
        b = int(max(0, min(255, 50 + (70 - 50) * ratio + wave * 10)))
        pygame.draw.line(screen, (r, g, b), (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
    
    pygame.draw.rect(screen, (100, 150, 255), rect, 2, border_radius=8)
    
    # タイトル（上部）
    title_surface = font.render(title, True, (200, 220, 255))
    screen.blit(title_surface, (rect.x + 10, y + 5))
    
    # 説明（中部）
    desc_font = get_japanese_font(12)
    desc_surface = desc_font.render(description, True, (180, 200, 255))
    screen.blit(desc_surface, (rect.x + 10, y + 30))
    
    # トグルボタン（右側）
    toggle_x = rect.x + rect.width - 120
    toggle_y = y + 20  # 位置を調整
    toggle_width = 100
    toggle_height = 30
    
    toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_width, toggle_height)
    
    # トグル背景
    bg_color = (0, 200, 100) if value else (200, 50, 50)
    pygame.draw.rect(screen, bg_color, toggle_rect, border_radius=15)
    pygame.draw.rect(screen, (255, 255, 255), toggle_rect, 2, border_radius=15)
    
    # トグル状態のテキスト
    toggle_text = "ON" if value else "OFF"
    toggle_text_surface = font.render(toggle_text, True, (255, 255, 255))
    toggle_text_rect = toggle_text_surface.get_rect(center=toggle_rect.center)
    screen.blit(toggle_text_surface, toggle_text_rect)
    
    # クリックでトグル
    if mouse_down and toggle_rect.collidepoint(mouse_pos):
        value = not value
    
    return value

def draw_romantic_preset_buttons(screen, preset_sizes, y, mouse_pos, mouse_down, font, animation_time):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    button_width = 100
    button_height = 50
    button_spacing = 15
    text_spacing = 20  # サイズ表示の間隔を追加
    
    for i, (name, width, height) in enumerate(preset_sizes):
        button_x = WINDOW_WIDTH//2 - (button_width * 2 + button_spacing) + (button_width + button_spacing) * (i % 3)
        button_y = y + (button_height + button_spacing + text_spacing) * (i // 3)  # テキストスペースを考慮
        
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        is_hover = button_rect.collidepoint(mouse_pos)
        
        # ボタンの背景（黒背景に合わせたグラデーション）
        for j in range(button_height):
            ratio = j / button_height
            wave = math.sin(animation_time * 0.05 + i * 0.5) * 0.1
            r = int(max(0, min(255, 40 + (80 - 40) * ratio + wave * 30)))
            g = int(max(0, min(255, 60 + (100 - 60) * ratio + wave * 20)))
            b = int(max(0, min(255, 80 + (120 - 80) * ratio + wave * 15)))
            pygame.draw.line(screen, (r, g, b), (button_x, button_y + j), (button_x + button_width, button_y + j))
        
        pygame.draw.rect(screen, (100, 150, 255), button_rect, 2, border_radius=8)
        
        # ボタンテキスト
        button_text = font.render(name, True, (255, 255, 255))
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
        
        # サイズ表示（ボタンの下に配置）
        size_text = get_japanese_font(12).render(f"{width}x{height}", True, (180, 200, 255))
        size_rect = size_text.get_rect(center=(button_rect.centerx, button_rect.bottom + 10))
        screen.blit(size_text, size_rect)
        
        # クリック処理
        if mouse_down and button_rect.collidepoint(mouse_pos):
            # 画面サイズを変更
            WINDOW_WIDTH = width
            WINDOW_HEIGHT = height
            # 画面サイズ設定を保存
            save_window_size_config(width, height)
            # 画面を再設定
            pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            print(f"画面サイズを変更しました: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")

def draw_romantic_input_field(screen, title, value, input_key, input_modes, y, mouse_pos, mouse_down, font, animation_time):
    """魅力的な入力フィールドを描画"""
    rect = pygame.Rect(100, y, WINDOW_WIDTH - 200, 60)  # 高さを50から60に増加
    is_hover = rect.collidepoint(mouse_pos)
    is_active = input_modes[input_key]
    
    # 背景（黒背景に合わせて調整）
    if is_active:
        color = (60, 80, 120)
    elif is_hover:
        color = (50, 70, 110)
    else:
        color = (40, 60, 100)
    
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (100, 150, 255), rect, 2, border_radius=8)
    
    # タイトル（上部）
    title_surface = font.render(title, True, (200, 220, 255))
    screen.blit(title_surface, (110, y + 5))
    
    # 入力テキスト（下部）
    text_surface = font.render(value, True, (255, 255, 255))
    screen.blit(text_surface, (110, y + 35))
    
    # クリックで入力モード切り替え
    if mouse_down and rect.collidepoint(mouse_pos):
        for key in input_modes:
            input_modes[key] = False
        input_modes[input_key] = True
    
    return y + 80  # 次の項目のy位置を調整

def draw_info_panel(screen, title, content, y, animation_time):
    """情報パネルを描画"""
    panel_rect = pygame.Rect(50, y, WINDOW_WIDTH - 100, 80)
    
    # 背景（黒背景に合わせて調整）
    wave = math.sin(animation_time * 0.03) * 0.1 + 0.9
    color = (int(30 * wave), int(40 * wave), int(60 * wave))
    pygame.draw.rect(screen, color, panel_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 150, 255), panel_rect, 2, border_radius=10)
    
    # タイトル
    title_font = get_japanese_font(16)
    title_surface = title_font.render(title, True, (200, 220, 255))
    screen.blit(title_surface, (60, y + 10))
    
    # コンテンツ
    content_font = get_japanese_font(12)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        content_surface = content_font.render(line, True, (180, 200, 255))
        screen.blit(content_surface, (60, y + 35 + i * 15))

def draw_parameter_info_panel(screen, y, animation_time):
    """パラメータ情報パネルを描画"""
    content = """学習率(α): 高いほど新しい経験を重視
割引率(γ): 高いほど将来の報酬を重視  
ランダム確率(ε): 高いほど探索を重視"""
    draw_info_panel(screen, "📊 パラメータ説明", content, y, animation_time)

def draw_advanced_info_panel(screen, y, animation_time):
    """高度設定情報パネルを描画"""
    content = """これらの設定は上級者向けです。
値を変更する際は慎重に行ってください。
不適切な値はAIの学習に悪影響を与える可能性があります。"""
    draw_info_panel(screen, "⚠️ 注意", content, y, animation_time)

def draw_romantic_button_group(screen, mouse_pos, mouse_down, font, animation_time):
    """魅力的なボタン群を描画"""
    global WINDOW_WIDTH, WINDOW_HEIGHT
    button_y = WINDOW_HEIGHT - 80
    
    # デフォルト値ボタン
    default_button = pygame.Rect(WINDOW_WIDTH//2 - 200, button_y, 120, 50)
    default_is_hover = default_button.collidepoint(mouse_pos)
    
    # ボタンの背景（黒背景に合わせたグラデーション）
    for i in range(default_button.height):
        ratio = i / default_button.height
        wave = math.sin(animation_time * 0.05) * 0.1
        r = int(max(0, min(255, 40 + (80 - 40) * ratio + wave * 30)))
        g = int(max(0, min(255, 60 + (100 - 60) * ratio + wave * 20)))
        b = int(max(0, min(255, 80 + (120 - 80) * ratio + wave * 15)))
        pygame.draw.line(screen, (r, g, b), (default_button.x, default_button.y + i), 
                        (default_button.x + default_button.width, default_button.y + i))
    
    pygame.draw.rect(screen, (100, 150, 255), default_button, 2, border_radius=8)
    # デフォルトボタンのフォントサイズを小さくする
    default_font = get_japanese_font(16)  # フォントサイズを小さく
    default_text = default_font.render("デフォルト", True, (255, 255, 255))
    default_text_rect = default_text.get_rect(center=default_button.center)
    screen.blit(default_text, default_text_rect)
    
    # デフォルトボタンの説明（ホバー時に表示）
    if default_is_hover:
        desc_font = get_japanese_font(12)
        desc_text = desc_font.render("設定を初期値に戻します", True, (180, 200, 255))
        desc_rect = desc_text.get_rect(center=(default_button.centerx, default_button.centery - 30))
        screen.blit(desc_text, desc_rect)
    
    # 戻るボタン
    back_button = pygame.Rect(WINDOW_WIDTH//2 + 80, button_y, 120, 50)
    back_is_hover = back_button.collidepoint(mouse_pos)
    
    # ボタンの背景（グラデーション）
    for i in range(back_button.height):
        ratio = i / back_button.height
        wave = math.sin(animation_time * 0.05) * 0.1
        r = int(max(0, min(255, 40 + (80 - 40) * ratio + wave * 30)))
        g = int(max(0, min(255, 60 + (100 - 60) * ratio + wave * 20)))
        b = int(max(0, min(255, 80 + (120 - 80) * ratio + wave * 15)))
        pygame.draw.line(screen, (r, g, b), (back_button.x, back_button.y + i), 
                        (back_button.x + back_button.width, back_button.y + i))
    
    pygame.draw.rect(screen, (100, 150, 255), back_button, 2, border_radius=8)
    back_text = font.render("戻る", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_button.center)
    screen.blit(back_text, back_text_rect)
    
    # 戻るボタンの説明（ホバー時に表示）
    if back_is_hover:
        desc_font = get_japanese_font(12)
        desc_text = desc_font.render("モード選択画面に戻ります", True, (180, 200, 255))
        desc_rect = desc_text.get_rect(center=(back_button.centerx, back_button.centery - 30))
        screen.blit(desc_text, desc_rect)
    
    # 操作説明
    help_font = get_japanese_font(14)
    help_text = help_font.render("ESCキーまたは戻るボタンでモード選択に戻ります", True, (180, 200, 255))
    help_rect = help_text.get_rect(center=(WINDOW_WIDTH//2, button_y - 25))
    screen.blit(help_text, help_rect)
    
    # ボタンクリック判定
    if mouse_down:
        if default_button.collidepoint(mouse_pos):
            # デフォルト値にリセット
            return "default"  # デフォルトボタンが押された
        elif back_button.collidepoint(mouse_pos):
            return "back"  # 戻るボタンが押された
    
    return False

def get_slider_rect(key, x, y):
    """スライダーの矩形を取得"""
    # スライダーの基本位置（設定画面のy_offsetに基づいて計算）
    base_y = 140  # 設定画面の開始位置
    
    if key == 'ai_speed':
        return pygame.Rect(100, base_y + 50, WINDOW_WIDTH - 200, 50)
    elif key == 'pretrain_total':
        return pygame.Rect(100, base_y + 130, WINDOW_WIDTH - 200, 50)
    elif key == 'alpha':
        return pygame.Rect(100, base_y + 350, WINDOW_WIDTH - 200, 50)
    elif key == 'gamma':
        return pygame.Rect(100, base_y + 430, WINDOW_WIDTH - 200, 50)
    elif key == 'epsilon':
        return pygame.Rect(100, base_y + 510, WINDOW_WIDTH - 200, 50)
    else:
        return None

def handle_slider_drag(key, x, slider_values, input_texts):
    """スライダーのドラッグ処理"""
    # スライダーの範囲を計算（100からWINDOW_WIDTH-100まで）
    slider_range = WINDOW_WIDTH - 200
    slider_start = 100
    
    # マウス位置を0-1の範囲に正規化
    normalized_value = (x - slider_start) / slider_range
    normalized_value = max(0.0, min(1.0, normalized_value))  # 0-1の範囲に制限
    
    if key == 'ai_speed':
        # AI思考速度: 10-1000ms
        new_value = int(10 + normalized_value * (1000 - 10))
        slider_values['ai_speed'] = normalized_value
        input_texts['ai_speed'] = str(new_value)
    elif key == 'pretrain_total':
        # 事前訓練回数: 1-100回
        new_value = int(1 + normalized_value * (100 - 1))
        slider_values['pretrain_total'] = normalized_value
        input_texts['pretrain_total'] = str(new_value)
    elif key == 'alpha':
        # 学習率: 0.0-1.0
        new_value = normalized_value
        slider_values['alpha'] = new_value
        input_texts['alpha'] = f"{new_value:.2f}"
    elif key == 'gamma':
        # 割引率: 0.0-1.0
        new_value = normalized_value
        slider_values['gamma'] = new_value
        input_texts['gamma'] = f"{new_value:.2f}"
    elif key == 'epsilon':
        # ランダム確率: 0.0-1.0
        new_value = normalized_value
        slider_values['epsilon'] = new_value
        input_texts['epsilon'] = f"{new_value:.2f}"

def draw_romantic_background(screen, animation_time):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    """黒を基調とした背景を描画"""
    # 黒のグラデーション背景
    for y in range(WINDOW_HEIGHT):
        ratio = y / WINDOW_HEIGHT
        # 黒から濃いグレーへのグラデーション
        wave = math.sin(animation_time * 0.02 + ratio * 3.14) * 0.05
        
        r = int(max(0, min(255, 10 + (30 - 10) * ratio + wave * 20)))
        g = int(max(0, min(255, 10 + (30 - 10) * ratio + wave * 20)))
        b = int(max(0, min(255, 15 + (40 - 15) * ratio + wave * 25)))
        
        pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
    
    # 星のような装飾（より控えめに）
    for i in range(15):
        x = (i * 123 + animation_time * 0.3) % WINDOW_WIDTH
        y = (i * 456 + animation_time * 0.2) % WINDOW_HEIGHT
        brightness = int(max(0, min(255, 80 + math.sin(animation_time * 0.05 + i) * 40)))
        pygame.draw.circle(screen, (brightness, brightness, brightness), (int(x), int(y)), 1)

def draw_animated_title(screen, title, animation_time):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    """アニメーション付きタイトルを描画"""
    title_font = get_japanese_font(48)
    
    # タイトルの色が時間とともに変化（黒背景に合わせて明るい色）
    wave = math.sin(animation_time * 0.05) * 0.3 + 0.7
    r = int(max(0, min(255, 200 + 55 * wave)))
    g = int(max(0, min(255, 220 + 35 * wave)))
    b = int(max(0, min(255, 255)))
    
    title_surface = title_font.render(title, True, (r, g, b))
    title_x = WINDOW_WIDTH//2 - title_surface.get_width()//2
    title_y = 30 + int(math.sin(animation_time * 0.03) * 3)  # 上下に揺れる
    
    # 影を描画（より濃い影）
    shadow_surface = title_font.render(title, True, (0, 0, 0))
    screen.blit(shadow_surface, (title_x + 3, title_y + 3))
    
    screen.blit(title_surface, (title_x, title_y))

def draw_tab_bar(screen, tabs, current_tab, mouse_pos, mouse_down, font):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    """タブバーを描画"""
    tab_height = 50
    tab_width = WINDOW_WIDTH // len(tabs)
    y = 100
    
    for i, tab in enumerate(tabs):
        tab_rect = pygame.Rect(i * tab_width, y, tab_width, tab_height)
        is_hover = tab_rect.collidepoint(mouse_pos)
        is_active = i == current_tab
        
        # タブの背景色（黒背景に合わせて調整）
        if is_active:
            color = (60, 100, 180)
        elif is_hover:
            color = (80, 120, 200)
        else:
            color = (40, 60, 120)
        
        pygame.draw.rect(screen, color, tab_rect)
        pygame.draw.rect(screen, (100, 150, 255), tab_rect, 2)
        
        # タブテキスト
        tab_font = get_japanese_font(16)
        tab_surface = tab_font.render(tab, True, (255, 255, 255))
        tab_text_rect = tab_surface.get_rect(center=tab_rect.center)
        screen.blit(tab_surface, tab_text_rect)

def handle_tab_click(mouse_pos, tabs, current_tab):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    """タブクリックを処理"""
    tab_height = 50
    tab_width = WINDOW_WIDTH // len(tabs)
    y = 100
    
    for i in range(len(tabs)):
        tab_rect = pygame.Rect(i * tab_width, y, tab_width, tab_height)
        if tab_rect.collidepoint(mouse_pos):
            return i
    return None

def draw_game_settings_tab(screen, input_texts, input_modes, slider_values, mouse_pos, mouse_down, font, animation_time):
    """ゲーム設定タブを描画"""
    y_offset = 170
    
    # セクションヘッダー
    draw_romantic_section_header(screen, "🎮 ゲーム設定", y_offset, animation_time)
    y_offset += 60
    
    # AI思考速度設定（カスタム入力）
    y_offset = draw_romantic_input_field(screen, "AI思考速度", input_texts['ai_speed'], 
                                       'ai_speed', input_modes, 
                                       y_offset, mouse_pos, mouse_down, font, animation_time)
    
    # 事前訓練回数設定（カスタム入力）
    y_offset = draw_romantic_input_field(screen, "事前訓練回数", input_texts['pretrain_total'], 
                                       'pretrain_total', input_modes, 
                                       y_offset, mouse_pos, mouse_down, font, animation_time)
    
    # 詳細説明パネル
    draw_info_panel(screen, "💡 ヒント", 
                   "AI思考速度を上げると対戦が速くなりますが、\nAIの思考時間が短くなるため精度が下がる可能性があります。\n事前訓練回数を増やすとAIの強さが向上します。", 
                   y_offset, animation_time)

def draw_ai_learning_tab(screen, input_texts, input_modes, slider_values, mouse_pos, mouse_down, font, animation_time):
    """AI学習設定タブを描画"""
    y_offset = 170
    
    # セクションヘッダー
    draw_romantic_section_header(screen, "🤖 AI学習パラメータ", y_offset, animation_time)
    y_offset += 60
    
    # Q学習パラメータ（カスタム入力）
    y_offset = draw_romantic_input_field(screen, "学習率 (α)", input_texts['alpha'], 
                                       'alpha', input_modes, 
                                       y_offset, mouse_pos, mouse_down, font, animation_time)
    
    y_offset = draw_romantic_input_field(screen, "割引率 (γ)", input_texts['gamma'], 
                                       'gamma', input_modes, 
                                       y_offset, mouse_pos, mouse_down, font, animation_time)
    
    y_offset = draw_romantic_input_field(screen, "ランダム確率 (ε)", input_texts['epsilon'], 
                                       'epsilon', input_modes, 
                                       y_offset, mouse_pos, mouse_down, font, animation_time)
    
    # パラメータ説明
    draw_parameter_info_panel(screen, y_offset, animation_time)

def draw_display_settings_tab(screen, local_draw_mode, local_fast_mode, local_debug_mode, 
                            preset_sizes, mouse_pos, mouse_down, font, animation_time):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    y_offset = 170
    
    # セクションヘッダー
    draw_romantic_section_header(screen, "🖥️ 表示設定", y_offset, animation_time)
    y_offset += 60
    
    # トグル設定項目
    local_draw_mode = draw_romantic_toggle(screen, "描画モード", local_draw_mode, 
                                          "ゲーム画面の描画を有効にする", 
                                          y_offset, mouse_pos, mouse_down, font, animation_time)
    y_offset += 90  # 間隔を80から90に増加
    
    local_fast_mode = draw_romantic_toggle(screen, "高速モード", local_fast_mode, 
                                          "AI同士の対戦を高速で実行", 
                                          y_offset, mouse_pos, mouse_down, font, animation_time)
    y_offset += 90  # 間隔を80から90に増加
    
    local_debug_mode = draw_romantic_toggle(screen, "デバッグモード", local_debug_mode, 
                                           "デバッグ情報を表示する", 
                                           y_offset, mouse_pos, mouse_down, font, animation_time)
    y_offset += 90  # 間隔を80から90に増加
    
    # 画面サイズ設定
    draw_romantic_section_header(screen, "📐 画面サイズ", y_offset, animation_time)
    y_offset += 60
    
    draw_romantic_preset_buttons(screen, preset_sizes, y_offset, mouse_pos, mouse_down, font, animation_time)

    return local_draw_mode, local_fast_mode, local_debug_mode

def draw_advanced_settings_tab(screen, input_texts, input_modes, slider_values, mouse_pos, mouse_down, font, animation_time):
    """高度設定タブを描画"""
    y_offset = 170
    
    # セクションヘッダー
    draw_romantic_section_header(screen, "⚙️ 高度な設定", y_offset, animation_time)
    y_offset += 60
    
    # カスタム入力フィールド
    y_offset = draw_romantic_input_field(screen, "ウィンドウ幅", input_texts['window_width'], 
                                       'window_width', input_modes, 
                                       y_offset, mouse_pos, mouse_down, font, animation_time)
    
    y_offset = draw_romantic_input_field(screen, "ウィンドウ高さ", input_texts['window_height'], 
                                       'window_height', input_modes, 
                                       y_offset, mouse_pos, mouse_down, font, animation_time)
    
    # 高度な説明
    draw_advanced_info_panel(screen, y_offset, animation_time)
