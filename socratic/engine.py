"""
AI-sokratik suhbat dvigateli («Yoshga oid fiziologiya va gigiyena» fani).

Til modeli ishlatilmaydi: javob kalit so'zlar bo'yicha tahlil qilinadi va `scenarios.py`
dagi yo'naltiruvchi savollar zanjiri bo'ylab suhbat olib boriladi. Dvigatel hech qachon
tayyor javobni birinchi bo'lib aytmaydi — avval savol, keyin ishora, faqat ikki urinishdan
keyingina qisqa tushuntirish.

Holat (sessiyada saqlanadi, JSON'ga mos):
  topic   — mavzu kaliti yoki None (erkin savol rejimi)
  theme   — erkin rejimda foydalanuvchi savoli
  phase   — "choose" | "dialog" | "conclude" | "done"
  step    — joriy savol raqami
  tries   — joriy savoldagi mazmunli javoblar soni
  hints   — joriy savolda so'ralgan ishoralar; shorts — juda qisqa javoblar
  found   — joriy savolda topilgan tushunchalar; asked — berilgan aniqlashtiruvchi savollar
  learned — butun suhbatda topilgan tushunchalar
  turns   — [{"role": "bot"|"user", "text": ...}]
"""

import random
import re

from .scenarios import CONCLUDE_ASK, GENERIC_STEPS, TOPICS

MAX_TURNS = 80
MIN_WORDS = 3

APOSTROPHES = "'‘’ʻʼ`´"
HELP_WORDS = ["bilmayman", "bilmadim", "ishora", "yordam", "tushunmadim", "qiyin", "bilmiman", "yordam bering"]
FINISH_WORDS = ["yakunla", "tugat", "boldi yetar", "yetarli"]

ACK = ["Yaxshi fikr.", "Qiziq kuzatish.", "To‘g‘ri yo‘nalishdasiz.", "Ajoyib, fikringiz mantiqli.", "Zo‘r mulohaza."]
PARTIAL = ["«{found}» haqida to‘g‘ri aytdingiz.", "«{found}» — muhim nuqta, uni topdingiz.", "Siz «{found}»ni to‘g‘ri ilg‘adingiz."]
MISS = ["Hmm, keling, boshqa tomondan yondashamiz.", "Bu yerda biroz to‘xtab o‘ylab ko‘raylik.", "Fikringizni tushundim, lekin bir narsani aniqlashtiraylik."]
SHORT = ["Fikringizni biroz kengroq yozing: nima uchun aynan shunday deb o‘ylaysiz?",
         "Qisqa javob — yaxshi boshlanish. Endi uni asoslang: nega shunday?"]
NEXT = ["Keyingi savol:", "Endi bir qadam chuqurroq:", "Davom etamiz:"]


def normalize(text):
    text = (text or "").lower()
    for ch in APOSTROPHES:
        text = text.replace(ch, "")
    text = text.replace("₂", "2").replace("ё", "e")
    return re.sub(r"\s+", " ", text).strip()


def has_any(text, keywords):
    """Kalit so'z o'zagi so'z boshida uchraydimi (normallashtirilgan matnda)."""
    return any(re.search(r"(?<![\w])" + re.escape(normalize(kw)), text) for kw in keywords)


def new_state(topic=None):
    return {"topic": topic if topic in TOPICS else None, "theme": "", "phase": "choose", "step": 0,
            "tries": 0, "hints": 0, "shorts": 0, "found": [], "asked": [], "learned": [], "turns": []}


