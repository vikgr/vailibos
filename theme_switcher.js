/* Theme Switcher Script for SOPDS */

(function() {
    const theme = localStorage.getItem('sopds-theme') || 'eink';
    document.documentElement.setAttribute('data-theme', theme);
})();

document.addEventListener('DOMContentLoaded', () => {
    const topBar = document.querySelector('.top-bar-right');
    if (topBar) {
        const toggle = document.createElement('li');
        toggle.innerHTML = `
            <a href="#" id="theme-toggle" class="button hollow small">
                <i class="fi-lightbulb"></i> <span id="theme-text">Switch Mode</span>
            </a>
        `;
        const menu = topBar.querySelector('ul.menu');
        if (menu) {
            menu.prepend(toggle);
        }

        const btn = document.getElementById('theme-toggle');
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'eink' ? 'premium' : 'eink';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('sopds-theme', target);
            updateBtnText(target);
        });
        
        updateBtnText(localStorage.getItem('sopds-theme') || 'eink');
    }

    function updateBtnText(theme) {
        const text = document.getElementById('theme-text');
        if (text) {
            text.innerText = theme === 'eink' ? 'Premium Mode' : 'E-Ink Mode';
        }
    }
});
