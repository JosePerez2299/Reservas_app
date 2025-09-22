from django import template
from django.db.models.manager import BaseManager
from django.db.models import ForeignKey, ManyToManyField
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def get_model_fields(model, exclude=None):
    exclude = exclude or []
    return [
        {'name': f.name, 'verbose': f.verbose_name}
        for f in model._meta.fields if f.name not in exclude
    ]

@register.filter
def get_attr(obj, attr_name):
    """
    Obtiene el atributo de un objeto y devuelve la representación 'bonita'
    """
    try:
        # Obtener el campo del modelo
        field = obj._meta.get_field(attr_name)
        
        # Para ForeignKey, usar get_FOO_display() si existe
        if isinstance(field, ForeignKey):
            display_method = f"get_{attr_name}_display"
            if hasattr(obj, display_method):
                return getattr(obj, display_method)()
            else:
                # Si no hay método display, obtener el objeto relacionado
                related_obj = getattr(obj, attr_name)
                return str(related_obj) if related_obj else "-"
        
        # Para campos con choices, usar get_FOO_display()
        if field.choices:
            display_method = f"get_{attr_name}_display"
            if hasattr(obj, display_method):
                return getattr(obj, display_method)()
        
        # Para ManyToMany
        if isinstance(field, ManyToManyField):
            attr = getattr(obj, attr_name)
            if isinstance(attr, BaseManager):
                relacionados = attr.all()
                if relacionados.exists():
                    return ", ".join(str(x) for x in relacionados)
                else:
                    return "-"
    
    except:
        # Si no es un campo del modelo, continuar con la lógica original
        pass
    
    # Lógica original para otros casos
    attr = getattr(obj, attr_name, None)
    
    if attr is None:
        return "-"
    
    # Si es un Manager (ManyToMany desde el lado inverso)
    if isinstance(attr, BaseManager):
        items = attr.all()
        if items.exists():
            return ", ".join(str(x) for x in items)
        else:
            return "-"
    
    # Si es callable (método o property)
    if callable(attr):
        try:
            result = attr()
            return result if result is not None else "-"
        except:
            return "-"
    
    # Para booleanos, mostrar Sí/No
    if isinstance(attr, bool):
        return "Sí" if attr else "No"
    
    return attr

@register.filter
def get_attr_html(obj, attr_name):
    """
    Versión HTML del get_attr para casos especiales
    """
    try:
        field = obj._meta.get_field(attr_name)
        
        # Para booleanos, mostrar iconos
        if field.__class__.__name__ == 'BooleanField':
            value = getattr(obj, attr_name)
            if value:
                return format_html('<i class="fas fa-check text-success"></i>')
            else:
                return format_html('<i class="fas fa-times text-error"></i>')
        
        # Para ForeignKey con imagen o color
        if isinstance(field, ForeignKey):
            related_obj = getattr(obj, attr_name)
            if related_obj:
                # Si el objeto relacionado tiene color
                if hasattr(related_obj, 'color'):
                    return format_html(
                        '<span class="badge" style="background-color: {}">{}</span>',
                        related_obj.color,
                        str(related_obj)
                    )
                # Si tiene imagen
                elif hasattr(related_obj, 'imagen') and related_obj.imagen:
                    return format_html(
                        '<div class="flex items-center gap-2">'
                        '<img src="{}" class="w-6 h-6 rounded" alt="{}">'
                        '<span>{}</span>'
                        '</div>',
                        related_obj.imagen.url,
                        str(related_obj),
                        str(related_obj)
                    )
            
    except:
        pass
    
    # Fallback al get_attr normal
    return get_attr(obj, attr_name)

@register.filter
def get_field_by_name(form, field_name):
    """
    Returns a form field by its name if it exists in the form.
    Usage: {{ form|get_field_by_name:field_name }}
    """
    try:
        return form[field_name]
    except (KeyError, AttributeError):
        return None

@register.simple_tag
def get_field_type(model, field_name):
    """
    Obtiene el tipo de campo para aplicar estilos específicos
    """
    try:
        field = model._meta.get_field(field_name)
        field_type = field.__class__.__name__
        
        if field_type == 'BooleanField':
            return 'boolean'
        elif field_type in ['ForeignKey', 'OneToOneField']:
            return 'foreign_key'
        elif field_type == 'ManyToManyField':
            return 'many_to_many'
        elif field.choices:
            return 'choices'
        elif field_type in ['DateField', 'DateTimeField']:
            return 'date'
        elif field_type in ['IntegerField', 'FloatField', 'DecimalField']:
            return 'number'
        else:
            return 'text'
    except:
        return 'text'