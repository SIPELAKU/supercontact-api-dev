from user_agents import parse

def parse_user_agent(user_agent: str) -> tuple[str, str]:
    ua = parse(user_agent)

    browser = f"{ua.browser.family} on {ua.os.family}"

    device = (
        ua.device.model
        if ua.device.model
        else ua.os.family
    )

    return browser, device
