/**
 * Модуль анимации монет с поддержкой переключения языка
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        const coins = document.querySelectorAll('.stat-icon.coin');

        if (!coins.length) return;

        // Запускаем анимацию для каждой монеты
        coins.forEach(function(coin, index) {
            coin.classList.remove('spin');
            void coin.offsetWidth;

            setTimeout(function() {
                coin.classList.add('spin');
            }, index * 800);
        });

        // ===== СМЕНА ИЗОБРАЖЕНИЙ ПРИ ПЕРЕКЛЮЧЕНИИ ЯЗЫКА =====
        function updateCoinImages(lang) {
            const images = document.querySelectorAll('.coin-img');

            images.forEach(function(img) {
                const newSrc = img.getAttribute('data-' + lang);
                if (newSrc && img.src !== newSrc) {
                    // Добавляем плавный переход
                    img.style.transition = 'opacity 0.3s ease';
                    img.style.opacity = '0.5';

                    setTimeout(function() {
                        img.src = newSrc;
                        img.style.opacity = '1';
                    }, 150);
                }
            });
        }

        // Функция для определения текущего языка
        function getCurrentLanguage() {
            // Проверяем атрибут lang на html
            const htmlLang = document.documentElement.lang || 'ru';
            // Проверяем cookie Django
            const cookieMatch = document.cookie.match(/django_language=([^;]+)/);
            const cookieLang = cookieMatch ? cookieMatch[1] : null;
            // Проверяем URL параметр
            const urlParams = new URLSearchParams(window.location.search);
            const urlLang = urlParams.get('language');

            // Приоритет: URL > Cookie > HTML
            const lang = urlLang || cookieLang || htmlLang;
            return lang.split('-')[0]; // ru-RU → ru
        }

        // Обновляем изображения при загрузке
        const initialLang = getCurrentLanguage();
        setTimeout(function() {
            updateCoinImages(initialLang);
        }, 300);

        // Наблюдаем за изменением атрибута lang на html
        const observer = new MutationObserver(function() {
            const lang = getCurrentLanguage();
            updateCoinImages(lang);
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['lang']
        });

        // Слушаем событие смены языка
        document.addEventListener('languageChanged', function(e) {
            const lang = e.detail.lang || 'ru';
            setTimeout(function() {
                updateCoinImages(lang);
            }, 100);
        });

        // Перехватываем клики по ссылкам переключения языка
        document.querySelectorAll('a[href*="language="], form[action*="set_language"]').forEach(function(el) {
            el.addEventListener('click', function() {
                // Ждем перезагрузки страницы
                setTimeout(function() {
                    const lang = getCurrentLanguage();
                    updateCoinImages(lang);
                }, 200);
            });
        });

        // Перехватываем submit формы смены языка
        document.querySelectorAll('form[action*="set_language"]').forEach(function(form) {
            form.addEventListener('submit', function() {
                setTimeout(function() {
                    const lang = getCurrentLanguage();
                    updateCoinImages(lang);
                }, 200);
            });
        });

        // Экспортируем функцию для глобального использования
        window.updateCoinImages = updateCoinImages;
        window.getCurrentLanguage = getCurrentLanguage;

        console.log('🪙 Coin stats initialized');
        console.log('📝 Current language:', initialLang);
    });

})();