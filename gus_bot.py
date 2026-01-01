import os
import csv
import random
from datetime import datetime

from nrclex import NRCLex

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    CallbackContext,
)

# =========================
# 1) CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_FILE = "feedback_log.csv"

EMOTIONS = ["joy", "sadness", "anger", "fear", "disgust", "surprise", "neutral"]

# PASTE YOUR TEXT_TEMPLATES HERE
TEXT_TEMPLATES = {
    "joy": [
        "Love that energy. Keep riding that wave.",
        "That’s a solid win. Keep going.",
        "Nice. You deserve that feeling.",
        "That sounds really good. Savor it.",
        "Moments like that charge you up. Remember them.",
        "You earned that smile. Let it stay a bit longer.",
        "So good to hear something positive from you.",
        "That’s a bright spot. Hold on to it.",
        "Your joy is valid. Let yourself feel it fully.",
        "That’s awesome. You’re doing better than you think.",
        "That feeling is important. Notice what created it.",
        "Great. Let’s see how you can keep this going.",
        "You sound genuinely lighter. That matters.",
        "Beautiful. Little wins stack into big changes.",
        "That’s the kind of update Gus likes to hear.",
        "You’re allowed to celebrate yourself, even for small things.",
        "Feels good when life cooperates a bit, right?",
        "That’s a green flag moment. Appreciate it.",
        "Keep that momentum. You’re on a good track.",
        "Nice. Screenshot this moment in your mind.",
    ],
    "sadness": [
        "That sounds really heavy. You don’t have to carry it alone.",
        "I’m sorry you’re going through that. It genuinely matters.",
        "Feeling low like this is tough. You’re still allowed to rest.",
        "You’re not weak for feeling this. You’re human.",
        "That hurts. It’s okay to give yourself time to process.",
        "You don’t have to fix everything today. Just breathe.",
        "Your pain is valid, even if others don’t see it.",
        "It’s okay if you don’t feel okay right now.",
        "Sometimes just putting it into words is the first step.",
        "You deserve kindness, especially from yourself right now.",
        "That sadness has a story. If you want, you can tell me more.",
        "Even if the day feels ruined, your story isn’t.",
        "You’re still here. That already means you’re stronger than you think.",
        "It’s okay to slow down. You’re not falling behind.",
        "You’re allowed to miss people and still move forward.",
        "Some chapters are just painful. It doesn’t mean the book is bad.",
        "You’re not a burden for feeling this way.",
        "Tears don’t mean failure. They mean you’re overwhelmed.",
        "Right now is hard, but it won’t always feel like this.",
        "You’re worthy of better days than this one.",
    ],
    "anger": [
        "That sounds really frustrating. Your reaction makes sense.",
        "Anger is a signal, not a flaw. Let’s look at what triggered it.",
        "You’re allowed to be angry. It doesn’t make you a bad person.",
        "Take a breath. You don’t have to solve it while you’re burning.",
        "That kind of situation would piss off anyone.",
        "Your boundaries were probably crossed. That matters.",
        "It’s okay to step back before you respond.",
        "Anger usually protects something soft underneath.",
        "You don’t have to suppress it, just don’t let it control you.",
        "Let’s turn that heat into clarity, not chaos.",
        "You can write everything you want to say, then decide what to send.",
        "Sometimes walking away is the strongest move.",
        "You deserve to be treated with respect, full stop.",
        "Your frustration is a sign that something isn’t okay for you.",
        "You can be angry and still choose a calm action.",
        "Try to pause before reacting. That pause is power.",
        "It’s okay if your patience snapped. You’ve been holding a lot.",
        "You’re not alone in feeling fed up by things like this.",
        "Let’s use this anger to define what you will and won’t accept.",
        "You can cool down and still stand firm about what hurt you.",
    ],
    "fear": [
        "That sounds scary. It’s okay to admit that.",
        "Anxiety can be loud, but it doesn’t mean it’s always right.",
        "You’re not alone in feeling nervous about this.",
        "Try breaking it into tiny steps. You don’t have to do everything at once.",
        "It makes sense you feel this way with so much pressure.",
        "You’re allowed to be afraid and still move slowly forward.",
        "Your fear is trying to protect you, even if it’s overreacting.",
        "Let’s focus on what you can control right now.",
        "You don’t have to see the whole path, just the next step.",
        "It’s okay to ask for help when things feel too big.",
        "Your worries are valid, but they’re not the whole truth.",
        "Sometimes the build‑up is worse than the thing itself.",
        "You’ve survived every hard moment up to now.",
        "Fear doesn’t mean you’re weak. It means you care.",
        "Breathe. In for 4, hold for 4, out for 6. Repeat a few times.",
        "It’s okay to slow down and ground yourself before acting.",
        "You’re not behind. You’re just overwhelmed.",
        "Let’s name the fear. Naming it makes it less blurry.",
        "Even if you feel shaky, you’re still showing up.",
        "You deserve to feel safe—in your body and in your choices.",
    ],
    "disgust": [
        "That sounds really unpleasant. Your reaction makes sense.",
        "It’s okay to feel turned off or grossed out by that.",
        "Your ‘nope’ instinct is allowed to exist.",
        "You don’t have to accept things that feel wrong to you.",
        "Sometimes distance is the healthiest response.",
        "You’re not overreacting if your values feel violated.",
        "You’re allowed to step away from people or situations that feel toxic.",
        "Your body and mind are saying ‘this isn’t right’—listen to that.",
        "Not everything deserves your tolerance or patience.",
        "You don’t have to keep engaging with what disgusts you.",
        "That feeling is telling you something important about your boundaries.",
        "It’s okay if something left a bad taste emotionally.",
        "You’re allowed to say, ‘I don’t like this, and I’m done.’",
        "You don’t have to justify why it feels gross. Your sense is enough.",
        "Cleansing your space—physically or digitally—can help.",
        "You’re not being dramatic. You’re reacting to something off.",
        "Sometimes the best move is to cut contact silently.",
        "You can protect your peace without explaining it to everyone.",
        "Your comfort level matters more than keeping things ‘polite’.",
        "If it feels wrong deep down, trust that signal.",
    ],
    "surprise": [
        "Interesting. That’s unexpected.",
        "Wow, that came out of nowhere.",
        "That must have caught you off guard.",
        "Life really dropped a plot twist there.",
        "Sometimes surprises are exhausting, even if they’re not bad.",
        "You’re allowed to need a moment to process it.",
        "Not knowing how to react immediately is completely normal.",
        "That’s a big shift from what you expected.",
        "It’s okay to say ‘I need time to think about this’.",
        "Your brain is just updating its map of the situation.",
        "Change like that can feel unreal at first.",
        "You can hold both ‘shocked’ and ‘curious’ at the same time.",
        "Let’s slow it down and see what this actually means for you.",
        "You don’t have to pretend you’re okay with it right away.",
        "Sometimes the most random events change a lot.",
        "You’re allowed to feel weird, even if others think it’s no big deal.",
        "It’s fine if your feelings haven’t caught up with the facts yet.",
        "You can ask questions until things make more sense.",
        "Your reaction doesn’t have to be perfect or logical.",
        "Even good surprises can be overwhelming at first.",
    ],
    "neutral": [
        "Got it. Tell me a bit more so I can understand clearly.",
        "Okay. What’s the main thing you want help with?",
        "I’m listening. You can unpack it at your own pace.",
        "Thanks for sharing. What part of this feels most important to you?",
        "Alright. What outcome are you hoping for here?",
        "I’m here. You can say it in messy draft mode first.",
        "Let’s break it down—what’s the core issue underneath?",
        "You don’t have to impress anyone here. Just be honest.",
        "Okay, let’s sort it step by step.",
        "Got it. Do you want validation, advice, or just a listener?",
        "You can talk about it in fragments. It doesn’t have to be perfect.",
        "I’m with you. What’s the part that keeps replaying in your head?",
        "Thanks for trusting me with this.",
        "We can map this like a problem: situation → thoughts → feelings.",
        "Okay. What feels confusing or stuck about this?",
        "Got it. What’s the worst‑case you’re afraid of here?",
        "You’re allowed to vent even if it’s not fully clear yet.",
        "Let’s make this less abstract—give me one concrete example.",
        "I’m here in the background, you can keep typing.",
        "Whenever you’re ready, we can turn this into a small plan.",
    ],
}  # Replace this with your templates

