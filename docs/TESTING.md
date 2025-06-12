# Guía de Pruebas | Testing Guide

_Español_

Esta guía proporciona información detallada sobre cómo escribir, ejecutar y mantener pruebas para el proyecto KMC (Kimfe Markdown Convention).

## Configuración del Entorno de Pruebas

Antes de ejecutar las pruebas, asegúrate de tener instaladas las dependencias de desarrollo:

```bash
# Instalar dependencias de desarrollo
pip install -e ".[dev]"
```

## Ejecutar Pruebas

### Ejecutar todas las pruebas

```bash
pytest
```

### Ejecutar pruebas con cobertura

```bash
pytest --cov=kmc_parser
```

### Ejecutar pruebas específicas

```bash
# Ejecutar una clase de prueba específica
pytest tests/test_parser.py::TestKMCParser

# Ejecutar un método de prueba específico
pytest tests/test_parser.py::TestKMCParser::test_parse_contextual_vars
```

## Estructura de las Pruebas

Las pruebas están organizadas siguiendo la estructura del código:

```
tests/
│
├── test_parser.py              # Pruebas para parser.py
├── test_auto_register.py       # Pruebas para registro automático de handlers
├── test_variable_definition.py # Pruebas para definiciones de variables
├── core/
│   ├── test_registry.py        # Pruebas para el sistema de registro
│   └── ...
├── handlers/
│   ├── test_base.py            # Pruebas para los handlers base
│   └── ...
├── extensions/
│   ├── test_plugin_manager.py  # Pruebas para el gestor de plugins
│   └── ...
└── ...
```

## Escribir Nuevas Pruebas

Al escribir nuevas pruebas, sigue estas directrices:

1. **Nombrado**: Las clases de prueba deben tener el prefijo `Test` y los métodos de prueba deben tener el prefijo `test_`.

2. **Estructura**: Usa el siguiente formato para las pruebas:
   ```python
   def test_alguna_funcionalidad(self):
       """Descripción clara de lo que prueba este test."""
       # Configuración (Setup)
       input_data = "alguna_entrada"
       
       # Ejecución (Exercise)
       result = function_to_test(input_data)
       
       # Verificación (Verify)
       self.assertEqual(result, "resultado_esperado")
       
       # Limpieza (Teardown, si es necesario)
       # cleanup_resources()
   ```

3. **Fixtures**: Usa fixtures de pytest para reutilizar configuraciones comunes:
   ```python
   @pytest.fixture
   def sample_parser():
       parser = KMCParser()
       # Configurar el parser con handlers de prueba
       return parser
       
   def test_process_document(self, sample_parser):
       result = sample_parser.process("texto de ejemplo")
       assert "texto procesado" in result
   ```

4. **Mocks**: Usa `unittest.mock` o `pytest-mock` para simular dependencias externas:
   ```python
   def test_api_handler(self, mocker):
       # Simular una llamada API externa
       mock_response = mocker.patch('requests.get')
       mock_response.return_value.json.return_value = {"data": "ejemplo"}
       
       handler = APIHandler()
       result = handler.handle("test_var")
       
       assert "ejemplo" in result
   ```

5. **Parametrización**: Para probar múltiples casos, usa parametrización:
   ```python
   @pytest.mark.parametrize("input_text,expected", [
       ("[[project:nombre]]", "Proyecto Demo"),
       ("[[user:email]]", "usuario@ejemplo.com"),
       ("[[org:nombre_empresa]]", "Reevolutiva"),
   ])
   def test_contextual_variables(self, sample_parser, input_text, expected):
       result = sample_parser.process(input_text)
       assert result == expected
   ```

## Pruebas de Integración

Las pruebas de integración verifican que diferentes componentes trabajen juntos correctamente:

