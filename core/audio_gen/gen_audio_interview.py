import re
from typing import Tuple, List
import numpy as np
from pydub import AudioSegment
import io
from scipy.io import wavfile
from TTS.api import TTS
from tqdm import tqdm
import torch
import pickle

from whisperspeech.pipeline import Pipeline


class XTTSWrapper:
    def __init__(self, device='cuda', model_type='coqui', host_speaker='maven brit 5.mp3', guest_speaker=None):
        self.device = device
        self.model_type = model_type
        self.host_speaker = host_speaker
        self.guest_speaker = guest_speaker
        if self.model_type == 'coqui':
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            # self.model = TTS("tts_models/multilingual/multi-dataset/your_tts").to(device)
            # self.model = TTS("tts_models/en/vctk/vits").to(device)
        else:
            self.model = Pipeline(t2s_ref='whisperspeech/whisperspeech:t2s-v1.95-small-8lang.model',
                                  s2a_ref='whisperspeech/whisperspeech:s2a-v1.95-medium-7lang.model')

        self.sampling_rate = 24000  # xtts_v2 default sampling rate

        # self.host_speaker = "Alice_longer.mp3" # good
        # self.host_speaker = "Maven brit four.mp3" # good
        # self.host_speaker = "maven brit 5.mp3"
        # self.host_speaker = "callum_longert.mp3"
        # self.guest_speaker = "SchizoVoice_m2.mp3"


    def generate_audio(self, text: str, is_host: bool = True) -> np.ndarray:
        """Generate audio for a single text chunk"""
        speaker_wav = self.host_speaker if is_host else self.guest_speaker
        if self.model_type == 'coqui':
            wav = self.model.tts(
                text=text,
                speaker_wav=speaker_wav,
                language="en",
                # emotion="happy",
                # speed=speed_fc
            )
        else:
            wav = self.model.generate(text)
            wav = wav.cpu().numpy()

        return wav

    def generate_audio_chunked(self, text: str, is_host: bool = True, max_chunk_size: int = 150) -> Tuple[np.ndarray, int]:
        """
        Generate audio for longer text by splitting into chunks and concatenating.
        """
        chunks = split_into_chunks(text, max_chunk_size)
        audio_segments = []

        for chunk in chunks:
            audio_arr = self.generate_audio(chunk, is_host)
            audio_segments.append(audio_arr)

            # pause between chunks
            pause_samples = int(self.sampling_rate * 0.2)  # 200ms pause
            pause = np.zeros(pause_samples)
            audio_segments.append(pause)

        final_audio = np.concatenate(audio_segments)
        return final_audio, self.sampling_rate

def split_into_chunks(text: str, max_chunk_size: int = 200) -> List[str]:
    """Split text into chunks at sentence boundaries"""
    text = text.replace("\n", " ").strip()
    text = text.replace("[", "").replace("]", "")
    # text = text.replace("\\", "")
    # print("original text->", text)

    sentences = re.split('(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def numpy_to_audio_segment(audio_arr: np.ndarray, sampling_rate: int) -> AudioSegment:
    """Convert numpy array to AudioSegment"""
    # Normalize audio if needed
    # if audio_arr.max() > 1.0 or audio_arr.min() < -1.0:
    #     audio_arr = audio_arr / np.max(np.abs(audio_arr))

    # Convert to 16-bit PCM
    audio_int16 = (audio_arr * 32767).astype(np.int16)

    # Create WAV file in memory
    byte_io = io.BytesIO()
    wavfile.write(byte_io, sampling_rate, audio_int16)
    byte_io.seek(0)

    # Convert to AudioSegment
    return AudioSegment.from_wav(byte_io)


def format_timestamp(milliseconds: float) -> str:
    """Convert milliseconds to VTT timestamp format (HH:MM:SS.mmm)"""
    # Handle milliseconds portion
    ms = int(milliseconds % 1000)
    seconds = int(milliseconds / 1000)

    # Convert to hours, minutes, seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def process_podcast_text(podcast_text, device='cuda', speed_factor=1,
                         host_speaker='maven brit 5.mp3', guest_speaker=None):
    """
    Process podcast text and generate audio

    Args:
        podcast_text: List of (speaker, text) tuples
        device: Device to run TTS on
        speed_factor: Speed up factor (1.0 = original speed, 1.1 = 10% faster, etc.)
        host_speaker: 15 second audio clip of host speaker
        guest_speaker: 15 second audio clip of guest speaker
    """
    tts = XTTSWrapper(device, model_type='coqui', host_speaker=host_speaker, guest_speaker=guest_speaker)
    final_audio = None

    for speaker, text in tqdm(podcast_text, desc="Generating podcast segments", unit="segment"):
        # lower case text
        # text = text.lower()
        is_host = (speaker == "Host")
        audio_arr, rate = tts.generate_audio_chunked(text, is_host=is_host)

        audio_segment = numpy_to_audio_segment(audio_arr, rate)

        # speed_fc = 1.1 if is_host else 1.0
        if speed_factor != 1.0:
            # sox-based speedup (maintains pitch better than segment_speed)
            audio_segment = audio_segment.speedup(playback_speed=speed_factor)

        if final_audio is None:
            final_audio = audio_segment
        else:
            final_audio += audio_segment

    return final_audio


# usage
if __name__ == "__main__":
    with open('../../data/podcast_schizo_data.pkl', 'rb') as file:
        PODCAST_TEXT = pickle.load(file)


    final_audio = process_podcast_text(PODCAST_TEXT, device='cuda', speed_factor=1.0)
    # final_audio.export("output.wav", format="wav")
    final_audio.export("../../data/podcast_schizo.mp3",
                      format="mp3",
                      bitrate="192k",
                      parameters=["-q:a", "0"])