# 7 chains per emotion, each chain has 4+ emojis
EMOJI_CHAINS = {
    "joy": [
        "😄🚀✨🌈", "😊🌟🎉✨", "😁🎊💫🌟", "🤩🔥🚀✨", "😄🙌✨🌟", "😌☀️🌼💫", "😄🌈⭐🎈"
    ],
    "sadness": [
        "💙🤝🌧️➡️🌈", "🤍🫂🌱✨", "😔💭💙🌧️", "🌧️📩💬🕯️", "🫶💭🌈💙", "😢🤝🕯️🌙", "😞🌧️🧣💭"
    ],
    "anger": [
        "😤➡️🧘‍♂️💨🌿", "😠💭🧊🧠", "😡🧱🛑🧊", "😤📝🧠📌", "😠🚦🧘💨", "😣📌🧠🧊", "😤💬🧊🧱"
    ],
    "fear": [
        "😟🤝🛡️🌙", "😰💭🫂💙", "😨🔦🧭🌌", "😟🌫️➡️🌤️🌈", "😧📘🧠✨", "😥🧘‍♀️💨🌿", "😟📩💬🕯️"
    ],
    "disgust": [
        "🤢🚫🧼🧽", "😖🧽🧴🚿", "😒✋🗑️🧻", "🤮➡️🧊🧠🧼", "😣🚿🧼🧽", "😑🚫📦🗑️", "😖🧹🧼🧴"
    ],
    "surprise": [
        "😲💡✨🌟", "🤯➡️🧘‍♂️💨", "😮📌💭💡", "😲🔍🧠✨", "😮🎁🌟🎉", "🤯🧊💬🧠", "😯📘✨💡"
    ],
    "neutral": [
        "🙂💭📌🧠", "🤔📎🧠💡", "😌📘💬✨", "🙂🧠📊📌", "🤝🙂💬📘", "😐💭🧭📌", "🙂📌✨🧠"
    ],
}

