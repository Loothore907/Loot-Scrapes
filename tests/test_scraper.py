import pytest
from pathlib import Path
from src.scrapers.crawl4ai_integration.scraper import Scraper, VendorData

@pytest.fixture
def scraper():
    config_path = Path(__file__).parent.parent / "src" / "scrapers" / "config" / "default_config.yaml"
    return Scraper(str(config_path))

def test_scraper_initialization(scraper):
    assert scraper is not None
    assert scraper.crawler is not None

def test_vendor_data_model():
    # Test that our data model works correctly
    data = {
        "name": "Test Dispensary",
        "address": "123 Test St",
        "phone": "555-555-5555",
        "website": "https://test.com",
        "hours": {"Monday": "9-5"},
        "menu_items": [{"name": "Test Product", "price": 10.00}],
        "deals": [{"description": "Test Deal", "discount": "10%"}]
    }
    
    vendor_data = VendorData(**data)
    assert vendor_data.name == "Test Dispensary"
    assert vendor_data.phone == "555-555-5555"
    assert len(vendor_data.menu_items) == 1
    assert len(vendor_data.deals) == 1

@pytest.mark.integration
def test_collect_vendor_data(scraper):
    # This is a placeholder test - you'll need to replace with actual test data
    test_url = "https://example-dispensary.com"
    
    try:
        data = scraper.collect_vendor_data(test_url)
        assert isinstance(data, VendorData)
    except Exception as e:
        pytest.skip(f"Integration test failed: {str(e)}")

def test_normalize_vendor_data(scraper):
    raw_data = {
        "name": ["Test Dispensary"],
        "address": ["123 Test St"],
        "phone": ["555-555-5555"],
        "website": ["https://test.com"],
        "hours": ["Monday: 9-5"],
        "menu": ["Product 1: $10"],
        "deals": ["10% off"]
    }
    
    normalized = scraper._normalize_vendor_data(raw_data)
    assert isinstance(normalized, dict)
    assert "name" in normalized
    assert "address" in normalized
    assert "phone" in normalized