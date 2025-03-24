import os
import pytest

def test_env_loaded():
    """Verifica que las variables de entorno se cargaron correctamente"""
    db_name = os.getenv("DB_NAME")
    assert db_name is not None
    assert "test" in db_name.lower()
    print(f"Base de datos configurada correctamente: {db_name}")