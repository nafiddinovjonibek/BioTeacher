"""
Diagnostika uchun HAQIQIY mazmunli savollar bazasi.

Bu fayl `seed_demo` boshqaruv buyrug'i tomonidan o'qiladi. Savollar tasodifiy
matn emas — har biri o'z komponentiga mazmunan bog'langan va ilmiy rahbar
tomonidan tahrirlanishi mumkin bo'lgan holda yozilgan.

Formatlar:
  LIKERT_ITEMS  — (komponent, matn, teskari_baholanadimi)
  TEST_ITEMS    — (komponent, bloom, savol, [variantlar], to'g'ri_indeks, izoh)
"""

from core.enums import BloomLevel, Component

# ---------------------------------------------------------------------------
# 1. LIKERT ANKETA — o'z-o'zini baholash (FR-07). Komponentga 10 tadan, jami 50.
#    Teskari baholanadigan savollar (FR-09) `True` bilan belgilangan.
# ---------------------------------------------------------------------------

LIKERT_ITEMS = [
    # --- MOT: motivatsion-qadriyatli ---
    (Component.MOT, "Men biologiya o'qituvchisi bo'lishni ongli ravishda tanlaganman.", False),
    (Component.MOT, "Kasbiy adabiyotlarni majburiyatsiz, o'z xohishim bilan o'qiyman.", False),
    (Component.MOT, "Biologiya sohasidagi yangiliklarni muntazam kuzatib boraman.", False),
    (Component.MOT, "O'zimni kelajakda o'z fanini puxta biladigan o'qituvchi sifatida tasavvur qilaman.", False),
    (Component.MOT, "Kasbiy qiyinchilik meni ruhdan tushirmaydi, aksincha harakatga undaydi.", False),
    (Component.MOT, "O'z ustimda ishlashni ko'pincha keyinga suraman.", True),
    (Component.MOT, "Pedagogik faoliyat men uchun shunchaki ish emas, qadriyat.", False),
    (Component.MOT, "Pedagogik amaliyotni qiziqish bilan kutaman.", False),
    (Component.MOT, "Bahoim yaxshi bo'lsa, qo'shimcha o'rganishga hojat yo'q deb hisoblayman.", True),
    (Component.MOT, "O'quvchilarga real foyda keltirishni kasbimning asosiy ma'nosi deb bilaman.", False),

    # --- COG: kognitiv ---
    (Component.COG, "Biologiyaning asosiy tushunchalarini erkin va aniq tushuntira olaman.", False),
    (Component.COG, "Biologiya–kimyo–ekologiya o'rtasidagi bog'liqlikni darsda ko'rsata olaman.", False),
    (Component.COG, "Yangi ilmiy ma'lumotni mustaqil topaman va manbaning ishonchliligini tekshiraman.", False),
    (Component.COG, "Zamonaviy pedagogik texnologiyalarning mohiyatini bilaman.", False),
    (Component.COG, "Murakkab biologik jarayonni o'quvchi tushunadigan tilda soddalashtira olaman.", False),
    (Component.COG, "Davlat ta'lim standarti va o'quv dasturi talablarini yaxshi bilaman.", False),
    (Component.COG, "Ko'p hollarda faqat darslikdagi ma'lumot bilan cheklanaman.", True),
    (Component.COG, "Biologik atamalarni to'g'ri va o'z o'rnida qo'llayman.", False),
    (Component.COG, "O'quvchilarning mavzu bo'yicha tipik xatolarini oldindan bila olaman.", False),
    (Component.COG, "Bilimimdagi bo'shliqni aniqlab, uni to'ldirish rejasini tuzaman.", False),

    # --- ACT: faoliyatli-texnologik ---
    (Component.ACT, "Dars maqsadini aniq va o'lchanadigan qilib qo'ya olaman.", False),
    (Component.ACT, "Dars bosqichlarini vaqt bo'yicha oqilona taqsimlayman.", False),
    (Component.ACT, "Mavzuga mos faol ta'lim metodini asoslab tanlay olaman.", False),
    (Component.ACT, "O'quvchilar uchun turli murakkablikdagi topshiriqlar tayyorlayman.", False),
    (Component.ACT, "Dars davomida o'quvchilarning tushunish darajasini nazorat qilib boraman.", False),
    (Component.ACT, "Kutilmagan vaziyatda dars rejasini tezda moslashtira olaman.", False),
    (Component.ACT, "Asosan tayyor dars ishlanmalaridan o'zgarishsiz foydalanaman.", True),
    (Component.ACT, "Baholash mezonlarini o'quvchilarga ish boshlanishidan oldin tushuntiraman.", False),
    (Component.ACT, "Guruhli ishni har bir o'quvchi faol bo'ladigan qilib tashkil qila olaman.", False),
    (Component.ACT, "Ko'rgazmali va raqamli vositalarni maqsadga muvofiq ishlataman.", False),

    # --- REF: refleksiv ---
    (Component.REF, "Har bir bajargan ishimdan keyin nima yaxshi chiqqanini tahlil qilaman.", False),
    (Component.REF, "Xatolarimni tan olaman va ularning sababini izlayman.", False),
    (Component.REF, "Tanqidiy fikrni shaxsiy hujum deb qabul qilaman.", True),
    (Component.REF, "O'z kasbiy faoliyatim haqida qaydlar yuritaman (kundalik, eslatma).", False),
    (Component.REF, "O'zimning kuchli va zaif tomonlarimni aniq ayta olaman.", False),
    (Component.REF, "Boshqalarning fikrini o'zim so'rayman va undan xulosa chiqaraman.", False),
    (Component.REF, "Muvaffaqiyatsizlikdan keyin nimani boshqacha qilishni aniq rejalashtiraman.", False),
    (Component.REF, "Ko'pincha \"shunday bo'ldi-da\" deb o'tib ketaman.", True),
    (Component.REF, "O'z ishimni mezonlar asosida, hissiyotsiz baholay olaman.", False),
    (Component.REF, "O'zimga qo'ygan bahoim odatda tashqi baho bilan mos keladi.", False),

    # --- CRE: kreativ ---
    (Component.CRE, "Bir mavzuni bir necha xil usulda tushuntira olaman.", False),
    (Component.CRE, "Noodatiy topshiriq va o'quv vazifalarini o'ylab topaman.", False),
    (Component.CRE, "Darsda o'yin, hikoya, metafora kabi vositalardan foydalanaman.", False),
    (Component.CRE, "Standart yechim ishlamasa, yangi variant izlayman.", False),
    (Component.CRE, "O'z g'oyalarimni hamkasblar bilan bo'lishishdan cho'chimayman.", False),
    (Component.CRE, "Odatda hamma qiladigan usuldan chetga chiqmayman.", True),
    (Component.CRE, "O'quvchilarning nostandart javoblarini rag'batlantiraman.", False),
    (Component.CRE, "Mavjud metodni o'z sinfim sharoitiga moslab o'zgartiraman.", False),
    (Component.CRE, "Biologik mavzuni o'quvchining real hayoti bilan bog'lay olaman.", False),
    (Component.CRE, "Loyihaviy va ijodiy topshiriqlar tuzishni yoqtiraman.", False),
]


