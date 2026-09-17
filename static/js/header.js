// static/js/header.js

/**
 * LYNXREACTOR — Header: бургер-меню, скролл, мобильное меню
 * Отдельный модуль для надёжности (main.js мог упасть).
 */

(function() {
    'use strict';

    // ============================================================
    // БУРГЕР-МЕНЮ
    // ============================================================

    function initBurgerMenu() {
        const burgerBtn = document.getElementById('burgerBtn');
        const mobileOverlay = document.getElementById('mobileOverlay');
        const closeOverlay = document.getElementById('closeOverlay');

        if (!burgerBtn || !mobileOverlay) {
            console.warn('🍔 Burger elements not found');
            return;
        }

        function openMenu() {
            mobileOverlay.classList.add('open');
            document.body.style.overflow = 'hidden';
            document.body.classList.add('mobile-menu-open');
        }

        function closeMenu() {
            mobileOverlay.classList.remove('open');
            document.body.style.overflow = '';
            document.body.classList.remove('mobile-menu-open');
        }

        // Открытие по бургеру
        burgerBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            openMenu();
        });

        // Закрытие по крестику
        if (closeOverlay) {
            closeOverlay.addEventListener('click', function(e) {
                e.preventDefault();
                closeMenu();
            });
        }

        // Закрытие по клику на overlay (вне меню)
        mobileOverlay.addEventListener('click', function(e) {
            if (e.target === mobileOverlay) {
                closeMenu();
            }
        });

        // Закрытие по Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && mobileOverlay.classList.contains('open')) {
                closeMenu();
            }
        });

        // Закрытие при клике на ссылку внутри меню
        mobileOverlay.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function() {
                // Небольшая задержка чтобы анимация сработала
                setTimeout(closeMenu, 150);
            });
        });

        console.log('🍔 Burger menu initialized');
    }

    // ============================================================
    // SCROLL — эффект "прилипшей" шапки
    // ============================================================

    function initHeaderScroll() {
        const header = document.getElementById('mainHeader');
        if (!header) return;

        let ticking = false;

        function updateHeader() {
            const scrolled = window.pageYOffset || document.documentElement.scrollTop || 0;
            if (scrolled > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
            ticking = false;
        }

        window.addEventListener('scroll', function() {
            if (!ticking) {
                requestAnimationFrame(updateHeader);
                ticking = true;
            }
        }, { passive: true });

        // Инициализация
        updateHeader();
    }

    // ============================================================
    // ИНИЦИАЛИЗАЦИЯ
    // ============================================================

    function init() {
        initBurgerMenu();
        initHeaderScroll();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('🎯 Header.js loaded');
})();