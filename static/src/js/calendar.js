function reservasCalendar(config = {}) {
    return {
        // Configuración
        reservasJsonUrl: config.reservasJsonUrl || '/api/reservas/',
        reservasByDateUrl: config.reservasByDateUrl || '/api/reservas/fecha/',
        editUrlTemplate: config.editUrlTemplate || '/reservas/edit/RESERVATION_ID/',
        calendarId: config.calendarId || 'main',

        // Estado
        filterStatus: 'all',
        selectedDate: null,
        calendar: null,

        // Inicialización
        init() {
            this.$nextTick(() => {
                this.initCalendar();
            });

            // Escuchar eventos de fecha seleccionada
            window.addEventListener('fecha-seleccionada', (event) => {
                this.selectedDate = event.detail;
                this.loadReservasWithHTMX(this.selectedDate);
            });
        },

        // Métodos
        initCalendar() {
            const calendarEl = document.getElementById(`calendar-${this.calendarId}`);
            if (!calendarEl) {
                console.error(`Calendar element with id 'calendar-${this.calendarId}' not found`);
                return;
            }

            this.calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                locale: 'es',
                firstDay: 1,
                validRange: {
                    start: new Date()
                },
                headerToolbar: {
                    left: '',
                    center: 'title',
                    right: ''
                },
                buttonText: {
                    today: 'Hoy',
                    month: 'Mes',
                    week: 'Semana',
                    day: 'Día'
                },
                events: this.fetchEvents.bind(this),
                dateClick: this.handleDateClick.bind(this),
                eventClick: this.handleEventClick.bind(this),
                height: 'auto',
                aspectRatio: 1.6,
                dayMaxEvents: 3,
                moreLinkClick: 'popover'
            });

            this.calendar.render();
            
            // Hacer el calendario disponible globalmente para los controles
            window.calendarInstance = this.calendar;
        },

        async fetchEvents(fetchInfo, successCallback, failureCallback) {
            try {
                const start = fetchInfo.startStr;
                const end = fetchInfo.endStr;
                const status = this.filterStatus !== 'all' ? this.filterStatus : '';
                
                const url = `${this.reservasJsonUrl}?start=${start}&end=${end}${status ? `&status=${status}` : ''}`;
                const response = await fetch(url);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                const events = this.mapEvents(data);
                successCallback(events);
            } catch (error) {
                console.error('Error fetching events:', error);
                failureCallback(error);
            }
        },

        mapEvents(events) {
            return events.map(event => {
                const pendientes = event.pendiente_count || 0;
                const aprobadas = event.aprobada_count || 0;
                const rechazadas = event.rechazada_count || 0;
                const total = pendientes + aprobadas + rechazadas;
                
                if (total === 0) return null;
                
                // Crear múltiples eventos si hay diferentes tipos de reservas
                const eventosDelDia = [];
                
                if (aprobadas > 0) {
                    eventosDelDia.push({
                        title: `${aprobadas} Aprobada${aprobadas > 1 ? 's' : ''}`,
                        start: event.fecha_uso,
                        allDay: true,
                        backgroundColor: '#22c55e',
                        borderColor: '#22c55e',
                        textColor: 'white',
                        extendedProps: { 
                            estado: 'aprobada',
                            count: aprobadas
                        }
                    });
                }
                
                if (pendientes > 0) {
                    eventosDelDia.push({
                        title: `${pendientes} Pendiente${pendientes > 1 ? 's' : ''}`,
                        start: event.fecha_uso,
                        allDay: true,
                        backgroundColor: '#f59e0b',
                        borderColor: '#f59e0b',
                        textColor: 'white',
                        extendedProps: { 
                            estado: 'pendiente',
                            count: pendientes
                        }
                    });
                }
                
                if (rechazadas > 0) {
                    eventosDelDia.push({
                        title: `${rechazadas} Rechazada${rechazadas > 1 ? 's' : ''}`,
                        start: event.fecha_uso,
                        allDay: true,
                        backgroundColor: '#ef4444',
                        borderColor: '#ef4444',
                        textColor: 'white',
                        extendedProps: { 
                            estado: 'rechazada',
                            count: rechazadas
                        }
                    });
                }
                
                return eventosDelDia;
            }).filter(event => event !== null).flat();
        },

        handleDateClick(info) {
            const fecha = info.dateStr;
            this.handleFechaSeleccionada(fecha);
        },

        handleEventClick(info) {
            info.jsEvent.preventDefault();
            const start = info.event.start;
            const dateStr = start.toISOString().slice(0, 10);
            this.handleFechaSeleccionada(dateStr);
        },

        handleFechaSeleccionada(fecha) {
            this.selectedDate = fecha.trim();
            this.highlightSelectedDate(fecha.trim());
            
            window.dispatchEvent(new CustomEvent('fecha-seleccionada', {
                detail: fecha.trim()
            }));
        },

        highlightSelectedDate(fecha) {
            // Remover highlight anterior
            const previousSelected = document.querySelector('.fc-daygrid-day.selected-date');
            if (previousSelected) {
                previousSelected.classList.remove('selected-date');
            }
            
            // Agregar highlight a la fecha seleccionada
            const selectedCell = document.querySelector(`[data-date="${fecha}"]`);
            if (selectedCell) {
                selectedCell.classList.add('selected-date');
            }
        },

        loadReservasWithHTMX(fecha) {
            if (!fecha) return;
            
            // Disparar evento HTMX personalizado para cargar reservas
            const estado = this.filterStatus === 'all' ? '' : this.filterStatus;
            
            // Usar htmx.ajax para hacer la petición con los valores correctos
            htmx.ajax('GET', this.reservasByDateUrl, {
                target: '#reservas-list',
                swap: 'innerHTML',
                values: { 
                    'fecha_uso': fecha,
                    'estado': estado 
                }
            });
        },

        // También actualizar setFilter para que funcione con la paginación
        setFilter(status) {
            this.filterStatus = status;
            if (this.calendar) {
                this.calendar.refetchEvents();
            }
            // Si hay una fecha seleccionada, recargar las reservas con el nuevo filtro
            if (this.selectedDate) {
                this.loadReservasWithHTMX(this.selectedDate);
            }
        },

        // Método para obtener el ID del calendario dinámicamente
        getCalendarId() {
            return this.calendarId || 'main';
        },

        formatSelectedDate() {
            if (!this.selectedDate) return '';
            const date = new Date(this.selectedDate + 'T00:00:00');
            return date.toLocaleDateString('es-ES', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    }
}