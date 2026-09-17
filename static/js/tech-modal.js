// static/js/tech-modal.js

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        var lang = document.documentElement.lang || 'ru';
        lang = lang.split('-')[0];

        var translations = {
            'ru': {
                'category': 'Категория',
                'badge': 'Основной'
            },
            'en': {
                'category': 'Category',
                'badge': 'Primary'
            }
        };

        var t = translations[lang] || translations['ru'];

        var modal = document.getElementById('techModal');
        var closeBtn = document.getElementById('techModalClose');
        var modalTitle = document.getElementById('techModalTitle');
        var modalCategory = document.getElementById('techModalCategory');
        var modalBadge = document.getElementById('techModalBadge');
        var modalDescription = document.getElementById('techModalDescription');
        var modalIcon = document.getElementById('techModalIcon');

        function getTechData(item) {
            return {
                name: item.dataset.techName || 'Technology',
                category: item.dataset.techCategory || 'Other',
                badge: item.dataset.techBadge || '',
                description: item.dataset.techDescription || 'No description available',
                icon: item.querySelector('.tech-icon img') ? item.querySelector('.tech-icon img').src : ''
            };
        }

        function openTechModal(techData) {
            if (!modal) return;

            if (modalTitle) modalTitle.textContent = techData.name || 'Technology';
            if (modalCategory) {
                modalCategory.textContent = t.category + ': ' + (techData.category || 'Other');
            }
            if (modalBadge) {
                if (techData.badge) {
                    modalBadge.textContent = t.badge;
                    modalBadge.style.display = 'inline-block';
                } else {
                    modalBadge.style.display = 'none';
                }
            }
            if (modalDescription) modalDescription.textContent = techData.description || 'No description available';
            if (modalIcon) {
                if (techData.icon) {
                    modalIcon.innerHTML = '<img src="' + techData.icon + '" alt="' + techData.name + '" loading="lazy">';
                } else {
                    modalIcon.innerHTML = '<span class="tech-icon-placeholder">' + (techData.name ? techData.name.charAt(0) : '?') + '</span>';
                }
            }

            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        function closeTechModal() {
            if (modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        }

        // ============================================================
        // ✅ КЛИК НА ВСЮ КАРТОЧКУ (НО НЕ НА КНОПКУ)
        // ============================================================

        var techItems = document.querySelectorAll('.tech-item');

        techItems.forEach(function(item) {
            item.addEventListener('click', function(e) {
                // Если кликнули по кнопке — не открываем модалку дважды
                if (e.target.closest('.tech-more-btn')) {
                    return;
                }
                var techData = getTechData(this);
                openTechModal(techData);
            });
        });

        // ============================================================
        // ✅ КЛИК НА КНОПКУ "Узнать больше"
        // ============================================================

        var buttons = document.querySelectorAll('.tech-more-btn');
        buttons.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                var item = this.closest('.tech-item');
                if (!item) return;
                var techData = getTechData(item);
                openTechModal(techData);
            });
        });

        // ============================================================
        // ЗАКРЫТИЕ МОДАЛКИ
        // ============================================================

        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                closeTechModal();
            });
        }

        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeTechModal();
                }
            });
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeTechModal();
            }
        });

        window.openTechModal = openTechModal;
        window.closeTechModal = closeTechModal;

        console.log('🔧 Tech Modal initialized (click on card)');
        console.log('📝 Language:', lang);
    });

})();