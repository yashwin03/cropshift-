"""
demo_data.py -- Predefined deterministic demo data for CropShift IVR.
Ensures IVR demo responses are fast, reliable, and decoupled from live external services/databases.
"""

DEMO_FARMER_NAME: str = "Raju Naik"

DEMO_RECOMMENDATION_PROMPTS: dict[str, str] = {
    "hi": (
        "Aapke khet ke liye hum groundnut shifaris karte hain. "
        "Anumanit avadhi 100 se 120 din hai. "
        "Main menu ke liye 9 dabayein, ya call samapt karne ke liye 0 dabayein."
    ),
    "kn": (
        "Namma sifarassu groundnut. Anumanita avadhi 100 rindha 120 dina. "
        "Main menu ge 9 otti, call mugiyalu 0 otti."
    ),
    "en": (
        "For your farm, we recommend groundnut. "
        "Expected duration is 100 to 120 days. "
        "Press 9 for main menu, or 0 to end call."
    ),
}

DEMO_MARKET_PROMPTS: dict[str, str] = {
    "hi": (
        "Aaj ka groundnut ka demo mandi bhav 6200 rupaye prati quintal hai. "
        "Main menu ke liye 9 dabayein, ya call samapt karne ke liye 0 dabayein."
    ),
    "kn": (
        "Eethindina groundnut demo market bele 6200 rupayi prati quintal ide. "
        "Main menu ge 9 otti, call mugiyalu 0 otti."
    ),
    "en": (
        "Today's demo market price for groundnut is 6200 rupees per quintal. "
        "Press 9 for main menu, or 0 to end call."
    ),
}

DEMO_SUBSIDY_PROMPTS: dict[str, str] = {
    "hi": (
        "Aap PM-KISAN yojana aur demo rajya krishi sahayata ke liye patra ho sakte hain. "
        "Main menu ke liye 9 dabayein, ya call samapt karne ke liye 0 dabayein."
    ),
    "kn": (
        "Neevu PM-KISAN yojana mattu demo rajya krishi sahayadhana galige arharaagiddira. "
        "Main menu ge 9 otti, call mugiyalu 0 otti."
    ),
    "en": (
        "You may be eligible for the PM-KISAN scheme and the demo state agriculture subsidy. "
        "Press 9 for main menu, or 0 to end call."
    ),
}
