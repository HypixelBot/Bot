def error(text):
    return f"\N{NO ENTRY SIGN} {text}"


def warning(text):
    return f"\N{WARNING SIGN} {text}"


def info(text):
    return f"\N{INFORMATION SOURCE} {text}"


def question(text):
    return f"\N{BLACK QUESTION MARK ORNAMENT} {text}"


def bold(text):
    return f"**{text}**"


def box(text, lang=""):
    ret = f"```{lang}\n{text}\n```"
    return ret


def inline(text):
    return f"`{text}`"


def italics(text):
    return f"*{text}*"


def pagify(text, delims=["\n"], *, escape=True, shorten_by=8, page_length=2000):
    """DOES NOT RESPECT MARKDOWN BOXES OR INLINE CODE"""
    in_text = text
    if escape:
        num_mentions = text.count("@here") + text.count("@everyone")
        shorten_by += num_mentions
    page_length -= shorten_by
    while len(in_text) > page_length:
        closest_delim = max([in_text.rfind(d, 0, page_length)
                             for d in delims])
        closest_delim = closest_delim if closest_delim != -1 else page_length
        if escape:
            to_send = escape_mass_mentions(in_text[:closest_delim])
        else:
            to_send = in_text[:closest_delim]
        yield to_send
        in_text = in_text[closest_delim:]

    if escape:
        yield escape_mass_mentions(in_text)
    else:
        yield in_text


def strikethrough(text):
    return f"~~{text}~~"


def underline(text):
    return f"__{text}__"


def escape(text: str):
    text = text.replace("@everyone", "@\u200beveryone")
    text = text.replace("@here", "@\u200bhere")
    text = (text.replace("`", "\\`")
                .replace("*", "\\*")
                .replace("_", "\\_")
                .replace("~", "\\~"))
    return text


def escape_mass_mentions(text):
    return escape(text)
