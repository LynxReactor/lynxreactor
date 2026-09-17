// static/js/pricing.js

document.addEventListener('DOMContentLoaded', function() {
    const currencyBtns = document.querySelectorAll('.currency-btn');
    const prices = document.querySelectorAll('.tariff-price');

    function updatePrices(currency) {
        const symbolMap = {
            'byn': 'BYN',
            'rub': '₽',
            'eur': '€',
            'usd': '$'
        };

        prices.forEach(price => {
            const value = price.dataset[currency];
            const valueEl = price.querySelector('.price-value');
            const symbolEl = price.querySelector('.price-symbol');

            if (price.querySelector('.price-custom')) {
                return;
            }

            if (value && valueEl) {
                const numValue = parseFloat(value);
                if (!isNaN(numValue) && numValue > 0) {
                    const formatted = numValue % 1 === 0 ? numValue.toFixed(0) : numValue.toFixed(2);
                    valueEl.textContent = formatted;

                    if (symbolEl) {
                        symbolEl.className = 'price-symbol';
                        symbolEl.innerHTML = '';
                        if (currency === 'byn') {
                            symbolEl.classList.add('nbrb-icon', 'nbrb-icon-byn');
                        } else {
                            symbolEl.textContent = symbolMap[currency] || '';
                        }
                    }
                }
            }
        });

        currencyBtns.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.currency === currency) {
                btn.classList.add('active');
            }
        });

        prices.forEach(price => {
            const valueEl = price.querySelector('.price-value');
            if (valueEl) {
                valueEl.style.transition = 'all 0.3s ease';
                valueEl.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    valueEl.style.transform = 'scale(1)';
                }, 300);
            }
        });
    }

    currencyBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const currency = this.dataset.currency;
            updatePrices(currency);
            localStorage.setItem('preferredCurrency', currency);
        });
    });

    const savedCurrency = localStorage.getItem('preferredCurrency');
    if (savedCurrency) {
        const btn = document.querySelector(`.currency-btn[data-currency="${savedCurrency}"]`);
        if (btn) {
            btn.click();
        }
    }
});