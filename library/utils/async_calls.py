import threading

def async_call(fn, *args, **kwargs):
    """
    Ejecuta una función en un hilo aparte.
    No bloquea la request.
    """
    thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
