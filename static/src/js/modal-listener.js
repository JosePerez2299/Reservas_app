const modal = document.getElementById('generic_modal');
const modalContent = document.getElementById('generic_modal_content');
if (modal) {
  modal.addEventListener('close', event => {
    modalContent.innerHTML = 'Cargando...';
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
        customClass: {
          popup: isDark ? 'bg-gray-900 text-white' : 'bg-white text-black',
          confirmButton: isDark ? 'bg-blue-600 text-white' : 'bg-blue-500 text-white',
        },
        buttonsStyling: false
      }).then((result) => {
        if (result.isConfirmed) {
          window.location.reload();
        }
      })
    });

htmx.on('htmx:afterSwap', function(event) {
      if (event.detail.target.id === 'generic_modal_content') {
        $('#generic_modal_content .select2').select2({
            placeholder: 'Buscar',
            language: {
                noResults: function(){
                  return "No se encontraron resultados";
                },
            },
            dropdownParent: $('#generic_modal')
        });
      }
    });