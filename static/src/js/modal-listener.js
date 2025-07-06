const modal = document.getElementById('generic_modal');
const modalContent = document.getElementById('generic_modal_content');
if (modal) {
  modal.addEventListener('close', event => {
    modalContent.innerHTML = `<div class="flex flex-col items-center justify-center py-12 space-y-4">
    <span class="loading loading-spinner loading-lg text-primary"></span>
    <p class="text-base-content/70">Cargando...</p>
  </div>`;
  });
} else {
  console.warn('No encontré #generic_modal en el DOM');
}

htmx.on('showMessage', function(event) {
    Swal.fire({
        icon: 'success',
        title: '¡Listo!',
        text: event.detail.value,
        confirmButtonText: 'Aceptar',
      }).then((result) => {
        if (result.isConfirmed) {
          window.location.reload();
        }
      })
    });

// Función para limpiar e inicializar Select2
function initializeSelect2() {
  // Destruir todas las instancias existentes en el modal
  $('#generic_modal_content .select2').each(function() {
    if ($(this).hasClass('select2-hidden-accessible')) {
      $(this).select2('destroy');
    }
  });
  
  // Limpiar cualquier contenedor residual
  $('#generic_modal_content .select2-container').remove();
  
  // Inicializar Select2 solo en elementos que no estén ya inicializados
  $('#generic_modal_content .select2').not('.select2-hidden-accessible').select2({
    placeholder: 'Buscar',
    language: {
      noResults: function(){
        return "No se encontraron resultados";
      },
    },
    dropdownParent: $('#generic_modal')
  });
}

// Solo un evento para manejar tanto la carga inicial como los refreshes  
htmx.on('htmx:afterSwap', function(event) {
  if (event.detail.target.id === 'generic_modal_content') {
    // Pequeño delay para asegurar que el DOM esté completamente actualizado
    setTimeout(function() {
      initializeSelect2();
    }, 50);
  }
});