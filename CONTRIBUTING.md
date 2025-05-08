# Guía de Contribución | Contributing Guide

_Español_

¡Gracias por tu interés en contribuir a KMC! Esta guía te ayudará a configurar tu entorno de desarrollo y a conocer nuestro proceso de contribución.

## Configuración del Entorno

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/reevolutiva/kmc-parser.git
   cd kmc-parser
   ```

2. **Configurar un entorno virtual (recomendado)**

   ```bash
   # Con venv (Python 3.8+)
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   
   # Con conda
   conda create -n kmc-env python=3.10
   conda activate kmc-env
   ```

3. **Instalar dependencias de desarrollo**

   ```bash
   pip install -e ".[dev]"
   ```

## Estructura del Proyecto

- **kmc_parser/**: Código principal del proyecto
  - **core/**: Componentes centrales (registro, configuración)
  - **handlers/**: Implementaciones de handlers para diferentes tipos de variables
  - **extensions/**: Sistema de plugins y extensiones
  - **integrations/**: Integraciones con sistemas externos
  - **models.py**: Definición de modelos de datos
  - **parser.py**: Parser principal de KMC
- **examples/**: Ejemplos de uso
- **tests/**: Pruebas unitarias y de integración
- **docs/**: Documentación

## Flujo de Trabajo para Contribuciones

1. **Crear un issue**
   
   Antes de comenzar cualquier trabajo significativo, crea un issue para discutir la propuesta, el bug o la mejora.

2. **Bifurcar (Fork) el repositorio**

   Crea tu propia copia del repositorio en GitHub.

3. **Crear una rama (branch)**

   ```bash
   git checkout -b feature/mi-caracteristica
   # o
   git checkout -b fix/mi-correccion
   ```

4. **Realizar cambios**

   Implementa tus cambios siguiendo las convenciones de estilo del proyecto.

5. **Escribir pruebas**

   Asegúrate de que tus cambios incluyan pruebas adecuadas.

6. **Ejecutar las pruebas**

   ```bash
   pytest
   ```

7. **Formatear el código**

   ```bash
   # Limpiar el código con black
   black kmc_parser tests
   
   # Ordenar imports con isort
   isort kmc_parser tests
   ```

8. **Comprobar tipos**

   ```bash
   mypy kmc_parser
   ```

9. **Commit y Push**

   ```bash
   git add .
   git commit -m "Descripción detallada del cambio"
   git push origin feature/mi-caracteristica
   ```

10. **Crear un Pull Request (PR)**

    Crea un PR a través de GitHub hacia la rama principal del repositorio original.

## Convenciones de Código

- Seguimos la guía de estilo [PEP 8](https://pep8.org/) para Python
- Utilizamos [Black](https://github.com/psf/black) para el formateo automático (configuración en pyproject.toml)
- Nombres de clases en PascalCase (ej. `ContextVariable`)
- Nombres de funciones y variables en snake_case (ej. `parse_variables`)
- Usamos docstrings en formato Google para la documentación

## Pruebas

Es esencial incluir pruebas para cualquier nueva funcionalidad o corrección de errores:

- Las pruebas unitarias se escriben con el módulo `unittest` o `pytest`
- Las pruebas se almacenan en el directorio `tests/`
- Para cada archivo en `kmc_parser/`, debe haber un archivo de prueba correspondiente en `tests/`

## Documentación

Si tus cambios requieren actualización de la documentación:

1. Actualiza los comentarios y docstrings en el código
2. Actualiza los archivos de markdown en la carpeta `docs/` si es necesario
3. Actualiza el README.md si estás introduciendo cambios significativos

## Proceso de Revisión

Una vez que hayas enviado un PR, los mantenedores del proyecto revisarán tu código. Este proceso puede implicar varios ciclos de retroalimentación y ajustes.

## Lineamientos de Contenido

- **Bilingüe**: Todo el contenido público (docstrings, comentarios, documentación) debe estar disponible tanto en español como en inglés cuando sea posible.
- **Claridad**: Usa nombres de variables y funciones descriptivos.
- **Comentarios**: Añade comentarios para explicar "por qué", no "qué" o "cómo" (el código debería ser autoexplicativo).

## Reporte de Bugs

Si encuentras un error, por favor crea un issue incluyendo:

- Descripción clara y concisa del error
- Pasos para reproducir el comportamiento
- Comportamiento esperado vs. real
- Capturas de pantalla si aplica
- Información del entorno: sistema operativo, versión de Python, etc.

## Contacto

Si tienes preguntas sobre cómo contribuir, puedes contactarnos en info@kimfe.com.

¡Gracias por contribuir a KMC!

---

_English_

Thank you for your interest in contributing to KMC! This guide will help you set up your development environment and understand our contribution process.

## Environment Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/reevolutiva/kmc-parser.git
   cd kmc-parser
   ```

