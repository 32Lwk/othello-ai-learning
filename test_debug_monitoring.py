#!/usr/bin/env python3
"""
デバッグサイトのネットワーク監視機能をテストするスクリプト
"""

import requests
import time
import json

def test_debug_site():
    """デバッグサイトの機能をテスト"""
    base_url = "http://localhost:5001"
    
    print("=== デバッグサイト機能テスト ===")
    
    # 1. デバッグサイトの状態確認
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ デバッグサイト状態: 正常")
            print(f"   CSV読み込み: {'✅' if data.get('csv_status', {}).get('success') else '❌'}")
            print(f"   API接続: {'✅' if data.get('api_status', {}).get('client_initialized') else '❌'}")
        else:
            print(f"❌ デバッグサイト状態: エラー (ステータス: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ デバッグサイト接続エラー: {e}")
        return False
    
    # 2. ネットワークログの確認
    try:
        response = requests.get(f"{base_url}/network_logs", timeout=5)
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ ネットワークログ: {len(logs)}件")
            if logs:
                print(f"   最新ログ: {logs[-1].get('timestamp', 'N/A')}")
        else:
            print(f"❌ ネットワークログ取得エラー: {response.status_code}")
    except Exception as e:
        print(f"❌ ネットワークログ取得エラー: {e}")
    
    # 3. パフォーマンス統計の確認
    try:
        response = requests.get(f"{base_url}/performance_stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ パフォーマンス統計: 総リクエスト {stats.get('total_requests', 0)}件")
        else:
            print(f"❌ パフォーマンス統計取得エラー: {response.status_code}")
    except Exception as e:
        print(f"❌ パフォーマンス統計取得エラー: {e}")
    
    # 4. メインサイトからのデータ取得テスト
    print("\n=== メインサイト連携テスト ===")
    
    # メインサイトの状態
    try:
        response = requests.get(f"{base_url}/api/main_status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ メインサイト状態取得: 正常")
            if data.get('csv_load_status', {}).get('success'):
                print(f"   CSV読み込み: ✅ ({data['csv_load_status']['row_count']}行)")
            else:
                print("   CSV読み込み: ❌")
        else:
            print(f"❌ メインサイト状態取得エラー: {response.status_code}")
    except Exception as e:
        print(f"❌ メインサイト状態取得エラー: {e}")
    
    # メインサイトのパフォーマンス
    try:
        response = requests.get(f"{base_url}/api/main_performance", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ メインサイトパフォーマンス: 総リクエスト {data.get('total_requests', 0)}件")
        else:
            print(f"❌ メインサイトパフォーマンス取得エラー: {response.status_code}")
    except Exception as e:
        print(f"❌ メインサイトパフォーマンス取得エラー: {e}")
    
    # メインサイトのログ
    try:
        response = requests.get(f"{base_url}/api/main_logs", timeout=5)
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ メインサイトログ: {len(logs)}件")
            if logs:
                print(f"   最新ログ: {logs[-1].get('timestamp', 'N/A')}")
        else:
            print(f"❌ メインサイトログ取得エラー: {response.status_code}")
    except Exception as e:
        print(f"❌ メインサイトログ取得エラー: {e}")
    
    # 5. APIテストを実行してログを生成
    print("\n=== APIテスト実行 ===")
    try:
        response = requests.get(f"{base_url}/test_api", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("✅ APIテスト: 成功")
            print(f"   レスポンス: {data.get('response', 'N/A')[:100]}...")
        else:
            print(f"❌ APIテストエラー: {response.status_code}")
    except Exception as e:
        print(f"❌ APIテストエラー: {e}")
    
    # 6. テスト後のログ確認
    print("\n=== テスト後のログ確認 ===")
    time.sleep(2)  # 少し待機
    
    try:
        response = requests.get(f"{base_url}/network_logs", timeout=5)
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ テスト後ネットワークログ: {len(logs)}件")
            if logs:
                print("   最新のログ:")
                for log in logs[-3:]:  # 最新3件を表示
                    print(f"     {log.get('timestamp', 'N/A')} - {log.get('endpoint', 'N/A')} - {log.get('status', 'N/A')}")
        else:
            print(f"❌ テスト後ログ取得エラー: {response.status_code}")
    except Exception as e:
        print(f"❌ テスト後ログ取得エラー: {e}")
    
    print("\n=== テスト完了 ===")
    return True

if __name__ == "__main__":
    test_debug_site() 