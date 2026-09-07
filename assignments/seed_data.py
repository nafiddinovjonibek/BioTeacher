"""
Topshiriqlar va rubrikalar bazasi — haqiqiy pedagogik mazmun bilan.

RUBRICS     — mezonli baholash jadvallari (FR-31, FR-37)
ASSIGNMENTS — laboratoriya, pedagogik keys, dars loyihasi, raqamli va ijodiy topshiriqlar
COMPETENCY  — "Men buni bajara olaman" checklisti (FR-34)
BADGES      — nishonlar va ularni berish qoidalari (FR-49, FR-50)
"""

from core.enums import BloomLevel, Component, Module

# ---------------------------------------------------------------------------
# RUBRIKALAR
# ---------------------------------------------------------------------------

RUBRICS = [
    {
        "slug": "lab-tadqiqot",
        "title": "Biologik tadqiqot rubrikasi",
        "description": "Muammoli laboratoriya topshiriqlarini baholash uchun.",
        "criteria": [
            {"name": "Taxminning asoslanganligi", "max_score": 4, "weight": 1.0,
             "hint": "Taxmin biologik bilimga tayanadimi yoki tasodifiymi?",
             "levels": {"0": "Taxmin yo'q", "2": "Taxmin bor, lekin asoslanmagan",
                        "4": "Taxmin aniq biologik qonuniyatga tayangan"}},
            {"name": "Tajriba rejasining to'g'riligi", "max_score": 4, "weight": 1.2,
             "hint": "Bitta o'zgaruvchi o'zgaradimi? Nazorat namunasi bormi?",
             "levels": {"0": "Reja yo'q", "2": "Reja bor, lekin o'zgaruvchilar nazorat qilinmagan",
                        "4": "Bitta mustaqil o'zgaruvchi, nazorat namunasi va takrorlash ko'zda tutilgan"}},
            {"name": "Natijani izohlash", "max_score": 4, "weight": 1.0,
             "hint": "Natija sabab-oqibat bilan bog'langanmi?",
             "levels": {"0": "Izoh yo'q", "2": "Natija bayon qilingan, sababi ochilmagan",
                        "4": "Sabab-oqibat aniq ko'rsatilgan"}},
            {"name": "Darsga bog'lash", "max_score": 4, "weight": 1.0,
             "hint": "Bu tajribani o'quvchilarga qanday berasiz?",
             "levels": {"0": "Bog'lanmagan", "2": "Umumiy gap bilan bog'langan",
                        "4": "Aniq sinf, mavzu va metod ko'rsatilgan"}},
        ],
    },
    {
        "slug": "dars-loyihasi",
        "title": "Dars loyihasi rubrikasi",
        "description": "Dars fragmenti va loyihasini baholash uchun (FR-31).",
        "criteria": [
            {"name": "Maqsadga muvofiqlik", "max_score": 4, "weight": 1.2,
             "hint": "Maqsad o'lchanadigan fe'l bilan yozilganmi?",
             "levels": {"0": "Maqsad yo'q yoki o'qituvchi faoliyatini bildiradi",
                        "2": "Maqsad bor, lekin o'lchash qiyin",
                        "4": "Maqsad o'quvchi harakatida, kuzatiladigan va o'lchanadigan"}},
            {"name": "Metod tanlovining asoslanganligi", "max_score": 4, "weight": 1.2,
             "hint": "Nima uchun aynan shu metod?",
             "levels": {"0": "Metod ko'rsatilmagan", "2": "Metod nomlangan, asos yo'q",
                        "4": "Metod maqsad va Bloom darajasiga bog'lab asoslangan"}},
            {"name": "O'quvchini faollashtirish", "max_score": 4, "weight": 1.0,
             "hint": "Darsda o'quvchi nima QILADI?",
             "levels": {"0": "O'quvchi faqat tinglaydi", "2": "Qisman faollik bor",
                        "4": "Dars vaqtining katta qismida o'quvchi faoliyat ko'rsatadi"}},
            {"name": "Baholash tizimi", "max_score": 4, "weight": 1.0,
             "hint": "Natija qanday o'lchanadi? Mezon oldindan berilganmi?",
             "levels": {"0": "Baholash ko'zda tutilmagan", "2": "Baholash bor, mezon noaniq",
                        "4": "Aniq mezonlar va formativ baholash lahzalari ko'rsatilgan"}},
            {"name": "Vaqt taqsimoti", "max_score": 4, "weight": 0.8,
             "hint": "Bosqichlar real 45 daqiqaga sig'adimi?",
             "levels": {"0": "Vaqt ko'rsatilmagan", "2": "Vaqt bor, lekin real emas",
                        "4": "Bosqichlar vaqti real va muvozanatli"}},
        ],
    },
    {
        "slug": "pedagogik-keys",
        "title": "Pedagogik vaziyat tahlili rubrikasi",
        "description": "Keys yechimini baholash uchun.",
        "criteria": [
            {"name": "Muammoni to'g'ri aniqlash", "max_score": 4, "weight": 1.2,
             "hint": "Belgi bilan sabab farqlanganmi?",
             "levels": {"0": "Muammo aniqlanmagan", "2": "Faqat tashqi belgi aytilgan",
                        "4": "Muammoning pedagogik sababi aniqlangan"}},
            {"name": "Yechimning amaliyligi", "max_score": 4, "weight": 1.0,
             "hint": "Yechim real sinf sharoitida bajarilarlimi?",
             "levels": {"0": "Yechim yo'q", "2": "Yechim umumiy, amalga oshirish noaniq",
                        "4": "Aniq, bajariladigan qadamlar ketma-ketligi berilgan"}},
            {"name": "Pedagogik asoslilik", "max_score": 4, "weight": 1.0,
             "hint": "Yechim metodika tamoyillariga mos keladimi?",
             "levels": {"0": "Asos yo'q", "2": "Qisman asoslangan",
                        "4": "Metodik tamoyil yoki nazariyaga aniq tayangan"}},
            {"name": "Natijani bashorat qilish", "max_score": 4, "weight": 0.8,
             "hint": "Yechim ishlaganini qanday bilasiz?",
             "levels": {"0": "Bashorat yo'q", "2": "Umumiy kutilma aytilgan",
                        "4": "Kuzatiladigan natija va uni tekshirish yo'li ko'rsatilgan"}},
        ],
    },
    {
        "slug": "raqamli-mahsulot",
        "title": "Raqamli ta'lim mahsuloti rubrikasi",
        "description": "Infografika, taqdimot, interaktiv material uchun.",
        "criteria": [
            {"name": "Mazmuniy to'g'rilik", "max_score": 4, "weight": 1.2,
             "hint": "Biologik ma'lumot xatosizmi?",
             "levels": {"0": "Jiddiy xatolar bor", "2": "Kichik noaniqliklar bor",
                        "4": "Mazmun to'liq to'g'ri"}},
            {"name": "Vizual tushunarlilik", "max_score": 4, "weight": 1.0,
             "hint": "O'quvchi yordamisiz tushuna oladimi?",
             "levels": {"0": "Chalkash", "2": "Qisman tushunarli",
                        "4": "Tuzilma aniq, asosiy g'oya darhol ko'rinadi"}},
            {"name": "Pedagogik maqsadga xizmat qilishi", "max_score": 4, "weight": 1.0,
             "hint": "Bu material qaysi o'quv natijasiga olib boradi?",
             "levels": {"0": "Maqsad ko'rinmaydi", "2": "Umumiy tarzda foydali",
                        "4": "Aniq o'quv natijasiga yo'naltirilgan"}},
        ],
    },
    {
        "slug": "ijodiy-ish",
        "title": "Ijodiy yechim rubrikasi",
        "description": "Kreativ topshiriqlarni baholash (FR-37).",
        "criteria": [
            {"name": "Originallik", "max_score": 4, "weight": 1.0,
             "hint": "Yechim shabloniy emasmi?",
             "levels": {"0": "To'liq shabloniy", "2": "Ma'lum usulning kichik o'zgarishi",
                        "4": "Yangi, o'ziga xos yondashuv"}},
            {"name": "Pedagogik asoslilik", "max_score": 4, "weight": 1.2,
             "hint": "Ijodiylik o'quv maqsadiga xizmat qiladimi?",
             "levels": {"0": "Faqat ko'ngilochar", "2": "Qisman o'quv maqsadiga bog'langan",
                        "4": "Ijodiy shakl aniq o'quv natijasini ta'minlaydi"}},
            {"name": "Amaliy qo'llanuvchanlik", "max_score": 4, "weight": 1.0,
             "hint": "Real sinfda, mavjud resurs bilan bajarilarlimi?",
             "levels": {"0": "Amalga oshmaydi", "2": "Katta resurs talab qiladi",
                        "4": "Oddiy sharoitda ham qo'llanadi"}},
        ],
    },
]