# ---------------------------------------------------------------------------
# 2. BILIM TESTI — Bloom darajalari bo'yicha taqsimlangan (FR-08).
#    (komponent, bloom, savol, variantlar, to'g'ri_indeks, izoh)
# ---------------------------------------------------------------------------

TEST_ITEMS = [
    # === COG · 1-daraja: Bilaman ===
    (Component.COG, BloomLevel.KNOW,
     "Fotosintezning yorug'lik bosqichi hujayraning qaysi qismida kechadi?",
     ["Tilakoid membranalarida", "Xloroplast stromasida", "Mitoxondriya matriksida", "Hujayra sitoplazmasida"],
     0, "Yorug'lik bosqichi tilakoid membranalarida, qorong'ilik bosqichi (Kalvin sikli) stromada kechadi."),

    (Component.COG, BloomLevel.KNOW,
     "DNK molekulasida azot asoslari qanday juftlashadi?",
     ["A–T va G–S", "A–G va T–S", "A–S va G–T", "Barcha asoslar o'zaro erkin juftlashadi"],
     0, "Komplementarlik qoidasi: adenin–timin (2 vodorod bog'i), guanin–sitozin (3 vodorod bog'i)."),

    (Component.COG, BloomLevel.KNOW,
     "Ribosomalarning asosiy vazifasi nima?",
     ["Oqsil sintezi", "ATF sintezi", "Lipidlar sintezi", "Moddalarni tashish"],
     0, "Ribosoma — translyatsiya, ya'ni i-RNK ma'lumotini oqsilga aylantirish joyi."),

    (Component.COG, BloomLevel.KNOW,
     "Mitoz bo'linishining qaysi fazasida xromosomalar hujayra ekvatorida joylashadi?",
     ["Metafaza", "Profaza", "Anafaza", "Telofaza"],
     0, "Metafazada xromosomalar ekvatorial tekislikda saflanadi — bu mitozning eng ko'rinarli fazasi."),

    (Component.COG, BloomLevel.KNOW,
     "Qaysi organoid faqat o'simlik hujayrasida uchraydi?",
     ["Xloroplast", "Mitoxondriya", "Ribosoma", "Golji apparati"],
     0, "Xloroplast va sellulozali hujayra devori o'simlik hujayrasining ajratuvchi belgilaridir."),

    # === COG · 2-daraja: Tushunaman ===
    (Component.COG, BloomLevel.UNDERSTAND,
     "Nima uchun mitoxondriya \"hujayraning energiya stansiyasi\" deb ataladi?",
     ["Unda nafas olish jarayonida ATF sintezlanadi",
      "U hujayraga kislorod kirgizadi",
      "U oziq moddalarni to'playdi",
      "U hujayra haroratini boshqaradi"],
     0, "Kislorodli nafas olishning Krebs sikli va oksidlanish fosforlanishi mitoxondriyada kechadi."),

    (Component.COG, BloomLevel.UNDERSTAND,
     "Osmos hodisasining mohiyati nimada?",
     ["Erituvchining yarim o'tkazuvchi membrana orqali konsentratsiya bo'yicha harakati",
      "Erigan moddaning membrana orqali faol tashilishi",
      "Suvning energiya sarflab tashilishi",
      "Gazlarning membrana orqali almashinuvi"],
     0, "Osmos — passiv jarayon: suv kam konsentratsiyali muhitdan yuqori konsentratsiyalisiga o'tadi."),

    (Component.COG, BloomLevel.UNDERSTAND,
     "Fermentlar reaksiya tezligini qanday oshiradi?",
     ["Aktivlanish energiyasini pasaytirish orqali",
      "Reaksiya mahsuloti miqdorini oshirish orqali",
      "Harorat ko'tarish orqali",
      "Substrat miqdorini ko'paytirish orqali"],
     0, "Ferment aktivlanish energiyasi to'sig'ini pasaytiradi; muvozanat holatini o'zgartirmaydi."),

    (Component.COG, BloomLevel.UNDERSTAND,
     "Nima uchun retsessiv belgi ota-onada ko'rinmasa ham, bolada namoyon bo'lishi mumkin?",
     ["Ota-ona geterozigota bo'lishi mumkin",
      "Retsessiv gen mutatsiya natijasida paydo bo'ladi",
      "Retsessiv genlar faqat bolalarda ishlaydi",
      "Dominant gen yosh o'tishi bilan yo'qoladi"],
     0, "Aa × Aa chatishtirishda 25% aa (retsessiv fenotip) nasl olinadi."),

    (Component.COG, BloomLevel.UNDERSTAND,
     "Ekotizimda energiyaning bir trofik darajadan ikkinchisiga o'tishida ~90% yo'qoladi. Buning sababi nima?",
     ["Energiyaning katta qismi nafas olish va issiqlikka sarflanadi",
      "Organizmlar energiyani to'liq hazm qila olmaydi va uni yo'qotadi",
      "Energiya quyoshga qaytadi",
      "Energiya tuproqqa singib ketadi"],
     0, "10% qoidasi: energiyaning aksari hayot faoliyati va issiqlik tarqalishiga ketadi."),

    # === COG · 3-daraja: Qo'llayman ===
    (Component.COG, BloomLevel.APPLY,
     "Aa × Aa chatishtirishda F1 avlodda fenotip nisbati qanday bo'ladi?",
     ["3 : 1", "1 : 1", "9 : 3 : 3 : 1", "1 : 2 : 1"],
     0, "Monogibrid chatishtirishda fenotip 3:1, genotip esa 1:2:1 nisbatda bo'ladi."),

    (Component.COG, BloomLevel.APPLY,
     "DNK zanjirining bir qismi TAC GGA TTC bo'lsa, unga komplementar i-RNK qanday bo'ladi?",
     ["AUG SSU AAG", "ATG SST AAG", "AUG GGU AAG", "UAS SSA UUS"],
     0, "Transkripsiyada T→A, A→U, G→S, S→G. Timin o'rniga urasil yoziladi."),

    (Component.COG, BloomLevel.APPLY,
     "Qonning I(0) guruhiga ega ota-ona va IV(AB) guruhiga ega ota-onadan qanday guruhli bolalar tug'ilishi mumkin?",
     ["II(A) va III(B)", "Faqat IV(AB)", "I(0) va IV(AB)", "Barcha to'rt guruh"],
     0, "ii × I^A I^B → I^A i (II guruh) yoki I^B i (III guruh)."),

    (Component.COG, BloomLevel.APPLY,
     "O'simlik ildizini konsentrlangan tuz eritmasiga solsak, hujayrada nima kuzatiladi?",
     ["Plazmoliz — sitoplazma devordan ajraladi",
      "Deplazmoliz — hujayra shishadi",
      "Hujayra devori yoriladi",
      "Hech qanday o'zgarish bo'lmaydi"],
     0, "Gipertonik muhitda suv hujayradan chiqadi va plazmoliz ro'y beradi."),

    # === COG · 4-daraja: Tahlil qilaman ===
    (Component.COG, BloomLevel.ANALYZE,
     "Tajribada o'simlik yorug'liksiz qoldirildi, lekin harorat va namlik saqlandi. Bir hafta o'tib barglar sarg'aydi. Eng ishonchli izoh qaysi?",
     ["Yorug'lik yo'qligida xlorofill parchalanadi va yangisi sintezlanmaydi",
      "Harorat past bo'lgani uchun barglar sarg'aygan",
      "O'simlik suv yetishmasligidan qurigan",
      "Barglar tabiiy ravishda qariydi"],
     0, "Nazorat qilinayotgan yagona o'zgaruvchi — yorug'lik, demak sabab shunda: xlorofill sintezi to'xtaydi."),

    (Component.COG, BloomLevel.ANALYZE,
     "Ikki hududda bir tur o'simlik o'sadi: birida bargi keng, ikkinchisida ingichka. Genotip bir xil. Bu nimani ko'rsatadi?",
     ["Modifikatsion (fenotipik) o'zgaruvchanlikni",
      "Mutatsion o'zgaruvchanlikni",
      "Kombinativ o'zgaruvchanlikni",
      "Yangi tur paydo bo'lganini"],
     0, "Genotip bir xil bo'lgani uchun farq irsiy emas — bu reaksiya normasi doirasidagi modifikatsiya."),

    (Component.COG, BloomLevel.ANALYZE,
     "Ekotizimda yirtqichlar butunlay yo'q qilinsa, qisqa muddatda nima kuzatiladi?",
     ["O'txo'rlar soni ortadi, so'ng o'simlik zaxirasi kamayadi",
      "Ekotizim barqarorroq bo'ladi",
      "O'simliklar soni doimiy ortib boradi",
      "Hech qanday sezilarli o'zgarish bo'lmaydi"],
     0, "Yirtqich — tartibga soluvchi omil; uni yo'qotish trofik kaskadga olib keladi."),

    # === COG · 5-daraja: Baholayman ===
    (Component.COG, BloomLevel.EVALUATE,
     "Talaba tajribada 5 ta o'simlikni turli yorug'likda o'stirdi, lekin sug'orish miqdorini yozib bormadi. Bu tajribaning asosiy kamchiligi nimada?",
     ["Nazorat qilinmagan o'zgaruvchi natijani ishonchsiz qiladi",
      "Namuna hajmi juda katta",
      "Tajriba juda uzoq davom etgan",
      "Yorug'lik o'zgaruvchi sifatida noto'g'ri tanlangan"],
     0, "Ilmiy tajribada faqat bitta mustaqil o'zgaruvchi o'zgarishi, qolganlari nazoratda bo'lishi kerak."),

    (Component.COG, BloomLevel.EVALUATE,
     "Internetdagi \"Bu o'simlik barcha kasallikni davolaydi\" degan maqolani baholashda birinchi navbatda nimaga qaraysiz?",
     ["Manba va tekshirilgan ilmiy tadqiqotga havola borligiga",
      "Maqolaning necha marta ulashilganiga",
      "Sarlavhaning qiziqarliligiga",
      "Rasmlarning sifatiga"],
     0, "Ilmiy savodxonlik: da'vo dalilga va tekshiriladigan manbaga tayanishi kerak."),

    # === ACT · pedagogik faoliyat ===
    (Component.ACT, BloomLevel.UNDERSTAND,
     "\"Hujayra tuzilishini tushuntirib bera oladi\" — bu dars maqsadi sifatida qanday baholanadi?",
     ["Yaxshi — natija kuzatiladigan fe'l bilan ifodalangan",
      "Yomon — juda uzun",
      "Yomon — o'qituvchi faoliyatini bildiradi",
      "Yaxshi — chunki mavzu nomi kiritilgan"],
     0, "O'lchanadigan maqsad o'quvchi harakatini bildiruvchi fe'l bilan yoziladi (aytadi, ko'rsatadi, taqqoslaydi)."),

    (Component.ACT, BloomLevel.APPLY,
     "O'quvchilar \"Fotosintez\" mavzusini yodlashgan, lekin masala yecha olmaydi. Qaysi qadam eng mantiqiy?",
     ["Amaliy vaziyatli topshiriqlar berish va jarayonni bosqichma-bosqich tahlil qildirish",
      "Mavzuni yana bir marta o'qib berish",
      "Ko'proq ta'rif yodlatish",
      "Test savollari sonini oshirish"],
     0, "Muammo \"bilish\" darajasida qolganida — vazifani \"qo'llash\" darajasiga ko'tarish kerak."),

    (Component.ACT, BloomLevel.APPLY,
     "45 daqiqalik darsda yangi mavzuga odatda qancha vaqt ajratish maqbul hisoblanadi?",
     ["15–20 daqiqa, qolgani mustahkamlash va amaliyotga",
      "40 daqiqa, mustahkamlash uyga vazifada",
      "5 daqiqa, qolgani mustaqil o'qishga",
      "Butun dars — yangi mavzuga"],
     0, "Faol ta'limda bayon qisqa bo'lib, vaqtning katta qismi o'quvchi faoliyatiga beriladi."),

    (Component.ACT, BloomLevel.ANALYZE,
     "Guruhli ishda bir o'quvchi hamma ishni bajarib, qolganlari kuzatib turibdi. Sababi ko'pincha nimada?",
     ["Guruh a'zolari o'rtasida rollar taqsimlanmagan",
      "Guruh juda kichik",
      "Topshiriq juda oson",
      "O'quvchilar bir-birini yoqtirmaydi"],
     0, "Samarali guruhli ishda har bir a'zoning aniq roli va shaxsiy javobgarligi bo'lishi shart."),

    (Component.ACT, BloomLevel.EVALUATE,
     "Ikki o'qituvchi bir mavzuni o'tdi: biri video ko'rsatdi, ikkinchisi o'quvchilarga model yasattirdi. Qaysi mezon bo'yicha taqqoslash to'g'riroq?",
     ["O'quvchilar erishgan natija va faollik darajasi bo'yicha",
      "Qaysi biri ko'proq texnika ishlatgani bo'yicha",
      "Dars qancha qiziqarli o'tgani bo'yicha",
      "O'qituvchining tajribasi bo'yicha"],
     0, "Metodning samaradorligi vositaning zamonaviyligi bilan emas, o'quv natijasi bilan o'lchanadi."),

    # === REF · refleksiya ===
    (Component.REF, BloomLevel.UNDERSTAND,
     "Refleksiyaning asosiy maqsadi nima?",
     ["O'z faoliyatini tahlil qilib, keyingi qadamni aniqlash",
      "Bajarilgan ishni sanab o'tish",
      "O'zini boshqalar bilan taqqoslash",
      "Xatolar uchun uzr so'rash"],
     0, "Refleksiya — hisobot emas, tahlil: nima bo'ldi, nega, endi nima qilaman."),

    (Component.REF, BloomLevel.EVALUATE,
     "Qaysi refleksiya sifatliroq hisoblanadi?",
     ["\"Guruhli ish rejadan 10 daqiqa cho'zildi, chunki rollarni oldindan taqsimlamadim; keyingi darsda rollarni yozib beraman\"",
      "\"Dars yaxshi o'tdi, hammasi zo'r bo'ldi\"",
      "\"O'quvchilar sust edi, ular tayyorlanmagan\"",
      "\"Menga dars yoqdi\""],
     0, "Sifatli refleksiyada aniq fakt, sabab-oqibat bog'lanishi va keyingi qadam bo'ladi."),

    (Component.REF, BloomLevel.ANALYZE,
     "O'z ishini doim mentordan yuqori baholaydigan talaba uchun eng foydali qadam qaysi?",
     ["Rubrika mezonlarini o'qib, har bir ballni dalil bilan asoslashga o'rganish",
      "Umuman o'zini baholamaslik",
      "Mentordan pastroq ball qo'yishni odat qilish",
      "Boshqa talabalar bahosiga qarab moslashish"],
     0, "Baholash adekvatligi mezonni tushunish va dalilga tayanish orqali o'sadi."),

    # === CRE · kreativlik ===
    (Component.CRE, BloomLevel.CREATE,
     "\"Moddalar almashinuvi\" mavzusini tushuntirish uchun qaysi yondashuv ijodiyroq va samaraliroq?",
     ["O'quvchilarga shahar infratuzilmasi metaforasini berib, o'zlariga model tuzdirish",
      "Ta'rifni doskaga yozdirish",
      "Mavzuni ovoz chiqarib o'qitish",
      "Tayyor sxemani daftariga ko'chirtirish"],
     0, "Metafora + o'quvchining o'zi model yaratishi — \"Yarataman\" darajasidagi faoliyat."),

    (Component.CRE, BloomLevel.CREATE,
     "Biologiya darsida o'quvchi \"Bu bilimning menga nima keragi bor?\" deb so'radi. Eng kuchli javob qanday bo'ladi?",
     ["Mavzuni uning kundalik hayotidagi aniq vaziyat bilan bog'lab, misol topishni o'ziga topshirish",
      "\"Imtihonda kerak bo'ladi\" deb aytish",
      "Savolni e'tiborsiz qoldirish",
      "Mavzuning ilmiy ahamiyatini uzoq tushuntirish"],
     0, "Ma'no o'quvchining o'z tajribasi bilan bog'langanda paydo bo'ladi; izlashni unga topshirish motivatsiyani oshiradi."),

    (Component.CRE, BloomLevel.ANALYZE,
     "O'quvchi darslikda yo'q, lekin mantiqan to'g'ri javob berdi. O'qituvchining eng to'g'ri harakati qaysi?",
     ["Javobni tan olib, uni sinf bilan birga tekshirib ko'rish",
      "\"Darslikda bunday emas\" deb rad etish",
      "Javobni e'tiborsiz qoldirib davom etish",
      "Baholamay, keyinroq aytishni so'rash"],
     0, "Nostandart, lekin asosli javobni rag'batlantirish ilmiy fikrlashni rivojlantiradi."),
]


