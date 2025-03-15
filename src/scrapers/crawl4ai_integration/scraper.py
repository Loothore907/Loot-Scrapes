from typing import Dict, List, Optional
import crawl4ai
from pydantic import BaseModel

class VendorData(BaseModel):
    """Schema for normalized vendor data"""
    name: str
    address: str
    phone: str
    website: Optional[str]
    hours: Dict[str, str]
    menu_items: List[Dict[str, any]]
    deals: List[Dict[str, any]]

class Scraper:
    """Interface for crawl4ai integration"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the scraper with optional configuration"""
        self.crawler = crawl4ai.Crawler(config_path) if config_path else crawl4ai.Crawler()
    
    def collect_vendor_data(self, url: str) -> VendorData:
        """
        Collect vendor data from a given URL using crawl4ai
        
        Args:
            url: The vendor's website URL
            
        Returns:
            VendorData object containing normalized vendor information
        """
        # Configure crawl4ai for cannabis vendor data extraction
        extraction_config = {
            "targets": {
                "name": "//h1[contains(@class, 'business-name')]",
                "address": "//div[contains(@class, 'address')]",
                "phone": "//div[contains(@class, 'phone')]",
                "hours": "//div[contains(@class, 'hours')]",
                "menu": "//div[contains(@class, 'menu-items')]",
                "deals": "//div[contains(@class, 'deals')]"
            }
        }
        
        # Execute the crawl
        raw_data = self.crawler.extract(url, extraction_config)
        
        # Process and normalize the data
        normalized_data = self._normalize_vendor_data(raw_data)
        
        return VendorData(**normalized_data)
    
    def _normalize_vendor_data(self, raw_data: Dict) -> Dict:
        """
        Normalize raw crawled data into standard format
        
        Args:
            raw_data: Dictionary of raw scraped data
            
        Returns:
            Dictionary of normalized data matching VendorData schema
        """
        # TODO: Implement normalization logic
        # This will need to handle different vendor site formats
        return {
            "name": raw_data.get("name", ""),
            "address": raw_data.get("address", ""),
            "phone": raw_data.get("phone", ""),
            "website": raw_data.get("website", ""),
            "hours": {},  # TODO: Parse hours
            "menu_items": [],  # TODO: Parse menu items
            "deals": []  # TODO: Parse deals
        }
    
    def collect_batch_vendor_data(self, urls: List[str]) -> List[VendorData]:
        """
        Collect data from multiple vendor URLs
        
        Args:
            urls: List of vendor website URLs
            
        Returns:
            List of VendorData objects
        """
        return [self.collect_vendor_data(url) for url in urls]