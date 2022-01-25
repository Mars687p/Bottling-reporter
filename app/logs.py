from loguru import logger

logger.add('logs.log', encoding='utf8', format='[{time:YYYY-MM-DD HH:mm:ss}] {level} {message}', 
            level='INFO', retention="60 days")
