const modal = document.getElementById('generic_modal');
const modalContent = document.getElementById('generic_modal_content');

// Abrir modal y cargar contenido vía HTMX
window.openModal = function(url) {
  showSpinner();
  modal.showModal();
  htmx.ajax('GET', url, { target: '#generic_modal_content', swap: 'innerHTML' });
};

// Cerrar modal
window.closeModal = function() { modal.close(); };

// Cerrar modal con confirmación
window.closeModalWithConfirmation = function(message = '¿Descartar cambios?') {
  Swal.fire({
    title: 'Confirmar',
    text: message,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'No, continuar',
    confirmButtonColor: '#f87171',
    cancelButtonColor: '#6b7280'
  }).then((result) => {
    if (result.isConfirmed) {
      closeModal();
    }
  });
};

// Mostrar spinner mientras carga contenido
function showSpinner() {
  if (!modalContent) return;
  modalContent.innerHTML = `
    <div class="flex flex-col items-center justify-center py-12 space-y-4">
      <span class="loading loading-spinner loading-lg text-primary"></span>
      <p class="text-base-content/70">Cargando...</p>
    </div>
  `;
}

// Limpiar modal al cerrar
if (modal) {
  modal.addEventListener('close', event => {
    showSpinner();
  });
}

// Inicializar componentes dentro de la modal
function initializeModalComponents() {
  if (!modalContent) return;

  // Inicializar Select2 en modal si existe la función global
  if (window.initializeSelect2) {
    initializeSelect2(modalContent);
  }

  // Aquí puedes inicializar tooltips, datepickers, máscaras, Alpine.js, etc.
  const dateInputs = modalContent.querySelectorAll('input[type="date"]');
  dateInputs.forEach(input => {
    // Inicialización de datepickers si es necesario
  });

  console.log('Componentes adicionales inicializados en modal');
}

// Eventos HTMX
htmx.on('htmx:afterSwap', function(event) {
  if (event.detail.target.id === 'generic_modal_content') {
    // Scrollear al inicio
    const modalBox = modalContent.querySelector('.modal-box');
    if (modalBox) modalBox.scrollTop = 0;

    // Inicializar componentes dentro de la modal
    initializeModalComponents();

    // Inicializar Alpine.js si existe
    if (window.Alpine) Alpine.initTree(event.detail.target);

    // Disparar evento custom
    window.dispatchEvent(new CustomEvent('modalContentLoaded', {
      detail: { target: event.detail.target }
    }));
  }
});

// Manejar cierre automático si status 204
htmx.on('htmx:beforeSwap', function(event) {
  if (event.detail.target.id === 'generic_modal_content' && event.detail.xhr.status === 204) {
    modal.close();
    event.detail.shouldSwap = false;
  }
});

// Manejo de errores
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
