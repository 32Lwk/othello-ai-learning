#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医薬品プログラムのセットアップテスト
"""

def test_imports():
    """必要なライブラリのインポートテスト"""
    print("=== ライブラリのインポートテスト ===")
    
    try:
        import pandas as pd
        print("✅ pandas: インポート成功")
    except ImportError as e:
        print(f"❌ pandas: インポート失敗 - {e}")
        return False
    
    try:
        from openai import OpenAI
        print("✅ openai: インポート成功")
    except ImportError as e:
        print(f"❌ openai: インポート失敗 - {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv: インポート成功")
    except ImportError as e:
        print(f"⚠️ python-dotenv: インポート失敗 - {e}")
        print("   .envファイルの読み込みは無効になりますが、環境変数は使用可能です")
    
    return True

def test_api_key():
    """APIキーの設定テスト"""
    print("\n=== APIキーの設定テスト ===")
    
    import os
    
    # .envファイルの読み込みを試行
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .envファイルの読み込みを試行しました")
    except ImportError:
        print("⚠️ python-dotenvがインストールされていないため、.envファイルは読み込めません")
    
    # 環境変数の確認
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ 環境変数からAPIキーを取得: {api_key[:20]}...")
        return True
    else:
        print("❌ 環境変数にAPIキーが設定されていません")
        return False

def test_csv_file():
    """CSVファイルの存在確認"""
    print("\n=== CSVファイルの確認 ===")
    
    import os
    
    csv_file = "症状-薬.csv"
    if os.path.exists(csv_file):
        print(f"✅ {csv_file}: ファイルが存在します")
        return True
    else:
        print(f"❌ {csv_file}: ファイルが見つかりません")
        return False

def main():
    """メイン関数"""
    print("医薬品プログラムのセットアップテストを開始します...\n")
    
    # テストの実行
    imports_ok = test_imports()
    api_key_ok = test_api_key()
    csv_ok = test_csv_file()
    
    # 結果の表示
    print("\n=== テスト結果 ===")
    if imports_ok and api_key_ok and csv_ok:
        print("🎉 すべてのテストが成功しました！プログラムを実行できます。")
        print("\n実行コマンド:")
        print("python 医薬品.py")
    else:
        print("⚠️ 一部のテストが失敗しました。以下の対応を行ってください：")
        
        if not imports_ok:
            print("- 必要なライブラリをインストール: pip install pandas openai python-dotenv")
        
        if not api_key_ok:
            print("- APIキーを環境変数に設定: $env:OPENAI_API_KEY='your-api-key'")
        
        if not csv_ok:
            print("- CSVファイルが正しい場所にあることを確認")

if __name__ == "__main__":
    main() 