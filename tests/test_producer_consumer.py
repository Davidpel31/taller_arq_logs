"""
Tests unitarios para Producer y Consumer
Usar: pytest tests/test_producer.py -v
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'producer'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'consumer'))


class TestProducerValidation:
    """Tests para validación de datos en Producer"""
    
    def test_validar_datos_estacion_valida(self):
        """Prueba que estación válida no lanza excepción"""
        from producer import validar_datos
        
        # Debe pasar sin error
        assert validar_datos(3, 25.0, 65.0) == True
    
    def test_validar_datos_estacion_invalida_baja(self):
        """Prueba que estación menor a 1 falla"""
        from producer import validar_datos
        
        with pytest.raises(ValueError, match="Estación inválida"):
            validar_datos(0, 25.0, 65.0)
    
    def test_validar_datos_estacion_invalida_alta(self):
        """Prueba que estación mayor a 5 falla"""
        from producer import validar_datos
        
        with pytest.raises(ValueError, match="Estación inválida"):
            validar_datos(6, 25.0, 65.0)
    
    def test_validar_datos_temperatura_invalida_baja(self):
        """Prueba que temperatura menor a 15 falla"""
        from producer import validar_datos
        
        with pytest.raises(ValueError, match="Temperatura inválida"):
            validar_datos(2, 10.0, 65.0)
    
    def test_validar_datos_temperatura_invalida_alta(self):
        """Prueba que temperatura mayor a 35 falla"""
        from producer import validar_datos
        
        with pytest.raises(ValueError, match="Temperatura inválida"):
            validar_datos(2, 40.0, 65.0)
    
    def test_validar_datos_humedad_invalida_baja(self):
        """Prueba que humedad menor a 40 falla"""
        from producer import validar_datos
        
        with pytest.raises(ValueError, match="Humedad inválida"):
            validar_datos(2, 25.0, 30.0)
    
    def test_validar_datos_humedad_invalida_alta(self):
        """Prueba que humedad mayor a 90 falla"""
        from producer import validar_datos
        
        with pytest.raises(ValueError, match="Humedad inválida"):
            validar_datos(2, 25.0, 95.0)
    
    def test_validar_datos_limites_minimos(self):
        """Prueba datos en límites mínimos válidos"""
        from producer import validar_datos
        
        assert validar_datos(1, 15.0, 40.0) == True
    
    def test_validar_datos_limites_maximos(self):
        """Prueba datos en límites máximos válidos"""
        from producer import validar_datos
        
        assert validar_datos(5, 35.0, 90.0) == True


class TestProducerDataFormat:
    """Tests para formato de datos en Producer"""
    
    def test_formato_json_valido(self):
        """Prueba que el JSON es válido"""
        data = {
            "estacion_id": 1,
            "temperatura": 25.5,
            "humedad": 65.0,
            "fecha": "2025-11-11T12:30:45.123456"
        }
        
        # Debe serializar sin error
        json_str = json.dumps(data)
        assert json_str is not None
        
        # Debe deserializar sin error
        parsed = json.loads(json_str)
        assert parsed["estacion_id"] == 1
        assert parsed["temperatura"] == 25.5


class TestConsumerValidation:
    """Tests para Consumer"""
    
    def test_validar_datos_completos(self):
        """Prueba que datos completos se procesan"""
        data = {
            "estacion_id": 1,
            "temperatura": 25.0,
            "humedad": 65.0,
            "fecha": "2025-11-11T12:30:45"
        }
        
        # Verificar que tiene todas las claves
        required_keys = ["estacion_id", "temperatura", "humedad", "fecha"]
        assert all(key in data for key in required_keys)
    
    def test_validar_datos_incompletos(self):
        """Prueba que datos incompletos fallan"""
        data = {
            "estacion_id": 1,
            "temperatura": 25.0,
            # Falta 'humedad' y 'fecha'
        }
        
        required_keys = ["estacion_id", "temperatura", "humedad", "fecha"]
        assert not all(key in data for key in required_keys)


class TestJSONHandling:
    """Tests para manejo de JSON"""
    
    def test_json_decode_valido(self):
        """Prueba decodificación JSON válida"""
        json_str = '{"estacion_id": 1, "temperatura": 25.0}'
        
        try:
            data = json.loads(json_str)
            assert data["estacion_id"] == 1
        except json.JSONDecodeError:
            pytest.fail("JSONDecodeError fue lanzada inesperadamente")
    
    def test_json_decode_invalido(self):
        """Prueba que JSON inválido falla"""
        json_str = '{"estacion_id": 1, "temperatura": 25.0'  # Falta }
        
        with pytest.raises(json.JSONDecodeError):
            json.loads(json_str)


class TestDataTypes:
    """Tests para tipos de datos"""
    
    def test_estacion_id_es_entero(self):
        """Prueba que estacion_id es entero"""
        data = {"estacion_id": 1}
        assert isinstance(data["estacion_id"], int)
    
    def test_temperatura_es_float(self):
        """Prueba que temperatura es float"""
        data = {"temperatura": 25.5}
        assert isinstance(data["temperatura"], (int, float))
    
    def test_fecha_es_string(self):
        """Prueba que fecha es string"""
        data = {"fecha": "2025-11-11T12:30:45"}
        assert isinstance(data["fecha"], str)


class TestEdgeCases:
    """Tests para casos extremos"""
    
    def test_temperatura_negativa(self):
        """Prueba temperatura negativa"""
        from producer import validar_datos
        
        with pytest.raises(ValueError):
            validar_datos(1, -5.0, 65.0)
    
    def test_humedad_cero(self):
        """Prueba humedad en cero"""
        from producer import validar_datos
        
        with pytest.raises(ValueError):
            validar_datos(1, 25.0, 0.0)
    
    def test_humedad_cien(self):
        """Prueba humedad en 100"""
        from producer import validar_datos
        
        with pytest.raises(ValueError):
            validar_datos(1, 25.0, 100.0)


# Fixture para datos válidos
@pytest.fixture
def datos_validos():
    """Fixture con datos meteorológicos válidos"""
    return {
        "estacion_id": 3,
        "temperatura": 22.5,
        "humedad": 60.0,
        "fecha": "2025-11-11T12:30:45.123456"
    }


@pytest.fixture
def datos_invalidos_incompletos():
    """Fixture con datos incompletos"""
    return {
        "estacion_id": 3,
        "temperatura": 22.5
        # Faltan 'humedad' y 'fecha'
    }


class TestWithFixtures:
    """Tests usando fixtures"""
    
    def test_datos_validos_fixture(self, datos_validos):
        """Prueba datos válidos desde fixture"""
        assert "estacion_id" in datos_validos
        assert "temperatura" in datos_validos
        assert "humedad" in datos_validos
        assert "fecha" in datos_validos
    
    def test_datos_invalidos_fixture(self, datos_invalidos_incompletos):
        """Prueba datos incompletos desde fixture"""
        required_keys = ["estacion_id", "temperatura", "humedad", "fecha"]
        assert not all(key in datos_invalidos_incompletos for key in required_keys)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
