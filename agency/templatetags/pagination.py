# agency/templatetags/pagination.py

from django import template

register = template.Library()


@register.simple_tag
def page_range(current, total, delta=2):
    """
    Возвращает range страниц вокруг текущей для пагинации.
    Пример: current=5, total=10, delta=2 → [3, 4, 5, 6, 7]
    """
    try:
        current = int(current)
        total = int(total)
        delta = int(delta)
    except (TypeError, ValueError):
        return range(1, 2)

    start = max(1, current - delta)
    end = min(total, current + delta)
    return range(start, end + 1)