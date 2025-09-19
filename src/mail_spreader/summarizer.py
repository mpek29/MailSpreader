import torch
from transformers import pipeline
import re
import time
import json
import yaml

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
    Extract a key phrase from assistant response.
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

    return None


def generate_summaries(descriptions: list[str], max_retries: int = 3) -> list[str]:
    """
    Generate one-sentence summaries for a list of company descriptions.
    """
    pipe = pipeline(
        "text-generation",
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        torch_dtype="auto",  # torch.bfloat16 peut poser problème selon la machine
        device_map="auto"
    )

    summaries = []

    for idx, description in enumerate(descriptions):
        clean_description = re.sub(r'\s+', ' ', description)

        system_msg = "You are a chatbot that generates introductory phrases for cover letters based on company descriptions."
        user_msg = (
            "Create a sentence beginning with "
            "\"I'm looking forward to starting my work placement with your company, which specializes in\" "
                f"based on the following description: \"{clean_description}\""
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        extracted_text = None
        attempt = 0

        while extracted_text is None and attempt < max_retries:
            attempt += 1

            try:
                prompt = pipe.tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                outputs = pipe(
                    prompt,
                    max_new_tokens=100,
                    do_sample=True,
                    temperature=0.7,
                    top_k=50,
                    top_p=0.95
                )
                generated_text = outputs[0]['generated_text']

                assistant_match = re.search(r'<\|assistant\|>(.*)', generated_text, flags=re.DOTALL)
                assistant_response = assistant_match.group(1).strip() if assistant_match else generated_text.strip()

                extracted_text = extract_priority_phrase(assistant_response)
                if not extracted_text:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error during generation: {e}")
                time.sleep(1)

        if extracted_text is None:
            extracted_text = assistant_response

        summaries.append(extracted_text)

        print_progress_bar(iteration=idx + 1, total=len(descriptions), prefix="Summarizing")

    return summaries

def generate_summaries_extra(yaml_file, json_file_metadata, json_file_summaries):
    with open(yaml_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Récupérer les variables
    with open(json_file_metadata, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    company_about_texts = metadata.get("company_about_texts", [])

    # Generate summaries only for entries with non-empty email addresses
    generated_summaries = generate_summaries(company_about_texts)

    # Prepare final data
    data = {
        "summaries": generated_summaries
    }

    # Sauvegarder en JSON
    with open(json_file_summaries, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def translate_json(input_path: str, output_path: str):
    """
    Reads a JSON file with a ‘summaries’ key (list of texts), translates each text into French, then saves the result in a new JSON file.
    """

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)


    if "summaries" not in data:
        raise ValueError("Le JSON ne contient pas la clé 'summaries'.")

    # Prepare the translation pipeline
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")

    # Translate each text
    translated_summaries = []
    for idx, text in enumerate(data["summaries"]):
        traduction = translator(text)[0]["translation_text"]
        translated_summaries.append(traduction)
        print_progress_bar(iteration=idx + 1, total=len(data["summaries"]), prefix="Summarizing")

    # Create a new dictionary for the translated JSON
    translated_data = {"summaries": translated_summaries}

    # Save to the new JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)