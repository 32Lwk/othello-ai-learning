from flask import Flask, render_template, request, session, jsonify
from medicine_logic import diagnose_symptoms, answer_question, csv_load_status
from debug_logger import performance_stats, network_logs, add_network_log
import json
import time
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # セッション管理用

# キャッシュバスティング用のバージョン番号
VERSION = str(int(time.time()))

# AI自動応答制御用のグローバル変数
AI_AUTO_REPLY = True
MANUAL_REPLY_QUEUE = []  # 手動返信待ちのメッセージ

ALL_SESSIONS = {}  # {session_id: {'username': str, 'messages': list, 'last_activity': timestamp}}
USER_COUNTER = 1  # ユーザー名の連番
MAX_SESSIONS = 50  # 最大セッション数
SESSION_TIMEOUT = 3600  # セッションタイムアウト（秒）

def cleanup_old_sessions():
    """古いセッションをクリーンアップ"""
    global ALL_SESSIONS, USER_COUNTER
    current_time = time.time()
    expired_sessions = []
    
    for sid, info in ALL_SESSIONS.items():
        last_activity = info.get('last_activity', 0)
        if current_time - last_activity > SESSION_TIMEOUT:
            expired_sessions.append(sid)
    
    # 期限切れセッションを削除
    for sid in expired_sessions:
        del ALL_SESSIONS[sid]
        print(f"Expired session removed: {sid}")
    
    # セッション数が上限を超えた場合、最も古いセッションを削除
    if len(ALL_SESSIONS) > MAX_SESSIONS:
        oldest_sessions = sorted(ALL_SESSIONS.items(), key=lambda x: x[1].get('last_activity', 0))
        sessions_to_remove = len(ALL_SESSIONS) - MAX_SESSIONS
        for i in range(sessions_to_remove):
            sid = oldest_sessions[i][0]
            del ALL_SESSIONS[sid]
            print(f"Old session removed due to limit: {sid}")

def get_next_user_number():
    """次のユーザー番号を取得（既存の番号を再利用）"""
    global USER_COUNTER
    used_numbers = set()
    
    # 既存のセッションで使用されている番号を収集
    for info in ALL_SESSIONS.values():
        username = info.get('username', '')
        if username.startswith('ユーザー'):
            try:
                number = int(username.replace('ユーザー', ''))
                used_numbers.add(number)
            except ValueError:
                pass
    
    # 使用されていない最小の番号を見つける
    next_number = 1
    while next_number in used_numbers:
        next_number += 1
    
    # USER_COUNTERを更新（次回の効率化のため）
    USER_COUNTER = max(USER_COUNTER, next_number + 1)
    
    return next_number

def find_existing_session(client_ip, user_agent):
    """既存のセッションを検索（同じ人からのアクセスのみ）"""
    current_time = time.time()
    
    for existing_sid, info in ALL_SESSIONS.items():
        # IPアドレスとUser-Agentの両方が一致し、かつ30分以内のアクセス
        if (info.get('client_ip') == client_ip and 
            info.get('user_agent') == user_agent and 
            current_time - info.get('last_activity', 0) < 1800):  # 30分以内
            return existing_sid
    
    return None

def update_session_activity(sid):
    """セッションの最終アクティビティを更新"""
    if sid in ALL_SESSIONS:
        ALL_SESSIONS[sid]['last_activity'] = time.time()

