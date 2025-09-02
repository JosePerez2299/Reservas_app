from django import template

register = template.Library()

@register.inclusion_tag('includes/field_messages.html')
def field_messages(field):
    """Renderiza help_text y errores para un campo del formulario"""
    return {
        'field': field,
        'help_text': field.help_text if hasattr(field, 'help_text') else None,
        'errors': field.errors if hasattr(field, 'errors') else None,
    }

@register.simple_tag
def render_field_complete(field, css_class=""):
    """Renderiza un campo completo con help_text y errores"""
    html = f'<div class="form-field {css_class}">'
    
    # El campo en sí
    html += str(field)
    
    # Help text
    if hasattr(field, 'help_text') and field.help_text:
        html += f'''
        <p class="text-xs text-base-content/60">
            <i class="fas fa-info-circle text-base-content/40"></i>
            {field.help_text}
        </p>
        '''
    
    # Errores
    if hasattr(field, 'errors') and field.errors:
        html += f'''
        <p class="text-xs text-error flex items-center gap-2">
            <i class="fas fa-exclamation-circle text-error"></i>
            {field.errors}
        </p>
        '''
    
    html += '</div>'
    return html