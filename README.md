# BioTeacher — Self-Development Platform

Bo'lajak biologiya fani o'qituvchilarida o'z-o'zini rivojlantirish metodikasini
takomillashtirishga xizmat qiluvchi elektron ta'lim platformasi.

Texnik topshiriq: [`TZ.md`](TZ.md). Kodning har bir qismi TZ'dagi talab kodi
(`FR-xx`, `NFR-xx`, `SR-xx`) bilan izohlangan.

---

## Tez boshlash

```bash
# 1. Virtual muhitni faollashtiring
env\Scripts\activate                # Windows
# source env/bin/activate           # Linux/macOS

# 2. Bog'liqliklarni o'rnating
pip install -r requirements.txt

# 3. Bazani tayyorlang
python manage.py migrate

# 4. Kontent yuklang (savollar, topshiriqlar, darslar, nishonlar)
python manage.py seed_demo

# 5. Administrator yarating
python manage.py createsuperuser

# 6. Ishga tushiring
python manage.py runserver
```

Sayt: <http://127.0.0.1:8000> · Admin panel: <http://127.0.0.1:8000/admin/>

### Demo ma'lumot bilan sinash

```bash
python manage.py seed_demo --with-users
```

Tajriba (E) va nazorat (C) guruhlari, 24 ta talaba va ularning boshlang'ich/yakuniy
o'lchovlari yaratiladi — tadqiqot moduli va statistikani darhol sinab ko'rish uchun.

| Kirish | Rol | Parol |
|---|---|---|
| `mentor@bioteacher.uz` | O'qituvchi kabineti | `bioteacher2026` |
| `tadqiqotchi@bioteacher.uz` | Tadqiqot paneli | `bioteacher2026` |
| `talaba1@bioteacher.uz` … `talaba24@` | Talaba kabineti | `bioteacher2026` |

> Demo o'lchovlar **modellashtirilgan**, real tadqiqot natijasi emas — ular faqat
> statistika modulini sinash uchun. Haqiqiy tajriba oldidan `--reset` bilan tozalang.

---

## Ilmiy model

Platformadagi barcha o'lchov 5 komponentga bog'lanadi:

| Kod | Komponent | Manba |
|---|---|---|
| `MOT` | Motivatsion-qadriyatli | Likert anketa + faollik indeksi |
| `COG` | Kognitiv | Bloom darajali test + dars natijalari |
| `ACT` | Faoliyatli-texnologik | Amaliy topshiriq rubrikasi |
| `REF` | Refleksiv | Refleksiya kundaligining sifati |
| `CRE` | Kreativ | Ijodiy topshiriq rubrikasi |

**Integral indeks:**

```
SDI = MOT×0.15 + COG×0.25 + ACT×0.25 + REF×0.20 + CRE×0.15
```

Har bir komponent ikki manbadan aralashtiriladi:
`diagnostika × 0.4 + amaliyot × 0.6`. Bir manba bo'lmasa, ikkinchisi to'liq vazn oladi;
ikkalasi ham bo'lmasa, oldingi qiymat saqlanadi (qayta hisoblash ma'lumotni yo'qotmaydi).

Vaznlar admin panelidan sozlanadi (**Diagnostika → Vaznlar profillari**). Har bir
`Measurement` o'zi ishlatgan vaznlarni nusxa qilib saqlaydi, shuning uchun vazn
o'zgarishi eski natijalarni buzmaydi (`SR-05`).

### Daraja shkalasi

| Ball | Daraja |
|---|---|
| 0–39 % | 🔴 Boshlang'ich |
| 40–59 % | 🟠 Past-o'rta |
| 60–74 % | 🟡 O'rta |
| 75–89 % | 🟢 Yuqori |
| 90–100 % | 🔵 Ijodiy |

---

## Loyiha strukturasi

```
core/           Sozlamalar, URL xaritasi, umumiy enum'lar va SDI formulasi
accounts/       Foydalanuvchi, profil, guruh, rollar, audit, mentor kabineti
diagnostics/    Anketa, bilim testi, urinishlar, MUZLATILGAN o'lchovlar, tavsiyalar
goals/          SMART maqsadlar va haftalik vazifalar
content/        BioBilim: bo'lim → mavzu → dars → material, mustahkamlash testi
assignments/    Topshiriqlar, rubrikalar, ishlar, o'z bahosi va mentor bahosi
reflection/     Refleksiya kundaligi va sifat bahosi
progress/       Komponent ballari, dinamika, faollik, streak, kunlik topshiriq
gamification/   Nishonlar va ularni berish qoidalari
research/       Tajriba/nazorat guruhlari, anonim eksport, statistika
notifications/  Ichki bildirishnomalar va email sozlamalari
home/           Landing, dashboard, seed_demo buyrug'i
```

### Muhim fayllar