# ---------------------------------------------------------------------------
# TOPSHIRIQLAR
# ---------------------------------------------------------------------------

ASSIGNMENTS = [
    # ================= LABORATORIYA (muammoli topshiriqlar) =================
    {
        "slug": "lab-yoruglik-va-barg",
        "module": Module.LAB, "kind": "LAB4", "component": Component.COG,
        "bloom": BloomLevel.ANALYZE, "difficulty": 2, "minutes": 30,
        "rubric": "lab-tadqiqot",
        "title": "Yorug'liksiz qolgan barg",
        "context": "Xona o'simligining bir bargi bir hafta davomida qora qog'oz bilan yopib qo'yildi. "
                   "Harorat, sug'orish va namlik o'zgarmadi.",
        "body": "Bir haftadan keyin yopilgan bargda qanday o'zgarish kuzatiladi? Nima uchun?\n\n"
                "Taxminingizni asoslang, uni tekshirish uchun tajriba rejasini tuzing, natijani "
                "bashorat qiling va xulosangizni 6-sinf darsida qanday ishlatishingizni yozing.",
        "reference": "Yopilgan barg sarg'ayadi va kraxmal to'planmaydi. Sababi: yorug'liksiz "
                     "fotosintezning yorug'lik bosqichi to'xtaydi, ATF va NADPH hosil bo'lmaydi, "
                     "demak Kalvin sikli ham ishlamaydi; xlorofill esa yangilanmay parchalanadi.\n\n"
                     "Tajriba rejasi: bitta o'simlikda bir barg yopiladi (tajriba), yonidagi barg "
                     "ochiq qoladi (nazorat) — bu boshqa barcha omillarni tenglashtiradi. "
                     "Tekshirish: yod eritmasi bilan kraxmal sinovi — ochiq barg ko'karadi, yopilgani yo'q.\n\n"
                     "Darsda qo'llash: bu tajriba \"Fotosintez shartlari\" mavzusiga muammoli kirish "
                     "sifatida ishlatiladi. O'quvchilar avval taxmin yozadi, keyin natijani ko'radi — "
                     "kognitiv nomuvofiqlik qiziqishni kuchaytiradi.",
    },
    {
        "slug": "lab-kartoshka-osmos",
        "module": Module.LAB, "kind": "LAB4", "component": Component.COG,
        "bloom": BloomLevel.APPLY, "difficulty": 2, "minutes": 25,
        "rubric": "lab-tadqiqot",
        "title": "Kartoshka va tuzli suv",
        "context": "Bir xil o'lchamdagi ikki kartoshka bo'lakchasi olindi: biri toza suvga, "
                   "ikkinchisi konsentrlangan tuz eritmasiga solindi.",
        "body": "30 daqiqadan keyin bo'lakchalarning qattiqligi va o'lchami qanday farq qiladi? "
                "Jarayonning nomini ayting va mexanizmini tushuntiring.\n\n"
                "Tajriba rejangizda o'lchash usulini (massani tarozida o'lchash) ham ko'rsating.",
        "reference": "Toza suvdagi bo'lakcha qattiqlashadi va massasi ortadi (gipotonik muhit — suv "
                     "hujayraga kiradi, turgor ortadi). Tuzli eritmadagisi yumshaydi va massasi "
                     "kamayadi (gipertonik muhit — suv hujayradan chiqadi, plazmoliz).\n\n"
                     "Jarayon — osmos: suvning yarim o'tkazuvchi membrana orqali kam erigan modda "
                     "tomonidan ko'p erigan modda tomon passiv harakati.\n\n"
                     "Miqdoriy o'lchash: har bir bo'lakchani tajribadan oldin va keyin tarozida "
                     "o'lchab, massa o'zgarishi foizini hisoblash — bu tajribani sifatiydan "
                     "miqdoriyga aylantiradi va o'quvchida ilmiy yondashuv shakllantiradi.",
    },
    {
        "slug": "lab-donlarning-nafas-olishi",
        "module": Module.LAB, "kind": "LAB4", "component": Component.COG,
        "bloom": BloomLevel.ANALYZE, "difficulty": 3, "minutes": 35,
        "rubric": "lab-tadqiqot",
        "title": "Unib chiqayotgan donlar issiqlik chiqaradimi?",
        "context": "Ikki termosga bir xil miqdorda no'xat solindi: birinchisiga ho'llangan va "
                   "unib chiqayotgan donlar, ikkinchisiga qaynatilgan (o'lik) donlar.",
        "body": "24 soatdan keyin termoslardagi harorat qanday farq qiladi? Sababini biologik "
                "jihatdan asoslang.\n\n"
                "Nima uchun ikkinchi termosga aynan QAYNATILGAN donlar solingan? Bu qanday "
                "metodologik vazifani bajaradi?",
        "reference": "Unib chiqayotgan donlar solingan termosda harorat sezilarli ko'tariladi. "
                     "Sabab: unib chiqish davrida nafas olish jadal kechadi, organik moddaning "
                     "oksidlanishida ajralgan energiyaning bir qismi ATF ga, qolgani ISSIQLIKKA aylanadi.\n\n"
                     "Qaynatilgan donlar — NAZORAT namunasi. Ular bir xil massa va hajmga ega, lekin "
                     "tirik emas. Bu issiqlik donning fizik xossasidan emas, aynan hayot faoliyatidan "
                     "kelayotganini isbotlaydi. Nazoratsiz tajriba xulosasi ishonchsiz bo'lar edi.\n\n"
                     "Darsda: bu tajriba \"nazorat namunasi nima uchun kerak\" degan ilmiy metodni "
                     "tushuntirishning eng aniq misoli.",
    },
    {
        "slug": "lab-turli-tuproq",
        "module": Module.LAB, "kind": "LAB4", "component": Component.COG,
        "bloom": BloomLevel.EVALUATE, "difficulty": 4, "minutes": 40,
        "rubric": "lab-tadqiqot",
        "title": "Tajribadagi xatoni toping",
        "context": "Talaba loviya urug'ining unib chiqishini o'rgandi: 1-idish deraza oldida "
                   "(issiq, yorug'), 2-idish yerto'lada (salqin, qorong'i). Yerto'ladagi "
                   "urug'lar sekinroq unib chiqdi. Talaba xulosa qildi: \"Yorug'lik urug'ning "
                   "unib chiqishi uchun zarur\".",
        "body": "Bu xulosa to'g'rimi? Tajribaning metodologik kamchiligini aniqlang va uni "
                "to'g'rilangan tajriba rejasini tuzing.\n\n"
                "Bu keysni o'quvchilarga ilmiy metodni o'rgatishda qanday ishlatasiz?",
        "reference": "Xulosa NOTO'G'RI. Tajribada bir vaqtning o'zida IKKI o'zgaruvchi o'zgargan: "
                     "yorug'lik va harakat. Sekin unib chiqishning sababi katta ehtimol bilan past "
                     "harorat, yorug'lik emas — ko'pchilik urug'lar unib chiqish uchun yorug'likka "
                     "muhtoj emas.\n\n"
                     "To'g'rilangan reja: ikki idish ham BIR XIL haroratda saqlanadi (masalan, "
                     "22°C), biri yorug'da, ikkinchisi qorong'i quti ostida. Boshqa barcha shart "
                     "(namlik, urug' soni, tuproq) bir xil. Har bir variant kamida 3 marta "
                     "takrorlanadi.\n\n"
                     "Darsda qo'llash: o'quvchilarga tayyor xulosani tanqid qildirish — bu \"Baholayman\" "
                     "darajasidagi eng kuchli topshiriq turlaridan biri. O'quvchi xatoni o'zi topsa, "
                     "\"bitta o'zgaruvchi\" qoidasi umrbod esda qoladi.",
    },

    # ================= MEN — O'QITUVCHIMAN (keyslar) =================
    {
        "slug": "keys-hujayra-tushunmayapti",
        "module": Module.TEACHER, "kind": "CASE", "component": Component.ACT,
        "bloom": BloomLevel.CREATE, "difficulty": 3, "minutes": 40,
        "rubric": "pedagogik-keys",
        "title": "7-sinf \"Hujayra\" mavzusini o'zlashtira olmayapti",
        "context": "7-sinf o'quvchilari \"Hujayra tuzilishi\" mavzusini uchinchi darsdir "
                   "o'rganishmoqda. Ular organoidlar nomini yodlab olishgan, lekin \"Nima uchun "
                   "mitoxondriya mushak hujayrasida ko'p bo'ladi?\" degan savolga javob bera olmadi.",
        "body": "Vaziyatdagi asosiy pedagogik muammoni aniqlang (belgi emas, sabab!).\n"
                "Qaysi metodni tanlaysiz va nima uchun aynan shuni?\n"
                "O'quvchilarga beriladigan aniq topshiriqni yozing.\n"
                "10-15 daqiqalik dars fragmenti ssenariysini tuzing.",
        "reference": "MUAMMO: o'zlashtirish \"Bilaman\" darajasida qotib qolgan — nom bilan funksiya "
                     "o'rtasida bog'lanish qurilmagan. Yodlash bor, ma'no yo'q.\n\n"
                     "METOD: muammoli ta'lim + tuzilma-funksiya taqqoslash jadvali. Nima uchun: "
                     "maqsad \"Tahlil qilaman\" darajasiga chiqish, demak o'quvchi bog'lanishni "
                     "O'ZI topishi kerak.\n\n"
                     "TOPSHIRIQ: \"Uchta hujayra berilgan — mushak, teri epiteliysi, o'simlik bargi. "
                     "Har birida qaysi organoid ko'proq bo'lishi kerak va nega? Javobingizni "
                     "hujayraning VAZIFASI bilan asoslang.\"\n\n"
                     "FRAGMENT: 2 daq — savolni qo'yish (kognitiv nomuvofiqlik); 5 daq — juftlikda "
                     "muhokama va jadval to'ldirish; 5 daq — guruhlar javobini taqqoslash; "
                     "3 daq — umumlashtirish: \"tuzilma vazifaga bo'ysunadi\" tamoyilini o'quvchilar "
                     "o'z so'zi bilan aytadi.",
    },
    {
        "slug": "keys-faol-emas-sinf",
        "module": Module.TEACHER, "kind": "CASE", "component": Component.ACT,
        "bloom": BloomLevel.CREATE, "difficulty": 3, "minutes": 35,
        "rubric": "pedagogik-keys",
        "title": "Sinf savollarga javob bermaydi",
        "context": "9-sinfda dars o'tyapsiz. Savol berasiz — sinf jim. Faqat ikki o'quvchi "
                   "doim javob beradi, qolganlari past qarab o'tiradi. Bu holat bir necha "
                   "darsdan beri takrorlanmoqda.",
        "body": "Nima uchun sinf javob bermayapti? Kamida ikkita ehtimoliy sababni ko'rsating.\n"
                "Qaysi metod bilan barcha o'quvchini faoliyatga jalb qilasiz?\n"
                "Keyingi darsda qo'llaydigan aniq texnikani yozing.\n"
                "Bu ishlaganini qanday bilasiz?",
        "reference": "EHTIMOLIY SABABLAR: (1) savol butun sinfga qaratilgan — shaxsiy javobgarlik yo'q; "
                     "(2) xato javob berishdan qo'rquv, sinfda xavfsiz muhit shakllanmagan; "
                     "(3) o'ylash uchun vaqt berilmayapti — o'qituvchi 1-2 soniyada javobni o'zi aytadi.\n\n"
                     "METOD: \"O'yla — juftlik — bo'lish\" (Think–Pair–Share). Nima uchun: har bir "
                     "o'quvchi avval yakka o'ylaydi (majburiy faoliyat), keyin juftlikda aytadi "
                     "(past xavf), so'ng sinfga chiqadi (javob allaqachon tekshirilgan — qo'rquv kamayadi).\n\n"
                     "TEXNIKA: savoldan keyin 20 soniya SUKUT (\"o'ylash vaqti\"), keyin 1 daqiqa "
                     "juftlikda muhokama, so'ng tasodifiy tanlov bilan javob so'rash.\n\n"
                     "TEKSHIRISH: dars oxirida \"chiqish chiptasi\" — har bir o'quvchi bitta savolga "
                     "yozma javob beradi. Javob berganlar ulushi o'lchanadigan ko'rsatkich.",
    },
    {
        "slug": "keys-tez-va-sekin",
        "module": Module.TEACHER, "kind": "CASE", "component": Component.ACT,
        "bloom": BloomLevel.CREATE, "difficulty": 4, "minutes": 40,
        "rubric": "pedagogik-keys",
        "title": "Bir sinfda turli darajadagi o'quvchilar",
        "context": "Sinfda 5-6 o'quvchi topshiriqni 5 daqiqada bajarib, zerikib qoladi; "
                   "7-8 o'quvchi esa ulgurmaydi va ortda qoladi. Bir xil topshiriq ikkala "
                   "guruh uchun ham noto'g'ri.",
        "body": "Bu vaziyatning pedagogik nomi nima va uni qanday hal qilasiz?\n"
                "Bitta biologiya mavzusi uchun uch darajali topshiriq tizimini tuzing.\n"
                "Baholashni qanday adolatli qilasiz?",
        "reference": "PEDAGOGIK NOM: differensiatsiyaning yo'qligi. Yechim — tabaqalashtirilgan "
                     "topshiriqlar (differentiated instruction).\n\n"
                     "UCH DARAJALI TIZIM (\"Fotosintez\" mavzusi misolida):\n"
                     "• Baza (Bilaman/Tushunaman): tenglamani to'ldiring va bosqichlarni nomlang.\n"
                     "• O'rta (Qo'llayman/Tahlil): grafikdan fotosintez tezligini cheklovchi omilni "
                     "aniqlang va izohlang.\n"
                     "• Yuqori (Baholayman/Yarataman): issiqxonada hosildorlikni oshirish uchun "
                     "qaysi omilga sarmoya kiritish maqsadga muvofiq — asoslang.\n\n"
                     "ADOLATLI BAHOLASH: har bir daraja ichida bir xil rubrikadan foydalaniladi, "
                     "lekin yuqori darajaga o'tish ixtiyoriy va qo'shimcha ball beradi. Muhimi — "
                     "past daraja \"zaiflar uchun\" deb belgilanmaydi: o'quvchi o'zi tanlaydi, "
                     "bu avtonomiyani va motivatsiyani saqlaydi.",
    },
    {
        "slug": "loyiha-fotosintez-darsi",
        "module": Module.TEACHER, "kind": "LESSON_PLAN", "component": Component.ACT,
        "bloom": BloomLevel.CREATE, "difficulty": 4, "minutes": 50,
        "rubric": "dars-loyihasi",
        "title": "Dars loyihasi: \"Fotosintez\" (6-sinf, 45 daqiqa)",
        "context": "6-sinf, \"O'simliklar hayoti\" bo'limi. O'quvchilar hujayra tuzilishini "
                   "o'tishgan, xloroplast bilan tanish. Sinfda proyektor bor, laboratoriya jihozi cheklangan.",
        "body": "To'liq dars loyihasini ishlab chiqing. Har bir bo'limni real 45 daqiqaga "
                "moslashtiring va metod tanlovini asoslang.",
        "reference": "NAMUNAVIY YECHIM (qisqartirilgan):\n\n"
                     "MAQSAD: dars oxirida o'quvchi (a) fotosintez tenglamasini yoza oladi; "
                     "(b) yorug'lik va qorong'ilik bosqichini farqlaydi; (c) fotosintezni "
                     "cheklovchi kamida ikki omilni nomlab, ta'sirini izohlaydi.\n\n"
                     "BOSQICHLAR: 5 daq — muammoli kirish (\"yopilgan barg\" surati, taxmin yozish); "
                     "10 daq — o'qituvchi bayoni + sxema (faqat asosiy mexanizm); 12 daq — juftlikda "
                     "sxemani to'ldirish topshirig'i; 10 daq — cheklovchi omillar grafigini tahlil "
                     "qilish (guruhli ish); 5 daq — chiqish chiptasi; 3 daq — refleksiya va uy vazifasi.\n\n"
                     "METOD ASOSI: muammoli kirish qiziqish uyg'otadi (motivatsiya); juftlikdagi "
                     "ish \"Tushunaman\" darajasini ta'minlaydi; grafik tahlili \"Tahlil qilaman\" "
                     "darajasiga olib chiqadi.\n\n"
                     "BAHOLASH: chiqish chiptasi 3 ta savol — har bir maqsad bo'yicha bittadan. "
                     "Mezon o'quvchilarga dars boshida aytiladi.\n\n"
                     "RESURSLAR: proyektor uchun 4 ta slayd, tarqatma sxema, cheklovchi omillar grafigi.",
    },

    # ================= RAQAMLI BIOLOGIYA =================
    {
        "slug": "raqamli-infografika-hujayra",
        "module": Module.DIGITAL, "kind": "DIGITAL", "component": Component.ACT,
        "bloom": BloomLevel.CREATE, "difficulty": 3, "minutes": 45,
        "rubric": "raqamli-mahsulot",
        "title": "\"Hujayra organoidlari\" infografikasi",
        "context": "7-sinf o'quvchilari uchun bitta A4 sahifaga sig'adigan infografika kerak.",
        "body": "Canva, Figma yoki PowerPoint yordamida infografika tayyorlang. Unda har bir "
                "organoidning nomi, ko'rinishi va VAZIFASI bir qarashda tushunarli bo'lsin.\n\n"
                "Tayyor faylni yuklang yoki havolasini yozing. Javobingizda: qanday vizual "
                "tamoyillardan foydalandingiz va bu infografika qaysi dars bosqichida ishlatiladi?",
        "reference": "Kuchli infografikaning belgilari: (1) bitta asosiy g'oya — bu yerda "
                     "\"tuzilma vazifaga mos\"; (2) rang bilan guruhlash (energiya, sintez, "
                     "tashish organoidlar); (3) matn minimal — har bir organoidga 5-7 so'z; "
                     "(4) o'qish yo'nalishi aniq (yuqoridan pastga yoki markazdan chetga).\n\n"
                     "Qo'llash bosqichi: infografika mavzuni tushuntirishdan KEYIN, mustahkamlash "
                     "bosqichida beriladi — aks holda o'quvchi tayyor javobni ko'chiradi va "
                     "o'ylash faoliyati yo'qoladi. Yanada kuchli variant: bo'sh infografika berib, "
                     "o'quvchilarning o'zlariga to'ldirtirish.",
    },
    {
        "slug": "raqamli-interaktiv-topshiriq",
        "module": Module.DIGITAL, "kind": "DIGITAL", "component": Component.ACT,
        "bloom": BloomLevel.CREATE, "difficulty": 3, "minutes": 40,
        "rubric": "raqamli-mahsulot",
        "title": "Interaktiv topshiriq yaratish",
        "context": "Bepul vositalar (LearningApps, Wordwall, Google Forms, Quizizz) yordamida.",
        "body": "Ixtiyoriy biologiya mavzusiga interaktiv topshiriq yarating: moslashtirish, "
                "tasniflash, ketma-ketlik tuzish yoki viktorina.\n\n"
                "Havolani yozing va javobingizda tushuntiring: topshiriq qaysi Bloom darajasiga "
                "mo'ljallangan va nima uchun aynan shu format tanlandi?",
        "reference": "Format va daraja mosligi: moslashtirish/tasniflash — \"Tushunaman\"; "
                     "ketma-ketlik tuzish (masalan, mitoz fazalari) — \"Tushunaman/Qo'llayman\"; "
                     "vaziyatli savollar — \"Tahlil qilaman\".\n\n"
                     "Tipik xato: interaktiv vosita faqat yodlashni tekshiradigan test uchun "
                     "ishlatiladi — bunda raqamli shakl qo'shimcha qiymat bermaydi. Raqamli vosita "
                     "aynan shu narsani qog'ozda qilib bo'lmaydigan holda kuch beradi: bir zumda "
                     "qaytar aloqa, urinishlar tarixi, tasodifiy variant.",
    },
    {
        "slug": "raqamli-jarayon-modeli",
        "module": Module.DIGITAL, "kind": "DIGITAL", "component": Component.COG,
        "bloom": BloomLevel.APPLY, "difficulty": 3, "minutes": 35,
        "rubric": "raqamli-mahsulot",
        "title": "Biologik jarayonni sxema bilan modellashtirish",
        "context": "Moddalar almashinuvi, oqsil sintezi yoki moddalar aylanishidan birini tanlang.",
        "body": "Tanlagan jarayonni bosqichma-bosqich ochib beruvchi diagramma tuzing "
                "(diagrams.net, Canva yoki qo'lda chizib rasmga oling).\n\n"
                "Diagrammada sabab-oqibat strelkalari aniq bo'lsin. Javobda: o'quvchilar qaysi "
                "qismda ko'proq adashadi va sxemangiz buni qanday oldini oladi?",
        "reference": "Yaxshi jarayon sxemasining shartlari: har bir strelka NIMA sababdan NIMAga "
                     "olib borishini bildiradi; bosqichlar raqamlangan; kirish va chiqish moddalari "
                     "ajratib ko'rsatilgan.\n\n"
                     "Oqsil sintezida o'quvchilar eng ko'p transkripsiya va translyatsiyani "
                     "chalkashtiradi. Yechim: sxemada ikki jarayonni turli rangda va turli "
                     "\"joy\" (yadro / sitoplazma) fonida ko'rsatish — makon bo'yicha ajratish "
                     "xotirada mustahkam iz qoldiradi.",
    },

    # ================= KREATIV O'QITUVCHI =================
    {
        "slug": "kreativ-fotosintez-noodatiy",
        "module": Module.CREATIVE, "kind": "CREATIVE", "component": Component.CRE,
        "bloom": BloomLevel.CREATE, "difficulty": 3, "minutes": 30,
        "rubric": "ijodiy-ish",
        "title": "Fotosintezni noodatiy usulda tushuntiring",
        "context": "6-sinf o'quvchilari uchun. Darslikdagi sxemadan foydalanish TAQIQLANADI.",
        "body": "Fotosintez jarayonini butunlay boshqacha yo'l bilan tushuntiring: hikoya, "
                "rolli o'yin, metafora, qo'shiq, komiks, harakatli mashq yoki o'zingiz "
                "o'ylab topgan shakl.\n\n"
                "Yechimingizni batafsil bayon qiling: kim nima qiladi, qancha vaqt oladi, "
                "qanday resurs kerak va o'quvchi aynan NIMANI tushunib qoladi.",
        "reference": "Namunaviy yechim — \"O'simlik zavodi\" rolli o'yini:\n"
                     "O'quvchilar rol oladi: 6 nafari — CO₂ molekulasi, 6 nafari — suv, "
                     "2 nafari — xlorofill (energiya qabul qiluvchi), 1 nafari — quyosh. "
                     "\"Quyosh\" energiya kartochkasini xlorofillga beradi; xlorofill suvni "
                     "\"parchalaydi\" — kislorod sinfdan chiqib ketadi; qolgan qismlar CO₂ bilan "
                     "birlashib glyukoza \"molekulasi\" hosil qiladi (o'quvchilar qo'l ushlashadi).\n\n"
                     "Nima uchun ishlaydi: harakat va rol orqali o'rganish (kinestetik kanal) "
                     "mavhum jarayonni jismoniy tajribaga aylantiradi; kislorodning aynan SUVdan "
                     "chiqishi ko'z oldida sodir bo'ladi — bu eng ko'p uchraydigan xatoni oldini oladi.\n\n"
                     "Vaqt: 10-12 daqiqa. Resurs: rang-barang kartochkalar. Natija: o'quvchi "
                     "jarayonning kirish-chiqish moddalarini va energiya manbaini aytib bera oladi.",
    },
    {
        "slug": "kreativ-yangi-topshiriq",
        "module": Module.CREATIVE, "kind": "CREATIVE", "component": Component.CRE,
        "bloom": BloomLevel.CREATE, "difficulty": 4, "minutes": 35,
        "rubric": "ijodiy-ish",
        "title": "\"Yarataman\" darajasidagi topshiriq o'ylab toping",
        "context": "Ixtiyoriy biologiya mavzusini tanlang.",
        "body": "Bloom taksonomiyasining eng yuqori — \"Yarataman\" darajasiga mos topshiriq "
                "tuzing. Topshiriq o'quvchidan yangi mahsulot (loyiha, model, yechim, ssenariy) "
                "yaratishni talab qilsin.\n\n"
                "Topshiriq matnini, baholash mezonlarini va kutilayotgan natija namunasini yozing.",
        "reference": "\"Yarataman\" darajasining belgisi: yagona to'g'ri javob YO'Q, natija — "
                     "o'quvchi yaratgan yangi mahsulot.\n\n"
                     "Namuna (Ekologiya): \"Maktabingiz hovlisi uchun bioxilma-xillikni oshirish "
                     "loyihasini ishlab chiqing. Loyihada: (1) hozirgi holat tahlili, (2) kamida "
                     "3 ta aniq taklif, (3) har bir taklifning ekologik asosi, (4) natijani "
                     "o'lchash usuli bo'lsin.\"\n\n"
                     "MEZONLAR: ekologik asoslilik (4 ball), amalga oshirish mumkinligi (4), "
                     "natijani o'lchash rejasi (4), taqdimot aniqligi (2).\n\n"
                     "Tipik xato: \"Referat yozing\" yoki \"Taqdimot tayyorlang\" — bu \"Yarataman\" "
                     "emas, ko'pincha \"Bilaman\" darajasidagi ko'chirish faoliyati. Farq: yangi "
                     "mahsulot yaratilyaptimi yoki mavjud ma'lumot qayta joylashtirilyaptimi?",
    },
    {
        "slug": "kreativ-hayot-bilan-boglash",
        "module": Module.CREATIVE, "kind": "CREATIVE", "component": Component.CRE,
        "bloom": BloomLevel.APPLY, "difficulty": 2, "minutes": 25,
        "rubric": "ijodiy-ish",
        "title": "\"Buning menga nima keragi bor?\"",
        "context": "Dars o'rtasida o'quvchi shu savolni berdi. Mavzu — moddalar almashinuvi.",
        "body": "Bu savolga javob beruvchi 5 daqiqalik dars epizodini ishlab chiqing.\n\n"
                "Shart: javob \"imtihonda kerak bo'ladi\" turidagi tashqi motivatsiyaga "
                "tayanmasin — o'quvchining o'z hayoti bilan real bog'lanish topilsin.",
        "reference": "Kuchli yondashuv — javobni O'ZINGIZ bermay, o'quvchiga izlatish:\n\n"
                     "\"Yaxshi savol. Keling, birga tekshiramiz. Kim bugun ertalab nonushta qildi? "
                     "Nima yedingiz? Endi savol: o'sha non 30 daqiqadan keyin qayerga ketdi va "
                     "nima uchun siz hozir charchamay o'tiribsiz?\"\n\n"
                     "Keyin: sport bilan shug'ullanadiganlarga — nima uchun mashqdan keyin "
                     "uglevod kerak; ro'za tutganlarga — organizm energiyani qayerdan oladi; "
                     "kasal bo'lganlarga — nima uchun harorat ko'tarilganda ko'proq energiya sarflanadi.\n\n"
                     "Nima uchun ishlaydi: ma'no o'quvchining shaxsiy tajribasiga ulanganda paydo "
                     "bo'ladi. Bundan tashqari, savolni jiddiy qabul qilish sinfda ishonch muhitini "
                     "kuchaytiradi — keyingi safar ular ko'proq savol beradi.",
    },
]


