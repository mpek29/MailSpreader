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

def extract_priority_phrase(text: str, lang: str = "en") -> str:
    """
    Extract a key phrase from assistant response based on language.
    """

    if lang == "fr":
        primary_patterns = [
            r'\b(spécialisée dans|spécialisant dans|y compris)\s+[^.!?,"]+'
        ]
        secondary_patterns = [
            r'\b(une entreprise réputée|un leader|une entreprise qui|un\s+[^.!?,"]*?leader dans)\s+[^.!?,"]+'
        ]
    else:  # default to English
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


def generate_summaries(descriptions: list[str], lang: str = "en", max_retries: int = 3) -> list[str]:
    """
    Generate one-sentence summaries for a list of company descriptions,
    using either English or French prompting based on `lang`.
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

        if lang == "fr":
            system_msg = "Tu es un assistant qui génère des phrases d'introduction pour des lettres de motivation à partir de descriptions d'entreprise."
            user_msg = (
                "Crée une phrase qui commence par "
                "\"Je suis impatient de commencer mon stage au sein de votre entreprise, qui est spécialisée dans\" "
                f"à partir de la description suivante : \"{clean_description}\""
            )
        else:  # default to English
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

                extracted_text = extract_priority_phrase(assistant_response, lang=lang)
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

def generate_summaries_extra(yaml_file, json_file_email, json_file_metadata, json_file_summaries):
    with open(yaml_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Récupérer les variables
    lang = config.get("lang", "")
    with open(json_file_metadata, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    company_about_texts = metadata.get("company_about_texts", [])

    # Récupérer la liste des URLs
    with open(json_file_email, "r", encoding="utf-8") as f:
        emaildata = json.load(f)

    company_emails = emaildata.get("extracted_emails", [])

    # Préparer les textes valides et leur index
    valid_texts = []
    valid_indexes = []
    for i, (email, about_text) in enumerate(zip(company_emails, company_about_texts)):
        if email.strip():
            valid_texts.append(about_text)
            valid_indexes.append(i)

    # Générer les résumés uniquement pour les entrées avec email non vide
    generated_summaries = generate_summaries(valid_texts, lang=lang)
    
    # Réinsérer les résumés aux bons index, sinon chaîne vide
    summaries = ["" for _ in company_about_texts]
    for idx, summary in zip(valid_indexes, generated_summaries):
        summaries[idx] = summary

    # Préparer les données finales
    data = {
        "summaries": summaries
    }

    # Sauvegarder en JSON
    with open(json_file_summaries, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)