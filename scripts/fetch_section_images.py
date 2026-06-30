#!/usr/bin/env python3
"""Download copyright-free section images (Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "static" / "images"
CONTENT = ROOT / "content"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

DOWNLOADS: dict[str, tuple[str, str]] = {
    "burgers.webp": (PEX.format(id="1639557"), "Pexels #1639557"),
    "wings-chicken.webp": (PEX.format(id="106343"), "Pexels #106343"),
    "fries.webp": (PEX.format(id="4498573"), "Pexels #4498573"),
    "salad.webp": (PEX.format(id="1213710"), "Pexels #1213710"),
    "dipping-sauces.webp": (PEX.format(id="2772535"), "Pexels #2772535"),
    "build-your-meal.webp": (PEX.format(id="769289"), "Pexels #769289"),
    "special-deals.webp": (PEX.format(id="958545"), "Pexels #958545"),
    "promotions.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "hero.webp": (PEX.format(id="2702674"), "Pexels #2702674"),
    "slideshow-burgers.webp": (PEX.format(id="1639557"), "Pexels #1639557"),
    "slideshow-wings.webp": (PEX.format(id="106343"), "Pexels #106343"),
    "slideshow-fries.webp": (PEX.format(id="4498573"), "Pexels #4498573"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
    "burgers": "burgers.webp",
    "wings-chicken": "wings-chicken.webp",
    "fries": "fries.webp",
    "salad": "salad.webp",
    "dipping-sauces": "dipping-sauces.webp",
    "build-your-meal": "build-your-meal.webp",
    "special-deals": "special-deals.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def download_one(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = (
            "<p>Halal certified burgers, wings, and fries in Chaguanas. "
            "Build your meal with sides and dipping sauces.</p>"
        )
    text = (
        "---\n"
        'title: "Brgrs n Wngs"\n'
        f"image: {img('hero.webp')}\n"
        "images:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('burgers.webp')}\n"
        f"    - image: {img('wings-chicken.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('slideshow-burgers.webp')}\n"
        f"    - image: {img('slideshow-wings.webp')}\n"
        f"    - image: {img('slideshow-fries.webp')}\n"
        f"    - image: {img('special-deals.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    credits: list[str] = []
    for filename, (url, credit) in DOWNLOADS.items():
        if download_one(filename, url):
            credits.append(f"- {filename} — {credit}")

    for section, image_file in SECTIONS.items():
        if (IMAGES_DIR / image_file).exists():
            update_section_index(section, image_file)
        else:
            print(f"WARN: missing {image_file} for {section}")

    if (IMAGES_DIR / "hero.webp").exists():
        update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos (Pexels License — free to use):\n" + "\n".join(credits) + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
