from rest_framework import serializers
from .models import (
    Departamento,
    Municipio,
    Rol,
    Usuario,
    EmpresaPrestadorTuristico,
    VacanteEmpleo,
    TuristaRegistro,
    EncuestaPercepcion,
    AtractivoTuristico,
    DiagnosticoTerritorial,
    IniciativaTuristica,
    EventoTuristico,
    RecursoReservable,
    Reserva,
    Promocion,
    Pago,
    ReglaPrecio,
    RestauranteMesa,
    RestauranteMenuProducto,
    RestaurantePedido,
    RestaurantePedidoItem,
    AgenciaPaquete,
    PaqueteServicio,
    AgenciaReservaPaquete,
    GuiaPerfil,
    GuiaDisponibilidad,
    GuiaReservaTour,
    InventarioTipoItem,
    InventarioItemIndividual,
    ProductoEventoEmpresa,
    RegistroCliente,
)

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'

class MunicipioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = '__all__'

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'rol', 'municipio', 'departamento', 'empresa_asociada', 'is_active', 'date_joined')

class EmpresaPrestadorTuristicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpresaPrestadorTuristico
        fields = '__all__'

class VacanteEmpleoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacanteEmpleo
        fields = '__all__'

class TuristaRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuristaRegistro
        fields = '__all__'

class EncuestaPercepcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncuestaPercepcion
        fields = '__all__'

class AtractivoTuristicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtractivoTuristico
        fields = '__all__'

class DiagnosticoTerritorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticoTerritorial
        fields = '__all__'

class IniciativaTuristicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = IniciativaTuristica
        fields = '__all__'

class EventoTuristicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoTuristico
        fields = '__all__'

class RecursoReservableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecursoReservable
        fields = '__all__'

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'

class PromocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocion
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'

class ReglaPrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglaPrecio
        fields = '__all__'

class RestauranteMesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestauranteMesa
        fields = '__all__'

class RestauranteMenuProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestauranteMenuProducto
        fields = '__all__'

class RestaurantePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantePedido
        fields = '__all__'

class RestaurantePedidoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantePedidoItem
        fields = '__all__'

class AgenciaPaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgenciaPaquete
        fields = '__all__'

class PaqueteServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaqueteServicio
        fields = '__all__'

class AgenciaReservaPaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgenciaReservaPaquete
        fields = '__all__'

class GuiaPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuiaPerfil
        fields = '__all__'

class GuiaDisponibilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuiaDisponibilidad
        fields = '__all__'

class GuiaReservaTourSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuiaReservaTour
        fields = '__all__'

class InventarioTipoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventarioTipoItem
        fields = '__all__'

class InventarioItemIndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventarioItemIndividual
        fields = '__all__'

class ProductoEventoEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoEventoEmpresa
        fields = '__all__'

class RegistroClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroCliente
        fields = '__all__'
