"""String utilities."""
import re

from jdfile.utils.alerts import logger as log
from jdfile.utils.enums import InsertLocation, Separator, TransformCase


def insert(string: str, value: str, location: InsertLocation, separator: Separator) -> str:
    """Insert a value into the new filename.

    Args:
        string (str): String to insert value into.
        location (InsertLocation): Where to insert the value.
        separator (Separator): Separator to use.
        value (str): Value to insert.

    Returns:
        str: New filename with value inserted.
    """
    match separator:
        case Separator.UNDERSCORE:
            sep = "_"
        case Separator.DASH:
            sep = "-"
        case Separator.SPACE:
            sep = " "
        case Separator.NONE:
            sep = ""
        case _:
            sep = "_"

    match location:
        case InsertLocation.BEFORE:
            return f"{value}{sep}{string}"
        case InsertLocation.AFTER:
            return f"{string}{sep}{value}"


def match_case(string: str, match_case: list[str] = []) -> str:
    """Match case of words in a string to a list of words.

    Args:
        match_case (list[str]): List of words to match case.
        string (str): String to match case in.

    Returns:
        str: String with case matched.
    """
    if len(match_case) > 0:
        for term in match_case:
            string = re.sub(
                rf"(^|[-_ ]){re.escape(term)}([-_ ]|$)", rf"\1{term}\2", string, flags=re.I
            )

    return string


def normalize_separators(string: str, separator: Separator = Separator.IGNORE) -> str:
    """Normalize separators in a string.

    Args:
        Separator (Separator): Separator to normalize to.
        string (str): String to fix separators in.

    Returns:
        str: String with separators normalized.
    """
    match separator:
        case Separator.SPACE:
            return re.sub(r"[-_ \.]+", " ", string).strip("-_ ")

        case Separator.DASH:
            return re.sub(r"[-_ \.]+", "-", string).strip("-_ ")

        case Separator.UNDERSCORE:
            return re.sub(r"[-_ \.]+", "_", string).strip("-_ ")

        case Separator.NONE:
            return re.sub(r"[-_ \.]+", "", string).strip("-_ ")

        case _:
            return re.sub(r"([-_ \.])[-_ \.]+", r"\1", string).strip("-_ ")


def split_camelcase_words(string: str, match_case: list[str] = []) -> str:
    """Split camelCase words in a string into separate words.

    If camelCase words are in the match_case list, they will be put back together.

    Args:
        match_case (list[str], optional): List of words to retain case. Defaults to [].
        string (str): String to split words in.

    Returns:
        str: String with camelCase words split.
    """
    words = " ".join([word for word in re.split(r"(?=[A-Z][a-z])", string) if word])

    # Put match case words back together
    if len(match_case) > 0:
        match_case_terms = {}
        for _match in match_case:
            split_term = " ".join([w for w in re.split(r"(?=[A-Z][a-z])", _match) if w])
            match_case_terms[_match] = split_term

        for phrase, split_phrase in match_case_terms.items():
            words = re.sub(
                rf"(^|[-_ \d]){re.escape(split_phrase)}([-_ \d]|$)",
                rf"\1{phrase}\2",
                words,
                flags=re.I,
            )

    return words


def split_words(
    string: str,
) -> list[str]:
    """Split a string into a list of words. Ignore single letters, special characters, and numbers.

    Args:
        string (str): String to split into words.

    Returns:
        list[str]: List of words.
    """
    string = strip_special_chars(string)
    return [
        w for w in re.split(r"[-_ \.]+", string) if re.match(r"^\d*[A-Z]+\d*[A-Z]+\d*$", w.upper())
    ]


def strip_special_chars(string: str, replacement: str = "") -> str:
    """Strip special characters from a string.

    Args:
        string (str): String to strip special characters from.
        replacement (str, optional): Replacement character. Defaults to "".

    Returns:
        str: String with special characters stripped.
    """
    return re.sub(r"[^\w\d_ -]", replacement, string)


