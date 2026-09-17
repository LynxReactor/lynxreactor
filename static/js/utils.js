// static/js/utils.js

(function() {
    'use strict';

    /**
     * Получение CSRF токена
     */
    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (token) return token;
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    /**
     * Показ уведомления
     */
    function showNotification(type, message) {
        const existing = document.querySelector('.notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.className = 'notification notification-' + type;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${type === 'success' ? '✅' : '❌'}</span>
                <span class="notification-message">${message.replace(/\n/g, '<br>')}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const bgColor = type === 'success'
            ? (isDark ? 'rgba(45, 143, 90, 0.95)' : 'rgba(46, 204, 113, 0.95)')
            : (isDark ? 'rgba(177, 58, 58, 0.95)' : 'rgba(231, 76, 60, 0.95)');

        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '24px',
            zIndex: '9999',
            maxWidth: '450px',
            padding: '16px 20px',
            borderRadius: '12px',
            background: bgColor,
            color: '#ffffff',
            boxShadow: isDark ? '0 8px 40px rgba(0,0,0,0.4)' : '0 8px 40px rgba(0,0,0,0.15)',
            backdropFilter: 'blur(10px)',
            transform: 'translateX(100%)',
            opacity: '0',
            transition: 'all 0.5s ease',
            fontFamily: 'var(--font-sans, sans-serif)',
            fontSize: '14px'
        });

        document.body.appendChild(notification);

        requestAnimationFrame(function() {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        });

        setTimeout(function() {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(100%)';
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 500);
            }
        }, 5000);

        notification.querySelector('.notification-close')?.addEventListener('click', function() {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 500);
        });
    }

    // Экспорт
    window.getCsrfToken = getCsrfToken;
    window.showNotification = showNotification;

    console.log('🔧 Utils initialized');
})();