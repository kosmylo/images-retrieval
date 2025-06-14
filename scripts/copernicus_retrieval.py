import requests
import os
import json
import logging
from datetime import datetime

# Base URL for ArcGIS ImageServer
BASE_URL = "https://image.discomap.eea.europa.eu/arcgis/rest/services/GioLand/VHR_2021_LAEA/ImageServer/exportImage"

output_dir = "copernicus_images"
os.makedirs(output_dir, exist_ok=True)

headers = {
    "User-Agent": "mAiEnergyBot/1.0 (kosmylo@gmail.com; downloading Copernicus satellite images for research)"
}

# Define EU regions with bounding boxes (LAEA projection)
regions = [
  {
    "name": "Austria",
    "bbox": [4284800, 2584400, 4843900, 2904000],
    "subregions": [
      {"name": "Vienna",         "bbox": [4780900, 2797500, 4808300, 2822800]},  
      {"name": "Lower Austria",  "bbox": [4657000, 2711000, 4837300, 2903400]},  
      {"name": "Upper Austria",  "bbox": [4528400, 2709100, 4687700, 2863500]},  
      {"name": "Styria",         "bbox": [4594000, 2617000, 4783000, 2766000]},  
      {"name": "Tyrol",          "bbox": [4328500, 2615300, 4543500, 2741000]},  
      {"name": "Carinthia",      "bbox": [4525000, 2588000, 4706000, 2682000]},  
      {"name": "Salzburg",       "bbox": [4479000, 2650000, 4619000, 2778000]},  
      {"name": "Vorarlberg",     "bbox": [4285000, 2636000, 4339000, 2721000]},  
      {"name": "Burgenland",     "bbox": [4778000, 2653000, 4854000, 2805000]},  
      {"name": "Graz Metro",     "bbox": [4727700, 2670000, 4740700, 2684700]}    
    ]
  },
  {
    "name": "Belgium",
    "bbox": [3770000, 2960000, 4072000, 3167000],
    "subregions": [
      {"name": "Brussels",         "bbox": [3915400, 3088400, 3933400, 3103800]},  
      {"name": "Flanders",         "bbox": [3792000, 3092000, 4036500, 3162400]},  
      {"name": "Wallonia",         "bbox": [3760000, 2960000, 4000000, 3180000]},  
      {"name": "Antwerp",          "bbox": [3912300, 3113900, 3992300, 3165600]},  
      {"name": "Ghent",            "bbox": [3878500, 3105000, 3920000, 3140000]},  
      {"name": "Liège",            "bbox": [3990000, 3070000, 4030000, 3140000]},  
      {"name": "Charleroi",        "bbox": [3865000, 3033000, 3905000, 3095000]},  
      {"name": "Namur",            "bbox": [3800000, 3000000, 3840000, 3070000]},  
      {"name": "Limburg Region",   "bbox": [3945000, 3120000, 4000000, 3180000]},  
      {"name": "Brabant Wallon",   "bbox": [3810000, 3025000, 3850000, 3095000]}  
    ]
  },
  {
    "name": "Bulgaria",
    "bbox": [5356000, 2099000, 5816000, 2536000],
    "subregions": [
      {"name": "Sofia",           "bbox": [5409500, 2260000, 5450000, 2323000]},  
      {"name": "Plovdiv",         "bbox": [5535500, 2195000, 5575000, 2235000]},  
      {"name": "Varna",           "bbox": [5765000, 2360000, 5805000, 2400000]},  
      {"name": "Burgas",          "bbox": [5685000, 2225000, 5725000, 2265000]},  
      {"name": "Dobrich region",  "bbox": [5860000, 2400000, 5910000, 2440000]},  
      {"name": "Veliko Tarnovo",  "bbox": [5590000, 2380000, 5630000, 2420000]},  
      {"name": "Ruse",            "bbox": [5725000, 2420000, 5760000, 2460000]},  
      {"name": "Stara Zagora",    "bbox": [5630000, 2170000, 5670000, 2210000]},  
      {"name": "Blagoevgrad",     "bbox": [5480000, 2150000, 5520000, 2190000]},  
      {"name": "Botevgrad",       "bbox": [5540000, 2280000, 5580000, 2320000]}  
    ]
  },
  {
    "name": "Croatia",
    "bbox": [4587000, 2124000, 5044000, 2651000],
    "subregions": [
      {"name": "Zagreb",      "bbox": [4790000, 2570000, 4830000, 2610000]},  
      {"name": "Istria",      "bbox": [4640000, 2500000, 4700000, 2570000]},  
      {"name": "Split",       "bbox": [4900000, 2380000, 4940000, 2425000]},  
      {"name": "Dalmatia",    "bbox": [4850000, 2300000, 4980000, 2450000]},  
      {"name": "Slavonia",    "bbox": [4970000, 2620000, 5060000, 2720000]},  
      {"name": "Kvarner",     "bbox": [4730000, 2420000, 4790000, 2500000]},  
      {"name": "Rijeka",      "bbox": [4725000, 2460000, 4765000, 2515000]},  
      {"name": "Osijek",      "bbox": [5020000, 2660000, 5060000, 2700000]},  
      {"name": "Dubrovnik",   "bbox": [5000000, 2200000, 5040000, 2240000]},  
      {"name": "Zadar",       "bbox": [4860000, 2390000, 4900000, 2430000]}  
    ]
  },
  {
    "name": "Cyprus",
    "bbox": [6357000, 1572000, 6527000, 1761000],
    "subregions": [
      {"name": "Nicosia",                 "bbox": [6430000, 1640000, 6470000, 1670000]},  
      {"name": "Limassol",                "bbox": [6425000, 1550000, 6460000, 1580000]},  
      {"name": "Larnaca",                 "bbox": [6485000, 1530000, 6525000, 1560000]},  
      {"name": "Paphos",                  "bbox": [6350000, 1490000, 6390000, 1525000]},  
      {"name": "Famagusta",               "bbox": [6500000, 1630000, 6540000, 1665000]},  
      {"name": "Renewables Zone East",    "bbox": [6480000, 1590000, 6520000, 1620000]},  
      {"name": "Renewables Zone West",    "bbox": [6400000, 1550000, 6440000, 1590000]},  
      {"name": "NIC district",            "bbox": [6430000, 1620000, 6470000, 1650000]},  
      {"name": "LPRO industrial",         "bbox": [6460000, 1500000, 6500000, 1530000]},  
      {"name": "Limassol port area",      "bbox": [6425000, 1550000, 6465000, 1580000]}  
    ]
  },
  {
    "name": "Czech Republic",
    "bbox": [4475000, 2828000, 4941000, 3143000],
    "subregions": [
      {"name": "Prague",           "bbox": [4550000, 2920000, 4590000, 2960000]},  
      {"name": "Central Bohemia",  "bbox": [4510000, 2900000, 4610000, 3000000]},  
      {"name": "Moravia",          "bbox": [4630000, 2840000, 4800000, 3050000]},  
      {"name": "Brno",             "bbox": [4640000, 2870000, 4680000, 2900000]},  
      {"name": "Ostrava",          "bbox": [4710000, 2890000, 4750000, 2930000]},  
      {"name": "Pilsen",           "bbox": [4470000, 2870000, 4510000, 2910000]},  
      {"name": "Ústí nad Labem",   "bbox": [4440000, 2960000, 4480000, 3000000]},  
      {"name": "Liberec",          "bbox": [4500000, 3000000, 4540000, 3040000]},  
      {"name": "Karlovy Vary",     "bbox": [4450000, 2890000, 4490000, 2930000]},  
      {"name": "South Moravian",   "bbox": [4620000, 2850000, 4780000, 3060000]}  
    ]
  },
  {
    "name": "Denmark",
    "bbox": [4196300, 3496400, 4628200, 3861200],
    "subregions": [
      {"name": "Copenhagen",   "bbox": [4438800, 3544000, 4641400, 3681100]},  
      {"name": "Zealand",      "bbox": [4340000, 3565000, 4480000, 3725000]},  
      {"name": "Funen",        "bbox": [4160000, 3540000, 4260000, 3640000]},  
      {"name": "Jutland",      "bbox": [3800000, 3600000, 4200000, 4050000]},  
      {"name": "Aarhus",       "bbox": [4040000, 3800000, 4080000, 3840000]},  
      {"name": "Odense",       "bbox": [4000000, 3770000, 4040000, 3810000]},  
      {"name": "Aalborg",      "bbox": [3950000, 3920000, 3990000, 3960000]},  
      {"name": "Fredericia",   "bbox": [4020000, 3750000, 4050000, 3780000]},  
      {"name": "Esbjerg",      "bbox": [3970000, 3750000, 4010000, 3790000]},  
      {"name": "Bornholm",     "bbox": [4320000, 3600000, 4380000, 3650000]}  
    ]
  },
  {
    "name": "Estonia",
    "bbox": [5000000, 3877000, 5329000, 4224000],
    "subregions": [
      {"name": "Tallinn",      "bbox": [5170000, 4390000, 5210000, 4430000]},  
      {"name": "Tartu",        "bbox": [5300000, 4250000, 5340000, 4290000]},  
      {"name": "Narva",        "bbox": [5320000, 4400000, 5360000, 4440000]},  
      {"name": "Pärnu",        "bbox": [5280000, 4230000, 5320000, 4270000]},  
      {"name": "Saaremaa",     "bbox": [5130000, 4180000, 5190000, 4230000]},  
      {"name": "Harju County", "bbox": [5160000, 4380000, 5220000, 4450000]},  
      {"name": "Lääne-Viru",   "bbox": [5260000, 4360000, 5300000, 4400000]},  
      {"name": "Tartu County", "bbox": [5280000, 4240000, 5340000, 4300000]},  
      {"name": "Põlva",        "bbox": [5320000, 4200000, 5350000, 4235000]},  
      {"name": "Ida-Viru",     "bbox": [5310000, 4360000, 5350000, 4420000]}  
    ]
  },
  {
    "name": "Finland",
    "bbox": [4835000, 4072000, 5136000, 5347000],
    "subregions": [
      {"name": "Helsinki",    "bbox": [5144800, 4590000, 5185000, 4630000]},  
      {"name": "Espoo",       "bbox": [5135000, 4590000, 5175000, 4625000]},  
      {"name": "Tampere",     "bbox": [5000000, 4570000, 5040000, 4610000]},  
      {"name": "Turku",       "bbox": [4930000, 4530000, 4970000, 4570000]},  
      {"name": "Oulu",        "bbox": [5060000, 5030000, 5100000, 5070000]},  
      {"name": "Lahti",       "bbox": [5090000, 4570000, 5130000, 4610000]},  
      {"name": "Kuopio",      "bbox": [5240000, 4900000, 5280000, 4940000]},  
      {"name": "Jyväskylä",   "bbox": [5060000, 4720000, 5100000, 4760000]},  
      {"name": "Rovaniemi",   "bbox": [4930000, 5290000, 4970000, 5330000]},  
      {"name": "Vaasa",       "bbox": [4835000, 4870000, 4875000, 4910000]}  
    ]
  },
  {
    "name": "France",
    "bbox": [3030000, 2150000, 4312000, 3129000],
    "subregions": [
      {"name": "Paris",                       "bbox": [3590000, 2980000, 3630000, 3020000]},  
      {"name": "Île‑de‑France",               "bbox": [3550000, 2940000, 3650000, 3040000]},  
      {"name": "Auvergne Rhône-Alpes",        "bbox": [3580000, 2670000, 3860000, 2950000]},  
      {"name": "Occitanie",                  "bbox": [3410000, 2470000, 3720000, 2760000]},  
      {"name": "Provence-Alpes-Côte d’Azur",  "bbox": [3770000, 2270000, 4030000, 2580000]},  
      {"name": "Brittany",                   "bbox": [3160000, 2860000, 3430000, 3140000]},  
      {"name": "Hauts‑de‑France",            "bbox": [3530000, 3090000, 3780000, 3290000]},  
      {"name": "Grand Est",                  "bbox": [3660000, 2920000, 3970000, 3180000]},  
      {"name": "Normandy",                   "bbox": [3370000, 2980000, 3660000, 3220000]},  
      {"name": "New Aquitaine",              "bbox": [3210000, 2660000, 3520000, 2960000]}  
    ]
  },
  {
    "name": "Germany",
    "bbox": [4008000, 2692000, 4643000, 3567000],
    "subregions": [
      {"name": "Berlin",             "bbox": [4545000, 3272000, 4560000, 3295000]},  
      {"name": "North Rhine-Westphalia", "bbox": [4026800, 3031700, 4284500, 3269300]},  
      {"name": "Bavaria",            "bbox": [4340000, 3070000, 4730000, 3450000]},  
      {"name": "Baden-Württemberg",  "bbox": [4190000, 2980000, 4500000, 3300000]},  
      {"name": "Hesse",             "bbox": [4310000, 3120000, 4490000, 3290000]},  
      {"name": "Hamburg",           "bbox": [4430000, 3400000, 4460000, 3435000]},  
      {"name": "Lower Saxony",      "bbox": [4170000, 3300000, 4460000, 3530000]},  
      {"name": "Saxony",            "bbox": [4570000, 3180000, 4810000, 3420000]},  
      {"name": "Thuringia",         "bbox": [4450000, 3110000, 4630000, 3280000]},  
      {"name": "Brandenburg",       "bbox": [4560000, 3280000, 4800000, 3480000]}  
    ]
  },
  {
    "name": "Greece",
    "bbox": [5175000, 1346000, 6040000, 2287000],
    "subregions": [
      {"name": "Athens",             "bbox": [5526000, 1764000, 5560000, 1798000]},  
      {"name": "Thessaloniki",       "bbox": [5430000, 1980000, 5470000, 2020000]},  
      {"name": "Crete",              "bbox": [5520000, 1500000, 5780000, 1670000]},  
      {"name": "Piraeus Port",       "bbox": [5520000, 1740000, 5550000, 1770000]},  
      {"name": "Peloponnese",        "bbox": [5360000, 1620000, 5530000, 1790000]},  
      {"name": "Western Macedonia",  "bbox": [5280000, 1920000, 5450000, 2090000]},  
      {"name": "Central Macedonia",  "bbox": [5430000, 1940000, 5590000, 2120000]},  
      {"name": "Epirus",             "bbox": [5190000, 1900000, 5370000, 2080000]},  
      {"name": "Attica Region",      "bbox": [5500000, 1740000, 5570000, 1830000]},  
      {"name": "Aegean Islands",     "bbox": [5650000, 1570000, 5830000, 1830000]}  
    ]
  },
  {
    "name": "Hungary",
    "bbox": [4796000, 2533000, 5268000, 2914000],
    "subregions": [
      {"name": "Budapest",             "bbox": [5400000, 2790000, 5440000, 2830000]},  
      {"name": "Central Hungary",      "bbox": [5380000, 2770000, 5460000, 2850000]},  
      {"name": "Transdanubia",         "bbox": [5300000, 2730000, 5580000, 2970000]},  
      {"name": "Northern Hungary",     "bbox": [5400000, 2900000, 5550000, 3050000]},  
      {"name": "Southern Great Plain", "bbox": [5480000, 2600000, 5700000, 2850000]},  
      {"name": "Western Transdanubia", "bbox": [5300000, 2800000, 5550000, 3000000]},  
      {"name": "Lake Balaton",         "bbox": [5460000, 2740000, 5530000, 2800000]},  
      {"name": "Győr city",            "bbox": [5405000, 2870000, 5435000, 2905000]},  
      {"name": "Pécs city",            "bbox": [5550000, 2710000, 5580000, 2745000]},  
      {"name": "Debrecen",             "bbox": [5565000, 2860000, 5595000, 2895000]}  
    ]
  },
  {
    "name": "Ireland",
    "bbox": [2876000, 3333000, 3344000, 3722000],
    "subregions": [
      {"name": "Dublin",          "bbox": [2780000, 3770000, 2820000, 3810000]},  
      {"name": "Cork",            "bbox": [2690000, 3640000, 2730000, 3680000]},  
      {"name": "Galway",          "bbox": [2670000, 3770000, 2710000, 3820000]},  
      {"name": "Limerick",        "bbox": [2710000, 3690000, 2750000, 3730000]},  
      {"name": "Waterford",       "bbox": [2750000, 3610000, 2790000, 3650000]},  
      {"name": "Belfast",         "bbox": [2795000, 3870000, 2835000, 3915000]},  
      {"name": "Midwest Region",  "bbox": [2650000, 3720000, 2790000, 3890000]},  
      {"name": "Southwest Region", "bbox": [2650000, 3600000, 2800000, 3780000]},  
      {"name": "Dublin Metro",    "bbox": [2790000, 3780000, 2810000, 3805000]},  
      {"name": "Shannon Estuary", "bbox": [2700000, 3650000, 2730000, 3690000]}  
    ]
  },
  {
    "name": "Italy",
    "bbox": [4011000, 1366000, 4987000, 2704000],
    "subregions": [
      {"name": "Rome",             "bbox": [4550000, 1860000, 4590000, 1900000]},  
      {"name": "Milan",            "bbox": [4490000, 1920000, 4530000, 1960000]},  
      {"name": "Lombardy",         "bbox": [4440000, 1870000, 4580000, 2020000]},  
      {"name": "Veneto",           "bbox": [4520000, 1900000, 4660000, 2040000]},  
      {"name": "Tuscany",          "bbox": [4380000, 1790000, 4520000, 1940000]},  
      {"name": "Sicily",           "bbox": [4440000, 1360000, 4740000, 1600000]},  
      {"name": "Naples",           "bbox": [4550000, 1760000, 4590000, 1800000]},  
      {"name": "Emilia‑Romagna",   "bbox": [4490000, 1940000, 4630000, 2100000]},  
      {"name": "Puglia",           "bbox": [4620000, 1650000, 4810000, 1850000]},  
      {"name": "Campania",         "bbox": [4540000, 1720000, 4680000, 1880000]}  
    ]
  },
  {
    "name": "Latvia",
    "bbox": [4989000, 3668000, 5386000, 4025000],
    "subregions": [
      {"name": "Riga",         "bbox": [5470000, 4040000, 5510000, 4080000]},  
      {"name": "Latgale",      "bbox": [5570000, 3950000, 5690000, 4150000]},  
      {"name": "Kurzeme",      "bbox": [5190000, 3930000, 5470000, 4150000]},  
      {"name": "Vidzeme",      "bbox": [5400000, 4050000, 5600000, 4250000]},  
      {"name": "Zemgale",      "bbox": [5350000, 3980000, 5550000, 4200000]},  
      {"name": "Jelgava",      "bbox": [5430000, 4000000, 5460000, 4030000]},  
      {"name": "Daugavpils",   "bbox": [5520000, 3960000, 5550000, 3990000]},  
      {"name": "Ventspils",    "bbox": [5230000, 4050000, 5260000, 4080000]},  
      {"name": "Liepāja",      "bbox": [5230000, 4000000, 5260000, 4030000]},  
      {"name": "Valmiera",     "bbox": [5440000, 4100000, 5480000, 4140000]}  
    ]
  },
  {
    "name": "Lithuania",
    "bbox": [5018000, 3472000, 5349000, 3827000],
    "subregions": [
      {"name": "Vilnius",      "bbox": [5250000, 3810000, 5290000, 3850000]},  
      {"name": "Kaunas",       "bbox": [5200000, 3790000, 5240000, 3830000]},  
      {"name": "Klaipėda",     "bbox": [5150000, 3740000, 5190000, 3780000]},  
      {"name": "Šiauliai",     "bbox": [5230000, 3840000, 5270000, 3880000]},  
      {"name": "Panevėžys",    "bbox": [5210000, 3830000, 5250000, 3870000]},  
      {"name": "Alytus",       "bbox": [5220000, 3760000, 5260000, 3800000]},  
      {"name": "Marijampolė",  "bbox": [5210000, 3770000, 5250000, 3810000]},  
      {"name": "Telšiai",      "bbox": [5170000, 3860000, 5210000, 3900000]},  
      {"name": "Utena",        "bbox": [5270000, 3820000, 5310000, 3860000]},  
      {"name": "Visaginas",    "bbox": [5300000, 3840000, 5340000, 3880000]}  
    ]
  },
  {
    "name": "Luxembourg",
    "bbox": [3956000, 2944000, 4040000, 3044000],
    "subregions": [
      {"name": "Luxembourg City",  "bbox": [3970000, 3030000, 3990000, 3050000]},  
      {"name": "South Luxembourg", "bbox": [3956000, 3000000, 3990000, 3040000]},  
      {"name": "North Luxembourg", "bbox": [3980000, 3040000, 4020000, 3080000]},  
      {"name": "Région de l'Est",  "bbox": [3990000, 3010000, 4025000, 3050000]},  
      {"name": "Esch-sur-Alzette", "bbox": [3965000, 2990000, 3990000, 3015000]},  
      {"name": "Clervaux",         "bbox": [3980000, 3060000, 4010000, 3085000]},  
      {"name": "Diekirch",         "bbox": [3975000, 3040000, 4005000, 3070000]},  
      {"name": "Grevenmacher",     "bbox": [3995000, 3020000, 4030000, 3045000]},  
      {"name": "Mersch",           "bbox": [3980000, 3035000, 4005000, 3065000]},  
      {"name": "Remich",           "bbox": [3995000, 3005000, 4020000, 3030000]}  
    ]
  },
  {
    "name": "Malta",
    "bbox": [4680000, 1403000, 4759000, 1483000],
    "subregions": [
      {"name": "Valletta",         "bbox": [4705000, 1460000, 4715000, 1470000]},  
      {"name": "Marsaxlokk",       "bbox": [4710000, 1430000, 4720000, 1440000]},  
      {"name": "Birkirkara",       "bbox": [4700000, 1465000, 4715000, 1480000]},  
      {"name": "Floriana",         "bbox": [4705000, 1460000, 4710000, 1465000]},  
      {"name": "Zebbug",           "bbox": [4695000, 1460000, 4705000, 1470000]},  
      {"name": "Rabat",            "bbox": [4690000, 1470000, 4700000, 1480000]},  
      {"name": "Gozo",             "bbox": [4675000, 1435000, 4695000, 1455000]},  
      {"name": "Mdina",            "bbox": [4695000, 1470000, 4700000, 1475000]},  
      {"name": "Sliema",           "bbox": [4705000, 1465000, 4710000, 1475000]},  
      {"name": "Bżar Solar Park",  "bbox": [4715000, 1450000, 4720000, 1460000]}  
    ]
  },
  {
    "name": "Netherlands",
    "bbox": [3849000, 3092000, 4139000, 3406000],
    "subregions": [
      {"name": "Amsterdam",         "bbox": [4075000, 3265000, 4115000, 3305000]},  
      {"name": "Rotterdam",         "bbox": [4040000, 3210000, 4080000, 3250000]},  
      {"name": "The Hague",         "bbox": [4020000, 3210000, 4060000, 3250000]},  
      {"name": "Utrecht",           "bbox": [4060000, 3240000, 4100000, 3280000]},  
      {"name": "Eindhoven",         "bbox": [4110000, 3130000, 4150000, 3170000]},  
      {"name": "Groningen",         "bbox": [4010000, 3320000, 4050000, 3360000]},  
      {"name": "Maastricht",        "bbox": [4075000, 3110000, 4115000, 3150000]},  
      {"name": "Leeuwarden",        "bbox": [3960000, 3370000, 4000000, 3410000]},  
      {"name": "Almere",            "bbox": [4095000, 3260000, 4125000, 3290000]},  
      {"name": "Wind Farm North Sea","bbox": [3680000, 3430000, 3800000, 3550000]}  
    ]
  },
  {
    "name": "Poland",
    "bbox": [4622000, 2884000, 5220000, 3637000],
    "subregions": [
      {"name": "Warsaw",             "bbox": [5470000, 3420000, 5510000, 3460000]},  
      {"name": "Kuyavia-Pomerania",  "bbox": [5290000, 3370000, 5490000, 3550000]},  
      {"name": "Lower Silesia",      "bbox": [5090000, 3240000, 5340000, 3460000]},  
      {"name": "Lodz",               "bbox": [5320000, 3320000, 5360000, 3360000]},  
      {"name": "Silesia",            "bbox": [5320000, 3260000, 5460000, 3400000]},  
      {"name": "Pomerania",          "bbox": [5250000, 3590000, 5400000, 3700000]},  
      {"name": "Poznan",             "bbox": [5120000, 3420000, 5160000, 3460000]},  
      {"name": "Gdansk",             "bbox": [5370000, 3660000, 5410000, 3700000]},  
      {"name": "Katowice",           "bbox": [5325000, 3240000, 5365000, 3280000]},  
      {"name": "Zielona Góra",       "bbox": [5020000, 3390000, 5060000, 3430000]}  
    ]
  },
  {
    "name": "Portugal",
    "bbox": [2585000, 1752000, 2990000, 2261000],
    "subregions": [
      {"name": "Lisbon",     "bbox": [2800000, 1990000, 2830000, 2020000]},  
      {"name": "Porto",      "bbox": [2750000, 2040000, 2780000, 2070000]},  
      {"name": "Alentejo",   "bbox": [2690000, 1900000, 2890000, 2180000]},  
      {"name": "Algarve",    "bbox": [2730000, 1780000, 2880000, 2020000]},  
      {"name": "Madeira",    "bbox": [1705000, 1265000, 2013000, 1540000]},  
      {"name": "Azores",     "bbox": [ 814000, 2526000, 1462000, 2536000]},  
      {"name": "Coimbra",    "bbox": [2770000, 1980000, 2790000, 2005000]},  
      {"name": "Faro",       "bbox": [2790000, 1750000, 2815000, 1765000]},  
      {"name": "Aveiro",     "bbox": [2760000, 2020000, 2785000, 2035000]},  
      {"name": "Braga",      "bbox": [2740000, 2070000, 2765000, 2095000]}  
    ]
  },
  {
    "name": "Romania",
    "bbox": [5148000, 2335000, 6500000, 3150000],
    "subregions": [
      {"name": "Bucharest",       "bbox": [6050000, 2785000, 6090000, 2825000]},  
      {"name": "Transylvania",    "bbox": [5700000, 2730000, 6000000, 3030000]},  
      {"name": "Moldova Region",  "bbox": [6000000, 2800000, 6200000, 3050000]},  
      {"name": "Wallachia",       "bbox": [5800000, 2700000, 6100000, 2950000]},  
      {"name": "Oltenia",         "bbox": [5700000, 2650000, 5900000, 2900000]},  
      {"name": "Dobrogea",        "bbox": [6100000, 2750000, 6300000, 3000000]},  
      {"name": "Cluj-Napoca",     "bbox": [5580000, 2860000, 5620000, 2900000]},  
      {"name": "Timișoara",       "bbox": [5460000, 2740000, 5500000, 2780000]},  
      {"name": "Iași",            "bbox": [6140000, 2860000, 6180000, 2900000]},  
      {"name": "Craiova",         "bbox": [5620000, 2680000, 5660000, 2720000]}  
    ]
  },
  {
    "name": "Slovakia",
    "bbox": [4833000, 2758000, 5225000, 3023000],
    "subregions": [
      {"name": "Bratislava",      "bbox": [4980000, 2890000, 5020000, 2930000]},  
      {"name": "Košice",          "bbox": [5320000, 2920000, 5360000, 2960000]},  
      {"name": "Prešov",          "bbox": [5300000, 2970000, 5340000, 3010000]},  
      {"name": "Trnava region",   "bbox": [4890000, 2870000, 4930000, 2910000]},  
      {"name": "Žilina region",   "bbox": [5020000, 2930000, 5060000, 2970000]},  
      {"name": "Banská Bystrica", "bbox": [5090000, 2830000, 5130000, 2870000]},  
      {"name": "Nitra region",    "bbox": [4940000, 2835000, 4980000, 2875000]},  
      {"name": "Trenčín region",  "bbox": [4890000, 2900000, 4930000, 2940000]},  
      {"name": "Žilina city",     "bbox": [5025000, 2950000, 5065000, 2990000]},  
      {"name": "Kosice city",     "bbox": [5325000, 2925000, 5360000, 2955000]}  
    ]
  },
  {
    "name": "Slovenia",
    "bbox": [4585000, 2484000, 4824000, 2663000],
    "subregions": [
      {"name": "Ljubljana",      "bbox": [4605000, 2580000, 4645000, 2620000]},  
      {"name": "Maribor",        "bbox": [4700000, 2585000, 4740000, 2625000]},  
      {"name": "Celje",          "bbox": [4675000, 2565000, 4715000, 2605000]},  
      {"name": "Kranj",          "bbox": [4585000, 2575000, 4625000, 2615000]},  
      {"name": "Koper",          "bbox": [4520000, 2525000, 4560000, 2565000]},  
      {"name": "Nova Gorica",    "bbox": [4465000, 2540000, 4505000, 2580000]},  
      {"name": "Murska Sobota",  "bbox": [4755000, 2590000, 4795000, 2630000]},  
      {"name": "Velenje",        "bbox": [4665000, 2575000, 4705000, 2615000]},  
      {"name": "Ptuj",           "bbox": [4720000, 2575000, 4760000, 2615000]},  
      {"name": "Savinja region", "bbox": [4630000, 2545000, 4670000, 2585000]}  
    ]
  },
  {
    "name": "Spain",
    "bbox": [2583000, 1651000, 3887000, 2337000],
    "subregions": [
      {"name": "Madrid",             "bbox": [3040000, 2110000, 3080000, 2150000]},  
      {"name": "Barcelona",          "bbox": [3410000, 2200000, 3450000, 2240000]},  
      {"name": "Andalusia",          "bbox": [2900000, 1550000, 3330000, 1990000]},  
      {"name": "Valencia",           "bbox": [3240000, 1930000, 3290000, 1980000]},  
      {"name": "Galicia",            "bbox": [2780000, 2170000, 3050000, 2500000]},  
      {"name": "Basque Country",     "bbox": [3190000, 2190000, 3250000, 2240000]},  
      {"name": "Castile‑La Mancha",  "bbox": [3010000, 1980000, 3280000, 2320000]},  
      {"name": "Catalonia",          "bbox": [3310000, 2070000, 3450000, 2260000]},  
      {"name": "Canary Islands",     "bbox": [1544000, 1024000, 2046000, 1040000]},  
      {"name": "Balearic Islands",   "bbox": [3010000, 1760000, 3180000, 1920000]}  
    ]
  },
  {
    "name": "Sweden",
    "bbox": [4358000, 3558000, 4889000, 5163000],
    "subregions": [
      {"name": "Stockholm",    "bbox": [4740000, 4420000, 4780000, 4460000]},  
      {"name": "Gothenburg",   "bbox": [4430000, 4260000, 4470000, 4300000]},  
      {"name": "Malmö",        "bbox": [4570000, 4230000, 4610000, 4270000]},  
      {"name": "Uppsala",      "bbox": [4740000, 4470000, 4780000, 4510000]},  
      {"name": "Västerås",     "bbox": [4650000, 4400000, 4690000, 4440000]},  
      {"name": "Linköping",    "bbox": [4610000, 4290000, 4650000, 4330000]},  
      {"name": "Örebro",       "bbox": [4540000, 4310000, 4580000, 4350000]},  
      {"name": "Umeå",         "bbox": [4820000, 4870000, 4860000, 4910000]},  
      {"name": "Luleå",        "bbox": [4990000, 5050000, 5030000, 5090000]},  
      {"name": "Kiruna",       "bbox": [5170000, 5360000, 5210000, 5400000]}  
    ]
  }
]

