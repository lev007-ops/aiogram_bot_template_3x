from aiogram import types, Router, F


echo_router = Router()


@echo_router.message(F.text, state=None)
async def bot_echo(message: types.Message):
    await message.answer(message.text)
