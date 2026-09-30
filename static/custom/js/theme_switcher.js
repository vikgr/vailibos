/* Theme Switcher Script for SOPDS */

function setThemeCookie(theme) {
    document.cookie = 'vailib_theme=' + theme + '; path=/; max-age=31536000; SameSite=Lax';
}

function getThemeCookie() {
    const value = `; ${document.cookie}`;
    const parts = value.split('; vailib_theme=');
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

(function() {
    const existing = getThemeCookie();
    if (existing) {
        document.documentElement.setAttribute('data-theme', existing);
        try { localStorage.setItem('sopds-theme', existing); } catch (e) {}
        return;
    }

    const ua = (navigator.userAgent || '').toLowerCase();
    const isEink = /kindle|kobo|nook|pocketbook|ereader|sonyreader|e-ink|eink|boox|tolino|bookeen|onyx|remarkable|likebook|boyue|hanvon|dasung|inkpalm|supernote|mobiscribe|cybook|bokeen|inkbook/.test(ua);
    const isMonochrome = window.matchMedia && (window.matchMedia('(monochrome)').matches || window.matchMedia('(monochrome: 1)').matches);
    const isLowColor = window.screen && window.screen.colorDepth && window.screen.colorDepth <= 8;

    let defaultTheme = 'premium';
    if (isEink || isMonochrome || isLowColor) {
        defaultTheme = 'eink';
    } else {
        const dpr = window.devicePixelRatio || 1;
        const maxDim = Math.max(window.screen.width || 0, window.screen.height || 0);
        const isColor = !window.screen.colorDepth || window.screen.colorDepth > 8;
        if (isColor && (maxDim * dpr >= 800 || maxDim >= 768 || dpr >= 1.5)) {
            defaultTheme = 'premium';
        }
    }

    document.documentElement.setAttribute('data-theme', defaultTheme);
    setThemeCookie(defaultTheme);
    try { localStorage.setItem('sopds-theme', defaultTheme); } catch (e) {}
})();

document.addEventListener('DOMContentLoaded', () => {
    // New Segmented Control UI for Theme Switching
    const themeSegment = document.querySelector('.theme-segment');
    if (themeSegment) {
        const options = themeSegment.querySelectorAll('.theme-opt');
        
        function updateUI(activeTheme) {
            options.forEach(opt => {
                if (opt.getAttribute('data-val') === activeTheme) {
                    opt.classList.add('active');
                } else {
                    opt.classList.remove('active');
                }
            });
        }
        
        // Initialize UI from cookie or attribute
        const currentTheme = getThemeCookie() || document.documentElement.getAttribute('data-theme') || 'premium';
        updateUI(currentTheme);
        
        // Click Listeners
        options.forEach(opt => {
            opt.addEventListener('click', (e) => {
                e.preventDefault();
                const targetTheme = opt.getAttribute('data-val');
                document.documentElement.setAttribute('data-theme', targetTheme);
                try { localStorage.setItem('sopds-theme', targetTheme); } catch (e) {}
                setThemeCookie(targetTheme);
                updateUI(targetTheme);
                // Reload so Django serves the correct template branch
                window.location.reload();
            });
        });
    }
});