def download_copernicus_image(country_name, region_name, bbox, output_dir):
    x_min, y_min, x_max, y_max = bbox

    params = {
        "bbox": f"{x_min},{y_min},{x_max},{y_max}",
        "bboxSR": "3035",
        "imageSR": "3035",
        "size": "1200,1200",
        "format": "jpg",
        "f": "image"
    }

    region_dir = os.path.join(output_dir, country_name)
    os.makedirs(region_dir, exist_ok=True)

    image_file_name = f"{region_name.replace(' ', '_')}.jpg"
    image_file_path = os.path.join(region_dir, image_file_name)

    try:
        response = requests.get(BASE_URL, headers=headers, params=params, stream=True)
        response.raise_for_status()
        
        with open(image_file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"Downloaded image: {region_name} ({country_name})")

        metadata = {
            "title": f"Copernicus VHR 2021 - {region_name}",
            "url": response.url,
            "document_type": "copernicus_satellite_image",
            "categories": ["satellite_imagery", "land_use", "solar_wind_potential"],
            "source": {
                "provider": "Copernicus Land Monitoring Service",
                "repository": "land.copernicus.eu"
            },
            "retrieved_date": datetime.today().strftime('%Y-%m-%d'),
            "additional_info": {
                "resolution": "1200x1200",
                "format": "jpg",
                "bbox": {
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max
                },
                "projection": "EPSG:3035",
                "country": country_name,
                "region": region_name
            }
        }

        metadata_file_name = f"{region_name.replace(' ', '_')}.json"
        metadata_path = os.path.join(region_dir, metadata_file_name)

        with open(metadata_path, 'w') as json_file:
            json.dump(metadata, json_file, indent=4)

    except requests.HTTPError as http_err:
        logging.error(f"HTTP error for {region_name} ({country_name}): {http_err}")
    except Exception as err:
        logging.error(f"Unexpected error for {region_name} ({country_name}): {err}")

def download_copernicus_images(output_dir="output/images/copernicus"):
    logging.info("Starting Copernicus satellite image downloads.")
    
    for country in regions:
        country_name = country["name"]
        subregions = country.get("subregions", [])

        if not subregions:
            download_copernicus_image(country_name, country_name, country["bbox"], output_dir)
        else:
            for subregion in subregions:
                region_name = subregion["name"]
                bbox = subregion["bbox"]
                download_copernicus_image(country_name, region_name, bbox, output_dir)
    
    logging.info("Copernicus satellite image download complete.")