```python
def test_full_document_processing():
    """Prueba el proceso completo de un documento KMC."""
    parser = KMCParser()
    # Registrar handlers necesarios
    
    with open("tests/resources/sample_document.md", "r") as f:
        content = f.read()
        
    result = parser.process(content)
    
    # Verificar que el resultado contenga elementos esperados
    assert "Título procesado" in result
    assert "Contenido generado" in result
```

## Recomendaciones para Pruebas

1. **Pruebas aisladas**: Cada prueba debe ser independiente y no depender del estado dejado por otras pruebas.

2. **Limpieza**: Si una prueba modifica el estado global (archivos, variables de entorno), asegúrate de limpiarlo en el teardown.

3. **Reproducibilidad**: Las pruebas deben ser deterministas - el mismo resultado cada vez.

4. **Claridad**: Los nombres de pruebas deben describir claramente qué se está probando y bajo qué condiciones.

5. **Documentación**: Incluye docstrings en tus pruebas para explicar su propósito y cualquier detalle importante.

## Pruebas Específicas para KMC

### Pruebas de Variables Contextuales

```python
def test_contextual_variable_resolution():
    parser = KMCParser()
    parser.register_context_handler("project", lambda var: "Demo" if var == "nombre" else f"<project:{var}>")
    
    result = parser.process("Proyecto: [[project:nombre]]")
    assert result == "Proyecto: Demo"
```

### Pruebas de Variables de Metadata

```python
def test_metadata_variable_resolution():
    parser = KMCParser()
    parser.register_metadata_handler("doc", lambda var: "1.0" if var == "version" else f"<doc:{var}>")
    
    result = parser.process("Versión: [{doc:version}]")
    assert result == "Versión: 1.0"
```

### Pruebas de Variables Generativas

```python
def test_generative_variable_with_kmc_definition():
    parser = KMCParser()
    
    # Registrar un handler generativo de prueba
    def test_ai_handler(var):
        if var.name == "extract_title" and var.prompt and "contenido" in var.prompt:
            return "Título Extraído"
        return "<generado>"
    
    parser.register_generative_handler("ai:gpt4", test_ai_handler)
    
    # Documento con definición KMC y variable de metadata referenciada
    content = """
    # Documento de Prueba
    
    [{doc:titulo}]
    
    <!-- KMC_DEFINITION FOR [{doc:titulo}]:
    GENERATIVE_SOURCE = {{ai:gpt4:extract_title}}
    PROMPT = "Extrae un título del siguiente contenido: Este es un contenido de prueba"
    -->
    """
    
    result = parser.process(content)
    assert "Título Extraído" in result
```

## Recursos Adicionales

