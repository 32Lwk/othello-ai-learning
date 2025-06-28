import pygame
import sys
from constants import *
from ui_components import get_japanese_font

def settings_screen(screen, font, debug_mode, ai_speed, draw_mode, pretrain_total):
    """設定画面"""
    # 設定項目の入力モード
    input_modes = {
        'ai_speed': False,
        'pretrain_total': False,
        'alpha': False,
        'gamma': False,
        'epsilon': False
    }
    
    # 入力テキスト
    input_texts = {
        'ai_speed': str(ai_speed),
        'pretrain_total': str(pretrain_total),
        'alpha': str(0.1),  # デフォルト値
        'gamma': str(0.9),  # デフォルト値
        'epsilon': str(0.1)  # デフォルト値
    }
    
    # 設定項目の説明
    setting_descriptions = {
        'ai_speed': 'AIの思考速度（ミリ秒）',
        'pretrain_total': '事前訓練の対戦回数',
        'alpha': 'Q学習の学習率（0.0-1.0）',
        'gamma': 'Q学習の割引率（0.0-1.0）',
        'epsilon': 'ε-greedy法のランダム確率（0.0-1.0）'
    }
    
    # 設定項目の範囲
    setting_ranges = {
        'ai_speed': (10, 1000),
        'pretrain_total': (1, 1000),
        'alpha': (0.0, 1.0),
        'gamma': (0.0, 1.0),
        'epsilon': (0.0, 1.0)
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
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # 入力モードを全てオフにする
                    for key in input_modes:
                        input_modes[key] = False
                    running = False
                elif event.key == pygame.K_RETURN:
                    # 現在の入力モードを終了
                    for key in input_modes:
                        if input_modes[key]:
                            try:
                                if key == 'ai_speed':
                                    local_ai_speed = int(input_texts[key])
                                elif key == 'pretrain_total':
                                    local_pretrain_total = int(input_texts[key])
                                elif key == 'alpha':
                                    local_alpha = float(input_texts[key])
                                elif key == 'gamma':
                                    local_gamma = float(input_texts[key])
                                elif key == 'epsilon':
                                    local_epsilon = float(input_texts[key])
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
        
        # 背景を描画（グラデーション風）
        draw_gradient_background(screen)
        
        # タイトル
        title_font = get_japanese_font(42)
        title = title_font.render("⚙ 設定", True, (50, 50, 100))
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))
        
        # 左列: 基本設定とAI学習パラメータ
        left_column_x = 50
        right_column_x = WINDOW_WIDTH//2 + 20  # 位置をさらに調整
        
        # カテゴリ1: 基本設定（左列）
        draw_category_title(screen, "基本設定", 80, left_column_x)
        
        # AI思考速度（ユーザー入力可能）
        draw_input_setting(screen, "AI思考速度", input_texts['ai_speed'], 
                          setting_descriptions['ai_speed'], 'ai_speed',
                          left_column_x, 120, 250, 90,  # 幅を300から250に変更
                          mouse_pos, mouse_down, font, input_modes)
        
        # 事前訓練回数（ユーザー入力可能）
        draw_input_setting(screen, "事前訓練回数", input_texts['pretrain_total'], 
                          setting_descriptions['pretrain_total'], 'pretrain_total',
                          left_column_x, 220, 250, 90,  # 幅を300から250に変更
                          mouse_pos, mouse_down, font, input_modes)
        
        # カテゴリ2: AI学習パラメータ（左列）
        draw_category_title(screen, "AI学習パラメータ", 340, left_column_x)  # y位置を調整
        
        # Q学習パラメータ（ユーザー入力可能）
        draw_input_setting(screen, "学習率 (α)", input_texts['alpha'], 
                          setting_descriptions['alpha'], 'alpha',
                          left_column_x, 380, 250, 90,  # 幅を300から250に変更
                          mouse_pos, mouse_down, font, input_modes)
        
        draw_input_setting(screen, "割引率 (γ)", input_texts['gamma'], 
                          setting_descriptions['gamma'], 'gamma',
                          left_column_x, 480, 250, 90,  # 幅を300から250に変更
                          mouse_pos, mouse_down, font, input_modes)
        
        draw_input_setting(screen, "ランダム確率 (ε)", input_texts['epsilon'], 
                          setting_descriptions['epsilon'], 'epsilon',
                          left_column_x, 580, 250, 90,  # 幅を300から250に変更
                          mouse_pos, mouse_down, font, input_modes)
        
        # 右列: 表示設定
        draw_category_title(screen, "表示設定", 80, right_column_x)
        
        # トグル設定項目（右列）
        y_offset = 120
        
        # 高速モード
        local_fast_mode = draw_enhanced_toggle_setting(screen, "高速モード", local_fast_mode, 
                           "AI同士の対戦を高速で実行", 
                           right_column_x, y_offset, 220, 70,  # 幅を250から220に変更
                           mouse_pos, mouse_down, font)
        
        y_offset += 90  # 間隔を90に変更
        
        # 描画モード
        local_draw_mode = draw_enhanced_toggle_setting(screen, "描画モード", local_draw_mode, 
                           "ゲーム画面の描画を有効にする", 
                           right_column_x, y_offset, 220, 70,  # 幅を250から220に変更
                           mouse_pos, mouse_down, font)
        
        y_offset += 90  # 間隔を90に変更
        
        # デバッグモード
        local_debug_mode = draw_enhanced_toggle_setting(screen, "デバッグモード", local_debug_mode, 
                           "デバッグ情報を表示する", 
                           right_column_x, y_offset, 220, 70,  # 幅を250から220に変更
                           mouse_pos, mouse_down, font)
        
        # ボタン群（下部中央）
        if draw_button_group(screen, mouse_pos, mouse_down, font):
            running = False
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    
    # 設定値を返す
    return local_debug_mode, local_ai_speed, local_draw_mode, local_pretrain_total

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
            return True  # 戻る
    
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