# RL-style scores: (emotion, chain) -> score
CHAIN_SCORES = {(e, c): 0 for e in EMOJI_CHAINS for c in EMOJI_CHAINS[e]}


# =========================
# 2) UTILITIES
# =========================
def ensure_log_header():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "user_id", "emotion", "emoji_chain", "feedback", "user_text"])


def log_feedback(user_id: int, emotion: str, chain: str, feedback: str, user_text: str):
    ensure_log_header()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([datetime.now().isoformat(timespec="seconds"), user_id, emotion, chain, feedback, user_text])


def detect_emotion(text: str) -> str:
    if not text:
        return "neutral"

    t = text.lower()

    # Common phrases/words for each emotion (30+ per class)
    joy_words = [
        "happy", "so happy", "glad", "excited", "so excited", "awesome", "amazing",
        "great", "good mood", "joy", "thrilled", "delighted", "proud", "grateful",
        "won", "i won", "victory", "first prize", "top rank", "topped the exam",
        "passed", "cleared the exam", "promotion", "got the job", "got selected",
        "birthday", "my birthday", "anniversary", "celebration", "celebrating",
        "feeling positive", "feeling good", "feeling better"
    ]

    sadness_words = [
        "sad", "so sad", "depressed", "down", "downhearted", "upset", "low",
        "crying", "cried", "lonely", "alone", "empty", "numb", "broken",
        "rejected", "got rejected", "rejection", "breakup", "heartbroken",
        "failed", "i failed", "lost the exam", "lost marks", "lost someone",
        "miss them", "missing them", "hurt", "it hurts", "pain", "in pain",
        "disappointed", "discouraged", "hopeless", "no one cares"
    ]

    anger_words = [
        "angry", "so angry", "mad", "furious", "pissed", "pissed off",
        "irritated", "annoyed", "frustrated", "rage", "lost my temper",
        "screamed", "shouted", "hate this", "hate him", "hate her",
        "fed up", "done with this", "can't tolerate", "unfair", "unjust",
        "they used me", "they lied", "betrayed", "cheated me"
    ]

    fear_words = [
        "scared", "so scared", "afraid", "terrified", "nervous", "anxious",
        "anxiety", "panic", "panic attack", "worried", "stressed", "under stress",
        "tensed", "so tense", "fear", "fearful", "i can't do this", "what if",
        "overthinking", "over thinking", "i feel unsafe", "i feel not safe",
        "shaking", "shivering", "i am nervous", "i am anxious"
    ]

    disgust_words = [
        "disgusted", "disgusting", "gross", "nasty", "yuck", "ew", "so dirty",
        "filthy", "repulsive", "i hate this place", "this is sick",
        "this makes me sick", "i can't stand this", "cringe", "cringy",
    ]

    surprise_words = [
        "surprised", "so surprised", "shocked", "so shocked", "wow",
        "didn't expect", "never expected", "unexpected", "can't believe",
        "out of nowhere", "suddenly happened", "suddenly he", "suddenly she",
        "plot twist", "unbelievable"
    ]

    # 1) Base scores from NRCLex
    emo = NRCLex(text)
    scores = dict(emo.raw_emotion_scores)

    # 2) Bias scores with keyword matches
    def boost_if(words, key, amount=3):
        if any(w in t for w in words):
            scores[key] = scores.get(key, 0) + amount

    boost_if(joy_words, "joy")
    boost_if(sadness_words, "sadness")
    boost_if(anger_words, "anger")
    boost_if(fear_words, "fear")
    boost_if(disgust_words, "disgust")
    boost_if(surprise_words, "surprise")

    if not scores:
        return "neutral"

    total = sum(scores.values())
    probs = {k: v / total for k, v in scores.items()}
    label = max(probs, key=probs.get)
    score = probs[label]

    # 3) If low confidence, treat as neutral
    if score < 0.2:
        return "neutral"

    mapping = {
        "joy": "joy",
        "sadness": "sadness",
        "anger": "anger",
        "fear": "fear",
        "disgust": "disgust",
        "surprise": "surprise",
        "trust": "neutral",
        "anticipation": "neutral",
    }
    return mapping.get(label, "neutral")


