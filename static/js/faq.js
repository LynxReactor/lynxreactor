// static/js/faq.js

(function() {
    'use strict';

    function initFaq() {
        var faqItems = document.querySelectorAll('.faq-item');

        if (faqItems.length === 0) {
            return;
        }

        faqItems.forEach(function(item) {
            var question = item.querySelector('.faq-question');
            var answer = item.querySelector('.faq-answer');
            var content = answer ? answer.querySelector('.faq-answer-content') : null;

            if (!question) {
                return;
            }

            // Удаляем старые обработчики
            var newQuestion = question.cloneNode(true);
            question.parentNode.replaceChild(newQuestion, question);

            // Измеряем высоту контента для анимации
            var contentHeight = 0;
            if (content && answer) {
                answer.style.maxHeight = 'none';
                answer.style.overflow = 'visible';
                contentHeight = content.scrollHeight + 24;
                answer.style.maxHeight = '0';
                answer.style.overflow = 'hidden';
            }

            newQuestion.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                var parentItem = this.closest('.faq-item');
                if (!parentItem) {
                    return;
                }

                var isActive = parentItem.classList.contains('active');
                var parentAnswer = parentItem.querySelector('.faq-answer');

                // Закрываем все другие вопросы
                document.querySelectorAll('.faq-item').forEach(function(otherItem) {
                    if (otherItem !== parentItem && otherItem.classList.contains('active')) {
                        otherItem.classList.remove('active');
                        var otherAnswer = otherItem.querySelector('.faq-answer');
                        if (otherAnswer) {
                            otherAnswer.style.maxHeight = '0px';
                            otherAnswer.style.padding = '0';
                            otherAnswer.style.borderTop = 'none';
                        }
                        var otherQuestion = otherItem.querySelector('.faq-question');
                        if (otherQuestion) {
                            otherQuestion.setAttribute('aria-expanded', 'false');
                        }
                    }
                });

                // Переключаем текущий вопрос
                if (isActive) {
                    parentItem.classList.remove('active');
                    if (parentAnswer) {
                        parentAnswer.style.maxHeight = '0px';
                        parentAnswer.style.padding = '0';
                        parentAnswer.style.borderTop = 'none';
                    }
                    this.setAttribute('aria-expanded', 'false');
                } else {
                    parentItem.classList.add('active');
                    if (parentAnswer && contentHeight > 0) {
                        parentAnswer.style.maxHeight = contentHeight + 'px';
                        parentAnswer.style.padding = '0';
                        parentAnswer.style.borderTop = '1px solid rgba(200, 154, 91, 0.1)';
                    } else if (parentAnswer) {
                        parentAnswer.style.maxHeight = '300px';
                        parentAnswer.style.padding = '0';
                        parentAnswer.style.borderTop = '1px solid rgba(200, 154, 91, 0.1)';
                    }
                    this.setAttribute('aria-expanded', 'true');
                }
            });
        });
    }

    // ============================================================
    // МОДАЛЬНОЕ ОКНО ДЛЯ ВОПРОСА (FAQ)
    // ============================================================

    function initFaqModal() {
        var faqModal = document.getElementById('faqModal');
        var faqModalClose = document.getElementById('faqModalClose');
        var faqCtaBtn = document.getElementById('faqCtaBtn');

        if (!faqModal) {
            return;
        }

        function openFaqModal() {
            faqModal.classList.add('active');
            document.body.style.overflow = 'hidden';
            document.body.classList.add('modal-open');
        }

        function closeFaqModal() {
            faqModal.classList.remove('active');
            document.body.style.overflow = '';
            document.body.classList.remove('modal-open');
        }

        if (faqCtaBtn) {
            faqCtaBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                openFaqModal();
            });
        }

        if (faqModalClose) {
            faqModalClose.addEventListener('click', closeFaqModal);
        }

        faqModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeFaqModal();
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && faqModal.classList.contains('active')) {
                closeFaqModal();
            }
        });

        document.querySelectorAll('.faq-contact-item').forEach(function(item) {
            item.addEventListener('click', function() {
                if (this.getAttribute('href') !== '#' && this.getAttribute('href') !== '') {
                    setTimeout(closeFaqModal, 400);
                }
            });
        });
    }

    // Запускаем после полной загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initFaq();
            initFaqModal();
        });
    } else {
        initFaq();
        initFaqModal();
    }

    setTimeout(function() {
        var firstQuestion = document.querySelector('.faq-question');
        if (firstQuestion) {
            initFaq();
        }
    }, 500);
})();