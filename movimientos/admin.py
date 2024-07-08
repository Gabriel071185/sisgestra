from django.contrib import admin
from .models import Ubicacion, Transporte,  Movimiento, Puesto, Operador

# Register your models here


admin.site.register(Ubicacion)
admin.site.register(Transporte)
admin.site.register(Movimiento)
admin.site.register(Puesto)
admin.site.register(Operador)
