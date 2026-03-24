# tests/test_modbus.py
# Python 3.11+
import asyncio
import pytest

from src.modbus.client import ModbusPLC
from src.config.settings import config
from src.utils.logger import logger

# Константы из конфигурации
DO_START = config.get_int("modbus_mapping.do.start_address", 40000)
DO_FAST_START = config.get_int("modbus_mapping.do.fast_start", 40020)
DO_FAST_COUNT = config.get_int("modbus_mapping.do.fast_count", 4)

DI_START = config.get_int("modbus_mapping.di.start_address", 10001)
DI_FAST_START = config.get_int("modbus_mapping.di.fast_start", 10001)
DI_FAST_COUNT = config.get_int("modbus_mapping.di.fast_count", 4)
DI_COUNT = config.get_int("modbus_mapping.di.count", 36)

@pytest.mark.asyncio
async def test_connection():
    """Тест подключения к ПЛК."""
    plc = ModbusPLC()
    try:
        connected = await plc.connect()
        assert connected is True
    finally:
        await plc.disconnect()

@pytest.mark.asyncio
async def test_read_single_do():
    """Тест чтения одного DO регистра."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        values = await plc.read_registers(DO_START, 1)
        
        assert values is not None
        assert len(values) == 1
        logger.info(f"DO {DO_START}: {values}")
    finally:
        await plc.disconnect()

@pytest.mark.asyncio
async def test_read_multiple_do_slow_only():
    """
    Чтение только медленных DO.
    Медленные DO: от DO_START до DO_FAST_START - 1
    """
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        slow_count = DO_FAST_START - DO_START
        values = await plc.read_registers(DO_START, slow_count)
        
        assert values is not None
        assert len(values) == slow_count
        logger.info(f"DO {DO_START}-{DO_FAST_START-1} (медленные): {values}")
    finally:
        await plc.disconnect()

@pytest.mark.asyncio
async def test_write_single_do():
    """Тест записи DO1."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        test_value = 1
        
        # Запись
        success = await plc.write_register(DO_START, test_value)
        assert success is True
        
        # Задержка для физического переключения (~1 сек)
        await asyncio.sleep(1.1)
        
        # Проверка
        values = await plc.read_registers(DO_START, 1)
        assert values is not None
        assert values[0] == test_value
        logger.info(f"DO {DO_START} записан: {values}")
    finally:
        await plc.disconnect()

@pytest.mark.asyncio
async def test_read_single_di():
    """Тест чтения DI5 (адрес 10005)."""
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        di_address = 10005
        bits = await plc.read_discrete_inputs(di_address, 1)
        
        assert bits is not None
        # Modbus возвращает минимум 1 байт (8 бит) даже при запросе 1 бита
        # Поэтому проверяем, что первый бит соответствует ожидаемому
        assert len(bits) >= 1
        logger.info(f"DI {di_address}: {bits[:1]} (получено {len(bits)} бит)")
    finally:
        await plc.disconnect()

@pytest.mark.asyncio
async def test_read_multiple_di_slow_only():
    """
    Чтение только медленных DI.
    Медленные DI: от 10005 до 10036
    """
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        slow_start = 10005
        slow_count = 32  # 10005-10036
        
        bits = await plc.read_discrete_inputs(slow_start, slow_count)
        
        assert bits is not None
        # Modbus возвращает количество бит, кратное 8
        assert len(bits) >= slow_count
        # Преобразование bool в int для единообразия вывода
        int_bits = [1 if b else 0 for b in bits[:slow_count]]
        logger.info(f"DI {slow_start}-{slow_start + slow_count - 1} (медленные): {int_bits}")
    finally:
        await plc.disconnect()
@pytest.mark.skip(reason="Быстрые DI (10001-10004) отключены в ПЛК")
@pytest.mark.asyncio
async def test_read_multiple_di_fast_only():
    """
    Чтение только быстрых DI.
    Быстрые DI: от 10001 до 10004
    """
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        fast_start = 10001
        fast_count = 4
        
        bits = await plc.read_discrete_inputs(fast_start, fast_count)
        
        assert bits is not None
        # Modbus возвращает количество бит, кратное 8
        assert len(bits) >= fast_count
        # Преобразование bool в int для единообразия вывода
        int_bits = [1 if b else 0 for b in bits[:fast_count]]
        logger.info(f"DI {fast_start}-{fast_start + fast_count - 1} (быстрые): {int_bits}")
    finally:
        await plc.disconnect()

@pytest.mark.asyncio
async def test_read_all_do():
    """
    Чтение всех DO (медленные + быстрые) отдельными запросами.
    """
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Медленные DO: 40000-40019
        slow_count = 20
        slow_values = await plc.read_registers(40000, slow_count)
        assert slow_values is not None
        
        # Быстрые DO: 40020-40023
        fast_count = 4
        fast_values = await plc.read_registers(40020, fast_count)
        assert fast_values is not None
        
        all_values = slow_values + fast_values
        logger.info(f"Все DO (40000-40023): {all_values}")
    finally:
        await plc.disconnect()
@pytest.mark.skip(reason="Быстрые DI (10001-10004) отключены в ПЛК")
@pytest.mark.asyncio
async def test_read_all_di():
    """
    Чтение всех DI (быстрые + медленные) отдельными запросами.
    """
    plc = ModbusPLC()
    try:
        await plc.connect()
        
        # Быстрые DI: 10001-10004
        fast_count = 4
        fast_bits = await plc.read_discrete_inputs(10001, fast_count)
        assert fast_bits is not None
        
        # Медленные DI: 10005-10036
        slow_start = 10005
        slow_count = 32
        slow_bits = await plc.read_discrete_inputs(slow_start, slow_count)
        assert slow_bits is not None
        
        # Преобразование bool в int
        fast_ints = [1 if b else 0 for b in fast_bits[:fast_count]]
        slow_ints = [1 if b else 0 for b in slow_bits[:slow_count]]
        all_bits = fast_ints + slow_ints
        
        logger.info(f"Все DI (10001-10036): {all_bits}")
    finally:
        await plc.disconnect()