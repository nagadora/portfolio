# protect_filters.py
#
# 画像保護用のフィルタ実装。
# - 高周波ノイズ（エッジ強調）
# - ラインジッター（行ごとの水平方向ゆらぎ）
# - 色量子化（階調を落としてディテール削り）
#
# strength: 0.0 ~ 1.0 を想定（GUI のスライダー）
# mix      : 0.0 ~ 1.0 を想定（combo でのブレンド比）

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def ensure_rgb(img: Image.Image) -> Image.Image:
    """必ず RGB に統一（RGBA / L などが来ても防ぐ）"""
    if img.mode != "RGB":
        return img.convert("RGB")
    return img


# ============================
# 1. 高周波ノイズ系フィルタ
# ============================

def apply_highfreq(img: Image.Image, strength: float) -> Image.Image:
    """
    エッジ付近に強くノイズを乗せる高周波フィルタ。
    strength が大きいほどノイズが強くなる。
    """
    img = ensure_rgb(img)
    arr = np.asarray(img).astype(np.float32) / 255.0  # (H, W, 3)

    # グレースケールで簡易エッジ強度を計算
    gray = arr.mean(axis=2)
    gy, gx = np.gradient(gray)
    edge_mag = np.sqrt(gx * gx + gy * gy)  # 0〜?（エッジが強いほど大きい）
    edge_mag = np.clip(edge_mag * 4.0, 0.0, 1.0)  # 少し強調して 0〜1 に収める

    # エッジほどノイズが強くなるようにマスク
    # 0.3〜1.0 の範囲にする
    mask = 0.3 + 0.7 * edge_mag
    mask = mask[..., None]  # (H, W, 1)

    # strength に応じたノイズ量
    # 0.0 → 0, 1.0 → 標準偏差 0.2 くらい
    noise_sigma = 0.05 + 0.15 * strength
    noise = np.random.normal(loc=0.0, scale=noise_sigma, size=arr.shape).astype(
        np.float32
    )

    out = arr + noise * mask
    out = np.clip(out, 0.0, 1.0)

    return Image.fromarray((out * 255.0).astype(np.uint8))


# ============================
# 2. ラインジッターフィルタ
# ============================

def apply_line_jitter(img: Image.Image, strength: float) -> Image.Image:
    """
    行ごとに水平方向へランダムシフトをかける。
    線画や輪郭が「ゆらいで」見えるような効果。

    strength が大きいほどシフト量が増える。
    """
    img = ensure_rgb(img)
    arr = np.asarray(img)
    h, w, c = arr.shape

    # 最大シフト幅（ピクセル）
    # strength=0.0 → 1px, 1.0 → 12px くらい
    max_shift = int(1 + 11 * strength)
    if max_shift <= 0:
        return img

    out = np.empty_like(arr)

    # 行ごとにランダムなシフト量で左右にずらす
    for y in range(h):
        shift = np.random.randint(-max_shift, max_shift + 1)
        out[y] = np.roll(arr[y], shift, axis=0)

    return Image.fromarray(out)


# ============================
# 3. 色量子化（階調を削る）
# ============================

def quantize_colors(img: Image.Image, levels: int) -> Image.Image:
    """
    RGB 各チャンネルを 'levels' 段階に量子化する。
    levels を小さくするとグラデーションが大きく崩れる。
    """
    img = ensure_rgb(img)
    arr = np.asarray(img).astype(np.float32)

    levels = max(2, int(levels))
    step = 255.0 / float(levels - 1)

    arr_q = np.round(arr / step) * step
    arr_q = np.clip(arr_q, 0.0, 255.0)

    return Image.fromarray(arr_q.astype(np.uint8))


# ============================
# 4. combo モード（全部盛り）
# ============================

@dataclass
class ComboParams:
    strength: float  # 0〜1
    mix: float       # 0〜1


def apply_combo(img: Image.Image, strength: float, mix: float) -> Image.Image:
    """
    - まず色階調を削る（量子化）
    - 高周波ノイズを付加
    - ラインジッターで線を揺らす
    - 最後に元画像とブレンド（mix）
    """
    strength = float(np.clip(strength, 0.0, 1.0))
    mix = float(np.clip(mix, 0.0, 1.0))

    base = ensure_rgb(img)

    # 1) 色量子化：strength が強いほど levels を小さくする
    #    strength=0 → levels=64, 1 → levels=8
    max_levels = 64
    min_levels = 8
    levels = int(max_levels - (max_levels - min_levels) * strength)
    quant = quantize_colors(base, levels=levels)

    # 2) 高周波ノイズ（量子化後の画像に適用）
    hi = apply_highfreq(quant, strength=strength)

    # 3) ラインジッター
    jittered = apply_line_jitter(hi, strength=strength)

    # 4) 元の量子化画像とのブレンド
    #    mix=0 → 量子化だけ
    #    mix=1 → ジッター＋ノイズをフル適用
    jittered = jittered.convert("RGB")
    quant = quant.convert("RGB")

    out = Image.blend(quant, jittered, alpha=mix)
    return out


# ============================
# 5. エントリポイント用ラッパ
# ============================

Mode = Literal["highfreq", "jitter", "combo"]


def apply_protect_filter(img: Image.Image, mode: Mode, strength: float, mix: float) -> Image.Image:
    """
    GUI / CLI から呼び出す統一インターフェース。
    """
    mode = mode.lower()

    if mode == "highfreq":
        return apply_highfreq(img, strength=strength)
    elif mode == "jitter":
        return apply_line_jitter(img, strength=strength)
    elif mode == "combo":
        return apply_combo(img, strength=strength, mix=mix)
    else:
        # 不明なモードの場合は元画像をそのまま返す
        return ensure_rgb(img)
        
        
# ============================
# 6. 旧インターフェースとの互換レイヤ
# ============================

class ProtectConfig:
    """
    旧バージョンとの互換用設定クラス。

    ・引数なし ProtectConfig() でもOK
    ・mode / strength / mix をキーワード付きで渡してもOK
    ・fft_strength など追加のキーワードも **kwargs で受け取って無視する
    """

    def __init__(
        self,
        mode: str = "combo",
        strength: float = 0.9,
        mix: float = 0.9,
        **kwargs
    ):
        self.mode = mode
        self.strength = strength
        self.mix = mix
        # 追加パラメータ（fft_strength など）は今は使わない
        self.extra = kwargs


def protect_image(
    img: Image.Image,
    config: ProtectConfig | None = None,
    *,
    mode: str | None = None,
    strength: float | None = None,
    mix: float | None = None,
    **kwargs,
) -> Image.Image:
    """
    旧バージョンとの互換用ラッパー。

    - protect_image(img, config=ProtectConfig(...))
    - protect_image(img, mode="combo", strength=0.9, mix=0.8)
    - protect_image(img, ProtectConfig(...))  ← 位置引数パターン

    みたいな呼び出しを全部受けられるようにして、
    最終的には apply_protect_filter に集約する。
    """

    # 1) config が渡されていれば、そこを優先
    if config is not None:
        mode_val = config.mode
        strength_val = config.strength
        mix_val = config.mix
    else:
        # 2) 個別のキーワードから組み立てる
        mode_val = mode if mode is not None else "combo"
        strength_val = strength if strength is not None else 0.9
        mix_val = mix if mix is not None else 0.9

    return apply_protect_filter(
        img=img,
        mode=mode_val,
        strength=strength_val,
        mix=mix_val,
    )