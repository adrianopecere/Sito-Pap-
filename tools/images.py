#!/usr/bin/env python3
"""Prepare images for the site (needs Pillow: `python3 -m pip install pillow`).

  python3 tools/images.py cover  SOURCE BOOK_ID     -> public/assets/img/covers/BOOK_ID.jpg
  python3 tools/images.py photo  SOURCE NAME        -> public/assets/img/photos/NAME.jpg (+ NAME-sm.jpg)
  python3 tools/images.py portrait SOURCE           -> public/assets/img/portrait.jpg
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

ASSETS = Path(__file__).resolve().parent.parent / 'public' / 'assets' / 'img'


def _open(src):
    im = ImageOps.exif_transpose(Image.open(src))
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        bg = Image.new('RGB', im.size, 'white')
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert('RGB')


def _save(im, dest, width, quality):
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, 'JPEG', quality=quality, optimize=True, progressive=True)
    print(f'{dest.relative_to(ASSETS.parent.parent.parent)}  {im.width}x{im.height}  {dest.stat().st_size // 1024} KB')


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    kind, src = argv[1], argv[2]
    im = _open(src)
    if kind == 'cover':
        _save(im, ASSETS / 'covers' / f'{argv[3]}.jpg', 520, 86)
    elif kind == 'photo':
        _save(im, ASSETS / 'photos' / f'{argv[3]}.jpg', 2400, 80)
        _save(im, ASSETS / 'photos' / f'{argv[3]}-sm.jpg', 1100, 78)
    elif kind == 'portrait':
        _save(im, ASSETS / 'portrait.jpg', 900, 84)
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main(sys.argv)
