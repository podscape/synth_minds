import os
import pickle

from core.audio_gen.gen_audio_interview import process_podcast_text
from core.utils_core import TextExtractor, read_file_to_string, download_pdf
from core.interview.generate_interview import run_sample_interview

url = "https://podscape-n87kdrzdp-infin1t3s-projects.vercel.app/aibxt.pdf"
output_dir = 'data'
filename = 'data/schizo.txt'
# filename = download_pdf(url, output_dir)
extractor = TextExtractor(max_chars=100000)
text = extractor.extract_text(filename)
filename = os.path.basename(filename).split('.')[0]
output_cleaned_text = f'{output_dir}/{filename}.txt'
# save_text_to_file(text, output_cleaned_text)
INPUT_PROMPT = read_file_to_string(output_cleaned_text)
final_content = run_sample_interview(INPUT_PROMPT)

with open('data/podcast_schizo_data.pkl', 'wb') as file:
    pickle.dump(final_content, file)

with open('data/podcast_schizo_data.pkl', 'rb') as file:
    PODCAST_TEXT = pickle.load(file)

final_audio = process_podcast_text(PODCAST_TEXT, device='cuda', speed_factor=1.0,
                                   host_speaker='maven brit 5.mp3', guest_speaker='SchizoVoice_m2.mp3')
# final_audio.export("output.wav", format="wav")
final_audio.export("../../data/podcast_schizo.mp3",
                  format="mp3",
                  bitrate="192k",
                  parameters=["-q:a", "0"])