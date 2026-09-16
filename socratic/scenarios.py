"""
AI-sokratik suhbat ssenariylari — «Yoshga oid fiziologiya va gigiyena» fani bo'yicha.

Har bir mavzu — yo'naltiruvchi savollar zanjiri. Har bir savolda:
  ask       — savol matni;
  concepts  — javobda kutiladigan tushunchalar: {name, kw (kalit so'z o'zaklari), probe (yetishmasa beriladigan savol)};
  wrong     — tipik noto'g'ri tasavvur: (kalit so'zlar, qarshi savol);
  hint      — «Bilmayman» deyilganda beriladigan ishora (javobni to'liq aytmaydi);
  insight   — ikki urinishdan keyin ham topilmasa, qisqa tushuntirish.

Kalit so'zlar kichik harfda va tutuq belgisisiz yoziladi («osish», «qozgal»): javob ham shu ko'rinishga keltiriladi.

Mavzular o'sib borayotgan organizm fiziologiyasi va maktab gigiyenasini qamrab oladi:
tayanch-harakat tizimi, nerv tizimi va charchash, uyqu, ko'rish, ovqatlanish-nafas muhiti,
balog'at yoshi. Har bir suhbat oxirida bo'lajak o'qituvchi shu mavzuni darsda qanday ochib
berishini o'ylaydi (`TEACH_STEP`).
"""

TEACH_STEP = {
    "ask": "Endi o‘qituvchi sifatida o‘ylab ko‘ring: bu mavzuni o‘quvchilarga tayyor ta’rif va nasihat bermasdan qanday ochib berasiz? "
           "Qaysi savol, o‘z-o‘zini kuzatish yoki oddiy o‘lchovdan boshlaysiz?",
    "concepts": [
        {"name": "tajriba yoki o‘z-o‘zini kuzatish", "kw": ["tajriba", "kuzat", "olcha", "sinov", "sinab", "anketa", "namoyish", "kundalik"],
         "probe": "O‘quvchilar buni o‘z tanasida yoki sinfda ko‘rishi uchun qanday oddiy o‘lchov yoki kuzatish tashkil qilish mumkin?"},
        {"name": "muammoli savol", "kw": ["savol", "muammo", "nega", "nima uchun", "bashorat", "taxmin", "farazi"],
         "probe": "Darsni qaysi «nega?» savoli bilan boshlasangiz, o‘quvchilar javobni o‘zlari izlashga kirishadi?"},
        {"name": "hayotiy misol", "kw": ["misol", "hayot", "kundalik", "uyda", "sinfda", "vaziyat", "holat"],
         "probe": "O‘quvchilarning kundalik hayotidan — kun tartibi, dars, tanaffusdan — bu mavzuga qanday misol keltira olasiz?"},
    ],
    "wrong": [(["tushuntiraman", "aytib beraman", "ta'rif beraman", "tarif beraman", "yozdiraman", "o'qib beraman", "oqib beraman", "nasihat"],
               "Agar siz qoidani o‘zingiz aytib bersangiz, o‘quvchi nimani o‘ylaydi va nimani kashf qiladi? Gigiyena qoidasi nasihat sifatida emas, "
               "o‘z tanasi haqidagi kashfiyot sifatida qabul qilinishi uchun darsning birinchi 5 daqiqasida nima qilardingiz?")],
    "hint": "Ishora: yoshga oid fiziologiya darsining kuchi shundaki, o‘quvchi tekshiruv obyektini o‘zi bilan olib yuradi — bu uning o‘z organizmi. "
            "Sinfda o‘lchash yoki kuzatish mumkin bo‘lgan qanday ko‘rsatkich bor?",
    "insight": "Bunday dars odatda uch qadamdan iborat: o‘z-o‘zini kuzatish yoki oddiy o‘lchov → o‘quvchilarning taxmini → fiziologik sabab bilan tekshirish. "
               "Shunda gigiyena qoidasi tayyor talab emas, o‘z xulosa bo‘lib qoladi.",
}

