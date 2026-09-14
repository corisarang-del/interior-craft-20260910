from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

VAULT = Path('/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사')
IMAGE_ROOT = VAULT / '기출문제' / '이미지'


def enhance_question_image(src, dst, scale=1.5):
    with Image.open(src).convert('RGB') as im:
        out = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
        out = ImageEnhance.Contrast(out).enhance(1.06)
        out = ImageEnhance.Sharpness(out).enhance(1.35)
        out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=105, threshold=3))
        dst.parent.mkdir(parents=True, exist_ok=True)
        out.save(dst, format='JPEG', quality=90, optimize=True, progressive=True)


def convert_all(src_root=IMAGE_ROOT, dst_root=None, scale=1.5):
    src_root = Path(src_root)
    dst_root = Path(dst_root) if dst_root else src_root
    files = sorted(src_root.glob('*/*.jpg'))
    converted = []
    for src in files:
        rel = src.relative_to(src_root)
        dst = dst_root / rel
        enhance_question_image(src, dst, scale=scale)
        converted.append(dst)
    return converted


if __name__ == '__main__':
    files = convert_all()
    print('converted', len(files), 'images')
