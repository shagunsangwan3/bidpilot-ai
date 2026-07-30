import re


def parse_user_agent(ua: str | None) -> tuple[str | None, str | None]:
    """Lightweight best-effort (browser, operating_system) extraction from a
    User-Agent string. Not exhaustive — covers the common desktop/mobile
    browsers and OSes well enough for a login-history display. A dedicated
    parsing library would be more thorough; this avoids adding one for what's
    ultimately decorative information on a settings page.
    """
    if not ua:
        return None, None

    browser = None
    for name, pattern in [
        ("Edge", r"Edg/"),
        ("Chrome", r"Chrome/"),
        ("Firefox", r"Firefox/"),
        ("Safari", r"Version/.*Safari/"),
        ("Opera", r"OPR/"),
    ]:
        if re.search(pattern, ua):
            browser = name
            break

    os_name = None
    for name, pattern in [
        ("Windows", r"Windows"),
        ("macOS", r"Mac OS X"),
        ("iOS", r"iPhone|iPad"),
        ("Android", r"Android"),
        ("Linux", r"Linux"),
    ]:
        if re.search(pattern, ua):
            os_name = name
            break

    return browser, os_name
