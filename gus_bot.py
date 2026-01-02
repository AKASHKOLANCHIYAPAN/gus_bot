# ===============================
# GUS BOT – FINAL INDIAN TONE VERSION (Railway Fixed)
# Emotion Accurate • Polite • Warm • Human
# ===============================

import os
import csv
import random
from datetime import datetime

# --------- NLTK + TEXTBLOB FIX FOR RAILWAY ----------
import nltk
import textblob
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

textblob.download_corpora.lite()
# -----------------------------------------------------

from nrclex import NRCLex
import openai

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
# ENVIRONMENT
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set")

openai.api_key = OPENAI_API_KEY

LOG_FILE = "feedback_log.csv"

# =========================
# EMOJI CHAINS
# =========================
EMOJI_CHAINS = {
    "joy":["😄🚀✨🌈","😊🌟🎉✨","😁🎊💫🌟","🤩🔥🚀✨","😄🙌✨🌟","😌☀️🌼💫","😄🌈⭐🎈","🌞💛🎵🎈","🎉😎🌟🎊","💫🌟🌈✨"],
    "sadness":["💙🤝🌧️➡️🌈","🤍🫂🌱✨","😔💭💙🌧️","🌧️📩💬🕯️","🫶💭🌈💙","😢🤝🕯️🌙","😞🌧️🧣💭","🫂🌈💌🌙","💧🕯️🌿💛","🌧️💙🧸🫂"],
    "anger":["😤➡️🧘‍♂️💨🌿","😠💭🧊🧠","😡🧱🛑🧊","😤📝🧠📌","😠🚦🧘💨","😣📌🧠🧊","😤💬🧊🧱","🔥💢🛑🧊","😠🛑⚡🧘","💢🧠🛡️🧊"],
    "fear":["😟🤝🛡️🌙","😰💭🫂💙","😨🔦🧭🌌","😟🌫️➡️🌤️🌈","😧📘🧠✨","😥🧘‍♀️💨🌿","😟📩💬🕯️","😰🫂💛🌿","😨🌙🛡️💭","😧💫🕯️🌌"],
    "disgust":["🤢🚫🧼🧽","😖🧽🧴🚿","😒✋🗑️🧻","🤮➡️🧊🧠🧼","😣🚿🧼🧽","😑🚫📦🗑️","😖🧹🧼🧴","🤢🗑️🚿🧼","😤🧴🧽🚫","😒💢🧼🧽"],
    "surprise":["😲💡✨🌟","🤯➡️🧘‍♂️💨","😮📌💭💡","😲🔍🧠✨","😮🎁🌟🎉","🤯🧊💬🧠","😯📘✨💡","😮💫📝🌈","😲🎉💭✨","🤯🌟💡📌"],
    "neutral":["🙂💭📌🧠","🤔📎🧠💡","😌📘💬✨","🙂🧠📊📌","🤝🙂💬📘","😐💭🧭📌","🙂📌✨🧠","😶📖🧠💡","😌📄💭📝","🤔📘📝💡"],
}

CHAIN_SCORES = {(e,c):0 for e in EMOJI_CHAINS for c in EMOJI_CHAINS[e]}

# =========================
# LOG
# =========================
def ensure_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE,"w",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow(["timestamp","user_id","emotion","emoji_chain","feedback","user_text"])

def log_feedback(uid,emotion,chain,fb,text):
    ensure_log()
    with open(LOG_FILE,"a",newline="",encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.now().isoformat(timespec="seconds"),uid,emotion,chain,fb,text])


# =========================
# EMOTION DETECTOR
# =========================
def detect_emotion(text: str) -> str:
    if not text:
        return "neutral"

    t = text.lower().strip()

    sadness = [
        "sad","cry","crying","hurt","broken","heartbreak","left me","ignored","avoid me",
        "alone","lonely","empty","pain","miss","missing","cheated","betrayed",
        "failed","lost marks","lost job","accident","hospital","injured",
        "passed away","died","funeral","tired","exhausted","drained","mentally tired"
    ]

    joy = [
        "happy","so happy","excited","won","passed","cleared","success","achievement",
        "promotion","selected","got job","accepted","proposal accepted","celebration","good news"
    ]

    anger = [
        "angry","mad","frustrated","irritated","annoyed","pissed","rage","furious",
        "fight","argument","shouted","insulted","disrespected","humiliated","treated badly"
    ]

    fear = [
        "scared","afraid","panic","anxiety","worried","tensed",
        "stress","stressed","nervous","uncertain","shaking"
    ]

    disgust = [
        "disgust","gross","yuck","nasty","cringe","sick of this"
    ]

    surprise = [
        "shocked","surprised","unexpected","can't believe","suddenly","out of nowhere"
    ]

    def match(words): 
        return any(w in t for w in words)

    if match(sadness): return "sadness"
    if match(joy): return "joy"
    if match(anger): return "anger"
    if match(fear): return "fear"
    if match(disgust): return "disgust"
    if match(surprise): return "surprise"

    if "cheated" in t or "betrayed" in t or "unfaithful" in t:
        return "sadness"

    emo = NRCLex(text)
    scores = dict(emo.raw_emotion_scores)
    if scores:
        label = max(scores,key=scores.get)
        mapping = {
            "joy":"joy","sadness":"sadness","anger":"anger",
            "fear":"fear","disgust":"disgust","surprise":"surprise"
        }
        if label in mapping:
            return mapping[label]

    return "sadness"


