САХАР — структура изображений

1. Главное фото
   images/hero/
   Положи сюда одну или несколько фотографий.
   На сайте используется ПЕРВАЯ по алфавиту.

2. Превью карточек услуг
   images/previews/manic/
   images/previews/pedic/
   images/previews/lashes/
   images/previews/brows/
   images/previews/hair/
   images/previews/biowave/
   images/previews/laser/
   images/previews/permanent/

   Для каждой карточки используется первая фотография по алфавиту.
   Удобно назвать её 01.jpg.

3. Работы
   images/works/manic/
   images/works/pedic/
   images/works/lashes/
   images/works/brows/
   images/works/hair/
   images/works/biowave/
   images/works/laser/
   images/works/permanent/

   Сюда можно кидать любое количество фото.
   Все они появятся в разделе "Наши работы".

4. Мастера
   images/masters/

   Можно просто назвать фото:
   Алина.jpg

   Тогда на сайте будет:
   Алина
   Beauty-мастер

   Или указать специализацию прямо в имени:
   Алина__Маникюр и педикюр.jpg
   Мария__Брови и ресницы.webp

   Два нижних подчёркивания "__" разделяют имя и специализацию.

5. После любых изменений изображений запусти:

   python generate_gallery.py

   Скрипт пересоздаст gallery.json.
   После этого можно проверять сайт через Flask или загружать на Netlify.

Поддерживаемые форматы:
.jpg .jpeg .png .webp .gif .avif

ВАЖНО:
gallery.json вручную редактировать не нужно.
