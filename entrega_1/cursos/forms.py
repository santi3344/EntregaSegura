from django import forms

from usuarios.models import Perfil

from .models import Curso, Grupo


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ('nombre', 'descripcion')
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Matemáticas I'}),
            'descripcion': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Descripción del curso (opcional)'}
            ),
        }


class GrupoForm(forms.ModelForm):
    estudiantes = forms.ModelMultipleChoiceField(
        queryset=Perfil.objects.none(),
        required=False,
        label='Estudiantes asignados',
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Grupo
        fields = ('nombre', 'curso', 'estudiantes')
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Grupo A'}),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].queryset = Curso.objects.filter(
            docente=user
        ).order_by('nombre')
        self.fields['curso'].empty_label = 'Selecciona uno de tus cursos'
        self.fields['estudiantes'].queryset = Perfil.objects.filter(
            rol='ESTUDIANTE'
        ).select_related('usuario').order_by(
            'usuario__last_name',
            'usuario__first_name',
            'usuario__username',
        )