# =========================
# EMOJI SELECTOR
# =========================
def pick_chain(emotion):
    chains = EMOJI_CHAINS[emotion]
    weights = [max(1,CHAIN_SCORES[(emotion,c)]+1) for c in chains]
    return random.choices(chains,weights=weights,k=1)[0]

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👍",callback_data="fb_up"),
         InlineKeyboardButton("👎",callback_data="fb_down")]
    ])


# =========================
# CHATGPT — INDIAN POLITE HUMAN TONE
# =========================
def generate_reply(text,emotion):
    styles = {
        "sadness":"very gentle, humble, comforting indian tone",
        "joy":"warm indian happiness, graceful and proud tone",
        "anger":"calm, respectful, soothing tone acknowledging hurt",
        "fear":"reassuring, kind, protective tone",
        "disgust":"understanding and validating tone",
        "surprise":"soft grounding tone",
        "neutral":"kind indian-friendly tone"
    }

    prompt = f"""
You are Gus, a very kind and emotionally mature Indian-style support companion.

Rules:
• Sound like a calm Indian friend
• Be soft, kind, respectful, heartfelt
• Reply only 1–2 short sentences
• No advice, no questions
• No robotic motivation
• NO emojis (they are handled separately)

Emotion tone: {styles.get(emotion,'warm caring tone')}
User: "{text}"
"""

    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=80,
            temperature=0.9
        )
        return res.choices[0].message.content.strip()
    except:
        fallback = {
            "sadness":"That truly sounds heavy… I’m really sorry you’re going through this.",
            "joy":"That’s genuinely wonderful to hear, I’m really happy for you.",
            "anger":"Anyone would feel hurt in a situation like that, your feelings are valid.",
            "fear":"That sounds overwhelming, but you are not alone in this.",
            "disgust":"That really does sound uncomfortable, I can understand why it affected you.",
            "surprise":"That must have come as quite a shock, take a moment to breathe.",
            "neutral":"I’m right here for you, whenever you feel like sharing."
        }
        return fallback.get(emotion,"I’m here for you.")


# =========================
# TELEGRAM HANDLERS
# =========================
def start(update,context):
    update.message.reply_text(
        "vanakam naba/nanbis.., I’m Gus 😊\n\n"
        "You can share anything from your heart.\n"
        "I’ll reply gently with warmth and care, along with a small emoji chain.\n"
        "After my reply, kindly tap 👍 or 👎 — it helps me improve."
    )

def handle_text(update,context):
    user_text = update.message.text or ""
    emotion = detect_emotion(user_text)
    chain = pick_chain(emotion)
    reply = generate_reply(user_text,emotion)

    context.user_data["last"]={"emotion":emotion,"chain":chain,"text":user_text}

    update.message.reply_text(
        f"{reply}\n{chain}\n\nKindly click your feedback (👍 or 👎).",
        reply_markup=keyboard()
    )

def feedback(update,context):
    q = update.callback_query
    q.answer()

    last = context.user_data.get("last")
    if not last:
        q.edit_message_text("Please share something first 😊")
        return

    emo,chain,text = last["emotion"],last["chain"],last["text"]

    if q.data=="fb_up":
        CHAIN_SCORES[(emo,chain)]+=1
        msg="Thank you so much 💛 Your feedback truly helps me get better."
        fb="UP"
    else:
        CHAIN_SCORES[(emo,chain)]-=1
        msg="Thank you for telling me 🙏 I’ll surely try to improve."
        fb="DOWN"

    log_feedback(q.from_user.id,emo,chain,fb,text)
    q.edit_message_text(msg)


# =========================
# MAIN
# =========================
def main():
    updater = Updater(token=BOT_TOKEN,use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start",start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command,handle_text))
    dp.add_handler(CallbackQueryHandler(feedback))

    updater.start_polling()
    updater.idle()

if __name__=="__main__":
    main()
