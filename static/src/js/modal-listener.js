/**
 * MODAL MANAGER - Sistema modular para manejo de modales
 * 
 * Características:
 * - Clase principal ModalManager para encapsular funcionalidad
 * - Sistema de plugins para componentes (Select2, Alpine, etc.)
 * - Manejo robusto de errores y estados
 * - API limpia y extensible
 */

class ModalManager {
  constructor(modalId = 'generic_modal', contentId = 'generic_modal_content') {
    this.modal = document.getElementById(modalId);
    this.modalContent = document.getElementById(contentId);
    this.plugins = new Map();
    this.isLoading = false;
    
    if (!this.modal || !this.modalContent) {
      console.warn(`Modal elements not found: ${modalId}, ${contentId}`);
      return;
    }
    
    this.init();
  }
  
  init() {
    this.setupEventListeners();
    this.registerDefaultPlugins();
    this.setupCloseButton();
  }
  
  /**
   * Registra un plugin para manejo de componentes
   */
  registerPlugin(name, plugin) {
    this.plugins.set(name, plugin);
  }
  
  /**
   * Abre la modal con contenido desde URL
   */
  async open(url) {
    if (this.isLoading) return;
    
    try {
      this.isLoading = true;
      this.showSpinner();
      this.modal.showModal();
      
      await this.loadContent(url);
    } catch (error) {
      this.showError('Error al cargar el contenido');
      console.error('Modal load error:', error);
    } finally {
      this.isLoading = false;
    }
  }
  
  /**
   * Cierra la modal
   */
  close() {
    if (this.modal) {
      this.cleanup();
      this.modal.close();
    }
  }
  
  /**
   * Cierra la modal con confirmación
   */
  closeWithConfirmation(message = '¿Estás seguro de que deseas cancelar?') {
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
        this.close();
      }
    });
  }
  
  /**
   * Carga contenido via HTMX
   */
  loadContent(url) {
    return new Promise((resolve, reject) => {
      htmx.ajax('GET', url, {
        target: `#${this.modalContent.id}`,
        swap: 'innerHTML'
      }).then(resolve).catch(reject);
    });
  }
  
  /**
   * Muestra spinner de carga
   */
  showSpinner() {
    this.modalContent.innerHTML = this.getSpinnerHTML();
  }
  
  /**
   * Muestra mensaje de error
   */
  showError(message, icon = '⚠️') {
    this.modalContent.innerHTML = this.getErrorHTML(message, icon);
  }
  
  /**
   * Limpia componentes antes de cerrar
   */
  cleanup() {
    this.plugins.forEach(plugin => {
      if (plugin.cleanup) {
        plugin.cleanup(this.modalContent);
      }
    });
    this.showSpinner();
  }
  
  /**
   * Inicializa componentes después de cargar contenido
   */
  initializeComponents() {
    // Scroll al inicio
    const modalBox = this.modal.querySelector('.modal-box');
    if (modalBox) modalBox.scrollTop = 0;
    
    // Inicializar plugins
    this.plugins.forEach(plugin => {
      if (plugin.initialize) {
        plugin.initialize(this.modalContent);
      }
    });
    
    // Disparar evento personalizado
    window.dispatchEvent(new CustomEvent('modalContentLoaded', {
      detail: { target: this.modalContent, modal: this }
    }));
    
    console.log('Componentes modal inicializados');
  }
  
  /**
   * Configura event listeners
   */
  setupEventListeners() {
    // Evento al cerrar modal
    this.modal.addEventListener('close', () => {
      this.cleanup();
    });
    
    // HTMX: antes del swap
    document.body.addEventListener('htmx:beforeSwap', (event) => {
      if (event.detail.target === this.modalContent) {
        this.cleanup();
        
        // Cerrar modal si respuesta 204
        if (event.detail.xhr.status === 204) {
          this.close();
          event.detail.shouldSwap = false;
        }
      }
    });
    
    // HTMX: después del swap
    document.body.addEventListener('htmx:afterSwap', (event) => {
      if (event.detail.target === this.modalContent) {
        setTimeout(() => this.initializeComponents(), 50);
      }
    });
    
    // HTMX: error de respuesta
    document.body.addEventListener('htmx:responseError', (event) => {
      if (event.detail.target === this.modalContent) {
        this.showError('Error al cargar el contenido');
      }
    });
    
    // HTMX: error de conexión
    document.body.addEventListener('htmx:sendError', (event) => {
      if (event.detail.target === this.modalContent) {
        this.showError('Sin conexión a internet', '🌐');
      }
    });
    
    // Mensajes de éxito
    document.body.addEventListener('showMessage', (event) => {
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
  }
  
  /**
   * Configura el botón de cerrar
   */
  setupCloseButton() {
    const closeButton = this.modal.querySelector('form[method="dialog"] button');
    if (closeButton) {
      Object.assign(closeButton.style, {
        position: 'fixed',
        top: '8px',
        right: '8px',
        zIndex: '9999',
        pointerEvents: 'auto'
      });
      
      closeButton.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.close();
      });
    }
  }
  
  /**
   * Registra plugins por defecto
   */
  registerDefaultPlugins() {
    // Plugin Select2
    this.registerPlugin('select2', {
      initialize: (container) => {
        const $container = $(container);
        $container.find('select.select2').each(function() {
          const $select = $(this);
          if ($select.data('select2')) return;
          
          const $modal = $select.closest('#generic_modal');
          const dropdownParent = $modal.length ? $modal : $(document.body);
          
          $select.select2({
            placeholder: 'Buscar',
            language: { noResults: () => "No se encontraron resultados" },
            width: '100%',
            dropdownParent: dropdownParent
          });
        });
      },
      
      cleanup: (container) => {
        const $container = $(container);
        $container.find('select.select2').each(function() {
          const $select = $(this);
          if ($select.data('select2')) {
            try {
              $select.select2('destroy');
            } catch (e) {
              console.warn('Error destroying select2:', e);
            }
          }
        });
        $container.find('.select2-container').remove();
      }
    });
    
    // Plugin Alpine.js
    this.registerPlugin('alpine', {
      initialize: (container) => {
        if (window.Alpine) {
          Alpine.initTree(container);
        }
      }
    });
    
    // Plugin para componentes generales
    this.registerPlugin('general', {
      initialize: (container) => {
        // Reinicializar tooltips
        const tooltips = container.querySelectorAll('[data-tip]');
        // ... lógica de tooltips
        
        // Reinicializar inputs con máscaras
        const maskedInputs = container.querySelectorAll('[data-mask]');
        // ... lógica de máscaras
        
        // Reinicializar datepickers
        const dateInputs = container.querySelectorAll('input[type="date"]');
        // ... lógica de datepickers
      }
    });
  }
  
  /**
   * Genera HTML del spinner
   */
  getSpinnerHTML() {
    return `
      <div class="flex flex-col items-center justify-center py-12 space-y-4">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <p class="text-base-content/70">Cargando...</p>
      </div>
    `;
  }
  
  /**
   * Genera HTML de error
   */
  getErrorHTML(message, icon = '⚠️') {
    const iconClass = icon === '🌐' ? 'text-warning' : 'text-error';
    return `
      <div class="flex flex-col items-center justify-center py-12 space-y-4">
        <div class="${iconClass} text-6xl">${icon}</div>
        <p class="${iconClass} font-semibold">${message}</p>
        <button class="btn btn-sm btn-outline" onclick="modalManager.close()">Cerrar</button>
      </div>
    `;
  }
}