2. **Set up a virtual environment (recommended)**

   ```bash
   # With venv (Python 3.8+)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # With conda
   conda create -n kmc-env python=3.10
   conda activate kmc-env
   ```

3. **Install development dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

## Project Structure

- **kmc_parser/**: Main project code
  - **core/**: Core components (registry, configuration)
  - **handlers/**: Handlers implementations for different variable types
  - **extensions/**: Plugin system and extensions
  - **integrations/**: Integrations with external systems
  - **models.py**: Data model definitions
  - **parser.py**: Main KMC parser
- **examples/**: Usage examples
- **tests/**: Unit and integration tests
- **docs/**: Documentation

## Contribution Workflow

1. **Create an issue**
   
   Before starting any significant work, create an issue to discuss the proposal, bug, or improvement.

2. **Fork the repository**

   Create your own copy of the repository on GitHub.

3. **Create a branch**

   ```bash
   git checkout -b feature/my-feature
   # or
   git checkout -b fix/my-bugfix
   ```

4. **Make changes**

   Implement your changes following the project's style conventions.

5. **Write tests**

   Make sure your changes include appropriate tests.

6. **Run tests**

   ```bash
   pytest
   ```

7. **Format code**

   ```bash
   # Clean code with black
   black kmc_parser tests
   
   # Sort imports with isort
   isort kmc_parser tests
   ```

8. **Check types**

   ```bash
   mypy kmc_parser
   ```

9. **Commit and Push**

   ```bash
   git add .
   git commit -m "Detailed description of the change"
   git push origin feature/my-feature
   ```

10. **Create a Pull Request (PR)**

    Create a PR through GitHub to the main branch of the original repository.

## Code Conventions

- We follow the [PEP 8](https://pep8.org/) style guide for Python
- We use [Black](https://github.com/psf/black) for automatic formatting (configuration in pyproject.toml)
- Class names in PascalCase (e.g., `ContextVariable`)
- Function and variable names in snake_case (e.g., `parse_variables`)
- We use Google format docstrings for documentation

## Testing

It's essential to include tests for any new functionality or bug fixes:

- Unit tests are written with the `unittest` module or `pytest`
- Tests are stored in the `tests/` directory
- For each file in `kmc_parser/`, there should be a corresponding test file in `tests/`

## Documentation

If your changes require documentation updates:

1. Update comments and docstrings in the code
2. Update markdown files in the `docs/` folder if necessary
3. Update README.md if you're introducing significant changes

## Review Process

Once you've submitted a PR, project maintainers will review your code. This process may involve several cycles of feedback and adjustments.

## Content Guidelines

- **Bilingual**: All public content (docstrings, comments, documentation) should be available in both Spanish and English when possible.
- **Clarity**: Use descriptive variable and function names.
- **Comments**: Add comments to explain "why", not "what" or "how" (the code should be self-explanatory).

## Bug Reports

If you find a bug, please create an issue including:

- Clear and concise description of the bug
- Steps to reproduce the behavior
- Expected vs. actual behavior
- Screenshots if applicable
- Environment information: operating system, Python version, etc.

## Contact

If you have questions about how to contribute, you can contact us at info@kimfe.com.

Thank you for contributing to KMC!
