import torch
from accelerate import Accelerator
import transformers
import pickle

from core.utils_core import read_file_to_string
from sys_prompts import *

from tqdm.notebook import tqdm
import warnings

warnings.filterwarnings('ignore')

MODEL = "meta-llama/Llama-3.1-8B-Instruct"



INPUT_PROMPT = read_file_to_string('./resources/clean_extracted_text.txt')

pipeline = transformers.pipeline(
    "text-generation",
    model=MODEL,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

messages = [
    {"role": "system", "content": sys_prompts["interview_gen_prompt"]},
    {"role": "user", "content": INPUT_PROMPT},
]

outputs = pipeline(
    messages,
    max_new_tokens=8126,
    temperature=1,
)

save_string_pkl = outputs[0]["generated_text"][-1]['content']

with open('./resources/data.pkl', 'wb') as file:
    pickle.dump(save_string_pkl, file)