import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aioredis import Redis

from tgbot.config import load_config
from tgbot.handlers import echo

logger = logging.getLogger('bot')


async def on_startup(bot: Bot, dp: Dispatcher):
    # код для выполнения при запуске
    config = load_config(".env")
    logger.info('Try set bot commands')
    await bot.set_my_commands(
            [
                types.BotCommand(command=c[0], description=c[1]) for c in config.misc.bot_commands
            ]
        )
    logger.info('Set bot commands is Successful')


def register_global_middlewares(dp: Dispatcher, config):
    logger.info('Try register global middlewares')
    logger.info('Register global middlewares is Successful')


def init_logging(config):
    if len(logging.getLogger().handlers) > 0:
        # The Lambda environment pre-configures a handler logging to stderr.
        # If a handler is already configured, `.basicConfig` does not execute.
        # Thus, we set the level directly.
        logging.getLogger().setLevel(logging.INFO)
    else:
        import colorlog
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s "
            "%(bold)s[%(levelname)s]%(thin)s "
            "%(name)s%(reset)s - "
            "%(bold)s%(funcName)s (%(filename)s:%(lineno)d)%(reset)s - "
            "%(message)s",
        ))
        logging.basicConfig(
            level=logging.INFO,
            handlers=[handler],
        )
    if config.misc.enable_peewee_logging:
        logging.getLogger('peewee').addHandler(logging.StreamHandler())


async def main():
    config = load_config(".env")
    init_logging(config)

    if config.tg_bot.use_redis:
        logger.info('Try to connect Redis')
        redis = Redis(host=config.misc.redis_host)
        logger.info('Connect to Redis is Successful')
        storage = RedisStorage(redis)
        logger.info('aiogram storage is RedisStorage')
    else:
        storage = MemoryStorage()
        logger.info('aiogram storage is MemoryStorage')
    bot = Bot(token=config.tg_bot.token, parse_mode='Markdown')
    dp = Dispatcher(storage=storage)

    for router in [echo.echo_router]:
        dp.include_router(router)

    register_global_middlewares(dp, config)

    await on_startup(bot, dp)
    try:
        await dp.start_polling(bot)
    finally:
        logger.info('Try close storage and session')
        await dp.storage.close()
        await bot.session.close()
        logger.info('Close storage and session is Successful')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
