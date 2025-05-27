from django import forms
from django.db.models import Q
from reservas.models import Reserva, Usuario

class ReservaCreateForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['usuario', 'fecha_uso', 'hora_inicio', 'hora_fin', 'espacio', 'motivo']
        widgets = {
            'fecha_uso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        # Si es administrador, mostrar selector de usuarios
        if self.request.user.is_admin:
            self.fields['usuario'].queryset = Usuario.objects.filter(Q(groups__name='usuario') | Q(groups__name='moderador'))
        
        # Si es moderador, mostrar selector de usuarios
        elif self.request.user.is_moderador:
            self.fields['usuario'].queryset = Usuario.objects.filter(groups__name='usuario')
        
        # Si es usuario, mostrar selector de su usuario
        elif self.request.user.is_usuario:
            self.fields['usuario'].queryset = Usuario.objects.filter(pk=self.request.user.pk)
            self.fields['usuario'].initial = self.request.user
            self.fields['usuario'].disabled = True
            self.fields['usuario'].help_text = "No puedes cambiar este campo"
            

class ReservaUpdateForm(ReservaCreateForm):
    estado = forms.ChoiceField(choices=Reserva.ESTADO_CHOICES)

    class Meta(ReservaCreateForm.Meta):
        fields = ReservaCreateForm.Meta.fields + ['estado']
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['usuario'].disabled = True
        self.fields['espacio'].disabled = True
        # NO añadimos ni mostramos aprobado_por aquí

    def save(self, commit=True):
        # Primero, instancia sin guardar aún
        instance = super().save(commit=False)
        # Asignamos el usuario que aprueba automáticamente
        instance.aprobado_por = self.request.user
        # Ahora sí guardamos
        if commit:
            instance.save()
        return instance
