// static/js/animations.js

document.addEventListener('DOMContentLoaded', function() {

    // ============================================================
    // SCROLL ANIMATIONS (Intersection Observer)
    // ============================================================

    const animateElements = document.querySelectorAll('.animate-on-scroll');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    const delay = entry.target.dataset.delay || 0;
                    setTimeout(function() {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, delay);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        animateElements.forEach(function(element, index) {
            var delay = Math.min(index * 100, 600);
            element.dataset.delay = delay;
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            observer.observe(element);
        });
    } else {
        animateElements.forEach(function(element) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        });
    }

    // ============================================================
    // COUNTER ANIMATION FOR STATS
    // ============================================================

    var statValues = document.querySelectorAll('.stat-value');

    if ('IntersectionObserver' in window) {
        var counterObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var element = entry.target;
                    var text = element.textContent;
                    var match = text.match(/\d+/);

                    if (match) {
                        var target = parseInt(match[0]);
                        if (!isNaN(target) && target > 0) {
                            animateCounter(element, target);
                        }
                    }
                    counterObserver.unobserve(element);
                }
            });
        }, { threshold: 0.5 });

        statValues.forEach(function(stat) {
            counterObserver.observe(stat);
        });
    }

    function animateCounter(element, target) {
        var current = 0;
        var duration = 2000;
        var startTime = Date.now();
        var suffix = element.textContent.replace(/\d+/, '');

        function updateCounter() {
            var elapsed = Date.now() - startTime;
            var progress = Math.min(elapsed / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            current = Math.ceil(eased * target);

            if (target > 100) {
                element.textContent = current.toLocaleString() + suffix;
            } else if (target % 1 === 0) {
                element.textContent = current + suffix;
            } else {
                element.textContent = current.toFixed(1) + suffix;
            }

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target.toLocaleString() + suffix;
            }
        }

        updateCounter();
    }

    // ============================================================
    // HOVER ANIMATION FOR CARDS
    // ============================================================

    document.querySelectorAll('.service-card, .portfolio-card, .tech-item, .tariff-card').forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            var image = this.querySelector('.service-card-overlay, .portfolio-image img, .tech-icon');
            if (image) {
                image.style.transition = 'transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            }
        });

        card.addEventListener('mouseleave', function() {
            var image = this.querySelector('.service-card-overlay, .portfolio-image img, .tech-icon');
            if (image) {
                image.style.transition = 'transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            }
        });
    });

    // ============================================================
    // PARALLAX EFFECT FOR HERO
    // ============================================================

    var heroBackground = document.querySelector('.hero-background');
    if (heroBackground) {
        window.addEventListener('scroll', function() {
            var scrolled = window.pageYOffset;
            heroBackground.style.transform = 'translateY(' + (scrolled * 0.4) + 'px)';
            heroBackground.style.opacity = 1 - (scrolled / 1000);
        }, { passive: true });
    }

    // ============================================================
    // LAZY LOAD IMAGES
    // ============================================================

    if ('IntersectionObserver' in window) {
        var lazyImages = document.querySelectorAll('img[loading="lazy"]');
        var imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    var src = img.dataset.src;
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // ============================================================
    // SCROLL INDICATOR
    // ============================================================

    var scrollIndicator = document.querySelector('.hero-scroll-indicator');
    if (scrollIndicator) {
        window.addEventListener('scroll', function() {
            var scrolled = window.pageYOffset;
            if (scrolled > 100) {
                scrollIndicator.style.opacity = '0';
                scrollIndicator.style.transition = 'opacity 0.5s ease';
            } else {
                scrollIndicator.style.opacity = '0.9';
            }
        }, { passive: true });
    }
});