# ---------------------------------------------------------------------------
# KOMPETENSIYA CHECKLISTI (FR-34)
# ---------------------------------------------------------------------------

COMPETENCY_ITEMS = [
    (Component.ACT, "Dars maqsadini o'lchanadigan qilib yoza olaman",
     "Maqsad o'quvchi harakatini bildiruvchi fe'l bilan yozilgan va tekshirilishi mumkin."),
    (Component.ACT, "45 daqiqalik dars bosqichlarini vaqt bo'yicha taqsimlay olaman",
     "Har bir bosqichga real vaqt ajratilgan va jami 45 daqiqaga sig'adi."),
    (Component.ACT, "Mavzuga mos faol ta'lim metodini asoslab tanlay olaman",
     "Metod tanlovini Bloom darajasi va o'quv maqsadi bilan bog'lay olaman."),
    (Component.ACT, "Rubrika (mezonli baholash jadvali) tuza olaman",
     "3-5 mezon, har bir ball uchun kuzatiladigan tavsif."),
    (Component.ACT, "Tabaqalashtirilgan (uch darajali) topshiriq tizimini tuza olaman",
     "Bir mavzuga turli darajadagi o'quvchilar uchun topshiriq."),
    (Component.COG, "Murakkab biologik jarayonni sodda tilda tushuntira olaman",
     "7-sinf o'quvchisi tushunadigan darajada, mazmunni buzmasdan."),
    (Component.COG, "Ilmiy manbaning ishonchliligini baholay olaman",
     "Muallif, nashr, tekshirilgan tadqiqotga havola mavjudligini tekshiraman."),
    (Component.COG, "O'quvchilarning mavzu bo'yicha tipik xatolarini bilaman",
     "Darsga tayyorlanayotganda tipik xatolarni oldindan rejalashtiraman."),
    (Component.CRE, "Bir mavzuni kamida uch xil usulda tushuntira olaman",
     "Metafora, model, tajriba, rolli o'yin va boshqalar."),
    (Component.CRE, "\"Yarataman\" darajasidagi topshiriq tuza olaman",
     "Yagona to'g'ri javobi yo'q, yangi mahsulot yaratishni talab qiladigan topshiriq."),
    (Component.REF, "O'z darsimni mezonlar asosida tahlil qila olaman",
     "Hissiyotga emas, aniq mezon va dalilga tayanaman."),
    (Component.REF, "Tanqidiy fikrdan xulosa chiqarib, keyingi qadamni belgilay olaman",
     "Fikrni himoyalanmasdan qabul qilaman va aniq harakat rejasiga aylantiraman."),
    (Component.MOT, "O'z kasbiy rivojlanishimni mustaqil rejalashtira olaman",
     "Uzoq muddatli maqsad va haftalik vazifalarga bo'lish."),
    (Component.MOT, "Kasbiy adabiyot va manbalarni muntazam kuzatib boraman",
     "Kamida haftasiga bir marta yangi metodik yoki ilmiy material o'qiyman."),
]


