document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth'
    });
    calendar.setOption('locale', 'es');
    calendar.render();

    events: [
        { title: 'Evento 1', start: '2025-06-18' },
        { title: 'Evento 2', start: '2025-06-20', end: '2025-06-22' },
      ]

    calendar.addEventSource({
        url: '/calendario/events',
        method: 'GET',
        failure: function() {
            alert('Error al cargar los eventos');
        }
    });
  });

  // 