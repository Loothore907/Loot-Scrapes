import os
import json
from pathlib import Path
from src.scrapers.crawl4ai_integration.scraper import Scraper

def main():
    # Initialize scraper with default config
    config_path = Path(__file__).parent.parent / "src" / "scrapers" / "config" / "default_config.yaml"
    scraper = Scraper(str(config_path))
    
    # Example vendor URLs (replace with actual vendor URLs)
    vendor_urls = [
        "https://example-dispensary1.com",
        "https://example-dispensary2.com"
    ]
    
    # Collect data from all vendors
    vendor_data = scraper.collect_batch_vendor_data(vendor_urls)
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / "output" / "normalized"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save normalized data
    output_file = output_dir / "vendor_data.json"
    with open(output_file, "w") as f:
        json.dump([data.dict() for data in vendor_data], f, indent=2)
    
    print(f"Data collected and saved to {output_file}")

if __name__ == "__main__":
    main()