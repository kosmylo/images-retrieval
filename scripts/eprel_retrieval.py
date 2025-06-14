import os
import re
import json
import logging
from datetime import datetime
import requests
from pdf2image import convert_from_path

BASE_URL = "https://eprel.ec.europa.eu/labels"

# Product list: (category, ID, name)
products = [
    # Light sources
    ("lightsources", 423340, "Philips Signify LED"),
    ("lightsources", 614102, "LEDVANCE LED Lamp"),
    ("lightsources", 546279, "Osram LED Superstar PAR11 Spotlight"),
    ("lightsources", 546424, "Osram LED Lamp"),
    ("lightsources", 1672034, "Conalux LED Bulb"),
    ("lightsources", 523286, "Osram LED Superstar Classic A Bulb"),
    ("lightsources", 1027006, "UMAGE 2435 LED Panel Light"),
    ("lightsources", 997961, "Light-Point AURA W1 LED Wall Lamp"),

    # Electronic displays (TVs/monitors)
    ("electronicdisplays", 342333, "LG 32-inch LCD TV"),
    ("electronicdisplays", 360640, "Philips 32PHS5505 LED TV"),
    ("electronicdisplays", 360650, "Philips 24PFS5505 LED TV"),
    ("electronicdisplays", 360643, "Philips 43PFS5505 Full HD LED TV"),
    ("electronicdisplays", 1161811, "Philips 43PUS8057 UHD LED TV"),
    ("electronicdisplays", 2249039, "Philips 65PUS8500 Ambilight TV"),
    ("electronicdisplays", 420631, "Philips 55PUS9435 Android TV"),
    ("electronicdisplays", 580722, "Philips 43PUS7406 LED TV"),
    ("electronicdisplays", 1133973, "Philips 32PHS5507 LED TV"),
    ("electronicdisplays", 1537992, "Philips 55OLED708 OLED TV"),
    ("electronicdisplays", 1875218, "Samsung The Frame QE55LS03 TV"),
    ("electronicdisplays", 403707, "Sony XR-55A90J OLED TV"),
    ("electronicdisplays", 1133974, "Philips 43PFS5507 LED TV"),
    ("electronicdisplays", 617003, "Philips 24PFS5505/62 LED TV"),        
    ("electronicdisplays", 617007, "Philips 32PHS5505/62 LED TV"),        
    ("electronicdisplays", 617056, "Philips 43PFS5505/62 LED TV"),

    # Air conditioners (household air conditioners)
    ("airconditioners", 209450, "Samsung AR12TXHQASIN Air Conditioner"),   
    ("airconditioners", 386947, "Mitsubishi MSZ-AP20VGK Air Conditioner"),  
    ("airconditioners", 161369, "Daikin FTXA42A2V1BT Air Conditioner"),     

    # Refrigerating appliances (household refrigerators, freezers, wine coolers)
    ("refrigeratingappliances2019", 373089, "Millesime Wine Cooler"),
    ("refrigeratingappliances2019", 1879960, "Samsung RF65DG9H0EB1 Fridge-Freezer"),
    ("refrigeratingappliances2019", 788877, "Siemens KG39NAIAT Fridge-Freezer"),
    ("refrigeratingappliances2019", 260955, "Bosch KSV36VLEP Refrigerator"),
    ("refrigeratingappliances2019", 420406, "Samsung RS6HA8891B1 Fridge-Freezer"),
    ("refrigeratingappliances2019", 1599545, "LG GSM32HSBEH Fridge-Freezer"),
    ("refrigeratingappliances2019", 2026753, "LG GBF3102EEP Fridge-Freezer"),
    ("refrigeratingappliances2019", 2000312, "Bosch KGN33NLEBG Fridge-Freezer"),
    ("refrigeratingappliances2019", 2090506, "Bosch KGN392WEBG Fridge-Freezer"),
    ("refrigeratingappliances2019", 1847166, "LG GBV3110EPY Fridge-Freezer"),
    ("refrigeratingappliances2019", 1790415, "Klarstein 18-Bottle Wine Cooler"),

    # Refrigerating appliances with direct sales function (commercial refrigerators/freezers)
    ("refrigeratingappliancesdirectsalesfunction", 1519452, "JBG-2 LDFI291250 Beverage Cooler"),
    ("refrigeratingappliancesdirectsalesfunction", 1680698, "JBG-2 WNEL172500 Freezer Cabinet"),
    ("refrigeratingappliancesdirectsalesfunction", 1178346, "ARNEG spa. OSK3P-963128090VCB022801"),

    # Dishwashers (household)
    ("dishwashers2019", 2119457, "Indesit IN2IE10 Dishwasher"),
    ("dishwashers2019", 1450861, "Siemens SN65ZX07CE Dishwasher"),
    ("dishwashers2019", 1776411, "Bosch SMV4EVX08E Dishwasher"),
    ("dishwashers2019", 1864516, "Neff S195HCX02G Dishwasher"),
    ("dishwashers2019", 1606927, "Bosch SMD8TCX01E Dishwasher"),
    ("dishwashers2019", 1452629, "Candy CF 5C7F0X Dishwasher"),
    ("dishwashers2019", 2261658, "Bosch SMS6TCI02G Serie 6 Dishwasher"),

    # Washing machines (household)
    ("washingmachines2019", 1776425, "Bosch WGG244FCGB Washer"),
    ("washingmachines2019", 1865269, "Miele WCA032 WCS Washer"),
    ("washingmachines2019", 1105176, "Bosch Serie 6 WUU28T70 Washer"),
    ("washingmachines2019", 1331024, "PKM WA8-ES1416DAI Washer"),
    ("washingmachines2019", 1465039, "Samsung WW80T534AAX Washer"),
    ("washingmachines2019", 1365926, "Bosch Serie 6 WGG254F0IT Washer"),
    ("washingmachines2019", 262932, "Samsung WW90T534DAW Washer"),

    # Washer-dryers (household)
    ("washerdriers2019", 1256614, "Bosch WNG25401GB Washer-Dryer"),
    ("washerdriers2019", 1450874, "Siemens WN54C2A40 Washer-Dryer"),
    ("washerdriers2019", 1450882, "Bosch WNC244070 Serie 8 Washer-Dryer"),
    ("washerdriers2019", 306895, "Candy CSOW 4855TWE/1-S Washer-Dryer"),   

    # Tumble dryers (household)
    ("tumbledriers", 1298104, "AEG TR722E84P Dryer"),                     
    ("tumbledriers", 1563412, "Bosch WTH85223GB Dryer"),
    ("tumbledriers", 1574692, "Siemens iQ700 WQ45B2B40 Dryer"),
    ("tumbledriers", 1776057, "Bosch Serie 4 WTN83203 Dryer"),

    # Ovens (domestic electric ovens)
    ("ovens", 82328, "Indesit IFW 6330 IX Oven"),
    ("ovens", 1293452, "Bosch Serie 8 HBG7763B1 Oven"),
    ("ovens", 165747, "Neff B3ACE4HN0B Built-in Oven"),

    # Range hoods (cooker hoods)
    ("rangehoods", 767499, "Neff I88WMM1S7B Hood"),
    ("rangehoods", 563610, "Bosch DFR067A52 Hood"),
    ("rangehoods", 1323374, "AEG DPK5660B Hood"),
    ("rangehoods", 1994289, "Klarstein DownDraft 60 Cooker Hood"),

    # Local space heaters (room heaters, stoves)
    ("localspaceheaters", 415304, "Spartherm Linear Module XS Wood Stove"),
    ("localspaceheaters", 415438, "Spartherm Arte U-70h Fireplace"),
    ("localspaceheaters", 545040, "Extraflame LUCE BIANCO Pellet Stove"),

    # Space heaters / combination heaters (boilers, heat pumps)
    ("spaceheaters", 86427, "Vaillant ecoTEC Gas Boiler"),
    ("spaceheaters", 790978, "Vaillant ecoTEC Pro VMW236 Boiler"),

    # Packages of space heaters/combination heaters (boiler + control + solar)
    ("spaceheaterpackages", 1019834, "Ritter 72P0010 Boiler+Solar Package"),  

    # Water heaters (hot water storage tanks, electric heaters, heat pump water heaters)
    ("waterheaters", 108766, "Ariston Blu1 Eco Electric Water Heater"),
     
    # Residential ventilation units (heat-recovery ventilators)
    ("residentialventilationunits", 94736, "Systemair Ventila FT Ventilation Unit"),
    ("residentialventilationunits", 2085254, "Zehnder ComfoAir Q600 Ventilation Unit"),
    ("residentialventilationunits", 2082335, "Zehnder ComfoAir Q350 Ventilation Unit"),

    # Hot water storage tanks for water heaters
    ("waterheaters", 108766, "Ariston Blu1 Eco Electric Water Heater"),

    # Hot water storage tanks for water heaters
    ("hotwaterstoragetanks", 27672, "Wolf Pufferspeicher SPU-1-200 Tank"),
    ("hotwaterstoragetanks", 27673, "Wolf Pufferspeicher SPU-2-500 Tank"),

    # Solid fuel boilers (biomass boilers)
    ("solidfuelboilers", 2261458, "PellPal DUO 18 Pellet Boiler"),            

    # Solid fuel boiler packages (boiler + supplementary heaters/solar package)
    ("solidfuelboilerpackages", 1447353, "Solarbayer HKK 30 Boiler Package"),

    # Tyres (vehicle tyres with EU labels)
    ("tyres", 1743675, "Goodyear EfficientGrip Performance"),
    ("tyres", 568079, "Goodyear EfficientGrip Cargo"),
    ("tyres", 596965, "Pirelli P Zero Nero"),
    ("tyres", 409435, "Michelin e.Primacy (other size)"),
    ("tyres", 843310, "Continental PremiumContact 7"),
    ("tyres", 659191, "Continental EcoContact 6"),
    ("tyres", 643892, "Continental SportContact 7"),
    ("tyres", 596271, "Continental VanContact 4Season"),
    ("tyres", 2049862, "Continental CrossContact LX Sport"),
    ("tyres", 382321, "Bridgestone Turanza T005 (195/65R15 91H)"),
    ("tyres", 611160, "Goodyear EfficientGrip Cargo 2"),                     
    ("tyres", 411122, "Michelin e.Primacy (205/55R17 95V XL)"),              
    ("tyres", 412786, "Michelin Primacy 4+ (205/55R16 91H)"),                
    ("tyres", 977568, "Michelin Primacy 4+ (235/45R18 98Y)"),                
    ("tyres", 1104261, "Michelin e.Primacy S2 (205/55R19 97V)"),
    ("tyres", 796599, "Michelin e.Primacy (205/55R17)"),
    ("tyres", 1434459, "Goodyear Eagle F1 Asymmetric 6 (235/40R19)"),
    ("tyres", 380987, "Bridgestone Turanza T005 (205/55R16 91W)"),
    ("tyres", 501593, "Bridgestone Turanza T005 (225/45R17 94Y)")
]

