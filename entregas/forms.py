from django import forms
from django.utils import timezone

from cursos.models import Curso
from usuarios.models import Perfil

from .models import Actividad, Entrega, VersionEntrega


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['titulo', 'descripcion', 'curso', 'fecha_limite']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'fecha_limite': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['curso'].queryset = Curso.objects.filter(docente=user)

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo'].strip()
        if not titulo:
            raise forms.ValidationError('El título es obligatorio.')
        if any(ord(char) < 32 for char in titulo):
            raise forms.ValidationError('El título contiene caracteres inválidos.')
        return titulo

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '')
        if any(ord(char) < 9 for char in descripcion):
            raise forms.ValidationError('La descripción contiene caracteres inválidos.')
        return descripcion.strip()

    def clean_fecha_limite(self):
        fecha = self.cleaned_data['fecha_limite']
        if fecha <= timezone.now():
            raise forms.ValidationError('La fecha límite debe ser futura.')
        return fecha


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['actividad', 'archivo', 'repositorio_github', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'repositorio_github': forms.URLInput(attrs={
                'placeholder': 'https://github.com/usuario/repositorio',
            }),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            perfil = Perfil.objects.filter(usuario=user, rol='ESTUDIANTE').first()
            if perfil:
                cursos_asignados = Curso.objects.filter(grupos__estudiantes=perfil).distinct()
                self.fields['actividad'].queryset = Actividad.objects.filter(
                    curso__in=cursos_asignados,
                    activo=True,
                ).order_by('curso__nombre', 'titulo')
            else:
                self.fields['actividad'].queryset = Actividad.objects.none()

    def clean_repositorio_github(self):
        value = self.cleaned_data.get('repositorio_github', '').strip()
        if not value:
            raise forms.ValidationError('El repositorio GitHub es obligatorio.')
        return value

    def clean_observaciones(self):
        value = self.cleaned_data.get('observaciones', '')
        if any(ord(char) < 9 for char in value):
            raise forms.ValidationError('Las observaciones contienen caracteres inválidos.')
        return value.strip()

    def clean(self):
        cleaned = super().clean()
        actividad = cleaned.get('actividad')
        if actividad and self.user:
            perfil = Perfil.objects.filter(usuario=self.user, rol='ESTUDIANTE').first()
            if perfil and Entrega.objects.filter(
                actividad=actividad, estudiante=perfil
            ).exists():
                self.add_error('actividad', 'Ya existe una entrega para esta actividad.')
        return cleaned


class VersionEntregaForm(forms.ModelForm):
    class Meta:
        model = VersionEntrega
        fields = ['archivo', 'repositorio_github', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 3}),
            'repositorio_github': forms.URLInput(attrs={
                'placeholder': 'https://github.com/usuario/repositorio',
            }),
        }

    def clean_repositorio_github(self):
        value = self.cleaned_data.get('repositorio_github', '').strip()
        if not value:
            raise forms.ValidationError('El repositorio GitHub es obligatorio.')
        return value

    def clean_comentario(self):
        value = self.cleaned_data.get('comentario', '')
        if any(ord(char) < 9 for char in value):
            raise forms.ValidationError('El comentario contiene caracteres inválidos.')
        return value.strip()
