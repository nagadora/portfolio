# ポートフォリオサイト

このディレクトリは、GitHub Pages などで公開する  
ポートフォリオサイト本体を格納しています。

- シングルページ構成のトップ (`index.html`)
- 各プロジェクトの詳細ページ (`projects/*.html`)
- 共通スタイル (`styles.css`)
- 画像・スクリーンショットなど (`assets/`)

を前提とした、静的サイト構成になっています。

---

## 構成

```text
web/
├─ README.md
├─ index.html               # トップページ
├─ styles.css               # 全体スタイル
├─ projects/
│  ├─ creator-flow-log.html # Creator Flow Log（制作記録ツール）の紹介ページ
│  └─ art-guard-lab.html    # Art Guard Lab（画像保護ツール）の紹介ページ
└─ assets/
   └─ ...                   # ロゴ、スクリーンショット、説明図など