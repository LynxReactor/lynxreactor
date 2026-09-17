# Scripts

Утилиты для разработки проекта **LYNXREACTOR**.

⚠️ **Все скрипты запускаются из корня проекта** (там, где `manage.py`).

## i18n/

Утилиты для работы с переводами (`.po` → `.mo`).

| Скрипт | Назначение |
|--------|-----------|
| `check_po.py` | Аудит `.po` (fuzzy, empty, obsolete) |
| `check_po_selfmsgstr.py` | Поиск записей, где `msgstr == msgid` (непереведённые) |
| `check_i18n.py` | Проверка конкретных строк на EN/RU |
| `compile_mo.py` | Компиляция `.po` → `.mo` через polib |
| `remove_fuzzy.py` | Удаление `#, fuzzy` из шапки `.po` |
| `translate_po.py` | Автоперевод RU по словарю |

### Примеры

```bash
# 1. Проверить .po файлы
python scripts/i18n/check_po.py

# 2. Найти непереведённые записи в RU
python scripts/i18n/check_po_selfmsgstr.py

# 3. Проверить конкретные строки (EN/RU)
python scripts/i18n/check_i18n.py

# 4. Скомпилировать .po → .mo (если gettext не работает)
python scripts/i18n/compile_mo.py

# 5. Автоперевод (сначала dry-run)
python scripts/i18n/translate_po.py --dry-run
python scripts/i18n/translate_po.py