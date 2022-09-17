"""Gather synonyms from NLTK."""
from pathlib import Path

import nltk

from filemanager._utils import dedupe_list


def instantiate_nltk() -> None:  # pragma: no cover
    """Instantiate nltk package."""
    ntlk_data_path = Path(Path.home() / ".filemanager" / "nltk_data")
    nltk.data.path.append(ntlk_data_path)

    if Path(ntlk_data_path / "corpora" / "wordnet.zip").exists() is False:
        nltk.download("wordnet", download_dir=ntlk_data_path)

    if Path(ntlk_data_path / "corpora" / "omw-1.4.zip").exists() is False:
        nltk.download("omw-1.4", download_dir=ntlk_data_path)


def find_synonyms(word: str) -> list[str]:  # pragma: no cover
    """Find synonyms for a word.

    Args:
        word (str): The word to find synonyms for.

    Returns:
        list[str]: List of synonyms.
    """
    from nltk.corpus import wordnet

    synonyms = [word]

    if len(wordnet.synsets(word)) > 0:
        for syn in wordnet.synsets(word):
            for lm in syn.lemmas():
                synonyms.append(lm.name())

        for w in wordnet.synsets(word)[0].also_sees():
            synonyms.append(w.lemmas()[0].name())

        for w in wordnet.synsets(word)[0].similar_tos():
            synonyms.append(w.lemmas()[0].name())

    return dedupe_list(synonyms)
