# Images-Retrieval

A Docker Compose–based pipeline designed to **collect, download, and annotate** energy-related images from authoritative sources including Copernicus, EPREL, INRIA, IRF, NASA Earth Observatory, Wikimedia Commons, and Wikipedia. This repository is ideal for building structured image datasets suitable for training multimodal AI models focused on the energy domain.

## 🚀 Features

- **Multi-source image retrieval**:
  - **Copernicus**: Satellite imagery
  - **EPREL**: Energy efficiency labels for appliances
  - **INRIA**: Aerial imagery dataset (via Kaggle)
  - **IRF**: Irregular facade dataset (via Kaggle)
  - **NASA Earth Observatory**: Earth observation images from NASA RSS feeds
  - **Wikimedia Commons**: Curated open-license images from specified energy-related categories
  - **Wikipedia**: Contextually relevant images extracted from Wikipedia articles

- **Structured Metadata Annotation**:
  - JSON metadata automatically created per image, including:
    - Resolution and format
    - Retrieval date
    - Source and descriptive category information

- **Configurable Toggles and Limits**:
  - Easily control each image source via environment flags (`RUN_COPERNICUS`, `RUN_EPREL`, `RUN_INRIA`, `RUN_IRF`, `RUN_NASA`, `RUN_WIKIMEDIA`, `RUN_WIKIPEDIA_IMAGES`)
  - Define image retrieval limits directly in `.env`

- **Comprehensive Logging**:
  - Detailed logs stored in `logs/images_app.log`
  - Real-time status updates on retrieval progress, successes, and errors

## 🗂 Repository Structure

images_retrieval
├── .env
├── .gitignore
├── Dockerfile
├── README.md
├── docker-compose.yaml
├── secrets
    └── kaggle.json
├── logs
│   └── images_app.log
├── main.py
├── output
│   └── wiki.jsonl
│   └── images
│       ├── copernicus
│       ├── eprel
│       ├── inria
│       ├── irf
│       ├── nasa
│       ├── wikimedia
│       └── wikipedia
├── requirements.txt
└── scripts
    ├── copernicus_retrieval.py
    ├── eprel_retrieval.py
    ├── inria_retrieval.py
    ├── irf_retrieval.py
    ├── nasa_retrieval.py
    ├── wikimedia_retrieval.py
    └── wikipedia_images_retrieval.py

- **`main.py`**: Orchestrates retrieval processes from configured sources.
- **`scripts/`**: Individual scripts managing retrieval from each data source.
- **`docker-compose.yaml`**: Defines services and environment configuration.
- **`Dockerfile`**: Docker container setup and Python dependencies.
- **`secrets/`**: stores sensitive credentials (kaggle.json for Kaggle API).

## 🔧 Prerequisites

- Docker & Docker Compose installed locally.
- Kaggle account and API credentials (`kaggle.json`) required for INRIA and IRF datasets. [Setup Kaggle API](https://www.kaggle.com/docs/api).
- `wiki.jsonl` from the `articles-retrieval` repository for Wikipedia image retrieval.
- Active internet connection for downloading external resources.

## ⚙️ Configuration

Configure the image retrieval pipeline by creating and editing a `.env` file at the repository root:

```bash
# Toggles (0: off, 1: on)
RUN_COPERNICUS=1
RUN_EPREL=1
RUN_INRIA=1
RUN_IRF=1
RUN_NASA=1
RUN_WIKIMEDIA=1
RUN_WIKIPEDIA_IMAGES=1

# Maximum number of images retrieved per source
MAX_INRIA_IMAGES=500
MAX_IRF_IMAGES=500
MAX_NASA_IMAGES=500
MAX_WIKIMEDIA_IMAGES=500

# INRIA-specific toggles
DOWNLOAD_INRIA_DATA=1
EXTRACT_INRIA_DATA=1

# IRF-specific toggles
DOWNLOAD_IRF_DATA=1
EXTRACT_IRF_DATA=1
```

Create your `.env` file in the repository root with:

```bash
touch .env
```

Open the file with a text editor to add your values, for example:

```bash
nano .env
```

Set your preferred retrieval parameters and toggles accordingly.

### Kaggle API Credentials

- Obtain `kaggle.json` from your Kaggle account (Profile → Account → Create API Token).

- Place the file at `./secrets/kaggle.json`.

### Wikipedia Images Retrieval

- Copy the `wiki.jsonl` file from the `output/wiki.jsonl` directory of the `articles-retrieval` repository to `./output/images/wikipedia/wiki.jsonl`:

```bash
mkdir -p output/images/wikipedia
cp path-to-articles-retrieval/output/wiki.jsonl output/images/wikipedia/
```

## 📂 Output

Images and metadata are saved as follows:

```text
output/images/
├── copernicus/
│   ├── image_1.png
│   └── image_1.json
├── eprel/
│   ├── label_1.png
│   └── label_1.json
├── inria/
│   ├── aerial_image_1.tif
│   └── aerial_image_1.json
├── irf/
│   ├── facade_image_1.jpg
│   └── facade_image_1.json
├── nasa/
│   ├── nasa_image_1.jpg
│   └── nasa_image_1.json
├── wikimedia/
│   ├── wikimedia_image_1.jpg
│   └── wikimedia_image_1.json
└── wikipedia/
    ├── wikipedia_image_1.jpg
    └── wikipedia_image_1.json
```

Each image has accompanying metadata structured as follows:

```json
{
  "filename": "image_name.jpg",
  "retrieved_date": "YYYY-MM-DD",
  "additional_info": {
    "resolution": "1920x1080px",
    "image_format": "JPEG"
  },
  "source": {
    "provider": "Source Provider",
    "repository": "Source URL"
  }
}
```

## 🐳 Build & Run

1. **Build the image**  from the repository root:

   ```bash
    docker build -t images-collector .
   ```

2. **Run the service** using Docker Compose:

   ```bash
   docker-compose up
   ```

   All scraper settings can be customized via environment variables in `.env`.

3. **Stop the service** when finished:

   ```bash
   docker-compose down
   ```

All retrieved images and metadata will be available in the `output/images/` directory.organized by source and ready for analysis and model training.