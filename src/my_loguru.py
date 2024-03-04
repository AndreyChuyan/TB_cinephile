import logging
import traceback
from loguru import logger
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
# Путь к директории, где будут храниться логи
file_log = "logs.log"
dir_log = "logs"
dir_path_log = os.path.join(script_dir, '..', dir_log)
if not os.path.exists(dir_path_log):        # Создаем новую папку
    os.makedirs(dir_path_log)
LOG_PATH = os.path.join(dir_path_log, file_log)

# Настройка стандартного логгера 'logging' для других целей
other_logs = logging.getLogger('other_logs')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(f'{LOG_PATH}other.log')],
)

class Logger:
    """
    Класс Logger обеспечивает настройку и использование логгера loguru для различных уровней логирования.
    Поддерживает создание файлов логов для уровней: INFO, ERROR, WARNING, DEBUG, а также кастомный уровень REQUEST.
    """
    # Формат сообщений лога
    __message_format = "{time:YYYY-MM-DD HH:mm:ss} :: {level} :: {message}"

    # Настройка логгера loguru для разных уровней логирования и файлов
    logger.add(f"{LOG_PATH}info.log", format=__message_format, level="INFO", rotation="100 MB",
               filter=lambda record: record["level"].name == 'INFO')

    logger.add(f"{LOG_PATH}error.log", format=__message_format, level="ERROR", rotation="100 MB",
               filter=lambda record: record["level"].name == 'ERROR', backtrace=True, diagnose=True)

    logger.add(f"{LOG_PATH}warning.log", format=__message_format, level="WARNING", rotation="100 MB",
               filter=lambda record: record["level"].name == 'WARNING')

    logger.add(f"{LOG_PATH}debug.log", format=__message_format, level="DEBUG", rotation="100 MB",
               filter=lambda record: record["level"].name == 'DEBUG')

    # Создание кастомного уровня логирования для запросов
    new_level = logger.level("REQUEST", no=38, color="<green>", icon="🐍")
    logger.add(f"{LOG_PATH}/requests/" + '{time:YYYY-MM}.log', format='{time:YYYY-MM-DD HH:mm:ss}|{message}',
               level="REQUEST", rotation="100 MB", filter=lambda record: record["level"].name == 'REQUEST')

    catch = logger.catch

    @staticmethod
    def _get_mes(args: list, sep=' ', traceback=''):
        """
        Форматирует сообщение для лога, объединяя аргументы и добавляя информацию о трассировке, если необходимо.
        """
        mes = sep.join(map(str, args))
        if traceback:
            mes += f'\n{traceback}'
        return mes.replace('\n', '\n\t-> ')

    @classmethod
    def __get_traceback_coll(cls):
        """
        Получает информацию о месте в коде, откуда был вызван лог.
        """
        traceback_info = traceback.extract_stack()[-3]
        file_name, line_number, place, _ = traceback_info
        return f'Traceback: "{file_name}:{line_number}" in {place}'

    @classmethod
    def info(cls, *args: str, sep=' ', is_traceback=False):
        """
        Логирует информационное сообщение.
        """
        tb = cls.__get_traceback_coll() if is_traceback else ''
        logger.info(cls._get_mes(args, sep, tb))

    @classmethod
    def debug(cls, *args: str, sep=' ', is_traceback=False):
        tb = cls.__get_traceback_coll() if is_traceback else ''
        logger.debug(cls._get_mes(args, sep, tb))

    @classmethod
    def warning(cls, *args: str, sep=' ', is_traceback=False):
        tb = cls.__get_traceback_coll() if is_traceback else ''
        logger.warning(cls._get_mes(args, sep, tb))

    @classmethod
    def exception(cls, *args: str, sep=' '):
        tb = cls.__get_traceback_coll()
        logger.exception(cls._get_mes(args, sep, tb))

    @classmethod
    def error(cls, *args: str, sep=' '):
        tb = cls.__get_traceback_coll()
        logger.error(cls._get_mes(args, sep, tb))

    @classmethod
    def request(cls, *args: str, sep=' '):
        logger.log("REQUEST", cls._get_mes(args, sep))
