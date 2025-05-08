"""
API Plugin - Plugin de ejemplo para KMC Parser que integra APIs externas
"""
from typing import Dict, Any, Optional
import logging
import json
import os

from kmc_parser.extensions.plugin_base import KMCPlugin
from kmc_parser.handlers.base import GenerativeHandler, generative_handler
from kmc_parser.models import GenerativeVariable
from kmc_parser.core.registry import registry


class WeatherAPIHandler(GenerativeHandler):
    """
    Handler para obtener información del clima a través de una API externa.
    
    Este handler procesará variables como {{api:weather:ciudad}} en documentos KMC.
    """
    __kmc_handler_type__ = "generative"
    __kmc_var_type__ = "api:weather"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el handler de clima.
        
        Args:
            config: Configuración del handler, puede incluir:
                - api_key: Clave de API del servicio de clima
                - units: Unidades de medida (metric, imperial)
                - lang: Idioma de las respuestas
        """
        super().__init__(config)
        self.api_key = config.get("api_key", "demo_key")
        self.units = config.get("units", "metric")
        self.lang = config.get("lang", "es")
        self.logger = logging.getLogger("kmc.handlers.weather")
        
    def _generate_content(self, var: GenerativeVariable) -> str:
        """
        Obtiene datos de clima para una ciudad.
        
        Args:
            var: Variable generativa que contiene la ciudad o ubicación
            
        Returns:
            Datos de clima formateados
        """
        # En producción, aquí se haría una llamada a la API real
        # Por ahora, simulamos respuestas para demostrar el concepto
        location = var.name or "desconocida"
        if var.prompt:
            # Si hay un prompt, buscamos la ciudad en él
            import re
            match = re.search(r'ciudad[:\s]+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)', var.prompt, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
        
        return self._simulate_weather_data(location)
    
    def _simulate_weather_data(self, location: str) -> str:
        """
        Simula datos de clima para demostración.
        
        Args:
            location: Ciudad o ubicación
            
        Returns:
            Datos de clima simulados en formato texto
        """
        # Simulación básica - en producción se consultaría una API real
        weather_data = {
            "madrid": {
                "temp": 22.5,
                "humidity": 45,
                "description": "Soleado",
                "wind_speed": 10.2
            },
            "barcelona": {
                "temp": 25.1,
                "humidity": 60,
                "description": "Parcialmente nublado",
                "wind_speed": 8.5
            },
            "santiago": {
                "temp": 18.7,
                "humidity": 72,
                "description": "Nublado",
                "wind_speed": 5.3
            },
            "bogotá": {
                "temp": 16.2,
                "humidity": 68,
                "description": "Lluvia ligera",
                "wind_speed": 6.7
            },
            "ciudad de méxico": {
                "temp": 23.8,
                "humidity": 40,
                "description": "Soleado con nubes dispersas",
                "wind_speed": 7.2
            }
        }
        
        location_lower = location.lower()
        if location_lower in weather_data:
            data = weather_data[location_lower]
            units_symbol = "°C" if self.units == "metric" else "°F"
            
            return f"""### Clima actual en {location.title()}

- **Temperatura**: {data['temp']}{units_symbol}
- **Humedad**: {data['humidity']}%
- **Condición**: {data['description']}
- **Velocidad del viento**: {data['wind_speed']} km/h

*Datos simulados para demostración. En un entorno de producción, estos datos serían obtenidos de una API de clima en tiempo real.*
"""
        else:
            return f"""### Clima para {location}

Lo siento, no hay datos disponibles para esta ubicación.

