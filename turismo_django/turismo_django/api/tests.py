from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Usuario, Rol, Departamento, EmpresaPrestadorTuristico, ProductoEventoEmpresa
from rest_framework.authtoken.models import Token

from .models import Municipio

class DepartamentoAPITests(APITestCase):
    def setUp(self):
        # Create roles and users
        self.superadmin_rol = Rol.objects.create(nombre_rol='SuperAdmin')
        self.test_rol = Rol.objects.create(nombre_rol='test')
        self.superadmin = Usuario.objects.create_user(username='superadmin', password='testpassword', rol=self.superadmin_rol)
        self.user = Usuario.objects.create_user(username='testuser', password='testpassword', rol=self.test_rol)

        # Create tokens
        self.superadmin_token = Token.objects.create(user=self.superadmin)
        self.user_token = Token.objects.create(user=self.user)

        # Create some data
        self.departamento = Departamento.objects.create(codigo_departamento='01', nombre_departamento='Antioquia')
        self.municipio = Municipio.objects.create(codigo_municipio='05001', nombre_municipio='Medellín', departamento=self.departamento)

    def test_get_departamentos(self):
        """
        Ensure any authenticated user can get the list of departamentos.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('departamento-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre_departamento'], 'Antioquia')

class EmpresaPrestadorTuristicoAPITests(APITestCase):
    def setUp(self):
        # Create roles and users
        self.superadmin_rol = Rol.objects.create(nombre_rol='SuperAdmin')
        self.test_rol = Rol.objects.create(nombre_rol='test')
        self.superadmin = Usuario.objects.create_user(username='superadmin', password='testpassword', rol=self.superadmin_rol)
        self.user = Usuario.objects.create_user(username='testuser', password='testpassword', rol=self.test_rol)

        # Create tokens
        self.superadmin_token = Token.objects.create(user=self.superadmin)
        self.user_token = Token.objects.create(user=self.user)

        # Create some data
        self.departamento = Departamento.objects.create(codigo_departamento='01', nombre_departamento='Antioquia')
        self.municipio = Municipio.objects.create(codigo_municipio='05001', nombre_municipio='Medellín', departamento=self.departamento)
        self.empresa = EmpresaPrestadorTuristico.objects.create(razon_social_o_nombre_comercial='Test Empresa', tipo_prestador='Hotel', municipio=self.municipio)

    def test_list_empresas(self):
        """
        Ensure any authenticated user can list empresas.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response = self.client.get(reverse('empresa-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_empresa_as_superadmin(self):
        """
        Ensure a superadmin can create an empresa.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.superadmin_token.key)
        data = {'razon_social_o_nombre_comercial': 'New Empresa', 'tipo_prestador': 'Restaurant', 'municipio': self.municipio.codigo_municipio}
        response = self.client.post(reverse('empresa-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_empresa_as_normal_user(self):
        """
        Ensure a normal user cannot create an empresa.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        data = {'razon_social_o_nombre_comercial': 'New Empresa', 'tipo_prestador': 'Restaurant', 'municipio': self.municipio.codigo_municipio}
        response = self.client.post(reverse('empresa-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_empresa_as_superadmin(self):
        """
        Ensure a superadmin can update an empresa.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.superadmin_token.key)
        data = {'razon_social_o_nombre_comercial': 'Updated Empresa'}
        response = self.client.patch(reverse('empresa-detail', kwargs={'pk': self.empresa.pk}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['razon_social_o_nombre_comercial'], 'Updated Empresa')

    def test_delete_empresa_as_superadmin(self):
        """
        Ensure a superadmin can delete an empresa.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.superadmin_token.key)
        response = self.client.delete(reverse('empresa-detail', kwargs={'pk': self.empresa.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class ProductoEventoEmpresaAPITests(APITestCase):
    def setUp(self):
        # Create roles and users
        self.owner_rol = Rol.objects.create(nombre_rol='PropietarioEmpresa')
        self.other_rol = Rol.objects.create(nombre_rol='test')
        self.departamento = Departamento.objects.create(codigo_departamento='01', nombre_departamento='Antioquia')
        self.municipio = Municipio.objects.create(codigo_municipio='05001', nombre_municipio='Medellín', departamento=self.departamento)
        self.empresa = EmpresaPrestadorTuristico.objects.create(razon_social_o_nombre_comercial='Test Empresa', tipo_prestador='Hotel', municipio=self.municipio)
        self.owner = Usuario.objects.create_user(username='owner', password='testpassword', rol=self.owner_rol, empresa_asociada=self.empresa)
        self.other_user = Usuario.objects.create_user(username='other', password='testpassword', rol=self.other_rol)

        # Create tokens
        self.owner_token = Token.objects.create(user=self.owner)
        self.other_token = Token.objects.create(user=self.other_user)

        # Create some data
        self.producto = ProductoEventoEmpresa.objects.create(nombre='Test Product', tipo='Producto', empresa=self.empresa)

    def test_list_productos(self):
        """
        Ensure any authenticated user can list productos.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.other_token.key)
        response = self.client.get(reverse('productoeventoempresa-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_producto_as_owner(self):
        """
        Ensure an owner can create a producto for their empresa.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.owner_token.key)
        data = {'nombre': 'New Product', 'tipo': 'Producto', 'empresa': self.empresa.pk}
        response = self.client.post(reverse('productoeventoempresa-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_producto_for_other_empresa(self):
        """
        Ensure an owner cannot create a producto for another empresa.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.owner_token.key)
        other_empresa = EmpresaPrestadorTuristico.objects.create(razon_social_o_nombre_comercial='Other Empresa', tipo_prestador='Hotel', municipio=self.municipio)
        data = {'nombre': 'New Product', 'tipo': 'Producto', 'empresa': other_empresa.pk}
        response = self.client.post(reverse('productoeventoempresa-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_producto_as_owner(self):
        """
        Ensure an owner can update their producto.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.owner_token.key)
        data = {'nombre': 'Updated Product'}
        response = self.client.patch(reverse('productoeventoempresa-detail', kwargs={'pk': self.producto.pk}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_producto_as_owner(self):
        """
        Ensure an owner can delete their producto.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.owner_token.key)
        response = self.client.delete(reverse('productoeventoempresa-detail', kwargs={'pk': self.producto.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
