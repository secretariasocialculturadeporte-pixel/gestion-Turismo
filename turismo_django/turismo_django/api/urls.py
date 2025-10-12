from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    CurrentUserView,
    DepartamentoViewSet,
    MunicipioViewSet,
    RolViewSet,
    UsuarioViewSet,
    EmpresaPrestadorTuristicoViewSet,
    VacanteEmpleoViewSet,
    TuristaRegistroViewSet,
    EncuestaPercepcionViewSet,
    AtractivoTuristicoViewSet,
    DiagnosticoTerritorialViewSet,
    IniciativaTuristicaViewSet,
    EventoTuristicoViewSet,
    RecursoReservableViewSet,
    ReservaViewSet,
    PromocionViewSet,
    PagoViewSet,
    ReglaPrecioViewSet,
    RestauranteMesaViewSet,
    RestauranteMenuProductoViewSet,
    RestaurantePedidoViewSet,
    RestaurantePedidoItemViewSet,
    AgenciaPaqueteViewSet,
    PaqueteServicioViewSet,
    AgenciaReservaPaqueteViewSet,
    GuiaPerfilViewSet,
    GuiaDisponibilidadViewSet,
    GuiaReservaTourViewSet,
    InventarioTipoItemViewSet,
    InventarioItemIndividualViewSet,
    ProductoEventoEmpresaViewSet,
    RegistroClienteViewSet,
)

router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet, basename='departamento')
router.register(r'municipios', MunicipioViewSet)
router.register(r'roles', RolViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'empresas', EmpresaPrestadorTuristicoViewSet, basename='empresa')
router.register(r'vacantes', VacanteEmpleoViewSet)
router.register(r'turistas', TuristaRegistroViewSet)
router.register(r'encuestas', EncuestaPercepcionViewSet)
router.register(r'atractivos', AtractivoTuristicoViewSet)
router.register(r'diagnosticos', DiagnosticoTerritorialViewSet)
router.register(r'iniciativas', IniciativaTuristicaViewSet)
router.register(r'eventos', EventoTuristicoViewSet)
router.register(r'recursos', RecursoReservableViewSet)
router.register(r'reservas', ReservaViewSet)
router.register(r'promociones', PromocionViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'reglas-precio', ReglaPrecioViewSet)
router.register(r'mesas', RestauranteMesaViewSet)
router.register(r'menu', RestauranteMenuProductoViewSet)
router.register(r'pedidos', RestaurantePedidoViewSet)
router.register(r'pedidos-items', RestaurantePedidoItemViewSet)
router.register(r'paquetes', AgenciaPaqueteViewSet)
router.register(r'paquetes-servicios', PaqueteServicioViewSet)
router.register(r'reservas-paquetes', AgenciaReservaPaqueteViewSet)
router.register(r'guias', GuiaPerfilViewSet)
router.register(r'guias-disponibilidad', GuiaDisponibilidadViewSet)
router.register(r'guias-reservas', GuiaReservaTourViewSet)
router.register(r'inventario-tipos', InventarioTipoItemViewSet)
router.register(r'inventario-items', InventarioItemIndividualViewSet)
router.register(r'productos-eventos', ProductoEventoEmpresaViewSet, basename='productoeventoempresa')
router.register(r'registros-clientes', RegistroClienteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('user/', CurrentUserView.as_view(), name='user'),
]