@app.route('/', methods=['GET', 'POST'])
def index():
    # 古いセッションをクリーンアップ
    cleanup_old_sessions()
    
    current_time = time.time()
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # セッションIDの取得または作成
    sid = session.get('_id')
    if not sid:
        sid = str(int(time.time() * 1000)) + str(id(session))
        session['_id'] = sid
    
    # ユーザー名の設定
    if 'username' not in session:
        # 既存のセッションを検索（同じ人からのアクセスのみ）
        existing_session = find_existing_session(client_ip, user_agent)
        
        if existing_session:
            # 既存のセッションを再利用
            session['username'] = ALL_SESSIONS[existing_session]['username']
            session['messages'] = ALL_SESSIONS[existing_session]['messages'].copy()
            print(f"Reusing existing session: {existing_session} for IP: {client_ip}, User: {session['username']}")
        else:
            # 新しいユーザー番号を取得
            user_number = get_next_user_number()
            session['username'] = f'ユーザー{user_number}'
            session['messages'] = []
            print(f"New user created: {session['username']} for IP: {client_ip}, User-Agent: {user_agent[:50]}...")
    else:
        print(f"Existing session accessed: {session['username']} for IP: {client_ip}")
    
    # メッセージの初期化
    if 'messages' not in session:
        session['messages'] = []
    
    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        if user_message:
            session['messages'].append({
                'type': 'user',
                'content': user_message
            })
            # AI自動応答がOFFの場合は手動返信待ちにする
            if not AI_AUTO_REPLY:
                pending_message = {
                    'session_id': session.get('_id', 'unknown'),
                    'user_message': user_message,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'pending'
                }
                MANUAL_REPLY_QUEUE.append(pending_message)
                add_network_log(
                    'POST',
                    'メインサイト - 手動返信待ち',
                    {'symptom': user_message},
                    {'status': 'pending_manual_reply'},
                    0,
                    'pending'
                )
                bot_response = {
                    'type': 'bot',
                    'content': '申し訳ございません。現在、AI自動応答が一時停止されています。担当者が確認次第、回答いたします。',
                    'diagnosis': None
                }
            else:
                last_diagnosis = None
                for msg in reversed(session['messages']):
                    if msg['type'] == 'bot' and msg.get('diagnosis') and msg['diagnosis'].get('symptom_pairs'):
                        last_diagnosis = msg['diagnosis']
                        break
                if last_diagnosis and not is_symptom_input(user_message):
                    start_time = time.time()
                    answer = answer_question(user_message, last_diagnosis)
                    end_time = time.time()
                    response_time = round(end_time - start_time, 3)
                    add_network_log(
                        'POST',
                        'メインサイト - 質問回答',
                        {'question': user_message, 'diagnosis': last_diagnosis},
                        {'answer': answer[:100] + '...' if len(answer) > 100 else answer},
                        response_time,
                        'success'
                    )
                    bot_response = {
                        'type': 'bot',
                        'content': answer,
                        'diagnosis': None
                    }
                else:
                    start_time = time.time()
                    diagnosis = diagnose_symptoms(user_message)
                    end_time = time.time()
                    response_time = round(end_time - start_time, 3)
                    add_network_log(
                        'POST',
                        'メインサイト - 症状診断',
                        {'symptom': user_message},
                        {'diagnosis': diagnosis},
                        response_time,
                        'success' if not diagnosis.get('error') else 'error'
                    )
                    bot_response = {
                        'type': 'bot',
                        'content': '診断結果をお伝えします。',
                        'diagnosis': diagnosis
                    }
                    if diagnosis.get('error'):
                        bot_response['content'] = f"申し訳ございません。{diagnosis['error']}"
                        bot_response['diagnosis'] = None
            session['messages'].append(bot_response)
            session.modified = True
    
    # ALL_SESSIONSにセッション情報を保存/更新
    # 既存のALL_SESSIONSエントリがある場合は、手動返信メッセージを保持
    if sid in ALL_SESSIONS:
        existing_session = ALL_SESSIONS[sid]
        existing_messages = existing_session.get('messages', [])
        
        # 手動返信メッセージを保持
        manual_replies = [msg for msg in existing_messages if msg.get('manual_reply')]
        
        # 現在のセッションメッセージに手動返信を追加
        current_messages = session['messages'].copy()
        for manual_reply in manual_replies:
            # 既に同じ内容の手動返信が含まれていないかチェック
            if not any(msg.get('manual_reply') and msg.get('content') == manual_reply.get('content') for msg in current_messages):
                current_messages.append(manual_reply)
        
        # ALL_SESSIONSを更新
        ALL_SESSIONS[sid] = {
            'username': session['username'],
            'messages': current_messages,
            'last_activity': current_time,
            'client_ip': client_ip,
            'user_agent': user_agent
        }
        
        # セッションをALL_SESSIONSの内容で更新
        session['messages'] = current_messages
        session.modified = True
        
        print(f"Session {sid} updated with manual replies: {len(current_messages)} messages")
        if manual_replies:
            print(f"Manual replies preserved: {len(manual_replies)} messages")
    else:
        # 新しいセッションの場合
        ALL_SESSIONS[sid] = {
            'username': session['username'],
            'messages': session['messages'].copy(),
            'last_activity': current_time,
            'client_ip': client_ip,
            'user_agent': user_agent
        }
    
    # 手動返信メッセージがあるかチェック
    manual_replies = [msg for msg in session['messages'] if msg.get('manual_reply')]
    if manual_replies:
        print(f"Manual replies found in session {sid}: {len(manual_replies)} messages")
        for i, reply in enumerate(manual_replies):
            print(f"  Manual reply {i+1}: {reply.get('content', '')[:50]}...")
    
    return render_template('index.html', messages=session.get('messages', []), version=VERSION, username=session['username'])

