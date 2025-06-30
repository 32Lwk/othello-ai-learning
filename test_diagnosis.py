#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

def test_diagnosis():
    """AI診断機能をテスト"""
    print("=== AI診断機能テスト ===")
    
    try:
        from medicine_logic import diagnose_symptoms, df, csv_load_status
        
        # CSV読み込み状況を確認
        print(f"CSV読み込み状況: {csv_load_status['success']}")
        if csv_load_status['success']:
            print(f"エンコーディング: {csv_load_status['encoding']}")
            print(f"行数: {csv_load_status['row_count']}")
            print(f"列数: {csv_load_status['col_count']}")
            print(f"列名: {csv_load_status['columns']}")
        else:
            print(f"エラー: {csv_load_status['error']}")
            return False
        
        # テスト用の症状
        test_symptoms = [
            "頭痛",
            "発熱",
            "喉が痛い",
            "腹痛と下痢",
            "咳と鼻水",
            "関節痛",
            "めまい",
            "存在しない症状"
        ]
        
        print(f"\n=== 診断テスト ===")
        for symptom in test_symptoms:
            print(f"\n--- 症状: {symptom} ---")
            try:
                result = diagnose_symptoms(symptom)
                
                if 'error' in result:
                    print(f"❌ エラー: {result['error']}")
                else:
                    print(f"✅ 症状マッチング: {result['symptom_pairs']}")
                    print(f"💊 薬: {result['medicines']}")
                    print(f"⚠️ 注意点数: {len(result['cautions'])}")
                    if result['cautions']:
                        print(f"   最初の注意点: {result['cautions'][0][:100]}...")
                    print(f"🤖 組み合わせアドバイス: {result['combination_advice'][:100]}...")
                
            except Exception as e:
                print(f"❌ 診断中にエラー: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ テスト実行中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_question_answering():
    """質問回答機能をテスト"""
    print(f"\n=== 質問回答機能テスト ===")
    
    try:
        from medicine_logic import diagnose_symptoms, answer_question
        
        # まず症状を診断
        symptom = "頭痛"
        print(f"症状: {symptom}")
        diagnosis = diagnose_symptoms(symptom)
        
        if 'error' in diagnosis:
            print(f"❌ 診断エラー: {diagnosis['error']}")
            return False
        
        print(f"✅ 診断成功: {diagnosis['symptom_pairs']}")
        
        # 質問をテスト
        test_questions = [
            "この薬の副作用は？",
            "いつ飲めばいいですか？",
            "他の薬と一緒に飲んでも大丈夫ですか？",
            "今日の天気は？"  # 医薬品以外の質問
        ]
        
        for question in test_questions:
            print(f"\n--- 質問: {question} ---")
            try:
                answer = answer_question(question, diagnosis)
                print(f"回答: {answer[:200]}...")
            except Exception as e:
                print(f"❌ 回答エラー: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 質問回答テスト中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("AI診断機能のテストを開始します...")
    
    # 診断機能テスト
    diagnosis_ok = test_diagnosis()
    
    # 質問回答機能テスト
    question_ok = test_question_answering()
    
    print(f"\n=== テスト結果 ===")
    if diagnosis_ok and question_ok:
        print("🎉 すべてのテストが成功しました！")
    else:
        print("⚠️ 一部のテストで問題が発生しました")
    
    print("\nテスト完了") 