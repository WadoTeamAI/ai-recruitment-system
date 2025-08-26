#!/usr/bin/env python3
"""
HR採用支援システム - 統合デモランナー
整理されたフォルダ構成でのデモ実行
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# srcディレクトリを追加
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

def main():
    """メインデモ実行"""
    print("🚀 HR採用支援システム - 整理されたフォルダ構成でのデモ")
    print("=" * 60)
    
    print("\n📁 フォルダ構成:")
    print("hr_system/")
    print("├── src/          # ソースコード")
    print("├── docs/         # ドキュメント") 
    print("├── examples/     # サンプルデータ")
    print("├── output/       # 出力ファイル")
    print("├── config/       # 設定ファイル")
    print("└── run_demo.py   # このファイル")
    
    try:
        # 相対importを避けるため、直接importする
        from src.demo_script import demo_full_workflow, performance_comparison
        
        print("\n🎯 デモンストレーション開始...")
        demo_full_workflow()
        performance_comparison()
        
    except Exception as e:
        print(f"\n❌ デモ実行中にエラーが発生しました: {e}")
        
        # 代替方法として、個別にモジュールをテスト
        print("\n🔄 代替方法でテストを実行します...")
        test_individual_modules()

def test_individual_modules():
    """個別モジュールのテスト"""
    try:
        # パスを調整してimport
        import sys
        import os
        
        # 現在のディレクトリをsrcに変更
        original_dir = os.getcwd()
        src_dir = Path(__file__).parent / 'src'
        os.chdir(src_dir)
        
        # hr_recruitment_system.pyを直接実行
        print("\n📋 履歴書分析システムをテスト...")
        import hr_recruitment_system
        print("✅ hr_recruitment_system.py - 正常読み込み")
        
        # interview_system.pyをテスト
        print("\n❓ 面接システムをテスト...")
        import interview_system
        print("✅ interview_system.py - 正常読み込み")
        
        # 元のディレクトリに戻る
        os.chdir(original_dir)
        
        print("\n✅ 全モジュールが正常に読み込まれました!")
        print("\n📋 手動実行方法:")
        print("cd hr_system/src/")
        print("python hr_recruitment_system.py  # メインシステムテスト")
        print("python -c 'import hr_recruitment_system; hr_recruitment_system.main()'")
        
    except Exception as e:
        print(f"❌ 個別テストでもエラーが発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
