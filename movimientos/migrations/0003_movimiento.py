# Generated by Django 4.2 on 2024-07-02 23:35

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('movimientos', '0002_transporte'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion_carga', ckeditor.fields.RichTextField(blank=True, max_length=15000, null=True)),
                ('tiempo', models.DateTimeField(auto_now=True)),
                ('transporte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='movimientos.transporte')),
                ('ubicacion_final', models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ubicacion_final', to='movimientos.ubicacion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
