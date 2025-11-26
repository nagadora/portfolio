from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from PIL import Image

from protect_filters import ProtectConfig, protect_image


class ArtGuardGuiApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Art Guard Lab - GUI Demo")
        self.geometry("600x260")
        self.resizable(False, False)

        # 状態
        self.input_path: Path | None = None

        # ウィンドウ背景色
        self.configure(bg="#0f172a")

        # ウィジェット生成
        self._create_widgets()

    def _create_widgets(self) -> None:
        root = self

        root.columnconfigure(0, weight=1)

        # タイトル
        title_label = tk.Label(
            root,
            text="Art Guard Lab (GUI Demo)",
            font=("Meiryo UI", 14, "bold"),
            fg="#e5e7eb",
            bg="#0f172a",
        )
        title_label.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))

        subtitle_label = tk.Label(
            root,
            text="SNS投稿前の画像に、高周波＋ジッターの保護フィルタをかけるデモツールです。",
            font=("Meiryo UI", 9),
            fg="#9ca3af",
            bg="#0f172a",
        )
        subtitle_label.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

        # 入力ファイル行
        file_frame = tk.Frame(root, bg="#0f172a")
        file_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)

        file_label = tk.Label(
            file_frame,
            text="入力画像:",
            font=("Meiryo UI", 10),
            fg="#e5e7eb",
            bg="#0f172a",
        )
        file_label.grid(row=0, column=0, sticky="w")

        self.file_path_var = tk.StringVar(value="（未選択）")
        file_path_label = tk.Label(
            file_frame,
            textvariable=self.file_path_var,
            font=("Meiryo UI", 9),
            fg="#9ca3af",
            bg="#0f172a",
            anchor="w",
        )
        file_path_label.grid(row=0, column=1, sticky="ew", padx=(8, 8))

        file_button = ttk.Button(
            file_frame,
            text="画像を選択...",
            command=self.on_select_file,
        )
        file_button.grid(row=0, column=2, sticky="e")

        # モード & スライダー
        controls_frame = tk.Frame(root, bg="#0f172a")
        controls_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 8))
        controls_frame.columnconfigure(1, weight=1)

        # モード選択
        mode_label = tk.Label(
            controls_frame,
            text="モード:",
            font=("Meiryo UI", 10),
            fg="#e5e7eb",
            bg="#0f172a",
        )
        mode_label.grid(row=0, column=0, sticky="w")

        self.mode_var = tk.StringVar(value="combo")
        mode_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.mode_var,
            values=["fft", "jitter", "combo"],
            state="readonly",
            width=10,
        )
        mode_combo.grid(row=0, column=1, sticky="w")

        # strength スライダー
        strength_label = tk.Label(
            controls_frame,
            text="強さ (strength):",
            font=("Meiryo UI", 10),
            fg="#e5e7eb",
            bg="#0f172a",
        )
        strength_label.grid(row=1, column=0, sticky="w", pady=(8, 0))

        self.strength_var = tk.DoubleVar(value=0.6)
        strength_scale = ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            variable=self.strength_var,
        )
        strength_scale.grid(row=1, column=1, sticky="ew", pady=(8, 0), padx=(8, 8))

        self.strength_value_label = tk.Label(
            controls_frame,
            text="0.60",
            font=("Meiryo UI", 9),
            fg="#9ca3af",
            bg="#0f172a",
        )
        self.strength_value_label.grid(row=1, column=2, sticky="e", pady=(8, 0))
        self.strength_var.trace_add("write", self._update_strength_label)

        # mix スライダー
        mix_label = tk.Label(
            controls_frame,
            text="ブレンド (mix):",
            font=("Meiryo UI", 10),
            fg="#e5e7eb",
            bg="#0f172a",
        )
        mix_label.grid(row=2, column=0, sticky="w", pady=(8, 0))

        self.mix_var = tk.DoubleVar(value=0.9)
        mix_scale = ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            variable=self.mix_var,
        )
        mix_scale.grid(row=2, column=1, sticky="ew", pady=(8, 0), padx=(8, 8))

        self.mix_value_label = tk.Label(
            controls_frame,
            text="0.90",
            font=("Meiryo UI", 9),
            fg="#9ca3af",
            bg="#0f172a",
        )
        self.mix_value_label.grid(row=2, column=2, sticky="e", pady=(8, 0))
        self.mix_var.trace_add("write", self._update_mix_label)

        # 実行ボタン & ステータス
        bottom_frame = tk.Frame(root, bg="#0f172a")
        bottom_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=(8, 12))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="準備完了。入力画像を選択してください。")
        status_label = tk.Label(
            bottom_frame,
            textvariable=self.status_var,
            font=("Meiryo UI", 9),
            fg="#9ca3af",
            bg="#0f172a",
            anchor="w",
        )
        status_label.grid(row=0, column=0, sticky="w")

        run_button = ttk.Button(
            bottom_frame,
            text="変換して保存",
            command=self.on_run,
        )
        run_button.grid(row=0, column=1, sticky="e")

    # ===== イベントハンドラ =====

    def on_select_file(self) -> None:
        filetypes = [
            ("画像ファイル", "*.png *.jpg *.jpeg *.webp *.bmp"),
            ("すべてのファイル", "*.*"),
        ]
        filename = filedialog.askopenfilename(
            title="入力画像を選択",
            filetypes=filetypes,
        )
        if not filename:
            return
        self.input_path = Path(filename)
        self.file_path_var.set(str(self.input_path))
        self.status_var.set("入力画像が選択されました。")

    def on_run(self) -> None:
        if self.input_path is None:
            messagebox.showwarning("入力画像なし", "まず入力画像を選択してください。")
            return

        initial_name = self.input_path.stem + "_protected.png"
        out_path_str = filedialog.asksaveasfilename(
            title="出力画像の保存先",
            defaultextension=".png",
            initialfile=initial_name,
            filetypes=[("PNG 画像", "*.png"), ("すべてのファイル", "*.*")],
        )
        if not out_path_str:
            return

        mode = self.mode_var.get()
        strength = float(self.strength_var.get())
        mix = float(self.mix_var.get())

        try:
            self.status_var.set("変換中です...")
            self.update_idletasks()

            img = Image.open(self.input_path)

            cfg = ProtectConfig(
                fft_strength=strength,
                jitter_max_shift=1.0 + strength,
                mix_ratio=mix,
            )

            protected = protect_image(img, mode=mode, cfg=cfg)
            protected.save(out_path_str)

        except Exception as e:
            messagebox.showerror("エラー", f"変換に失敗しました。\n{e}")
            self.status_var.set("エラーが発生しました。詳細はメッセージをご確認ください。")
            return

        self.status_var.set(f"変換が完了しました：{out_path_str}")
        messagebox.showinfo("完了", "画像の変換と保存が完了しました。")

    # ===== スライダー表示更新 =====

    def _update_strength_label(self, *args) -> None:
        self.strength_value_label.config(text=f"{self.strength_var.get():.2f}")

    def _update_mix_label(self, *args) -> None:
        self.mix_value_label.config(text=f"{self.mix_var.get():.2f}")


def main() -> None:
    app = ArtGuardGuiApp()
    app.mainloop()


if __name__ == "__main__":
    main()