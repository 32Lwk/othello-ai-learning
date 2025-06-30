import pandas as pd
import os
import sys

def test_csv_loading():
    """CSVファイルの読み込みをテスト"""
    print("=== CSVファイル読み込みテスト ===")
    
    # ファイルパスの確認
    csv_path = "症状-薬.csv"
    print(f"CSVファイルパス: {csv_path}")
    print(f"ファイル存在: {os.path.exists(csv_path)}")
    
    if not os.path.exists(csv_path):
        print("❌ エラー: CSVファイルが見つかりません")
        return False
    
    # ファイルサイズの確認
    file_size = os.path.getsize(csv_path)
    print(f"ファイルサイズ: {file_size} bytes")
    
    # エンコーディングのテスト
    encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp']
    
    for encoding in encodings:
        try:
            print(f"\n--- {encoding} エンコーディングでテスト ---")
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"✅ 成功: {encoding} で読み込み成功")
            print(f"行数: {len(df)}")
            print(f"列数: {len(df.columns)}")
            print(f"列名: {list(df.columns)}")
            
            # 最初の5行を表示
            print("\n最初の5行:")
            print(df.head())
            
            # データ型を確認
            print(f"\nデータ型:")
            print(df.dtypes)
            
            # 欠損値の確認
            print(f"\n欠損値:")
            print(df.isnull().sum())
            
            return True
            
        except UnicodeDecodeError as e:
            print(f"❌ エラー: {encoding} でUnicodeDecodeError - {e}")
            continue
        except Exception as e:
            print(f"❌ エラー: {encoding} で予期しないエラー - {e}")
            continue
    
    print("\n❌ すべてのエンコーディングで読み込みに失敗しました")
    return False

def test_data_integrity():
    """データの整合性をテスト"""
    print("\n=== データ整合性テスト ===")
    
    try:
        df = pd.read_csv("症状-薬.csv", encoding='utf-8')
        
        # 必須列の確認
        required_columns = ['部位', '症状', '医薬品1', '医薬品2', '医薬品3']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ エラー: 必須列が不足しています - {missing_columns}")
            return False
        else:
            print("✅ 必須列はすべて存在します")
        
        # データの確認
        print(f"総行数: {len(df)}")
        print(f"部位の種類: {df['部位'].nunique()}")
        print(f"症状の種類: {df['症状'].nunique()}")
        
        # サンプルデータの確認
        print("\nサンプルデータ（最初の3行）:")
        for i, row in df.head(3).iterrows():
            print(f"行{i+1}: {row['部位']} - {row['症状']} -> {row['医薬品1']}, {row['医薬品2']}, {row['医薬品3']}")
        
        # 症状マッチングのテスト
        print("\n症状マッチングテスト:")
        test_symptoms = ['頭痛', '発熱', '腹痛', '咳']
        for symptom in test_symptoms:
            matches = df[df['症状'].str.contains(symptom, na=False)]
            print(f"'{symptom}' のマッチ数: {len(matches)}")
            if len(matches) > 0:
                print(f"  例: {matches.iloc[0]['部位']} - {matches.iloc[0]['症状']}")
        
        return True
        
    except Exception as e:
        print(f"❌ データ整合性テストでエラー: {e}")
        return False

if __name__ == "__main__":
    print("CSVファイル読み込みテストを開始します...")
    
    # 基本的な読み込みテスト
    loading_success = test_csv_loading()
    
    if loading_success:
        # データ整合性テスト
        integrity_success = test_data_integrity()
        
        if integrity_success:
            print("\n🎉 すべてのテストが成功しました！")
        else:
            print("\n⚠️ データ整合性に問題があります")
    else:
        print("\n❌ CSVファイルの読み込みに失敗しました")
    
    print("\nテスト完了") 