# TEXNIK TOPSHIRIQ (TZ)

## "BioTeacher — Self-Development Platform"
### Bo'lajak biologiya fani o'qituvchilarida o'z-o'zini rivojlantirish metodikasini takomillashtirishga xizmat qiluvchi elektron ta'lim platformasi

| | |
|---|---|
| **Hujjat turi** | Texnik topshiriq (Technical Specification) |
| **Versiya** | 1.0 |
| **Sana** | 2026-09-07 |
| **Loyiha kodi** | `BioTeacher` |
| **Ilmiy kontekst** | PhD dissertatsiyasi — tajriba-sinov ishining amaliy vositasi |
| **Texnologik asos** | Django 6.1 / Python 3.14 / SQLite (dev) → PostgreSQL (prod) |
| **Holat** | Tasdiqlash uchun taqdim etildi |

---

## 0. Hujjat haqida

Ushbu hujjat platformaning **nima qilishi**, **qanday qilishi** va **qachon "tayyor" deb hisoblanishi** ni bir ma'noli belgilaydi. Har bir talab `FR-xx` (funksional), `NFR-xx` (nofunksional) yoki `SR-xx` (ilmiy) kodi bilan raqamlangan va 12-bo'limdagi qabul qilish mezonlariga bog'langan.

**Muhim tamoyil:** platforma "test sayti" emas. U — **o'z-o'zini rivojlantirish siklini avtomatlashtiruvchi pedagogik tizim**. Har bir texnik qaror shu siklga xizmat qilishi shart; xizmat qilmaydigan funksiya TZ'ga kiritilmaydi.

---

## 1. Loyihaning maqsadi va vazifalari

### 1.1. Maqsad

Bo'lajak biologiya o'qituvchilarining o'z-o'zini rivojlantirish jarayonini **diagnostika → maqsad → faoliyat → baholash → refleksiya → monitoring** yopiq siklida tashkil etuvchi, natijalarni **o'lchanadigan raqamli ko'rsatkichlarga** aylantiruvchi va dissertatsiya tajriba-sinov ishi uchun **statistik ishonchli ma'lumot to'playdigan** veb-platforma yaratish.

### 1.2. Vazifalar

| № | Vazifa | Natija |
|---|---|---|
| V-01 | Talabaning boshlang'ich darajasini 5 komponent bo'yicha aniqlash | Diagnostik profil |
| V-02 | Individual rivojlanish traektoriyasini avtomatik shakllantirish | Shaxsiy yo'l xaritasi |
| V-03 | Kasbiy-pedagogik topshiriqlar bilan ta'minlash | Topshiriqlar banki |
| V-04 | Faoliyat natijasini mezonli baholash | Rubrik asosidagi ball |
| V-05 | Refleksiv ko'nikmani muntazam mashq qildirish | Refleksiya kundaligi |
| V-06 | O'sish dinamikasini vizuallashtirish | Monitoring paneli |
| V-07 | Tajriba va nazorat guruhlari ma'lumotini eksport qilish | CSV/XLSX + statistik hisobot |

### 1.3. Loyiha doirasidan tashqarida (Out of scope)

Mobil ilova (native), video-konferensiya, to'lov tizimi, sun'iy intellekt orqali erkin matnni to'liq avtomatik baholash (v1.0 da faqat **yordamchi** rejimda), boshqa fanlar uchun kontent.

---

## 2. Ilmiy asos va o'lchanadigan model

### 2.1. O'z-o'zini rivojlantirishning 5 komponentli modeli

Platformadagi barcha o'lchov shu strukturaga bog'lanadi (`SR-01`):

| Kod | Komponent | Mazmuni | O'lchash usuli |
|---|---|---|---|
| `MOT` | Motivatsion-qadriyatli | Kasbga qiziqish, o'sishga intilish | Likert anketa + faollik indeksi |
| `COG` | Kognitiv | Biologik va metodik bilim | Bloom darajali test |
| `ACT` | Faoliyatli-texnologik | Dars loyihalash, metod qo'llash | Amaliy topshiriq + rubrik |
| `REF` | Refleksiv | O'zini tahlil qila olish | Kundalik sifati + rubrik |
| `CRE` | Kreativ | Nostandart yechim yaratish | Ijodiy topshiriq + rubrik |

