#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import time
import sys

def check_app(url, name):
    """アプリの起動状況を確認"""
    try:
        print(f"\n=== {name} の確認 ===")
        print(f"URL: {url}")
        
        # タイムアウトを設定
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 200:
                print(f"✅ {name} は正常に動作しています")
                return True
            else:
                print(f"⚠️ {name} は起動していますが、ステータスコード: {response.getcode()}")
                return False
            
    except urllib.error.URLError as e:
        if "Connection refused" in str(e) or "No route to host" in str(e):
            print(f"❌ {name} に接続できません（起動していない可能性があります）")
        else:
            print(f"❌ {name} への接続エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ {name} の確認中にエラーが発生しました: {e}")
        return False

def main():
    print("=== アプリケーション起動状況確認 ===")
    
    # 両方のアプリを確認
    main_app_ok = check_app("http://localhost:5000/", "メインアプリ")
    test_app_ok = check_app("http://localhost:5002/", "テストサイト")
    
    print(f"\n=== 確認結果 ===")
    if main_app_ok and test_app_ok:
        print("🎉 両方のアプリが正常に動作しています！")
        print("\nアクセス方法:")
        print("- メインアプリ: http://localhost:5000/")
        print("- テストサイト: http://localhost:5002/")
        print("- デバッグサイト: http://localhost:5001/")
    elif main_app_ok:
        print("✅ メインアプリのみ動作しています")
        print("⚠️ テストサイトが起動していません")
    elif test_app_ok:
        print("✅ テストサイトのみ動作しています")
        print("⚠️ メインアプリが起動していません")
    else:
        print("❌ どちらのアプリも起動していません")
        print("\n起動方法:")
        print("1. メインアプリ: python app.py")
        print("2. テストサイト: python test_app.py")
        print("3. デバッグサイト: python debug_app.py")
        print("4. 一括起動: python start_servers.py")

if __name__ == "__main__":
    main() 