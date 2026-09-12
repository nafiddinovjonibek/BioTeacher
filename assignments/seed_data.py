"""
Topshiriqlar va rubrikalar bazasi — haqiqiy pedagogik mazmun bilan.

RUBRICS     — mezonli baholash jadvallari (FR-31, FR-37)
ASSIGNMENTS — laboratoriya, pedagogik keys, dars loyihasi, raqamli, ijodiy topshiriqlar va vizual keyslar
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
    {
        "slug": "vizual-tahlil",
        "title": "Vizual keys tahlili rubrikasi",
        "description": "Tasvirga asoslangan muammoli vaziyatni mustaqil tahlil qilishni baholash uchun.",
        "criteria": [
            {"name": "Kuzatish aniqligi", "max_score": 4, "weight": 1.0,
             "hint": "Tasvirdagi faktlar to'liq va izohsiz sanab o'tilganmi?",
             "levels": {"0": "Kuzatish yo'q yoki darhol xulosaga o'tilgan",
                        "2": "Asosiy belgilar bor, muhim tafsilotlar tushib qolgan",
                        "4": "Barcha muhim belgilar aniq, qiymat va birliklari bilan keltirilgan"}},
            {"name": "Muammoni ko'ra bilish", "max_score": 4, "weight": 1.0,
             "hint": "G'ayrioddiy holat aniq savol shaklida qo'yilganmi?",
             "levels": {"0": "Muammo aniqlanmagan", "2": "Muammo umumiy gap bilan aytilgan",
                        "4": "Muammo aniq, tekshirsa bo'ladigan savol shaklida"}},
            {"name": "Ilmiy asoslash", "max_score": 4, "weight": 1.2,
             "hint": "Tushuntirish biologik qonuniyatga va tasvirdagi dalilga tayanadimi?",
             "levels": {"0": "Asoslash yo'q yoki xato", "2": "Qonuniyat nomlangan, dalil bilan bog'lanmagan",
                        "4": "Sabab-oqibat zanjiri tasvirdagi dalillar bilan isbotlangan"}},
            {"name": "Pedagogik qo'llash", "max_score": 4, "weight": 1.0,
             "hint": "Keys darsda qanday ishlatilishi aniq ko'rsatilganmi?",
             "levels": {"0": "Ko'rsatilmagan", "2": "Umumiy g'oya bor",
                        "4": "Sinf, maqsad va yo'naltiruvchi savollar aniq berilgan"}},
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

    # ================= MUAMMOLI VIZUAL KEYSLAR (mustaqil tahlil) =================
    # `visual` — static/ ichidagi tasvir, `section` — fan slugi, `alt` — tasvirning matnli tavsifi.
    {
        "slug": "vizual-plazmoliz",
        "module": Module.VISUAL, "kind": "VISUAL", "component": Component.COG,
        "bloom": BloomLevel.ANALYZE, "difficulty": 2, "minutes": 25,
        "rubric": "vizual-tahlil", "section": "hujayra-biologiyasi",
        "visual": "img/cases/plazmoliz.svg",
        "alt": "Mikroskopning ikki ko'rish maydoni. A: qizil piyoz po'stining cho'ziq hujayralari, binafsha "
               "rangli hujayra shirasi hujayrani to'liq egallagan. B: xuddi shunday hujayralar, binafsha qism "
               "kichrayib, to'qroq tusga kirgan va hujayra devoridan ajralgan; 1 raqami binafsha qismni, "
               "2 raqami devor bilan binafsha qism orasidagi rangsiz bo'shliqni ko'rsatadi.",
        "title": "Mikroskop ostidagi ikki preparat",
        "context": "Qizil piyoz po'stidan ikkita preparat tayyorlandi. A preparatga distillangan suv, B preparatga "
                   "5% li osh tuzi (NaCl) eritmasi tomizildi. 10 daqiqadan keyin ikkalasi ham 400 marta "
                   "kattalashtirib kuzatildi.",
        "body": "Tasvirni diqqat bilan kuzating va A hamda B preparatdagi hujayralarni solishtiring.\n\n"
                "B preparatda hujayraning qaysi qismi o'zgardi, qaysi qismi o'zgarmadi? 1 va 2 raqamlari bilan "
                "belgilangan joylarda nima bor? Nima uchun hujayra devori o'z shaklini saqlab qoldi?\n\n"
                "B preparatdagi hujayralarni qanday qilib yana A holatiga qaytarish mumkin va bu tajriba "
                "hujayralar haqida nimani isbotlaydi?",
        "reference": "KUZATISH: A da binafsha rangli hujayra shirasi hujayrani to'liq to'ldirgan. B da hujayra "
                     "devorlari o'zgarmagan, binafsha qism esa kichrayib, to'qroq tusga kirgan va devordan ajralgan; "
                     "ular orasida rangsiz bo'shliq paydo bo'lgan.\n\n"
                     "MUAMMO: nima uchun hujayraning ichki qismi qisqardi-yu, devori qisqarmadi?\n\n"
                     "TUSHUNTIRISH: bu — plazmoliz. Tashqi eritma gipertonik, shuning uchun suv osmos yo'li bilan "
                     "vakuoladan tashqariga chiqadi: protoplast (1 — sitoplazma va vakuola) kichrayadi, shira "
                     "quyuqlashib to'qroq ko'rinadi. Hujayra devori sellulozadan iborat, mustahkam va eritmalarni "
                     "erkin o'tkazadi — u shaklini saqlaydi, devor bilan protoplast orasidagi bo'shliqni (2) esa tashqi "
                     "tuz eritmasi egallaydi. Preparatga yana toza suv tomizilsa, deplazmoliz kuzatiladi — bu "
                     "hujayralar tirikligini va membrananing yarim o'tkazuvchanligini isbotlaydi.\n\n"
                     "DARSDA: 6-7-sinfda avval faqat A tasvirini ko'rsatib, \"tuz tomizsak nima bo'ladi?\" deb bashorat "
                     "yozdiriladi, keyin B ko'rsatiladi. Yo'naltiruvchi savollar: \"Qaysi qism o'zgarmadi?\", "
                     "\"Bo'shliqni nima to'ldirdi?\", \"Nega sho'r tuproqda o'simlik so'liydi?\"",
    },
    {
        "slug": "vizual-xloroz",
        "module": Module.VISUAL, "kind": "VISUAL", "component": Component.COG,
        "bloom": BloomLevel.ANALYZE, "difficulty": 3, "minutes": 30,
        "rubric": "vizual-tahlil", "section": "hujayra-biologiyasi",
        "visual": "img/cases/xloroz.svg",
        "alt": "Bir xil navdagi ikki o'simlik. 1-o'simlikda pastki, qari barglar butunlay sarg'aygan, yuqori yosh "
               "barglar yashil. 2-o'simlikda pastki barglar yashil, yuqori yosh barglar sarg'aygan, lekin ularning "
               "tomirlari yashil qolgan.",
        "title": "Sarg'aygan barglar qayerda?",
        "context": "Bir xil navdagi ikki o'simlik bir xil sharoitda o'stirildi, faqat oziq eritmasi farq qildi: har "
                   "birida bittadan mineral element yetishmadi. To'rt haftadan keyin barglarda xloroz (sarg'ayish) "
                   "paydo bo'ldi.",
        "body": "Ikki o'simlikdagi xlorozni solishtiring: u qaysi barglarda boshlandi va barg yuzasida qanday "
                "taqsimlangan?\n\n"
                "Har bir o'simlikda qaysi element yetishmaydi deb o'ylaysiz? Nima uchun bir o'simlikda qari, "
                "boshqasida yosh barglar zararlandi? Taxminingizni qanday tajriba bilan tekshirasiz?",
        "reference": "KUZATISH: 1-o'simlikda pastki (qari) barglar bir tekis sarg'aygan, yuqori barglar yashil. "
                     "2-o'simlikda aksincha — yosh barglar sarg'aygan, lekin ularning tomirlari yashil qolgan "
                     "(tomirlararo xloroz).\n\n"
                     "TUSHUNTIRISH: 1 — azot (N) yetishmovchiligi. Azot o'simlik ichida harakatchan: yetishmaganda "
                     "o'simlik uni qari barglardagi oqsil va xlorofilldan ajratib, yosh barglarga ko'chiradi — shuning "
                     "uchun avval pastki barglar butunlay sarg'ayadi. 2 — temir (Fe) yetishmovchiligi. Temir "
                     "harakatsiz, qari barglardan qayta taqsimlanmaydi, shuning uchun yangi o'sayotgan barglar zarar "
                     "ko'radi; temir xlorofill sintezida ishtirok etadigan fermentlar uchun zarur.\n\n"
                     "TEKSHIRISH: har bir o'simlikning yarmiga taxmin qilingan element qo'shiladi, qolgan yarmi "
                     "nazorat bo'ladi; 2-3 haftada yangi barglar yashillashsa, taxmin tasdiqlanadi.\n\n"
                     "DARSDA: 6-sinf \"O'simliklarning mineral oziqlanishi\" mavzusida yoki maktab o'quv-tajriba "
                     "uchastkasida kuzatish topshirig'i sifatida. Savollar: \"Qaysi barglar birinchi zararlandi?\", "
                     "\"Element o'simlik ichida ko'chsa, qaysi barg birinchi zarar ko'radi?\"",
    },
    {
        "slug": "vizual-ferment-harorat",
        "module": Module.VISUAL, "kind": "VISUAL", "component": Component.COG,
        "bloom": BloomLevel.ANALYZE, "difficulty": 3, "minutes": 30,
        "rubric": "vizual-tahlil", "section": "genetika",
        "visual": "img/cases/ferment-harorat.svg",
        "alt": "Chiziqli grafik: so'lak amilazasining reaksiya tezligi haroratga bog'liq. 0 °C da 4%, 20 °C da 33%, "
               "37 °C da eng yuqori 100%, 45 °C da 60%, 50 °C da 27%, 60 °C da 2%, 65 °C dan yuqorida nol. Yonida "
               "qo'shimcha tajriba: 0 °C da ushlangan ferment 37 °C da 97%, 70 °C da ushlangani 2% faollik ko'rsatgan.",
        "title": "Ferment faolligi va harorat",
        "context": "Talabalar so'lak amilazasining kraxmalni parchalash tezligini 0 °C dan 70 °C gacha bo'lgan haroratda "
                   "o'lchashdi (yod sinovi bilan). Qo'shimcha tajribada ferment 10 daqiqa davomida 0 °C va 70 °C da "
                   "ushlab turildi, so'ng yana 37 °C da sinaldi.",
        "body": "Grafikni tahlil qiling: harorat ortishi bilan reaksiya tezligi qanday o'zgaradi? Egri chiziq nima "
                "uchun simmetrik emas — o'ng tomoni keskinroq tushadi?\n\n"
                "Qo'shimcha tajriba natijalarini tushuntiring: nega sovitilgan ferment faolligini tiklaydi, qizdirilgani "
                "esa yo'q? Issiq buloqlarda yashovchi bakteriya fermentining grafigi qanday bo'lishini bashorat qiling.",
        "reference": "KUZATISH: 0 °C dan 37 °C gacha tezlik asta-sekin ortadi, 37 °C atrofida eng yuqori (100%), keyin "
                     "keskin tushib, 60 °C dan yuqorida deyarli nolga teng. 0 °C da ushlangan ferment 37 °C da 97% "
                     "faollik ko'rsatdi, 70 °C da ushlangani — atigi 2%.\n\n"
                     "TUSHUNTIRISH: harorat ortganda molekulalarning kinetik energiyasi va to'qnashuvlar soni oshadi — "
                     "tezlik ortadi. Optimumdan yuqorida oqsilning uchlamchi tuzilmasini ushlab turgan kuchsiz (vodorod "
                     "va boshqa) bog'lar uziladi, faol markaz shakli buziladi — denaturatsiya. U tez kechadi va "
                     "qaytmaydi, shuning uchun egri o'ng tomonda keskin tushadi va qizdirilgan ferment tiklanmaydi. Past "
                     "haroratda esa tuzilma buzilmaydi, faqat harakat sekinlashadi — isitilganda faollik qaytadi. "
                     "Termofil bakteriya fermentining optimumi ancha yuqori (70–80 °C atrofida) bo'ladi.\n\n"
                     "DARSDA: \"ferment o'ladi\" degan xato iborani ishlatmaslik kerak — ferment tirik emas, u "
                     "denaturatsiyaga uchraydi. 9-sinfda so'lak va kraxmal bilan uch xil haroratda (muzli suv, 37 °C, "
                     "qaynoq suv) yod sinovi o'tkazib, o'quvchilar grafikni o'zlari chizishadi.",
    },
    {
        "slug": "vizual-shajara",
        "module": Module.VISUAL, "kind": "VISUAL", "component": Component.COG,
        "bloom": BloomLevel.EVALUATE, "difficulty": 4, "minutes": 35,
        "rubric": "vizual-tahlil", "section": "genetika",
        "visual": "img/cases/shajara.svg",
        "alt": "Uch avlodli oila shajarasi. I avlodda belgisi yo'q ota (I-1) va ona (I-2). Ularning to'rt farzandidan "
               "qizi II-2 va o'g'li II-6 da belgi bor, o'g'li II-3 va qizi II-5 da yo'q. Belgili II-2 belgisi yo'q "
               "erkak II-1 ga turmushga chiqqan, ularning o'g'li III-1 va qizi III-2 da belgi yo'q. II-3 va uning "
               "rafiqasi II-4 ning qizi III-3 va o'g'li III-4 da ham belgi yo'q.",
        "title": "Oila shajarasi: belgi qanday irsiylanadi?",
        "context": "Shifokor-genetik oilada kam uchraydigan bir belgini o'rganish uchun uch avlod shajarasini tuzdi. "
                   "Oila a'zolari orasida qarindosh nikoh yo'q.",
        "body": "Shajarani tahlil qiling. Belgi dominantmi yoki retsessiv, autosomaga yoki X-xromosomaga birikkanmi? "
                "Har bir xulosangizni shajaradagi aniq oila a'zosi bilan isbotlang.\n\n"
                "I-1 va I-2 ning genotiplarini yozing. Ularning navbatdagi farzandida belgi namoyon bo'lish ehtimoli "
                "qancha? II-3 ning geterozigota (tashuvchi) bo'lish ehtimolini hisoblang.",
        "reference": "KUZATISH: belgisi yo'q ota-onadan (I-1, I-2) belgili qiz (II-2) va o'g'il (II-6) tug'ilgan. "
                     "Belgili ona II-2 ning o'g'li III-1 da belgi yo'q.\n\n"
                     "TUSHUNTIRISH: 1) Sog' ota-onadan belgili farzand tug'ilishi belgi RETSESSIV ekanini ko'rsatadi "
                     "(dominant bo'lsa, ota-onadan kamida birida namoyon bo'lardi). 2) Belgili qiz II-2 ning otasi I-1 "
                     "sog' — agar belgi X-xromosomaga birikkan retsessiv bo'lsa, qiz ikkala X ni ham belgili olgan, "
                     "demak otasi ham belgili bo'lishi kerak edi. Shuningdek, belgili ona II-2 ning o'g'li III-1 sog'. "
                     "Demak, belgi AUTOSOM-RETSESSIV.\n\n"
                     "Genotiplar: I-1 — Aa, I-2 — Aa, II-2 va II-6 — aa. Navbatdagi farzandda belgi ehtimoli: "
                     "Aa × Aa → 1/4 (25%). II-3 sog', demak aa emas: qolgan AA : Aa : Aa ichidan tashuvchi bo'lish "
                     "ehtimoli 2/3. III-1 va III-2 albatta Aa (tashuvchi): ular onasidan a oladi, lekin sog'.\n\n"
                     "DARSDA: 10-sinfda \"farazni rad etish\" algoritmi — har bir irsiylanish turini navbatma-navbat "
                     "tekshirib, uni inkor qiladigan shaxsni topish. Hayotiy misollar: albinizm, fenilketonuriya.",
    },
    {
        "slug": "vizual-trofik-kaskad",
        "module": Module.VISUAL, "kind": "VISUAL", "component": Component.COG,
        "bloom": BloomLevel.ANALYZE, "difficulty": 3, "minutes": 30,
        "rubric": "vizual-tahlil", "section": "ekologiya",
        "visual": "img/cases/trofik-kaskad.svg",
        "alt": "Chapda oziq to'ri sxemasi: o'tlar va tol butalari bug'uga, tol butalari qunduzga oziq bo'ladi, bug'u "
               "bo'riga oziq bo'ladi; qo'shiqchi qushlar tol butalarida yashaydi. O'ngda to'rtta kichik ustunli "
               "diagramma — bo'rilar qaytarilishidan oldin va 15 yildan keyin: bug'ular soni 100% dan 45% ga kamaygan, "
               "tol butalarining balandligi 0,8 m dan 2,4 m ga, qunduz oilalari 1 tadan 9 taga, qo'shiqchi qush "
               "turlari 8 tadan 14 taga ko'paygan.",
        "title": "Yirtqich qaytgan vodiy",
        "context": "Tog' vodiysida bo'rilar yo'q qilingach, bug'ular ko'payib ketdi. Oradan yillar o'tib vodiyga "
                   "bo'rilar qayta keltirildi. Diagrammada 15 yil davomidagi o'zgarishlar berilgan (o'quv maqsadida "
                   "soddalashtirilgan ma'lumotlar).",
        "body": "Oziq to'ri va diagrammani birga tahlil qiling. Bo'rilar tol butalarini yemaydi — unda nima uchun "
                "ular qaytgach butalar baland o'sdi, qunduz va qushlar ko'paydi? Ta'sir zanjirini bosqichma-bosqich "
                "yozing.\n\n"
                "O'zgarishlarning sababi aynan bo'rilar ekanini isbotlash uchun yana qanday ma'lumot kerak? Agar "
                "bo'rilar yana yo'qolsa, 10 yildan keyin nima bo'lishini bashorat qiling.",
        "reference": "KUZATISH: bo'rilar qaytgach bug'ular soni ikki baravardan ko'proq kamaygan, tol butalari uch "
                     "baravar baland bo'lgan, qunduz oilalari 1 tadan 9 taga, qush turlari 8 tadan 14 taga ko'paygan.\n\n"
                     "TUSHUNTIRISH: bu — trofik kaskad. Yirtqich o'txo'rlar sonini kamaytiradi va ularning xulqini "
                     "o'zgartiradi (bug'ular ochiq daryo bo'yida uzoq qolmaydi). O'txo'r bosimi kamaygach, tol butalari "
                     "tiklanadi; tol — qunduzning oziq va qurilish materiali, qunduz to'g'onlari botqoqliklar hosil "
                     "qilib, yangi yashash joylarini yaratadi; butalarda qushlar uya quradi. Yuqori trofik darajadagi "
                     "bitta tur pastki darajalarga zanjir bo'ylab ta'sir qiladi.\n\n"
                     "SABABIYAT: bir vaqtda o'zgargan boshqa omillarni istisno qilish kerak — yog'ingarchilik, ov, "
                     "boshqa yirtqichlar (ayiq), yaylov. Bo'ri bo'lmagan qo'shni vodiy bilan taqqoslash (nazorat) eng "
                     "kuchli dalil bo'ladi. Bo'rilar yana yo'qolsa: bug'ular ko'payadi, butalar qayta yeyiladi, qunduz "
                     "va qushlar kamayadi. Mashhur real misol — AQShdagi Yellouston milliy bog'i (1995 yildan bo'rilar "
                     "qayta keltirilgan); u yerda ham olimlar ta'sir kuchi haqida hali bahslashadi.\n\n"
                     "DARSDA: 9-11-sinf ekologiya. O'quvchilar zanjirni kartochkalar bilan tuzadi va \"bitta tur "
                     "yo'qolsa nima bo'ladi?\" savoliga javob beradi — korrelyatsiya va sababiyat farqini ham shu yerda "
                     "ko'rsatish mumkin.",
    },
    {
        "slug": "vizual-oquvchi-daftari",
        "module": Module.VISUAL, "kind": "VISUAL", "component": Component.ACT,
        "bloom": BloomLevel.EVALUATE, "difficulty": 3, "minutes": 35,
        "rubric": "vizual-tahlil", "section": "metodika",
        "visual": "img/cases/oquvchi-daftari.svg",
        "alt": "6-sinf o'quvchisi daftaridagi rasm: quyosh, o'simlik va tuproq. Strelkalar: tuproqdan ildizga \"ovqat\" "
               "va \"suv\", havodan bargga \"kislorod\", bargdan havoga \"karbonat angidrid\", quyoshdan o'simlikka "
               "\"issiqlik\". Pastida yozuv: \"O'simlik ovqatini tuproqdan oladi. Barglar kislorod bilan nafas oladi. "
               "Quyosh o'simlikni isitadi.\"",
        "title": "O'quvchi daftaridagi fotosintez sxemasi",
        "context": "\"Fotosintez\" mavzusidan keyin 6-sinf o'quvchilariga \"O'simlik qanday oziqlanadi? Sxema "
                   "chizing\" degan topshiriq berildi. Rasmda bitta o'quvchining ishi. Sinfdagi 26 o'quvchidan "
                   "17 tasining sxemasi shunga o'xshash chiqdi.",
        "body": "O'quvchining sxemasini tahlil qiling: undagi qaysi tasavvurlar ilmiy jihatdan noto'g'ri yoki to'liq "
                "emas? Qaysi biri eng asosiy (qolganlari undan kelib chiqadigan) xato?\n\n"
                "Bu tasavvurlar qayerdan paydo bo'lgan bo'lishi mumkin? Xatoni shunchaki \"to'g'ri javob\"ni aytish "
                "bilan emas, o'quvchi o'zi anglaydigan qilib tuzatish uchun 10-15 daqiqalik dars fragmentini rejalang.",
        "reference": "KUZATISH: sxemada \"ovqat\" tuproqdan ildizga kiradi; bargga kislorod kiradi, karbonat angidrid "
                     "chiqadi; quyosh faqat \"issiqlik\" beradi. Organik modda (glyukoza, kraxmal) va yorug'lik "
                     "energiyasi umuman yo'q.\n\n"
                     "TAHLIL: asosiy xato — \"o'simlik ovqatni tayyor holda tuproqdan oladi\". Aslida tuproqdan suv va "
                     "mineral tuzlar olinadi, organik moddani o'simlik o'zi — bargda, yorug'lik energiyasi hisobiga "
                     "karbonat angidrid va suvdan sintez qiladi. Gazlar yo'nalishi fotosintezga teskari, lekin bu "
                     "to'liq xato emas: o'quvchi nafas olishni tasvirlagan — o'simlik ham kecha-kunduz nafas oladi. "
                     "Demak, u ikki jarayonni chalkashtirgan. Quyoshning roli — issiqlik emas, ENERGIYA manbai. "
                     "Manbalar: kundalik til (\"o'simlikni o'g'itlab ovqatlantiramiz\"), hayvonlar bilan o'xshatish.\n\n"
                     "FRAGMENT (kognitiv to'qnashuv): 1) Van Gelmont tajribasi: tol novdasi 5 yilda taxminan 74 kg ga "
                     "og'irlashgan, tuproq esa atigi 57 g ga kamaygan — \"massa qayerdan keldi?\" (5 daq). 2) Juftlikda "
                     "bashorat va muhokama (5 daq). 3) Yorug'da va qorong'ida saqlangan barglarda kraxmalga yod sinovi "
                     "natijasini ko'rsatish (3 daq). 4) O'quvchi sxemasini o'zi qayta chizadi — fotosintez va nafas "
                     "olish alohida rangda (2 daq). Formativ savol: \"Yo'g'on daraxt tanasining massasi asosan nimadan "
                     "hosil bo'lgan?\"",
    },
    {
        "slug": "vizual-ish-qobiliyati",
        "module": Module.VISUAL, "kind": "VISUAL", "component": Component.ACT,
        "bloom": BloomLevel.APPLY, "difficulty": 2, "minutes": 25,
        "rubric": "vizual-tahlil", "section": "yosh-fiziologiya-va-gigiyena-fani",
        "visual": "img/cases/ish-qobiliyati.svg",
        "alt": "Ikki chiziqli grafik. Chapda kun davomida ish qobiliyati: 1-darsda 72%, 2-darsda 90%, 3-darsda 100%, "
               "4-darsda 88%, 5-darsda 74%, 6-darsda 63%. O'ngda hafta davomida: dushanba 82%, seshanba 96%, "
               "chorshanba 100%, payshanba 90%, juma 76%, shanba 68%.",
        "title": "O'quvchining ish qobiliyati grafigi",
        "context": "Maktab psixologi 7-sinf o'quvchilarining aqliy ish qobiliyatini kun va hafta davomida (diqqat "
                   "testi — bajarish tezligi va xatolar soni bo'yicha) o'lchadi. Grafiklarda o'rtacha natija "
                   "berilgan, eng yuqori qiymat 100% deb olingan.",
        "body": "Grafiklarni tahlil qiling: kun va hafta davomida ish qobiliyati qanday o'zgaradi? Egri chiziqda qaysi "
                "fiziologik davrlarni ajratish mumkin?\n\n"
                "Biologiyadan nazorat ishini qaysi kun va nechanchi darsga qo'yish maqsadga muvofiq? 45 daqiqalik dars "
                "ichida ham shunday qonuniyat bor — darsning tuzilishini shunga moslab rejalang.",
        "reference": "KUZATISH: kun davomida ish qobiliyati 1-darsda nisbatan past (72%), 2-3-darsda eng yuqori, "
                     "5-6-darsga kelib 63% gacha tushadi. Hafta davomida seshanba-chorshanba eng yuqori, juma-shanba "
                     "eng past.\n\n"
                     "TUSHUNTIRISH: uch davr ajratiladi — ishga kirishish (organizm faoliyat ritmiga moslashadi), "
                     "barqaror yuqori ish qobiliyati va charchash (asab hujayralarida himoya tormozlanishi rivojlanadi). "
                     "Dushanba — hafta boshidagi ishga kirishish, hafta oxiri — to'plangan charchoq.\n\n"
                     "QO'LLASH: nazorat ishi seshanba yoki chorshanba kuni, 2-3-darsga qo'yiladi. Dars ichida: dastlabki "
                     "5-7 daqiqa — kirishish (takrorlash, qiziqarli savol), taxminan 10-30-daqiqalar — eng murakkab yangi "
                     "material, 25-30-daqiqadan keyin faoliyat turini almashtirish yoki jismoniy daqiqa, oxirida — "
                     "mustahkamlash. Individual farqlarni (sog'liq, uyqu, bioritm) ham hisobga olish kerak.\n\n"
                     "DARSDA: bo'lajak o'qituvchi uchun — dars jadvali va dars tuzilishini gigiyena talablariga moslash "
                     "ko'nikmasi; o'quvchilar bilan esa \"Men qachon yaxshi o'qiyman?\" o'z-o'zini kuzatish loyihasi.",
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
