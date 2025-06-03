import torch
from transformers import pipeline
import re
import time

def print_progress_bar(iteration: int, total: int, prefix: str = "", bar_length: int = 50) -> None:
    progress_fraction = iteration / total
    filled_length = int(bar_length * progress_fraction)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    percent = progress_fraction * 100
    print(f"\r{prefix} |{bar}| {percent:6.2f}% ({iteration}/{total})", end="", flush=True)
    if iteration == total:
        print()

def extract_priority_phrase(text: str) -> str:
    """
    Extract key phrase with prioritization from assistant response.
    """
    primary_patterns = [
        r'\b(specializes in|specializing in|including)\s+[^.!?,"]+'
    ]
    secondary_patterns = [
        r'\b(a reputable|a leading|a company that|a\s+[^.!?,"]*?leader in)\s+[^.!?,"]+'
    ]
    for pattern in primary_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0).strip().strip('"')

    for pattern in secondary_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0).strip().strip('"')

    return None  # Retourne None si aucun motif trouvé

def generate_summaries(descriptions: list[str], max_retries: int = 3) -> list[str]:
    """
    Generate one-sentence summaries for a list of company descriptions.
    """
    pipe = pipeline(
        "text-generation",
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    summaries = []

    for idx, description in enumerate(descriptions):
        clean_description = re.sub(r'\s+', ' ', description)

        messages = [
            {
                "role": "system",
                "content": "You are a chatbot specialized in generating cover letter introductions based on company resumes."
            },
            {
                "role": "user",
                "content": (
                    "Create a sentence beginning with "
                    "\"I'm looking forward to starting my work placement with your company, which specializes in\" "
                    f"based on the following resume: \"{clean_description}\""
                ),
            },
        ]

        extracted_text = None
        attempt = 0

        while extracted_text is None and attempt < max_retries:
            attempt += 1

            prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            outputs = pipe(prompt, max_new_tokens=100, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

            generated_text = outputs[0]['generated_text']

            assistant_match = re.search(r'<\|assistant\|>(.*)', generated_text, flags=re.DOTALL)
            assistant_response = assistant_match.group(1).strip() if assistant_match else generated_text.strip()

            extracted_text = extract_priority_phrase(assistant_response)

            if extracted_text is None:
                print(f"[Retry {attempt}] No matching phrase found, retrying...")
                time.sleep(0.5)  # Petite pause avant nouvelle tentative

        if extracted_text is None:
            # Si échec après toutes les tentatives, on conserve la réponse brute
            extracted_text = assistant_response

        print(extracted_text)
        summaries.append(extracted_text)

        print_progress_bar(current=idx + 1, total=len(descriptions), prefix="Summarizing")

    return summaries