*Nota: Este es un handler simulado. En producción, se consultaría una API real de clima.*
"""


class StockAPIHandler(GenerativeHandler):
    """
    Handler para obtener información financiera a través de una API externa.
    
    Este handler procesará variables como {{api:stock:AAPL}} en documentos KMC.
    """
    __kmc_handler_type__ = "generative"
    __kmc_var_type__ = "api:stock"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el handler de información bursátil.
        
        Args:
            config: Configuración del handler, puede incluir:
                - api_key: Clave de API del servicio financiero
                - currency: Moneda para los precios
        """
        super().__init__(config)
        self.api_key = config.get("api_key", "demo_key")
        self.currency = config.get("currency", "USD")
        self.logger = logging.getLogger("kmc.handlers.stock")
        
    def _generate_content(self, var: GenerativeVariable) -> str:
        """
        Obtiene datos de mercado para un símbolo bursátil.
        
        Args:
            var: Variable generativa que contiene el símbolo o empresa
            
        Returns:
            Datos financieros formateados
        """
        # Obtener el símbolo de la variable
        symbol = var.name.upper() if var.name else "UNKNOWN"
        
        return self._simulate_stock_data(symbol)
    
    def _simulate_stock_data(self, symbol: str) -> str:
        """
        Simula datos financieros para demostración.
        
        Args:
            symbol: Símbolo bursátil
            
        Returns:
            Datos financieros simulados en formato texto
        """
        # Simulación básica - en producción se consultaría una API real
        stock_data = {
            "AAPL": {
                "price": 182.63,
                "change": 1.25,
                "change_percent": 0.69,
                "volume": 45687321,
                "company": "Apple Inc."
            },
            "MSFT": {
                "price": 325.48,
                "change": -2.15,
                "change_percent": -0.66,
                "volume": 28943156,
                "company": "Microsoft Corporation"
            },
            "GOOGL": {
                "price": 133.95,
                "change": 0.87,
                "change_percent": 0.65,
                "volume": 19764532,
                "company": "Alphabet Inc."
            },
            "AMZN": {
                "price": 128.91,
                "change": -0.54,
                "change_percent": -0.42,
                "volume": 32145687,
                "company": "Amazon.com, Inc."
            }
        }
        
        if symbol in stock_data:
            data = stock_data[symbol]
            change_symbol = "+" if data['change'] > 0 else ""
            
            return f"""### Datos financieros de {data['company']} ({symbol})

- **Precio actual**: {self.currency} {data['price']}
- **Cambio**: {change_symbol}{data['change']} ({change_symbol}{data['change_percent']}%)
- **Volumen**: {data['volume']:,}

*Datos simulados para demostración. En un entorno de producción, estos datos serían obtenidos de una API financiera en tiempo real.*

#### Nota importante
Esta información no constituye asesoramiento financiero y está destinada únicamente para fines informativos.
"""
        else:
            return f"""### Datos financieros para {symbol}

No se encontró información para el símbolo bursátil **{symbol}**.

*Nota: Este es un handler simulado. En producción, se consultaría una API real financiera.*
"""


class ExternalAPIsPlugin(KMCPlugin):
    """
    Plugin que añade soporte para APIs externas en documentos KMC,
    como información meteorológica, datos financieros, etc.
    """
    __version__ = "0.1.0"
    
    def initialize(self) -> bool:
        """
        Inicializa el plugin y registra los handlers.
        
        Returns:
            True si la inicialización fue exitosa, False en caso contrario
        """
        self.logger.info(f"Inicializando plugin {self.name} v{self.version}")
        
        # Registrar handlers de API
        handlers_count = self.register_handlers()
        
        self.logger.info(f"Plugin {self.name} inicializado correctamente. "
                         f"Se registraron {handlers_count} handlers.")
        return True
    
    def register_handlers(self) -> int:
        """
        Registra los handlers proporcionados por este plugin.
        
        Returns:
            Número de handlers registrados
        """
        count = 0
        
        # Configuración para los handlers
        weather_config = {
            "api_key": self.config.get("weather_api_key"),
            "units": self.config.get("weather_units", "metric"),
            "lang": self.config.get("weather_lang", "es")
        }
        
        stock_config = {
            "api_key": self.config.get("stock_api_key"),
            "currency": self.config.get("currency", "USD")
        }
        
        # Registrar handlers
        try:
            # Weather API Handler
            weather_handler = WeatherAPIHandler(config=weather_config)
            registry.register_generative_handler("api:weather", weather_handler)
            count += 1
            
            # Stock API Handler
            stock_handler = StockAPIHandler(config=stock_config)
            registry.register_generative_handler("api:stock", stock_handler)
            count += 1
            
        except Exception as e:
            self.logger.error(f"Error al registrar handlers: {str(e)}")
        
        return count