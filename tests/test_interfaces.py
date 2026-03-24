# tests/test_interfaces.py
# Python 3.11+
# Тестирование интерфейсов RS-485, RS-232 и подтяжек
import asyncio
import pytest

from src.modbus.client import ModbusPLC
from src.config.settings import config
from src.utils.logger import logger

# Константы из конфигурации
# RS-485 COM1
RS485_COM1_ENABLE = config.get_int("modbus_mapping.rs485_com1.enable", 40100)
RS485_COM1_SLAVE_ID = config.get_int("modbus_mapping.rs485_com1.slave_id", 40102)
RS485_COM1_FUNCTION_CODE = config.get_int("modbus_mapping.rs485_com1.function_code", 40103)
RS485_COM1_REGISTER_ADDRESS = config.get_int("modbus_mapping.rs485_com1.register_address", 40104)
RS485_COM1_SUCCESS_PERCENT = config.get_int("modbus_mapping.rs485_com1.success_percent", 40110)

# RS-485 COM2
RS485_COM2_ENABLE = config.get_int("modbus_mapping.rs485_com2.enable", 40112)
RS485_COM2_SLAVE_ID = config.get_int("modbus_mapping.rs485_com2.slave_id", 40114)
RS485_COM2_SUCCESS_PERCENT = config.get_int("modbus_mapping.rs485_com2.success_percent", 40122)

# RS-232 COM4
RS232_COM4_ENABLE = config.get_int("modbus_mapping.rs232_com4.enable", 40300)
RS232_COM4_SLAVE_ID = config.get_int("modbus_mapping.rs232_com4.slave_id", 40302)
RS232_COM4_SUCCESS_PERCENT = config.get_int("modbus_mapping.rs232_com4.success_percent", 40310)

# Подтяжки (Coils)
PULLUP_COM1 = config.get_int("modbus_mapping.pullup.com1", 1)
PULLUP_COM2 = config.get_int("modbus_mapping.pullup.com2", 2)


# ==================== ТЕСТЫ RS-485 COM1 ====================