# ---------------------------------------------------------------------------
# 3. DARS TESTLARI — kontent modullariga bog'lanadi (mavzu slugi bo'yicha).
# ---------------------------------------------------------------------------

LESSON_QUIZZES = {
    "hujayra-tuzilishi": [
        ("Hujayra nazariyasining asosiy qoidasi qaysi?",
         ["Har bir hujayra faqat mavjud hujayradan hosil bo'ladi",
          "Hujayralar o'z-o'zidan jonsiz moddadan paydo bo'ladi",
          "Faqat hayvon hujayralarida yadro bo'ladi",
          "Hujayra bo'linmasdan ko'payadi"], 0),
        ("Prokariot hujayrada nima bo'lmaydi?",
         ["Yadro qobig'i", "Ribosoma", "Sitoplazma", "Hujayra membranasi"], 0),
        ("Hujayra membranasining asosiy tarkibi nimadan iborat?",
         ["Ikki qavatli lipid va oqsillar", "Faqat oqsil", "Sellyuloza", "Nuklein kislotalar"], 0),
        ("Lizosomaning vazifasi nima?",
         ["Hujayra ichidagi moddalarni parchalash", "Oqsil sintezi",
          "Energiya ishlab chiqarish", "Irsiy ma'lumot saqlash"], 0),
        ("Xloroplastning ichki tuzilmalari qanday ataladi?",
         ["Tilakoidlar va granalar", "Kristalar", "Sisternalar", "Mikrovorsinkalar"], 0),
    ],
    "fotosintez": [
        ("Fotosintezning umumiy tenglamasi qaysi?",
         ["6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂", "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O",
          "6O₂ + 6H₂O → C₆H₁₂O₆", "CO₂ + H₂O → CH₄ + O₂"], 0),
        ("Fotosintezda ajralib chiqadigan kislorod qaysi moddadan olinadi?",
         ["Suvdan", "Karbonat angidriddan", "Glyukozadan", "Havodan"], 0),
        ("Kalvin sikli qayerda kechadi?",
         ["Xloroplast stromasida", "Tilakoid ichida", "Mitoxondriyada", "Yadroda"], 0),
        ("Qaysi omil fotosintez tezligini cheklovchi bo'lishi mumkin?",
         ["Yorug'lik intensivligi, CO₂ miqdori va harorat",
          "Faqat tuproq unumdorligi", "Faqat kechasi bo'ladigan namlik", "O'simlik yoshi"], 0),
    ],
    "irsiyat-asoslari": [
        ("Gomozigota organizm qanday genotipga ega?",
         ["AA yoki aa", "Aa", "AB", "Aa va aa aralash"], 0),
        ("Mendelning birinchi qonuni nima deyiladi?",
         ["Birinchi avlod bir xilligi qonuni", "Ajralish qonuni",
          "Mustaqil taqsimlanish qonuni", "Bog'langan irsiylanish qonuni"], 0),
        ("Dominant belgi deb nimaga aytiladi?",
         ["Geterozigota holatda ham namoyon bo'ladigan belgi",
          "Faqat gomozigota holatda ko'rinadigan belgi",
          "Har doim yashirin qoladigan belgi",
          "Mutatsiya natijasida paydo bo'ladigan belgi"], 0),
        ("Aa × aa chatishtirishda retsessiv fenotipli nasl ulushi qancha?",
         ["50%", "25%", "75%", "100%"], 0),
    ],
    "ekotizim": [
        ("Ekotizimning produtsentlari kimlar?",
         ["Yashil o'simliklar va fotosintezlovchi bakteriyalar",
          "O'txo'r hayvonlar", "Yirtqichlar", "Zamburug'lar va bakteriyalar"], 0),
        ("Trofik zanjirda energiyaning taxminan qancha qismi keyingi darajaga o'tadi?",
         ["10%", "50%", "90%", "100%"], 0),
        ("Redutsentlarning ekotizimdagi roli nima?",
         ["Organik qoldiqlarni mineral moddalarga parchalash",
          "Fotosintez qilish", "O'txo'rlarni nazorat qilish", "Kislorod ishlab chiqarish"], 0),
        ("Ekologik piramida nimani ko'rsatadi?",
         ["Trofik darajalar bo'yicha biomassa yoki energiya taqsimotini",
          "Turlarning geografik tarqalishini", "Populyatsiya yoshini", "Iqlim o'zgarishini"], 0),
    ],
    "faol-talim-metodlari": [
        ("\"Klaster\" metodi asosan nima uchun ishlatiladi?",
         ["Tushunchalar o'rtasidagi bog'liqlikni vizual tuzilmaga solish uchun",
          "Test o'tkazish uchun", "Uyga vazifa berish uchun", "Baho qo'yish uchun"], 0),
        ("\"INSERT\" metodida o'quvchi matnni o'qiyotib nimani belgilaydi?",
         ["Ma'lum, yangi, tushunarsiz va qarama-qarshi ma'lumotlarni",
          "Faqat yangi so'zlarni", "Faqat sarlavhalarni", "Faqat raqamlarni"], 0),
        ("Muammoli ta'limning yadrosi nimada?",
         ["O'quvchi oldiga tayyor javobsiz, izlanishni talab qiladigan vaziyat qo'yish",
          "Mavzuni batafsil tushuntirib berish", "Ko'p test yechtirish", "Guruhga bo'lish"], 0),
        ("Formativ baholashning maqsadi nima?",
         ["O'quv jarayonida qiyinchilikni aniqlab, o'qitishni to'g'rilash",
          "Chorak oxirida baho qo'yish", "O'quvchilarni reytingga joylash",
          "Ota-onalarga hisobot berish"], 0),
    ],
}