def is_symptom_input(message):
    """メッセージが症状入力かどうかを判定"""
    # 症状を示すキーワード
    symptom_keywords = [
        '痛い', '痛み', '熱', '咳', '鼻水', '頭痛', '腹痛', '吐き気', '下痢', '便秘',
        '痒い', '腫れ', '炎症', '発疹', 'めまい', 'だるい', '疲れ', '不調', '症状',
        '喉', '胃', '腸', '目', '耳', '鼻', '皮膚', '関節', '筋肉'
    ]
    
    # 質問を示すキーワード
    question_keywords = [
        'ですか', 'でしょうか', 'ですか？', 'でしょうか？', 'どう', '何', 'なぜ', 'いつ',
        '副作用', '飲み方', '注意', '効果', '効き目', '時間', '回数', '量', '併用',
        '一緒に', '同時に', '飲んで', '使って', '服用', '投与'
    ]
    
    # 質問キーワードが含まれている場合は質問と判定
    for keyword in question_keywords:
        if keyword in message:
            return False
    
    # 症状キーワードが含まれている場合は症状入力と判定
    for keyword in symptom_keywords:
        if keyword in message:
            return True
    
    # デフォルトは症状入力として扱う
    return True

@app.route('/clear', methods=['POST'])
def clear_chat():
    """チャット履歴をクリア"""
    session['messages'] = []
    return '', 204