def strip_stopwords(string: str, stopwords: list[str] = []) -> str:
    """Strip stopwords from the new filename.

    Args:
        string(str): String to strip stopwords from.
        stopwords (list[str], optional): List of additional stopwords to strip. Defaults to [].

    Returns:
        str: String with stopwords stripped.
    """
    common_english_stopwords = [
        "a",
        "able",
        "ableabout",
        "about",
        "above",
        "abroad",
        "abst",
        "accordance",
        "according",
        "accordingly",
        "across",
        "act",
        "actually",
        "ad",
        "added",
        "adj",
        "adopted",
        "ae",
        "af",
        "affected",
        "affecting",
        "affects",
        "after",
        "afterwards",
        "ag",
        "again",
        "against",
        "ago",
        "ah",
        "ahead",
        "ai",
        "ain't",
        "aint",
        "al",
        "all",
        "allow",
        "allows",
        "almost",
        "alone",
        "along",
        "alongside",
        "already",
        "also",
        "although",
        "always",
        "am",
        "amid",
        "amidst",
        "among",
        "amongst",
        "amoungst",
        "amount",
        "an",
        "and",
        "announce",
        "another",
        "any",
        "anybody",
        "anyhow",
        "anymore",
        "anyone",
        "anything",
        "anyway",
        "anyways",
        "anywhere",
        "ao",
        "apart",
        "apparently",
        "appear",
        "appreciate",
        "appropriate",
        "approximately",
        "aq",
        "ar",
        "are",
        "area",
        "areas",
        "aren",
        "aren't",
        "arent",
        "arise",
        "around",
        "arpa",
        "as",
        "aside",
        "ask",
        "asked",
        "asking",
        "asks",
        "associated",
        "at",
        "au",
        "auth",
        "available",
        "aw",
        "away",
        "awfully",
        "az",
        "b",
        "ba",
        "back",
        "backed",
        "backing",
        "backs",
        "backward",
        "backwards",
        "bb",
        "bd",
        "be",
        "became",
        "because",
        "become",
        "becomes",
        "becoming",
        "been",
        "before",
        "beforehand",
        "began",
        "begin",
        "beginning",
        "beginnings",
        "begins",
        "behind",
        "being",
        "beings",
        "believe",
        "below",
        "beside",
        "besides",
        "better",
        "between",
        "beyond",
        "bf",
        "bg",
        "bh",
        "bi",
        "big",
        "bill",
        "billion",
        "biol",
        "bj",
        "bm",
        "bn",
        "bo",
        "both",
        "bottom",
        "br",
        "brief",
        "briefly",
        "bs",
        "bt",
        "but",
        "buy",
        "bv",
        "bw",
        "by",
        "bz",
        "c",
        "c'mon",
        "c's",
        "ca",
        "call",
        "came",
        "can",
        "can't",
        "cannot",
        "cant",
        "caption",
        "cause",
        "causes",
        "cc",
        "cd",
        "certain",
        "certainly",
        "cf",
        "cg",
        "ch",
        "ci",
        "ck",
        "cl",
        "clear",
        "clearly",
        "click",
        "cm",
        "cmon",
        "cn",
        "co",
        "co.",
        "com",
        "come",
        "comes",
        "computer",
        "con",
        "concerning",
        "consequently",
        "consider",
        "considering",
        "contain",
        "containing",
        "contains",
        "copy",
        "corresponding",
        "could",
        "could've",
        "couldn",
        "couldn't",
        "couldnt",
        "course",
        "cr",
        "cry",
        "cs",
        "cu",
        "currently",
        "cv",
        "cx",
        "cy",
        "cz",
        "d",
        "dare",
        "daren't",
        "darent",
        "de",
        "dear",
        "definitely",
        "describe",
        "described",
        "despite",
        "did",
        "didn",
        "didn't",
        "didnt",
        "differ",
        "different",
        "differently",
        "directly",
        "dj",
        "dk",
        "dm",
        "do",
        "does",
        "doesn",
        "doesn't",
        "doesnt",
        "doing",
        "don",
        "don't",
        "done",
        "dont",
        "doubtful",
        "down",
        "downed",
        "downs",
        "downwards",
        "due",
        "during",
        "dz",
        "e",
        "each",
        "early",
        "ec",
        "ed",
        "edu",
        "ee",
        "effect",
        "eg",
        "eh",
        "either",
        "eleven",
        "else",
        "elsewhere",
        "empty",
        "end",
        "ended",
        "ending",
        "ends",
        "enough",
        "entirely",
        "er",
        "es",
        "especially",
        "et",
        "et-al",
        "etc",
        "even",
        "evenly",
        "ever",
        "evermore",
        "every",
        "everybody",
        "everyone",
        "everything",
        "everywhere",
        "ex",
        "exactly",
        "example",
        "except",
        "f",
        "face",
        "faces",
        "fairly",
        "far",
        "farther",
        "felt",
        "few",
        "fewer",
        "ff",
        "fi",
        "fifth",
        "fify",
        "fill",
        "find",
        "finds",
        "fire",
        "first",
        "fix",
        "fj",
        "fk",
        "fm",
        "fo",
        "followed",
        "following",
        "follows",
        "for",
        "forever",
        "former",
        "formerly",
        "forth",
        "forty",
        "forward",
        "found",
        "fr",
        "free",
        "from",
        "front",
        "full",
        "fully",
        "further",
        "furthered",
        "furthering",
        "furthermore",
        "furthers",
        "fx",
        "g",
        "ga",
        "gave",
        "gb",
        "gd",
        "ge",
        "general",
        "generally",
        "get",
        "gets",
        "getting",
        "gf",
        "gg",
        "gh",
        "gi",
        "give",
        "given",
        "gives",
        "giving",
        "gl",
        "gm",
        "gmt",
        "gn",
        "go",
        "goes",
        "going",
        "gone",
        "good",
        "goods",
        "got",
        "gotten",
        "gov",
        "gp",
        "gq",
        "gr",
        "great",
        "greater",
        "greatest",
        "greetings",
        "grouping",
        "gs",
        "gt",
        "gu",
        "gw",
        "gy",
        "h",
        "had",
        "hadn't",
        "hadnt",
        "half",
        "happens",
        "hardly",
        "has",
        "hasn",
        "hasn't",
        "hasnt",
        "have",
        "haven",
        "haven't",
        "havent",
        "having",
        "he",
        "he'd",
        "he'll",
        "he's",
        "hed",
        "hell",
        "hello",
        "help",
        "hence",
        "her",
        "here",
        "here's",
        "hereafter",
        "hereby",
        "herein",
        "heres",
        "hereupon",
        "hers",
        "herself",
        "herse”",
        "hes",
        "hi",
        "hid",
        "highest",
        "him",
        "himself",
        "himse”",
        "his",
        "hither",
        "hk",
        "hm",
        "hn",
        "hopefully",
        "how",
        "how'd",
        "how'll",
        "how's",
        "howbeit",
        "however",
        "hr",
        "ht",
        "htm",
        "html",
        "hu",
        "i",
        "i'd",
        "i'll",
        "i'm",
        "i've",
        "i.e.",
        "id",
        "ie",
        "if",
        "ignored",
        "ii",
        "il",
        "ill",
        "im",
        "immediate",
        "immediately",
        "importance",
        "important",
        "in",
        "inasmuch",
        "inc",
        "inc.",
        "indeed",
        "indicate",
        "indicated",
        "indicates",
        "inner",
        "inside",
        "insofar",
        "instead",
        "int",
        "interest",
        "interested",
        "interesting",
        "interests",
        "into",
        "inward",
        "io",
        "iq",
        "ir",
        "is",
        "isn",
        "isn't",
        "isnt",
        "it",
        "it'd",
        "it'll",
        "it's",
        "itd",
        "itll",
        "its",
        "itself",
        "ive",
        "j",
        "je",
        "jm",
        "jo",
        "join",
        "jp",
        "just",
        "k",
        "ke",
        "keep",
        "keeps",
        "kept",
        "kg",
        "kh",
        "ki",
        "kind",
        "km",
        "kn",
        "knew",
        "know",
        "known",
        "knows",
        "kp",
        "kr",
        "kw",
        "ky",
        "kz",
        "l",
        "la",
        "largely",
        "last",
        "lately",
        "later",
        "latest",
        "latter",
        "latterly",
        "lb",
        "lc",
        "least",
        "length",
        "less",
        "lest",
        "let",
        "let's",
        "lets",
        "li",
        "like",
        "liked",
        "likely",
        "likewise",
        "line",
        "little",
        "lk",
        "ll",
        "long",
        "longer",
        "longest",
        "look",
        "looking",
        "looks",
        "lower",
        "lr",
        "ls",
        "lt",
        "ltd",
        "lu",
        "lv",
        "ly",
        "m",
        "ma",
        "made",
        "mainly",
        "make",
        "makes",
        "making",
        "man",
        "many",
        "may",
        "maybe",
        "mayn't",
        "maynt",
        "mc",
        "md",
        "me",
        "mean",
        "means",
        "meantime",
        "meanwhile",
        "member",
        "members",
        "men",
        "merely",
        "mg",
        "mh",
        "might",
        "might've",
        "mightn't",
        "mightnt",
        "mil",
        "mill",
        "million",
        "minus",
        "miss",
        "mk",
        "ml",
        "mm",
        "mn",
        "mo",
        "more",
        "moreover",
        "most",
        "mostly",
        "move",
        "mp",
        "mq",
        "mr",
        "mrs",
        "ms",
        "msie",
        "mt",
        "mu",
        "much",
        "mug",
        "must",
        "must've",
        "mustn't",
        "mustnt",
        "mv",
        "mw",
        "mx",
        "my",
        "myself",
        "mz",
        "n",
        "na",
        "namely",
        "nay",
        "nc",
        "nd",
        "ne",
        "near",
        "nearly",
        "necessarily",
        "necessary",
        "need",
        "needed",
        "needing",
        "needn't",
        "neednt",
        "needs",
        "neither",
        "never",
        "neverf",
        "neverless",
        "nevertheless",
        "newest",
        "next",
        "nf",
        "ng",
        "ni",
        "nl",
        "no",
        "no-one",
        "nobody",
        "none",
        "nonetheless",
        "noone",
        "nor",
        "normally",
        "nos",
        "noted",
        "nothing",
        "notwithstanding",
        "now",
        "nowhere",
        "np",
        "nr",
        "nu",
        "null",
        "nz",
        "o",
        "obtain",
        "obtained",
        "obviously",
        "of",
        "off",
        "often",
        "oh",
        "ok",
        "okay",
        "older",
        "oldest",
        "om",
        "omitted",
        "on",
        "once",
        "one's",
        "ones",
        "only",
        "onto",
        "open",
        "opened",
        "opening",
        "opposite",
        "or",
        "ord",
        "ordered",
        "ordering",
        "other",
        "others",
        "otherwise",
        "ought",
        "oughtn't",
        "oughtnt",
        "our",
        "ours",
        "ourselves",
        "out",
        "outside",
        "over",
        "overall",
        "owing",
        "own",
        "p",
        "pa",
        "page",
        "pages",
        "parted",
        "particular",
        "particularly",
        "parting",
        "parts",
        "past",
        "pe",
        "per",
        "perhaps",
        "pf",
        "pg",
        "ph",
        "pk",
        "pl",
        "placed",
        "please",
        "plus",
        "pm",
        "pmid",
        "pn",
        "point",
        "pointed",
        "pointing",
        "poorly",
        "possible",
        "possibly",
        "potentially",
        "pp",
        "pr",
        "predominantly",
        "present",
        "presented",
        "presenting",
        "presents",
        "presumably",
        "previously",
        "primarily",
        "probably",
        "problem",
        "problems",
        "promptly",
        "proud",
        "provided",
        "provides",
        "pt",
        "put",
        "puts",
        "pw",
        "py",
        "q",
        "qa",
        "que",
        "quickly",
        "quite",
        "qv",
        "r",
        "ran",
        "rather",
        "rd",
        "re",
        "readily",
        "really",
        "reasonably",
        "recent",
        "recently",
        "ref",
        "refs",
        "regarding",
        "regardless",
        "regards",
        "related",
        "relatively",
        "research",
        "reserved",
        "respectively",
        "resulted",
        "resulting",
        "results",
        "right",
        "ring",
        "ro",
        "round",
        "ru",
        "run",
        "rw",
        "s",
        "sa",
        "said",
        "same",
        "saw",
        "say",
        "saying",
        "says",
        "sb",
        "sc",
        "sd",
        "se",
        "sec",
        "second",
        "secondly",
        "seconds",
        "section",
        "see",
        "seeing",
        "seem",
        "seemed",
        "seeming",
        "seems",
        "seen",
        "sees",
        "self",
        "selves",
        "sensible",
        "serious",
        "seriously",
        "several",
        "sg",
        "sh",
        "shall",
        "shan't",
        "shant",
        "she",
        "she'd",
        "she'll",
        "she's",
        "shed",
        "shell",
        "shes",
        "should",
        "should've",
        "shouldn",
        "shouldn't",
        "shouldnt",
        "showed",
        "showing",
        "shown",
        "showns",
        "shows",
        "si",
        "side",
        "sides",
        "significant",
        "significantly",
        "similar",
        "similarly",
        "since",
        "sincere",
        "site",
        "sj",
        "sk",
        "sl",
        "slightly",
        "sm",
        "small",
        "smaller",
        "smallest",
        "sn",
        "so",
        "some",
        "somebody",
        "someday",
        "somehow",
        "someone",
        "somethan",
        "something",
        "sometime",
        "sometimes",
        "somewhat",
        "somewhere",
        "soon",
        "sorry",
        "specifically",
        "specified",
        "specify",
        "specifying",
        "st",
        "still",
        "stop",
        "strongly",
        "su",
        "sub",
        "substantially",
        "successfully",
        "such",
        "sufficiently",
        "suggest",
        "sup",
        "sure",
        "sv",
        "sy",
        "system",
        "sz",
        "t",
        "t's",
        "take",
        "taken",
        "taking",
        "tc",
        "td",
        "tell",
        "ten",
        "tends",
        "test",
        "text",
        "tf",
        "tg",
        "th",
        "than",
        "thank",
        "thanks",
        "thanx",
        "that",
        "that'll",
        "that's",
        "that've",
        "thatll",
        "thats",
        "thatve",
        "the",
        "their",
        "theirs",
        "them",
        "themselves",
        "then",
        "thence",
        "there",
        "there'd",
        "there'll",
        "there're",
        "there's",
        "there've",
        "thereafter",
        "thereby",
        "thered",
        "therefore",
        "therein",
        "therell",
        "thereof",
        "therere",
        "theres",
        "thereto",
        "thereupon",
        "thereve",
        "these",
        "they",
        "they'd",
        "they'll",
        "they're",
        "they've",
        "theyd",
        "theyll",
        "theyre",
        "theyve",
        "thick",
        "thin",
        "thing",
        "things",
        "think",
        "thinks",
        "third",
        "this",
        "thorough",
        "thoroughly",
        "those",
        "thou",
        "though",
        "thoughh",
        "thought",
        "thoughts",
        "thousand",
        "throug",
        "through",
        "throughout",
        "thru",
        "thus",
        "til",
        "till",
        "tip",
        "tis",
        "tj",
        "tk",
        "tm",
        "tn",
        "to",
        "today",
        "together",
        "too",
        "took",
        "top",
        "toward",
        "towards",
        "tp",
        "tr",
        "tried",
        "tries",
        "trillion",
        "truly",
        "try",
        "trying",
        "ts",
        "tt",
        "turn",
        "turned",
        "turning",
        "turns",
        "tw",
        "twas",
        "twice",
        "tz",
        "u",
        "ua",
        "ug",
        "uk",
        "um",
        "un",
        "under",
        "underneath",
        "undoing",
        "unfortunately",
        "unless",
        "unlike",
        "unlikely",
        "until",
        "unto",
        "up",
        "upon",
        "ups",
        "upwards",
        "us",
        "used",
        "useful",
        "usefully",
        "usefulness",
        "uses",
        "using",
        "usually",
        "uucp",
        "uy",
        "uz",
        "v",
        "va",
        "value",
        "various",
        "vc",
        "ve",
        "versus",
        "very",
        "vg",
        "vi",
        "via",
        "viz",
        "vn",
        "vol",
        "vols",
        "vs",
        "vu",
        "w",
        "want",
        "wanted",
        "wanting",
        "wants",
        "was",
        "wasn",
        "wasn't",
        "wasnt",
        "way",
        "ways",
        "we",
        "we'd",
        "we'll",
        "we're",
        "we've",
        "wed",
        "well",
        "went",
        "were",
        "weren",
        "weren't",
        "werent",
        "weve",
        "wf",
        "what",
        "what'd",
        "what'll",
        "what's",
        "what've",
        "whatever",
        "whatll",
        "whats",
        "whatve",
        "when",
        "when'd",
        "when'll",
        "when's",
        "whence",
        "whenever",
        "where",
        "where'd",
        "where'll",
        "where's",
        "whereafter",
        "whereas",
        "whereby",
        "wherein",
        "wheres",
        "whereupon",
        "wherever",
        "whether",
        "which",
        "whichever",
        "while",
        "whilst",
        "whim",
        "whither",
        "who",
        "who'd",
        "who'll",
        "who's",
        "whod",
        "whoever",
        "whole",
        "wholl",
        "whom",
        "whomever",
        "whos",
        "whose",
        "why",
        "why'd",
        "why'll",
        "why's",
        "widely",
        "width",
        "will",
        "willing",
        "wish",
        "with",
        "within",
        "without",
        "won",
        "won't",
        "wonder",
        "wont",
        "work",
        "worked",
        "working",
        "works",
        "world",
        "would",
        "would've",
        "wouldn",
        "wouldn't",
        "wouldnt",
        "ws",
        "www",
        "x",
        "y",
        "ye",
        "year",
        "years",
        "yes",
        "yet",
        "you",
        "you'd",
        "you'll",
        "you're",
        "you've",
        "youd",
        "youll",
        "young",
        "younger",
        "youngest",
        "your",
        "youre",
        "yours",
        "yourself",
        "yourselves",
        "youve",
        "yt",
        "yu",
        "z",
        "za",
        "zero",
        "zm",
        "zr",
    ]

    tmp_string = string
    common_english_stopwords.extend(stopwords)

    for word in common_english_stopwords:
        tmp_string = re.sub(
            rf"(^|[^A-Za-z0-9]){re.escape(word)}([^A-Za-z0-9]|$)",
            r"\1\2",
            tmp_string,
            flags=re.I,
        )

    if re.match(r"^.$|^$|^[- _]+$", tmp_string):
        log.trace(f"Skip stripping stopwords. String is empty: {string}")
        return string

    return tmp_string.strip(" -_")


def transform_case(string: str, transform_case: TransformCase) -> str:
    """Transform the case of a string.

    Args:
        string (str): String to transform case of.
        transform_case (TransformCase): Case to transform to.

    Returns:
        str: Transformed string.
    """
    match transform_case:
        case TransformCase.LOWER:
            return string.lower()
        case TransformCase.UPPER:
            return string.upper()
        case TransformCase.TITLE:
            return string.title()
        case TransformCase.CAMELCASE:
            return re.sub(r"[-_ ]", "", string.title())
        case TransformCase.SENTENCE:
            return string.capitalize()
        case _:
            return string
