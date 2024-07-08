from django.urls import path
from . import views

app_name = 'movimientos'
urlpatterns = [

    path('',views.index, name="index"),
    path('inicio/',views.panel_inicio, name="panel_inicio"),
    path('movimientos/',views.panel_movimientos, name="panel_movimientos"),
    path('registrar/',views.registro, name="registrar"),
    path('reportes/<int:id>/',views.panel_reportes, name="panel_reportes"),
    path('editar/<int:id>/', views.editar_movimiento, name='editar_movimiento'),
    path('eliminar/<int:id>/', views.eliminar_movimiento, name='eliminar_movimiento'),
    path('descargar/<int:id>/', views.descargar_movimiento, name='descargar_movimiento'),
    path('parte_operadores/',views.parte_operadores, name="panel_operadores"),
    path('reporte_operadores/',views.panel_reportes_operadores, name="panel_reporte_operadores"),
    path('puesto_operadores_eliminar/<int:id>/', views.puesto_operadores_eliminar, name='puesto_operadores_eliminar'),
    path('puesto_operadores_editar/<int:id>/',views.puesto_operadores_editar, name="puesto_operadores_editar"),
]
