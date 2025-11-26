# Creator Flow Log – Kotlin Demo

イラスト・Live2D 制作の「作業ログ」を  
ローカルで簡単に管理できる Kotlin 製のデモアプリです。

CLI ベースで動く軽量ツールで、  
制作工程を可視化するポートフォリオ用途の技術デモとして作成しています。

---

## できること

- 制作ログの追加（作品名・作業内容・日付など）
- ログ一覧の参照
- JSON ファイル (`creator_flow_log_gui.json`) への保存・読み書き
- GUI 版とのデータ共有（今後の拡張前提）

---

## プロジェクト構成

実際のフォルダ構成に合わせた説明です。

```text
creator_flow_log_kotlin/
├─ .git/                    # Git 管理
├─ .gradle/                 # Gradle の内部キャッシュ
├─ .idea/                   # IntelliJ IDEA プロジェクト設定
├─ .kotlin/                 # Kotlin ビルドキャッシュ
├─ build/                   # ビルド成果物（jar など）
├─ gradle/                  # ラッパースクリプト用設定
├─ KotlinProject/           # (IDE の設定により生成されている場合)
├─ src/
│   ├─ main/
│   │   ├─ kotlin/          # Kotlin ソースコード
│   │   └─ resources/       # リソース（必要なら）
│   └─ test/                # テストコード（必要なら）
│
├─ creator_flow_log_gui.json  # 制作ログの保存先（アプリが自動で更新）
├─ build.gradle.kts           # Gradle 設定（Kotlin DSL）
├─ settings.gradle.kts        # プロジェクト設定
├─ gradlew                    # Unix 用 Gradle ラッパー
├─ gradlew.bat                # Windows 用 Gradle ラッパー
└─ .gitignore