| Fayl | Nima uchun |
|---|---|
| `core/enums.py` | Komponentlar, Bloom darajalari, shkala, **SDI formulasi** |
| `progress/services.py` | Ball hisoblash yadrosi, traektoriya, faollik |
| `diagnostics/services.py` | Urinish → ball → o'lchov → tavsiya zanjiri |
| `reflection/services.py` | Refleksiya sifatining shaffof heuristik bahosi |
| `research/services.py` | Anonim eksport va tavsifiy statistika |
| `accounts/permissions.py` | Kim kimning ma'lumotini ko'ra oladi (`NFR-12`) |

---

## Kontentni tahrirlash

Boshlang'ich kontent kod ichida emas, alohida ma'lumot fayllarida — ularni
dasturlashni bilmasdan ham tahrirlash mumkin:

| Fayl | Tarkibi |
|---|---|
| `diagnostics/seed_data.py` | 50 Likert savol, Bloom bo'yicha test savollari, dars testlari |
| `content/seed_data.py` | Bo'limlar, mavzular, darslar matni va metodik izohlar |
| `assignments/seed_data.py` | Rubrikalar, topshiriqlar, etalon yechimlar, nishonlar |

Tahrirlagandan keyin:

```bash
python manage.py seed_demo          # yangilaydi (mavjud yozuvlarni buzmaydi)
python manage.py seed_demo --reset  # butunlay qaytadan yuklaydi
```

Kundalik ish uchun admin panel qulayroq: **Diagnostika → So'rovnomalar**,
**Topshiriqlar → Topshiriqlar**, **BioBilim kontenti → Bo'limlar**.

### Excel/CSV orqali ommaviy yuklash (`FR-68`)

Metodist kontentni Excel'da tayyorlab, dasturchisiz yuklaydi:

```bash
# 1. To'g'ri ustunli namuna fayl oling
python manage.py import_content --template questions --out savollar.xlsx

# 2. Faylni to'ldiring, keyin avval tekshirib ko'ring
python manage.py import_content --type questions --file savollar.xlsx --dry-run

# 3. Xato qolmasa — yuklang
python manage.py import_content --type questions --file savollar.xlsx
```

