from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Perfil


class RuntimeAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='runtime_auth',
            password='RuntimePass!2026',
        )
        Perfil.objects.create(usuario=self.user, rol='ESTUDIANTE')

    def test_login_rejects_missing_credentials_and_accepts_valid_credentials(self):
        invalid = self.client.post(reverse('login'), {'usuario': '', 'password': ''})
        self.assertContains(invalid, 'obligatorios', status_code=200)

        oversized = self.client.post(reverse('login'), {
            'usuario': 'u' * 151,
            'password': 'p',
        })
        self.assertContains(oversized, '150 caracteres', status_code=200)

        valid = self.client.post(reverse('login'), {
            'usuario': 'runtime_auth',
            'password': 'RuntimePass!2026',
        })
        self.assertRedirects(valid, reverse('panel_estudiante'))
