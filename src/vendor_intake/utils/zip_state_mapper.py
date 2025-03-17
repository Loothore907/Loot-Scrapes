"""
ZIP Code to State Mapper

This module provides functionality to map ZIP codes to their corresponding states
and perform validation on ZIP code inputs.

File: src/vendor_intake/utils/zip_state_mapper.py
"""

import csv
import re
import os
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

class ZipCodeMapper:
    """Class for mapping ZIP codes to states and performing related operations."""
    
    def __init__(self, zip_database_path: Optional[str] = None):
        """
        Initialize the ZIP code mapper with an optional custom database path.
        
        Args:
            zip_database_path: Path to the ZIP code database CSV file. If None, will use a
                               built-in database or attempt to download one.
        """
        self.zip_to_state_map: Dict[str, str] = {}
        self.zip_database_path = zip_database_path
        self._load_zip_database()
    
    def _load_zip_database(self) -> None:
        """
        Load the ZIP code to state mapping database.
        
        If a custom path is provided, it will attempt to load from there.
        Otherwise, it will use a built-in database or download one if necessary.
        
        Raises:
            FileNotFoundError: If the database file cannot be found.
        """
        try:
            if self.zip_database_path and os.path.exists(self.zip_database_path):
                # Use provided database file
                self._load_from_csv(self.zip_database_path)
            else:
                # If no custom path or file doesn't exist, use the built-in dataset
                package_dir = Path(__file__).parent
                default_db_path = package_dir / "data" / "zip_code_database.csv"
                
                if os.path.exists(default_db_path):
                    self._load_from_csv(default_db_path)
                else:
                    # Create initial mapping with fallback data
                    self._create_initial_mapping()
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(default_db_path), exist_ok=True)
                    
                    # Try to download a more comprehensive database
                    self._download_zip_database(default_db_path)
        except Exception as e:
            logger.error(f"Error loading ZIP code database: {str(e)}")
            # Fall back to built-in mapping if there's an error
            self._create_initial_mapping()

    def _load_from_csv(self, file_path: Union[str, Path]) -> None:
        """
        Load ZIP code data from a CSV file.
        
        Args:
            file_path: Path to the CSV file containing ZIP code data.
        """
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # CSV structure may vary, so handle different column names
                    zip_code = row.get('zip_code') or row.get('zipcode') or row.get('ZIP')
                    state = row.get('state') or row.get('STATE') or row.get('state_abbr')
                    
                    if zip_code and state:
                        self.zip_to_state_map[zip_code] = state
                
            logger.info(f"Loaded {len(self.zip_to_state_map)} ZIP codes from {file_path}")
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {str(e)}")
            raise

    def _create_initial_mapping(self) -> None:
        """
        Create an initial ZIP code to state mapping with common ranges.
        This is a fallback if no database file is available.
        """
        # Define ZIP code ranges for states (simplified)
        state_ranges = {
            'AL': (35000, 36999),
            'AK': (99500, 99999),
            'AZ': (85000, 86999),
            'AR': (71600, 72999),
            # Add more states as needed
            'WA': (98000, 99499),
            # ... other states ...
        }
        
        # Create mapping based on ranges
        for state, (start, end) in state_ranges.items():
            for zip_code in range(start, end + 1):
                self.zip_to_state_map[str(zip_code)] = state
        
        logger.info("Created initial ZIP code mapping with basic ranges")

    def _download_zip_database(self, save_path: Path) -> None:
        """
        Download a comprehensive ZIP code database if available.
        
        Args:
            save_path: Path where the downloaded database should be saved.
        """
        # This is a placeholder for actual download logic
        # In a production system, you might download from Census.gov or another source
        try:
            logger.info("Attempting to download ZIP code database...")
            # Actual download code would go here
            # For now, just log a message
            logger.info("ZIP code database download functionality not implemented")
        except Exception as e:
            logger.error(f"Failed to download ZIP code database: {str(e)}")

    def validate_zip_code(self, zip_code: str) -> bool:
        """
        Validate if a string is a properly formatted US ZIP code.
        
        Args:
            zip_code: String to validate as a ZIP code
            
        Returns:
            bool: True if the string is a valid ZIP code format, False otherwise
        """
        # Basic format validation (5 digits, or 5 digits + dash + 4 digits)
        zip_pattern = r'^\d{5}(?:-\d{4})?$'
        
        if not re.match(zip_pattern, zip_code):
            return False
            
        # For simplicity, we'll just check if it's in our database or in a valid range
        base_zip = zip_code[:5]  # Get first 5 digits
        
        return base_zip in self.zip_to_state_map or self._is_in_valid_range(base_zip)
    
    def _is_in_valid_range(self, zip_base: str) -> bool:
        """
        Check if a 5-digit ZIP code is within valid US ZIP code ranges.
        
        Args:
            zip_base: 5-digit ZIP code
            
        Returns:
            bool: True if in valid range, False otherwise
        """
        try:
            zip_num = int(zip_base)
            # US ZIP codes generally range from 00001 to 99999
            # but certain ranges are not used
            return 0 < zip_num < 100000
        except ValueError:
            return False

    def get_state_for_zip(self, zip_code: str) -> Optional[str]:
        """
        Get the state abbreviation for a given ZIP code.
        
        Args:
            zip_code: ZIP code to look up
            
        Returns:
            str or None: Two-letter state abbreviation, or None if not found
        """
        # Handle ZIP+4 format by extracting the base ZIP
        base_zip = zip_code.split('-')[0]
        
        return self.zip_to_state_map.get(base_zip)
    
    def process_zip_codes(self, zip_codes: Union[str, List[str]]) -> Dict[str, List[str]]:
        """
        Process multiple ZIP codes and group them by state.
        
        Args:
            zip_codes: String with ZIP codes (possibly mixed with text) or a list of ZIP codes
            
        Returns:
            Dict mapping state abbreviations to lists of valid ZIP codes in that state
        """
        # Handle string input by parsing into a list
        if isinstance(zip_codes, str):
            # Extract all potential ZIP codes using regex
            # This finds all 5-digit sequences that might be ZIP codes
            zip_list = re.findall(r'\b\d{5}(?:-\d{4})?\b', zip_codes)
        else:
            zip_list = zip_codes
            
        # If no ZIP codes found, try alternate parsing
        if not zip_list and isinstance(zip_codes, str):
            # Try splitting by common separators and filtering
            potential_zips = re.split(r'[,;\s\n]+', zip_codes)
            zip_list = [z.strip() for z in potential_zips if z.strip() and z.strip().isdigit()]
            
        result: Dict[str, List[str]] = {}
        invalid_zips: List[str] = []
        
        # Process each ZIP code
        for zip_code in zip_list:
            # Validate ZIP code format
            if not self.validate_zip_code(zip_code):
                logger.warning(f"Invalid ZIP code format: {zip_code}")
                invalid_zips.append(zip_code)
                continue
                
            # Get state for ZIP code
            state = self.get_state_for_zip(zip_code)
            if state:
                if state not in result:
                    result[state] = []
                result[state].append(zip_code)
            else:
                logger.warning(f"Could not determine state for ZIP code: {zip_code}")
                invalid_zips.append(zip_code)
        
        if invalid_zips:
            logger.warning(f"Unprocessed ZIP codes: {', '.join(invalid_zips)}")
            
        return result

    def states_to_urls(self, states: Set[str], base_url: str = "https://potadvisor.com") -> Dict[str, Tuple[str, str]]:
        """
        Convert state abbreviations to PotAdvisor URLs.
        
        Args:
            states: Set of state abbreviations
            base_url: Base URL for PotAdvisor state pages
            
        Returns:
            Dict mapping state abbreviations to tuples of (url, state_name)
        """
        state_names = {
            'AL': 'alabama',
            'AK': 'alaska',
            'AZ': 'arizona',
            'AR': 'arkansas',
            'CA': 'california',
            'CO': 'colorado',
            'CT': 'connecticut',
            'DE': 'delaware',
            'FL': 'florida',
            'GA': 'georgia',
            'HI': 'hawaii',
            'ID': 'idaho',
            'IL': 'illinois',
            'IN': 'indiana',
            'IA': 'iowa',
            'KS': 'kansas',
            'KY': 'kentucky',
            'LA': 'louisiana',
            'ME': 'maine',
            'MD': 'maryland',
            'MA': 'massachusetts',
            'MI': 'michigan',
            'MN': 'minnesota',
            'MS': 'mississippi',
            'MO': 'missouri',
            'MT': 'montana',
            'NE': 'nebraska',
            'NV': 'nevada',
            'NH': 'new-hampshire',
            'NJ': 'new-jersey',
            'NM': 'new-mexico',
            'NY': 'new-york',
            'NC': 'north-carolina',
            'ND': 'north-dakota',
            'OH': 'ohio',
            'OK': 'oklahoma',
            'OR': 'oregon',
            'PA': 'pennsylvania',
            'RI': 'rhode-island',
            'SC': 'south-carolina',
            'SD': 'south-dakota',
            'TN': 'tennessee',
            'TX': 'texas',
            'UT': 'utah',
            'VT': 'vermont',
            'VA': 'virginia',
            'WA': 'washington',
            'WV': 'west-virginia',
            'WI': 'wisconsin',
            'WY': 'wyoming',
            'DC': 'district-of-columbia'
        }
        
        urls = {}
        for state in states:
            if state in state_names:
                state_name = state_names[state]
                
                # From screenshot we can see the actual URLs are in this format
                url = f"{base_url}/states/{state_name}/{state_name}-dispensaries/"
                
                urls[state] = (url, state_name)
            else:
                logger.warning(f"No URL mapping available for state: {state}")
        
        return urls

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the mapper
    mapper = ZipCodeMapper()
    
    # Process some ZIP codes
    test_zips = "99501, 98101, 97201, 90210"
    state_groups = mapper.process_zip_codes(test_zips)
    
    print("ZIP codes grouped by state:")
    for state, zips in state_groups.items():
        print(f"{state}: {', '.join(zips)}")
    
    # Generate URLs
    urls = mapper.states_to_urls(set(state_groups.keys()))
    
    print("\nPotAdvisor URLs:")
    for state, url in urls.items():
        print(f"{state}: {url}")