# EnvSnap

問い合わせフォームで求められがちな OS / CPU / メモリ / GPU 等の環境情報を自動取得し、
GUI で表示してワンクリックでコピーできる小さなユーティリティです。

目的は「環境情報を調べて書く手間」と「転記ミス」を減らして、問い合わせの往復回数を減らすことです。

## ポリシー（取得しない情報）
- シリアル番号、MACアドレス、UUID などの個体識別子は取得しません
- 問い合わせに必要な範囲の環境情報に限定します

## このリポジトリの想定構成

```text
envsnap/
 ├ python_core/
 │   ├ collect.py          # 環境情報の収集
 │   ├ format.py           # 出力テキスト/JSON整形
 │   └ envsnap_gui.py      # GUI（Copy/Save/Refresh）
 ├ windows_csharp/         # 実験用（任意：Python呼び出し・Clipboard）
 ├ mac_kotlin/             # 実験用（任意：Python呼び出し・pbcopy）
 ├ dist/                   # ビルド成果物（基本はGit管理しない）
 ├ build_win.bat           # Windowsビルド（PyInstaller）
 ├ build_mac.sh            # macOSビルド（PyInstaller：Macがある場合）
 └ .github/workflows/