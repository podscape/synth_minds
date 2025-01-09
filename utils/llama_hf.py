import asyncio
from transformers import pipeline

class AsyncTextGenerator:
    def __init__(self, model_name="meta-llama/Llama-3.1-8B-Instruct"):
        self.model_name = model_name
        self.generator = None

    async def initialize(self):
        self.generator = pipeline(
            task = "text-generation",
            model=self.model_name,
            device='cuda:1')

    async def generate_text(self, prompt):
        if not self.generator:
            await self.initialize()
        result = self.generator(prompt, max_length=1024, num_return_sequences=1)
        return result[0]['generated_text']

async def main():
    generator = AsyncTextGenerator("meta-llama/Llama-3.1-8B-Instruct")
    tasks = [
        asyncio.create_task(generator.generate_text("Write a poem about a lonely robot")),
        asyncio.create_task(generator.generate_text("Explain quantum computing in simple terms")),
        asyncio.create_task(generator.generate_text("What is the capital of France?"))
    ]

    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())