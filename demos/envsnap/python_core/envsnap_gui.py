# envsnap/python_core/envsnap_gui.py
from __future__ import annotations

import os
import sys
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- 重要：実行場所に依存せず同ディレクトリの collect.py / format.py を読めるようにする ---
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from collect import collect  # noqa: E402
from format import to_json, to_text  # noqa: E402


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("EnvSnap")
        self.minsize(820, 560)

        self.report = {}
        self._build_ui()
        self._bind_keys()

        # 起動直後に取得
        self.on_refresh()

    def _build_ui(self) -> None:
        # ルート
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        # 上部ボタン列
        bar = ttk.Frame(root)
        bar.pack(fill="x")

        ttk.Button(bar, text="Refresh", command=self.on_refresh).pack(side="left")
        ttk.Button(bar, text="Copy", command=self.on_copy).pack(side="left", padx=(8, 0))
        ttk.Button(bar, text="Save .txt", command=self.on_save_txt).pack(side="left", padx=(8, 0))
        ttk.Button(bar, text="Save .json", command=self.on_save_json).pack(side="left", padx=(8, 0))
        ttk.Button(bar, text="Quit", command=self.destroy).pack(side="right")

        # テキスト + スクロール
        body = ttk.Frame(root)
        body.pack(fill="both", expand=True, pady=(10, 0))

        self._text = tk.Text(
            body,
            wrap="word",
            undo=False,
            height=20,
            padx=10,
            pady=10,
        )
        self._text.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(body, orient="vertical", command=self._text.yview)
        scroll.pack(side="right", fill="y")
        self._text.configure(yscrollcommand=scroll.set)

        # 見やすさ：等幅寄り（環境によっては存在しないのでフォールバック）
        try:
            self._text.configure(font=("Consolas", 11))
        except Exception:
            pass

        # 読み取り専用っぽく（コピー用途なので編集は不要）
        self._text.configure(state="disabled")

        # ステータス
        self._status = ttk.Label(root, text="Ready", anchor="w")
        self._status.pack(fill="x", pady=(8, 0))

    def _bind_keys(self) -> None:
        # よく使うやつ
        self.bind("<Control-r>", lambda e: self.on_refresh())
        self.bind("<Control-R>", lambda e: self.on_refresh())
        self.bind("<Control-c>", lambda e: self.on_copy())
        self.bind("<Control-C>", lambda e: self.on_copy())

        # MacのCommandキー（Tkは環境次第で効く）
        self.bind("<Command-r>", lambda e: self.on_refresh())
        self.bind("<Command-c>", lambda e: self.on_copy())

    def _set_text(self, content: str) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.insert("1.0", content)
        self._text.configure(state="disabled")

    def _get_text(self) -> str:
        # state=disabled でも取得は可能
        return self._text.get("1.0", "end-1c")

    def _set_status(self, msg: str) -> None:
        self._status.configure(text=msg)

    def on_refresh(self) -> None:
        try:
            self._set_status("Collecting environment info...")
            self.update_idletasks()

            self.report = collect()
            content = to_text(self.report)

            self._set_text(content)
            self._set_status("Updated.")
        except Exception as e:
            self._set_status("Failed.")
            detail = traceback.format_exc()
            messagebox.showerror(
                "EnvSnap",
                "Failed to collect environment info.\n\n"
                f"{e}\n\n--- details ---\n{detail}",
            )

    def on_copy(self) -> None:
        content = self._get_text()
        if not content.strip():
            messagebox.showinfo("EnvSnap", "Nothing to copy.")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update_idletasks()  # クリップボード確定

        self._set_status("Copied to clipboard.")
        # うるさすぎるなら下のダイアログは消してOK
        messagebox.showinfo("EnvSnap", "Copied to clipboard.")

    def on_save_txt(self) -> None:
        content = self._get_text()
        if not content.strip():
            messagebox.showinfo("EnvSnap", "Nothing to save.")
            return

        path = filedialog.asksaveasfilename(
            title="Save as TXT",
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content + "\n")

        self._set_status(f"Saved: {os.path.basename(path)}")

    def on_save_json(self) -> None:
        if not self.report:
            messagebox.showinfo("EnvSnap", "Nothing to save.")
            return

        path = filedialog.asksaveasfilename(
            title="Save as JSON",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return

        content = to_json(self.report, pretty=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)

        self._set_status(f"Saved: {os.path.basename(path)}")


if __name__ == "__main__":
    App().mainloop()