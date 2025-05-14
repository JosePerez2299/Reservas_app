from django import template
register = template.Library()

@register.simple_tag
def get_model_fields(model, exclude=None):
    opts = model._meta
    exclude = exclude or []
    fields = []
    for f in opts.get_fields():
        # sólo campos de base de datos simples
        if not (f.many_to_one or f.one_to_many or f.many_to_many):
            if f.name in exclude:
                continue
            fields.append({'name': f.name, 'verbose': f.verbose_name.title()})
    return fields