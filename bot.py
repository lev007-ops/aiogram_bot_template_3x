import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aioredis import Redis

from tgbot.config import load_config
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.handlers import echo

logger = logging.getLogger(__name__)
peewee_logger = logging.getLogger('peewee')


async def on_startup(bot: Bot, dp: Dispatcher):
    # код для выполнения при запуске
    config = load_config(".env")
    await dp.bot.set_my_commands(
            [
                types.BotCommand(c[0], c[1]) for c in config.misc.bot_commands
            ]
        )


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))


async def main():
    file_log = logging.FileHandler('Log.log')
    console_out = logging.StreamHandler()
    peewee_logger.addHandler(logging.StreamHandler())
    peewee_logger.setLevel(logging.DEBUG)
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(levelname)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
        handlers=(file_log, console_out)
    )
    logger.info("Starting bot")
    config = load_config(".env")

    if config.tg_bot.use_redis:
        redis = Redis(host='redis')
        storage = RedisStorage(redis)
    else:
        storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='Markdown')
    dp = Dispatcher(storage=storage)

    for router in [echo.echo_router]:
        dp.include_router(router)

    register_global_middlewares(dp, config)

    await on_startup(bot)
    try:
        # await bot.delete_webhook()
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
