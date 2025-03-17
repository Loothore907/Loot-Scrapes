"""
PotAdvisor Crawler

This module implements a crawler for PotAdvisor websites using Crawl4AI.
It extracts dispensary data and filters by specified ZIP codes.

File: src/scrapers/crawl4ai_integration/potadvisor_crawler.py
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any, Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# Configure logging
logger = logging.getLogger(__name__)

class PotAdvisorCrawler:
    """
    Class for crawling PotAdvisor websites to extract dispensary information
    and filter results by provided ZIP codes.
    """
    
    def __init__(self, output_dir: str = "output/normalized"):
        """
        Initialize the PotAdvisor crawler.
        
        Args:
            output_dir: Directory where results will be saved
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(Path(output_dir), exist_ok=True)
        
        # Define extraction schemas
        self.listing_schema = self._define_listing_schema()
        self.detail_schema = self._define_detail_schema()
        
        logger.info("PotAdvisor crawler initialized with output directory: %s", output_dir)
    
    def _define_listing_schema(self) -> Dict[str, Any]:
        """
        Define the schema for extracting dispensary listings from state pages.
        
        Returns:
            Dictionary defining the extraction schema for listings
        """
        return {
            "name": "PotAdvisor State Listings",
            "baseSelector": ".article, article, .dispensary, div[class*='dispensary']",  # More flexible to match various structures
            "fields": [
                {
                    "name": "name",
                    "selector": "h2, h3, .title, .heading, [class*='title'], [class*='name']",  # More flexible for titles
                    "type": "text"
                },
                {
                    "name": "address",
                    "selector": "*:contains('Address:'), span[class*='address'], div[class*='address'], div:contains('Anchor')",  # More flexible for addresses
                    "type": "text"
                },
                {
                    "name": "url",
                    "selector": "a[href*='directory'], a.button, a[class*='btn'], a[class*='link'], a:not([class])",  # More flexible for links
                    "type": "attribute",
                    "attribute": "href"
                }
            ]
        }
    
    def _define_detail_schema(self) -> Dict[str, Any]:
        """
        Define the schema for extracting detailed dispensary information.
        
        Returns:
            Dictionary defining the extraction schema for details
        """
        return {
            "name": "PotAdvisor Dispensary Details",
            "fields": [
                {
                    "name": "name",
                    "selector": "h1, h2, .title, [class*='title'], [class*='heading']",  # More flexible title matching
                    "type": "text"
                },
                {
                    "name": "address",
                    "selector": "*:contains('Address:'), *[class*='address']",  # More flexible address matching
                    "type": "text"
                },
                {
                    "name": "phone",
                    "selector": "*:contains('Phone:'), a[href^='tel:'], *[class*='phone']",  # More flexible phone matching
                    "type": "text"
                },
                {
                    "name": "website",
                    "selector": "*:contains('Website:') a, a[href^='http'], a[class*='website'], a[class*='external']",  # More flexible website link matching
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "hours",
                    "selector": "*:contains('Hours:'), *[class*='hours'], *:contains('Open')",  # Fixed syntax error
                    "type": "text"
                },
                {
                    "name": "type",
                    "selector": "*:contains('Type:'), *[class*='type'], span:contains('Recreational'), span:contains('Medical')",  # More flexible type matching
                    "type": "text"
                }
            ]
        }
    
    def extract_zip_from_address(self, address: str) -> Optional[str]:
        """
        Extract ZIP code from an address string.
        
        Args:
            address: Address string to extract ZIP code from
            
        Returns:
            ZIP code string or None if not found
        """
        import re
        
        # Look for ZIP code pattern (5 digits, optionally followed by hyphen and 4 digits)
        zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address)
        
        if zip_match:
            return zip_match.group(1)
        return None
    
    async def crawl_state(self, state_abbr: str, state_name: str, url: str, 
                         filter_zip_codes: Set[str]) -> List[Dict[str, Any]]:
        """
        Crawl PotAdvisor for a specific state and extract dispensary information,
        filtering by the provided ZIP codes.
        
        Args:
            state_abbr: State abbreviation (e.g., 'AK')
            state_name: State name (e.g., 'alaska')
            url: PotAdvisor URL for the state listings
            filter_zip_codes: Set of ZIP codes to filter by
            
        Returns:
            List of dispensary data dictionaries
        """
        logger.info(f"Starting crawl for {state_name.title()} ({state_abbr})")
        
        # Configure the browser
        browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )
        
        # Set up extraction strategy for state listing page
        listing_strategy = JsonCssExtractionStrategy(self.listing_schema)
        
        # Configure crawler for state listing
        run_config = CrawlerRunConfig(
            extraction_strategy=listing_strategy,
            cache_mode=CacheMode.ENABLED
        )
        
        dispensaries = []
        
        try:
            # Perform initial crawl to get dispensary listings
            async with AsyncWebCrawler(config=browser_config) as crawler:
                logger.info(f"Crawling state listing: {url}")
                
                result = await crawler.arun(
                    url=url,
                    config=run_config
                )
                
                if result.success:
                    # Parse the extracted content
                    try:
                        listings = json.loads(result.extracted_content)
                        logger.info(f"Found {len(listings)} dispensaries in {state_name.title()}")
                        
                        # Filter by ZIP code
                        filtered_listings = []
                        
                        for listing in listings:
                            # Extract ZIP code from address
                            address = listing.get('address', '')
                            zip_code = self.extract_zip_from_address(address)
                            if zip_code:
                                listing['zip_code'] = zip_code
                            
                            # Include dispensaries with matching ZIP codes or if no filter is applied
                            if not filter_zip_codes or (zip_code and zip_code in filter_zip_codes):
                                filtered_listings.append(listing)
                        
                        logger.info(f"Filtered to {len(filtered_listings)} dispensaries in specified ZIP codes")
                        
                        # Crawl detailed pages for each filtered dispensary
                        detail_strategy = JsonCssExtractionStrategy(self.detail_schema)
                        detail_config = CrawlerRunConfig(
                            extraction_strategy=detail_strategy,
                            cache_mode=CacheMode.ENABLED
                        )
                        
                        for listing in filtered_listings:
                            # Get dispensary detail URL
                            detail_url = listing.get('url')
                            
                            if detail_url:
                                # Handle relative URLs
                                if not detail_url.startswith('http'):
                                    detail_url = f"https://potadvisor.com{detail_url}"
                                
                                logger.info(f"Crawling details for: {listing.get('name')} - {detail_url}")
                                
                                try:
                                    detail_result = await crawler.arun(
                                        url=detail_url,
                                        config=detail_config
                                    )
                                    
                                    if detail_result.success:
                                        # Parse detailed information
                                        detail_data = json.loads(detail_result.extracted_content)
                                        # Merge listing and detail data
                                        merged_data = {**listing}
                                        if detail_data and len(detail_data) > 0:
                                            merged_data.update(detail_data[0])
                                        dispensaries.append(merged_data)
                                    else:
                                        logger.warning(f"Failed to get details for {listing.get('name')}: {detail_result.error}")
                                        dispensaries.append(listing)  # Add listing data without details
                                except Exception as e:
                                    logger.error(f"Error crawling details for {listing.get('name')}: {str(e)}")
                                    dispensaries.append(listing)  # Add listing data without details
                            else:
                                logger.warning(f"No URL for dispensary: {listing.get('name')}")
                                dispensaries.append(listing)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON from extracted content. Content: {result.extracted_content[:100]}...")
                else:
                    logger.error(f"Failed to crawl state listing: {result.error}")
        except Exception as e:
            logger.exception(f"Error during crawling: {str(e)}")
        
        return dispensaries
    
    async def crawl_and_save(self, state_mapping: Dict[str, Tuple[str, str]], 
                          filter_zips_by_state: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Crawl PotAdvisor for multiple states and save results.
        
        Args:
            state_mapping: Dictionary mapping state abbreviations to (url, state_name) tuples
            filter_zips_by_state: Dictionary mapping state abbreviations to lists of ZIP codes to filter by
            
        Returns:
            Dictionary mapping state abbreviations to output file paths
        """
        output_files = {}
        
        for state_abbr, (url, state_name) in state_mapping.items():
            # Get filter ZIP codes for this state
            filter_zip_codes = set(filter_zips_by_state.get(state_abbr, []))
            
            # Crawl the state
            dispensaries = await self.crawl_state(
                state_abbr=state_abbr,
                state_name=state_name,
                url=url,
                filter_zip_codes=filter_zip_codes
            )
            
            if dispensaries:
                # Create output file path
                output_file = os.path.join(self.output_dir, f"{state_name.lower()}_dispensaries.json")
                
                # Save results to JSON file
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(dispensaries, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"Saved {len(dispensaries)} dispensaries to {output_file}")
                    output_files[state_abbr] = output_file
                except Exception as e:
                    logger.error(f"Error saving results for {state_name}: {str(e)}")
            else:
                logger.warning(f"No dispensaries found for {state_name}")
        
        return output_files


# Test function for when the module is run directly
async def test_crawler():
    """Test the PotAdvisor crawler with sample data."""
    # Sample state mapping
    state_mapping = {
        'AK': ('https://potadvisor.com/states/alaska/alaska-dispensaries/', 'alaska'),
        'WA': ('https://potadvisor.com/states/washington/washington-dispensaries/', 'washington')
    }
    
    # Sample ZIP codes
    filter_zips_by_state = {
        'AK': ['99501', '99503', '99508'],
        'WA': ['98101', '98103', '98105']
    }
    
    # Initialize crawler
    crawler = PotAdvisorCrawler(output_dir="output/normalized")
    
    # Crawl and save results
    output_files = await crawler.crawl_and_save(state_mapping, filter_zips_by_state)
    
    print("Crawling complete. Results saved to:")
    for state, file_path in output_files.items():
        print(f"- {state}: {file_path}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the test crawler
    asyncio.run(test_crawler())