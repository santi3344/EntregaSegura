from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_registrodocentependiente_telefono'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrodocentependiente',
            name='telefono',
        ),
    ]
