// static/admin/js/jazzmin-custom.js

// ========================================
// JAZZMIN CUSTOM - LYNXREACTOR
// ========================================

document.addEventListener('DOMContentLoaded', function() {

    // ========================================
    // ПОДСВЕТКА АКТИВНЫХ ЭЛЕМЕНТОВ
    // ========================================

    // Добавляем класс для анимации строк таблицы
    document.querySelectorAll('.table tbody tr').forEach((row, index) => {
        row.style.setProperty('--row-index', index + 1);
    });

    // ========================================
    // ПРЕВЬЮ ИЗОБРАЖЕНИЙ В ТАБЛИЦАХ
    // ========================================

    document.querySelectorAll('.field-image_preview img').forEach(img => {
        img.addEventListener('click', function(e) {
            // Открыть изображение в модальном окне или новом окне
            if (this.src) {
                window.open(this.src, '_blank');
            }
        });
    });

    // ========================================
    // ПОДСКАЗКИ ДЛЯ ПОЛЕЙ
    // ========================================

    // Добавляем подсказки к полям с классом .help-text
    document.querySelectorAll('.help-text').forEach(el => {
        el.style.color = '#A6A3A0';
        el.style.fontSize = '12px';
        el.style.marginTop = '4px';
    });

    // ========================================
    // КАСТОМНЫЙ ВАЛИДАТОР ДЛЯ ПОЛЕЙ EMAIL
    // ========================================

    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', function() {
            const email = this.value;
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (email && !regex.test(email)) {
                this.style.borderColor = '#b13a3a';
                this.style.boxShadow = '0 0 0 3px rgba(177, 58, 58, 0.15)';
            } else {
                this.style.borderColor = 'rgba(200, 154, 91, 0.15)';
                this.style.boxShadow = 'none';
            }
        });
    });

    // ========================================
    // КАСТОМНЫЙ ПОИСК
    // ========================================

    const searchInput = document.querySelector('#searchbar');
    if (searchInput) {
        searchInput.placeholder = 'Поиск...';
        searchInput.style.borderRadius = '8px';
        searchInput.style.padding = '10px 16px';
    }

    // ========================================
    // КОНТЕКСТНОЕ МЕНЮ (опционально)
    // ========================================

    document.querySelectorAll('.row-actions a').forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.color = '#C89A5B';
        });
        link.addEventListener('mouseleave', function() {
            this.style.color = '';
        });
    });

    // ========================================
    // АВТОСОХРАНЕНИЕ (опционально)
    // ========================================

    // Автосохранение каждые 30 секунд для форм с классом .auto-save
    document.querySelectorAll('.auto-save').forEach(form => {
        setInterval(() => {
            if (form.querySelector('input, textarea, select')) {
                // Проверяем, есть ли изменения
                const changed = form.querySelector('.changed');
                if (changed) {
                    form.submit();
                }
            }
        }, 30000);
    });

    // ========================================
    // КАСТОМНЫЙ TOAST / УВЕДОМЛЕНИЯ
    // ========================================

    // Добавляем стилизацию для уведомлений
    document.querySelectorAll('.alert').forEach(alert => {
        // Добавляем иконку
        const icon = document.createElement('i');
        if (alert.classList.contains('alert-success')) {
            icon.className = 'fas fa-check-circle mr-2';
        } else if (alert.classList.contains('alert-danger')) {
            icon.className = 'fas fa-exclamation-circle mr-2';
        } else if (alert.classList.contains('alert-warning')) {
            icon.className = 'fas fa-exclamation-triangle mr-2';
        } else {
            icon.className = 'fas fa-info-circle mr-2';
        }
        alert.prepend(icon);

        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            alert.style.transition = 'all 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 500);
        }, 5000);
    });

    // ========================================
    // ГОРЯЧИЕ КЛАВИШИ
    // ========================================

    document.addEventListener('keydown', function(e) {
        // Ctrl + S - сохранение
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const submitBtn = document.querySelector('input[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }

        // Ctrl + Shift + P - поиск
        if (e.ctrlKey && e.shiftKey && e.key === 'P') {
            e.preventDefault();
            const search = document.querySelector('#searchbar');
            if (search) {
                search.focus();
            }
        }
    });

    // ========================================
    // DARK MODE TOGGLE (для пользователя)
    // ========================================

    // Добавляем кнопку переключения темы
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'btn btn-sm btn-outline-light ml-2';
        toggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
        toggleBtn.style.borderColor = 'rgba(200, 154, 91, 0.3)';
        toggleBtn.style.color = '#C89A5B';
        toggleBtn.title = 'Переключить тему';

        toggleBtn.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const icon = this.querySelector('i');
            if (document.body.classList.contains('dark-mode')) {
                icon.className = 'fas fa-sun';
                document.body.style.background = '#0B0B0C';
            } else {
                icon.className = 'fas fa-moon';
                document.body.style.background = '';
            }
        });

        const navRight = document.querySelector('.navbar-nav.ml-auto');
        if (navRight) {
            const li = document.createElement('li');
            li.className = 'nav-item';
            li.appendChild(toggleBtn);
            navRight.prepend(li);
        }
    }

    // ========================================
    // КНОПКА "ОТПРАВИТЬ В INDEXNOW" ДЛЯ АДМИНКИ
    // ========================================

    // Добавляем кнопку "Отправить в IndexNow" в список изменений
    const changelistForm = document.querySelector('#changelist-form');
    if (changelistForm) {
        const actions = document.querySelector('.actions');
        if (actions) {
            const indexnowBtn = document.createElement('button');
            indexnowBtn.type = 'button';
            indexnowBtn.className = 'btn btn-primary ml-2';
            indexnowBtn.innerHTML = '📤 Отправить выбранные в IndexNow';
            indexnowBtn.style.cssText = `
                background: linear-gradient(135deg, #C89A5B 0%, #9A6D35 100%) !important;
                border: none !important;
                color: #0B0B0C !important;
                padding: 6px 16px !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
            `;
            indexnowBtn.addEventListener('mouseenter', function() {
                this.style.background = 'linear-gradient(135deg, #D8B477 0%, #C89A5B 100%) !important';
            });
            indexnowBtn.addEventListener('mouseleave', function() {
                this.style.background = 'linear-gradient(135deg, #C89A5B 0%, #9A6D35 100%) !important';
            });

            indexnowBtn.addEventListener('click', function() {
                // Собираем выбранные ID
                const selected = document.querySelectorAll('input.action-select:checked');
                if (selected.length === 0) {
                    alert('⚠️ Выберите хотя бы одну запись для отправки.');
                    return;
                }

                // Получаем URL для каждой записи
                const urls = [];
                selected.forEach(function(checkbox) {
                    const row = checkbox.closest('tr');
                    if (row) {
                        const viewLink = row.querySelector('.field-__str__ a');
                        if (viewLink) {
                            const url = viewLink.getAttribute('href');
                            if (url) {
                                urls.push(url);
                            }
                        }
                    }
                });

                if (urls.length === 0) {
                    alert('⚠️ Не удалось получить URL для выбранных записей.');
                    return;
                }

                if (confirm(`Отправить ${urls.length} записей в IndexNow?`)) {
                    // Отправляем на сервер
                    fetch('/admin/indexnow/submit/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken()
                        },
                        body: JSON.stringify({ urls: urls })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('✅ ' + data.message);
                        } else {
                            alert('❌ ' + data.message);
                        }
                    })
                    .catch(error => {
                        alert('❌ Ошибка отправки: ' + error.message);
                    });
                }
            });

            actions.appendChild(indexnowBtn);
        }
    }

    // ========================================
    // ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    // ========================================

    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (token) return token;
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
});