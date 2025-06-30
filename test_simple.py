#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡単なテストスクリプト
修正された関数が正常に動作するか確認します
"""

from medicine_logic import df, api_key, client

def test_basic_functions():
    """基本的な関数のテスト"""
    print("=== 基本テスト開始 ===")
    
    # CSVファイルの読み込み確認
    print(f"CSVファイル読み込み: {'成功' if df is not None else '失敗'}")
    if df is not None:
        print(f"データ行数: {len(df)}")
        print(f"列名: {list(df.columns)}")
    
    # APIキーの確認
    print(f"APIキー設定: {'成功' if api_key else '失敗'}")
    
    # OpenAIクライアントの確認
    print(f"OpenAIクライアント: {'成功' if client else '失敗'}")
    
    print("=== 基本テスト完了 ===")

def test_symptom_matching():
    """症状マッチングのテスト"""
    print("\n=== 症状マッチングテスト開始 ===")
    
    if df is None:
        print("CSVファイルが読み込めません")
        return
    
    # テスト用の症状
    test_symptoms = [
        "喉が痛い",
        "頭が痛くて熱がある",
        "腹痛と下痢",
        "存在しない症状"
    ]
    
    for symptom in test_symptoms:
        print(f"\n症状: {symptom}")
        try:
            from medicine_logic import match_symptom_pairs
            result = match_symptom_pairs(symptom, df)
            print(f"結果: {result}")
        except Exception as e:
            print(f"エラー: {e}")
    
    print("=== 症状マッチングテスト完了 ===")

def test_medicine_lookup():
    """薬の検索テスト"""
    print("\n=== 薬の検索テスト開始 ===")
    
    if df is None:
        print("CSVファイルが読み込めません")
        return
    
    # テスト用の症状ペア
    test_pairs = [
        "喉 - 痛み",
        "頭 - 痛み",
        "存在しない症状"
    ]
    
    for pair in test_pairs:
        print(f"\n症状ペア: {pair}")
        try:
            from medicine_logic import get_medicines
            result = get_medicines(pair, df)
            print(f"薬: {result}")
        except Exception as e:
            print(f"エラー: {e}")
    
    print("=== 薬の検索テスト完了 ===")

if __name__ == "__main__":
    test_basic_functions()
    test_symptom_matching()
    test_medicine_lookup()
    print("\n=== 全テスト完了 ===") 