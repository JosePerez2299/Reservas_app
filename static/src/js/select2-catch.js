/**
 * Inicializa todos los selects con clase 'select2'
 * @param {HTMLElement} container Opcional. Contenedor donde buscar. Por defecto, todo el documento.
 */
function initializeSelect2(container = document) {
  $(container).find('select.select2').each(function() {
    // Destruir instancia previa si existiera
    if ($(this).hasClass('select2-hidden-accessible')) {
      $(this).select2('destroy');
    }
  });

  // Inicializar
  $(container).find('select.select2').not('.select2-hidden-accessible').select2({
    placeholder: 'Buscar',
    language: {
      noResults: function() {
        return "No se encontraron resultados";
      },
    },
    // Si el select está dentro de un modal, ajustar dropdownParent
    dropdownParent: $(container).closest('.modal').length
      ? $(container).closest('.modal')
      : undefined
  });
}

// Hacer global para poder llamarlo desde otros scripts
window.initializeSelect2 = initializeSelect2;

// Inicializar Select2 al cargar la página principal
document.addEventListener('DOMContentLoaded', function() {
  initializeSelect2();
});
