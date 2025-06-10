from config import config
from aiogram import Bot
from aiogram import Dispatcher
from handlers import router as handlers_r
from callbacks import router as callbacks_r
import asyncio


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(handlers_r)
    dispatcher.include_router(callbacks_r)


    # Start long polling
    try:
        await dispatcher.start_polling(bot)
    finally:
        # Close API client after end of work
        await bot.session.close()


if __name__ == "__main__":
    print('Start')
    asyncio.run(main())


