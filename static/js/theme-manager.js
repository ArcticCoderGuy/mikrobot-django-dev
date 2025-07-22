// MikroBot Theme Manager
class ThemeManager {
    constructor() {
        this.themes = {
            'light': { name: 'Light Mode', icon: '☀️' },
            'blue': { name: 'Blue Mode', icon: '🔵' },
            'dark': { name: 'Dark Mode', icon: '🌙' }
        };
        
        this.currentTheme = localStorage.getItem('mikrobot-theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.createThemeSelector();
        this.bindEvents();
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('mikrobot-theme', theme);
        this.updateThemeSelector();
    }

    createThemeSelector() {
        // Check if theme selector already exists
        if (document.querySelector('.theme-selector')) return;

        const selector = document.createElement('div');
        selector.className = 'theme-selector';
        selector.innerHTML = `
            <button class="theme-toggle">
                <span class="theme-icon">${this.themes[this.currentTheme].icon}</span>
                <span class="theme-name">${this.themes[this.currentTheme].name}</span>
                <i class="fas fa-chevron-down"></i>
            </button>
            <div class="theme-dropdown">
                ${Object.entries(this.themes).map(([key, theme]) => `
                    <a href="#" class="theme-option ${key === this.currentTheme ? 'active' : ''}" data-theme="${key}">
                        <span class="theme-icon">${theme.icon}</span>
                        <span class="theme-name">${theme.name}</span>
                    </a>
                `).join('')}
            </div>
        `;

        // Add to header
        const header = document.querySelector('header .flex.items-center.space-x-6, header .header-flex > div:last-child');
        if (header) {
            header.insertBefore(selector, header.firstChild);
        }
    }

    updateThemeSelector() {
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            const icon = toggle.querySelector('.theme-icon');
            const name = toggle.querySelector('.theme-name');
            if (icon) icon.textContent = this.themes[this.currentTheme].icon;
            if (name) name.textContent = this.themes[this.currentTheme].name;
        }

        // Update active state in dropdown
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.toggle('active', option.dataset.theme === this.currentTheme);
        });
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            // Theme toggle click
            if (e.target.closest('.theme-toggle')) {
                e.preventDefault();
                const dropdown = document.querySelector('.theme-dropdown');
                dropdown.classList.toggle('show');
            }
            
            // Theme option click
            if (e.target.closest('.theme-option')) {
                e.preventDefault();
                const theme = e.target.closest('.theme-option').dataset.theme;
                this.applyTheme(theme);
                document.querySelector('.theme-dropdown').classList.remove('show');
            }
            
            // Close dropdown on outside click
            if (!e.target.closest('.theme-selector')) {
                document.querySelector('.theme-dropdown')?.classList.remove('show');
            }
        });
    }

    // Public method to change theme programmatically
    setTheme(theme) {
        if (this.themes[theme]) {
            this.applyTheme(theme);
        }
    }

    // Get current theme
    getCurrentTheme() {
        return this.currentTheme;
    }
}

// Initialize theme manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.themeManager = new ThemeManager();
    
    // Add smooth scrolling for better UX
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add loading animation completion
    setTimeout(() => {
        document.body.classList.add('themes-loaded');
    }, 100);
});

// Export for global access
window.ThemeManager = ThemeManager;