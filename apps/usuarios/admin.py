from django.contrib import admin

from apps.usuarios.models import Usuario

# Register your models here.
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    fields = [
        'username',
        'email',
        'ubicacion',
        'piso',
        'is_active',
        'is_staff',
        'groups',
        'user_permissions',
    ]
    filter_horizontal = ('groups', 'user_permissions')