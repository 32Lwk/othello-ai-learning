#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

print("=== CSVファイル読み込み状況確認 ===")

try:
    from medicine_logic import df, CSV_PATH
    
    print(f"CSV_PATH: {CSV_PATH}")
    print(f"ファイル存在: {os.path.exists(CSV_PATH)}")
    
    if df is not None:
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {list(df.columns)}")
        print(f"行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        
        # 最初の3行を表示
        print("\n最初の3行:")
        print(df.head(3))
        
        print("\n✅ CSVファイルは正常に読み込まれています")
    else:
        print("\n❌ DataFrameがNoneです")
        
except Exception as e:
    print(f"\n❌ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()

print("\n確認完了") 