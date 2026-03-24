# src/modbus/client.py
# Python 3.11+
# Для библиотеки: pymodbus >= 3.6.0
import asyncio
from typing import Optional, List, Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from src.utils.logger import logger
from src.config.settings import config

class ModbusPLC:
    """
    Асинхронный клиент для работы с Modbus TCP ПЛК110.
    """
    
    # Константы
    DEFAULT_PORT = 502
    DEFAULT_TIMEOUT = 3.0
    DEFAULT_RETRIES = 3
    DEFAULT_DEVICE_ID = 1
    
    def __init__(self):
        """Инициализация клиента."""
        self.host: str = config.get_str("plc.host", "10.77.151.21")
        self.port: int = config.get_int("plc.port", self.DEFAULT_PORT)
        self.timeout: float = config.get_float("plc.timeout", self.DEFAULT_TIMEOUT)
        self.retries: int = config.get_int("plc.retries", self.DEFAULT_RETRIES)
        self.device_id: int = config.get_int("plc.device_id", self.DEFAULT_DEVICE_ID)
        
        self.client: Optional[AsyncModbusTcpClient] = None
        self._connected: bool = False
        self._lock = asyncio.Lock()
        
        # Статистика
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.last_error: Optional[str] = None
    
    async def connect(self) -> bool:
        """Установка соединения с ПЛК."""
        async with self._lock:
            if self.client and self._connected:
                return True
            
            logger.info(f"Подключение к Modbus TCP {self.host}:{self.port}")
            
            try:
                self.client = AsyncModbusTcpClient(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout
                )
                self._connected = await self.client.connect()
                
                if self._connected:
                    logger.info(f"Подключено к Modbus TCP {self.host}:{self.port}")
                else:
                    logger.error(f"Ошибка подключения Modbus TCP: не удалось подключиться")
                
                return self._connected
                
            except Exception as e:
                logger.error(f"Ошибка подключения Modbus TCP: {e}")
                self._connected = False
                return False
    
    async def disconnect(self):
        """Закрытие соединения."""
        async with self._lock:
            if self.client:
                self.client.close()
                self._connected = False
                logger.info(f"Отключено от Modbus TCP {self.host}:{self.port}")
    
    async def is_connected(self) -> bool:
        """Проверка состояния соединения."""
        return self._connected and self.client is not None and self.client.connected
    
    async def _execute_request(self, request_func, *args, **kwargs) -> Optional[Any]:
        """
        Выполнение запроса с обработкой ошибок и блокировкой.
        """
        async with self._lock:
            if not await self.is_connected():
                logger.error("Нет соединения с ПЛК")
                return None
            
            if self.client is None:
                logger.error("Клиент не инициализирован")
                return None
            
            self.total_requests += 1
            
            for attempt in range(self.retries):
                try:
                    response = await request_func(*args, **kwargs)
                    
                    if response is None:
                        logger.error("Получен пустой ответ")
                        continue
                    
                    if hasattr(response, 'isError') and response.isError():
                        logger.error(f"Ошибка Modbus: {response}")
                        self.failed_requests += 1
                        self.last_error = str(response)
                        continue
                    
                    self.successful_requests += 1
                    return response
                    
                except ModbusException as e:
                    logger.error(f"Исключение Modbus (попытка {attempt + 1}/{self.retries}): {e}")
                    self.last_error = str(e)
                    if attempt < self.retries - 1:
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    logger.error(f"Неизвестная ошибка: {e}")
                    self.last_error = str(e)
                    break
            
            self.failed_requests += 1
            return None
    
    # ========== HOLDING REGISTERS (FC 03/06/16) ==========
    
    async def read_registers(self, address: int, count: int, 
                            device_id: Optional[int] = None) -> Optional[List[int]]:
        """
        Чтение holding registers (FC 03).
        
        Args:
            address: Modbus адрес регистра (например, 40000, 40001)
            count: Количество регистров
            device_id: ID устройства (по умолчанию self.device_id)
        
        Returns:
            Список значений или None при ошибке
        """
        dev_id = device_id if device_id is not None else self.device_id
        logger.debug(f"Чтение регистров: FC 03, device={dev_id}, addr={address}, count={count}")
        
        if self.client is None:
            logger.error("Клиент не инициализирован")
            return None
        
        response = await self._execute_request(
            self.client.read_holding_registers,
            address=address,
            count=count,
            device_id=dev_id
        )
        
        if response and hasattr(response, 'registers'):
            logger.debug(f"Прочитано {count} регистров: {response.registers}")
            return response.registers
        
        logger.error(f"Ошибка чтения регистров: addr={address}, count={count}")
        return None
    
    async def write_register(self, address: int, value: int,
                            device_id: Optional[int] = None) -> bool:
        """
        Запись одного holding register (FC 06).
        
        Args:
            address: Modbus адрес регистра (например, 40000, 40001)
            value: Значение для записи
            device_id: ID устройства
        
        Returns:
            True при успехе, иначе False
        """
        dev_id = device_id if device_id is not None else self.device_id
        logger.debug(f"Запись регистра: FC 06, device={dev_id}, addr={address}, value={value}")
        
        if self.client is None:
            logger.error("Клиент не инициализирован")
            return False
        
        response = await self._execute_request(
            self.client.write_register,
            address=address,
            value=value,
            device_id=dev_id
        )
        
        if response:
            logger.debug(f"Регистр {address} записан: {value}")
            return True
        
        logger.error(f"Ошибка записи регистра: addr={address}, value={value}")
        return False
    
    async def write_registers(self, address: int, values: List[int],
                             device_id: Optional[int] = None) -> bool:
        """
        Запись нескольких holding registers (FC 16).
        
        Args:
            address: Modbus адрес первого регистра
            values: Список значений
            device_id: ID устройства
        
        Returns:
            True при успехе, иначе False
        """
        dev_id = device_id if device_id is not None else self.device_id
        logger.debug(f"Запись {len(values)} регистров: FC 16, device={dev_id}, addr={address}, values={values}")
        
        if self.client is None:
            logger.error("Клиент не инициализирован")
            return False
        
        response = await self._execute_request(
            self.client.write_registers,
            address=address,
            values=values,
            device_id=dev_id
        )
        
        if response:
            logger.debug(f"Записано {len(values)} регистров по адресу {address}")
            return True
        
        logger.error(f"Ошибка записи регистров: addr={address}")
        return False
    
    # ========== DISCRETE INPUTS (FC 02) ==========
    
    async def read_discrete_inputs(self, address: int, count: int,
                                   device_id: Optional[int] = None) -> Optional[List[int]]:
        """
        Чтение дискретных входов (FC 02).
        
        Args:
            address: Modbus адрес входа (например, 10001, 10002)
            count: Количество входов
            device_id: ID устройства
        
        Returns:
            Список int значений (0/1) или None при ошибке
        """
        dev_id = device_id if device_id is not None else self.device_id
        logger.debug(f"Чтение дискретных входов: FC 02, device={dev_id}, addr={address}, count={count}")
        
        if self.client is None:
            logger.error("Клиент не инициализирован")
            return None
        
        response = await self._execute_request(
            self.client.read_discrete_inputs,
            address=address,
            count=count,
            device_id=dev_id
        )
        
        if response and hasattr(response, 'bits'):
            int_bits = [1 if b else 0 for b in response.bits]
            logger.debug(f"Прочитано {count} дискретных входов: {int_bits}")
            return int_bits
        
        logger.error(f"Ошибка чтения дискретных входов: addr={address}")
        return None
    
    # ========== COILS (FC 01/05) ==========
    
    async def read_coils(self, address: int, count: int,
                        device_id: Optional[int] = None) -> Optional[List[int]]:
        """
        Чтение катушек (FC 01).
        
        Args:
            address: Modbus адрес катушки (например, 1, 2)
            count: Количество катушек
            device_id: ID устройства
        
        Returns:
            Список int значений (0/1) или None при ошибке
        """
        dev_id = device_id if device_id is not None else self.device_id
        logger.debug(f"Чтение coils: FC 01, device={dev_id}, addr={address}, count={count}")
        
        if self.client is None:
            logger.error("Клиент не инициализирован")
            return None
        
        response = await self._execute_request(
            self.client.read_coils,
            address=address,
            count=count,
            device_id=dev_id
        )
        
        if response and hasattr(response, 'bits'):
            int_bits = [1 if b else 0 for b in response.bits]
            logger.debug(f"Прочитано {count} coils: {int_bits}")
            return int_bits
        
        logger.error(f"Ошибка чтения coils: addr={address}")
        return None
    
    async def write_coil(self, address: int, value: bool,
                        device_id: Optional[int] = None) -> bool:
        """
        Запись одной катушки (FC 05).
        
        Args:
            address: Modbus адрес катушки
            value: Значение для записи (True/False или 1/0)
            device_id: ID устройства
        
        Returns:
            True при успехе, иначе False
        """
        dev_id = device_id if device_id is not None else self.device_id
        bool_value = bool(value)
        logger.debug(f"Запись coil: FC 05, device={dev_id}, addr={address}, value={1 if bool_value else 0}")
        
        if self.client is None:
            logger.error("Клиент не инициализирован")
            return False
        
        response = await self._execute_request(
            self.client.write_coil,
            address=address,
            value=bool_value,
            device_id=dev_id
        )
        
        if response:
            logger.debug(f"Coil {address} записан: {1 if bool_value else 0}")
            return True
        
        logger.error(f"Ошибка записи coil: addr={address}")
        return False