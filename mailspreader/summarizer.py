import spacy

VERB_TO_NOUN_FR = {
    "concevoir": "la conception de",
    "fabriquer": "la fabrication de",
    "produire": "la production de",
    "développer": "le développement de",
    "commercialiser": "la commercialisation de",
    "vendre": "la vente de",
    "proposer": "la proposition de",
    "offrir": "l’offre de",
    "assurer": "l’assurance de",
    "réparer": "la réparation de",
    "fournir": "la fourniture de",
    "installer": "l’installation de",
    "maintenir": "la maintenance de",
    "créer": "la création de",
    "distribuer": "la distribution de",
    "gérer": "la gestion de",
    "conditionner": "le conditionnement de",
    "assembler": "l’assemblage de",
    "traiter": "le traitement de",
    "industrialiser": "l’industrialisation de",
    "valoriser": "la valorisation de",
    "numériser": "la numérisation de",
    "auditer": "l’audit de",
    "financer": "le financement de",
    "programmer": "la programmation de",
    "coder": "le codage de"
}

VERB_TO_NOUN_EN = {
    "design": "the design of",
    "manufacture": "the manufacture of",
    "produce": "the production of",
    "develop": "the development of",
    "market": "the marketing of",
    "sell": "the sale of",
    "offer": "the offering of",
    "ensure": "the ensuring of",
    "repair": "the repair of",
    "provide": "the provision of",
    "install": "the installation of",
    "maintain": "the maintenance of",
    "create": "the creation of",
    "distribute": "the distribution of",
    "manage": "the management of",
    "package": "the packaging of",
    "assemble": "the assembly of",
    "process": "the processing of",
    "industrialize": "the industrialization of",
    "enhance": "the enhancement of",
    "digitize": "the digitization of",
    "audit": "the audit of",
    "finance": "the financing of",
    "program": "the programming of",
    "code": "the coding of"
}

def print_progress_bar(
    iteration: int, total: int, prefix: str = "", bar_length: int = 50
) -> None:
    """
    Render a progress bar in the terminal.

    Args:
        iteration (int): Current iteration count (1-based).
        total (int): Total number of iterations.
        prefix (str): Optional string to prefix the progress bar.
        bar_length (int): Length of the progress bar in characters.
    """
    progress_fraction = iteration / total
    filled_length = int(bar_length * progress_fraction)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    percent = progress_fraction * 100
    print(
        f"\r{prefix} |{bar}| {percent:6.2f}% ({iteration}/{total})",
        end="",
        flush=True,
    )
    if iteration == total:
        print()

def get_full_phrase(token):
    words = [t.text for t in sorted(token.subtree, key=lambda x: x.i)]
    return " ".join(words)

def extract_activity_from_sentence(sent, verb_to_noun, lang):
    for token in sent:
        if token.pos_ == "VERB" and token.lemma_ in verb_to_noun:
            nominal = verb_to_noun[token.lemma_]

            complements_phrases = []

            for child in token.children:
                if child.dep_ in {"obj", "obl", "xcomp", "ccomp"}:
                    phrase = get_full_phrase(child)
                    complements_phrases.append(phrase)
                elif child.dep_ == "prep":
                    phrase = get_full_phrase(child)
                    complements_phrases.append(phrase)

            if complements_phrases:
                full_complement = ", ".join(complements_phrases).lower()

                if lang == "fr":
                    full_complement = full_complement.replace("de des", "de").replace("de le", "du")
                    if full_complement.startswith(("le ", "la ", "les ", "un ", "une ", "des ", "du ", "de l'")) and nominal.endswith(" de"):
                        nominal = nominal[:-3]
                    return f"spécialisée dans {nominal} {full_complement}"

                elif lang == "en":
                    # en anglais on adapte la phrase un peu différemment
                    # exemple : "specialized in the repair of electronic cards"
                    # Pas de contraction à gérer, on garde la formule simple
                    return f"specialized in {nominal} {full_complement}"

    # fallback sur noms (uniquement pour fr, pour anglais on peut laisser None)
    if lang == "fr":
        nouns_of_interest = {v.split()[1] for v in verb_to_noun.values()}
        for token in sent:
            if token.pos_ == "NOUN" and token.lemma_.lower() in nouns_of_interest:
                phrase = token.lemma_.lower()
                preps = []
                for child in token.children:
                    if child.dep_ == "prep":
                        preps.append(get_full_phrase(child).lower())
                if preps:
                    phrase += " " + " ".join(preps)
                return f"spécialisée dans la {phrase}"

    return None

def generate_summaries(company_texts, lang="fr"):
    if lang == "fr":
        nlp = spacy.load("fr_core_news_md")
        verb_to_noun = VERB_TO_NOUN_FR
    elif lang == "en":
        nlp = spacy.load("en_core_web_md")
        verb_to_noun = VERB_TO_NOUN_EN
    else:
        raise ValueError("Unsupported language. Use 'fr' or 'en'.")

    summaries = []
    for i in range(len(company_texts)):
        doc = nlp(company_texts[i])
        found = None
        for sent in doc.sents:
            found = extract_activity_from_sentence(sent, verb_to_noun, lang)
            if found:
                break
        if not found:
            found = "activité principale non identifiée" if lang == "fr" else "main activity not identified"
        summaries.append(found)

        print_progress_bar(iteration=i, total=len(company_texts), prefix="Summarize Progress:", bar_length=len(company_texts))
    return summaries
