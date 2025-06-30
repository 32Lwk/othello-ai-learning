#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import urllib.error
import json

def test_main_app_diagnosis():
    """メインサイトの診断機能をテスト"""
    print("=== メインサイト診断機能テスト ===")
    
    # テスト用の症状（1つだけテストして時間を短縮）
    test_symptoms = [
        "頭痛"
    ]
    
    for symptom in test_symptoms:
        print(f"\n--- 症状: {symptom} ---")
        
        try:
            # POSTリクエストの準備
            data = urllib.parse.urlencode({'message': symptom}).encode('utf-8')
            req = urllib.request.Request(
                'http://localhost:5000/',
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            # リクエスト送信（タイムアウトを30秒に延長）
            with urllib.request.urlopen(req, timeout=30) as response:
                html_content = response.read().decode('utf-8')
                
                # 診断結果が含まれているかチェック
                if '推定された症状' in html_content:
                    print("✅ 診断結果が正常に表示されています")
                    # 薬の情報も確認
                    if '市販薬候補' in html_content:
                        print("✅ 市販薬情報が表示されています")
                    if '注意点' in html_content:
                        print("✅ 注意点が表示されています")
                    if '薬の選び方アドバイス' in html_content:
                        print("✅ アドバイスが表示されています")
                elif 'エラー' in html_content:
                    print("❌ エラーが発生しています")
                    # エラー内容を確認
                    if 'APIエラー' in html_content:
                        print("   APIエラーが発生しています")
                    elif 'CSV' in html_content:
                        print("   CSVファイル関連のエラーが発生しています")
                else:
                    print("⚠️ 診断結果が表示されていません")
                
                # レスポンスの長さを確認
                print(f"レスポンスサイズ: {len(html_content)} 文字")
                
        except urllib.error.URLError as e:
            if 'timed out' in str(e):
                print("❌ タイムアウトが発生しました（API呼び出しに時間がかかっています）")
            else:
                print(f"❌ リクエストエラー: {e}")
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")

def test_api_endpoints():
    """APIエンドポイントをテスト"""
    print(f"\n=== APIエンドポイントテスト ===")
    
    endpoints = [
        ('/api/status', 'システム状況'),
        ('/api/performance', 'パフォーマンス統計'),
        ('/api/logs', '通信ログ')
    ]
    
    for endpoint, name in endpoints:
        try:
            req = urllib.request.Request(f'http://localhost:5000{endpoint}')
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                print(f"✅ {name}: 正常に応答")
                if 'error' in data:
                    print(f"   ⚠️ エラー: {data['error']}")
        except Exception as e:
            print(f"❌ {name}: {e}")

if __name__ == "__main__":
    print("メインサイトのテストを開始します...")
    
    # APIエンドポイントテスト
    test_api_endpoints()
    
    # 診断機能テスト
    test_main_app_diagnosis()
    
    print("\nテスト完了") 