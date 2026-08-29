import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"
OUTPUT_FILE = BASE_DIR / "gallery.json"

CATEGORIES = (
    "manic",
    "pedic",
    "lashes",
    "brows",
    "hair",
    "biowave",
    "laser",
    "permanent",
    "pirsing",
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}

def image_files(folder: Path):
    if not folder.exists():
        return []
    return sorted(
        (
            file for file in folder.iterdir()
            if file.is_file() and file.suffix.lower() in ALLOWED_EXTENSIONS
        ),
        key=lambda p: p.name.lower()
    )

def relative(file: Path):
    return file.relative_to(BASE_DIR).as_posix()

def pretty_text(value: str):
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value

# -----------------------------
# ГЛАВНОЕ ФОТО
# -----------------------------
# Поддерживаются оба варианта:
# images/hero/
# images/hero.jpg
hero = ""

hero_folder_files = image_files(IMAGES_DIR / "hero")
if hero_folder_files:
    hero = relative(hero_folder_files[0])
else:
    for ext in ALLOWED_EXTENSIONS:
        candidate = IMAGES_DIR / f"hero{ext}"
        if candidate.exists():
            hero = relative(candidate)
            break

# -----------------------------
# ПРЕВЬЮ УСЛУГ
# -----------------------------
# Новый вариант:
# images/previews/hair/
#
# Если там пусто, берём первое фото из работ:
# images/works/hair/
# или старой папки:
# images/hair/
previews = {}
works = {}

for category in CATEGORIES:
    preview_files = image_files(IMAGES_DIR / "previews" / category)

    new_work_files = image_files(IMAGES_DIR / "works" / category)
    old_work_files = image_files(IMAGES_DIR / category)

    # Объединяем новые и старые папки без дублей
    all_work_files = []
    seen = set()

    for file in new_work_files + old_work_files:
        key = str(file.resolve())
        if key not in seen:
            seen.add(key)
            all_work_files.append(file)

    works[category] = [relative(file) for file in all_work_files]

    if preview_files:
        previews[category] = relative(preview_files[0])
    elif all_work_files:
        previews[category] = relative(all_work_files[0])
    else:
        previews[category] = ""

# -----------------------------
# МАСТЕРА
# -----------------------------
# images/masters/
#
# Имя файла:
# Алина.jpg
# или
# Алина__Маникюр и педикюр.jpg
masters = []

for file in image_files(IMAGES_DIR / "masters"):
    stem = file.stem

    if "__" in stem:
        name_raw, specialty_raw = stem.split("__", 1)
        name = pretty_text(name_raw)
        specialty = pretty_text(specialty_raw)
    else:
        name = pretty_text(stem)
        specialty = "Beauty-мастер"

    masters.append({
        "image": relative(file),
        "name": name or "Мастер салона",
        "specialty": specialty or "Beauty-мастер",
    })

manifest = {
    "hero": hero,
    "previews": previews,
    "works": works,
    "masters": masters,
}

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    json.dump(manifest, file, ensure_ascii=False, indent=2)

print()
print("Готово:", OUTPUT_FILE)
print()

print("Главное фото:", hero if hero else "не найдено")
print()

print("Услуги:")
for category in CATEGORIES:
    print(
        f"{category}: "
        f"{len(works[category])} работ, "
        f"превью: {'есть' if previews[category] else 'нет'}"
    )

print()
print("Мастера:", len(masters))
print()
print("gallery.json обновлён.")
