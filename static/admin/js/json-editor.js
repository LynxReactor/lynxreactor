// static/admin/js/json-editor.js

(function() {
    'use strict';

    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }

    ready(function() {
        const editors = document.querySelectorAll('.json-editor[data-json-field="true"]');

        editors.forEach(function(editor) {
            // Оборачиваем
            const wrapper = document.createElement('div');
            wrapper.className = 'json-editor-wrapper';
            editor.parentNode.insertBefore(wrapper, editor);
            wrapper.appendChild(editor);

            const fieldName = editor.id || editor.name || '';
            const fieldType = getFieldType(fieldName);

            // Helper
            const helper = document.createElement('div');
            helper.className = 'json-editor-helper';
            helper.innerHTML = `
                <span class="helper-title">💡 Формат JSON:</span>
                <code>{"key": "value"}</code> или <code>["item1", "item2"]</code>
                <span class="example">📝 Пример: ${getExample(fieldType)}</span>
            `;
            wrapper.appendChild(helper);

            // Валидация
            editor.addEventListener('blur', function() {
                const value = this.value.trim();
                if (!value) {
                    this.classList.remove('error');
                    return;
                }
                try {
                    JSON.parse(value);
                    this.classList.remove('error');
                } catch (e) {
                    this.classList.add('error');
                    showError(this, e.message);
                }
            });

            editor.addEventListener('input', function() {
                this.classList.remove('error');
            });

            // Format button
            const formatBtn = document.createElement('button');
            formatBtn.type = 'button';
            formatBtn.className = 'json-format-btn';
            formatBtn.textContent = '🔧 Форматировать JSON';
            formatBtn.addEventListener('click', function() {
                formatJSON(editor);
            });
            wrapper.appendChild(formatBtn);

            // Clear button
            const clearBtn = document.createElement('button');
            clearBtn.type = 'button';
            clearBtn.className = 'json-format-btn';
            clearBtn.textContent = '🗑️ Очистить';
            clearBtn.style.cssText = 'margin-left:8px;background:rgba(248,81,73,0.1);color:#f85149;';
            clearBtn.addEventListener('click', function() {
                editor.value = '';
                editor.classList.remove('error');
                showNotification('🗑️ Поле очищено', 'success');
            });
            wrapper.appendChild(clearBtn);
        });

        function getFieldType(name) {
            if (name.includes('features')) return 'features';
            if (name.includes('gallery') || name.includes('images')) return 'gallery';
            if (name.includes('technologies')) return 'technologies';
            return 'default';
        }

        function getExample(type) {
            const examples = {
                'features': '["Быстрая загрузка", "Адаптивный дизайн"]',
                'gallery': '["/media/photo1.jpg", "/media/photo2.jpg"]',
                'technologies': '["Python", "Django", "PostgreSQL"]',
                'default': '{"key": "value"}',
            };
            return examples[type] || examples['default'];
        }

        function formatJSON(editor) {
            try {
                const value = editor.value.trim();
                if (!value) return;
                const parsed = JSON.parse(value);
                editor.value = JSON.stringify(parsed, null, 2);
                editor.classList.remove('error');
                showNotification('✅ JSON отформатирован', 'success');
            } catch (e) {
                editor.classList.add('error');
                showNotification('❌ Ошибка: ' + e.message, 'error');
            }
        }

        function showError(editor, message) {
            const existing = editor.parentNode.querySelector('.json-error-message');
            if (existing) existing.remove();

            const div = document.createElement('div');
            div.className = 'json-error-message';
            div.style.cssText = 'margin-top:8px;padding:8px 12px;background:rgba(248,81,73,0.1);'
                + 'border:1px solid rgba(248,81,73,0.2);border-radius:4px;color:#f85149;font-size:12px;';
            div.textContent = '❌ ' + message;
            editor.parentNode.appendChild(div);
        }

        function showNotification(message, type) {
            document.querySelectorAll('.json-notification').forEach(el => el.remove());

            const n = document.createElement('div');
            n.className = `json-notification ${type}`;
            n.textContent = message;
            document.body.appendChild(n);

            requestAnimationFrame(() => n.classList.add('show'));
            setTimeout(() => {
                n.classList.remove('show');
                setTimeout(() => n.remove(), 400);
            }, 3000);
        }
    });
})();