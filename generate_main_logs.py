#!/usr/bin/env python3
"""
メインサイトでAPI呼び出しを実行してログを生成するスクリプト
"""

import requests
import time
import json

def generate_main_logs():
    """メインサイトでAPI呼び出しを実行してログを生成"""
    base_url = "http://localhost:5000"
    
    print("=== メインサイトログ生成テスト ===")
    
    # 症状診断を実行
    symptoms = ["頭痛", "発熱", "腹痛", "咳"]
    
    for symptom in symptoms:
        print(f"\n--- 症状: {symptom} ---")
        try:
            # POSTリクエストで症状診断を実行
            response = requests.post(
                f"{base_url}/",
                data={'message': symptom},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ 診断成功: {symptom}")
            else:
                print(f"❌ 診断エラー: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 診断エラー: {e}")
        
        # 少し待機
        time.sleep(2)
    
    # ログを確認
    print("\n=== ログ確認 ===")
    try:
        response = requests.get(f"{base_url}/api/logs", timeout=5)
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ メインサイトログ: {len(logs)}件")
            if logs:
                print("   最新のログ:")
                for log in logs[-5:]:  # 最新5件を表示
                    print(f"     {log.get('timestamp', 'N/A')} - {log.get('endpoint', 'N/A')} - {log.get('status', 'N/A')}")
        else:
            print(f"❌ ログ取得エラー: {response.status_code}")
    except Exception as e:
        print(f"❌ ログ取得エラー: {e}")
    
    print("\n=== ログ生成完了 ===")

if __name__ == "__main__":
    generate_main_logs() 