# ---------------------------------------------------------------------------
# NISHONLAR (FR-49, FR-50)
# ---------------------------------------------------------------------------

BADGES = [
    {
        "code": "faol-izlanuvchi", "emoji": "🏅", "title": "Faol izlanuvchi",
        "description": "Muntazam faoliyat — rivojlanishning asosiy sharti.",
        "how": "14 kun ketma-ket faol bo'ling",
        "rules": [("streak", 14)],
    },
    {
        "code": "yosh-tadqiqotchi", "emoji": "🔬", "title": "Yosh tadqiqotchi",
        "description": "Biologik muammolarni tadqiqot mantiqi bilan yechish.",
        "how": "Laboratoriya modulida 5 ta ish bajaring",
        "rules": [("lab_submissions", 5)],
    },
    {
        "code": "kelajak-oqituvchisi", "emoji": "👩‍🏫", "title": "Kelajak o'qituvchisi",
        "description": "Dars loyihalash — pedagogik mahoratning yadrosi.",
        "how": "3 ta dars loyihasi ishlab chiqing",
        "rules": [("lesson_plans", 3)],
    },
    {
        "code": "kreativ-pedagog", "emoji": "💡", "title": "Kreativ pedagog",
        "description": "Nostandart pedagogik yechim yaratish qobiliyati.",
        "how": "Kreativ modulda 4 ta ish bajaring",
        "rules": [("creative_works", 4)],
    },
    {
        "code": "innovatsion-biolog", "emoji": "🌱", "title": "Innovatsion biolog",
        "description": "Raqamli vositalarni ta'limda qo'llay olish.",
        "how": "Raqamli biologiya modulida 3 ta mahsulot yarating",
        "rules": [("digital_works", 3)],
    },
    {
        "code": "mustaqil-izlanuvchi", "emoji": "📚", "title": "Mustaqil izlanuvchi",
        "description": "Kasbiy bilimni mustaqil kengaytirish.",
        "how": "10 ta darsni o'zlashtiring",
        "rules": [("lessons_passed", 10)],
    },
    {
        "code": "refleksiv-amaliyotchi", "emoji": "🔍", "title": "Refleksiv amaliyotchi",
        "description": "O'z faoliyatini muntazam tahlil qilish odati.",
        "how": "15 ta refleksiya yozuvi yarating",
        "rules": [("reflections", 15)],
    },
    {
        "code": "oz-ustida-ishlovchi", "emoji": "📈", "title": "O'z ustida ishlovchi",
        "description": "O'z natijangizga nisbatan aniq o'sish — eng muhim ko'rsatkich.",
        "how": "SDI ko'rsatkichingizni 15 foiz punktga oshiring",
        "rules": [("sdi_growth", 15)],
    },
    {
        "code": "maqsadga-sodiq", "emoji": "🎯", "title": "Maqsadga sodiq",
        "description": "Boshlangan ishni oxiriga yetkazish.",
        "how": "3 ta maqsadni to'liq yakunlang",
        "rules": [("goals_done", 3)],
    },
]


