# src/main.py
# Python 3.11+
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modbus.client import ModbusPLC
from src.utils.logger import logger
from src.config.settings import config

async def main():
    """Точка входа для консольного тестирования."""
    logger.info("Запуск тестирования Modbus клиента")
    
    plc = ModbusPLC()
    
    # Получение адресов из конфигурации (используются напрямую)
    do_start = config.get_int("modbus_mapping.do.start_address", 40000)
    do_fast_start = config.get_int("modbus_mapping.do.fast_start", 40020)
    do_fast_count = config.get_int("modbus_mapping.do.fast_count", 4)
    
    di_start = config.get_int("modbus_mapping.di.start_address", 10001)
    di_fast_start = config.get_int("modbus_mapping.di.fast_start", 10001)
    di_fast_count = config.get_int("modbus_mapping.di.fast_count", 4)
    di_count = config.get_int("modbus_mapping.di.count", 36)
    
    try:
        if not await plc.connect():
            logger.error("Не удалось подключиться к ПЛК")
            return
        
        # Чтение медленных DO
        slow_do_count = do_fast_start - do_start
        slow_do_values = await plc.read_registers(do_start, slow_do_count)
        if slow_do_values:
            logger.info(f"DO {do_start}-{do_fast_start-1} (медленные): {slow_do_values}")
        
        # Чтение быстрых DO
        fast_do_values = await plc.read_registers(do_fast_start, do_fast_count)
        if fast_do_values:
            logger.info(f"DO {do_fast_start}-{do_fast_start + do_fast_count - 1} (быстрые): {fast_do_values}")
        
        # Чтение быстрых DI
        fast_di_values = await plc.read_discrete_inputs(di_fast_start, di_fast_count)
        if fast_di_values:
            logger.info(f"DI {di_fast_start}-{di_fast_start + di_fast_count - 1} (быстрые): {fast_di_values}")
        
        # Чтение медленных DI
        slow_di_start = di_fast_start + di_fast_count
        slow_di_count = di_count - di_fast_count
        slow_di_values = await plc.read_discrete_inputs(slow_di_start, slow_di_count)
        if slow_di_values:
            logger.info(f"DI {slow_di_start}-{di_start + di_count - 1} (медленные): первые 5: {slow_di_values[:5]}...")
        
        # Тест записи DO1
        logger.info(f"Установка DO1 (адрес {do_start}) в 1")
        success = await plc.write_register(do_start, 1)
        if success:
            logger.info("DO1 установлен")
            await asyncio.sleep(1.1)
            
            new_values = await plc.read_registers(do_start, 1)
            if new_values:
                logger.info(f"Проверка DO1: {new_values[0]}")
        
    except Exception as e:
        logger.error(f"Ошибка в main: {e}")
    finally:
        await plc.disconnect()

if __name__ == "__main__":
    asyncio.run(main())