/**
 * UTILIDAD PARA SELECT2 GLOBAL
 */
class Select2Helper {
  static initialize(container = document) {
    const $container = $(container);
    if ($container.length === 0) return;

    $container.find('select.select2').each(function() {
      const $select = $(this);
      if ($select.data('select2')) return;

      $select.select2({
        placeholder: 'Buscar',
        language: { noResults: () => "No se encontraron resultados" },
        width: '100%'
      });
    });
  }

  static destroy(container = document) {
    const $container = $(container);
    if ($container.length === 0) return;

    $container.find('select.select2').each(function() {
      const $select = $(this);
      if ($select.data('select2')) {
        try {
          $select.select2('destroy');
        } catch (e) {
          console.warn('Error destroying select2:', e);
        }
      }
    });

    $container.find('.select2-container').remove();

    // Limpieza global de contenedores huérfanos
    $('.select2-container').filter(function() {
      const cid = $(this).attr('id');
      if (!cid) return true;
      const hasOwner = $(`select.select2[aria-owns="${cid}"], select.select2[aria-controls="${cid}"]`).length > 0;
      return !hasOwner;
    }).remove();
  }
}

/**
 * INICIALIZACIÓN GLOBAL
 */

// Instancia global del modal manager
let modalManager;

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  modalManager = new ModalManager();
  
  // Inicializar Select2 en elementos existentes
  Select2Helper.initialize(document);
  
  console.log('Modal Manager inicializado');
});

/**
 * API GLOBAL PARA COMPATIBILIDAD
 */
window.openModal = function(url) {
  if (modalManager) {
    modalManager.open(url);
  }
};

window.closeModal = function() {
  if (modalManager) {
    modalManager.close();
  }
};

window.closeModalWithConfirmation = function(message) {
  if (modalManager) {
    modalManager.closeModalWithConfirmation(message);
  }
};

// Exponer utilidades Select2
window.initializeSelect2 = Select2Helper.initialize;
window.destroySelect2 = Select2Helper.destroy;

/**
 * EJEMPLO DE EXTENSIÓN:
 * 
 * // Agregar plugin personalizado
 * modalManager.registerPlugin('datepicker', {
 *   initialize: (container) => {
 *     $(container).find('.datepicker').datepicker();
 *   },
 *   cleanup: (container) => {
 *     $(container).find('.datepicker').datepicker('destroy');
 *   }
 * });
 */