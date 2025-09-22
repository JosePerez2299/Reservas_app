// SweetAlert global
document.addEventListener('showMessage', function(event) {
    Swal.fire({
      icon: 'success',
      title: '¡Listo!',
      text: event.detail.value || '',
      confirmButtonText: 'Aceptar',
    }).then((result) => {
      if (result.isConfirmed) {
        window.location.reload();
      }
    });
  });
  