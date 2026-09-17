// static/js/particles.js

(function() {
    'use strict';

    class ParticlesBackground {
        constructor(options = {}) {
            this.container = options.container || document.body;
            this.count = options.count || 20;
            this.size = options.size || 3;
            this.speed = options.speed || 0.3;
            this.opacity = options.opacity || 0.5;
            this.linkDistance = options.linkDistance || 250;
            this.linkWidth = options.linkWidth || 1.5;

            this.darkColor = options.darkColor || 'rgba(200, 154, 91, 0.5)';
            this.lightColor = options.lightColor || 'rgba(184, 115, 79, 0.9)';
            this.darkLinkColor = options.darkLinkColor || 'rgba(200, 154, 91, 0.12)';
            this.lightLinkColor = options.lightLinkColor || 'rgba(184, 115, 79, 0.30)';

            this.canvas = null;
            this.ctx = null;
            this.width = 0;
            this.height = 0;
            this.particles = [];
            this.animationId = null;
            this.isRunning = false;

            this.resize = this.resize.bind(this);
            this.animate = this.animate.bind(this);

            // ✅ Проверяем мобилку ДО init
            this.isMobile = this.checkMobile();

            if (this.isMobile) {
                console.log('📱 Mobile device detected — Particles disabled');
                return;
            }

            this.init();
        }

        checkMobile() {
            const width = window.innerWidth;
            const userAgent = navigator.userAgent || navigator.vendor || window.opera;
            if (width < 768) return true;
            if (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase())) {
                return true;
            }
            return false;
        }

        getTheme() {
            return document.documentElement.getAttribute('data-theme') || 'light';
        }

        getColors() {
            const theme = this.getTheme();
            return {
                particle: theme === 'dark' ? this.darkColor : this.lightColor,
                link: theme === 'dark' ? this.darkLinkColor : this.lightLinkColor,
            };
        }

        // ============================================================
        // INIT
        // ============================================================

        init() {
            // 1. Создаём canvas
            this.canvas = document.createElement('canvas');
            this.canvas.className = 'particles-canvas';
            document.body.appendChild(this.canvas);

            // 2. ✅ Получаем ctx ДО resize
            this.ctx = this.canvas.getContext('2d');
            if (!this.ctx) {
                console.error('❌ Cannot get 2D context for particles canvas');
                return;
            }
            this.ctx.imageSmoothingEnabled = true;

            // 3. Ресайз (теперь ctx уже есть)
            this.resize();
            this.createParticles();

            // 4. Слушатели
            window.addEventListener('resize', this.resize);
            this.observeThemeChanges();

            // 5. Старт
            this.start();

            console.log('✨ Particles initialized');
        }

        // ============================================================
        // RESIZE
        // ============================================================

        resize() {
            if (!this.canvas || !this.ctx) return;

            const wasMobile = this.isMobile;
            this.isMobile = this.checkMobile();

            if (this.isMobile) {
                if (this.isRunning) {
                    this.stop();
                    if (this.canvas) {
                        this.canvas.style.display = 'none';
                    }
                }
                return;
            }

            if (wasMobile && !this.isMobile) {
                if (this.canvas) {
                    this.canvas.style.display = 'block';
                    this.resizeCanvas();
                    this.createParticles();
                    this.start();
                }
                return;
            }

            if (!this.isMobile) {
                this.resizeCanvas();
            }
        }

        resizeCanvas() {
            if (!this.canvas || !this.ctx) {
                console.warn('⚠️ resizeCanvas: canvas or ctx not ready');
                return;
            }

            this.width = window.innerWidth;
            this.height = window.innerHeight;

            const dpr = window.devicePixelRatio || 1;
            this.canvas.width = this.width * dpr;
            this.canvas.height = this.height * dpr;
            this.canvas.style.width = this.width + 'px';
            this.canvas.style.height = this.height + 'px';

            // ✅ Сброс трансформации перед scale, чтобы избежать накопления
            this.ctx.setTransform(1, 0, 0, 1, 0, 0);
            this.ctx.scale(dpr, dpr);

            if (this.particles.length > 0) {
                this.particles.forEach(p => {
                    p.x = Math.random() * this.width;
                    p.y = Math.random() * this.height;
                });
            }
        }

        // ============================================================
        // PARTICLES
        // ============================================================

        createParticles() {
            this.particles = [];
            for (let i = 0; i < this.count; i++) {
                this.particles.push({
                    x: Math.random() * this.width,
                    y: Math.random() * this.height,
                    vx: (Math.random() - 0.5) * this.speed * 1.5,
                    vy: (Math.random() - 0.5) * this.speed * 1.5,
                    size: this.size * (0.5 + Math.random() * 0.8),
                    opacity: 0.4 + Math.random() * 0.6,
                });
            }
        }

        drawParticle(p) {
            if (!this.ctx) return;

            const colors = this.getColors();

            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fillStyle = colors.particle;
            this.ctx.globalAlpha = p.opacity * 0.7;
            this.ctx.fill();
            this.ctx.globalAlpha = 1;
        }

        drawLinks() {
            if (!this.ctx) return;

            const colors = this.getColors();
            const maxDist = this.linkDistance;

            for (let i = 0; i < this.particles.length; i++) {
                for (let j = i + 1; j < this.particles.length; j++) {
                    const dx = this.particles[i].x - this.particles[j].x;
                    const dy = this.particles[i].y - this.particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < maxDist) {
                        const alpha = 1 - (dist / maxDist);
                        this.ctx.beginPath();
                        this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                        this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                        this.ctx.strokeStyle = colors.link;
                        this.ctx.globalAlpha = alpha * 0.5;
                        this.ctx.lineWidth = this.linkWidth;
                        this.ctx.stroke();
                        this.ctx.globalAlpha = 1;
                    }
                }
            }
        }

        updateParticles() {
            for (let p of this.particles) {
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0 || p.x > this.width) p.vx *= -1;
                if (p.y < 0 || p.y > this.height) p.vy *= -1;

                p.x = Math.max(0, Math.min(this.width, p.x));
                p.y = Math.max(0, Math.min(this.height, p.y));
            }
        }

        // ============================================================
        // ANIMATION LOOP
        // ============================================================

        animate() {
            if (!this.isRunning || !this.ctx) return;

            this.ctx.clearRect(0, 0, this.width, this.height);

            this.updateParticles();
            this.drawLinks();

            for (let p of this.particles) {
                this.drawParticle(p);
            }

            this.animationId = requestAnimationFrame(this.animate);
        }

        start() {
            if (this.isRunning || this.isMobile || !this.ctx) return;
            this.isRunning = true;
            this.animate();
        }

        stop() {
            this.isRunning = false;
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
                this.animationId = null;
            }
        }

        destroy() {
            this.stop();
            window.removeEventListener('resize', this.resize);
            if (this.themeObserver) {
                this.themeObserver.disconnect();
            }
            if (this.canvas && this.canvas.parentNode) {
                this.canvas.parentNode.removeChild(this.canvas);
            }
        }

        // ============================================================
        // THEME OBSERVER
        // ============================================================

        observeThemeChanges() {
            const observer = new MutationObserver(() => {
                // Перерисовка произойдёт при следующем кадре — цвета обновятся
            });
            observer.observe(document.documentElement, {
                attributes: true,
                attributeFilter: ['data-theme']
            });
            this.themeObserver = observer;
        }
    }

    // ============================================================
    // SINGLETON
    // ============================================================

    let particles = null;

    function initParticles(options = {}) {
        if (particles) {
            particles.destroy();
            particles = null;
        }

        const isMobile = window.innerWidth < 768 ||
            /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(
                (navigator.userAgent || navigator.vendor || window.opera || '').toLowerCase()
            );

        if (isMobile) {
            console.log('📱 Mobile — Particles disabled');
            return null;
        }

        particles = new ParticlesBackground({
            count: options.count || 20,
            size: options.size || 3,
            speed: options.speed || 0.3,
            opacity: options.opacity || 0.5,
            linkDistance: options.linkDistance || 200,
            linkWidth: options.linkWidth || 1,
            container: options.container || document.body,
        });

        return particles;
    }

    function destroyParticles() {
        if (particles) {
            particles.destroy();
            particles = null;
        }
    }

    window.initParticles = initParticles;
    window.destroyParticles = destroyParticles;

    // ============================================================
    // AUTO-INIT
    // ============================================================

    document.addEventListener('DOMContentLoaded', function() {
        const isMobile = window.innerWidth < 768 ||
            /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(
                (navigator.userAgent || navigator.vendor || window.opera || '').toLowerCase()
            );

        if (isMobile) {
            console.log('📱 Mobile — Particles disabled');
            return;
        }

        // Читаем количество частиц из data-атрибута на <body>
        // Fallback: 20 (меньше нагрузка на CPU)
        const rawCount = document.body.dataset.particlesCount;
        const parsed = parseInt(rawCount, 10);
        const particleCount = Number.isFinite(parsed) && parsed > 0 ? parsed : 20;

        setTimeout(function() {
            initParticles({ count: particleCount });
        }, 300);
    });

    console.log('✨ Particles script loaded');
})();