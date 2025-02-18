# Generated by Django 4.2 on 2024-07-02 23:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movimientos', '0005_puesto'),
    ]

    operations = [
        migrations.AddField(
            model_name='puesto',
            name='primer_tiempo',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primer_tiempo', to='movimientos.operador'),
        ),
        migrations.AddField(
            model_name='puesto',
            name='segundo_tiempo',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='segundo_tiempo', to='movimientos.operador'),
        ),
    ]
