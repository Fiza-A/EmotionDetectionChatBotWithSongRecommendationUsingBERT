SELF_HARM_PATTERNS = (
    "kill myself",
    "end my life",
    "suicide",
    "self harm",
    "hurt myself",
    "i want to die",
    "can't go on",
    "cant go on",
)


def has_self_harm_intent(text: str) -> bool:
    normalized = text.lower()
    return any(pattern in normalized for pattern in SELF_HARM_PATTERNS)


def safety_response() -> str:
    return (
        "I’m really sorry you’re feeling this much pain. I can’t provide crisis care, but you deserve immediate support: "
        "please contact a trusted person now or call your local emergency number. If you’re in India, you can contact "
        "KIRAN at 1800-599-0019; if you’re in the US or Canada, call or text 988."
    )
