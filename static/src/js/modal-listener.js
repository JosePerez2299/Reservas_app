const modal = document.getElementById('generic_modal');
const modalContent = document.getElementById('generic_modal_content');

// Función global para abrir la modal
window.openModal = function(url) {
  // 1. Mostrar spinner inmediatamente
  showSpinner();
  
  // 2. Abrir la modal inmediatamente
  modal.showModal();
  
  // 3. Cargar el contenido via HTMX
  htmx.ajax('GET', url, {
    target: '#generic_modal_content',
    swap: 'innerHTML'
  });
};

// Función para mostrar el spinner
function showSpinner() {
  modalContent.innerHTML = `
    <div class="flex flex-col items-center justify-center py-12 space-y-4">
      <span class="loading loading-spinner loading-lg text-primary"></span>
      <p class="text-base-content/70">Cargando...</p>
    </div>
  `;
}

// Limpiar modal cuando se cierra
if (modal) {
  modal.addEventListener('close', event => {
    showSpinner();
  });
} else {
  console.warn('No encontré #generic_modal en el DOM');
}

// Manejar mensajes de éxito
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
  });
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

// Manejar el cierre automático de la modal en submit exitoso
htmx.on('htmx:beforeSwap', function(event) {
  if (event.detail.target.id === 'generic_modal_content' && event.detail.xhr.status === 204) {
    // Cerrar la modal y prevenir el swap
    modal.close();
    event.detail.shouldSwap = false;
  }
});

// Manejar la carga del contenido
htmx.on('htmx:afterSwap', function(event) {
  if (event.detail.target.id === 'generic_modal_content') {
    setTimeout(function() {
      initializeSelect2();
    }, 50);
  }
});

// Manejar errores de carga
htmx.on('htmx:responseError', function(event) {
  if (event.detail.target.id === 'generic_modal_content') {
    modalContent.innerHTML = `
      <div class="flex flex-col items-center justify-center py-12 space-y-4">
        <div class="text-error text-6xl">⚠️</div>
        <p class="text-error font-semibold">Error al cargar el contenido</p>
        <button class="btn btn-sm btn-outline" onclick="modal.close()">Cerrar</button>
      </div>
    `;
  }
});

// Manejar cuando no hay conexión
htmx.on('htmx:sendError', function(event) {
  if (event.detail.target.id === 'generic_modal_content') {
    modalContent.innerHTML = `
      <div class="flex flex-col items-center justify-center py-12 space-y-4">
        <div class="text-warning text-6xl">🌐</div>
        <p class="text-warning font-semibold">Sin conexión a internet</p>
        <button class="btn btn-sm btn-outline" onclick="modal.close()">Cerrar</button>
      </div>
    `;
  }
});

