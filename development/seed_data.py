"""
«3D simulyatsiyalar» va «Tajriba uchastkasi resurslari» namunaviy kontenti.

Migratsiya faqat yo'q yozuvlarni (slug bo'yicha) yaratadi — admin keyin tahrirlagan
yoki o'chirgan namunalar qayta yozilmaydi. Namunalarni admin istalgancha o'zgartiradi.
"""

# `visual` — static/ ichidagi 3D tasvir, `section` — fan slugi (bo'lmasa fan bog'lanmaydi).
SIMULATIONS = [
    {
        "slug": "3d-hayvon-hujayrasi",
        "title": "Hayvon hujayrasining 3D modeli",
        "section": "hujayra-biologiyasi",
        "visual": "img/sim3d/hayvon-hujayrasi.svg",
        "alt": "Choragi kesib olingan shar shaklidagi hayvon hujayrasi. Markazda yadro va yadrocha, atrofida "
               "mitoxondriyalar, endoplazmatik to'r, Golji apparati, ribosomalar va sitoplazma ko'rinadi.",
        "summary": "Hujayraning bir bo'lagi kesib olingan: membrana ichidagi organoidlar va ularning "
                   "o'zaro joylashuvi uch o'lchamda ko'rinadi.",
        "body": "Model hayvon hujayrasini shar ko'rinishida tasvirlaydi. Hujayraning choragi kesib olingani uchun "
                "ichki tuzilma — yadro, sitoplazma va organoidlar bir-biriga nisbatan qanday joylashgani "
                "ko'rinadi.\n\n"
                "Darslikdagi tekis rasmdan farqli ravishda, 3D kesim organoidlar hujayra hajmining turli "
                "chuqurligida joylashganini va yadro hujayraning katta qismini egallashini ko'rsatadi.",
        "parts": "Hujayra membranasi — hujayrani tashqi muhitdan ajratadi, moddalar almashinuvini boshqaradi\n"
                 "Yadro — irsiy axborotni (DNK) saqlaydi va hujayra faoliyatini boshqaradi\n"
                 "Yadrocha — ribosoma bo'laklarini hosil qiladi\n"
                 "Mitoxondriya — hujayraning «energiya stansiyasi», ATF sintezlanadi\n"
                 "Endoplazmatik to'r — oqsil va lipidlarni sintezlaydi hamda tashiydi\n"
                 "Golji apparati — moddalarni jamlaydi, qadoqlaydi va hujayradan chiqaradi\n"
                 "Ribosomalar — oqsil sintezi bo'ladigan mayda tanachalar",
        "task": "Modeldagi organoidlarni nomlang va har birining vazifasini bir gap bilan yozing.\n"
                "Nima uchun yadro atrofida endoplazmatik to'r zich joylashgan? Farazingizni asoslang.\n"
                "Bu modelda o'simlik hujayrasiga xos qaysi tuzilmalar yo'q?\n"
                "Modeldan 7-sinf darsida qanday foydalanasiz? 2 ta yo'naltiruvchi savol tuzing.",
    },
    {
        "slug": "3d-dnk-qosh-spirali",
        "title": "DNK qo'sh spirali",
        "section": "genetika",
        "visual": "img/sim3d/dnk-spiral.svg",
        "alt": "Buralgan narvonga o'xshash DNK qo'sh spirali. Ikki qand-fosfat zanjiri spiral bo'lib buralgan, "
               "ular orasida to'rt xil rangdagi azotli asos juftlari zinapoyadek joylashgan.",
        "summary": "Ikki polinukleotid zanjirining spiral buralishi va komplementar asos juftlari "
                   "uch o'lchamli ko'rinishda.",
        "body": "Model DNK molekulasining bir bo'lagini ko'rsatadi. Ikki zanjir bir-biriga o'ralib, o'ng "
                "qo'shspiral hosil qiladi; zanjirlar orasidagi «zinapoyalar» — azotli asos juftlari.\n\n"
                "Ranglar asoslarni farqlaydi: A (adenin) doim T (timin) bilan, G (guanin) doim C (sitozin) "
                "bilan juftlashadi. Spiralning bir to'liq aylanishiga taxminan 10 juft asos to'g'ri keladi.",
        "parts": "Qand-fosfat zanjiri — spiralning tashqi «tayanchi», nukleotidlarni bog'laydi\n"
                 "Adenin – Timin (A–T) — ikki vodorod bog' bilan juftlashadi\n"
                 "Guanin – Sitozin (G–C) — uch vodorod bog' bilan juftlashadi\n"
                 "Katta va kichik ariqcha — oqsillar DNK bilan shu yerda bog'lanadi",
        "task": "Bir zanjirdagi asoslar ketma-ketligi ATGCCA bo'lsa, ikkinchi zanjirni yozing.\n"
                "Nima uchun G–C juftlari ko'p bo'lgan DNK qizdirilganda qiyinroq ajraladi?\n"
                "Modeldagi qaysi xususiyat DNKning o'z-o'zidan nusxa ko'chirishini tushuntiradi?",
    },
    {
        "slug": "3d-xloroplast",
        "title": "Xloroplast ichki tuzilishi",
        "section": "hujayra-biologiyasi",
        "visual": "img/sim3d/xloroplast.svg",
        "alt": "Uzunasiga kesilgan linza shaklidagi yashil xloroplast. Ichida tanga ustunlariga o'xshash "
               "granalar, ularni bog'lovchi lamellalar va och yashil stroma ko'rinadi.",
        "summary": "Qo'sh membranali organoid kesimda: tilakoidlar granalarga yig'ilgan, "
                   "ular orasida stroma.",
        "body": "Model xloroplastni uzunasiga kesilgan holda ko'rsatadi. Ichki membranalar yassi xaltachalar — "
                "tilakoidlarni hosil qiladi; ular tangalar ustuni kabi taxlanib, granalarni tashkil etadi.\n\n"
                "Fotosintezning yorug'lik bosqichi tilakoid membranalarida, qorong'ilik bosqichi (Kalvin sikli) "
                "esa stromada boradi. 3D kesim bu ikki «ish joyi» bir-biriga qanchalik yaqinligini ko'rsatadi.",
        "parts": "Tashqi va ichki membrana — organoidni sitoplazmadan ajratadi\n"
                 "Grana — tilakoidlar ustuni, xlorofill shu yerda joylashgan\n"
                 "Lamella — granalarni bir-biri bilan bog'laydi\n"
                 "Stroma — suyuq muhit, CO₂ dan glyukoza hosil bo'ladi\n"
                 "Kraxmal donachasi — fotosintez mahsulotining zaxirasi",
        "task": "Yorug'lik va qorong'ilik bosqichlari modelning qaysi qismida borishini ko'rsating.\n"
                "Nima uchun tilakoidlar ustun bo'lib taxlangan? Bu tuzilmaning afzalligi nimada?\n"
                "Xloroplastning mitoxondriya bilan 2 ta o'xshash va 2 ta farqli jihatini yozing.",
    },
    {
        "slug": "3d-barg-kesimi",
        "title": "Barg plastinkasining ko'ndalang kesimi",
        "section": "hujayra-biologiyasi",
        "visual": "img/sim3d/barg-kesimi.svg",
        "alt": "Barg plastinkasidan kesib olingan uch o'lchamli blok. Yuqorida epidermis, ostida ustunsimon "
               "to'qima, g'ovak to'qima, o'rtada o'tkazuvchi naycha va pastki epidermisda og'izcha ko'rinadi.",
        "summary": "Bargdan kesib olingan blok: to'qimalar qatlam-qatlam, og'izcha va tomir "
                   "bargning ichki muhitiga qanday ulangani ko'rinadi.",
        "body": "Model barg plastinkasining kichik bir bo'lagini kesib olingan blok ko'rinishida tasvirlaydi. "
                "Blokning old yuzasi — ko'ndalang kesim, yuqori yuzasi — bargning ustki tomoni.\n\n"
                "Yuqoridan pastga qarab to'qimalar ketma-ketligini kuzating: har bir qatlamning tuzilishi uning "
                "fotosintez, gaz almashinuvi va suv bug'lantirishdagi vazifasiga mos.",
        "parts": "Ustki epidermis — himoya qiladi, ustidagi kutikula suv yo'qotilishini kamaytiradi\n"
                 "Ustunsimon to'qima — xloroplastga eng boy qatlam, asosiy fotosintez shu yerda\n"
                 "G'ovak to'qima — hujayralararo bo'shliqlar gaz almashinuvini ta'minlaydi\n"
                 "O'tkazuvchi tomir — ksilema suv keltiradi, floema organik moddani olib ketadi\n"
                 "Og'izcha — pastki epidermisdagi teshik, gaz almashinuvi va transpiratsiya",
        "task": "Nima uchun og'izchalar ko'pincha bargning pastki tomonida joylashgan?\n"
                "Ustunsimon to'qima nega yuqorida, g'ovak to'qima nega pastda? Tuzilish va vazifani bog'lang.\n"
                "Cho'l o'simligining bargi bu modeldan qanday farq qilishi mumkin? Taxmin qiling.",
    },
]

