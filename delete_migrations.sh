#!/bin/bash
# borrar_migraciones.sh
# Este script elimina todas las migraciones de las apps dentro de "apps/"

echo "⚠️  Esto eliminará todas las migraciones. Asegúrate de tener respaldo si es necesario."

for app in apps/*; do
    if [ -d "$app/migrations" ]; then
        echo "🔹 Limpiando migraciones en $app/migrations..."
        find "$app/migrations" -type f -not -name "__init__.py" -delete
    fi
done

echo "✅ Todas las migraciones han sido eliminadas."
echo "💡 Ahora puedes generar nuevas migraciones con: python manage.py makemigrations"