- [Documentación de pytest](https://docs.pytest.org/)
- [Documentación de pytest-mock](https://pytest-mock.readthedocs.io/)
- [Documentación de pytest-cov](https://pytest-cov.readthedocs.io/)

---

_English_

This guide provides detailed information on how to write, run, and maintain tests for the KMC (Kimfe Markdown Convention) project.

## Setting Up the Testing Environment

Before running tests, make sure you have the development dependencies installed:

```bash
# Install development dependencies
pip install -e ".[dev]"
```

## Running Tests

### Run all tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=kmc_parser
```

### Run specific tests

```bash
# Run a specific test class
pytest tests/test_parser.py::TestKMCParser

# Run a specific test method
pytest tests/test_parser.py::TestKMCParser::test_parse_contextual_vars
```

## Test Structure

Tests are organized following the code structure:

```
tests/
│
├── test_parser.py              # Tests for parser.py
├── test_auto_register.py       # Tests for automatic handler registration
├── test_variable_definition.py # Tests for variable definitions
├── core/
│   ├── test_registry.py        # Tests for the registry system
│   └── ...
├── handlers/
│   ├── test_base.py            # Tests for base handlers
│   └── ...
├── extensions/
│   ├── test_plugin_manager.py  # Tests for the plugin manager
│   └── ...
└── ...
```

## Writing New Tests

When writing new tests, follow these guidelines:

1. **Naming**: Test classes should have the prefix `Test` and test methods should have the prefix `test_`.

2. **Structure**: Use the following format for tests:
   ```python
   def test_some_functionality(self):
       """Clear description of what this test is checking."""
       # Setup
       input_data = "some_input"
       
       # Exercise
       result = function_to_test(input_data)
       
       # Verify
       self.assertEqual(result, "expected_result")
       
       # Teardown (if necessary)
       # cleanup_resources()
   ```

3. **Fixtures**: Use pytest fixtures to reuse common setups:
   ```python
   @pytest.fixture
   def sample_parser():
       parser = KMCParser()
       # Configure the parser with test handlers
       return parser
       
   def test_process_document(self, sample_parser):
       result = sample_parser.process("example text")
       assert "processed text" in result
   ```

4. **Mocks**: Use `unittest.mock` or `pytest-mock` to simulate external dependencies:
   ```python
   def test_api_handler(self, mocker):
       # Simulate an external API call
       mock_response = mocker.patch('requests.get')
       mock_response.return_value.json.return_value = {"data": "example"}
       
       handler = APIHandler()
       result = handler.handle("test_var")
       
       assert "example" in result
   ```

5. **Parameterization**: To test multiple cases, use parameterization:
   ```python
   @pytest.mark.parametrize("input_text,expected", [
       ("[[project:name]]", "Demo Project"),
       ("[[user:email]]", "user@example.com"),
       ("[[org:company_name]]", "Reevolutiva"),
   ])
   def test_contextual_variables(self, sample_parser, input_text, expected):
       result = sample_parser.process(input_text)
       assert result == expected
   ```

## Integration Tests

Integration tests verify that different components work together correctly:

```python
def test_full_document_processing():
    """Test the complete processing of a KMC document."""
    parser = KMCParser()
    # Register necessary handlers
    
    with open("tests/resources/sample_document.md", "r") as f:
        content = f.read()
        
    result = parser.process(content)
    
    # Verify that the result contains expected elements
    assert "Processed Title" in result
    assert "Generated Content" in result
```

## Testing Best Practices

1. **Isolated tests**: Each test should be independent and not rely on state left by other tests.

2. **Cleanup**: If a test modifies global state (files, environment variables), make sure to clean it up in the teardown.

3. **Reproducibility**: Tests should be deterministic - same result every time.

4. **Clarity**: Test names should clearly describe what is being tested and under what conditions.

5. **Documentation**: Include docstrings in your tests to explain their purpose and any important details.

## KMC-Specific Tests

### Contextual Variable Tests

```python
def test_contextual_variable_resolution():
    parser = KMCParser()
    parser.register_context_handler("project", lambda var: "Demo" if var == "name" else f"<project:{var}>")
    
    result = parser.process("Project: [[project:name]]")
    assert result == "Project: Demo"
```

### Metadata Variable Tests

```python
def test_metadata_variable_resolution():
    parser = KMCParser()
    parser.register_metadata_handler("doc", lambda var: "1.0" if var == "version" else f"<doc:{var}>")
    
    result = parser.process("Version: [{doc:version}]")
    assert result == "Version: 1.0"
```

### Generative Variable Tests

```python
def test_generative_variable_with_kmc_definition():
    parser = KMCParser()
    
    # Register a test generative handler
    def test_ai_handler(var):
        if var.name == "extract_title" and var.prompt and "content" in var.prompt:
            return "Extracted Title"
        return "<generated>"
    
    parser.register_generative_handler("ai:gpt4", test_ai_handler)
    
    # Document with KMC definition and referenced metadata variable
    content = """
    # Test Document
    
    [{doc:title}]
    
    <!-- KMC_DEFINITION FOR [{doc:title}]:
    GENERATIVE_SOURCE = {{ai:gpt4:extract_title}}
    PROMPT = "Extract a title from the following content: This is a test content"
    -->
    """
    
    result = parser.process(content)
    assert "Extracted Title" in result
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-mock documentation](https://pytest-mock.readthedocs.io/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
