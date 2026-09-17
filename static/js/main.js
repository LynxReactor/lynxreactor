// static/js/main.js

(function() {
    'use strict';

    // ============================================================
    // МОДАЛКА УСЛУГ
    // ============================================================

    function openServiceModal(data) {
        const modal = document.getElementById('serviceModal');
        if (!modal) return;

        const numberEl = document.getElementById('serviceModalNumber');
        const titleEl = document.getElementById('serviceModalTitle');
        const descEl = document.getElementById('serviceModalDescription');
        const imageEl = document.getElementById('serviceModalImage');

        if (numberEl) numberEl.textContent = data.number || '01';
        if (titleEl) titleEl.textContent = data.title || 'Услуга';
        if (descEl) descEl.textContent = data.description || 'Описание отсутствует';

        if (imageEl) {
            // Выбираем картинку по текущей теме
            const theme = document.documentElement.getAttribute('data-theme') || 'light';
            const imgSrc = theme === 'dark'
                ? (data.imageDark || data.imageLight)
                : (data.imageLight || data.imageDark);

            if (imgSrc) {
                imageEl.src = imgSrc;
                imageEl.style.display = 'block';
            } else {
                imageEl.style.display = 'none';
                imageEl.removeAttribute('src');
            }
        }

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeServiceModal() {
        const modal = document.getElementById('serviceModal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    function extractServiceData(card) {
        // Новые атрибуты data-service-image-light/dark (для карточек из БД),
        // с fallback на старый data-service-image (для default-карточек)
        const light = card.dataset.serviceImageLight || card.dataset.serviceImage || '';
        const dark = card.dataset.serviceImageDark || card.dataset.serviceImage || '';

        return {
            number: card.dataset.serviceNumber || '01',
            title: card.dataset.serviceTitle || 'Услуга',
            description: card.dataset.serviceDescription || 'Описание отсутствует',
            imageLight: light,
            imageDark: dark,
        };
    }

    // ============================================================
    // ДЕЛЕГИРОВАНИЕ (без MutationObserver, без дублей)
    // ============================================================

    document.addEventListener('click', function(e) {
        // Кнопка "Подробнее" на карточке услуги
        const serviceBtn = e.target.closest('.service-more-btn');
        if (serviceBtn) {
            e.preventDefault();
            e.stopPropagation();
            const card = serviceBtn.closest('.service-card');
            if (card) openServiceModal(extractServiceData(card));
            return;
        }

        // Клик по самой карточке услуги (не по кнопке/ссылке)
        const serviceCard = e.target.closest('.service-card');
        if (serviceCard && !e.target.closest('button, a')) {
            openServiceModal(extractServiceData(serviceCard));
            return;
        }

        // Закрытие модалки по клику на overlay
        if (e.target.id === 'serviceModal') closeServiceModal();
    });

    // Кнопка закрытия
    const serviceModalClose = document.getElementById('serviceModalClose');
    if (serviceModalClose) {
        serviceModalClose.addEventListener('click', closeServiceModal);
    }

    // Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeServiceModal();
    });

    // Экспорт (на случай, если понадобится извне)
    window.openServiceModal = openServiceModal;
    window.closeServiceModal = closeServiceModal;

    console.log('🔧 Main.js initialized (services only, delegation)');
})();