import os
import torch
from accelerate import Accelerator
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer
from core.utils_core import TextExtractor, save_text_to_file
from sys_prompts import *

# Constants
DEFAULT_MODEL = "meta-llama/Llama-3.2-1B-Instruct"
CHUNK_SIZE = 1000

# This class is somehow overpowered when the file to process is small, however, let's keep it for when needed.
# The cleaner gets rid of stuff from the document (e.g., a white paper of the project, etc.) which is not usable for generating podcast, etc.
class TextProcessor:
    def __init__(self, model_name=DEFAULT_MODEL):
        self.accelerator = Accelerator()
        self.setup_model(model_name)

    def setup_model(self, model_name):
        """Initialize the model and tokenizer"""
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            use_safetensors=True,
            device_map='cuda',
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_safetensors=True)
        self.model, self.tokenizer = self.accelerator.prepare(self.model, self.tokenizer)

    @staticmethod
    def create_word_bounded_chunks(text, target_chunk_size):
        """Split text into chunks at word boundaries"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for the space
            if current_length + word_length > target_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        print(f"Split text into {len(chunks)} chunks")
        return chunks

    def process_chunk(self, text_chunk, chunk_num, preproc_prompt):
        """Process a single chunk of text"""
        conversation = [
            {"role": "system", "content": preproc_prompt},
            {"role": "user", "content": text_chunk},
        ]

        prompt = self.tokenizer.apply_chat_template(conversation, tokenize=False)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                temperature=0.7,
                top_p=0.9,
                max_new_tokens=512
            )

        processed_text = self.tokenizer.decode(output[0], skip_special_tokens=True)[len(prompt):].strip()

        # Print progress information
        print(f"INPUT TEXT:\n{text_chunk[:500]}...")
        print(f"\nPROCESSED TEXT:\n{processed_text[:500]}...")
        print(f"{'=' * 90}\n")

        return processed_text

    def process_file(self, input_file, preproc_prompt):
        """Process an entire file"""
        text_extractor = TextExtractor(max_chars=100000)
        extracted_text = text_extractor.extract_text(input_file)

        if input_file.lower().endswith('.pdf'):
            outfile_extracted_text = "../../data/extracted_text.txt"
            save_text_to_file(extracted_text, outfile_extracted_text)
        else:
            outfile_extracted_text = input_file
            print("File is a txt file, using the original file as extracted text!")

        # Create chunks
        chunks = self.create_word_bounded_chunks(extracted_text, CHUNK_SIZE)
        num_chunks = len(chunks)

        # Create output file
        output_file = f"../../data/clean_{os.path.basename(outfile_extracted_text)}"
        processed_text = ""

        # Process chunks and write to file
        with open(output_file, 'w', encoding='utf-8') as out_file:
            for chunk_num, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
                processed_chunk = self.process_chunk(chunk, chunk_num, preproc_prompt)
                processed_text += processed_chunk + "\n"
                out_file.write(processed_chunk + "\n")
                out_file.flush()

        # Print summary
        print(f"\nProcessing complete!")
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        print(f"Total chunks processed: {num_chunks}")

        # Preview results
        print("\nPreview of final processed text:")
        print("\nBEGINNING:")
        # print(processed_text)
        print(processed_text[:1000])
        print("\n...\n\nEND:")
        print(processed_text[-1000:])

        return output_file


def main():
    input_file = "../../data/dolos.txt"
    # input_file = "../../data/2402.13116v4.pdf"
    preproc_prompt = sys_prompts["preproc_prompt"]

    processor = TextProcessor()
    processor.process_file(input_file, preproc_prompt)


if __name__ == "__main__":
    main()