@pytest.mark.asyncio
async def test_rs485_com1_read_config():
    """Тест чтения конфигурации RS-485 COM1."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Чтение Slave ID
        slave_id = await plc.read_registers(RS485_COM1_SLAVE_ID, 1)
        assert slave_id is not None
        logger.info(f"RS-485 COM1 Slave ID: {slave_id[0]}")
        
        # Чтение Function Code
        func_code = await plc.read_registers(RS485_COM1_FUNCTION_CODE, 1)
        assert func_code is not None
        logger.info(f"RS-485 COM1 Function Code: {func_code[0]}")
        
        # Чтение Register Address
        reg_addr = await plc.read_registers(RS485_COM1_REGISTER_ADDRESS, 1)
        assert reg_addr is not None
        logger.info(f"RS-485 COM1 Register Address: {reg_addr[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_rs485_com1_enable_disable():
    """Тест включения/выключения опроса RS-485 COM1."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Включение опроса
        logger.info("Включение опроса RS-485 COM1")
        success = await plc.write_register(RS485_COM1_ENABLE, 1)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_registers(RS485_COM1_ENABLE, 1)
        assert status is not None
        assert status[0] == 1
        logger.info(f"RS-485 COM1 Enable: {status[0]}")
        
        # Выключение опроса
        logger.info("Выключение опроса RS-485 COM1")
        success = await plc.write_register(RS485_COM1_ENABLE, 0)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_registers(RS485_COM1_ENABLE, 1)
        assert status is not None
        assert status[0] == 0
        logger.info(f"RS-485 COM1 Enable: {status[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_rs485_com1_statistics():
    """Тест чтения статистики RS-485 COM1."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Включение опроса для накопления статистики
        await plc.write_register(RS485_COM1_ENABLE, 1)
        await asyncio.sleep(2)
        
        # Чтение процента успешных запросов
        success_percent = await plc.read_registers(RS485_COM1_SUCCESS_PERCENT, 1)
        assert success_percent is not None
        logger.info(f"RS-485 COM1 Success Percent: {success_percent[0]}%")
        
        # Чтение кода последней ошибки
        last_error = await plc.read_registers(RS485_COM1_ENABLE + 9, 1)  # last_error = enable + 9
        if last_error:
            logger.info(f"RS-485 COM1 Last Error Code: {last_error[0]}")
        
        # Выключение опроса
        await plc.write_register(RS485_COM1_ENABLE, 0)
        
    finally:
        await plc.disconnect()


# ==================== ТЕСТЫ RS-485 COM2 ====================

@pytest.mark.asyncio
async def test_rs485_com2_read_config():
    """Тест чтения конфигурации RS-485 COM2."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Чтение Slave ID
        slave_id = await plc.read_registers(RS485_COM2_SLAVE_ID, 1)
        assert slave_id is not None
        logger.info(f"RS-485 COM2 Slave ID: {slave_id[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_rs485_com2_enable_disable():
    """Тест включения/выключения опроса RS-485 COM2."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Включение опроса
        logger.info("Включение опроса RS-485 COM2")
        success = await plc.write_register(RS485_COM2_ENABLE, 1)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_registers(RS485_COM2_ENABLE, 1)
        assert status is not None
        assert status[0] == 1
        logger.info(f"RS-485 COM2 Enable: {status[0]}")
        
        # Выключение опроса
        logger.info("Выключение опроса RS-485 COM2")
        success = await plc.write_register(RS485_COM2_ENABLE, 0)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_registers(RS485_COM2_ENABLE, 1)
        assert status is not None
        assert status[0] == 0
        logger.info(f"RS-485 COM2 Enable: {status[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_rs485_com2_statistics():
    """Тест чтения статистики RS-485 COM2."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Включение опроса для накопления статистики
        await plc.write_register(RS485_COM2_ENABLE, 1)
        await asyncio.sleep(2)
        
        # Чтение процента успешных запросов
        success_percent = await plc.read_registers(RS485_COM2_SUCCESS_PERCENT, 1)
        assert success_percent is not None
        logger.info(f"RS-485 COM2 Success Percent: {success_percent[0]}%")
        
        # Выключение опроса
        await plc.write_register(RS485_COM2_ENABLE, 0)
        
    finally:
        await plc.disconnect()


# ==================== ТЕСТЫ RS-232 COM4 ====================

@pytest.mark.asyncio
async def test_rs232_com4_read_config():
    """Тест чтения конфигурации RS-232 COM4."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Чтение Slave ID
        slave_id = await plc.read_registers(RS232_COM4_SLAVE_ID, 1)
        assert slave_id is not None
        logger.info(f"RS-232 COM4 Slave ID: {slave_id[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_rs232_com4_enable_disable():
    """Тест включения/выключения опроса RS-232 COM4."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Включение опроса
        logger.info("Включение опроса RS-232 COM4")
        success = await plc.write_register(RS232_COM4_ENABLE, 1)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_registers(RS232_COM4_ENABLE, 1)
        assert status is not None
        assert status[0] == 1
        logger.info(f"RS-232 COM4 Enable: {status[0]}")
        
        # Выключение опроса
        logger.info("Выключение опроса RS-232 COM4")
        success = await plc.write_register(RS232_COM4_ENABLE, 0)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_registers(RS232_COM4_ENABLE, 1)
        assert status is not None
        assert status[0] == 0
        logger.info(f"RS-232 COM4 Enable: {status[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_rs232_com4_statistics():
    """Тест чтения статистики RS-232 COM4."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Включение опроса для накопления статистики
        await plc.write_register(RS232_COM4_ENABLE, 1)
        await asyncio.sleep(2)
        
        # Чтение процента успешных запросов
        success_percent = await plc.read_registers(RS232_COM4_SUCCESS_PERCENT, 1)
        assert success_percent is not None
        logger.info(f"RS-232 COM4 Success Percent: {success_percent[0]}%")
        
        # Выключение опроса
        await plc.write_register(RS232_COM4_ENABLE, 0)
        
    finally:
        await plc.disconnect()


# ==================== ТЕСТЫ ПОДТЯЖЕК RS-485 ====================

        
   # ==================== ТЕСТЫ ПОДТЯЖЕК RS-485 ====================

@pytest.mark.asyncio
async def test_pullup_com1_read():
    """Тест чтения статуса подтяжки RS-485 COM1."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Чтение статуса подтяжки COM1 (coil)
        status = await plc.read_coils(PULLUP_COM1, 1)
        assert status is not None
        # Modbus возвращает минимум 1 байт (8 бит), берем первый бит
        assert len(status) >= 1
        logger.info(f"RS-485 COM1 Pull-up: {status[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_pullup_com1_enable_disable():
    """Тест включения/выключения подтяжки RS-485 COM1."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Включение подтяжки
        logger.info("Включение подтяжки RS-485 COM1")
        success = await plc.write_coil(PULLUP_COM1, True)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_coils(PULLUP_COM1, 1)
        assert status is not None
        assert status[0] == 1
        logger.info(f"RS-485 COM1 Pull-up: {status[0]}")
        
        # Выключение подтяжки
        logger.info("Выключение подтяжки RS-485 COM1")
        success = await plc.write_coil(PULLUP_COM1, False)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_coils(PULLUP_COM1, 1)
        assert status is not None
        assert status[0] == 0
        logger.info(f"RS-485 COM1 Pull-up: {status[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_pullup_com2_read():
    """Тест чтения статуса подтяжки RS-485 COM2."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Чтение статуса подтяжки COM2 (coil)
        status = await plc.read_coils(PULLUP_COM2, 1)
        assert status is not None
        # Modbus возвращает минимум 1 байт (8 бит), берем первый бит
        assert len(status) >= 1
        logger.info(f"RS-485 COM2 Pull-up: {status[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_pullup_com2_enable_disable():
    """Тест включения/выключения подтяжки RS-485 COM2."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Включение подтяжки
        logger.info("Включение подтяжки RS-485 COM2")
        success = await plc.write_coil(PULLUP_COM2, True)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_coils(PULLUP_COM2, 1)
        assert status is not None
        assert status[0] == 1
        logger.info(f"RS-485 COM2 Pull-up: {status[0]}")
        
        # Выключение подтяжки
        logger.info("Выключение подтяжки RS-485 COM2")
        success = await plc.write_coil(PULLUP_COM2, False)
        assert success is True
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        status = await plc.read_coils(PULLUP_COM2, 1)
        assert status is not None
        assert status[0] == 0
        logger.info(f"RS-485 COM2 Pull-up: {status[0]}")
        
    finally:
        await plc.disconnect()


@pytest.mark.asyncio
async def test_all_pullups_off():
    """Тест выключения всех подтяжек."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Выключение всех подтяжек
        await plc.write_coil(PULLUP_COM1, False)
        await plc.write_coil(PULLUP_COM2, False)
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        com1 = await plc.read_coils(PULLUP_COM1, 1)
        com2 = await plc.read_coils(PULLUP_COM2, 1)
        
        assert com1 is not None
        assert com2 is not None
        assert com1[0] == 0
        assert com2[0] == 0
        
        logger.info("Все подтяжки выключены")
        
    finally:
        await plc.disconnect()     
        
        
        
        
        
        
        
        
        
 # ==================== КОМБИНИРОВАННЫЕ ТЕСТЫ ====================

@pytest.mark.asyncio
async def test_all_interfaces_off():
    """Тест выключения всех интерфейсов."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Выключение всех интерфейсов
        await plc.write_register(RS485_COM1_ENABLE, 0)
        await plc.write_register(RS485_COM2_ENABLE, 0)
        await plc.write_register(RS232_COM4_ENABLE, 0)
        
        await asyncio.sleep(0.5)
        
        # Проверка статуса
        com1 = await plc.read_registers(RS485_COM1_ENABLE, 1)
        com2 = await plc.read_registers(RS485_COM2_ENABLE, 1)
        com4 = await plc.read_registers(RS232_COM4_ENABLE, 1)
        
        assert com1 is not None and com1[0] == 0
        assert com2 is not None and com2[0] == 0
        assert com4 is not None and com4[0] == 0
        
        logger.info("Все интерфейсы выключены")
        
    finally:
        await plc.disconnect()