TOPICS = {
    "skelet": {
        "title": "Qomat va tayanch-harakat tizimi",
        "icon": "user",
        "section": "Tayanch-harakat tizimi",
        "teaser": "Nega qomat aynan maktab yoshida buziladi?",
        "detect": ["qomat", "skelet", "suyak", "umurtqa", "skolioz", "bukri", "parta", "tayanch-harakat", "mushak", "sumka", "ryukzak"],
        "opening": "Qomat buzilishi — maktab yoshidagi eng ko‘p uchraydigan gigiyenik muammo. Men tayyor javob bermayman: "
                   "bir necha vaziyatni birga tahlil qilamiz, xulosaga esa o‘zingiz kelasiz.",
        "steps": [
            {
                "ask": "Bir sinfda 1-sinfda qomati buzilgan o‘quvchilar deyarli yo‘q, 8–9-sinfga borib esa ular sezilarli ko‘payadi. "
                       "Bolaning skeleti kattalarnikidan nimasi bilan farq qiladi va nega aynan shu yillarda qomat oson buziladi?",
                "concepts": [
                    {"name": "suyakda organik moddalar ko‘p — skelet egiluvchan", "kw": ["organik", "egiluvchan", "egilu", "yumshoq", "elastik", "moslashuvchan"],
                     "probe": "Bola suyagida mineral tuzlarga nisbatan qaysi moddalar ko‘proq? Shuning uchun u kam sinadi, lekin oson nima bo‘ladi?"},
                    {"name": "suyaklanish tugallanmagan (tog‘ay qismlar)", "kw": ["togay", "suyaklan", "tugallanmagan", "shakllanmagan", "osish zonasi", "davom etadi"],
                     "probe": "O‘sish davrida suyakning uchlarida qanday to‘qima saqlanib qoladi va bu nimani anglatadi?"},
                    {"name": "noto‘g‘ri holatning uzoq takrorlanishi", "kw": ["parta", "holat", "otirish", "sumka", "yelka", "uzoq", "har kuni"],
                     "probe": "Endi omilni qidiring: o‘quvchi kuniga necha soatni bir xil holatda o‘tkazadi va bu holat qanday bo‘ladi?"},
                ],
                "wrong": [(["irsiy", "genetik", "tugma", "ota-ona"],
                           "Irsiy moyillik bor, lekin irsiyat 8 yil ichida o‘zgarmaydi — qomati buzilganlar soni esa aynan shu 8 yilda bir necha barobar ortadi. "
                           "Demak, shu yillarda kuchayadigan boshqa qanday omil bor?")],
                "hint": "Ishora: bolaning suyagi tarkibi kattalarnikidan farq qiladi. Sinmaydigan, lekin osongina egiladigan novdani tasavvur qiling — "
                        "bunday skeletga uzoq davom etgan bir tomonlama bosim qanday ta’sir qiladi?",
                "insight": "Bolalar suyagida organik moddalar ulushi katta va suyaklanish tugallanmagan — skelet egiluvchan. Shuning uchun uzoq takrorlanadigan "
                           "noto‘g‘ri holat (partada qiyshayib o‘tirish, bir yelkada og‘ir sumka) qomatni turg‘un ravishda o‘zgartiradi.",
            },
            {
                "ask": "Ikki o‘quvchi bir xil og‘irlikdagi kitoblarni tashiydi: biri — bir yelkaga osilgan sumkada, ikkinchisi — ikki lyamkali ryukzakda. "
                       "Og‘irlik bir xil bo‘lsa, umurtqaga tushadigan yuk nimasi bilan farq qiladi?",
                "concepts": [
                    {"name": "yukning teng taqsimlanishi", "kw": ["taqsim", "teng", "ikki yelka", "bir tekis", "simmetri", "bolinadi"],
                     "probe": "Ryukzakdagi yuk necha nuqtaga tushadi, bir yelkadagi sumkaniki-chi? Bu umurtqa uchun nimani o‘zgartiradi?"},
                    {"name": "mushaklarning bir tomonlama zo‘riqishi", "kw": ["mushak", "bir tomon", "kuchlan", "zoriq", "assimetri", "muvozanat"],
                     "probe": "Bir yelkada yuk bo‘lsa, tana muvozanatni qanday saqlaydi? Qaysi tomondagi mushaklar doimiy tarang bo‘lib qoladi?"},
                    {"name": "umurtqaning yon egilishi (skolioz)", "kw": ["skolioz", "umurtqa", "yon", "qiysha", "egri", "egil"],
                     "probe": "Shu holat yillar davomida takrorlansa, umurtqa ustuni shakli qanday o‘zgaradi? Bu buzilish qanday ataladi?"},
                ],
                "wrong": [(["farqi yoq", "farq yoq", "bir xil", "ahamiyatsiz", "muhim emas"],
                           "Og‘irlik bir xil, lekin u qayerga tushadi? Bir yelkadagi yuk tanani qarama-qarshi tomonga egilishga majbur qiladi. "
                           "Shu holat kuniga bir necha marta, yillar davomida takrorlansa, o‘sib turgan umurtqa bilan nima bo‘ladi?")],
                "hint": "Ishora: bir yelkangizga og‘ir narsa osib turib oynaga qarang. Muvozanatni saqlash uchun yelkangiz va tanangiz qaysi tomonga siljiydi?",
                "insight": "Assimetrik yuk bir tomondagi mushaklarni doimiy zo‘riqtiradi va umurtqani yon tomonga egadi — skolioz shunday boshlanadi. "
                           "Ryukzak yukni ikki yelkaga teng taqsimlaydi; gigiyenik me’yorga ko‘ra sumka og‘irligi o‘quvchi tana vaznining 10 % idan oshmasligi kerak.",
            },
            {
                "ask": "45 daqiqalik dars davomida o‘quvchi deyarli qimirlamay o‘tiradi. Nega bunday statik o‘tirish yurishdan ham ko‘proq charchatadi "
                       "va o‘qituvchi buni darsda qanday yumshatishi mumkin?",
                "concepts": [
                    {"name": "statik zo‘riqish — mushaklar bo‘shashmaydi", "kw": ["statik", "qimirlamay", "bir holat", "doimiy", "tarang", "tonus"],
                     "probe": "Qimirlamay o‘tirganda tanani tik ushlab turgan mushaklar dam oladimi yoki doimiy taranglikda qoladimi?"},
                    {"name": "qon aylanishining sekinlashuvi", "kw": ["qon", "tomir", "kislorod", "uyush", "sekinlash", "modda almash"],
                     "probe": "Doimiy tarang mushakda qon harakati qanday bo‘ladi? Bu hujayralarga kislorod yetkazishga qanday ta’sir qiladi?"},
                    {"name": "harakat rejimi va jismoniy tarbiya daqiqasi", "kw": ["jismoniy tarbiya", "tanaffus", "mashq", "harakat", "turib", "gimnastika", "almash"],
                     "probe": "Endi yechimni o‘ylang: dars o‘rtasida 1–2 daqiqa nima qilinsa, mushaklardagi qon aylanishi tiklanadi?"},
                ],
                "wrong": [(["otirish oson", "charchamaydi", "dam olish", "dam oladi"],
                           "Agar o‘tirish dam olish bo‘lsa, nega 5–6 soat partada o‘tirgan o‘quvchi charchaydi va oxirgi darsda diqqati tarqaladi? "
                           "Bu paytda tanani tik ushlab turuvchi mushaklar bo‘shashadimi?")],
                "hint": "Ishora: statik holatda mushaklar qisqarib-bo‘shashmaydi, ular bir xil holatni ushlab turadi. Nasos kabi ishlamayotgan mushakda qon qanday harakatlanadi?",
                "insight": "Statik zo‘riqishda mushaklar uzluksiz taranglikda bo‘ladi, ulardagi qon aylanishi sekinlashadi — kislorod yetishmaydi va charchoq tez to‘planadi. "
                           "Shuning uchun boshlang‘ich sinflarda darsning 20–25-daqiqasida jismoniy tarbiya daqiqasi o‘tkaziladi, partaning balandligi esa bo‘yga moslanadi.",
            },
            TEACH_STEP,
        ],
        "key_points": [
            "Bolalar skeletida organik moddalar ko‘p va suyaklanish tugallanmagan — qomat tashqi ta’sirga juda sezgir.",
            "Assimetrik yuk va noto‘g‘ri parta o‘lchami qomat buzilishi hamda skoliozning asosiy sabablari.",
            "Statik zo‘riqish charchoqni tezlashtiradi; harakat rejimi va jismoniy tarbiya daqiqasi — profilaktikaning asosi.",
        ],
    },

    "nerv": {
        "title": "Nerv tizimi va charchash",
        "icon": "atom",
        "section": "Nerv tizimi",
        "teaser": "Nega 6-dars 1-darsdek o‘zlashtirilmaydi?",
        "detect": ["nerv", "charcha", "ish qobiliyat", "dars jadval", "diqqat", "qozgal", "tormozlan", "refleks", "miya", "stereotip"],
        "opening": "O‘quv yukini to‘g‘ri taqsimlash — nerv tizimi fiziologiyasini bilishdan boshlanadi. Keling, buni tayyor qoidalar orqali emas, "
                   "kundalik maktab vaziyatlari orqali ochamiz.",
        "steps": [
            {
                "ask": "Nazorat ishlari odatda 2–3-darsga qo‘yiladi, jismoniy tarbiya esa ko‘pincha kun oxiriga. "
                       "O‘quvchining ish qobiliyati kun davomida qanday o‘zgaradi va jadval nega shunga moslanadi?",
                "concepts": [
                    {"name": "ishga kirishish davri", "kw": ["kirishish", "boshida", "birinchi dars", "sekin", "kirish", "tayyorgarlik"],
                     "probe": "Kunning boshida organizm darrov to‘liq quvvatda ishlaydimi? Birinchi darsda qanday davr kechadi?"},
                    {"name": "yuqori va barqaror ish qobiliyati davri", "kw": ["yuqori", "ikkinchi", "uchinchi", "ortasi", "barqaror", "eng yaxshi"],
                     "probe": "Kunning qaysi qismida o‘zlashtirish eng yaxshi bo‘ladi? Murakkab fanlar shuning uchun qayerga qo‘yiladi?"},
                    {"name": "charchash — ish qobiliyatining pasayishi", "kw": ["charcha", "pasay", "tormozlan", "diqqat tarqal", "holsiz", "oxirida"],
                     "probe": "Kun oxirida nerv hujayralari bilan nima sodir bo‘ladi va bu o‘zlashtirishda qanday ko‘rinadi?"},
                ],
                "wrong": [(["hammasi bir xil", "farq yoq", "farqi yoq", "ahamiyatsiz", "ertalab eng yomon"],
                           "Agar ish qobiliyati kun davomida o‘zgarmasa, jadval tuzishning fiziologik ma’nosi qolmasdi. "
                           "Unda nega nazorat ishi oxirgi darsga emas, kunning o‘rtasiga qo‘yiladi?")],
                "hint": "Ishora: kun boshida organizm hali «ishga kirishmagan», kun oxirida esa nerv hujayralarining resursi kamaygan. "
                        "Bu ikkisining orasida qanday davr yotadi?",
                "insight": "Ish qobiliyati uch bosqichda o‘zgaradi: ishga kirishish (1-dars), yuqori barqaror davr (2–4-darslar) va charchash. "
                           "Shuning uchun murakkab fanlar jadvalning o‘rtasiga, kun oxiriga esa yengilroq va harakatli darslar qo‘yiladi.",
            },
            {
                "ask": "Charchash — zararli holatmi yoki foydali? O‘qituvchi o‘quvchining charchaganini ko‘rib nima qilgani to‘g‘ri: "
                       "talabni kuchaytirishimi yoki boshqa yo‘l bormi?",
                "concepts": [
                    {"name": "charchash — himoya tormozlanishi", "kw": ["himoya", "signal", "ogohlantir", "tabiiy", "normal", "foydali", "saqlaydi"],
                     "probe": "Og‘riq organizmni shikastdan saqlagani kabi, charchash nerv hujayralarini nimadan saqlaydi?"},
                    {"name": "faoliyat turini almashtirish", "kw": ["almash", "ozgartir", "boshqa faoliyat", "tanaffus", "dam", "harakat", "ogin"],
                     "probe": "Charchoqni yengishning eng fiziologik yo‘li qaysi: qattiqroq talab qilishmi yoki faoliyat turini o‘zgartirishmi?"},
                    {"name": "surunkali charchash (holdan toyish) xavfi", "kw": ["surunkali", "holdan", "toyish", "asabiy", "kasallik", "ortiqcha yuk", "tolib"],
                     "probe": "Agar charchash signali e’tiborsiz qoldirilib, yuk oshaversa, bu qanday holatga aylanadi?"},
                ],
                "wrong": [(["dangasa", "yalqov", "irodasi", "tanbeh", "jazo", "qiziqmaydi"],
                           "Agar sabab faqat irodada bo‘lsa, nega charchagan o‘quvchi 5 daqiqalik tanaffusdan yoki faoliyat turi almashgandan keyin "
                           "yana ishlay boshlaydi? Tanbeh bilan nerv hujayrasining sarflangan resursi tiklanadimi?")],
                "hint": "Ishora: charchash nerv hujayralarida ish davom etaverganda ularning haddan tashqari zo‘riqishiga yo‘l qo‘ymaydi. "
                        "Bu — nuqsonmi yoki himoya mexanizmimi?",
                "insight": "Charchash — nerv hujayralarini haddan ortiq zo‘riqishdan saqlaydigan himoya tormozlanishi. Uni inkor etib ish davom etsa, "
                           "surunkali charchash (holdan toyish) rivojlanadi. Eng samarali yo‘l — faoliyat turini almashtirish va o‘z vaqtida dam berish.",
            },
            {
                "ask": "Yozgi ta’tildan keyingi birinchi hafta o‘quvchilarga qiyin kechadi: diqqat tarqaladi, ertalab turish og‘ir. "
                       "Bu davrda organizmda aynan nima «qayta quriladi»?",
                "concepts": [
                    {"name": "dinamik stereotip", "kw": ["stereotip", "konikma", "odat", "rejim", "kun tartibi", "tizim"],
                     "probe": "Har kuni bir vaqtda takrorlanadigan faoliyat nerv tizimida nimani hosil qiladi? I. P. Pavlov buni qanday atagan?"},
                    {"name": "vaqtga bog‘langan shartli reflekslar", "kw": ["shartli refleks", "vaqt", "soat", "signal", "biologik soat", "bogla"],
                     "probe": "Nega organizm ovqat vaqti yoki uyqu vaqti yaqinlashganini soatsiz ham «biladi»? Bu qanday bog‘lanishlar hisobiga?"},
                    {"name": "moslashish vaqt talab qiladi", "kw": ["moslash", "adaptatsiya", "vaqt kerak", "asta", "bir necha kun", "tiklan"],
                     "probe": "Buzilgan stereotip bir kunda tiklanadimi? O‘quv yilining birinchi haftalari shuning uchun qanday davr hisoblanadi?"},
                ],
                "wrong": [(["yalqovlik", "dangasa", "unutib qoy", "unutadi", "bilimni unut"],
                           "Bilim unutilishi mumkin, lekin nega bu davrda uyquga ketish ham qiyinlashadi, ishtaha ham o‘zgaradi? "
                           "Demak, ta’tilda faqat bilimmi yoki butun kun tartibimi buzilgan?")],
                "hint": "Ishora: organizm takrorlanuvchi tartibga moslashadi va uni «oldindan biladi». Bu mustahkam bog‘lanishlar tizimining nomi bor.",
                "insight": "Muntazam kun tartibi dinamik stereotip — vaqtga bog‘langan shartli reflekslar tizimini hosil qiladi. Ta’tilda u buziladi, "
                           "o‘quv yili boshida qayta tiklanadi; shuning uchun dastlabki 1–2 hafta moslashish davri hisoblanadi va yuk asta oshiriladi.",
            },
            TEACH_STEP,
        ],
        "key_points": [
            "Ish qobiliyati kun va hafta davomida bosqichli o‘zgaradi; dars jadvali shu egri chiziqqa moslanadi.",
            "Charchash — himoya tormozlanishi; unga qarshi kurashilmaydi, u bilan hisoblashiladi.",
            "Muntazam kun tartibi dinamik stereotip hosil qilib, o‘quv yukini yengillashtiradi.",
        ],
    },

    "uyqu": {
        "title": "Uyqu gigiyenasi",
        "icon": "bell",
        "section": "Gigiyena",
        "teaser": "Ekran nega uyquni kechiktiradi?",
        "detect": ["uyqu", "uxla", "melatonin", "ekran", "telefon", "tungi", "kechasi", "uyqusiz"],
        "opening": "Uyqu — o‘sayotgan organizm uchun eng kam qadrlanadigan, ammo eng zarur davr. Keling, uning fiziologik ma’nosini "
                   "savollar orqali ochib olaylik.",
        "steps": [
            {
                "ask": "7 yoshli bolaga sutkasiga 10–11 soat, kattaga esa 7–8 soat uyqu yetarli hisoblanadi. "
                       "Nega o‘sayotgan organizmga ko‘proq uyqu kerak — uyqu vaqtida nima sodir bo‘ladi?",
                "concepts": [
                    {"name": "o‘sish gormonining ajralishi", "kw": ["osish gormoni", "gormon", "osadi", "osish", "boy"],
                     "probe": "Bolaning bo‘yi ko‘proq qachon o‘sadi — kunduzimi yoki kechasi? Buni qaysi modda boshqaradi?"},
                    {"name": "nerv tizimining tiklanishi", "kw": ["nerv", "miya", "tiklan", "dam", "hujayra", "resurs"],
                     "probe": "Kun davomida sarflangan nerv hujayralari resursi qaysi davrda tiklanadi?"},
                    {"name": "xotira va axborotning mustahkamlanishi", "kw": ["xotira", "esda", "axborot", "malumot", "organgan", "mustahkamlan", "saralan"],
                     "probe": "Kunduzi olingan ma’lumot bilan uyqu paytida nima bo‘ladi? Nega uyqusiz tunda o‘qilgan dars yomon esda qoladi?"},
                ],
                "wrong": [(["vaqtni yoqot", "behuda", "bekorga", "faoliyatsiz", "miya ishlamaydi", "foydasiz"],
                           "Agar uyqu shunchaki «harakatsizlik» bo‘lsa, nega uyqusiz qolgan odam yotib dam olsa ham o‘zini tiklay olmaydi? "
                           "Uyqu paytida miya faolligi nolga tushadimi?")],
                "hint": "Ishora: uyqu — passiv emas, faol davr. Unda organizmning o‘sishini boshqaradigan modda qonga chiqadi. Bu modda qanday ataladi?",
                "insight": "Uyqu — faol tiklanish davri: o‘sish gormonining asosiy qismi chuqur tungi uyquda ajraladi, nerv hujayralari resursi tiklanadi, "
                           "kunduzi olingan axborot saralanib xotiraga mustahkamlanadi. Shuning uchun o‘sish davridagi organizmga uyqu ko‘proq kerak.",
            },
            {
                "ask": "Yotishdan oldin telefon yoki kompyuter ekraniga uzoq qarash uyquga ta’sir qiladi. "
                       "Bu shunchaki mashg‘ulot qiziq bo‘lgani uchunmi yoki fiziologik sabab ham bormi?",
                "concepts": [
                    {"name": "yorug‘lik melatonin ajralishini susaytiradi", "kw": ["melatonin", "yorug", "nur", "gormon", "qorong"],
                     "probe": "Miya qorong‘ilikni qanday signal deb qabul qiladi va shunda qaysi gormon ajraladi?"},
                    {"name": "nerv tizimining qo‘zg‘alishi", "kw": ["qozgal", "hayajon", "asab", "nerv", "faollash", "tinchlan"],
                     "probe": "Ekrandagi mazmun — o‘yin, video, yozishmalar — nerv tizimini tinchlantiradimi yoki qo‘zg‘atadimi?"},
                    {"name": "uxlab qolish vaqtining cho‘zilishi", "kw": ["kech", "chozil", "uxlay olmay", "kechik", "sifati pasay", "qiyin"],
                     "probe": "Natijada uyquga ketish vaqti va uyquning umumiy davomiyligi bilan nima bo‘ladi?"},
                ],
                "wrong": [(["odatlanadi", "tasir qilmaydi", "farqi yoq", "aloqasi yoq", "muhim emas"],
                           "Kuzatuvlarda yotishdan oldin yorqin ekranga qaragan guruhda uxlab qolish vaqti o‘rtacha 30–60 daqiqaga cho‘zilgan. "
                           "Ekrandan chiqadigan ko‘k yorug‘likni miya sutkaning qaysi vaqti signali deb qabul qiladi?")],
                "hint": "Ishora: miya uchun asosiy vaqt signali — yorug‘lik. Yorqin ekran shu signalni qanday «aldaydi» va qaysi gormonni kechiktiradi?",
                "insight": "Ko‘k spektrli yorqin yorug‘lik miyaga «hali kunduz» signalini berib, melatonin — uyqu gormoni ajralishini kechiktiradi. "
                           "Bunga ekran mazmunidan kelib chiqadigan nerv qo‘zg‘alishi qo‘shiladi: uxlab qolish cho‘ziladi, uyqu sayozlashadi. "
                           "Gigiyenik tavsiya — yotishdan 1 soat oldin ekranni qo‘yish.",
            },
            {
                "ask": "Uyqusi surunkali yetishmaydigan o‘quvchini o‘qituvchi darsda qanday belgilarga qarab taniy oladi? "
                       "Va bu belgilar ko‘pincha qanday noto‘g‘ri baholanadi?",
                "concepts": [
                    {"name": "diqqatning beqarorligi", "kw": ["diqqat", "etibor", "chalgi", "tarqal", "toplay olmay", "esnay"],
                     "probe": "Uyqu yetishmaganda nerv tizimining qaysi funksiyasi birinchi bo‘lib zaiflashadi?"},
                    {"name": "xotira va o‘zlashtirishning pasayishi", "kw": ["xotira", "ozlashtir", "eslab qol", "baho", "pasay", "sekin"],
                     "probe": "Darsda berilgan yangi material bunday o‘quvchida qanday o‘zlashtiriladi?"},
                    {"name": "asabiylashish va kayfiyat o‘zgarishi", "kw": ["asabiy", "jizzaki", "kayfiyat", "yigla", "tajang", "hissiy", "keskin"],
                     "probe": "Hissiy holat-chi? Uyqusi yetmagan bola arzimagan tanbehga qanday javob qaytaradi?"},
                ],
                "wrong": [(["dangasa", "yalqov", "qiziqmaydi", "tarbiyasiz", "intizomsiz", "beparvo"],
                           "Shunday xulosadan oldin bitta savol bering: bu o‘quvchi kecha necha soat uxladi? "
                           "Agar xuddi shu belgilar 2–3 kun yetarli uyqudan keyin yo‘qolsa, sabab tarbiyadami yoki kun tartibidami?")],
                "hint": "Ishora: uyqu yetishmasa, avvalo nerv tizimining eng nozik funksiyalari — diqqat, xotira va hissiyotni boshqarish zarar ko‘radi. "
                        "Bu darsda qanday ko‘rinadi?",
                "insight": "Surunkali uyqu yetishmovchiligi diqqatning beqarorligi, xotira va o‘zlashtirishning pasayishi, asabiylashish orqali namoyon bo‘ladi. "
                           "Bu belgilar ko‘pincha «dangasalik» yoki «intizomsizlik» deb baholanadi, aslida esa avvalo kun tartibini tekshirish kerak.",
            },
            TEACH_STEP,
        ],
        "key_points": [
            "Uyqu — faol tiklanish davri: o‘sish gormoni ajraladi, nerv tizimi tiklanadi, xotira mustahkamlanadi.",
            "Yotishdan oldingi yorqin ekran melatonin ajralishini kechiktirib, uxlab qolishni cho‘zadi.",
            "Uyqu yetishmovchiligi diqqat, o‘zlashtirish va xulq-atvorda ko‘rinadi — uni tarbiya nuqsoni bilan adashtirmaslik kerak.",
        ],
    },

    "korish": {
        "title": "Ko‘rish gigiyenasi",
        "icon": "eye",
        "section": "Sezgi organlari",
        "teaser": "Miyopiya nega maktab yillarida ortadi?",
        "detect": ["korish", "koz", "miyopiya", "yaqindan kor", "kozoynak", "akkomodatsiya", "gavhar", "yoritilgan", "chiroq"],
        "opening": "«Maktab miyopiyasi» atamasi bejiz paydo bo‘lmagan. Ko‘rish gigiyenasi qoidalari qayerdan kelib chiqqanini "
                   "birga mulohaza qilib topamiz.",
        "steps": [
            {
                "ask": "1-sinfda ko‘zoynak taqadigan o‘quvchilar deyarli yo‘q, 9-sinfda esa ancha ko‘p. "
                       "Maktab yillarida ko‘z bilan nima sodir bo‘ladi va nima bunga sabab bo‘ladi?",
                "concepts": [
                    {"name": "yaqin masofada uzoq ishlash", "kw": ["yaqin", "kitob", "daftar", "ekran", "telefon", "yozish", "oqish"],
                     "probe": "O‘quvchining ko‘zi kuniga necha soat davomida qanday masofadagi obyekt bilan ishlaydi?"},
                    {"name": "akkomodatsiya mushagining zo‘riqishi", "kw": ["akkomodatsiya", "mushak", "gavhar", "zoriq", "tarang", "boshash"],
                     "probe": "Yaqinga qaraganda ko‘z gavharining qavariqligini o‘zgartiruvchi mushak qanday holatda bo‘ladi?"},
                    {"name": "ko‘z o‘qining uzayishi — miyopiya", "kw": ["miyopiya", "yaqindan kor", "uzay", "koz shakli", "ozgar", "uzoqni yomon"],
                     "probe": "Ko‘p yillik zo‘riqish natijasida ko‘z olmasining shakli bilan nima bo‘ladi va tasvir qayerga tushib qoladi?"},
                ],
                "wrong": [(["irsiy", "genetik", "tugma", "ota-ona"],
                           "Irsiy moyillik bor, lekin irsiyat bir odamda 8 yil ichida o‘zgarmaydi. Shu 8 yilda o‘quvchining ko‘zi ko‘proq nima bilan shug‘ullanadi — "
                           "uzoqni kuzatish bilanmi yoki yaqin masofadagi matn bilanmi?")],
                "hint": "Ishora: uzoqqa qaraganda gavharni boshqaruvchi mushak bo‘shashadi, yaqinga qaraganda esa… ? Bu holat kuniga bir necha soat davom etsa nima bo‘ladi?",
                "insight": "Yaqin masofadagi ish akkomodatsiya mushagini doimiy taranglikda ushlaydi. Uzoq yillik zo‘riqish ko‘z o‘qining uzayishiga va "
                           "yaqindan ko‘rish — miyopiya rivojlanishiga olib keladi; shuning uchun u «maktab miyopiyasi» deb ham ataladi.",
            },
            {
                "ask": "Yozuv stolining chap tomonida deraza yoki chiroq bo‘lishi tavsiya etiladi (chapaqaylar uchun — o‘ng tomonda). "
                       "Bu qoida qayerdan kelib chiqqan va yoritilganlik yetarli bo‘lmasa nima bo‘ladi?",
                "concepts": [
                    {"name": "yozayotgan qo‘l soya tashlamasligi", "kw": ["soya", "qol", "yozayotgan", "tushmas", "toy", "qarama-qarshi"],
                     "probe": "O‘ng qo‘lda yozayotganda yorug‘lik o‘ng tomondan tushsa, daftarning yozilayotgan joyiga nima tushadi?"},
                    {"name": "yetarli yoritilganlik", "kw": ["yorit", "yorug", "chiroq", "lyuks", "deraza", "xira", "kam"],
                     "probe": "Yorug‘lik miqdori-chi? Xira yorug‘likda matnni ko‘rish uchun ko‘z nima qilishga majbur bo‘ladi?"},
                    {"name": "ko‘zning ortiqcha zo‘riqishi va engashish", "kw": ["zoriq", "charcha", "yaqinlash", "engash", "egil", "qomat"],
                     "probe": "Ko‘rish qiyinlashganda o‘quvchi daftarga qanday yaqinlashadi va bu yana qaysi tizimga zarar beradi?"},
                ],
                "wrong": [(["odat", "anana", "ozi shunday", "farqi yoq", "muhim emas", "ahamiyatsiz"],
                           "Sinab ko‘ring: chiroqni o‘ng tomonga qo‘yib o‘ng qo‘lda yozing. Daftardagi yozuv joyiga nima tushadi "
                           "va odam buni qoplash uchun qanday harakat qiladi?")],
                "hint": "Ishora: qo‘l yorug‘lik manbai bilan daftar orasida turib qolsa, qog‘ozda nima hosil bo‘ladi?",
                "insight": "Yorug‘lik qarama-qarshi tomondan tushsa, yozayotgan qo‘l daftarga soya tashlamaydi. Yoritilganlik me’yordan (ish joyida 300–500 lk) "
                           "past bo‘lsa, o‘quvchi daftarga engashadi: ko‘z zo‘riqadi, ayni paytda qomat ham buziladi.",
            },
            {
                "ask": "Ko‘z charchamasligi uchun uzluksiz o‘qish yoki ekran oldida ishlashni bo‘lib turish tavsiya etiladi. "
                       "Nega aynan «uzoqqa qarash» maslahat beriladi va ekran oldida ko‘z nega achishadi?",
                "concepts": [
                    {"name": "akkomodatsiya mushagining bo‘shashishi", "kw": ["boshash", "dam", "mushak", "yozil", "tinch", "uzoqqa"],
                     "probe": "Uzoqdagi narsaga qaraganda akkomodatsiya mushagi qanday holatga keladi?"},
                    {"name": "muntazam tanaffus", "kw": ["tanaffus", "har yigirma", "vaqti-vaqti", "bolib", "dam ol", "yigirma daqiqa"],
                     "probe": "Bu dam berish qanchalik tez-tez kerak? Uzluksiz ishlashning qanday cheklovi bor?"},
                    {"name": "pirpiratish va ko‘zning namlanishi", "kw": ["pirpirat", "namlan", "quruq", "achish", "koz yosh", "yum"],
                     "probe": "Ekranga tikilib qaraganda pirpiratish soni ortadimi yoki kamayadi? Bu ko‘z yuzasiga qanday ta’sir qiladi?"},
                ],
                "wrong": [(["kozoynak yetarli", "dam kerak emas", "charchamaydi", "ozi otadi"],
                           "Ko‘zoynak nurning sinishini tuzatadi, lekin mushak zo‘riqishini bartaraf qiladimi? "
                           "Ekran oldida 3 soat uzluksiz o‘tirgan odamning ko‘zi nega achishadi va og‘riydi?")],
                "hint": "Ishora: mushak dam olishi uchun u bo‘shashishi kerak. Ko‘z mushagi qaysi masofaga qaraganda bo‘shashadi?",
                "insight": "Har 20 daqiqada 20 soniya davomida uzoqqa (kamida 6 m) qarash akkomodatsiya mushagini bo‘shashtiradi. "
                           "Ekranga tikilganda pirpiratish soni bir necha barobar kamayadi, ko‘z yuzasi quruqshaydi — shuning uchun ongli pirpiratish va "
                           "harakatli tanaffus zarur.",
            },
            TEACH_STEP,
        ],
        "key_points": [
            "Yaqin masofadagi uzoq ish akkomodatsiya mushagini zo‘riqtiradi va «maktab miyopiyasi»ni rivojlantiradi.",
            "To‘g‘ri yoritilganlik va yorug‘likning qarama-qarshi tomondan tushishi ko‘z zo‘riqishini kamaytiradi.",
            "Har 20 daqiqada uzoqqa qarash va tanaffus — ko‘rish gigiyenasining eng oddiy, isbotlangan qoidasi.",
        ],
    },

    "oziqlanish": {
        "title": "Ovqatlanish va sinf havosi gigiyenasi",
        "icon": "sprout",
        "section": "Gigiyena",
        "teaser": "Nonushtasiz dars nega og‘ir kechadi?",
        "detect": ["ovqatlan", "oziqlan", "nonushta", "taom", "vitamin", "kaloriya", "shamollat", "nafas", "oqsil", "havo"],
        "opening": "O‘quv kunining samarasi ko‘pincha darsdan tashqaridagi ikki narsaga bog‘liq: o‘quvchi nima yegani va qanday havodan nafas olgani. "
                   "Shuni birga tahlil qilamiz.",
        "steps": [
            {
                "ask": "Nonushta qilmay kelgan o‘quvchi ko‘pincha 2–3-darsda diqqatini yo‘qotadi, boshi og‘riydi, qo‘li titraydi. "
                       "Buning fiziologik sababi nimada?",
                "concepts": [
                    {"name": "miyaning asosiy energiya manbai — glyukoza", "kw": ["glyukoza", "qand", "energiya", "miya", "oziq"],
                     "probe": "Miya tana vaznining 2 % ini tashkil qilib, energiyaning 20 % ini sarflaydi. U bu energiyani qaysi moddadan oladi?"},
                    {"name": "qondagi qand miqdorining pasayishi", "kw": ["qon", "pasay", "kamay", "och", "zaxira", "tugaydi"],
                     "probe": "Uzoq ochlikda qon tarkibidagi qaysi ko‘rsatkich pasayadi va miya buni qanday sezadi?"},
                    {"name": "ish qobiliyati va diqqatning pasayishi", "kw": ["diqqat", "ish qobiliyat", "charcha", "ozlashtir", "holsiz", "bosh ogri"],
                     "probe": "Bu holat darsda qanday ko‘rinadi — o‘zlashtirish va diqqat bilan nima bo‘ladi?"},
                ],
                "wrong": [(["odatlangan", "ozish", "foydali", "zarari yoq", "kerak emas", "tushlik yetarli"],
                           "Ochlikka «odatlanish» mumkin, lekin miya energiyani zaxiraga to‘play oladimi? "
                           "Uzluksiz ishlab turgan miya uchun qondagi glyukoza kamaysa, u darhol nimani boshdan kechiradi?")],
                "hint": "Ishora: miya kislorod va bir turdagi «yoqilg‘i»ga juda bog‘liq va uni jigar zaxirasidan uzoq vaqt ta’minlab bo‘lmaydi. "
                        "Bu yoqilg‘i qanday modda?",
                "insight": "Miya energiyani asosan qondagi glyukozadan oladi va uni o‘zida zaxiralay olmaydi. Uzoq ochlikda qondagi qand miqdori pasayadi — "
                           "diqqat, xotira va ish qobiliyati keskin tushadi. Shuning uchun issiq nonushta o‘quv kunining gigiyenik talabi hisoblanadi.",
            },
            {
                "ask": "O‘sayotgan organizm uchun ovqat tarkibida qaysi moddalarning yetishmasligi eng xavfli? "
                       "Va nega ovqatlanish rejimi — kuniga necha marta va qaysi vaqtda yeyish — ham muhim?",
                "concepts": [
                    {"name": "oqsil — o‘sish uchun qurilish materiali", "kw": ["oqsil", "protein", "qurilish", "hujayra", "osish", "togima"],
                     "probe": "Bola nafaqat energiya sarflaydi, balki yangi hujayralar quradi. Hujayra asosan qaysi moddadan tuziladi?"},
                    {"name": "vitamin va minerallar (kalsiy, temir, D)", "kw": ["vitamin", "kalsiy", "temir", "mineral", "yod", "d vitamin"],
                     "probe": "Suyaklanish va qon hosil bo‘lishi uchun qanday mineral moddalar hamda vitaminlar zarur?"},
                    {"name": "muntazam ovqatlanish rejimi", "kw": ["rejim", "mahal", "bir vaqtda", "muntazam", "vaqtida", "tartib"],
                     "probe": "Har kuni bir vaqtda ovqatlanish hazm bezlariga qanday ta’sir qiladi? Bu qaysi refleks bilan bog‘liq?"},
                ],
                "wrong": [(["kaloriya yetarli", "qorni toy", "shirinlik", "tez taom", "yeyishning farqi yoq"],
                           "Kaloriya yetarli bo‘lishi mumkin, lekin kaloriya va qurilish materiali bir xil narsami? "
                           "Shirinlik hamda tez taomdan olingan energiya bilan yangi hujayra va suyak to‘qimasi quriladimi?")],
                "hint": "Ishora: o‘sish — bu yangi to‘qima qurilishi. Qurilish uchun esa faqat «yoqilg‘i» emas, «g‘isht» ham kerak. Bu «g‘isht» qaysi modda?",
                "insight": "O‘sayotgan organizmga oqsil qurilish materiali sifatida zarur; kalsiy va D vitamini suyaklanish uchun, temir esa gemoglobin uchun kerak. "
                           "Muntazam, bir vaqtda ovqatlanish esa hazm bezlarining shartli refleks bo‘yicha oldindan ishga tushishini ta’minlaydi.",
            },
            {
                "ask": "Tanaffusda shamollatilmagan sinfda dars oxiriga borib o‘quvchilar esnaydi, boshi og‘riydi, diqqati tarqaladi. "
                       "Xonadagi havo tarkibida nima o‘zgardi va bu organizmga qanday ta’sir qiladi?",
                "concepts": [
                    {"name": "CO₂ miqdorining ortishi", "kw": ["co2", "uglekislo", "karbonat", "ortadi", "toplan", "meyordan"],
                     "probe": "30 ta o‘quvchi bir soat nafas oladi. Xona havosida qaysi gaz miqdori sezilarli ortadi?"},
                    {"name": "kislorodning kamayishi", "kw": ["kislorod", "yetishmay", "kamay", "toza havo", "nafas"],
                     "probe": "Ayni paytda qaysi gaz kamayadi va bu miya hujayralari uchun nimani anglatadi?"},
                    {"name": "shamollatish — asosiy profilaktika", "kw": ["shamollat", "deraza", "havo almash", "ochib", "tanaffus", "havoni yangila"],
                     "probe": "Endi yechimni ayting: har tanaffusda qanday oddiy gigiyenik tadbir bajarilishi kerak?"},
                ],
                "wrong": [(["issiq", "harorat", "zerik", "charchagani uchun", "dars qiziq emas"],
                           "Harorat va zerikish ham ta’sir qiladi, lekin nega deraza ochilgach, xuddi o‘sha darsda holat bir necha daqiqada yaxshilanadi? "
                           "Deraza ochilganda xonaga nima kiradi va nima chiqadi?")],
                "hint": "Ishora: yopiq xonadagi har bir odam havodan bir gazni oladi va boshqasini chiqaradi. Bir soatda 30 kishi buni qancha marta takrorlaydi?",
                "insight": "Yopiq sinfda CO₂ miqdori gigiyenik me’yordan (0,1 %) oshadi, kislorod kamayadi, havo namligi va harorati ortadi — natijada bosh og‘riydi, "
                           "diqqat pasayadi. Gigiyenik talab: har tanaffusda ko‘ndalang shamollatish, iliq havoda esa darsni ochiq deraza tuynugida o‘tkazish.",
            },
            TEACH_STEP,
        ],
        "key_points": [
            "Miya energiyani glyukozadan oladi va uni zaxiralay olmaydi — nonushta ish qobiliyatining sharti.",
            "O‘sayotgan organizmga oqsil, kalsiy, temir va vitaminlar zarur; muntazam rejim hazm bezlarini shartli refleks bo‘yicha ishlatadi.",
            "Sinfni muntazam shamollatish CO₂ to‘planishining oldini oladi va darsdagi ish qobiliyatini saqlaydi.",
        ],
    },

    "balogat": {
        "title": "Balog‘at yoshi fiziologiyasi",
        "icon": "dna",
        "section": "O‘sish va rivojlanish",
        "teaser": "O‘smirdagi keskin o‘zgarishlar sababi nima?",
        "detect": ["balogat", "osmir", "usmir", "gormon", "jinsiy", "gipofiz", "akne", "sakrash", "otish davri"],
        "opening": "Balog‘at davri — o‘qituvchi uchun eng nozik yosh bosqichi. Uning xulq-atvordagi ko‘rinishlari ortida aniq fiziologik sabablar yotadi; "
                   "shularni birga ochamiz.",
        "steps": [
            {
                "ask": "11–15 yoshdagi o‘smirning qo‘l-oyog‘i tanasiga nisbatan tez o‘sadi, harakatlari beso‘naqay bo‘lib qoladi, tez charchaydi. "
                       "Nega o‘sish bir tekis emas va nega bu aynan shu yoshda boshlanadi?",
                "concepts": [
                    {"name": "o‘sish sakrashi va a’zolarning notekis o‘sishi", "kw": ["sakrash", "tez osadi", "notekis", "bir tekis emas", "jadal", "nomutanosib"],
                     "probe": "Bu davrda tananing hamma qismi bir xil tezlikda o‘sadimi? Avval nima uzayadi?"},
                    {"name": "gormonal boshqaruv (gipofiz, jinsiy bezlar)", "kw": ["gormon", "gipofiz", "bez", "jinsiy bez", "endokrin", "qalqonsimon"],
                     "probe": "Aynan shu yoshda organizmning qaysi tizimi keskin faollashadi va o‘sishni nima boshqaradi?"},
                    {"name": "yurak-qon tomir va mushaklarning orqada qolishi", "kw": ["yurak", "tomir", "mushak", "ulgurmay", "orqada", "charcha", "bosim"],
                     "probe": "Bo‘y tez uzayganda yurak va qon tomirlar shu sur’atga ulguradimi? Shundan qanday belgilar kelib chiqadi?"},
                ],
                "wrong": [(["ovqat", "sport", "notogri ovqatlan", "genetika", "irsiy"],
                           "Ovqatlanish va irsiyat o‘sish darajasiga ta’sir qiladi, lekin nega bu sakrash deyarli barcha o‘smirlarda ma’lum yoshda boshlanadi? "
                           "Shu davrda organizmda qaysi boshqaruv tizimi faollashadi?")],
                "hint": "Ishora: bu davrda qonga bezlar ishlab chiqaradigan boshqaruvchi moddalar ko‘p tushadi va aynan ular naysimon suyaklar o‘sishini tezlashtiradi.",
                "insight": "Balog‘at davrida gipofiz va jinsiy bezlar faollashadi; gormonlar ta’sirida naysimon suyaklar jadal o‘sadi. Yurak-qon tomir tizimi va "
                           "mushaklar bu sur’atdan orqada qoladi — shundan beso‘naqaylik, tez charchash va qon bosimining beqarorligi kelib chiqadi. "
                           "Shuning uchun bu yoshda jismoniy yuk ehtiyotkorlik bilan me’yorlanadi.",
            },
            {
                "ask": "O‘smirda kayfiyat tez o‘zgaradi, arzimagan tanbehga keskin javob qaytaradi, gohida esa bir necha kun loqayd bo‘ladi. "
                       "Bu faqat tarbiya masalasimi yoki fiziologik asosi ham bormi?",
                "concepts": [
                    {"name": "gormonal fonning ta’siri", "kw": ["gormon", "fon", "jinsiy bez", "endokrin", "qon", "ozgar"],
                     "probe": "Bu yoshda qonda nima keskin o‘zgaradi va u nerv tizimiga ta’sir qiladimi?"},
                    {"name": "qo‘zg‘alishning tormozlanishdan ustunligi", "kw": ["qozgal", "tormozlan", "ustun", "muvozanat", "nerv", "postloq"],
                     "probe": "Bosh miya po‘stlog‘ida qo‘zg‘alish va tormozlanish jarayonlari bu davrda muvozanatdami? Qaysi biri kuchliroq?"},
                    {"name": "o‘z-o‘zini boshqarish endi shakllanayotgani", "kw": ["boshqar", "shakllan", "nazorat", "iroda", "organ", "vaqtinchalik"],
                     "probe": "O‘z hissiyotini boshqarish ko‘nikmasi tug‘ma beriladimi yoki shakllanadimi? Bu jarayon qachon yakunlanadi?"},
                ],
                "wrong": [(["tarbiyasizlik", "qasddan", "atayin", "hurmatsiz", "jazo", "erkalik"],
                           "Agar bu faqat qasddan qilingan xatti-harakat bo‘lsa, nega u 17–18 yoshga borib ko‘pincha o‘z-o‘zidan yumshaydi? "
                           "Shu davrda tarbiya o‘zgaradimi yoki organizmda nimadir barqarorlashadimi?")],
                "hint": "Ishora: nerv tizimida ikki asosiy jarayon bor — qo‘zg‘alish va tormozlanish. Balog‘at davrida ularning nisbati qanday buziladi?",
                "insight": "Balog‘at davrida gormonal fon o‘zgaradi va nerv tizimida qo‘zg‘alish tormozlanishdan ustun turadi — shundan tez asabiylashish, "
                           "hissiy beqarorlik va charchoqning tez almashinuvi. Bu qonuniy, o‘tkinchi holat; o‘qituvchidan keskinlikni kuchaytirmaslik va "
                           "hurmatga asoslangan muloqot talab etiladi.",
            },
            {
                "ask": "Aynan shu yoshda terining yog‘lanishi ortadi, toshmalar paydo bo‘ladi, terlash kuchayadi va o‘smir bundan uyaladi. "
                       "O‘qituvchi shaxsiy gigiyena mavzusini sinfda qanday yoritsa, bu masala uyat emas, bilim sifatida qabul qilinadi?",
                "concepts": [
                    {"name": "ter va yog‘ bezlarining faollashuvi", "kw": ["bez", "ter bez", "yog bez", "faollash", "teri", "sekretsiya"],
                     "probe": "Gormonlar ta’sirida terining qaysi bezlari faollashadi va bu qanday tashqi belgilar beradi?"},
                    {"name": "muntazam shaxsiy gigiyena", "kw": ["gigiyena", "yuvin", "toza", "dush", "almash", "parvarish", "kiyim"],
                     "probe": "Bu o‘zgarishlarga javoban kundalik tartibga qanday amaliy qoidalar qo‘shilishi kerak?"},
                    {"name": "holatning tabiiyligini tushuntirish", "kw": ["tabiiy", "normal", "uyalmas", "hamma", "vaqtinchalik", "yoshga oid", "ilmiy"],
                     "probe": "Mavzuni qanday ohangda bersangiz, o‘quvchi o‘zini «nuqsonli» deb his qilmaydi?"},
                ],
                "wrong": [(["gapirmaslik", "aytmaslik", "uyat", "keraksiz", "ozi bilib oladi", "oila aytadi"],
                           "Agar bu haqda maktabda gapirilmasa, o‘smir ma’lumotni qayerdan oladi va u ishonchli bo‘ladimi? "
                           "Bilim bo‘shlig‘i odatda nima bilan to‘ladi?")],
                "hint": "Ishora: bu o‘zgarishlar sababi — ichki sekretsiya bezlari faolligi. Sabab tushunarli bo‘lsa, hodisa o‘smir uchun qo‘rqinchli bo‘lib qoladimi?",
                "insight": "Gormonlar ta’sirida ter va yog‘ bezlari faollashadi — bu tabiiy yoshga oid o‘zgarish. Mavzu shaxsga emas, yosh fiziologiyasiga qaratilib, "
                           "xotirjam ilmiy tilda tushuntirilsa, o‘quvchida uyalish emas, o‘z salomatligi uchun mas’uliyat shakllanadi.",
            },
            TEACH_STEP,
        ],
        "key_points": [
            "Balog‘at davrida gormonal faollik o‘sish sakrashini keltirib chiqaradi; a’zolar notekis o‘sadi va yurak yukka ulgurmaydi.",
            "Nerv tizimida qo‘zg‘alish tormozlanishdan ustun bo‘ladi — hissiy beqarorlikning fiziologik asosi shu.",
            "Shaxsiy gigiyena va kun tartibi bu davrda salomatlikni saqlashning asosiy vositasi; mavzu xotirjam, ilmiy tilda yoritiladi.",
        ],
    },
}

