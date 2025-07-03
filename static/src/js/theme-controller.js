  
// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const themeController = document.querySelector('.theme-controller');
    
    // Establecer el estado del checkbox según el tema actual
    if (themeController) {
        themeController.checked = document.documentElement.getAttribute('data-theme') === 'dark';
        
        // Manejar cambios futuros
        themeController.addEventListener('change', function() {
            const theme = this.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        });
    }
});

// Mobile menu functionality (puede permanecer igual)
document.addEventListener('click', function(e) {
    const dropdowns = document.querySelectorAll('.dropdown[open]');
    dropdowns.forEach(dropdown => {
        if (!dropdown.contains(e.target)) {
            dropdown.removeAttribute('open');
        }
    });
});


function themeSwitcher() {
  return {
    // usamos booleano para simplificar el binding con el checkbox
    dark: localStorage.getItem('theme') === 'dark',

    init() {
      // al iniciar, aplicamos el tema según localStorage o preferencia del sistema
      this.applyTheme(this.dark)
    },

    toggle() {
      // invocado al hacer click sobre el swap
      this.dark = !this.dark
      this.applyTheme(this.dark)
    },

    applyTheme(isDark) {
      // ponemos el atributo data-theme que DaisyUI utiliza
      document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
      // guardamos la preferencia
      localStorage.setItem('theme', isDark ? 'dark' : 'light')
    }
  }
}