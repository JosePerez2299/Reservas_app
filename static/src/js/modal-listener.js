const modal = document.getElementById('generic_modal');
const modalContent = document.getElementById('generic_modal_content');

/**
 * FUNCIONES GLOBALES PARA MANEJAR LA MODAL
 * 
 * Disponibles globalmente:
 * - openModal(url): Abre la modal y carga contenido
 * - closeModal(): Cierra la modal inmediatamente
 * - closeModalWithConfirmation(message): Cierra con confirmación
 * 
 * Uso en templates:
 * <button onclick="closeModal()">Cerrar</button>
 * <button onclick="closeModalWithConfirmation('¿Descartar cambios?')">Cancelar</button>
 */

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

// Función global para cerrar la modal
window.closeModal = function() {
  if (modal) {
    modal.close();
  }
};

// Función global para cerrar la modal con mensaje de confirmación
window.closeModalWithConfirmation = function(message = '¿Estás seguro de que deseas cancelar?') {
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
  
  // Asegurar que el botón de cerrar esté siempre visible
  const closeButton = modal.querySelector('form[method="dialog"] button');
  if (closeButton) {
    // Agregar estilos inline para asegurar visibilidad
    closeButton.style.position = 'fixed';
    closeButton.style.top = '8px';
    closeButton.style.right = '8px';
    closeButton.style.zIndex = '9999';
    closeButton.style.pointerEvents = 'auto';
    
    // Event listener adicional por si el form method="dialog" no funciona
    closeButton.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      modal.close();
    });
  }
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

// Función para reinicializar otros componentes comunes
function initializeModalComponents() {
  const modalContent = document.getElementById('generic_modal_content');
  if (!modalContent) return;
  
  // Reinicializar tooltips de Tailwind si los hay
  const tooltips = modalContent.querySelectorAll('[data-tip]');
  tooltips.forEach(tooltip => {
    // Re-trigger tooltip initialization if needed
  });
  
  // Reinicializar inputs con máscaras si los hay
  const maskedInputs = modalContent.querySelectorAll('[data-mask]');
  maskedInputs.forEach(input => {
    // Re-apply input masks if needed
  });
  
  // Reinicializar datepickers si los hay
  const dateInputs = modalContent.querySelectorAll('input[type="date"]');
  dateInputs.forEach(input => {
    // Re-initialize date pickers if needed
  });
  
  console.log('Componentes adicionales inicializados en modal');
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
    // Scrollear al principio del modal
    const modalBox = document.querySelector('.modal-box');
    if (modalBox) {
      console.log('Scrolleando al principio del modal');
      modalBox.scrollTop = 0;
    }
    
    setTimeout(function() {
      // Reinicializar componentes comunes
      initializeSelect2();
      initializeModalComponents();
      
      // Reinicializar Alpine.js si hay componentes
      if (window.Alpine) {
        Alpine.initTree(event.detail.target);
      }
      
      // Disparar evento personalizado para que otros scripts se enganchen
      window.dispatchEvent(new CustomEvent('modalContentLoaded', {
        detail: { target: event.detail.target }
      }));
      
      console.log('Contenido modal cargado y componentes inicializados');
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

