from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_registrodocentependiente'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrodocentependiente',
            name='telefono',
            field=models.CharField(default='', max_length=16),
            preserve_default=False,
        ),
    ]
