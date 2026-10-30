import hashlib
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.exceptions import ValidationError

from .models import EvidenciaValidacion


MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.zip', '.rar', '.7z'}
GITHUB_PATTERN = re.compile(
    r'^https?://(?:www\.)?github\.com/([^/]+)/([^/#?]+?)/?$',
    re.IGNORECASE,
)


def _file_bytes(uploaded_file):
    uploaded_file.seek(0)
    content = uploaded_file.read()
    uploaded_file.seek(0)
    return content


def github_repository_status(url):
    match = GITHUB_PATTERN.match((url or '').strip())
    if not match:
        return False, 'La URL debe tener el formato https://github.com/usuario/repositorio.'

    owner, repository = match.groups()
    api_url = f'https://api.github.com/repos/{owner}/{repository}'
    request = Request(api_url, headers={'User-Agent': 'EntregaSegura/2.0'})
    try:
        with urlopen(request, timeout=5) as response:
            if response.status == 200:
                return True, f'Repositorio verificado: github.com/{owner}/{repository}.'
            return False, f'GitHub respondió con estado HTTP {response.status}.'
    except HTTPError as error:
        if error.code == 404:
            return False, 'El repositorio no existe o no es público.'
        return False, f'GitHub rechazó la consulta (HTTP {error.code}).'
    except URLError:
        return False, 'No fue posible conectarse con GitHub.'


def validate_submission(uploaded_file, github_url, activity, profile):
    content = _file_bytes(uploaded_file)
    extension = '.' + uploaded_file.name.rsplit('.', 1)[-1].lower() if '.' in uploaded_file.name else ''
    file_ok = extension in ALLOWED_EXTENSIONS and uploaded_file.size <= MAX_FILE_SIZE
    if extension not in ALLOWED_EXTENSIONS:
        file_message = 'Extensión no permitida. Usa PDF, DOC/DOCX, ZIP, RAR o 7Z.'
    elif uploaded_file.size > MAX_FILE_SIZE:
        file_message = 'El archivo supera el límite de 10 MB.'
    else:
        file_message = f'Archivo aceptado ({extension}, {uploaded_file.size} bytes).'

    integrity_ok = bool(content)
    digest = hashlib.sha256(content).hexdigest() if integrity_ok else ''
    integrity_message = (
        f'Archivo no vacío. SHA-256: {digest}'
        if integrity_ok else 'El archivo está vacío.'
    )

    metadata_ok = bool(activity and profile and github_url and GITHUB_PATTERN.match(github_url.strip()))
    metadata_message = (
        'Actividad, estudiante y URL de repositorio asociados correctamente.'
        if metadata_ok else 'Faltan datos de actividad, estudiante o una URL GitHub válida.'
    )
    github_ok, github_message = github_repository_status(github_url)

    return {
        'ARCHIVO': (file_ok, file_message),
        'INTEGRIDAD': (integrity_ok, integrity_message),
        'METADATOS': (metadata_ok, metadata_message),
        'GITHUB': (github_ok, github_message),
        'hash_archivo': digest,
    }


def raise_for_failed_validations(results):
    failures = [
        value[1] for key, value in results.items()
        if key != 'hash_archivo' and not value[0]
    ]
    if failures:
        raise ValidationError(failures)


def save_validation_evidence(results, *, entrega=None, version=None):
    for capa, value in results.items():
        if capa == 'hash_archivo':
            continue
        aprobado, mensaje = value
        EvidenciaValidacion.objects.create(
            entrega=entrega,
            version=version,
            capa=capa,
            aprobado=aprobado,
            mensaje=mensaje,
        )
