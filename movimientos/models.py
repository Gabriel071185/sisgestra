from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


class Ubicacion(models.Model):
    codigo_porton = models.CharField(max_length=20,unique=True)

    @classmethod
    def get_default(cls):
        ubicacion, created = cls.objects.get_or_create(codigo_porton = "Playa")
        return ubicacion.pk

    def __str__(self):
        return self.codigo_porton
    class Meta:
        verbose_name_plural = "Ubicaciones"
        
class Transporte(models.Model):
    codigo_transporte = models.CharField(max_length=20, unique=True)
    ultima_ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_DEFAULT, null=True, default=Ubicacion.get_default())
    cargado = models.BooleanField(default=False)
    
    def __str__(self):
        return self.codigo_transporte


class Movimiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    transporte = models.ForeignKey(Transporte, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion_carga = RichTextField( max_length=15000, null=True, blank=True)
    ubicacion_final = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='ubicacion_final', null=True, blank=True, default=Ubicacion.get_default())
    tiempo = models.DateTimeField(auto_now=True)

    def save(self) -> None:
        # transporte = Transporte.objects.get(pk = self.transporte.pk)
        # transporte.ultima_ubicacion = self.ubicacion_final
        # transporte.save()
        self.transporte.ultima_ubicacion = self.ubicacion_final
        self.transporte.save()

        return super().save()   

    def delete(self):
        if Movimiento.objects.filter(transporte = self.transporte).order_by('-tiempo').first().tiempo > self.tiempo:
            return super().delete()
        self.transporte.ultima_ubicacion = Ubicacion.objects.get(codigo_porton = "Playa")
        self.transporte.cargado = False
        self.transporte.save()
        return super().delete()


    

class Operador(models.Model):
    datos_operador = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Operadores"

    def __str__(self):
        return f"{self.datos_operador}"

class Puesto(models.Model):
    class RolChoices(models.TextChoices):
        Titular = "T", 'Titular'
        Extras = "E", 'Extras'
        CambioTurno = "C", 'C/T'

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,) 
    nombre_puesto = models.CharField(max_length=100, unique=True)
    operador = models.OneToOneField(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name='puesto')
    rol= models.CharField(max_length=1, choices=RolChoices.choices, default=RolChoices.Titular)
    primer_tiempo = models.OneToOneField(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name='primer_tiempo')
    segundo_tiempo = models.OneToOneField(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name='segundo_tiempo')


    
    def __str__(self):
        return f"{self.nombre_puesto}, {self.rol}, {self.operador}, {self.primer_tiempo}, {self.segundo_tiempo}"

   