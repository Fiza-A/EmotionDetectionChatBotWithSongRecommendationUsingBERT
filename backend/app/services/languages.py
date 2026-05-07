SUPPORTED_LANGUAGES = {
    "en": "English",
    "eng": "English",
    "english": "English",
    "hi": "Hindi",
    "hin": "Hindi",
    "hindi": "Hindi",
    "ta": "Tamil",
    "tam": "Tamil",
    "tamil": "Tamil",
    "te": "Telugu",
    "tel": "Telugu",
    "telugu": "Telugu",
    "ml": "Malayalam",
    "mal": "Malayalam",
    "malayalam": "Malayalam",
    "kn": "Kannada",
    "kan": "Kannada",
    "kannada": "Kannada",
    "bn": "Bengali",
    "ben": "Bengali",
    "bengali": "Bengali",
    "mr": "Marathi",
    "mar": "Marathi",
    "marathi": "Marathi",
    "pa": "Punjabi",
    "pan": "Punjabi",
    "punjabi": "Punjabi",
    "gu": "Gujarati",
    "guj": "Gujarati",
    "gujarati": "Gujarati",
}


def normalize_languages(languages: list[str]) -> list[str]:
    normalized: list[str] = []
    for language in languages:
        canonical = SUPPORTED_LANGUAGES.get(language.strip().lower())
        if canonical and canonical not in normalized:
            normalized.append(canonical)
    return normalized
