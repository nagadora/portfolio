# デモソフトウェア集（demos/）

このディレクトリには、ポートフォリオ用に用意した  
「実際に動作する」デモソフトウェアをまとめています。

Web 側（`web/`）は画面イメージやコンセプトを伝えることに特化し、  
こちらの `demos/` は、実行可能なツールとして動作することを重視しています。

## 収録方針
- 可能な限り「手元で実行できる」こと
- 実行手順（依存関係／ビルド／配布物）が README だけで追えること
- 配布物（exe/app）は `dist/` に出す想定（基本はGit管理しない）

## ディレクトリ構成

```text
demos/
├─ README.md
├─ envsnap/                   # 問い合わせ用 環境情報スナップショット（GUI / Copy対応）
│  ├─ python_core/
│  │  ├─ collect.py
│  │  ├─ format.py
│  │  └─ envsnap_gui.py
│  ├─ windows_csharp/          # 実験用（任意）
│  ├─ mac_kotlin/              # 実験用（任意）
│  ├─ dist/                    # ビルド成果物（例：envsnap_win.exe / EnvSnap_mac.app）
│  ├─ build_win.bat            # Windows向けビルド（PyInstaller）
│  ├─ build_mac.sh             # macOS向けビルド（Macがある場合）
│  └─ README.md
├─ creator-flow-log-kotlin/    # 制作記録管理ツール（Kotlin CLI）
└─ art-guard-lab-python/       # 画像保護フィルタ（Python）