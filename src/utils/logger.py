# src/utils/logger.py
# Python 3.11+
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(log_dir: str = "logs", level: int = logging.DEBUG) -> logging.Logger:
    """
    Настройка корневого логгера.
    
    Args:
        log_dir: Директория для файлов логов
        level: Уровень логирования
    
    Returns:
        Настроенный корневой логгер
    """
    # Создание директории для логов
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Корневой логгер
    logger = logging.getLogger("plc110")
    logger.setLevel(level)
    
    # Формат логов с миллисекундами
    # %f - микросекунды (6 цифр), обрезаем до 3 цифр для миллисекунд
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Обработчик консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Обработчик файла (ротация 10 МБ, 5 файлов)
    file_handler = RotatingFileHandler(
        log_path / "plc110.log",
        maxBytes=10_485_760,  # 10 МБ
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Глобальный логгер (инициализируется при импорте)
logger = setup_logger()