headers = {
    "User-Agent": "mAiEnergyBot/1.0 (kosmylo@gmail.com; downloading EPREL labels for research)"
}

def sanitize_filename(filename):
    """Sanitize filename by replacing problematic characters."""
    return re.sub(r'[\\/*?:"<>|()+\[\]{}]', '_', filename)

def download_eprel_labels(output_dir):

    os.makedirs(output_dir, exist_ok=True)

    for category, product_id, product_name in products:
        try:
            download_eprel_label(category, product_id, product_name, output_dir)
        except Exception as e:
            logging.error(f"Error downloading/processing {product_name} ({product_id}): {e}")

    logging.info("EPREL energy label download and conversion complete.")

def download_eprel_label(category, product_id, product_name, base_output_dir):
    urls_to_try = [
        f"{BASE_URL}/{category}/Label_{product_id}.pdf",
        f"{BASE_URL}/{category}/Label_{product_id}_big_color.pdf"
    ]

    category_dir = os.path.join(base_output_dir, category)
    os.makedirs(category_dir, exist_ok=True)

    safe_product_name = sanitize_filename(product_name)
    
    pdf_file_name = f"{safe_product_name}_{product_id}.pdf"
    pdf_file_path = os.path.join(category_dir, pdf_file_name)

    for url in urls_to_try:
        try:
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code != 200:
                logging.warning(f"Failed to download from {url}: HTTP {response.status_code}")
                continue

            with open(pdf_file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            try:
                images = convert_from_path(pdf_file_path, dpi=200)
                break  # PDF and conversion successful
            except Exception as e:
                logging.warning(f"Invalid PDF for {product_name} ({product_id}), retrying other URL...")
                os.remove(pdf_file_path)
                continue
        except Exception as e:
            logging.error(f"Request failed for {url}: {e}")
            continue
    else:
        logging.error(f"Failed to download/convert PDF for {product_name} ({product_id}) after retries.")
        return

    image_file_name = f"{safe_product_name}_{product_id}.png"
    image_file_path = os.path.join(category_dir, image_file_name)

    try:
        images[0].save(image_file_path, 'PNG')
        logging.info(f"Saved label image: {image_file_name}")
    except Exception as e:
        logging.error(f"Failed to convert/save image for {product_name} ({product_id}): {e}")
        return

    metadata = {
        "title": product_name,
        "url": url,
        "document_type": "eprel_label_image",
        "categories": [category],
        "source": {
            "provider": "European Commission EPREL",
            "repository": "eprel.ec.europa.eu"
        },
        "retrieved_date": datetime.today().strftime('%Y-%m-%d'),
        "additional_info": {
            "resolution": f"{images[0].width}x{images[0].height}",
            "format": "png"
        }
    }

    metadata_file_name = f"{safe_product_name}_{product_id}.json"
    metadata_path = os.path.join(category_dir, metadata_file_name)

    with open(metadata_path, 'w') as json_file:
        json.dump(metadata, json_file, indent=4)
    logging.info(f"Saved metadata for: {product_name}")