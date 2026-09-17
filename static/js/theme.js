// static/js/theme.js

(function() {
    'use strict';

    /**
     * Получение сохранённой темы из localStorage
     */
    function getSavedTheme() {
        try {
            return localStorage.getItem('theme');
        } catch (e) {
            return null;
        }
    }

    /**
     * Получение системной темы
     */
    function getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    /**
     * Обновление иконки переключателя темы
     */
    function updateThemeToggleIcon(theme) {
        const toggle = document.getElementById('themeToggle');
        if (!toggle) return;

        const lightIcon = toggle.querySelector('.theme-icon-light');
        const darkIcon = toggle.querySelector('.theme-icon-dark');

        if (theme === 'dark') {
            if (lightIcon) lightIcon.style.display = 'none';
            if (darkIcon) darkIcon.style.display = 'inline';
        } else {
            if (lightIcon) lightIcon.style.display = 'inline';
            if (darkIcon) darkIcon.style.display = 'none';
        }
    }

    /**
     * Обновление темы в мобильном меню
     */
    function updateMobileThemeToggle(theme) {
        const mobileToggle = document.querySelector('.mobile-theme-toggle');
        if (!mobileToggle) return;

        const lightIcon = mobileToggle.querySelector('.theme-icon-light');
        const darkIcon = mobileToggle.querySelector('.theme-icon-dark');
        // Label НЕ трогаем — Django уже отрендерил {% trans "Сменить тему" %}

        if (theme === 'dark') {
            if (lightIcon) lightIcon.style.display = 'none';
            if (darkIcon) darkIcon.style.display = 'inline';
        } else {
            if (lightIcon) lightIcon.style.display = 'inline';
            if (darkIcon) darkIcon.style.display = 'none';
        }
    }

    /**
     * Установка темы
     * НЕ перезагружает страницу — картинки переключаются через CSS
     */
    function setTheme(theme, updateServer = true) {
        try {
            localStorage.setItem('theme', theme);
        } catch (e) {}

        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        updateThemeToggleIcon(theme);
        updateMobileThemeToggle(theme);

        // Сброс Turnstile
        document.querySelectorAll('.cf-turnstile').forEach(function(widget) {
            if (window.turnstile) {
                try { window.turnstile.reset(); } catch (e) {}
            }
        });

        if (updateServer) {
            fetch('/toggle-theme/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': window.getCsrfToken()
                },
                body: 'theme=' + encodeURIComponent(theme)
            })
            .then(function(response) {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(function(data) {
                if (data.success) {
                    console.log('✅ Theme set to:', data.theme);
                    // ✅ НЕ перезагружаем — картинки переключаются через CSS
                } else {
                    console.warn('⚠️ Theme toggle error:', data.error);
                }
            })
            .catch(function(error) {
                console.warn('⚠️ Theme toggle error:', error);
                // ✅ НЕ перезагружаем
            });
        }
    }

    /**
     * Переключение темы
     */
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        console.log('🔄 Switching theme from', currentTheme, 'to', newTheme);
        setTheme(newTheme, true);
    }

    /**
     * Инициализация темы при загрузке
     */
    function initTheme() {
        const savedTheme = getSavedTheme();
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const theme = savedTheme || currentTheme || getSystemTheme();

        console.log('🎨 Initializing theme:', theme);

        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        updateThemeToggleIcon(theme);
        updateMobileThemeToggle(theme);
    }

    // ============================================================
    // ЭКСПОРТ
    // ============================================================

    window.toggleTheme = toggleTheme;
    window.setTheme = setTheme;
    window.getSavedTheme = getSavedTheme;
    window.getSystemTheme = getSystemTheme;

    // ============================================================
    // ИНИЦИАЛИЗАЦИЯ
    // ============================================================

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }

    // ============================================================
    // ОБРАБОТЧИКИ
    // ============================================================

    document.addEventListener('DOMContentLoaded', function() {
        const themeToggleBtn = document.getElementById('themeToggle');
        if (themeToggleBtn) {
            const newBtn = themeToggleBtn.cloneNode(true);
            themeToggleBtn.parentNode.replaceChild(newBtn, themeToggleBtn);
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                toggleTheme();
            });
        }

        const mobileThemeToggle = document.querySelector('.mobile-theme-toggle');
        if (mobileThemeToggle) {
            const newMobileBtn = mobileThemeToggle.cloneNode(true);
            mobileThemeToggle.parentNode.replaceChild(newMobileBtn, mobileThemeToggle);
            newMobileBtn.addEventListener('click', function(e) {
                e.preventDefault();
                toggleTheme();
            });
        }
    });

    // ============================================================
    // СИСТЕМНАЯ ТЕМА
    // ============================================================

    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    darkModeMediaQuery.addEventListener('change', function(e) {
        if (!getSavedTheme()) {
            const newTheme = e.matches ? 'dark' : 'light';
            console.log('🔄 System theme changed to:', newTheme);
            setTheme(newTheme, true);
        }
    });

    console.log('🎨 Theme.js initialized');
})();