"""Work with NLTK Library."""

from pathlib import Path

import nltk
from loguru import logger

from jdfile.constants import CACHE_DIR


def instantiate_nltk() -> None:  # pragma: no cover
    """Ensure necessary NLTK corpora are downloaded and available.

    Checks if the NLTK 'wordnet' and 'omw' corpora are present in APP_DIR. Downloads the corpora if not present. Logs the success of new installations and notes if the corpora were already installed.
    """
    nltk_data_path = Path(CACHE_DIR / "nltk_data")
    if not nltk_data_path.exists():
        nltk_data_path.mkdir(parents=True)
    nltk.data.path.append(str(nltk_data_path))  # Ensure nltk can find the custom data path

    # Define a list of corpora to check or download
    corpora = [("wordnet", "corpora/wordnet.zip"), ("omw-1.4", "corpora/omw-1.4.zip")]
    install = False  # Flag to track if any downloads were initiated

    for corpus_name, corpus_path in corpora:
        if not (nltk_data_path / corpus_path).exists():
            nltk.download(corpus_name, download_dir=str(nltk_data_path))
            install = True  # Mark that a download was necessary

    # Log the outcome based on whether any installations took place
    if install:
        logger.success("NLTK English synonym library instantiated.")
    else:
        logger.trace("NLTK English synonym library already installed.")


def find_synonyms(word: str) -> list[str]:  # pragma: no cover
    """Find synonyms for a word.

    Args:
        word (str): The word to find synonyms for.

    Returns:
        list[str]: De-duped alphabetical list of synonyms.
    """
    from nltk.corpus import wordnet  # noqa: PLC0415

    synonyms = [word]

    if len(wordnet.synsets(word)) > 0:
        for syn in wordnet.synsets(word):
            synonyms.extend([lm.name() for lm in syn.lemmas()])

        synonyms.extend([w.lemmas()[0].name() for w in wordnet.synsets(word)[0].also_sees()])
        synonyms.extend([w.lemmas()[0].name() for w in wordnet.synsets(word)[0].similar_tos()])

    if word.lower() in synonyms:
        synonyms.remove(word.lower())

    return sorted(set(synonyms))
