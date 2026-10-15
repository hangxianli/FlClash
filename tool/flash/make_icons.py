#!/usr/bin/env python3
"""Generate Flash launcher icons from the embedded 1024px source.

Runs in CI before the Android build: decodes tool/flash/icon-1024.b64 and
writes every launcher webp the res tree expects, plus assets/images/icon.png.
Requires Pillow (pip install pillow).
"""
import base64
import io
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RES = os.path.join(ROOT, 'android', 'app', 'src', 'main', 'res')

LEGACY = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
FOREGROUND = {'mdpi': 108, 'hdpi': 162, 'xhdpi': 216, 'xxhdpi': 324, 'xxxhdpi': 432}


def main():
    b64_path = os.path.join(os.path.dirname(__file__), 'icon-1024.b64')
    with open(b64_path, 'r', encoding='ascii') as f:
        src = Image.open(io.BytesIO(base64.b64decode(f.read()))).convert('RGBA')

    for density, px in LEGACY.items():
        icon = src.resize((px, px), Image.LANCZOS)
        mask = Image.new('L', (px, px), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, px, px], fill=255)
        round_icon = Image.new('RGBA', (px, px), (0, 0, 0, 0))
        round_icon.paste(icon, (0, 0), mask)
        for prefix in ('mipmap-', 'mipmap-television-'):
            folder = os.path.join(RES, f'{prefix}{density}')
            if not os.path.isdir(folder):
                continue
            icon.save(os.path.join(folder, 'ic_launcher.webp'), 'WEBP', lossless=True)
            round_path = os.path.join(folder, 'ic_launcher_round.webp')
            if prefix == 'mipmap-' or os.path.exists(round_path):
                round_icon.save(round_path, 'WEBP', lossless=True)
        fg_folder = os.path.join(RES, f'mipmap-{density}')
        src.resize((FOREGROUND[density], FOREGROUND[density]), Image.LANCZOS).save(
            os.path.join(fg_folder, 'ic_launcher_foreground.webp'), 'WEBP', lossless=True
        )

    src.resize((550, 550), Image.LANCZOS).save(
        os.path.join(ROOT, 'assets', 'images', 'icon.png')
    )
    print('Flash launcher icons generated.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
