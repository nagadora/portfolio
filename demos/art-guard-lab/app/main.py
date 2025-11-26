from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from protect_filters import protect_image, ProtectConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Art Guard Lab CLI Demo")
    parser.add_argument("input", help="入力画像パス")
    parser.add_argument("output", help="出力画像パス")
    parser.add_argument("--mode", default="combo", choices=["fft", "jitter", "combo"], help="保護モード")
    parser.add_argument("--strength", type=float, default=0.6, help="強さ（0.0〜1.0）")
    parser.add_argument("--mix", type=float, default=0.9, help="オリジナルとのブレンド比（0.0〜1.0）")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    img = Image.open(input_path)

    cfg = ProtectConfig(
        fft_strength=args.strength,
        jitter_max_shift=1.0 + args.strength,
        mix_ratio=args.mix,
    )

    result = protect_image(img, mode=args.mode, cfg=cfg)
    result.save(output_path)

    print("変換完了:", output_path)


if __name__ == "__main__":
    main()