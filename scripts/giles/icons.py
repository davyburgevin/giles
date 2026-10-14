"""Render the independent Giles monogram with Pillow, without external artwork."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args().out
    image = Image.new('RGBA', (1024, 1024))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((70, 70, 954, 954), radius=205, fill='#142832')
    # Geometric G, rather than a host-specific font.
    draw.arc((250, 240, 774, 784), 40, 320, fill='#EAD6A3', width=100)
    draw.line((540, 525, 775, 525, 775, 680), fill='#EAD6A3', width=100)
    assets = out / 'apps/desktop/assets'
    assets.mkdir(parents=True, exist_ok=True)
    image.save(assets / 'icon.icns', sizes=[(16,16),(32,32),(64,64),(128,128),(256,256),(512,512),(1024,1024)])
    image.save(assets / 'icon.png')
    image.save(assets / 'icon.ico', sizes=[(16,16),(32,32),(48,48),(256,256)])
    for name in ('nous-girl.png', 'nous-girl-dark.png', 'squircle-light.png', 'squircle-dark.png'):
        image.save(assets / name)
    # The build renderer copies prepared public images independently of assets.
    public = out / 'apps/desktop/public'
    public.mkdir(parents=True, exist_ok=True)
    for name in ('nous-girl.png', 'nous-girl-dark.png', 'favicon.png'):
        image.save(public / name)


if __name__ == '__main__':
    main()
