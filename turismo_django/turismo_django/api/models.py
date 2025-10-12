from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# --- Modelos de Geografía ---
class Departamento(models.Model):
    codigo_departamento = models.CharField(max_length=10, primary_key=True)
    nombre_departamento = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_departamento

class Municipio(models.Model):
    codigo_municipio = models.CharField(max_length=10, primary_key=True)
    nombre_municipio = models.CharField(max_length=255)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='municipios')

    def __str__(self):
        return f"{self.nombre_municipio}, {self.departamento.nombre_departamento}"

# --- Modelos de Usuarios y Roles ---
class Rol(models.Model):
    nombre_rol = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_rol

class Usuario(AbstractUser):
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, blank=True, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, blank=True, null=True)
    empresa_asociada = models.ForeignKey('EmpresaPrestadorTuristico', on_delete=models.SET_NULL, blank=True, null=True, related_name='empleados')

# --- Modelos de Contenido Principal ---
class EmpresaPrestadorTuristico(models.Model):
    razon_social_o_nombre_comercial = models.CharField(max_length=255)
    nit = models.CharField(max_length=20, unique=True, blank=True, null=True)
    tipo_prestador = models.CharField(max_length=255)
    tipo_prestador_otro = models.CharField(max_length=255, blank=True, null=True)
    es_formal = models.BooleanField(default=True)
    rnt = models.CharField(max_length=50, blank=True, null=True)
    descripcion_servicios = models.TextField(blank=True, null=True)
    direccion_principal = models.CharField(max_length=255, blank=True, null=True)
    telefonos_contacto = models.CharField(max_length=100, blank=True, null=True)
    email_contacto = models.EmailField(blank=True, null=True)
    pagina_web = models.URLField(blank=True, null=True)
    aprobada_publicar = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT)
    registrada_por_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='empresas_registradas')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.razon_social_o_nombre_comercial

class VacanteEmpleo(models.Model):
    titulo_vacante = models.CharField(max_length=255)
    descripcion = models.TextField()
    requisitos = models.TextField(blank=True, null=True)
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE, blank=True, null=True)
    nombre_empleador_alternativo = models.CharField(max_length=255, blank=True, null=True)
    tipo_contrato = models.CharField(max_length=100, blank=True, null=True)
    salario_rango = models.CharField(max_length=100, blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT)
    publicada_por_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.titulo_vacante

# --- Modelos de Encuestas y Feedback ---
class TuristaRegistro(models.Model):
    fecha_encuesta = models.DateField()
    nombre_turista = models.CharField(max_length=255, blank=True, null=True)
    genero = models.CharField(max_length=50, blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    rango_edad = models.CharField(max_length=50, blank=True, null=True)
    nacionalidad = models.CharField(max_length=100, blank=True, null=True)
    pais_residencia = models.CharField(max_length=100, blank=True, null=True)
    depto_origen = models.ForeignKey(Departamento, on_delete=models.SET_NULL, blank=True, null=True)
    municipio_origen = models.ForeignKey(Municipio, on_delete=models.SET_NULL, blank=True, null=True, related_name='turistas_origen')
    motivo_viaje = models.CharField(max_length=255, blank=True, null=True)
    otro_motivo_viaje = models.CharField(max_length=255, blank=True, null=True)
    municipio_encuestado = models.ForeignKey(Municipio, on_delete=models.PROTECT, related_name='encuestas_realizadas')
    registrado_por_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

class EncuestaPercepcion(models.Model):
    turista_registro = models.OneToOneField(TuristaRegistro, on_delete=models.CASCADE, primary_key=True)
    volveria = models.IntegerField(blank=True, null=True)
    experiencia_general_positiva = models.IntegerField(blank=True, null=True)
    fecha_valoracion = models.DateTimeField(auto_now_add=True)

# --- Modelos Placeholder ---
class AtractivoTuristico(models.Model):
    nombre_atractivo = models.CharField(max_length=255)
    tipo_categoria_principal = models.CharField(max_length=255, blank=True, null=True)
    descripcion_breve = models.TextField(blank=True, null=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT)
    aprobado_publicar = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_atractivo

class DiagnosticoTerritorial(models.Model):
    municipio = models.OneToOneField(Municipio, on_delete=models.CASCADE, primary_key=True)
    anio_diagnostico = models.IntegerField()
    dimension_1_infraestructura = models.FloatField(blank=True, null=True)
    dimension_2_sostenibilidad = models.FloatField(blank=True, null=True)
    resultado_total = models.FloatField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

class IniciativaTuristica(models.Model):
    nombre_iniciativa = models.CharField(max_length=255)
    tipo_iniciativa = models.CharField(max_length=100, blank=True, null=True) # Plan, Programa, Proyecto
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True) # Formulación, Ejecución, Terminado
    presupuesto = models.FloatField(blank=True, null=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.nombre_iniciativa

class EventoTuristico(models.Model):
    nombre_evento = models.CharField(max_length=255)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    publicado = models.BooleanField(default=False)
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.nombre_evento

# --- Modelos Genéricos para el Motor de Reservas ---
class RecursoReservable(models.Model):
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE)
    nombre_recurso = models.CharField(max_length=255)
    tipo_recurso = models.CharField(max_length=100) # Ej: Habitación, Tour, Mesa
    capacidad = models.IntegerField()
    descripcion = models.TextField(blank=True, null=True)
    precio_base = models.FloatField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_recurso} ({self.empresa.razon_social_o_nombre_comercial})"

