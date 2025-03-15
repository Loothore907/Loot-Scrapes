# Loot-Scrapes

Data collection and normalization hub for Loot's Ganja Guide ecosystem. This service handles automated data collection from multiple sources and normalizes it for consumption by the admin dashboard.

## Project Structure

```
Loot-Scrapes/
├── src/
│   ├── scrapers/           # Web scraping modules
│   │   ├── crawl4ai_integration/
│   │   ├── config/
│   │   └── targets/       # Site-specific configurations
│   ├── voice/             # Voice API integration
│   │   ├── config/
│   │   ├── api_integration/
│   │   └── call_scripts/
│   └── vendor_intake/     # Direct vendor data processing
│       ├── parsers/
│       └── validators/
├── output/                # Normalized data output
│   └── normalized/
├── tests/                 # Test suite
└── config/               # Global configuration
```

## Tech Stack

- **Language**: Python 3.11+
- **Web Scraping**: crawl4ai integration
- **Voice API**: (TBD - Twilio/other voice service)
- **Data Processing**: pandas, numpy
- **Testing**: pytest
- **Code Quality**: black, isort, flake8

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Loothore907/Loot-Scrapes.git
cd Loot-Scrapes
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Data Collection Methods

### 1. Web Scraping (crawl4ai)
- Automated collection from vendor websites
- Regulatory agency data extraction
- Menu and pricing information

### 2. Voice API Integration
- Automated calls to vendors
- Real-time data collection
- Schedule and availability information

### 3. Direct Vendor Data Intake
- JSON/CSV file processing
- Data validation and normalization
- Error reporting and correction

## Usage

### Web Scraping
```python
from src.scrapers.crawl4ai_integration import Scraper

scraper = Scraper()
data = scraper.collect_vendor_data("vendor_url")
```

### Voice Collection
```python
from src.voice.api_integration import VoiceCollector

collector = VoiceCollector()
data = collector.schedule_vendor_call("vendor_phone")
```

### Vendor Data Processing
```python
from src.vendor_intake.parsers import VendorDataParser

parser = VendorDataParser()
normalized_data = parser.process_file("vendor_data.json")
```

## Data Flow

1. Data Collection
   - Web scraping via crawl4ai
   - Voice API calls
   - Direct vendor uploads

2. Normalization
   - Data validation
   - Format standardization
   - Error checking

3. Output
   - Normalized JSON files
   - Ready for loots-data-services ingestion

## Integration Points

### crawl4ai Integration
- Utilizes crawl4ai as a dependency
- Custom configurations for cannabis industry
- AI-optimized data extraction

### Voice API Integration
- Automated call scheduling
- Speech-to-text processing
- Data extraction from conversations

### Admin Dashboard Integration
- Standardized output format
- Validation against dashboard schema
- Error reporting and logging

## Development

### Setting up development environment
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linters
flake8 src tests
black src tests
isort src tests
```

### Branch Strategy
- `main`: Production-ready code
- `develop`: Development branch
- Feature branches: `feature/feature-name`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Proprietary - See LICENSE file for details

## Related Projects

- [LootsGanjaGuide-Fresh](https://github.com/Loothore907/LootsGanjaGuide-Fresh.git) - Mobile Application
- [loots-data-services](https://github.com/Loothore907/loots-data-services.git) - Admin Dashboard