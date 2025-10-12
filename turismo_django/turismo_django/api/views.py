from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import IsSuperAdmin, IsOwnerOfEmpresa
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
from .serializers import (
    DepartamentoSerializer,
    MunicipioSerializer,
    RolSerializer,
    UsuarioSerializer,
    EmpresaPrestadorTuristicoSerializer,
    VacanteEmpleoSerializer,
    TuristaRegistroSerializer,
    EncuestaPercepcionSerializer,
    AtractivoTuristicoSerializer,
    DiagnosticoTerritorialSerializer,
    IniciativaTuristicaSerializer,
    EventoTuristicoSerializer,
    RecursoReservableSerializer,
    ReservaSerializer,
    PromocionSerializer,
    PagoSerializer,
    ReglaPrecioSerializer,
    RestauranteMesaSerializer,
    RestauranteMenuProductoSerializer,
    RestaurantePedidoSerializer,
    RestaurantePedidoItemSerializer,
    AgenciaPaqueteSerializer,
    PaqueteServicioSerializer,
    AgenciaReservaPaqueteSerializer,
    GuiaPerfilSerializer,
    GuiaDisponibilidadSerializer,
    GuiaReservaTourSerializer,
    InventarioTipoItemSerializer,
    InventarioItemIndividualSerializer,
    ProductoEventoEmpresaSerializer,
    RegistroClienteSerializer,
)

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer

class MunicipioViewSet(viewsets.ModelViewSet):
    queryset = Municipio.objects.all()
    serializer_class = MunicipioSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class EmpresaPrestadorTuristicoViewSet(viewsets.ModelViewSet):
    queryset = EmpresaPrestadorTuristico.objects.all()
    serializer_class = EmpresaPrestadorTuristicoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            self.permission_classes = [IsSuperAdmin]
        return super().get_permissions()

class VacanteEmpleoViewSet(viewsets.ModelViewSet):
    queryset = VacanteEmpleo.objects.all()
    serializer_class = VacanteEmpleoSerializer

class TuristaRegistroViewSet(viewsets.ModelViewSet):
    queryset = TuristaRegistro.objects.all()
    serializer_class = TuristaRegistroSerializer

class EncuestaPercepcionViewSet(viewsets.ModelViewSet):
    queryset = EncuestaPercepcion.objects.all()
    serializer_class = EncuestaPercepcionSerializer

class AtractivoTuristicoViewSet(viewsets.ModelViewSet):
    queryset = AtractivoTuristico.objects.all()
    serializer_class = AtractivoTuristicoSerializer

class DiagnosticoTerritorialViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticoTerritorial.objects.all()
    serializer_class = DiagnosticoTerritorialSerializer

class IniciativaTuristicaViewSet(viewsets.ModelViewSet):
    queryset = IniciativaTuristica.objects.all()
    serializer_class = IniciativaTuristicaSerializer

class EventoTuristicoViewSet(viewsets.ModelViewSet):
    queryset = EventoTuristico.objects.all()
    serializer_class = EventoTuristicoSerializer

class RecursoReservableViewSet(viewsets.ModelViewSet):
    queryset = RecursoReservable.objects.all()
    serializer_class = RecursoReservableSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

class PromocionViewSet(viewsets.ModelViewSet):
    queryset = Promocion.objects.all()
    serializer_class = PromocionSerializer

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

class ReglaPrecioViewSet(viewsets.ModelViewSet):
    queryset = ReglaPrecio.objects.all()
    serializer_class = ReglaPrecioSerializer

class RestauranteMesaViewSet(viewsets.ModelViewSet):
    queryset = RestauranteMesa.objects.all()
    serializer_class = RestauranteMesaSerializer

class RestauranteMenuProductoViewSet(viewsets.ModelViewSet):
    queryset = RestauranteMenuProducto.objects.all()
    serializer_class = RestauranteMenuProductoSerializer

class RestaurantePedidoViewSet(viewsets.ModelViewSet):
    queryset = RestaurantePedido.objects.all()
    serializer_class = RestaurantePedidoSerializer

class RestaurantePedidoItemViewSet(viewsets.ModelViewSet):
    queryset = RestaurantePedidoItem.objects.all()
    serializer_class = RestaurantePedidoItemSerializer

class AgenciaPaqueteViewSet(viewsets.ModelViewSet):
    queryset = AgenciaPaquete.objects.all()
    serializer_class = AgenciaPaqueteSerializer

class PaqueteServicioViewSet(viewsets.ModelViewSet):
    queryset = PaqueteServicio.objects.all()
    serializer_class = PaqueteServicioSerializer

class AgenciaReservaPaqueteViewSet(viewsets.ModelViewSet):
    queryset = AgenciaReservaPaquete.objects.all()
    serializer_class = AgenciaReservaPaqueteSerializer

class GuiaPerfilViewSet(viewsets.ModelViewSet):
    queryset = GuiaPerfil.objects.all()
    serializer_class = GuiaPerfilSerializer

class GuiaDisponibilidadViewSet(viewsets.ModelViewSet):
    queryset = GuiaDisponibilidad.objects.all()
    serializer_class = GuiaDisponibilidadSerializer

class GuiaReservaTourViewSet(viewsets.ModelViewSet):
    queryset = GuiaReservaTour.objects.all()
    serializer_class = GuiaReservaTourSerializer

class InventarioTipoItemViewSet(viewsets.ModelViewSet):
    queryset = InventarioTipoItem.objects.all()
    serializer_class = InventarioTipoItemSerializer

class InventarioItemIndividualViewSet(viewsets.ModelViewSet):
    queryset = InventarioItemIndividual.objects.all()
    serializer_class = InventarioItemIndividualSerializer

class ProductoEventoEmpresaViewSet(viewsets.ModelViewSet):
    queryset = ProductoEventoEmpresa.objects.all()
    serializer_class = ProductoEventoEmpresaSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            self.permission_classes = [IsOwnerOfEmpresa]
        return super().get_permissions()

class RegistroClienteViewSet(viewsets.ModelViewSet):
    queryset = RegistroCliente.objects.all()
    serializer_class = RegistroClienteSerializer

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
