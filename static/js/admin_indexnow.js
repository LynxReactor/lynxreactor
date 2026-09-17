// static/js/admin_indexnow.js

(function() {
    'use strict';

    window.sendToIndexNow = function(url, id) {
        if (!confirm(`Отправить страницу "${url}" в IndexNow?`)) {
            return;
        }

        const button = event.target;
        const originalText = button.textContent;
        button.textContent = '⏳ Отправка...';
        button.disabled = true;

        // ✅ Используем глобальную функцию из utils.js
        const csrfToken = window.getCsrfToken ? window.getCsrfToken() : '';

        fetch('/admin/indexnow/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ url: url })
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP ${response.status}: ${text.substring(0, 200)}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                button.textContent = '✅ Отправлено';
                button.style.background = '#2ecc71';
                alert('✅ Страница успешно отправлена в IndexNow!');
                setTimeout(() => {
                    button.textContent = originalText;
                    button.style.background = '#C89A5B';
                    button.disabled = false;
                }, 3000);
            } else {
                button.textContent = '❌ Ошибка';
                button.style.background = '#e74c3c';
                alert('❌ Ошибка: ' + (data.message || 'Неизвестная ошибка'));
                setTimeout(() => {
                    button.textContent = originalText;
                    button.style.background = '#C89A5B';
                    button.disabled = false;
                }, 3000);
            }
        })
        .catch(error => {
            console.error('❌ Ошибка:', error);
            button.textContent = '❌ Ошибка';
            button.style.background = '#e74c3c';
            alert('❌ Ошибка отправки: ' + error.message);
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '#C89A5B';
                button.disabled = false;
            }, 3000);
        });
    };
})();