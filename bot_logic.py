# ===============================
# GUS BOT – WEBHOOK VERSION
# Emotion + GPT + Emoji Chain
# ===============================

import os
import csv
import random
from datetime import datetime
import nltk
from textblob import download_corpora
from nrclex import NRCLex
import openai

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, Filters

# =========================
# NLTK FIX (Railway safe)
# =========================
try:
    nltk.data.find("tokenizers/punkt")
except:
    nltk.download("punkt")

try:
    download_corpora.lite()
except:
    pass

# =========================
# ENV
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

LOG_FILE = "feedback_log.csv"

# =========================
# EMOJI CHAINS
# =========================
EMOJI_CHAINS = {
    "joy": ["😄✨🌈", "😊🌟🎉", "😁🎊💫"],
    "sadness": ["💙🌧️🌈", "🤍🫂✨", "😔💭💙"],
    "anger": ["😤🧘🌿", "😠🧊🧠", "🔥🛑🧊"],
    "fear": ["😟🛡️🌙", "😰💭💙", "😨🌤️🌈"],
    "neutral": ["🙂💭✨", "🤔📘💡", "😌🧠📌"],
}

CHAIN_SCORES = {(e, c): 0 for e in EMOJI_CHAINS for c in EMOJI_CHAINS[e]}

# =========================
# LOGGING
# =========================
def ensure_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                ["timestamp", "user_id", "emotion", "emoji_chain", "feedback", "text"]
            )

def log_feedback(uid, emotion, chain, fb, text):
    ensure_log()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            [datetime.now().isoformat(), uid, emotion, chain, fb, text]
        )

# =========================
# EMOTION DETECTION
# =========================
def detect_emotion(text):
    text = text.lower()

    if any(w in text for w in ["happy", "won", "success", "excited"]):
        return "joy"
    if any(w in text for w in ["sad", "hurt", "alone", "cry"]):
        return "sadness"
    if any(w in text for w in ["angry", "mad", "frustrated"]):
        return "anger"
    if any(w in text for w in ["scared", "afraid", "anxious", "worried"]):
        return "fear"

    emo = NRCLex(text)
    if emo.raw_emotion_scores:
        label = max(emo.raw_emotion_scores, key=emo.raw_emotion_scores.get)
        if label in EMOJI_CHAINS:
            return label

    return "neutral"

# =========================
# GPT REPLY
# =========================
def generate_reply(text, emotion):

    prompt = f"""
You are Gus, a warm, kind emotional support chatbot.
Reply in 1-2 short caring sentences.
No advice. No emojis.

User message: "{text}"
Emotion detected: {emotion}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except:
        return "I’m here with you, and I truly understand how that feels."

# =========================
# EMOJI PICKER
# =========================
def pick_chain(emotion):
    chains = EMOJI_CHAINS.get(emotion, EMOJI_CHAINS["neutral"])
    weights = [max(1, CHAIN_SCORES[(emotion, c)] + 1) for c in chains]
    return random.choices(chains, weights=weights, k=1)[0]

def keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👍", callback_data="fb_up"),
            InlineKeyboardButton("👎", callback_data="fb_down"),
        ]
    ])

# =========================
# HANDLERS
# =========================
def start(update, context):
    update.message.reply_text(
        "Hello 😊 I’m Gus.\n\nYou can share anything with me."
    )

def handle_text(update, context):
    user_text = update.message.text
    emotion = detect_emotion(user_text)
    chain = pick_chain(emotion)
    reply = generate_reply(user_text, emotion)

    context.user_data["last"] = {
        "emotion": emotion,
        "chain": chain,
        "text": user_text,
    }

    update.message.reply_text(
        f"{reply}\n{chain}",
        reply_markup=keyboard()
    )

def feedback(update, context):
    query = update.callback_query
    query.answer()

    last = context.user_data.get("last")
    if not last:
        query.edit_message_text("Send a message first 😊")
        return

    emotion = last["emotion"]
    chain = last["chain"]
    text = last["text"]

    if query.data == "fb_up":
        CHAIN_SCORES[(emotion, chain)] += 1
        fb = "UP"
        msg = "Thank you 💛"
    else:
        CHAIN_SCORES[(emotion, chain)] -= 1
        fb = "DOWN"
        msg = "I’ll improve 🙏"

    log_feedback(query.from_user.id, emotion, chain, fb, text)
    query.edit_message_text(msg)
