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

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise forms.ValidationError('El nombre del curso es obligatorio.')
        if any(ord(char) < 32 for char in nombre):
            raise forms.ValidationError('El nombre contiene caracteres inválidos.')
        if self.user and Curso.objects.filter(
            docente=self.user, nombre__iexact=nombre
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya tienes un curso con ese nombre.')
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '')
        if any(ord(char) < 9 for char in descripcion):
            raise forms.ValidationError('La descripción contiene caracteres inválidos.')
        return descripcion.strip()


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

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise forms.ValidationError('El nombre del grupo es obligatorio.')
        if any(ord(char) < 32 for char in nombre):
            raise forms.ValidationError('El nombre contiene caracteres inválidos.')
        curso = self.cleaned_data.get('curso')
        if curso and Grupo.objects.filter(
            curso=curso, nombre__iexact=nombre
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un grupo con ese nombre en el curso.')
        return nombre

    def clean_estudiantes(self):
        estudiantes = self.cleaned_data.get('estudiantes')
        invalidos = estudiantes.exclude(rol='ESTUDIANTE')
        if invalidos.exists():
            raise forms.ValidationError('Solo se pueden asignar perfiles de estudiante.')
        return estudiantes
