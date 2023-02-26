"""Work with NLTK Library."""

from pathlib import Path

import nltk

from jdfile.utils.alerts import logger as log


def instantiate_nltk() -> None:  # pragma: no cover
    """Instantiate nltk package."""
    ntlk_data_path = Path(Path.home() / ".jdfile" / "nltk_data")
    nltk.data.path.append(ntlk_data_path)

    install = False
    if Path(ntlk_data_path / "corpora" / "wordnet.zip").exists() is False:
        install = True
        nltk.download("wordnet", download_dir=ntlk_data_path)

    if Path(ntlk_data_path / "corpora" / "omw-1.4.zip").exists() is False:
        install = True
        nltk.download("omw-1.4", download_dir=ntlk_data_path)

    if install:
        log.success("NLTK English synonym library instantiated")
    else:
        log.trace("NLTK English synonym library already installed")


def find_synonyms(word: str) -> list[str]:  # pragma: no cover
    """Find synonyms for a word.

    Args:
        word (str): The word to find synonyms for.

    Returns:
        list[str]: De-duped alphabetical list of synonyms.
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

    if word.lower() in synonyms:
        synonyms.remove(word.lower())

    return sorted(set(synonyms))
