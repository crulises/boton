import pytest
from unittest.mock import patch, mock_open

from boton.utils.config_parser import BotonConfigParser

# Contenido YAML válido para pruebas. esto más adelante lo podemos 
# sacar del archivo, lo dejo acá para que todo sea autocontenido
VALID_YAML = """
prompts:
  - prompt: "Optimización de SQL"
    tipo: "mejores-practicas-sql"
    extension: "sql"
  - prompt: "Buenas prácticas en Python"
    tipo: "mejores-practicas-python"
    extension: "py"
  - prompt: "Errores comunes en Jupyter"
    tipo: "errores-comunes"
    extension: "ipynb"
"""

# Contenido YAML inválido para pruebasesto más adelante lo podemos 
# sacar del archivo, lo dejo acá para que todo sea autocontenido
INVALID_YAML = """
prompts:
  - prompt: "Entrada incorrecta"
    tipo: "mejores-practicas
"""

# De igual manera, los fixtures, no son necesarios, pero los dejo acá
# para que todo sea autocontenido.
@pytest.fixture
def mock_valid_yaml_file():
    """Simula un archivo YAML válido."""
    with patch("builtins.open", mock_open(read_data=VALID_YAML)):
        yield "test_valid.yaml"  # Nombre de archivo simulado

@pytest.fixture
def mock_invalid_yaml_file():
    """Simula un archivo YAML con sintaxis inválida."""
    with patch("builtins.open", mock_open(read_data=INVALID_YAML)):
        yield "test_invalid.yaml"  # Nombre de archivo simulado

@pytest.fixture
def mock_nonexistent_yaml_file():
    """Simula un archivo que no existe en el sistema."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        yield "nonexistent.yaml"

def test_load_valid_yaml(mock_valid_yaml_file):
    """Verifica que se cargue correctamente un archivo YAML válido."""
    parser = BotonConfigParser(archivo=mock_valid_yaml_file)
    assert len(parser.config.get("prompts", [])) == 3
    assert parser.config["prompts"][0]["tipo"] == "mejores-practicas-sql"

def test_load_nonexistent_yaml(mock_nonexistent_yaml_file):
    """Verifica que se maneje correctamente el error de archivo no encontrado."""
    with patch("boton.utils.config_parser.logger.error") as mock_logger:
        parser = BotonConfigParser(archivo=mock_nonexistent_yaml_file)
        assert parser.config == {}
        mock_logger.assert_called_with("Error: El archivo 'nonexistent.yaml' no existe.")

def test_load_invalid_yaml(mock_invalid_yaml_file):
    """Verifica que se maneje correctamente un archivo YAML con sintaxis incorrecta."""
    with patch("boton.utils.config_parser.logger.error") as mock_logger:
        parser = BotonConfigParser(archivo=mock_invalid_yaml_file)
        assert parser.config == {}
        mock_logger.assert_called()

def test_get_prompts(mock_valid_yaml_file):
    """Verifica que el método get_prompts funcione correctamente."""
    parser = BotonConfigParser(archivo=mock_valid_yaml_file)
    resultado = parser.get_prompts(attr="tipo", valor="mejores-practicas-python")
    # Se espera que la lista contenga 1 elemento
    assert len(resultado) == 1
    # Se espera que el elemento sea un string ya que este representa un prompt
    assert isinstance(resultado[0], str)

def test_fz_filtrar_prompt(mock_valid_yaml_file):
    """Verifica que el método de búsqueda difusa retorne resultados relevantes."""
    parser = BotonConfigParser(mock_valid_yaml_file)
    resultado = parser.fz_filtrar_prompt("SQL", limite=2)
    assert len(resultado) > 0
    assert any("SQL" in p["prompt"] for p in resultado)