PLOT_RESOURCES = [
    {
        "slug": "urug-unuvchanligini-aniqlash",
        "title": "Urug'ning unuvchanligini aniqlash",
        "kind": "PLAN", "season": "SPRING", "grade": "6-sinf", "duration": "7–10 kun",
        "summary": "Ekishdan oldin urug' sifatini tekshirish: 100 ta urug'dan nechtasi unib chiqishini "
                   "hisoblab, unuvchanlik foizini aniqlash.",
        "body": "MAQSAD\nO'quvchilar urug'ning unuvchanligini aniqlashni o'rganadi va ekish me'yorini hisoblashda "
                "bu ko'rsatkichdan foydalanadi.\n\n"
                "JIHOZLAR\nBug'doy, loviya yoki no'xat urug'i (har bir guruhga 100 ta), likopcha yoki Petri "
                "idishi, filtr qog'oz yoki doka, suv, yorliq, kuzatuv jadvali.\n\n"
                "BAJARISH TARTIBI\n"
                "1. Likopchaga ikki qavat nam filtr qog'oz yoki doka to'shang.\n"
                "2. 100 ta urug'ni bir-biriga tegmaydigan qilib tering va ustini nam doka bilan yoping.\n"
                "3. Idishga guruh nomi va sanani yozing, xona haroratida (20–25 °C) saqlang.\n"
                "4. Har kuni bir vaqtda unib chiqqan urug'larni sanab, jadvalga yozing; qog'ozni nam tuting.\n"
                "5. 7-kuni unuvchanlik foizini hisoblang: unib chiqqan urug'lar soni ÷ 100 × 100%.\n\n"
                "XULOSA UCHUN SAVOLLAR\n"
                "• Qaysi kuni eng ko'p urug' unib chiqdi?\n"
                "• Unuvchanligi 70% bo'lgan urug'dan ekishda me'yorni qanday o'zgartirish kerak?\n"
                "• Harorat past bo'lsa, natija qanday o'zgaradi? Tekshirish rejasini tuzing.",
    },
    {
        "slug": "loviya-osishi-kundaligi",
        "title": "Loviya o'sishini kuzatish kundaligi",
        "kind": "DIARY", "season": "SPRING", "grade": "6–7-sinflar", "duration": "4 hafta",
        "summary": "Uchastkaga ekilgan loviyaning unib chiqishidan gullashigacha haftalik o'lchov va "
                   "kuzatuvlarni yozib borish uchun shablon.",
        "body": "KUNDALIKNI YURITISH TARTIBI\nHar hafta bir kunda (masalan, dushanba) bir xil o'simliklarni "
                "kuzating. Belgilangan 5 ta o'simlikka raqamli qoziqcha qo'ying.\n\n"
                "HAR BIR KUZATUVDA YOZILADI\n"
                "• Sana, havo harorati va ob-havo (quyoshli, bulutli, yog'ingarchilik)\n"
                "• Poya balandligi (sm) — tuproq sathidan uchki kurtakkacha\n"
                "• Chin barglar soni\n"
                "• Rivojlanish bosqichi: unib chiqish, urug'palla barglar, chin barglar, shonalash, gullash\n"
                "• Sug'orish, yumshatish yoki o'g'itlash bajarilgan bo'lsa — qayd\n"
                "• Zararkunanda yoki kasallik belgilari\n\n"
                "NAMUNAVIY JADVAL USTUNLARI\n"
                "Sana | O'simlik № | Balandlik, sm | Barglar soni | Bosqich | Izoh\n\n"
                "YAKUNIY TOPSHIRIQ\n"
                "4 haftalik o'rtacha balandlik bo'yicha o'sish grafigini chizing. Qaysi haftada o'sish eng tez "
                "bo'ldi va buni ob-havo yozuvlaringiz bilan qanday izohlaysiz?",
    },
    {
        "slug": "uchastka-fenologik-taqvimi",
        "title": "Uchastkadagi daraxt va butalarning fenologik taqvimi",
        "kind": "CALENDAR", "season": "ALL", "grade": "5–7-sinflar", "duration": "O'quv yili davomida",
        "summary": "Kurtak bo'rtishi, barg chiqarish, gullash, meva pishishi va barg to'kilishi "
                   "muddatlarini yil bo'yi qayd etish.",
        "body": "NIMA UCHUN KERAK\nFenologik kuzatuvlar o'simlik hayotidagi mavsumiy o'zgarishlarni ob-havo bilan "
                "bog'lashga o'rgatadi. Bir necha yil yuritilgan taqvim maktab uchun qimmatli ma'lumot bazasiga "
                "aylanadi.\n\n"
                "KUZATILADIGAN O'SIMLIKLAR (namuna)\n"
                "O'rik, olma, tut, terak, atirgul, na'matak — uchastkada o'sadigan 5–6 tur tanlanadi.\n\n"
                "QAYD ETILADIGAN FENOFAZALAR\n"
                "1. Kurtaklarning bo'rtishi\n"
                "2. Birinchi barglarning chiqishi\n"
                "3. Gullashning boshlanishi va ommaviy gullash\n"
                "4. Mevalarning pishishi\n"
                "5. Barglarning sarg'ayishi\n"
                "6. Ommaviy barg to'kilishi\n\n"
                "TAQVIMNI YURITISH\n"
                "Har bir tur uchun alohida qator ochiladi; fenofaza boshlangan sana katakchaga yoziladi. "
                "Mavsum oxirida sinf bilan birga «qaysi tur eng erta uyg'ondi va nega?» degan savol muhokama "
                "qilinadi.",
    },
    {
        "slug": "uchastkada-xavfsizlik-qoidalari",
        "title": "Uchastkada ishlashda xavfsizlik qoidalari",
        "kind": "GUIDE", "season": "ALL", "grade": "5–9-sinflar", "duration": "Mashg'ulot boshida 10 daqiqa",
        "summary": "O'quv-tajriba uchastkasida amaliy mashg'ulotdan oldin o'quvchilar bilan o'tiladigan "
                   "yo'riqnoma va imzo varag'i uchun matn.",
        "body": "UMUMIY QOIDALAR\n"
                "• Uchastkaga faqat o'qituvchi bilan birga kiriladi.\n"
                "• Ish kiyimi va qo'lqop kiyiladi; ochiq poyabzalda ishlash mumkin emas.\n"
                "• Ish joyida ovqatlanish va ichimlik ichish taqiqlanadi.\n\n"
                "ASBOBLAR BILAN ISHLASH\n"
                "• Ketmon, belkurak va xaskashni tig'i yoki tishi pastga qaratib olib yuriladi.\n"
                "• Asbob yerga tishi yuqoriga qaratib qo'yilmaydi.\n"
                "• Ishlayotgan o'quvchilar orasidagi masofa kamida 1,5 metr bo'lishi kerak.\n\n"
                "O'G'IT VA DORILAR\n"
                "• Mineral o'g'it va o'simlik himoya vositalari bilan faqat o'qituvchi ishlaydi.\n"
                "• O'quvchilar ularni qo'lqopsiz ushlamaydi.\n\n"
                "ISH TUGAGACH\n"
                "• Asboblar tozalanib, omborga topshiriladi.\n"
                "• Qo'l sovunlab yuviladi.\n"
                "• Jarohat yoki o'zini yomon his qilish holati darhol o'qituvchiga aytiladi.",
    },
    {
        "slug": "pomidor-kochatini-otqazish",
        "title": "Pomidor ko'chatini o'tqazish texnologiyasi",
        "kind": "GUIDE", "season": "SPRING", "grade": "7-sinf", "duration": "2 dars",
        "summary": "Ko'chatni tanlash, egatni tayyorlash, o'tqazish chuqurligi va parvarishi — "
                   "bosqichma-bosqich amaliy yo'riqnoma.",
        "body": "MUDDAT\nKo'chat tuproq harorati 12–15 °C ga yetib, sovuq qaytish xavfi o'tgach o'tqaziladi "
                "(ko'pchilik hududlarda aprel oxiri – may boshi).\n\n"
                "SIFATLI KO'CHAT BELGILARI\n"
                "Balandligi 20–25 sm, 5–7 ta chin barg, poyasi yo'g'on va to'q yashil, ildizi oq va tuproq "
                "bilan birga.\n\n"
                "BAJARISH TARTIBI\n"
                "1. Maydon yumshatiladi, 1 m² ga 3–4 kg chirindi solinadi.\n"
                "2. Egatlar orasi 70 sm, qator oralig'i 40 sm qilib belgilanadi.\n"
                "3. Chuqurcha ochib, 0,5 litr suv quyiladi.\n"
                "4. Ko'chat urug'palla barglarigacha ko'miladi, tuproq qo'l bilan zichlanadi.\n"
                "5. O'tqazilgan kuni kechqurun va 3 kundan so'ng sug'oriladi.\n\n"
                "KUZATUV TOPSHIRIG'I\n"
                "Ikki guruh ko'chat solishtiriladi: biri chirindili, biri chirindisiz qatorda. 3 hafta davomida "
                "balandlik va barglar soni kundalikka yoziladi.",
    },
]