@app.route('/api/status')
def api_status():
    """システム状況を返す"""
    try:
        # csv_load_statusのpathを文字列として確実に返す
        csv_path = csv_load_status.get('path')
        if csv_path is not None:
            csv_path_str = str(csv_path)
        else:
            csv_path_str = None
            
        status_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'csv_load_status': {
                'success': csv_load_status.get('success', False),
                'encoding': csv_load_status.get('encoding'),
                'error': csv_load_status.get('error'),
                'row_count': csv_load_status.get('row_count', 0),
                'col_count': csv_load_status.get('col_count', 0),
                'columns': csv_load_status.get('columns', []),
                'path': csv_path_str
            },
            'session_active': 'messages' in session,
            'message_count': len(session.get('messages', [])),
            'version': VERSION
        }
        return jsonify(status_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def api_performance():
    """パフォーマンス統計を返す"""
    try:
        return jsonify(performance_stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def api_logs():
    """通信ログを返す"""
    try:
        # network_logsが配列でない場合は空配列を返す
        if not isinstance(network_logs, list):
            return jsonify([])
        return jsonify(network_logs)
    except Exception as e:
        # エラーの場合も空配列を返す
        return jsonify([])

@app.route('/api/sessions')
def api_sessions():
    """セッション情報を返す"""
    try:
        # 現在のセッション情報を取得
        session_data = {
            'session_id': session.get('_id', 'unknown'),
            'messages_count': len(session.get('messages', [])),
            'last_activity': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'session_active': 'messages' in session,
            'messages': session.get('messages', [])
        }
        return jsonify(session_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai_control', methods=['GET', 'POST'])
def api_ai_control():
    """AI自動応答の制御"""
    global AI_AUTO_REPLY
    
    if request.method == 'GET':
        return jsonify({
            'ai_auto_reply': AI_AUTO_REPLY,
            'manual_reply_queue_count': len(MANUAL_REPLY_QUEUE)
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        mode = data.get('mode')
        
        if mode in ['on', 'off']:
            AI_AUTO_REPLY = (mode == 'on')
            return jsonify({
                'ai_auto_reply': AI_AUTO_REPLY,
                'message': f'AI自動応答を{"ON" if AI_AUTO_REPLY else "OFF"}にしました'
            })
        else:
            return jsonify({'error': 'Invalid mode. Use "on" or "off"'}), 400
    
    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/api/manual_reply_queue', methods=['GET', 'POST'])
def api_manual_reply_queue():
    """手動返信待ちキュー"""
    global MANUAL_REPLY_QUEUE, ALL_SESSIONS
    
    if request.method == 'GET':
        return jsonify(MANUAL_REPLY_QUEUE)
    
    elif request.method == 'POST':
        data = request.get_json()
        session_id = data.get('session_id')
        reply_message = data.get('reply_message')
        
        print(f"Manual reply request received: session_id={session_id}, message={reply_message}")
        print(f"Current ALL_SESSIONS keys: {list(ALL_SESSIONS.keys())}")
        
        if not session_id or not reply_message:
            return jsonify({'error': 'session_id and reply_message are required'}), 400
        
        # キューから該当するメッセージを削除
        for i, pending in enumerate(MANUAL_REPLY_QUEUE):
            if pending['session_id'] == session_id:
                MANUAL_REPLY_QUEUE.pop(i)
                print(f"Removed pending message from queue for session {session_id}")
                break
        
        # 指定されたセッションIDのユーザーセッションに返信メッセージを追加
        if session_id in ALL_SESSIONS:
            # ALL_SESSIONSから対象セッションを取得
            target_session = ALL_SESSIONS[session_id]
            print(f"Found target session: {target_session}")
            
            # 返信メッセージを追加
            manual_reply_message = {
                'type': 'bot',
                'content': reply_message,
                'diagnosis': None,
                'manual_reply': True  # 手動返信のフラグ
            }
            
            target_session['messages'].append(manual_reply_message)
            target_session['last_activity'] = time.time()  # 最終アクティビティを更新
            
            # ALL_SESSIONSを更新
            ALL_SESSIONS[session_id] = target_session
            
            # ログに記録
            add_network_log(
                'POST',
                'メインサイト - 手動返信',
                {'session_id': session_id, 'reply': reply_message},
                {'status': 'manual_reply_sent'},
                0,
                'success'
            )
            
            print(f"Manual reply sent to session {session_id}: {reply_message}")
            print(f"ALL_SESSIONS updated: {len(ALL_SESSIONS[session_id]['messages'])} messages")
            print(f"Target session info: {target_session}")
            print(f"Updated ALL_SESSIONS for {session_id}: {ALL_SESSIONS[session_id]}")
            print(f"Manual reply message added: {manual_reply_message}")
            
            # メインサイトでの反映確認用ログ
            print(f"=== Manual Reply Summary ===")
            print(f"Session ID: {session_id}")
            print(f"Total messages in ALL_SESSIONS: {len(ALL_SESSIONS[session_id]['messages'])}")
            print(f"Manual reply messages: {len([msg for msg in ALL_SESSIONS[session_id]['messages'] if msg.get('manual_reply')])}")
            print(f"Latest message: {ALL_SESSIONS[session_id]['messages'][-1] if ALL_SESSIONS[session_id]['messages'] else 'None'}")
            print(f"===========================")
            
            return jsonify({
                'message': '手動返信を送信しました',
                'remaining_queue': len(MANUAL_REPLY_QUEUE),
                'target_session_id': session_id,
                'messages_count': len(target_session['messages']),
                'session_updated': True
            })
        else:
            print(f"Session {session_id} not found in ALL_SESSIONS")
            print(f"Available sessions: {list(ALL_SESSIONS.keys())}")
            print(f"ALL_SESSIONS content: {ALL_SESSIONS}")
            return jsonify({'error': f'Session {session_id} not found'}), 404
    
    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/api/all_sessions')
def api_all_sessions():
    result = []
    for sid, info in ALL_SESSIONS.items():
        result.append({
            'session_id': sid,
            'username': info.get('username', ''),
            'messages': info.get('messages', []),
            'messages_count': len(info.get('messages', []))
        })
    
    # デバッグ用ログ
    print(f"ALL_SESSIONS API called: {len(result)} sessions")
    for session_info in result:
        print(f"Session {session_info['session_id']}: {session_info['messages_count']} messages")
    
    return jsonify(result)

@app.route('/api/session_stats')
def api_session_stats():
    """セッション管理の統計情報を返す"""
    try:
        current_time = time.time()
        active_sessions = 0
        expired_sessions = 0
        used_user_numbers = set()
        session_details = []
        
        for sid, info in ALL_SESSIONS.items():
            last_activity = info.get('last_activity', 0)
            if current_time - last_activity < SESSION_TIMEOUT:
                active_sessions += 1
                # ユーザー番号を収集
                username = info.get('username', '')
                if username.startswith('ユーザー'):
                    try:
                        number = int(username.replace('ユーザー', ''))
                        used_user_numbers.add(number)
                    except ValueError:
                        pass
                
                # セッション詳細情報を収集
                session_details.append({
                    'session_id': sid,
                    'username': username,
                    'client_ip': info.get('client_ip', ''),
                    'user_agent': info.get('user_agent', '')[:50] + '...' if len(info.get('user_agent', '')) > 50 else info.get('user_agent', ''),
                    'messages_count': len(info.get('messages', [])),
                    'last_activity': datetime.fromtimestamp(last_activity).strftime("%Y-%m-%d %H:%M:%S"),
                    'age_minutes': int((current_time - last_activity) / 60)
                })
            else:
                expired_sessions += 1
        
        stats = {
            'total_sessions': len(ALL_SESSIONS),
            'active_sessions': active_sessions,
            'expired_sessions': expired_sessions,
            'max_sessions': MAX_SESSIONS,
            'session_timeout': SESSION_TIMEOUT,
            'current_user_counter': USER_COUNTER,
            'used_user_numbers': sorted(list(used_user_numbers)),
            'next_available_number': get_next_user_number(),
            'session_details': session_details,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug_manual_replies')
def api_debug_manual_replies():
    """手動返信のデバッグ情報を返す"""
    try:
        debug_info = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_sessions': len(ALL_SESSIONS),
            'sessions_with_manual_replies': [],
            'manual_reply_queue': MANUAL_REPLY_QUEUE
        }
        
        for sid, info in ALL_SESSIONS.items():
            manual_replies = [msg for msg in info.get('messages', []) if msg.get('manual_reply')]
            if manual_replies:
                debug_info['sessions_with_manual_replies'].append({
                    'session_id': sid,
                    'username': info.get('username', ''),
                    'manual_replies_count': len(manual_replies),
                    'manual_replies': manual_replies,
                    'total_messages': len(info.get('messages', []))
                })
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 