"""
"BioBilim" moduli uchun haqiqiy o'quv kontenti.

Struktura: SECTIONS → topics → lessons. Har bir darsning matni qisqa, lekin
mazmunli — bo'lajak o'qituvchi uchun fan mazmuni + uni darsda qanday berish
haqidagi metodik izoh birga beriladi.
"""

from core.enums import Component

SECTIONS = [
    {
        "title": "Hujayra biologiyasi",
        "slug": "hujayra-biologiyasi",
        "icon": "🔬",
        "description": "Hayotning tuzilish va funksional birligi — hujayra hamda undagi asosiy jarayonlar.",
        "topics": [
            {
                "title": "Hujayra tuzilishi",
                "slug": "hujayra-tuzilishi",
                "component": Component.COG,
                "summary": "Hujayra nazariyasi, prokariot va eukariot hujayra, organoidlar tizimi.",
                "lessons": [
                    {
                        "title": "Hujayra nazariyasi va hujayra turlari",
                        "slug": "hujayra-nazariyasi",
                        "duration": 20,
                        "body": (
                            "Hujayra nazariyasi uch asosiy qoidaga tayanadi: barcha tirik organizmlar "
                            "hujayralardan tuzilgan; hujayra — tuzilish va funksional birlik; har bir "
                            "hujayra faqat mavjud hujayraning bo'linishidan hosil bo'ladi.\n\n"
                            "Tuzilishiga ko'ra hujayralar ikki katta guruhga bo'linadi. PROKARIOT "
                            "hujayrada shakllangan yadro qobig'i yo'q — irsiy material sitoplazmada, "
                            "nukleoid sohasida joylashadi (bakteriyalar, arxeylar). EUKARIOT hujayrada "
                            "yadro qobiq bilan o'ralgan va membranali organoidlar tizimi rivojlangan "
                            "(o'simlik, hayvon, zamburug', protistlar).\n\n"
                            "O'simlik va hayvon hujayrasi farqi: o'simlikda sellulozali hujayra devori, "
                            "xloroplast va yirik markaziy vakuola bor; hayvon hujayrasida esa "
                            "sentriollar mavjud, devor yo'q.\n\n"
                            "METODIK IZOH. Bu mavzuni faqat sxema ko'rsatib o'tish samarasiz — "
                            "o'quvchilar organoidlar nomini yodlaydi, lekin funksiyasini bog'lay olmaydi. "
                            "Samaraliroq yo'l: hujayrani \"zavod\" yoki \"shahar\" metaforasi bilan berib, "
                            "o'quvchilarga har bir organoidga mos \"kasb\" topishni topshirish. Bunda "
                            "faoliyat \"Bilaman\" darajasidan \"Tahlil qilaman\" darajasiga ko'tariladi."
                        ),
                        "materials": [
                            {"title": "Taqqoslash jadvali", "kind": "TEXT",
                             "body": "Darsda o'quvchilar bilan birga to'ldiring: belgi / prokariot / "
                                     "eukariot / o'simlik / hayvon. Tayyor jadval bermang — birga tuzing."},
                        ],
                    },
                    {
                        "title": "Membrana va moddalar tashilishi",
                        "slug": "membrana-va-transport",
                        "duration": 20,
                        "body": (
                            "Hujayra membranasi ikki qavatli lipid asosidan va unga botgan oqsillardan "
                            "iborat (suyuq mozaika modeli). Uning asosiy xususiyati — TANLAB "
                            "O'TKAZUVCHANLIK.\n\n"
                            "Passiv transport energiya talab qilmaydi va konsentratsiya farqi bo'yicha "
                            "boradi: oddiy diffuziya, yengillashgan diffuziya (oqsil kanallar orqali) va "
                            "OSMOS — suvning yarim o'tkazuvchi membrana orqali harakati.\n\n"
                            "Faol transport ATF energiyasini sarflaydi va moddani konsentratsiya "
                            "gradiyentiga QARSHI tashiydi (masalan, natriy-kaliy nasosi).\n\n"
                            "Gipotonik muhitda hujayra suv shimib shishadi (o'simlikda turgor), "
                            "gipertonik muhitda suv chiqib ketadi va plazmoliz kuzatiladi.\n\n"
                            "METODIK IZOH. Osmos mavhum tushuncha bo'lgani uchun uni albatta tajriba "
                            "bilan mustahkamlash kerak: kartoshka bo'lakchalarini toza suvda va tuzli "
                            "suvda qoldirib, 30 daqiqadan keyin qattiqligini taqqoslash — sinfda "
                            "bajarilishi mumkin bo'lgan eng ishonchli namoyish."
                        ),
                        "materials": [
                            {"title": "Sinf tajribasi: kartoshka va osmos", "kind": "TEXT",
                             "body": "Kerak: kartoshka, 2 ta idish, toza suv, osh tuzi. O'quvchilar avval "
                                     "TAXMIN yozadi, keyin kuzatadi, so'ng taxminini natija bilan "
                                     "solishtiradi. Refleksiya savoli: taxminingiz nega to'g'ri/noto'g'ri chiqdi?"},
                        ],
                    },
                ],
            },
            {
                "title": "Fotosintez",
                "slug": "fotosintez",
                "component": Component.COG,
                "summary": "Yorug'lik va qorong'ilik bosqichlari, cheklovchi omillar, amaliy ahamiyati.",
                "lessons": [
                    {
                        "title": "Fotosintezning bosqichlari",
                        "slug": "fotosintez-bosqichlari",
                        "duration": 25,
                        "body": (
                            "Fotosintez — yorug'lik energiyasini organik moddaning kimyoviy energiyasiga "
                            "aylantirish jarayoni:\n\n"
                            "6CO₂ + 6H₂O --(yorug'lik, xlorofill)--> C₆H₁₂O₆ + 6O₂\n\n"
                            "YORUG'LIK BOSQICHI tilakoid membranalarida kechadi. Xlorofill yorug'lik "
                            "kvantini yutadi, suv fotolizga uchraydi (shundan kislorod ajraladi), ATF va "
                            "NADPH hosil bo'ladi.\n\n"
                            "QORONG'ILIK BOSQICHI (Kalvin sikli) stromada kechadi va yorug'likka "
                            "bevosita bog'liq emas, lekin yorug'lik bosqichi bergan ATF va NADPH ni "
                            "ishlatadi. Bu yerda CO₂ fiksatsiya qilinib, glyukoza sintezlanadi.\n\n"
                            "CHEKLOVCHI OMILLAR: yorug'lik intensivligi, CO₂ konsentratsiyasi va harorat. "
                            "Fotosintez tezligi eng kam ta'minlangan omil bilan cheklanadi.\n\n"
                            "METODIK IZOH. Eng ko'p uchraydigan o'quvchi xatosi — kislorod karbonat "
                            "angidriddan ajraladi deb o'ylash. Buni oldini olish uchun izotopli tajriba "
                            "(H₂¹⁸O) natijasini keltiring: nishonlangan kislorod aynan SUVdan chiqadi. "
                            "Bu \"nega bilamiz?\" savoliga javob berib, ilmiy fikrlashni shakllantiradi."
                        ),
                        "materials": [
                            {"title": "Tipik xatolar ro'yxati", "kind": "TEXT",
                             "body": "1) O₂ CO₂ dan ajraladi deb o'ylash. 2) Qorong'ilik bosqichi faqat "
                                     "kechasi kechadi deb tushunish. 3) O'simlik nafas olmaydi deb hisoblash. "
                                     "Har bir xatoni oldindan bilib, darsga savol tayyorlang."},
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Genetika va irsiyat",
        "slug": "genetika",
        "icon": "🧬",
        "description": "Irsiylanish qonuniyatlari, o'zgaruvchanlik va masala yechish metodikasi.",
        "topics": [
            {
                "title": "Irsiyat asoslari",
                "slug": "irsiyat-asoslari",
                "component": Component.COG,
                "summary": "Mendel qonunlari, genotip va fenotip, monogibrid chatishtirish.",
                "lessons": [
                    {
                        "title": "Mendel qonunlari va asosiy tushunchalar",
                        "slug": "mendel-qonunlari",
                        "duration": 25,
                        "body": (
                            "Gen — belgining irsiy birligi. Allel — bir genning muqobil shakllari. "
                            "GOMOZIGOTA organizmda ikkala allel bir xil (AA yoki aa), GETEROZIGOTAda "
                            "har xil (Aa).\n\n"
                            "GENOTIP — organizmning gen tarkibi; FENOTIP — tashqi ko'rinadigan belgilar "
                            "yig'indisi. Fenotip = genotip + muhit ta'siri.\n\n"
                            "Mendelning I qonuni (bir xillik): sof liniyalarni chatishtirganda birinchi "
                            "avlod bir xil bo'ladi.\n"
                            "Mendelning II qonuni (ajralish): F2 avlodda fenotip 3:1, genotip 1:2:1 "
                            "nisbatda ajraladi.\n"
                            "Mendelning III qonuni (mustaqil taqsimlanish): turli juft belgilar "
                            "bir-biridan mustaqil irsiylanadi (agar turli xromosomalarda joylashgan bo'lsa).\n\n"
                            "METODIK IZOH. Genetik masalani yechishda o'quvchilar odatda javobni topadi, "
                            "lekin YO'LNI tushuntira olmaydi. Shuning uchun har bir masalada 4 qadamni "
                            "majburiy qiling: 1) belgilarni yozish, 2) ota-ona genotipini aniqlash, "
                            "3) Punnett katakchasini tuzish, 4) natijani so'z bilan izohlash. "
                            "To'rtinchi qadam eng muhimi — u \"Tushunaman\" darajasini ta'minlaydi."
                        ),
                        "materials": [
                            {"title": "Punnett katakchasi shabloni", "kind": "TEXT",
                             "body": "Doskada har doim bir xil shaklda chizing — o'quvchida barqaror "
                                     "algoritm shakllanadi. Boshida o'zingiz to'ldiring, keyin qisman, "
                                     "so'ng butunlay o'quvchiga bering (bosqichma-bosqich mustaqillik)."},
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Ekologiya",
        "slug": "ekologiya",
        "icon": "🌍",
        "description": "Ekotizim, trofik munosabatlar va inson ta'siri.",
        "topics": [
            {
                "title": "Ekotizim va trofik zanjirlar",
                "slug": "ekotizim",
                "component": Component.COG,
                "summary": "Produtsent, konsument, redutsent; energiya oqimi va 10% qoidasi.",
                "lessons": [
                    {
                        "title": "Ekotizim tarkibi va energiya oqimi",
                        "slug": "ekotizim-energiya",
                        "duration": 20,
                        "body": (
                            "Ekotizim — tirik organizmlar hamjamiyati va ular yashaydigan jonsiz muhitning "
                            "o'zaro bog'langan yaxlitligi.\n\n"
                            "Funksional guruhlar: PRODUTSENTLAR (yashil o'simliklar) — organik moddani "
                            "sintezlaydi; KONSUMENTLAR (o'txo'r va yirtqich hayvonlar) — tayyor organik "
                            "moddani iste'mol qiladi; REDUTSENTLAR (bakteriya, zamburug') — qoldiqlarni "
                            "mineral moddalarga parchalab, moddalar aylanishini yopadi.\n\n"
                            "Energiya ekotizimda BIR YO'NALISHDA oqadi: quyosh → produtsent → konsument → "
                            "issiqlik. Har bir trofik darajaga o'tishda energiyaning taxminan 90% i nafas "
                            "olish va issiqlikka sarflanadi — bu 10% QOIDASI. Shu sababli trofik zanjir "
                            "odatda 4-5 bo'g'indan oshmaydi.\n\n"
                            "Moddalar esa, energiyadan farqli, AYLANIB yuradi (uglerod, azot, suv sikllari).\n\n"
                            "METODIK IZOH. Bu mavzu \"yodlash\" mavzusiga aylanib qolmasligi uchun mahalliy "
                            "ekotizimdan foydalaning: o'quvchilar o'z hovlisi, ariq bo'yi yoki maktab "
                            "hududidagi zanjirni o'zlari tuzsin. Tanish obyekt mavhum sxemadan ko'ra "
                            "kuchli o'rganish effekti beradi."
                        ),
                        "materials": [
                            {"title": "Amaliy topshiriq g'oyasi", "kind": "TEXT",
                             "body": "O'quvchilarga: \"O'z mahallangizdagi 4 bo'g'inli trofik zanjirni "
                                     "tuzing va agar 2-bo'g'in yo'qolsa nima bo'lishini bashorat qiling\". "
                                     "Bu \"Tahlil qilaman\" darajasidagi topshiriq."},
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Biologiya o'qitish metodikasi",
        "slug": "metodika",
        "icon": "👩‍🏫",
        "description": "Faol ta'lim metodlari, dars loyihalash va baholash tizimi.",
        "topics": [
            {
                "title": "Faol ta'lim metodlari",
                "slug": "faol-talim-metodlari",
                "component": Component.ACT,
                "summary": "Klaster, INSERT, muammoli ta'lim, formativ baholash.",
                "lessons": [
                    {
                        "title": "Metod tanlash: nima uchun aynan shu?",
                        "slug": "metod-tanlash",
                        "duration": 25,
                        "body": (
                            "Metod — maqsadga erishish vositasi. Shuning uchun metod avval tanlanmaydi: "
                            "avval MAQSAD aniqlanadi, keyin unga mos vosita topiladi.\n\n"
                            "KLASTER — tushunchalar o'rtasidagi bog'liqlikni vizual tuzilmaga solish. "
                            "Mavzuni umumlashtirish va oldingi bilimni faollashtirishda kuchli.\n\n"
                            "INSERT — matnni belgilar bilan o'qish: ✓ bilaman, + yangi, − qarama-qarshi, "
                            "? tushunarsiz. Mustaqil o'qishni ongli qiladi.\n\n"
                            "MUAMMOLI TA'LIM — o'quvchi oldiga tayyor javobi yo'q vaziyat qo'yiladi. "
                            "Yadrosi: o'quvchi bilimidagi bo'shliqni O'ZI sezishi kerak.\n\n"
                            "BALIQ SKELETI — muammoning sabab va oqibatlarini tuzilmalashtirish.\n\n"
                            "Maqsad → metod mosligi:\n"
                            "• \"Bilaman\" darajasi → aqliy hujum, klaster\n"
                            "• \"Tushunaman\" → INSERT, o'z so'zi bilan qayta bayon\n"
                            "• \"Qo'llayman\" → amaliy masala, laboratoriya ishi\n"
                            "• \"Tahlil qilaman\" → keys, baliq skeleti, taqqoslash jadvali\n"
                            "• \"Yarataman\" → loyiha, model yasash, o'z topshirig'ini tuzish\n\n"
                            "METODIK IZOH. Boshlovchi o'qituvchining tipik xatosi — metodni \"qiziqarli "
                            "bo'lgani uchun\" tanlash. Har safar o'zingizdan so'rang: bu metod aynan qaysi "
                            "o'quv natijasiga olib boradi? Javob topilmasa — metod noto'g'ri tanlangan."
                        ),
                        "materials": [
                            {"title": "Metod tanlash chek-varag'i", "kind": "TEXT",
                             "body": "1) Dars maqsadi qaysi Bloom darajasida? 2) O'quvchilar bu mavzuda "
                                     "nimani biladi? 3) Menda qancha vaqt va qanday resurs bor? "
                                     "4) Natijani qanday o'lchayman? To'rt savolga javob bergach metod tanlang."},
                        ],
                    },
                    {
                        "title": "Dars maqsadi va baholash mezonlari",
                        "slug": "maqsad-va-baholash",
                        "duration": 20,
                        "body": (
                            "O'lchanadigan dars maqsadi O'QUVCHI harakatini bildiradi va kuzatiladigan "
                            "fe'l bilan yoziladi.\n\n"
                            "Yomon: \"O'quvchilarga fotosintez haqida ma'lumot berish\" — bu o'qituvchi "
                            "faoliyati, o'lchab bo'lmaydi.\n"
                            "Yaxshi: \"Dars oxirida o'quvchi fotosintezning ikki bosqichini farqlay oladi "
                            "va har birining mahsulotini nomlay oladi.\"\n\n"
                            "BAHOLASH TURLARI:\n"
                            "• Diagnostik — dars boshida, oldingi bilimni aniqlash uchun.\n"
                            "• Formativ — jarayonda, o'qitishni to'g'rilash uchun (baho qo'yish shart emas).\n"
                            "• Summativ — yakunda, natijani qayd etish uchun.\n\n"
                            "MEZON — bu \"yaxshi javob nimadan iborat\" degan savolga oldindan berilgan "
                            "javob. Mezonni o'quvchi ish boshlamasdan OLDIN bilishi kerak: shundagina u "
                            "o'zini boshqara oladi va o'z-o'zini baholay boshlaydi.\n\n"
                            "METODIK IZOH. Rubrika tuzganda 3-5 mezondan oshirmang va har bir ball uchun "
                            "kuzatiladigan tavsif yozing (\"2 ball — kamida ikki metod nomlanib, biri "
                            "asoslangan\"). \"Yaxshi bajarilgan\" kabi tavsiflar mezon emas."
                        ),
                        "materials": [
                            {"title": "Maqsad fe'llari", "kind": "TEXT",
                             "body": "Bilaman: nomlaydi, sanaydi, ta'riflaydi. Tushunaman: izohlaydi, "
                                     "o'z so'zi bilan aytadi. Qo'llayman: yechadi, qo'llaydi, ko'rsatadi. "
                                     "Tahlil: taqqoslaydi, ajratadi, sabab topadi. Baholayman: asoslaydi, "
                                     "tanqid qiladi. Yarataman: loyihalaydi, tuzadi, ishlab chiqadi."},
                        ],
                    },
                ],
            },
        ],
    },
]
