import unittest
import os
import shutil
from turismo_app.database import db_manager

class TestDbManagerAtractivos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a temporary database for testing."""
        cls.test_db_name = "test_atractivos.db"
        cls.original_db_path = db_manager.DB_PATH
        db_manager.DB_PATH = os.path.join(os.path.dirname(__file__), cls.test_db_name)

        # We will use the setup_database function from the creation script
        # to build a clean test database.
        from turismo_app.database import create_final_db
        cls.original_create_db_path = create_final_db.DB_PATH
        create_final_db.DB_PATH = db_manager.DB_PATH

        # The setup_database function handles creation and schema setup
        create_final_db.setup_database()

        # Now, apply the schema updates to the newly created test DB
        from turismo_app.database import update_schema
        cls.original_update_db_path = update_schema.DB_PATH
        update_schema.DB_PATH = db_manager.DB_PATH
        update_schema.update_schema()

        # Restore the original paths for the scripts
        create_final_db.DB_PATH = cls.original_create_db_path
        update_schema.DB_PATH = cls.original_update_db_path

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary database."""
        os.remove(db_manager.DB_PATH)
        db_manager.DB_PATH = cls.original_db_path

    def setUp(self):
        """Clean up database before each test."""
        with db_manager.get_db_connection() as conn:
            # Delete in order to respect foreign key constraints
            conn.execute("DELETE FROM atractivos_turisticos")
            conn.execute("DELETE FROM usuarios WHERE nombre_usuario != 'admin'") # Keep admin user
            conn.execute("DELETE FROM empresas_prestadores_turisticos")
            conn.execute("DELETE FROM municipios")
            conn.execute("DELETE FROM departamentos")

            # Re-insert necessary geo data for tests
            conn.execute("INSERT INTO departamentos (codigo_departamento, nombre_departamento) VALUES ('05', 'Antioquia')")
            conn.execute("INSERT INTO municipios (codigo_municipio, nombre_municipio, codigo_departamento) VALUES ('05001', 'Medellín', '05')")
            conn.commit()


    def test_crear_y_obtener_atractivo_detallado(self):
        """Test creating and retrieving a detailed tourist attraction."""
        atractivo_data = {
            "nombre": "Parque Arví",
            "descripcion": "Reserva forestal y parque ecoturístico.",
            "codigo_municipio": "05001",
            "tipo_atractivo": "Sitio Natural",
            "subtipo_atractivo": "Bosques",
            "ubicacion_especifica": "Corregimiento de Santa Elena",
            "temperatura_promedio": 17.0,
            "altitud": 2500,
            "horario_atencion": "Martes a Domingo, 9am a 6pm",
            "tarifa_ingreso": 5000.0,
            "actividades_principales": "Senderismo, Picnic, Avistamiento de aves",
            "servicios_ofrecidos": "Restaurantes, Baños, Guías",
            "recomendaciones": "Llevar ropa cómoda y abrigo.",
            "estado_conservacion": "Bueno",
            "contacto_informacion": "info@parquearvi.com",
            "audit_user_id": 1
        }

        atractivo_id = db_manager.crear_o_actualizar_atractivo_detallado(atractivo_data)
        self.assertIsNotNone(atractivo_id)

        atractivo_obtenido = db_manager.obtener_atractivo_detallado_por_id(atractivo_id)

        self.assertIsNotNone(atractivo_obtenido)
        self.assertEqual(atractivo_obtenido["nombre"], "Parque Arví")
        self.assertEqual(atractivo_obtenido["tipo_atractivo"], "Sitio Natural")
        self.assertEqual(atractivo_obtenido["nombre_municipio"], "Medellín")


    def test_actualizar_atractivo_detallado(self):
        """Test updating a detailed tourist attraction."""
        atractivo_data = {
            "nombre": "Jardín Botánico",
            "descripcion": "Oasis verde en la ciudad.",
            "codigo_municipio": "05001",
            "tipo_atractivo": "Cultural",
            "subtipo_atractivo": "Museo",
            "audit_user_id": 1
        }
        atractivo_id = db_manager.crear_o_actualizar_atractivo_detallado(atractivo_data)

        datos_actualizados = {
            "nombre": "Jardín Botánico de Medellín",
            "descripcion": "Un oasis de naturaleza y ciencia en el corazón de Medellín.",
            "tarifa_ingreso": 0.0, # Es gratis
            "audit_user_id": 1
        }

        db_manager.crear_o_actualizar_atractivo_detallado(datos_actualizados, atractivo_id)

        atractivo_actualizado = db_manager.obtener_atractivo_detallado_por_id(atractivo_id)

        self.assertEqual(atractivo_actualizado["nombre"], "Jardín Botánico de Medellín")
        self.assertEqual(atractivo_actualizado["descripcion"], "Un oasis de naturaleza y ciencia en el corazón de Medellín.")
        self.assertEqual(atractivo_actualizado["tarifa_ingreso"], 0.0)

if __name__ == '__main__':
    unittest.main()
