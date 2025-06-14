import os
import logging
from pathlib import Path
from scripts.copernicus_retrieval import download_copernicus_images
from scripts.eprel_retrieval import download_eprel_labels
from scripts.inria_retrieval import download_inria_images
from scripts.irf_retrieval import download_irf_images
from scripts.nasa_retrieval import download_nasa_images
from scripts.wikimedia_retrieval import download_wikimedia_images
from scripts.wikipedia_images_retrieval import download_wikipedia_images

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("logs/images_app.log"),
            logging.StreamHandler()
        ]
    )

def main():
    configure_logging()
    logging.info("=== Starting Image Retrieval ===")

    # Environment-driven toggles
    RUN_COPERNICUS = os.getenv("RUN_COPERNICUS", "1") == "1"
    RUN_EPREL = os.getenv("RUN_EPREL", "1") == "1"
    RUN_INRIA = os.getenv("RUN_INRIA", "1") == "1"
    RUN_IRF = os.getenv("RUN_IRF", "1") == "1"
    RUN_NASA = os.getenv("RUN_NASA", "1") == "1"
    RUN_WIKIMEDIA = os.getenv("RUN_WIKIMEDIA", "1") == "1"
    RUN_WIKIPEDIA_IMAGES = os.getenv("RUN_WIKIPEDIA_IMAGES", "1") == "1"

    logging.info(f"""
        RUN_COPERNICUS: {RUN_COPERNICUS},
        RUN_EPREL: {RUN_EPREL},
        RUN_INRIA: {RUN_INRIA},
        RUN_IRF: {RUN_IRF},
        RUN_NASA: {RUN_NASA},
        RUN_WIKIMEDIA: {RUN_WIKIMEDIA},
        RUN_WIKIPEDIA_IMAGES: {RUN_WIKIPEDIA_IMAGES}
    """)

    # Directories setup
    output_dir = Path("output/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Copernicus Satellite Images ---
    if RUN_COPERNICUS:
        try:
            download_copernicus_images(output_dir="output/images/copernicus")
            logging.info("Copernicus images retrieved successfully.")
        except Exception as e:
            logging.error(f"Copernicus retrieval failed: {e}")

    # --- EPREL Energy Labels ---
    if RUN_EPREL:
        try:
            download_eprel_labels(output_dir="output/images/eprel")
            logging.info("EPREL labels retrieved successfully.")
        except Exception as e:
            logging.error(f"EPREL retrieval failed: {e}")

    # --- INRIA Aerial Images ---
    if RUN_INRIA:
        try:
            cities = ["Austin", "Chicago", "Kitsap", "Western Tyrol", "Vienna", "Bellingham", "Bloomington", "Innsbruck", "San Francisco", "Eastern Tyrol"]
            max_inria_images = int(os.getenv("MAX_INRIA_IMAGES", 100))
            download_data = os.getenv("DOWNLOAD_INRIA_DATA", "1") == "1"
            extract_data = os.getenv("EXTRACT_INRIA_DATA", "1") == "1"

            download_inria_images(cities=cities, max_images=max_inria_images, output_dir="output/images/inria", download_data=download_data, extract_data=extract_data)
            logging.info("INRIA images retrieved successfully.")
        except Exception as e:
            logging.error(f"INRIA retrieval failed: {e}")

    # --- IRF Facade Images ---
    if RUN_IRF:
        try:
            max_irf_images = int(os.getenv("MAX_IRF_IMAGES", 100))
            download_data=os.getenv("DOWNLOAD_IRF_DATA", "1") == "1"
            extract_data=os.getenv("EXTRACT_IRF_DATA", "1") == "1"
            
            download_irf_images(max_irf_images, output_dir="output/images/irf", download_data=download_data, extract_data=extract_data)
            
            logging.info("IRF images retrieved successfully.")
        except Exception as e:
            logging.error(f"IRF retrieval failed: {e}")

    # --- NASA Earth Observatory Images ---
    if RUN_NASA:
        try:
            max_nasa_images = int(os.getenv("MAX_NASA_IMAGES", 100))
            
            download_nasa_images(max_images=max_nasa_images, output_dir="output/images/nasa")
            
            logging.info("NASA images retrieved successfully.")
        except Exception as e:
            logging.error(f"NASA retrieval failed: {e}")

    # --- Wikimedia Commons Images ---
    if RUN_WIKIMEDIA:
        try:
            wikimedia_categories = [
                "Satellite pictures", 
                "Construction", 
                "Power plants",
                "Solar panels", 
                "Wind turbines",
                "Smart meters",
                "Electric vehicles",
                "Energy storage",
                "Energy efficiency labels",
                "Renewable energy",
                "Energy transition",
                "Energy infrastructure",
                "Nuclear power plants",
                "Hydroelectric power plants",
                "Geothermal energy",   
                "Biomass energy",
                "Coal-fired power plants",
                "Geothermal power plants",
                "Biofuels",
                "Power transmission lines",
                "Smart grids",
                "Substations",
                "Control rooms of transmission systems",
                "Energy monitoring systems",
                "Energy management systems",
                "Natural gas power plants",
                "Zero energy buildings",
                "Energy-efficient buildings",
                "Near-zero energy buildings",
                "Energy-efficient appliances",
                "Energy-efficient lighting",
                "Energy-efficient HVAC systems",
                "Energy-efficient windows",
                "smart home energy systems",
                "microgrids",
                "demand response systems",
                "virtual power plants",
                "carbon capture and storage",
                "fuel cells",
                "hydrogen energy systems",
                "green roofs",
                "solar thermal systems",
                "energy-efficient transportation",
                "energy-efficient industrial processes",
                "energy-efficient manufacturing",
                "district heating systems",
                "district cooling systems",
                "heat pumps",
                "photovoltaic systems",
            ]

            max_wikimedia_images_per_category = int(os.getenv("MAX_WIKIMEDIA_IMAGES", 50))
            
            download_wikimedia_images(categories=wikimedia_categories, max_images_per_category=max_wikimedia_images_per_category, output_dir="output/images/wikimedia")
            
            logging.info("Wikimedia images retrieved successfully.")
        except Exception as e:
            logging.error(f"Wikimedia retrieval failed: {e}")

    # --- Wikipedia Article Images ---
    if RUN_WIKIPEDIA_IMAGES:
        try:
            input_wiki_json = Path("output/wiki.jsonl")
            
            download_wikipedia_images(input_file=input_wiki_json, output_dir="output/images/wikipedia")

            logging.info("Wikipedia images retrieved successfully.")
        except Exception as e:
            logging.error(f"Wikipedia images retrieval failed: {e}")

    logging.info("=== Image Retrieval Completed ===")

if __name__ == "__main__":
    main()