def pick_chain(emotion: str) -> str:
    chains = EMOJI_CHAINS[emotion]
    weights = [max(1, CHAIN_SCORES[(emotion, c)] + 1) for c in chains]
    return random.choices(chains, weights=weights, k=1)[0]


def feedback_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton("👍", callback_data="fb_up"),
        InlineKeyboardButton("👎", callback_data="fb_down"),
    ]]
    return InlineKeyboardMarkup(keyboard)


# =========================
# 3) HANDLERS
# =========================
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hey! I'm Gus 😄\n\n"
        "Feeling low or overwhelmed?\n"
        "Just text me—no judgment.\n\n"
        "After my reply, tap 👍 or 👎 so I can improve."
    )


def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text(
        "How to use Gus:\n"
        "/start - Start\n"
        "/help - Help\n\n"
        "Send any message. Gus detects emotion and replies with text + emoji chain.\n"
        "Tap 👍/👎 to rate."
    )


def handle_text(update: Update, context: CallbackContext):
    user_text = update.message.text or ""

    emotion = detect_emotion(user_text)
    reply_text = random.choice(TEXT_TEMPLATES[emotion])
    chain = pick_chain(emotion)

    context.user_data["last"] = {
        "emotion": emotion,
        "chain": chain,
        "text": user_text,
    }

    msg = f"{reply_text} {chain}\n\nKindly click your feedback (👍 or 👎)."
    update.message.reply_text(msg, reply_markup=feedback_keyboard())


def on_feedback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    last = context.user_data.get("last")
    if not last:
        query.edit_message_text("No recent message to rate. Send a new text first.")
        return

    emotion = last["emotion"]
    chain = last["chain"]
    user_text = last["text"]

    if query.data == "fb_up":
        CHAIN_SCORES[(emotion, chain)] += 1
        log_feedback(query.from_user.id, emotion, chain, "UP", user_text)
        query.edit_message_text("Thanks! 👍 Feedback saved.")
    elif query.data == "fb_down":
        CHAIN_SCORES[(emotion, chain)] -= 1
        log_feedback(query.from_user.id, emotion, chain, "DOWN", user_text)
        query.edit_message_text("Thanks! 👎 Feedback saved.")
    else:
        query.edit_message_text("Unknown feedback option.")


# =========================
# 4) MAIN (PTB 13.15)
# =========================
def main():
    if "PASTE_YOUR_TOKEN_HERE" in BOT_TOKEN:
        raise ValueError("Set BOT_TOKEN env var or paste the token into BOT_TOKEN.")

    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(CallbackQueryHandler(on_feedback))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
