from django import template

register = template.Library()

@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None and v != "":
            updated[k] = v
        elif k in updated:
            del updated[k]
    return updated.urlencode()
