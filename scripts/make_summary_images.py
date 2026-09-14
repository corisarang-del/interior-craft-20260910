from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

VAULT = Path('/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사')
OUT = VAULT / '기출핵심요약' / '이미지확대'


def output_names(round_id, number):
    return f'{round_id}-q{int(number):02d}-problem.jpg', f'{round_id}-q{int(number):02d}-full.jpg'


def enhance_image(src, problem_out, full_out):
    im = Image.open(src).convert('RGB')
    # Source videos are 640x360. Use a high-quality 4x enlargement and mild
    # sharpening; keep the full frame for context and a problem crop for text.
    scale = 1.5
    full = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
    full = ImageEnhance.Contrast(full).enhance(1.06)
    full = ImageEnhance.Sharpness(full).enhance(1.35).filter(ImageFilter.UnsharpMask(radius=1.2, percent=105, threshold=3))
    # The question occupies the left ~62% of the NaHapgyeok frame.
    crop = im.crop((0, 0, int(im.width * 0.62), im.height))
    problem = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.Resampling.LANCZOS)
    problem = ImageEnhance.Contrast(problem).enhance(1.08)
    problem = ImageEnhance.Sharpness(problem).enhance(1.5).filter(ImageFilter.UnsharpMask(radius=1.3, percent=115, threshold=3))
    problem_out.parent.mkdir(parents=True, exist_ok=True)
    full_out.parent.mkdir(parents=True, exist_ok=True)
    problem.save(problem_out, format='JPEG', quality=92, optimize=True, progressive=True)
    full.save(full_out, format='JPEG', quality=90, optimize=True, progressive=True)


def build_from_summary(summary_path=None):
    import re
    summary_path = summary_path or (VAULT / '기출핵심요약' / '실내건축기능사.md')
    text = Path(summary_path).read_text(encoding='utf-8')
    seen = set(); mapping = {}
    for rel in re.findall(r'!\[\]\(([^)]+)\)', text):
        m = re.search(r'이미지/([^/]+)/q(\d+)\.jpg$', rel)
        if not m: continue
        rid, num = m.group(1), int(m.group(2))
        key = (rid, num)
        if key in seen: continue
        seen.add(key)
        src = VAULT / '기출문제' / '이미지' / rid / f'q{num:02d}.jpg'
        problem_name, full_name = output_names(rid, num)
        problem = OUT / problem_name; full = OUT / full_name
        enhance_image(src, problem, full)
        mapping[key] = {'problem': problem_name, 'full': full_name}
    return mapping

if __name__ == '__main__':
    m = build_from_summary()
    print('generated', len(m), 'images in', OUT)