# ---------------------------------------------------------------------------
# REFLEKSIYA SAVOLLARI (FR-38) — rotatsiya uchun bir nechta variant
# ---------------------------------------------------------------------------

REFLECTION_PROMPTS = [
    (1, "Bugun nimani o'rgandim?",
     "Faktni emas, tushunchani yozing: ilgari qanday o'ylardingiz va endi qanday tushunyapsiz?"),
    (1, "Bu ishda men uchun eng yangi narsa nima bo'ldi?",
     "Aniq bir g'oya, metod yoki fakt — va u sizga nimani ochdi."),
    (2, "Nimani yaxshi bajardim?",
     "O'zingizni maqtash emas — qaysi harakatingiz aynan natija berdi va nega."),
    (2, "Ishimning qaysi qismidan mamnunman?",
     "Sabab bilan: nima uchun aynan shu qism yaxshi chiqdi?"),
    (3, "Qaysi jihatimni rivojlantirishim kerak?",
     "\"Hammasini\" emas — bitta aniq ko'nikma yoki bilim sohasini nomlang."),
    (3, "Qayerda qiynaldim va nima uchun?",
     "Qiyinchilikning sababini toping: bilim yetishmadimi, vaqtmi, yoki yondashuvmi?"),
    (4, "Keyingi safar nimani boshqacha qilaman?",
     "Aniq harakat: ertaga yoki keyingi darsda nimani boshqacha qilasiz?"),
    (4, "Bu tajribani keyingi ishimda qanday qo'llayman?",
     "Bitta aniq qadam ayting — \"harakat qilaman\" emas, \"nimani, qachon\"."),
]