class Reserva(models.Model):
    recurso = models.ForeignKey(RecursoReservable, on_delete=models.PROTECT)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    estado = models.CharField(max_length=100) # Ej: Confirmada, Cancelada, Completada
    monto_final = models.FloatField(blank=True, null=True)
    promocion = models.ForeignKey('Promocion', on_delete=models.SET_NULL, blank=True, null=True)

class Promocion(models.Model):
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE)
    codigo_promocion = models.CharField(max_length=50, unique=True, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    tipo_descuento = models.CharField(max_length=50) # "porcentaje" o "fijo"
    valor_descuento = models.FloatField()
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class Pago(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    monto = models.FloatField()
    metodo_pago = models.CharField(max_length=100, blank=True, null=True)
    estado_pago = models.CharField(max_length=100, blank=True, null=True)
    fecha_pago = models.DateTimeField(auto_now_add=True)

class ReglaPrecio(models.Model):
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE)
    nombre_regla = models.CharField(max_length=255)
    tipo_regla = models.CharField(max_length=100) # "temporada", "dia_semana", "demanda"
    valor_ajuste = models.FloatField() # Puede ser un porcentaje (ej. 1.2 para +20%) o un monto fijo
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    dias_semana = models.CharField(max_length=20, blank=True, null=True) # "1,2,3,4,5" para L-V

    def __str__(self):
        return self.nombre_regla

# --- Modelos para el Módulo de Restaurantes (RAT) ---
class RestauranteMesa(models.Model):
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE)
    nombre_mesa = models.CharField(max_length=100) # Ej: "Mesa 5", "Barra 1"
    capacidad = models.IntegerField()
    estado = models.CharField(max_length=50) # "Libre", "Ocupada", "Reservada"

    def __str__(self):
        return self.nombre_mesa

class RestauranteMenuProducto(models.Model):
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE)
    nombre_producto = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.FloatField()
    categoria = models.CharField(max_length=100, blank=True, null=True) # "Entradas", "Platos Fuertes", "Bebidas"
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_producto

class RestaurantePedido(models.Model):
    mesa = models.ForeignKey(RestauranteMesa, on_delete=models.PROTECT)
    mesero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    estado = models.CharField(max_length=50) # "Abierto", "Enviado a Cocina", "Cerrado"
    total = models.FloatField(blank=True, null=True)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(blank=True, null=True)

class RestaurantePedidoItem(models.Model):
    pedido = models.ForeignKey(RestaurantePedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(RestauranteMenuProducto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.FloatField()
    estado = models.CharField(max_length=50) # "Pedido", "En Preparación", "Entregado"
    notas = models.TextField(blank=True, null=True)

# --- Modelos para el Módulo de Agencias de Viajes (RAT) ---
class AgenciaPaquete(models.Model):
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE)
    nombre_paquete = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio_total = models.FloatField()
    duracion_dias = models.IntegerField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_paquete

class PaqueteServicio(models.Model):
    paquete = models.ForeignKey(AgenciaPaquete, on_delete=models.CASCADE)
    tipo_servicio = models.CharField(max_length=100) # "hotel", "tour", "transporte"
    id_servicio_especifico = models.IntegerField()
    descripcion_servicio = models.TextField(blank=True, null=True)

class AgenciaReservaPaquete(models.Model):
    paquete = models.ForeignKey(AgenciaPaquete, on_delete=models.PROTECT)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha_inicio = models.DateField()
    numero_personas = models.IntegerField()
    estado = models.CharField(max_length=50) # "Confirmada", "Cancelada", "Completada"

# --- Modelos para el Módulo de Guías Turísticos (RAT) ---
class GuiaPerfil(models.Model):
    guia = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    idiomas = models.CharField(max_length=255, blank=True, null=True) # "Español,Inglés"
    especialidades = models.CharField(max_length=255, blank=True, null=True) # "Historia,Naturaleza"
    certificaciones = models.TextField(blank=True, null=True)
    tarifa_por_hora = models.FloatField(blank=True, null=True)

class GuiaDisponibilidad(models.Model):
    guia = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateField()
    disponible = models.BooleanField(default=True)

class GuiaReservaTour(models.Model):
    guia = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='tours_guiados')
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='tours_contratados')
    fecha_hora_inicio = models.DateTimeField()
    duracion_horas = models.IntegerField()
    estado = models.CharField(max_length=50) # "Solicitada", "Confirmada", "Cancelada"

# --- Modelos de Inventario de Dotación ---
class InventarioTipoItem(models.Model):
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE)
    nombre_tipo = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    stock_minimo_deseado = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.nombre_tipo

class InventarioItemIndividual(models.Model):
    tipo_item = models.ForeignKey(InventarioTipoItem, on_delete=models.CASCADE)
    estado = models.CharField(max_length=100)
    fecha_compra = models.DateField(blank=True, null=True)
    veces_usado = models.IntegerField(default=0)
    fecha_ultimo_mantenimiento = models.DateField(blank=True, null=True)
    notas_mantenimiento = models.TextField(blank=True, null=True)

# --- Modelos Adicionales ---
class ProductoEventoEmpresa(models.Model):
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=50) # 'Producto' o 'Evento'
    precio = models.FloatField(blank=True, null=True)
    fecha_evento = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class RegistroCliente(models.Model):
    empresa = models.ForeignKey(EmpresaPrestadorTuristico, on_delete=models.CASCADE)
    nacionalidad = models.CharField(max_length=50) # 'Nacional' o 'Extranjero'
    cantidad = models.IntegerField(default=1)
    fecha_registro = models.DateField()