### 2.2. Bloom taksonomiyasi darajalari (`SR-02`)

Har bir savol/topshiriq majburiy ravishda darajaga tegishli: `1-Bilaman` → `2-Tushunaman` → `3-Qo'llayman` → `4-Tahlil qilaman` → `5-Baholayman` → `6-Yarataman`.

### 2.3. Daraja shkalasi (`SR-03`)

| Ball | Daraja | Ko'rsatkich | Izoh |
|---|---|---|---|
| 0–39 % | Boshlang'ich | ▮▯▯▯▯ | Rivojlantirish zarur |
| 40–59 % | Past-o'rta | ▮▮▯▯▯ | Tizimli ish talab etiladi |
| 60–74 % | O'rta | ▮▮▮▯▯ | Yetarli |
| 75–89 % | Yuqori | ▮▮▮▮▯ | Yaxshi |
| 90–100 % | Ijodiy | ▮▮▮▮▮ | Namunali |

**Rang semantikasi (v1.1 da qayta ko'rildi).** Shkala qizildan yashilga emas,
**och yashildan to'q yashilgacha** boradi. Sabab — `SR-07`: talaba boshqalar bilan
emas, o'z oldingi natijasi bilan taqqoslanadi. Qizil rang "sen yomonsan" degan
tashqi hukmni bildiradi va bu o'z-o'zini rivojlantirish metodikasiga zid; och → to'q
esa "sen shkalaning boshidasan" deydi.

**Rang yagona kanal emas.** Har bir daraja 5 bo'lakli pog'onali metr bilan ham
beriladi (to'ldirilgan bo'laklar soni = daraja), shuning uchun rangni ajrata
olmaydigan foydalanuvchi ham darajani aniq o'qiy oladi (`NFR-04`).

Interfeysda **yashil rang faqat o'lchovga tegishli**: tugma, havola va fokus
ko'k (`#1B5E8C`) rangda. Shunda "bosish mumkin" va "sizning natijangiz" hech
qachon chalkashmaydi.

### 2.4. Umumiy indeks formulasi (`SR-04`)

```
SDI (Self-Development Index) = Σ (Ki × Wi),  i ∈ {MOT, COG, ACT, REF, CRE}

Standart vaznlar:  W_MOT = 0.15   W_COG = 0.25   W_ACT = 0.25
                   W_REF = 0.20   W_CRE = 0.15
                   Σ Wi = 1.00
```

Vaznlar **admin panelidan sozlanadi** va har bir o'lchov snapshot'ida saqlanadi — bu retrospektiv qayta hisoblashni ta'minlaydi (`SR-05`).

### 2.5. Kesim nuqtalari (`SR-06`)

Tajriba-sinov uchun 4 ta majburiy kesim: `INITIAL` (boshlang'ich) → `INTERIM_1` (1-oraliq) → `INTERIM_2` (2-oraliq) → `FINAL` (yakuniy). Har bir kesim `Measurement` yozuvi sifatida muzlatiladi va o'zgartirilmaydi.

---

## 3. Foydalanuvchi rollari

| Rol | Kod | Huquqlar |
|---|---|---|
| Talaba | `STUDENT` | O'z profili, topshiriqlar, refleksiya, o'z monitoringi |
| O'qituvchi / mentor | `TEACHER` | O'z guruhlari, tekshirish, izoh, guruh analitikasi |
| Tadqiqotchi | `RESEARCHER` | Anonimlashtirilgan ma'lumot, eksport, statistika (tahrirsiz) |
| Kontent-metodist | `METHODIST` | Topshiriq, test, rubrika yaratish |
| Administrator | `ADMIN` | To'liq boshqaruv, vaznlar, rollar, tizim sozlamalari |

**Qoida (`FR-00`):** Talaba boshqa talabaning shaxsiy natijasini, refleksiyasini yoki reytingdagi ismini **hech qachon ko'rmaydi**. Taqqoslash faqat *o'zining oldingi natijasi* bilan (`SR-07`).

---

## 4. Funksional talablar — modullar bo'yicha

### M1. Autentifikatsiya va profil

| Kod | Talab |
|---|---|
| `FR-01` | Email/parol orqali ro'yxatdan o'tish, email tasdiqlash |
| `FR-02` | Profil: F.I.Sh., OTM, fakultet, kurs, guruh, avatar, telefon |
| `FR-03` | Talaba ro'yxatdan o'tganda **guruh kodi** (invite-code) orqali guruhga biriktiriladi |
| `FR-04` | Tajriba/nazorat guruhi belgisi (`experimental` / `control`) — faqat admin/tadqiqotchi ko'radi va o'zgartiradi |
| `FR-05` | Parolni tiklash, sessiyani boshqarish, oxirgi kirish jurnali |

### M2. "Men qanday o'qituvchiman?" — Diagnostika

| Kod | Talab |
|---|---|
| `FR-06` | Ro'yxatdan o'tgach majburiy boshlang'ich diagnostika (bloklanadigan onboarding) |
| `FR-07` | Anketa: 5 komponent × ≥10 savol = **≥50 ta Likert (1–5) savol** |
| `FR-08` | Bilim testi: Bloom bo'yicha taqsimlangan ≥30 savol, tasodifiy tanlanma, vaqt limiti |
| `FR-09` | Savollar tartibi aralashtiriladi; "reverse-scored" savollar qo'llab-quvvatlanadi |
| `FR-10` | Natija: komponentlar bo'yicha foiz, SDI, radar-diagramma, kuchli/zaif tomonlar matni |
| `FR-11` | Tugallanmagan urinish avtomatik saqlanadi va davom ettiriladi |
| `FR-12` | Natija asosida **individual tavsiya** generatsiya qilinadi (eng zaif 2 komponent → tegishli modullar) |

### M3. "Mening maqsadim" — Maqsad qo'yish va rejalashtirish

| Kod | Talab |
|---|---|
| `FR-13` | SMART-shablon: Maqsad · Muddat · Vazifalar · Resurslar · Kutilayotgan natija |
| `FR-14` | Maqsad ostida haftalik vazifalar (checklist), bajarilish foizi avtomatik |
| `FR-15` | Muddat yaqinlashganda eslatma (bildirishnoma + email) |
| `FR-16` | Maqsad yopilganda majburiy yakuniy refleksiya |
| `FR-17` | Mentor maqsadga izoh qoldirishi va tasdiqlashi mumkin |

### M4. "BioBilim" — Kasbiy bilim

| Kod | Talab |
|---|---|
| `FR-18` | Mavzular ierarxiyasi: Bo'lim → Mavzu → Dars → Topshiriq |
| `FR-19` | Kontent turlari: matn, rasm, video (embed), PDF, interaktiv topshiriq |
| `FR-20` | Har bir dars oxirida mustahkamlash testi, ≥70 % da "o'zlashtirildi" statusi |
| `FR-21` | Adaptiv rejim: xato ko'p bo'lgan mavzu qayta tavsiya qilinadi |

### M5. "Biologik laboratoriya" — Muammoli topshiriqlar

| Kod | Talab |
|---|---|
| `FR-22` | Topshiriq 4 bosqichli forma: **Taxmin → Tajriba rejasi → Natija bashorati → Xulosa** |
| `FR-23` | Har bosqich alohida saqlanadi, oldingi bosqichga qaytish mumkin |
| `FR-24` | Yuborilgach: etalon yechim va rubrik ochiladi (avval emas) |
| `FR-25` | O'z-o'zini baholash → keyin mentor bahosi; ikkalasi solishtiriladi (**baholash adekvatligi** ko'rsatkichi) |
| `FR-26` | Fayl biriktirish (rasm, PDF, ≤10 MB) |

### M6. "Men — o'qituvchi" — Pedagogik mahorat

| Kod | Talab |
|---|---|
| `FR-27` | Pedagogik keys (vaziyat) banki: sinf, mavzu, muammo tavsifi |
| `FR-28` | Talaba: muammoni aniqlaydi → metod tanlaydi → topshiriq yaratadi → dars fragmenti loyihasini yozadi |
| `FR-29` | Dars loyihasi konstruktori: maqsad, bosqichlar, vaqt, metod, baholash, resurs |
| `FR-30` | Loyihani PDF sifatida eksport qilish |
| `FR-31` | Rubrik bo'yicha baholash: maqsadga muvofiqlik, metod tanlovi, faollashtirish, baholash tizimi, vaqt taqsimoti |

### M7. "Raqamli biologiya"

| Kod | Talab |
|---|---|
| `FR-32` | Raqamli vosita bo'yicha amaliy topshiriqlar (infografika, diagramma, interaktiv material, taqdimot) |
| `FR-33` | Ish natijasini fayl/havola sifatida yuklash |
| `FR-34` | "Men buni bajara olaman" — kompetensiya checklist'i (self-assessment) |

### M8. "Kreativ o'qituvchi"

| Kod | Talab |
|---|---|
| `FR-35` | Ochiq ijodiy topshiriqlar, javob formati erkin (matn/rasm/video havola) |
| `FR-36` | Ixtiyoriy "Ijodiy galereya" — talaba **roziligi bilan** ishini guruhga ko'rsatishi mumkin |
| `FR-37` | Kreativlik rubrikasi: originallik, pedagogik asoslilik, amaliy qo'llanuvchanlik |

### M9. "Refleksiya kundaligi"

| Kod | Talab |
|---|---|
| `FR-38` | Har bir topshiriq yakunida 4 majburiy savol: *Nimani o'rgandim? / Nimani yaxshi bajardim? / Nimani rivojlantirishim kerak? / Keyingi safar nimani boshqacha qilaman?* |
| `FR-39` | Erkin kundalik yozuvlari, sana bo'yicha lenta, teg va qidiruv |
| `FR-40` | Minimal hajm nazorati (≥120 belgi) — shablon javoblarning oldini olish |
| `FR-41` | Refleksiya sifati rubrik bo'yicha baholanadi → `REF` komponentiga hissa |
| `FR-42` | Maxfiylik: kundalik faqat talaba va uning mentoriga ko'rinadi |

### M10. "Mening rivojlanishim" — Monitoring

| Kod | Talab |
|---|---|
| `FR-43` | Radar-diagramma: 5 komponent, kesimlar ustma-ust |
| `FR-44` | Chiziqli grafik: SDI dinamikasi vaqt bo'yicha |
| `FR-45` | Jadval: komponent × kesim (boshlang'ich / oraliq / yakuniy / o'sish Δ) |
| `FR-46` | Faollik: bajarilgan topshiriqlar, refleksiyalar soni, muntazamlik (streak) |
| `FR-47` | Avtomatik matnli xulosa: "Sizning `REF` ko'rsatkichingiz 3 oyda +22 % o'sdi" |
| `FR-48` | Shaxsiy hisobotni PDF eksport qilish |

### M11. "Mening yutuqlarim" — Gamifikatsiya

| Kod | Talab |
|---|---|
| `FR-49` | Nishonlar: 🏅 Faol izlanuvchi · 🔬 Yosh tadqiqotchi · 🌱 Innovatsion biolog · 👩‍🏫 Kelajak o'qituvchisi · 💡 Kreativ pedagog · 📚 Mustaqil izlanuvchi |
| `FR-50` | Nishon berish shartlari admin panelida sozlanadi (qoida: metrika + chegara) |
| `FR-51` | **Ochiq reyting jadvali yo'q.** Faqat shaxsiy o'sish ko'rsatkichi (`SR-07` ga muvofiq) |
| `FR-52` | "Bugungi 15 daqiqalik rivojlanish" — kunlik mikro-topshiriq va streak hisobi |

### M12. O'qituvchi kabineti

| Kod | Talab |
|---|---|
| `FR-53` | Guruhlar ro'yxati, har bir talabaning SDI va oxirgi faolligi |
| `FR-54` | Tekshirish navbati: yuborilgan, lekin baholanmagan ishlar |
| `FR-55` | Rubrik bo'yicha baholash interfeysi + matnli fikr-mulohaza |
| `FR-56` | Guruh analitikasi: o'rtacha, mediana, eng zaif komponent, xavf guruhidagi talabalar |
| `FR-57` | Guruhga e'lon / topshiriq tayinlash |

### M13. Tadqiqotchi moduli (dissertatsiya uchun kritik)

| Kod | Talab |
|---|---|
| `FR-58` | Tajriba (`E`) va nazorat (`C`) guruhlarini boshqarish |
| `FR-59` | Kesimlar kesimida ma'lumot eksporti: **CSV / XLSX**, ustunlar — `respondent_id, group, cut, MOT, COG, ACT, REF, CRE, SDI, date` |
| `FR-60` | Anonimlashtirish: eksportda F.I.Sh. o'rniga barqaror `respondent_id` |
| `FR-61` | Tavsifiy statistika: n, M (o'rtacha), SD, min, max, Δ |
| `FR-62` | Guruhlararo taqqoslash uchun tayyor jadval (t-mezon / χ² hisoblash uchun kirish ma'lumoti) |
| `FR-63` | Diagrammalarni PNG/SVG sifatida yuklab olish (dissertatsiyaga qo'yish uchun) |

### M14. Bildirishnomalar

| Kod | Talab |
|---|---|
| `FR-64` | Ichki bildirishnomalar markazi (o'qilgan/o'qilmagan) |
| `FR-65` | Email: baho qo'yildi, muddat yaqin, yangi topshiriq, haftalik xulosa |
| `FR-66` | Foydalanuvchi bildirishnoma turlarini o'chira oladi |

---

## 5. Asosiy biznes-jarayon (platforma algoritmi)

```
┌──────────────────────────────────────────────────────────────┐
│  1. DIAGNOSTIKA            → 5 komponent bo'yicha profil     │
│  2. DARAJANI ANIQLASH      → SDI, kuchli/zaif tomonlar       │
│  3. MAQSAD BELGILASH       → SMART reja, muddat              │
│  4. INDIVIDUAL TRAEKTORIYA → zaif komponentga mos modullar   │
│  5. MUSTAQIL FAOLIYAT      → BioBilim, Laboratoriya          │
│  6. AMALIY-PEDAGOGIK ISH   → dars loyihasi, keyslar          │
│  7. O'Z-O'ZINI BAHOLASH    → self-assessment rubrik bo'yicha │
│  8. REFLEKSIYA             → 4 savol + kundalik              │
│  9. MONITORING             → oraliq kesim, dinamika          │
│ 10. KEYINGI YO'NALISH      → traektoriya qayta hisoblanadi ┐ │
└────────────────────────────────────────────────────────────┼─┘
                                                             │
                     ▲───────── takrorlanuvchi sikl ─────────┘
```

**Traektoriyani qayta hisoblash qoidasi (`FR-67`):** har bir kesimdan keyin yoki 10 ta topshiriq bajarilganda tizim komponent ballarini yangilaydi va eng past 2 komponentga mos topshiriqlarni navbatga qo'yadi.

---

## 6. Ma'lumotlar modeli (Django)

### 6.1. Ilovalar strukturasi

```
core/                 # sozlamalar, urls, asgi/wsgi
accounts/             # User, Profile, StudyGroup, Enrollment, Role
diagnostics/          # Questionnaire, Question, Attempt, Answer, Measurement
goals/                # Goal, Task, GoalReview
content/              # Section, Topic, Lesson, Material
assignments/          # Assignment, Submission, Rubric, Criterion, Score
reflection/           # ReflectionEntry, ReflectionPrompt
progress/             # ComponentScore, Snapshot, ActivityLog, Streak
gamification/         # Badge, BadgeRule, UserBadge
research/             # StudyArm, ExportJob, StatSummary
notifications/        # Notification, NotificationSetting
```

### 6.2. Asosiy modellar (soddalashtirilgan sxema)

```python
# accounts
User(AbstractUser)          # email = USERNAME_FIELD
Profile                     # user(1:1), role, otm, faculty, course, group(FK), avatar
StudyGroup                  # name, invite_code, teacher(FK), study_arm: E|C
Enrollment                  # student, group, joined_at, is_active

# diagnostics
Questionnaire               # title, kind: LIKERT|TEST, cut: INITIAL..FINAL, is_active
Question                    # questionnaire, text, component, bloom_level, reverse_scored, order
Choice                      # question, text, value, is_correct
Attempt                     # user, questionnaire, started_at, finished_at, status
Answer                      # attempt, question, choice/value, text_answer
Measurement                 # user, cut, mot, cog, act, ref, cre, sdi,
                            # weights_json, created_at          ← MUZLATILADI

# assignments
Assignment                  # module, type, title, body, component,
                            # bloom_level, rubric(FK), deadline
Rubric / Criterion          # criterion: name, weight, max_score, level_descriptions
Submission                  # assignment, student, payload_json, files, status, submitted_at
Score                       # submission, scorer(self|mentor), criterion, value, comment

# reflection
ReflectionEntry             # user, submission(nullable), q1..q4, free_text,
                            # created_at, quality_score

# progress
ComponentScore              # user, component, value, source, computed_at
ActivityLog                 # user, action, object_ref, created_at
Streak                      # user, current, longest, last_active_date

# gamification
Badge / BadgeRule / UserBadge
```

### 6.3. Ma'lumotlar butunligi qoidalari

- `Measurement` yaratilgandan keyin **o'zgartirilmaydi** (immutable); xato bo'lsa — bekor qilinadi va yangisi yaratiladi.
- Har bir `Question` majburiy ravishda `component` va `bloom_level` ga ega.
- `Submission` faqat bir marta yuboriladi; qayta yuborish mentor ruxsati bilan.
- Barcha o'chirishlar — **soft delete** (`is_deleted`), tadqiqot ma'lumoti yo'qolmaydi.

---

## 7. Sahifalar va interfeys

### 7.1. Sahifalar ro'yxati

| Rol | Sahifalar |
|---|---|
| Mehmon | Landing, Kirish, Ro'yxatdan o'tish, Parolni tiklash |
| Talaba | Dashboard · Diagnostika · Maqsadlarim · BioBilim · Laboratoriya · Men-o'qituvchi · Raqamli biologiya · Kreativ · Refleksiya · Rivojlanishim · Yutuqlarim · Profil |
| O'qituvchi | Guruhlarim · Talaba kartochkasi · Tekshirish navbati · Analitika · E'lonlar |
| Tadqiqotchi | Tadqiqot paneli · Kesimlar · Eksport · Statistika |
| Admin | Django admin + Vaznlar sozlamasi · Nishon qoidalari · Kontent boshqaruvi |

### 7.2. Talaba dashboard'i tarkibi

1. Salomlashish + joriy SDI va daraja rangi
2. Radar-diagramma (5 komponent)
3. "Bugungi 15 daqiqalik rivojlanish" kartasi
4. Faol maqsad va uning progress-bari
5. Keyingi tavsiya etilgan 3 ta topshiriq
6. Oxirgi refleksiya va "yangi yozuv" tugmasi
7. Yaqinda olingan nishonlar

### 7.3. UI/UX talablari

| Kod | Talab |
|---|---|
| `NFR-01` | Til: **o'zbek (lotin)** — asosiy; arxitektura i18n'ga tayyor (rus/ingliz keyin qo'shiladi) |
| `NFR-02` | Responsive: 360px (mobil) → 1920px (desktop) |
| `NFR-03` | Ranglar semantikasi 2.3-bo'limdagi shkalaga qat'iy mos |
| `NFR-04` | Kontrast WCAG 2.1 AA; klaviatura bilan to'liq navigatsiya |
| `NFR-05` | Har bir uzun forma avtosaqlanadi (draft), ma'lumot yo'qolmaydi |
| `NFR-06` | Yuklanish holati (skeleton) va bo'sh holat (empty state) har bir ro'yxat uchun |
| `NFR-07` | Diagrammalar — Chart.js, SVG/PNG eksport bilan |

---

## 8. Nofunksional talablar

| Kod | Kategoriya | Talab |
|---|---|---|
| `NFR-08` | Unumdorlik | Sahifa TTFB < 500 ms; 200 bir vaqtdagi foydalanuvchi |
| `NFR-09` | Xavfsizlik | CSRF, XSS, SQLi himoyasi; parol — Argon2; login'da rate-limit |
| `NFR-10` | Xavfsizlik | `DEBUG = False`, `SECRET_KEY` — env'dan; `ALLOWED_HOSTS` to'ldirilgan |
| `NFR-11` | Fayllar | Tur va hajm validatsiyasi (≤10 MB), MIME tekshiruvi |
| `NFR-12` | Ruxsatlar | Har bir view'da object-level permission; IDOR testdan o'tkaziladi |
| `NFR-13` | Zaxira | Kunlik avtomatik backup, 30 kun saqlanadi |
| `NFR-14` | Jurnal | Audit log: kim, qachon, nimani o'zgartirdi |
| `NFR-15` | Testlar | Kritik oqimlar (diagnostika, baholash, SDI hisobi) uchun unit + integration test, coverage ≥ 70 % |
| `NFR-16` | Brauzerlar | Chrome, Edge, Firefox, Safari — oxirgi 2 versiya |
| `NFR-17` | Etika | Ishtirokchidan **informed consent**; ma'lumot faqat ilmiy maqsadda; anonimlashtirish kafolatlanadi |
| `NFR-18` | Deploy | `.env` konfiguratsiya, PostgreSQL, Nginx + Gunicorn, HTTPS |

---

## 9. Texnologiyalar steki

| Qatlam | Yechim | Izoh |
|---|---|---|
| Backend | Django 6.1, Python 3.14 | Loyihada allaqachon mavjud |
| DB | SQLite (dev) → PostgreSQL 16 (prod) | Migratsiya rejalashtirilgan |
| Frontend | Django Templates + Tailwind CSS + HTMX / Alpine.js | SPA shart emas; tezkor va yengil |
| Diagrammalar | Chart.js | Radar, line, bar |
| Fon vazifalari | Celery + Redis | Email, eksport, hisob-kitob |
| Eksport | openpyxl (XLSX), WeasyPrint (PDF) | |
| Statika | WhiteNoise | |
| Auth | django-allauth | Email tasdiqlash, parol tiklash |
| Test | pytest-django, factory-boy | |
| Kod sifati | ruff, black, pre-commit | |

---

## 10. Kontent hajmi (minimal talab)

| Kontent | Minimal hajm |
|---|---|
| Diagnostik Likert savollar | 50 ta (komponentga 10 tadan) |
| Bilim testi savollari | 120 ta (Bloom bo'yicha taqsimlangan) |
| Biologik muammoli topshiriqlar | 40 ta |
| Pedagogik keyslar | 30 ta |
| Raqamli kompetensiya topshiriqlari | 20 ta |
| Ijodiy topshiriqlar | 20 ta |
| Darslar / materiallar | 60 ta |
| Rubrikalar | Har bir topshiriq turi uchun 1 ta (≥6 ta) |

**Mas'ul:** kontentni metodist / ilmiy rahbar tayyorlaydi; ishlab chiquvchi import mexanizmini (`CSV/XLSX import`) beradi (`FR-68`).

---

## 11. Ishlab chiqish bosqichlari

| Bosqich | Mazmuni | Muddat | Natija |
|---|---|---|---|
| **B0. Poydevor** | Ilovalar strukturasi, User/Profile, auth, baza layout, Tailwind | 1 hafta | Kirish/ro'yxat ishlaydi |
| **B1. Diagnostika** | Anketa, test, Attempt, SDI hisobi, natija sahifasi | 2 hafta | Talaba profil oladi |
| **B2. Faoliyat yadrosi** | Topshiriqlar, Submission, Rubrik, baholash | 2 hafta | To'liq topshiriq sikli |
| **B3. Refleksiya + Maqsad** | Kundalik, 4 savol, SMART maqsadlar | 1 hafta | Sikl yopiladi |
| **B4. Monitoring** | Diagrammalar, kesimlar, dinamika, PDF hisobot | 1.5 hafta | O'sish ko'rinadi |
| **B5. O'qituvchi kabineti** | Guruhlar, tekshirish navbati, analitika | 1.5 hafta | Mentor ishlay oladi |
| **B6. Tadqiqot moduli** | E/C guruhlar, eksport, statistika | 1 hafta | Dissertatsiya ma'lumoti |
| **B7. Gamifikatsiya + Bildirishnoma** | Nishonlar, streak, email | 1 hafta | Motivatsiya konturi |
| **B8. Sifat va deploy** | Testlar, xavfsizlik auditi, prod deploy, hujjatlar | 1.5 hafta | Ishlab turgan tizim |

**Jami: ~12.5 hafta (≈3 oy).** B0–B4 — **MVP** (tajriba-sinovni boshlash uchun yetarli minimum).

---

## 12. Qabul qilish mezonlari (Definition of Done)

Loyiha quyidagilarning **barchasi** bajarilganda topshirilgan hisoblanadi:

1. Talaba ro'yxatdan o'tib, diagnostikadan o'tadi va 5 komponentli profil hamda SDI oladi.
2. Tizim avtomatik individual tavsiya beradi va traektoriyani shakllantiradi.
3. Talaba topshiriq bajaradi → o'zini baholaydi → mentor baholaydi → refleksiya yozadi.
4. Refleksiya sifati `REF` ballga ta'sir qiladi va bu grafikda ko'rinadi.
5. Kamida 2 ta kesim (`INITIAL`, `FINAL`) o'lchanadi va dinamika diagrammada aks etadi.
6. O'qituvchi guruh analitikasini ko'radi va tekshirish navbatida ishlaydi.
7. Tadqiqotchi E/C guruhlar bo'yicha anonim CSV/XLSX eksport oladi; ustunlar `FR-59` ga mos.
8. Talaba boshqa talabaning natijasini ko'ra olmasligi test bilan isbotlangan (`NFR-12`).
9. `SDI` hisobi uchun unit-testlar mavjud va o'tadi; coverage ≥ 70 %.
10. Prod'da `DEBUG=False`, HTTPS, backup sozlangan.
11. 10-bo'limdagi minimal kontent hajmi bazaga yuklangan.
12. Foydalanuvchi qo'llanmasi (talaba + o'qituvchi) va texnik README topshirilgan.

---

## 13. Xatarlar va ularni kamaytirish

| Xatar | Ta'sir | Yechim |
|---|---|---|
| Kontent kech tayyorlanadi | Yuqori | B0 dan boshlab parallel tayyorlanadi; import mexanizmi oldindan beriladi |
| Talabalar refleksiyani shablon yozadi | Yuqori | Minimal hajm, rubrik, mentor fikri, savollar rotatsiyasi |
| Diagnostika ishonchliligi past | Yuqori | Pilot sinov (n ≥ 30), Kronbax α ≥ 0.7 tekshiruvi, savollarni qayta ko'rish |
| Tajriba davomida ishtirokchi yo'qotish (drop-out) | O'rta | Bildirishnoma, streak, mentor aloqasi; zaxira namuna |
| Vaznlar o'zgarishi eski natijalarni buzadi | O'rta | Vaznlar snapshot'da saqlanadi (`SR-05`) |
| Gamifikatsiya ichki motivatsiyani siqib chiqaradi | O'rta | Ochiq reyting yo'q; faqat shaxsiy o'sish (`SR-07`) |

---

## 14. Kelajakdagi rivojlanish (v2.0+)

- Erkin matnli javoblarni LLM yordamida **dastlabki** baholash (mentor tasdig'i bilan)
- Mobil PWA
- Virtual laboratoriya simulyatorlari (interaktiv)
- Ko'p tillilik (rus, ingliz)
- OTM ma'lumot tizimlari bilan integratsiya (LMS / SSO)
- Mentor–talaba ichki chat

---

## 15. Atamalar lug'ati

| Atama | Ma'nosi |
|---|---|
| **SDI** | Self-Development Index — o'z-o'zini rivojlantirish integral indeksi |
| **Kesim (cut)** | Tajriba-sinovning o'lchov nuqtasi (boshlang'ich / oraliq / yakuniy) |
| **Rubrik** | Mezonli baholash jadvali |
| **Traektoriya** | Talabaning individual rivojlanish yo'li |
| **E / C guruh** | Tajriba (experimental) / nazorat (control) guruhi |
| **Baholash adekvatligi** | O'z bahosi va mentor bahosi orasidagi farq |

---

*Ushbu texnik topshiriq tasdiqlangandan so'ng 11-bo'limdagi bosqichlar bo'yicha ish boshlanadi. Har qanday o'zgartirish hujjat versiyasini oshiradi va alohida kelishiladi.*
