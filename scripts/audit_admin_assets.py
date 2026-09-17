#!/usr/bin/env python3
"""
audit_admin_assets.py — аудит подключений CSS/JS админки LYNXREACTOR.

Ищет:
  1. JAZZMIN_SETTINGS['custom_css'] и ['custom_js'] в settings
  2. Любые упоминания 'admin/css/' и 'admin/js/' в проекте
  3. Файлы, лежащие в static/admin/css/ и static/admin/js/
  4. Media-классы в admin.py (inline css/js)

Запуск (из корня проекта):
    python scripts/audit_admin_assets.py
"""
import re
import sys
from pathlib import Path

# Корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Директории, где искать код (не трогаем venv, node_modules, .git)
SCAN_DIRS = [
    'agency',
    'lynxreactor',
    'templates',
    'scripts',
]
SCAN_EXTS = ('.py', '.html', '.json', '.cfg', '.ini')

# Что искать в коде
PATTERNS = [
    (re.compile(r'custom_css\s*[=:]\s*[\'"]([^\'"]+)[\'"]'), 'custom_css'),
    (re.compile(r'custom_js\s*[=:]\s*[\'"]([^\'"]+)[\'"]'), 'custom_js'),
    (re.compile(r'admin/css/([\w\-/\.]+\.css)'), 'admin/css/'),
    (re.compile(r'admin/js/([\w\-/\.]+\.js)'), 'admin/js/'),
    (re.compile(r'[\'"]([\w\-/]*\.css)[\'"]'), 'css_ref'),
    (re.compile(r'[\'"]([\w\-/]*\.js)[\'"]'), 'js_ref'),
]


def scan_code():
    """Поиск паттернов в коде проекта."""
    results = []
    for dir_name in SCAN_DIRS:
        dir_path = BASE_DIR / dir_name
        if not dir_path.exists():
            continue
        for path in dir_path.rglob('*'):
            if not path.is_file():
                continue
            if path.suffix not in SCAN_EXTS:
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except (UnicodeDecodeError, PermissionError):
                continue

            for lineno, line in enumerate(text.splitlines(), 1):
                for pattern, label in PATTERNS:
                    for match in pattern.finditer(line):
                        results.append({
                            'file': str(path.relative_to(BASE_DIR)),
                            'line': lineno,
                            'label': label,
                            'match': match.group(0),
                            'value': match.group(1) if match.groups() else '',
                        })
    return results


def list_static_admin_files():
    """Список файлов в static/admin/css и static/admin/js."""
    static_dir = BASE_DIR / 'static' / 'admin'
    result = {'css': [], 'js': [], 'other': []}
    if not static_dir.exists():
        return result

    for path in sorted(static_dir.rglob('*')):
        if not path.is_file():
            continue
        rel = str(path.relative_to(BASE_DIR))
        if path.suffix == '.css':
            result['css'].append(rel)
        elif path.suffix == '.js':
            result['js'].append(rel)
        else:
            result['other'].append(rel)
    return result


def main():
    print('=' * 70)
    print('AUDIT: подключения admin CSS/JS')
    print('=' * 70)
    print(f'BASE_DIR: {BASE_DIR}')
    print()

    # --- 1. Поиск в коде ---
    print('--- 1. Упоминания в коде ---')
    results = scan_code()
    if not results:
        print('  Ничего не найдено.')
    else:
        # группируем по label
        by_label = {}
        for r in results:
            by_label.setdefault(r['label'], []).append(r)
        for label in ('custom_css', 'custom_js', 'admin/css/', 'admin/js/'):
            items = by_label.get(label, [])
            if items:
                print(f'\n  [{label}]')
                for r in items:
                    print(f"    {r['file']}:{r['line']}  {r['match']}")

    # --- 2. Файлы в static/admin/ ---
    print()
    print('--- 2. Файлы в static/admin/ ---')
    files = list_static_admin_files()
    print(f"  CSS:  {len(files['css'])}")
    for f in files['css']:
        print(f"    {f}")
    print(f"  JS:   {len(files['js'])}")
    for f in files['js']:
        print(f"    {f}")
    if files['other']:
        print(f"  Other: {len(files['other'])}")
        for f in files['other']:
            print(f"    {f}")

    # --- 3. Сводка ---
    print()
    print('=' * 70)
    print('СВОДКА')
    print('=' * 70)

    custom_css_refs = [r for r in results if r['label'] == 'custom_css']
    custom_js_refs = [r for r in results if r['label'] == 'custom_js']

    print(f"  custom_css в коде: {len(custom_css_refs)}")
    for r in custom_css_refs:
        print(f"    {r['file']}:{r['line']}  -> {r['value']}")

    print(f"  custom_js в коде: {len(custom_js_refs)}")
    for r in custom_js_refs:
        print(f"    {r['file']}:{r['line']}  -> {r['value']}")

    # Все .css / .js-упоминания в admin-контексте
    print()
    print('  Все ссылки на admin/css/ или admin/js/:')
    admin_refs = [r for r in results if r['label'] in ('admin/css/', 'admin/js/')]
    for r in admin_refs:
        print(f"    [{r['file']}:{r['line']}]  {r['match']}")


if __name__ == '__main__':
    main()