def detect_topic(text):
    norm = normalize(text)
    scores = {key: sum(1 for kw in t["detect"] if has_any(norm, [kw])) for key, t in TOPICS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else None


def steps_for(state):
    if state["topic"]:
        return TOPICS[state["topic"]]["steps"]
    return [{"ask": ask.format(theme=state["theme"] or "bu mavzu")} for ask in GENERIC_STEPS]


def progress(state):
    total = len(steps_for(state)) if state["phase"] != "choose" else 0
    step = total if state["phase"] in ("conclude", "done") else state["step"]
    return {"step": step, "total": total, "phase": state["phase"],
            "topic": state["topic"], "title": title(state)}


def title(state):
    if state["topic"]:
        return TOPICS[state["topic"]]["title"]
    if state["theme"]:
        return state["theme"][:60] + ("…" if len(state["theme"]) > 60 else "")
    return ""


def _rnd(state):
    return random.Random(f"{state['topic']}:{state['theme']}:{len(state['turns'])}")


def _say(state, text):
    if text.startswith("«") and len(text) > 1:
        text = "«" + text[1].upper() + text[2:]
    state["turns"].append({"role": "bot", "text": text})
    state["turns"] = state["turns"][-MAX_TURNS:]
    return text


def welcome_text():
    return ("Salom! Men AI-sokratik yordamchiman va «Yoshga oid fiziologiya va gigiyena» mavzularida suhbatlashaman. "
            "Tayyor javob bermayman — yo‘naltiruvchi savollar orqali mavzuni o‘zingiz tahlil qilishingizga yordam beraman.\n\n"
            "Quyidagi mavzulardan birini tanlang yoki o‘sib borayotgan organizm fiziologiyasi va maktab gigiyenasiga oid "
            "o‘z savolingizni yozing.")


def start(topic):
    """Tanlangan mavzu bilan yangi suhbat."""
    state = new_state(topic)
    if state["topic"] is None:
        return state, _say(state, welcome_text())
    t = TOPICS[state["topic"]]
    state["phase"] = "dialog"
    return state, _say(state, f"{t['opening']}\n\n{t['steps'][0]['ask']}")


def _advance(state, rnd, lead=""):
    state["step"] += 1
    state.update(tries=0, hints=0, shorts=0, found=[], asked=[])
    steps = steps_for(state)
    if state["step"] >= len(steps):
        state["phase"] = "conclude"
        return f"{lead}\n\n{CONCLUDE_ASK}".strip()
    return f"{lead}\n\n{rnd.choice(NEXT)} {steps[state['step']]['ask']}".strip()


def _finish(state, message):
    """Yakuniy xulosa: foydalanuvchi so'zlari + asosiy tushunchalar."""
    state["phase"] = "done"
    state["conclusion"] = message.strip()
    parts = ["Rahmat, ajoyib suhbat bo‘ldi! Siz o‘zingiz shunday xulosaga keldingiz:", f"«{message.strip()}»"]
    if state["topic"]:
        t = TOPICS[state["topic"]]
        if state["learned"]:
            parts.append("Suhbat davomida o‘zingiz topgan tushunchalar: " + ", ".join(state["learned"]) + ".")
        parts.append("Mavzuning asosiy g‘oyalari:\n" + "\n".join(f"• {p}" for p in t["key_points"]))
    parts.append("Bu xulosani refleksiya kundaligiga saqlab qo‘yishingiz mumkin — keyinroq o‘z fikringiz qanday o‘zgarganini ko‘rasiz.")
    return "\n\n".join(parts)


def reply(state, message):
    """Foydalanuvchi xabariga javob. Holat joyida o'zgaradi; javob matni qaytadi."""
    message = (message or "").strip()[:2000]
    if not message:
        return ""
    state["turns"].append({"role": "user", "text": message})
    rnd = _rnd(state)
    norm = normalize(message)

    if state["phase"] == "done":
        return _say(state, "Bu suhbat yakunlandi. Xulosani saqlashingiz yoki «Yangi suhbat» tugmasi bilan boshqa mavzuni boshlashingiz mumkin.")

    if state["phase"] == "choose":
        topic = detect_topic(message)
        if topic:
            t = TOPICS[topic]
            state.update(topic=topic, phase="dialog", step=0, tries=0, hints=0, shorts=0, found=[], asked=[])
            return _say(state, f"Yaxshi savol! U «{t['title']}» mavzusiga borib taqaladi. Javobni o‘zingiz topishingiz uchun "
                               f"avval bitta vaziyatni birga tahlil qilaylik.\n\n{t['steps'][0]['ask']}")
        state.update(theme=message, phase="dialog", step=0, tries=0, hints=0, shorts=0, found=[], asked=[])
        return _say(state, steps_for(state)[0]["ask"])

    if state["phase"] == "conclude":
        if len(norm.split()) < MIN_WORDS:
            return _say(state, "Xulosani biroz to‘liqroq yozing: bugun aynan nimani anglab yetdingiz?")
        return _say(state, _finish(state, message))

    # --- dialog
    steps = steps_for(state)
    step = steps[state["step"]]
    for key in ("hints", "shorts"):
        state.setdefault(key, 0)
    state.setdefault("asked", [])

    if has_any(norm, FINISH_WORDS) and len(norm.split()) <= 4:
        state["phase"] = "conclude"
        return _say(state, CONCLUDE_ASK)

    asks_help = has_any(norm, HELP_WORDS) and len(norm.split()) <= 6
    concepts = step.get("concepts", [])

    if asks_help:
        state["hints"] += 1
        if not concepts:
            if state["hints"] >= 2:
                return _say(state, _advance(state, rnd, "Mayli, bu savolga keyinroq qaytasiz."))
            return _say(state, "Hech qisi yo‘q — «bilmayman» ham fikrlashning boshlanishi. Shu mavzuda "
                               "allaqachon nimani bilasiz? Eng oddiy kuzatishingizdan boshlang.")
        if state["hints"] >= 2:
            return _say(state, _advance(state, rnd, f"Keling, buni birga aniqlaymiz. {step['insight']}"))
        return _say(state, step["hint"])

    if len(norm.split()) < MIN_WORDS and state["shorts"] < 1:
        state["shorts"] += 1
        return _say(state, rnd.choice(SHORT))

    state["tries"] += 1
    # Erkin rejim: tushunchalar yo'q — mazmunli javobdan keyin keyingi savolga o'tiladi.
    if not concepts:
        return _say(state, _advance(state, rnd, rnd.choice(ACK)))

    matched = [c for c in concepts if has_any(norm, c["kw"])]
    for c in matched:
        if c["name"] not in state["found"]:
            state["found"].append(c["name"])
        if c["name"] not in state["learned"]:
            state["learned"].append(c["name"])
    found = [c for c in concepts if c["name"] in state["found"]]
    missing = [c for c in concepts if c["name"] not in state["found"]]

    for keywords, counter in step.get("wrong", []):
        if has_any(norm, keywords) and len(matched) * 2 < len(concepts) and state["tries"] <= 2:
            return _say(state, f"{rnd.choice(MISS)} {counter}")

    # Yetarli: barcha tushunchalar yoki kamida yarmi + bitta aniqlashtirish.
    if not missing or (len(found) * 2 >= len(concepts) and state["tries"] >= 2):
        lead = rnd.choice(ACK)
        if found:
            lead += " Siz " + _join([f"«{c['name']}»" for c in found]) + "ni to‘g‘ri ko‘rsatdingiz."
        if missing:
            lead += f" Yana bir jihat: {step['insight']}"
        return _say(state, _advance(state, rnd, lead))

    if state["tries"] >= 3 or (not found and state["tries"] >= 2):
        return _say(state, _advance(state, rnd, f"Keling, fikrlarimizni jamlaymiz. {step['insight']}"))

    # Bir xil aniqlashtiruvchi savol ikki marta berilmaydi.
    fresh = [c for c in missing if c["name"] not in state["asked"]]
    if not fresh:
        return _say(state, _advance(state, rnd, f"Keling, fikrlarimizni jamlaymiz. {step['insight']}"))
    target = fresh[0]
    state["asked"].append(target["name"])
    if matched:
        praise = rnd.choice(PARTIAL).format(found=matched[-1]["name"])
        return _say(state, f"{praise} {target['probe']}")
    if found:
        return _say(state, f"Tushundim. Lekin savolning yana bir jihati bor. {target['probe']}")
    return _say(state, f"{rnd.choice(MISS)} {target['probe']}")


def _join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " va " + items[-1]


def transcript(state):
    names = {"bot": "AI-sokratik", "user": "Men"}
    return "\n\n".join(f"{names[t['role']]}: {t['text']}" for t in state["turns"])
