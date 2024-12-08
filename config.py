import os.path
import sys
from loguru import logger

# Определение текущего каталога
current_directory: str = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Конфигурация приложения.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): URI для подключения к базе данных SQLite.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Отключает отслеживание изменений объектов.
    """
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{os.path.join(current_directory, 'test.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SECRET_KEY=os.getenv('SECRET_KEY')

# Удаляем все существующие обработчики
logger.remove()

# Настройка логирования
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> - "
           "<level>{level:^8}</level> - "
           "<cyan>{name}</cyan>:<magenta>{line}</magenta> - "
           "<yellow>{function}</yellow> - "
           "<white>{message}</white>",
)

if __name__ == "__main__":
    current_directory: str = os.path.dirname(os.path.abspath(__file__))
    print(os.path.join(current_directory, "test.db"))