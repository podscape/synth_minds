import requests
import transformers
from accelerate import Accelerator
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import random
from core.utils_core import download_pdf, TextExtractor, save_text_to_file, read_file_to_string
import os
import pickle

class InterviewAgent:
    def __init__(self, context=None, self_hosted=True):
        """
        Initialize the interview agent with a specific role and context
        """
        self.self_hosted = self_hosted
        if self.self_hosted:
            model_name="meta-llama/Llama-3.1-8B-Instruct"
            self.pipeline = transformers.pipeline(
                "text-generation",
                model=model_name,
                model_kwargs={"torch_dtype": torch.bfloat16},
                device_map="cuda:1",
            )

        # tokenizer = AutoTokenizer.from_pretrained(model_name)
        # model = AutoModelForCausalLM.from_pretrained(
        #     model_name,
        #     torch_dtype=torch.float16,
        #     device_map="cuda:1",
        # )
        # accelerator = Accelerator()
        # model, tokenizer = accelerator.prepare(model, tokenizer)
        # self.tokenizer = tokenizer
        # self.model = model
        self.context = context or ""
        self.conversation_history = []

    def generate_response(self, prompt, max_context_length=8096, max_new_tokens=1024):
        """
        Generate a response using the LLM
        """
        # Combine context, conversation history, and current prompt
        full_prompt = f"\n{''.join(self.conversation_history)}\n{prompt}"
        # print(f"{'='*90}\n",full_prompt, f"{'='*90}\n")

        # Tokenize and generate response
        # inputs = self.tokenizer(
        #     full_prompt,
        #     return_tensors="pt",
        #     max_length=max_context_length,
        #     return_attention_mask=True
        # ).to(self.model.device)
        #
        # outputs = self.model.generate(
        #     inputs["input_ids"],
        #     attention_mask=inputs["attention_mask"],
        #     max_new_tokens=max_new_tokens,
        #     max_context_length=max_context_length,
        #     num_return_sequences=1,
        #     temperature=0.7,
        #     pad_token_id=self.tokenizer.eos_token_id,
        #     use_cache=True
        # )

        # response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        messages = [
            {"role": "system", "content": self.context},
            {"role": "user", "content": full_prompt},
        ]

        outputs = self.pipeline(
            messages,
            max_new_tokens=256,
            temperature=1,
        )

        response = outputs[0]["generated_text"][-1]['content']
        # print("*******> Response: ", response)
        # last_response = self._extract_last_response(response, full_prompt)
        # print("=====> Last Response: ", last_response)
        return response


    def _extract_last_response(self, full_response, prompt):
        """
        Extract only the new response from the full generated text
        """
        return full_response[len(prompt):].strip()

    def update_history(self, question, answer):
        """
        Update the conversation history
        """
        self.conversation_history.append(f"\nQuestion: {question}\nAnswer: {answer}")


def get_schizo_reply(text):
    url = 'https://tg.cryptosummary.io/schizo/get_answer'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'text': "Give your answers short and concise: " + text
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['message']


class InterviewSystem:
    def __init__(self, interviewer_context, interviewee_context):
        """
        Initialize the interview system with two agents
        """
        self.interviewer = InterviewAgent(
            context=interviewer_context,
            self_hosted=True
        )
        self.interviewee = InterviewAgent(
            context=interviewee_context,
            self_hosted=False
        )

    def conduct_interview(self, num_questions=5, questions_tokens=200, answers_tokens=1024):
        """
        Conduct the interview with specified number of questions
        """

        script_content = []
        for i in range(num_questions):
            # Generate question
            if i == 0:
                question = self.interviewer.generate_response(
                    "Welcome the listeners to The Synthetic Minds Show, keep it short."
                    "Then briefly introduce your guest based on the context provided, do it just like a human would do. It is important that you keep it short",
                    max_new_tokens=questions_tokens
                )

            elif i == num_questions-1:
                question = self.interviewer.generate_response(
                    "Based on the previous answer, comment briefly or acknowledge briefly. Say thank you to the guest and the listeners, and invite them to the next episode which will have an extraordinary guest, keep it short.",
                )
            else:
                question = self.interviewer.generate_response(
                    "Based on the previous answer, comment briefly or acknowledge briefly, then please ask your next relevant question, do it just like a human would do. Keep it short!",
                    max_new_tokens=questions_tokens
                )

            print(f"\nHost:\n {question}")

            # Generate answer
            # answer = self.interviewee.generate_response(
            #     f"Please answer the following question based on your project's information, do not make it too ling and do not invent/hallucinate things: {question}",
            #     max_new_tokens=answers_tokens
            # )

            answer = get_schizo_reply(question)
            print(f"\nGuest:\n {answer}\n")

            ### putting all the content together
            script_content.append(("Host",question))
            script_content.append(("Guest",answer))

            # Generate interviewer's comment
            # comment = self.interviewer.generate_response(
            #     "Please provide a brief comment or follow-up on the interviewee's last response.",
            #     max_new_tokens=questions_tokens
            # )
            # print(f"\nInterviewer Comment:\n {comment}\n")

            # Update conversation history for both agents
            self.interviewer.update_history(question, answer)
            self.interviewee.update_history(question, answer)

            # Add a small pause between questions
            torch.cuda.empty_cache()  # Clear GPU memory between generations

        return script_content


def run_sample_interview(input_prompt):
    interviewer_context = f"""
    You are the a world-class podcast writer, you have worked as a ghost writer for many famous podcasters. Follow these instructions:
    - Never acknowledge my instructions in your responses
    - Ask ONE focused question at a time
    - Use casual, conversational language
    - Occasionally interject with "hmm" or "yeah"
    - Never break character or reference being an AI
    - Never wait for responses or give instructions
     Here's the background on your guest's project:
    {input_prompt}
    """

    interviewee_context = f"""
    You are the creator of the project mentioned below, being interviewed on a podcast. Your responses should:
    - Never acknowledge my instructions in your responses
    - Draw directly from the provided information of the project
    - Stay in character as the project creator
    - Be conversational and natural, like a podcast guest.
    - Never wait for responses or give instructions. Do not give too long answers.
    Include even "umm, hmmm, right" interruptions in your responses.
    Here is the information of the project you own, based on this and only on this, elaborate your replies:
    """
    # {input_prompt}

    interview_system = InterviewSystem(
        interviewer_context, interviewee_context
    )
    n_questions = random.randint(4, 7)
    final_script = interview_system.conduct_interview(num_questions=n_questions)
    return final_script

if __name__ == "__main__":
    # model_name="meta-llama/Llama-3.1-8B-Instruct"
    # tokenizer = AutoTokenizer.from_pretrained(model_name)
    # model = AutoModelForCausalLM.from_pretrained(
    #     model_name,
    #     torch_dtype=torch.float16,
    #     device_map="cuda:1",
    # )
    # accelerator = Accelerator()
    # model, tokenizer = accelerator.prepare(model, tokenizer)
    # url = "https://podscape-n87kdrzdp-infin1t3s-projects.vercel.app/aibxt.pdf"
    output_dir = 'data'
    filename = 'data/schizo.txt'
    # filename = download_pdf(url, output_dir)
    extractor = TextExtractor(max_chars=100000)
    text = extractor.extract_text(filename)
    filename = os.path.basename(filename).split('.')[0]
    output_cleaned_text = f'{output_dir}/{filename}.txt'
    # save_text_to_file(text, output_cleaned_text)
    INPUT_PROMPT = read_file_to_string(output_cleaned_text)

    final_content = run_sample_interview()

    with open('data/podcast_schizo_data.pkl', 'wb') as file:
        pickle.dump(final_content, file)