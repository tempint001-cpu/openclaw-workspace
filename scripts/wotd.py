#!/usr/bin/env python3
"""
Word Of The Day - proper implementation
✅ Checks existing used words FIRST before picking
✅ Never sends duplicates
✅ Automatically adds used word to history
✅ Outputs formatted message ready to send
"""

import json
import random
from pathlib import Path

HISTORY_FILE = Path(__file__).parent.parent / "memory" / "wotd-history.json"

WORDS = [
    # Word, pronunciation, definition, quote
    ("epicaricacy", "/ˌɛpɪkærɪˈkeɪsi/", "Pleasure derived from the misfortunes of others. The proper, actual word for schadenfreude.", "Sometimes you just have to quietly enjoy it."),
    ("sonder", "/ˈsɒndə/", "The realisation that every random stranger you pass has a life just as complex and vivid as your own.", "Everyone you meet is fighting a battle you know nothing about."),
    ("petrichor", "/ˈpɛtrɪkɔː/", "The pleasant smell that accompanies the first rain after a long period of warm, dry weather.", "The best smell in the world. No arguments."),
    ("defenestration", "/diːˌfɛnɪˈstreɪʃn/", "The act of throwing someone out of a window.", "A very specific, extremely satisfying word."),
    ("limerence", "/ˈlɪmərəns/", "The state of being completely infatuated with someone; that obsessive, can't stop thinking about them feeling.", "It never lasts. That's the point."),
    ("hiraeth", "/ˈhɪraɪθ/", "A homesickness for a home you never had, or a home that no longer exists.", "Not nostalgia. Something deeper."),
    ("numinous", "/ˈnjuːmɪnəs/", "Describes something that feels holy, magical, or deeply awe-inspiring in a way you can't explain.", "That feeling you get looking up at the stars at 3am."),
    ("psithurism", "/ˈsaɪθjʊrɪzəm/", "The sound of wind rustling through leaves in trees.", "One of the most peaceful sounds there is."),
    ("mellifluous", "/məˈlɪfluəs/", "A voice or sound that is smooth, sweet, and musical.", "The kind of voice you could listen to forever."),
    ("serendipity", "/ˌserənˈdɪpɪti/", "The occurrence of finding something good or valuable without looking for it — a happy accident.", "All the best things in life happen this way."),
    ("magnanimous", "/mæɡˈnænɪməs/", "Noble, generous, and forgiving. Especially towards someone you have defeated.", "The mark of someone who is actually strong."),
    ("ineffable", "/ɪnˈɛfəbəl/", "Too great, extreme, or beautiful to be described in words.", "Some things can not be explained. Only felt."),
    ("eudaimonia", "/juːdaɪˈmoʊniə/", "A state of lasting, deep fulfilment and human flourishing. Not temporary happiness. Not a good day.", "The quiet, steady feeling that your life is good, right, and as it should be."),
    ("ephemeral", "/ɪˈfemərəl/", "Lasting for a very short time. Fleeting. Gone before you even properly notice it was there.", "All the best moments are ephemeral. That's exactly what makes them perfect."),
]

def load_history():
    if not HISTORY_FILE.exists():
        return {"used": [], "lastUpdated": None}
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

def get_next_word():
    history = load_history()
    used = set(history["used"])
    
    available = [w for w in WORDS if w[0] not in used]
    
    if not available:
        # Reset when all words are used
        history["used"] = []
        available = WORDS
    
    word = random.choice(available)
    
    # Mark as used BEFORE returning
    history["used"].append(word[0])
    history["lastUpdated"] = "2026-04-11"
    save_history(history)
    
    return word

if __name__ == "__main__":
    word, pron, defn, quote = get_next_word()
    
    print(f"""📚 Word of the Day: **{word.title()}**

{defn}

Pronounced: {pron}

> *"{quote}"*

#Nexa #WOTD""")
