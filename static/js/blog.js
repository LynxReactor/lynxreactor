// static/js/blog.js

/**
 * LYNXREACTOR — Blog JS
 *  - Голосование за посты (.post-vote-btn, .vote-btn)
 *  - Формы подписки (#subscribeForm, #sidebarSubscribeForm)
 *  Все строки интерфейса — через window.I18N (см. i18n_strings.html).
 */

(function() {
    'use strict';

    // ============================================================
    // I18N HELPER
    // ============================================================

    function t(key, fallback) {
        return (window.I18N && window.I18N[key]) || fallback || key;
    }

    // ============================================================
    // УВЕДОМЛЕНИЕ
    // ============================================================

    function notify(type, message) {
        if (typeof window.showNotification === 'function') {
            window.showNotification(type, message);
        } else {
            console.log(`[${type}] ${message}`);
        }
    }

    // ============================================================
    // ГОЛОСОВАНИЕ
    // ============================================================

    async function handleVote(btn, voteType, postId) {
        const flag = `voteInFlight_${postId}`;
        if (window[flag]) {
            console.log(`⏳ Vote already in flight for post ${postId}, skipping`);
            return;
        }
        window[flag] = true;

        const allBtns = document.querySelectorAll(`[data-post-id="${postId}"]`);
        allBtns.forEach(b => b.disabled = true);

        try {
            const response = await fetch(`/blog/vote/${postId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.getCsrfToken()
                },
                body: JSON.stringify({ vote_type: voteType })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                notify('error', data.error || t('vote_error', 'Ошибка голосования'));
                return;
            }

            updateCounters(postId, data.likes, data.dislikes);
            updateActiveState(postId, data.user_vote);

            const actionMsg =
                data.action === 'added'   ? '✅ ' + t('vote_added', 'Спасибо за голос!') :
                data.action === 'removed' ? '🗑️ ' + t('vote_removed', 'Голос отменён') :
                data.action === 'changed' ? '✅ ' + t('vote_changed', 'Голос изменён') :
                '✅ ' + t('vote_done', 'Готово');

            notify('success', actionMsg);

        } catch (error) {
            console.error('Vote error:', error);
            notify('error', t('vote_error', 'Ошибка голосования. Попробуйте позже.'));
        } finally {
            allBtns.forEach(b => b.disabled = false);
            window[flag] = false;
        }
    }

    function updateCounters(postId, likes, dislikes) {
        const detailLike = document.getElementById('likeCount');
        const detailDislike = document.getElementById('dislikeCount');
        if (detailLike) detailLike.textContent = likes;
        if (detailDislike) detailDislike.textContent = dislikes;

        const listLike = document.getElementById(`postLikeCount-${postId}`);
        const listDislike = document.getElementById(`postDislikeCount-${postId}`);
        if (listLike) listLike.textContent = likes;
        if (listDislike) listDislike.textContent = dislikes;
    }

    function updateActiveState(postId, userVote) {
        const btns = document.querySelectorAll(`[data-post-id="${postId}"]`);

        btns.forEach(b => {
            b.classList.remove('active');

            const voteType = b.dataset.vote;
            if (voteType === userVote) {
                b.classList.add('active');
            }
        });
    }

    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.post-vote-btn, .vote-btn');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        const voteType = btn.dataset.vote;
        const postId = btn.dataset.postId;

        if (!voteType) {
            console.warn('Vote button missing data-vote');
            return;
        }

        if (!postId) {
            console.warn('Vote button missing data-post-id');
            return;
        }

        handleVote(btn, voteType, postId);
    });

    // ============================================================
    // УНИВЕРСАЛЬНАЯ ОБРАБОТКА ФОРМ ПОДПИСКИ
    // ============================================================

    function initSubscribeFormById(config) {
        const form = document.getElementById(config.formId);
        if (!form) return;

        const emailInput = form.querySelector('input[name="email"]');
        const submitBtn = form.querySelector(config.btnSelector);
        const messageEl = document.getElementById(config.messageId);

        if (!emailInput || !submitBtn || !messageEl) {
            console.warn(`Subscribe form "${config.formId}" is missing required elements`);
            return;
        }

        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const flag = `submitting_${config.formId}`;
            if (window[flag]) {
                return;
            }

            const email = (emailInput.value || '').trim();

            if (!email) {
                showMsg('error', t('subscribe_empty_email', 'Пожалуйста, введите email'));
                emailInput.focus();
                return;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showMsg('error', t('subscribe_invalid_email', 'Введите корректный email'));
                emailInput.classList.add('error');
                emailInput.focus();
                return;
            }

            emailInput.classList.remove('error');

            window[flag] = true;

            submitBtn.disabled = true;
            const btnTextEl = submitBtn.querySelector('.subscribe-btn-text');
            const originalText = btnTextEl ? btnTextEl.textContent : null;
            if (btnTextEl) btnTextEl.textContent = '...';

            try {
                const formData = new FormData(form);

                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': window.getCsrfToken()
                    },
                    body: formData
                });

                if (!response.ok && response.status !== 400 && response.status !== 429) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    showMsg('success', '✅ ' + (data.message || t('subscribe_success', 'Спасибо за подписку!')));
                    form.reset();
                } else {
                    showMsg('error', data.error || t('subscribe_error', 'Ошибка подписки'));
                }
            } catch (error) {
                console.error('Subscribe error:', error);
                showMsg('error', t('subscribe_network_error', 'Ошибка соединения. Попробуйте позже.'));
            } finally {
                submitBtn.disabled = false;
                if (btnTextEl && originalText !== null) {
                    btnTextEl.textContent = originalText;
                }
                window[flag] = false;
            }
        });

        function showMsg(type, text) {
            messageEl.textContent = text;
            messageEl.className = config.messageClass + ' ' + type;

            setTimeout(function() {
                messageEl.className = config.messageClass;
            }, 5000);
        }
    }

    // ============================================================
    // Инициализация форм подписки
    // ============================================================

    // 1) blog_detail — под голосованием
    initSubscribeFormById({
        formId: 'subscribeForm',
        messageId: 'subscribeMessage',
        btnSelector: '.subscribe-btn',
        messageClass: 'subscribe-message'
    });

    // 2) blog_list — сайдбар, под популярными статьями
    initSubscribeFormById({
        formId: 'sidebarSubscribeForm',
        messageId: 'sidebarSubscribeMessage',
        btnSelector: '.sidebar-subscribe-btn',
        messageClass: 'sidebar-subscribe-message'
    });

    console.log('🗳️ Blog.js initialized (votes + subscribe forms + i18n)');
})();