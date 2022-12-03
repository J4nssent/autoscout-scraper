
from functools import reduce
import pandas as pd
import numpy as np
import json

# fn = ''
# data = pd.read_csv(fn, encoding="utf-8")
# print("makes:", data.make.unique())

# store as CSV
# file_name = query.replace('/', '').replace('?', '') + '.csv'
# file = open("combined/" + file_name, 'a', newline='')
# writer = csv.writer(file)
# writer.writerow(formatted[0].keys())
# for l in formatted:
#     writer.writerow(l.values())



makes_str = '''{
    "6": {
        "label": "Alfa Romeo",
        "value": 6
    },
    "8": {
        "label": "Aston Martin",
        "value": 8
    },
    "9": {
        "label": "Audi",
        "value": 9
    },
    "11": {
        "label": "Bentley",
        "value": 11
    },
    "13": {
        "label": "BMW",
        "value": 13
    },
    "14": {
        "label": "Alpina",
        "value": 14
    },
    "15": {
        "label": "Bugatti",
        "value": 15
    },
    "16": {
        "label": "Buick",
        "value": 16
    },
    "17": {
        "label": "Cadillac",
        "value": 17
    },
    "19": {
        "label": "Chevrolet",
        "value": 19
    },
    "20": {
        "label": "Chrysler",
        "value": 20
    },
    "21": {
        "label": "Citroen",
        "value": 21
    },
    "22": {
        "label": "Daewoo",
        "value": 22
    },
    "23": {
        "label": "Daihatsu",
        "value": 23
    },
    "27": {
        "label": "Ferrari",
        "value": 27
    },
    "28": {
        "label": "Fiat",
        "value": 28
    },
    "29": {
        "label": "Ford",
        "value": 29
    },
    "31": {
        "label": "Honda",
        "value": 31
    },
    "33": {
        "label": "Hyundai",
        "value": 33
    },
    "35": {
        "label": "Isuzu",
        "value": 35
    },
    "37": {
        "label": "Jaguar",
        "value": 37
    },
    "38": {
        "label": "Jeep",
        "value": 38
    },
    "39": {
        "label": "Kia",
        "value": 39
    },
    "40": {
        "label": "Lada",
        "value": 40
    },
    "41": {
        "label": "Lamborghini",
        "value": 41
    },
    "42": {
        "label": "Lancia",
        "value": 42
    },
    "43": {
        "label": "Lexus",
        "value": 43
    },
    "44": {
        "label": "Lotus",
        "value": 44
    },
    "45": {
        "label": "Maserati",
        "value": 45
    },
    "46": {
        "label": "Mazda",
        "value": 46
    },
    "47": {
        "label": "Mercedes-Benz",
        "value": 47
    },
    "48": {
        "label": "MG",
        "value": 48
    },
    "50": {
        "label": "Mitsubishi",
        "value": 50
    },
    "51": {
        "label": "Morgan",
        "value": 51
    },
    "52": {
        "label": "Nissan",
        "value": 52
    },
    "53": {
        "label": "Oldsmobile",
        "value": 53
    },
    "54": {
        "label": "Opel",
        "value": 54
    },
    "55": {
        "label": "Peugeot",
        "value": 55
    },
    "56": {
        "label": "Pontiac",
        "value": 56
    },
    "57": {
        "label": "Porsche",
        "value": 57
    },
    "60": {
        "label": "Renault",
        "value": 60
    },
    "61": {
        "label": "Rolls-Royce",
        "value": 61
    },
    "62": {
        "label": "Rover",
        "value": 62
    },
    "63": {
        "label": "Saab",
        "value": 63
    },
    "64": {
        "label": "SEAT",
        "value": 64
    },
    "65": {
        "label": "Skoda",
        "value": 65
    },
    "66": {
        "label": "SsangYong",
        "value": 66
    },
    "67": {
        "label": "Subaru",
        "value": 67
    },
    "68": {
        "label": "Suzuki",
        "value": 68
    },
    "70": {
        "label": "Toyota",
        "value": 70
    },
    "71": {
        "label": "TVR",
        "value": 71
    },
    "73": {
        "label": "Volvo",
        "value": 73
    },
    "74": {
        "label": "Volkswagen",
        "value": 74
    },
    "2120": {
        "label": "Triumph",
        "value": 2120
    },
    "2152": {
        "label": "Dodge",
        "value": 2152
    },
    "2153": {
        "label": "GMC",
        "value": 2153
    },
    "14882": {
        "label": "Iveco",
        "value": 14882
    },
    "14890": {
        "label": "Lincoln",
        "value": 14890
    },
    "14979": {
        "label": "AC",
        "value": 14979
    },
    "15525": {
        "label": "smart",
        "value": 15525
    },
    "15629": {
        "label": "Innocenti",
        "value": 15629
    },
    "15633": {
        "label": "Trabant",
        "value": 15633
    },
    "15636": {
        "label": "Proton",
        "value": 15636
    },
    "15641": {
        "label": "Land Rover",
        "value": 15641
    },
    "15643": {
        "label": "Austin",
        "value": 15643
    },
    "15644": {
        "label": "Autobianchi",
        "value": 15644
    },
    "15646": {
        "label": "Puch",
        "value": 15646
    },
    "15670": {
        "label": "Oldtimer",
        "value": 15670
    },
    "15672": {
        "label": "Caravans-Wohnm",
        "value": 15672
    },
    "15674": {
        "label": "HUMMER",
        "value": 15674
    },
    "16253": {
        "label": "Trucks-Lkw",
        "value": 16253
    },
    "16326": {
        "label": "Trailer-Anh�nger",
        "value": 16326
    },
    "16327": {
        "label": "Tata",
        "value": 16327
    },
    "16328": {
        "label": "Overig",
        "value": 16328
    },
    "16333": {
        "label": "DAF",
        "value": 16333
    },
    "16335": {
        "label": "Caterham",
        "value": 16335
    },
    "16336": {
        "label": "Wartburg",
        "value": 16336
    },
    "16337": {
        "label": "Galloper",
        "value": 16337
    },
    "16338": {
        "label": "MINI",
        "value": 16338
    },
    "16339": {
        "label": "Donkervoort",
        "value": 16339
    },
    "16341": {
        "label": "Pagani",
        "value": 16341
    },
    "16348": {
        "label": "Maybach",
        "value": 16348
    },
    "16350": {
        "label": "Piaggio",
        "value": 16350
    },
    "16351": {
        "label": "Wiesmann",
        "value": 16351
    },
    "16352": {
        "label": "Aixam",
        "value": 16352
    },
    "16353": {
        "label": "Ligier",
        "value": 16353
    },
    "16355": {
        "label": "Infiniti",
        "value": 16355
    },
    "16356": {
        "label": "Acura",
        "value": 16356
    },
    "16357": {
        "label": "Chatenet",
        "value": 16357
    },
    "16359": {
        "label": "Mahindra",
        "value": 16359
    },
    "16360": {
        "label": "Dacia",
        "value": 16360
    },
    "16361": {
        "label": "Microcar",
        "value": 16361
    },
    "16367": {
        "label": "Brilliance",
        "value": 16367
    },
    "16369": {
        "label": "Santana",
        "value": 16369
    },
    "16377": {
        "label": "Spyker",
        "value": 16377
    },
    "16379": {
        "label": "BYD",
        "value": 16379
    },
    "16380": {
        "label": "Corvette",
        "value": 16380
    },
    "16382": {
        "label": "Great Wall",
        "value": 16382
    },
    "16383": {
        "label": "DR Motor",
        "value": 16383
    },
    "16384": {
        "label": "Chery",
        "value": 16384
    },
    "16385": {
        "label": "VAZ",
        "value": 16385
    },
    "16386": {
        "label": "GAZ",
        "value": 16386
    },
    "16387": {
        "label": "IZH",
        "value": 16387
    },
    "16388": {
        "label": "Moskvich",
        "value": 16388
    },
    "16389": {
        "label": "UAZ",
        "value": 16389
    },
    "16393": {
        "label": "Lifan",
        "value": 16393
    },
    "16394": {
        "label": "ZAZ",
        "value": 16394
    },
    "16396": {
        "label": "Abarth",
        "value": 16396
    },
    "16397": {
        "label": "Daimler",
        "value": 16397
    },
    "16398": {
        "label": "Reliant",
        "value": 16398
    },
    "16399": {
        "label": "Melex",
        "value": 16399
    },
    "16400": {
        "label": "Bedford",
        "value": 16400
    },
    "16401": {
        "label": "Changhe",
        "value": 16401
    },
    "16402": {
        "label": "Iso Rivolta",
        "value": 16402
    },
    "16403": {
        "label": "GEM",
        "value": 16403
    },
    "16404": {
        "label": "Tasso",
        "value": 16404
    },
    "16407": {
        "label": "Casalini",
        "value": 16407
    },
    "16408": {
        "label": "Zastava",
        "value": 16408
    },
    "16409": {
        "label": "Grecav",
        "value": 16409
    },
    "16410": {
        "label": "Martin Motors",
        "value": 16410
    },
    "16411": {
        "label": "CityEL",
        "value": 16411
    },
    "16415": {
        "label": "DS Automobiles",
        "value": 16415
    },
    "16416": {
        "label": "Bellier",
        "value": 16416
    },
    "16418": {
        "label": "Bollor�",
        "value": 16418
    },
    "16419": {
        "label": "Ariel Motor",
        "value": 16419
    },
    "16420": {
        "label": "Town Life",
        "value": 16420
    },
    "16421": {
        "label": "Giotti Victoria",
        "value": 16421
    },
    "16422": {
        "label": "VEM",
        "value": 16422
    },
    "16423": {
        "label": "De la Chapelle",
        "value": 16423
    },
    "16424": {
        "label": "Borgward",
        "value": 16424
    },
    "16426": {
        "label": "LDV",
        "value": 16426
    },
    "16427": {
        "label": "Artega",
        "value": 16427
    },
    "16429": {
        "label": "ACM",
        "value": 16429
    },
    "16431": {
        "label": "Aspid",
        "value": 16431
    },
    "16434": {
        "label": "Dangel",
        "value": 16434
    },
    "16435": {
        "label": "Mansory",
        "value": 16435
    },
    "16436": {
        "label": "Estrima",
        "value": 16436
    },
    "50060": {
        "label": "KTM",
        "value": 50060
    },
    "50083": {
        "label": "PGO",
        "value": 50083
    },
    "50111": {
        "label": "NSU",
        "value": 50111
    },
    "51512": {
        "label": "Haima",
        "value": 51512
    },
    "51513": {
        "label": "Westfield",
        "value": 51513
    },
    "51519": {
        "label": "McLaren",
        "value": 51519
    },
    "51520": {
        "label": "Tesla",
        "value": 51520
    },
    "51534": {
        "label": "Hamann",
        "value": 51534
    },
    "51535": {
        "label": "TECHART",
        "value": 51535
    },
    "51536": {
        "label": "Ruf",
        "value": 51536
    },
    "51538": {
        "label": "SpeedArt",
        "value": 51538
    },
    "51539": {
        "label": "9ff",
        "value": 51539
    },
    "51540": {
        "label": "GEMBALLA",
        "value": 51540
    },
    "51542": {
        "label": "Gac Gonow",
        "value": 51542
    },
    "51543": {
        "label": "FISKER",
        "value": 51543
    },
    "51545": {
        "label": "Amphicar",
        "value": 51545
    },
    "51551": {
        "label": "Talbot",
        "value": 51551
    },
    "51552": {
        "label": "Dutton",
        "value": 51552
    },
    "51553": {
        "label": "Panther Westwinds",
        "value": 51553
    },
    "51554": {
        "label": "MP Lafer",
        "value": 51554
    },
    "51557": {
        "label": "Tazzari EV",
        "value": 51557
    },
    "51766": {
        "label": "Minauto",
        "value": 51766
    },
    "51767": {
        "label": "Hurtan",
        "value": 51767
    },
    "51770": {
        "label": "Plymouth",
        "value": 51770
    },
    "51773": {
        "label": "DFSK",
        "value": 51773
    },
    "51774": {
        "label": "Baic",
        "value": 51774
    },
    "51779": {
        "label": "De Tomaso",
        "value": 51779
    },
    "51780": {
        "label": "MAN",
        "value": 51780
    },
    "51781": {
        "label": "Koenigsegg",
        "value": 51781
    },
    "51782": {
        "label": "Mitsuoka",
        "value": 51782
    },
    "51788": {
        "label": "MPM Motors",
        "value": 51788
    },
    "51791": {
        "label": "Gillet",
        "value": 51791
    },
    "51793": {
        "label": "RAM",
        "value": 51793
    },
    "51794": {
        "label": "e.GO",
        "value": 51794
    },
    "51795": {
        "label": "StreetScooter",
        "value": 51795
    },
    "51796": {
        "label": "Alpine",
        "value": 51796
    },
    "51798": {
        "label": "Zhidou",
        "value": 51798
    },
    "51800": {
        "label": "Shuanghuan",
        "value": 51800
    },
    "51802": {
        "label": "Cupra",
        "value": 51802
    },
    "51803": {
        "label": "Maxus",
        "value": 51803
    },
    "51807": {
        "label": "Zotye",
        "value": 51807
    },
    "51809": {
        "label": "Vanderhall",
        "value": 51809
    },
    "51812": {
        "label": "Regis",
        "value": 51812
    },
    "51813": {
        "label": "Goupil",
        "value": 51813
    },
    "51816": {
        "label": "Haval",
        "value": 51816
    },
    "51817": {
        "label": "Polestar",
        "value": 51817
    },
    "51827": {
        "label": "Sevic",
        "value": 51827
    },
    "51831": {
        "label": "EVO",
        "value": 51831
    },
    "51833": {
        "label": "Studebaker",
        "value": 51833
    },
    "51834": {
        "label": "Mercury",
        "value": 51834
    },
    "51835": {
        "label": "Econelo",
        "value": 51835
    },
    "51836": {
        "label": "Vanden Plas",
        "value": 51836
    },
    "51837": {
        "label": "Giana",
        "value": 51837
    },
    "51839": {
        "label": "Selvo",
        "value": 51839
    },
    "51849": {
        "label": "JAC",
        "value": 51849
    },
    "51852": {
        "label": "Wenckstern",
        "value": 51852
    },
    "51854": {
        "label": "LEVC",
        "value": 51854
    },
    "51859": {
        "label": "Delorean",
        "value": 51859
    },
    "51860": {
        "label": "XEV",
        "value": 51860
    },
    "51861": {
        "label": "Seres",
        "value": 51861
    },
    "51866": {
        "label": "Segway",
        "value": 51866
    },
    "51869": {
        "label": "XBus",
        "value": 51869
    },
    "51872": {
        "label": "Aiways",
        "value": 51872
    },
    "51873": {
        "label": "Weltmeister",
        "value": 51873
    },
    "51874": {
        "label": "Embuggy",
        "value": 51874
    },
    "51875": {
        "label": "Karma",
        "value": 51875
    },
    "51880": {
        "label": "Elaris",
        "value": 51880
    },
    "51881": {
        "label": "Holden",
        "value": 51881
    },
    "51883": {
        "label": "Linzda",
        "value": 51883
    },
    "51885": {
        "label": "Genesis",
        "value": 51885
    },
    "51895": {
        "label": "Bristol",
        "value": 51895
    },
    "51896": {
        "label": "Shelby",
        "value": 51896
    },
    "51897": {
        "label": "Militem",
        "value": 51897
    },
    "51900": {
        "label": "Boldmen",
        "value": 51900
    },
    "51901": {
        "label": "Austin-Healey",
        "value": 51901
    },
    "51902": {
        "label": "Mega",
        "value": 51902
    },
    "51903": {
        "label": "Minari",
        "value": 51903
    },
    "51904": {
        "label": "BAIC",
        "value": 51904
    },
    "51905": {
        "label": "Edran",
        "value": 51905
    },
    "51906": {
        "label": "Martin",
        "value": 51906
    },
    "51907": {
        "label": "Gappy",
        "value": 51907
    },
    "51908": {
        "label": "Lorinser",
        "value": 51908
    },
    "51909": {
        "label": "Singer",
        "value": 51909
    },
    "51910": {
        "label": "Jensen",
        "value": 51910
    },
    "51912": {
        "label": "Carver",
        "value": 51912
    },
    "51913": {
        "label": "SGS",
        "value": 51913
    },
    "51914": {
        "label": "Lynk \u0026 Co",
        "value": 51914
    },
    "51915": {
        "label": "VinFast",
        "value": 51915
    },
    "51917": {
        "label": "Alba Mobility",
        "value": 51917
    },
    "51918": {
        "label": "Angelelli Automobili",
        "value": 51918
    },
    "51919": {
        "label": "Evetta",
        "value": 51919
    },
    "51920": {
        "label": "Devinci Cars",
        "value": 51920
    },
    "51921": {
        "label": "Lucid",
        "value": 51921
    },
    "51924": {
        "label": "EMC",
        "value": 51924
    },
    "51925": {
        "label": "Ineos",
        "value": 51925
    },
    "51926": {
        "label": "GTA",
        "value": 51926
    }
}'''
makes = json.loads(makes_str)
formatted = [e['label'] for e in makes.values()]
print(formatted)