# Mavzu aniqlanmasa — istalgan savol uchun umumiy sokratik savollar zanjiri.
GENERIC_STEPS = [
    "Qiziq savol. Avval aniqlashtirib olaylik: «{theme}» deganda aynan nimani nazarda tutyapsiz? O‘z so‘zlaringiz bilan qisqa ta’riflab bering.",
    "Tushunarli. Bu fikringiz nimaga asoslanadi — darslikkami, o‘quvchilarni kuzatishgami yoki shaxsiy tajribagami? Uni qanday tekshirib ko‘rish mumkin?",
    "Keling, teskarisini tasavvur qilaylik: agar bu fikr noto‘g‘ri bo‘lsa, o‘quvchilarda yoki o‘lchov natijalarida nimani kuzatgan bo‘lardik?",
    "Bu holatning boshqa sababi ham bo‘lishi mumkinmi? Kamida bitta muqobil tushuntirishni ayting va ularni qanday farqlash mumkinligini o‘ylang.",
    "Endi o‘qituvchi sifatida: bu savolni o‘quvchilarga qanday bersangiz, ular javobni o‘zlari izlashga kirishadi? Darsni qaysi «nega?» bilan boshlardingiz?",
]

CONCLUDE_ASK = ("Suhbatimiz yakuniga yetdi. Endi eng muhim qadam: 2–3 gap bilan o‘z xulosangizni yozing — "
                "bugun nimani tushundingiz va qaysi fikringiz o‘zgardi?")
