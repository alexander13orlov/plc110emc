# src/config/settings.py
# Python 3.11+
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, cast

class Config:
    """
    Загрузка и доступ к конфигурации из YAML.
    """
    
    def __init__(self, config_path: str = "config/default.yaml"):
        """
        Загрузка конфигурации.
        
        Args:
            config_path: Путь к YAML файлу конфигурации
        """
        self._config: Dict[str, Any] = self._load_config(config_path)
    
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Загрузка YAML файла."""
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"Файл конфигурации не найден: {path}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Приведение к словарю
        if data is None:
            return {}
        if isinstance(data, dict):
            return cast(Dict[str, Any], data)
        # Если корневой элемент не словарь (например, список), оборачиваем
        return {"_root": data}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получение значения по ключу (поддерживает вложенность через точки).
        
        Args:
            key: Ключ с точками (например, "plc.host")
            default: Значение по умолчанию
        
        Returns:
            Значение или default при отсутствии
        """
        keys = key.split(".")
        value: Any = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default
    
    def get_str(self, key: str, default: str = "") -> str:
        """Получение строкового значения."""
        value = self.get(key, default)
        if value is None:
            return default
        return str(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Получение целочисленного значения."""
        value = self.get(key, default)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Получение значения с плавающей точкой."""
        value = self.get(key, default)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Получение булевого значения."""
        value = self.get(key, default)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            return default
    
    @property
    def plc_config(self) -> Dict[str, Any]:
        """Конфигурация подключения к ПЛК."""
        return self._config.get("plc", {})
    
    @property
    def modbus_mapping(self) -> Dict[str, Any]:
        """Карта регистров Modbus."""
        return self._config.get("modbus_mapping", {})

# Глобальный экземпляр конфигурации
config = Config()