Turlari: `questions` (savollar va variantlar), `assignments` (topshiriqlar),
`lessons` (bo'lim → mavzu → dars). `--dry-run` bazaga yozmaydi, faqat har bir
qatorni tekshirib, xatolarni qator raqami bilan ko'rsatadi. Takroriy yuklash
mavjud yozuvni yangilaydi, dublikat yaratmaydi.

---

## Eslatmalarni avtomatlashtirish

Muddat eslatmalari (`FR-15`) va haftalik xulosa (`FR-65`) alohida buyruq bilan
yuboriladi — uni kunlik jadvalga qo'ying:

```bash
python manage.py send_reminders --weekly            # muddat + dushanba xulosasi
python manage.py send_reminders --dry-run           # yubormasdan ko'rish
python manage.py send_reminders --force-weekly      # xulosani hoziroq yuborish
```

Windows Task Scheduler (har kuni 08:00):

```
schtasks /create /tn BioTeacherReminders /sc daily /st 08:00 ^
  /tr "\"D:\dj projects\BioTeacher\env\Scripts\python.exe\" \"D:\dj projects\BioTeacher\manage.py\" send_reminders --weekly"
```

Linux cron:

```cron
0 8 * * *  cd /srv/bioteacher && ./venv/bin/python manage.py send_reminders --weekly
```

---

## Tadqiqot ishi (dissertatsiya uchun)

1. **Guruhlarni tayyorlang.** Mentor sifatida guruh yarating (`/mentor/`), kodni
   talabalarga bering.
2. **Bo'linmani belgilang.** Tadqiqotchi sifatida `/tadqiqot/` da har bir guruhga
   tajriba (E) yoki nazorat (C) belgisini qo'ying. Talabalar bu belgini ko'rmaydi.
3. **Rozilikni yig'ing.** Talaba `/hisob/rozilik/` sahifasida ishtirokka rozilik beradi
   (`NFR-17`). Rozilik ixtiyoriy va istalgan vaqtda bekor qilinadi.
4. **Kesimlarni o'tkazing.** Har bir kesim uchun alohida so'rovnoma bor:
   `anketa-initial`, `anketa-interim_1`, `anketa-interim_2`, `anketa-final`
   (test uchun ham shunday). Yakunlangan urinish avtomatik `Measurement` yaratadi
   va u **muzlatiladi**.
5. **Ma'lumotni oling.** `/tadqiqot/eksport/` — CSV yoki XLSX. Ustunlar:

   ```
   respondent_id; group; cut; MOT; COG; ACT; REF; CRE; SDI; date
   ```

   Ism-familiya, email va telefon eksportda **umuman bo'lmaydi** — faqat barqaror
   anonim kod.
6. **Statistikani ko'ring.** `/tadqiqot/statistika/` — n, M, SD, min, max hamda
   guruhlararo taqqoslash jadvali (Δ_E − Δ_C) va Welch t-statistikasi.
   p-qiymatni SPSS yoki Statistica'da yakunlaysiz.
7. **Diagrammalarni yuklang.** Monitoring sahifasidagi "Radar PNG" / "Grafik PNG"
   tugmalari dissertatsiyaga qo'yish uchun tayyor rasm beradi.

---

## Testlar

```bash
python manage.py test                    # barchasi (163 ta)
python manage.py test core               # SDI formulasi
python manage.py test home               # barcha sahifalarning smoke-testi
python manage.py test research           # eksport anonimligi va statistika
python manage.py test content            # kontent importi va o'zlashtirish chegarasi
```

Coverage:

```bash
pip install coverage
coverage run --source=. --omit="*/migrations/*,*/tests.py,env/*,manage.py,*/seed_data.py" manage.py test
coverage report
```

Joriy qamrov: **80 %** (`NFR-15` talabi — ≥ 70 %).

Testlar TZ'ning qabul mezonlariga bog'langan: SDI hisobi, `Measurement` ning
o'zgarmasligi, vazn snapshot'i, refleksiya sifati, baholash adekvatligi,
IDOR himoyasi va eksport anonimligi.

---

## Prod'ga chiqarish

`.env.example` dan nusxa oling va to'ldiring:

```bash
cp .env.example .env
```

Majburiy o'zgartirishlar:

```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<uzun tasodifiy qiymat>
DJANGO_ALLOWED_HOSTS=bioteacher.uz,www.bioteacher.uz
DATABASE_URL=postgres://user:parol@host:5432/bioteacher
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

`DEBUG=False` bo'lganda avtomatik yoqiladi: HTTPS redirect, HSTS, xavfsiz cookie'lar.

```bash
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

Nginx `/static/` va `/media/` ni to'g'ridan-to'g'ri uzatsin. Kunlik backup
(`NFR-13`) va `logs/audit.log` rotatsiyasini sozlang.

---

## Ma'lumot maxfiyligi

- Talaba boshqa talabaning natijasini, refleksiyasini yoki ishini **ko'ra olmaydi**
  (`FR-00`, `NFR-12` — testlar bilan tekshirilgan).
- **Ochiq reyting jadvali yo'q.** Taqqoslash faqat o'z oldingi natijasi bilan (`SR-07`).
- Ijodiy galereyaga ish faqat talabaning aniq roziligi bilan chiqadi (`FR-36`).
- Barcha o'chirishlar — soft delete: tadqiqot ma'lumoti yo'qolmaydi (TZ 6.3).
- Har bir muhim harakat audit jurnaliga yoziladi (`NFR-14`).

---

## TZ'dan farqlar

| TZ | Amalga oshirilgan | Sabab |
|---|---|---|
| Celery + Redis (fon vazifalari) | Sinxron bajarilish | v1.0 hajmida fon navbati kerak emas; email `fail_silently` bilan yuboriladi. Yuklama oshsa Celery qo'shiladi. |
| WeasyPrint (PDF) | `xhtml2pdf` | WeasyPrint Windows'da GTK kutubxonalarini talab qiladi; `xhtml2pdf` toza Python. |
| django-allauth | Django built-in auth | Tashqi bog'liqliksiz: ro'yxat, email tasdiqlash, parol tiklash o'z formalarimizda. |
| Tailwind CLI (build) | Tailwind CDN | Node.js talab qilmaydi. Prod uchun build qadami keyin qo'shiladi. |

Bu farqlar funksional talablarga (`FR-xx`) ta'sir qilmaydi.

---

## Kontent hajmi haqida

TZ'ning 10-bo'limida minimal kontent hajmi belgilangan (120 test savoli, 40 lab
topshirig'i, 30 keys va h.k.). Hozir bazada **ishlaydigan namuna** bor:

| Kontent | Hozir | TZ talabi |
|---|---|---|
| Likert savollar | 50 | 50 ✅ |
| Bilim testi savollari | 30 (×4 kesim) | 120 |
| Laboratoriya topshiriqlari | 4 | 40 |
| Pedagogik keyslar + dars loyihasi | 4 | 30 |
| Raqamli topshiriqlar | 3 | 20 |
| Ijodiy topshiriqlar | 3 | 20 |
| Darslar | 7 | 60 |
| Rubrikalar | 5 | ≥6 |

Mavjud kontent **haqiqiy mazmunli** — har bir savolda izoh, har bir topshiriqda
etalon yechim va metodik sharh bor, ya'ni ular shablon sifatida ishlaydi.
To'liq hajmni ilmiy rahbar va metodist `import_content` buyrug'i yoki admin panel
orqali to'ldiradi.
