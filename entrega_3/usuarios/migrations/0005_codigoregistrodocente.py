from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_remove_registrodocentependiente_telefono'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodigoRegistroDocente',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('clave', models.CharField(default='docente', max_length=50, unique=True)),
                ('codigo_hash', models.CharField(max_length=128)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
