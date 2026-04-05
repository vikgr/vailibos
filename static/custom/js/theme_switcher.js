/* Theme Switcher Script for SOPDS */

(function() {
    const theme = localStorage.getItem('sopds-theme') || 'premium';
    document.documentElement.setAttribute('data-theme', theme);
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
        
        // Initialize UI
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'premium';
        updateUI(currentTheme);
        
        // Click Listeners
        options.forEach(opt => {
            opt.addEventListener('click', (e) => {
                e.preventDefault();
                const targetTheme = opt.getAttribute('data-val');
                document.documentElement.setAttribute('data-theme', targetTheme);
                localStorage.setItem('sopds-theme', targetTheme);
                updateUI(targetTheme);
                console.log("Theme switched to", targetTheme);
            });
        });
    }
});
