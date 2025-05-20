# core/filters.py
import django_filters
from django.db import models
from django.utils.text import capfirst
import django_filters.widgets

def create_generic_filterset(model, include_fields=None, exclude_fields=None):
    """
    Crea dinámicamente un FilterSet para un modelo dado, basado en tipos de campos.
    """
    # Filtrado automático por campos compatibles
    filter_fields = {}

    for field in model._meta.get_fields():
        if field.auto_created:
            continue
        if include_fields and field.name not in include_fields:
            continue
        if exclude_fields and field.name in exclude_fields:
            continue

        if isinstance(field, (models.CharField, models.TextField)):
            if field.choices:  # Si tiene choices definidos
                filter_fields[field.name] = django_filters.ChoiceFilter(
                    field_name=field.name,
                    choices=field.choices,
                    label=capfirst(field.verbose_name)
                )
            else:
                filter_fields[field.name] = django_filters.CharFilter(
                    field_name=field.name,
                    lookup_expr='icontains',
                    label=capfirst(field.verbose_name)
                )
        elif isinstance(field, (models.BooleanField,)):
            filter_fields[field.name] = django_filters.BooleanFilter(
                field_name=field.name,
                label=capfirst(field.verbose_name)

            )
        elif isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
            filter_fields[field.name] = django_filters.RangeFilter(
                field_name=field.name,
                label=capfirst(field.verbose_name),
                widget=django_filters.widgets.RangeWidget(
                    attrs=[ 
                        {'type': 'number', 'class': 'form-control', 'placeholder': 'Desde'},
                        {'type': 'number', 'class': 'form-control', 'placeholder': 'Hasta'},
                    ]
                )
            )
        elif isinstance(field, models.DateField):
            filter_fields[field.name] = django_filters.DateFromToRangeFilter(
                field_name=field.name,
                label=capfirst(field.verbose_name)
            )
        elif isinstance(field, models.ForeignKey):
            filter_fields[field.name] = django_filters.ModelChoiceFilter(
                field_name=field.name,
                queryset=field.related_model.objects.all(),
                label=capfirst(field.verbose_name)
            )

    # Construcción dinámica del FilterSet
    return type(
        f"{model.__name__}AutoFilterSet",
        (django_filters.FilterSet,),
        {
            'Meta': type('Meta', (), {
                'model': model,
                'fields': list(filter_fields.keys()),
            }),
            **filter_fields
        }
    )
