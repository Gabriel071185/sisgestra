# Generated by Django 4.2 on 2024-07-10 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movimientos', '0013_alter_puesto_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transporte',
            name='cargado',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='transporte',
            name='ultima_ubicacion',
            field=models.ForeignKey(default='playa!', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='movimientos.ubicacion'),
        ),
    ]
