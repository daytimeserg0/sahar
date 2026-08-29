import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright

COMPANY_ID = "706799"
PAGE_URL = f"https://n751124.yclients.com/company/{COMPANY_ID}/personal/select-master?o=m5667039"

BOOKING_URL = (
    f"https://n751124.yclients.com/company/{COMPANY_ID}/personal/select-master?o=m{{}}"
)
REVIEWS_URL = (
    f"https://n751124.yclients.com/company/{COMPANY_ID}/personal/"
    f"select-master/master-info/{COMPANY_ID}/{{}}?o=m{{}}"
)

BASE_DIR = Path(__file__).resolve().parent
LOCAL_MASTERS_DIR = BASE_DIR / "images" / "masters"
OUTPUT_FILE = BASE_DIR / "masters.json"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


def normalize_name(value: str) -> str:
    """Нормализация имени для сопоставления с именем файла."""
    value = value.strip().lower()
    value = value.replace("ё", "е")
    value = re.sub(r"\s+", " ", value)
    return value


def find_local_photo(master_id: str, master_name: str) -> str | None:
    """
    Ищет локальную фотографию мастера.

    Приоритет:
    1. images/masters/<ID>.<ext>
    2. images/masters/<Имя мастера>.<ext>
    3. если не найдено — None, и будет использовано фото YCLIENTS.
    """
    LOCAL_MASTERS_DIR.mkdir(parents=True, exist_ok=True)

    files = [
        file
        for file in LOCAL_MASTERS_DIR.iterdir()
        if file.is_file() and file.suffix.lower() in ALLOWED_EXTENSIONS
    ]

    # Самый надёжный вариант — имя файла совпадает с ID мастера.
    for file in files:
        if file.stem.strip() == master_id:
            return file.relative_to(BASE_DIR).as_posix()

    wanted_name = normalize_name(master_name)

    # Второй вариант — имя файла совпадает с именем мастера.
    for file in files:
        if normalize_name(file.stem) == wanted_name:
            return file.relative_to(BASE_DIR).as_posix()

    return None


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page(
            viewport={"width": 1440, "height": 1200},
            locale="ru-RU",
        )

        print("Открываю YCLIENTS...")
        await page.goto(PAGE_URL, wait_until="networkidle", timeout=120000)
        await page.wait_for_timeout(2000)

        # Догружаем все карточки и изображения.
        for _ in range(8):
            await page.mouse.wheel(0, 1000)
            await page.wait_for_timeout(250)

        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(400)

        raw_masters = await page.evaluate(
            r"""
            () => {
                const containers = Array.from(
                    document.querySelectorAll('[data-locator^="master_container_"]')
                );

                return containers.map(container => {
                    const locator = container.getAttribute('data-locator') || '';
                    const id = locator.replace('master_container_', '');

                    const nameEl = container.querySelector(
                        '[data-locator="master_name"]'
                    );

                    const specialtyEl = container.querySelector(
                        '[data-locator="master_position_or_specialization"]'
                    );

                    const avatarEl = container.querySelector(
                        'img[data-locator="avatar"]'
                    );

                    const feedbacksEl = container.querySelector(
                        '[data-locator="feedbacks_count"]'
                    );

                    return {
                        id,
                        name: nameEl ? nameEl.textContent.trim() : '',
                        specialty: specialtyEl
                            ? specialtyEl.textContent.trim()
                            : '',
                        yclients_image: avatarEl
                            ? (avatarEl.currentSrc || avatarEl.src || '')
                            : '',
                        reviews_count: feedbacksEl
                            ? Number(feedbacksEl.textContent.trim())
                            : null,
                    };
                });
            }
            """
        )

        masters = []

        for master in raw_masters:
            master_id = str(master.get("id", "")).strip()
            name = str(master.get("name", "")).strip()

            # Виртуальную карточку "Любой специалист" не добавляем.
            if (
                not master_id
                or master_id == "-1"
                or not name
                or name.lower() == "любой специалист"
            ):
                continue

            local_photo = find_local_photo(master_id, name)
            image = local_photo or master.get("yclients_image", "")

            masters.append({
                "id": master_id,
                "name": name,
                "specialty": str(master.get("specialty", "")).strip(),
                "image": image,
                "reviews_count": master.get("reviews_count"),
                "reviews_url": REVIEWS_URL.format(master_id, master_id),
                "booking_url": BOOKING_URL.format(master_id),
            })

        OUTPUT_FILE.write_text(
            json.dumps(masters, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print()
        print(f"Готово: {OUTPUT_FILE}")
        print(f"Найдено мастеров: {len(masters)}")
        print()

        for master in masters:
            source = (
                "локальное фото"
                if master["image"].startswith("images/")
                else "фото YCLIENTS"
            )
            reviews = (
                master["reviews_count"]
                if master["reviews_count"] is not None
                else "-"
            )

            print(
                f"{master['name']} | "
                f"{master['specialty'] or 'без специализации'} | "
                f"отзывов: {reviews} | "
                f"{source}"
            )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
