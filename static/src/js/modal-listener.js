const theme = localStorage.getItem('theme');
const modal = document.getElementById('generic_modal');
const modalContent = document.getElementById('generic_modal_content');
if (modal) {
  modal.addEventListener('close', event => {
    modalContent.innerHTML = 'Cargando...';
    console.log('Modal cerrada (desde external .js)', event);
  });
} else {
  console.warn('No encontré #generic_modal en el DOM');
}
const isDark = document.documentElement.classList.contains('dark') ||
               document.documentElement.dataset.theme === 'dark';




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
