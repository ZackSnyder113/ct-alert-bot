import requests
import json
import os

API_URL = "https://api.dexscreener.com/community-takeovers/latest/v1"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SEEN_FILE = "seen_takeovers.json"


def get_takeovers():
    response = requests.get(API_URL, timeout=15)
    response.raise_for_status()
    return response.json()


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return None

    with open(SEEN_FILE, "r") as file:
        data = json.load(file)

    return {tuple(item) for item in data}


def save_seen(seen):
    with open(SEEN_FILE, "w") as file:
        json.dump([list(item) for item in seen], file)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data, timeout=15)
    response.raise_for_status()


def takeover_id(takeover):
    return (
        takeover.get("chainId", ""),
        takeover.get("tokenAddress", ""),
        takeover.get("claimDate", "")
    )


print("CT Alert Bot started...")

seen = load_seen()
takeovers = get_takeovers()

print(f"Found {len(takeovers)} takeovers")

current_ids = {
    takeover_id(takeover)
    for takeover in takeovers
}


# First run
if seen is None:

    seen = current_ids
    save_seen(seen)

    print("First run completed.")
    print("Existing takeovers saved.")
    print("No alerts sent.")

else:

    for takeover in takeovers:

        current_id = takeover_id(takeover)

        if current_id in seen:
            continue

        chain = takeover.get("chainId", "Unknown")
        token = takeover.get("tokenAddress", "Unknown")
        description = takeover.get("description") or "No description"
        claim_date = takeover.get("claimDate", "Unknown")

        message = (
            "🚨 NEW COMMUNITY TAKEOVER\n\n"
            f"Chain: {chain}\n"
            f"Token: {token}\n\n"
            f"{description}\n\n"
            f"Claim Date: {claim_date}"
        )

        send_telegram(message)

        print("NEW TAKEOVER:", token)

        seen.add(current_id)

    save_seen(seen)

print("Done.")
