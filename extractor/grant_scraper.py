#!/usr/bin/env python3
"""
Automated Monthly Grant Search and CSV Management System
Searches for grants monthly and appends only new findings to CSV file
"""

import os
import sys
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set, Optional
import requests
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('grant_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GrantScraperConfig:
    """Configuration management for the grant scraper"""
    
    def __init__(self, config_file: str = "grant_scraper_config.json"):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "search_criteria": {
                "keywords": ["research grant", "innovation funding", "nonprofit grant"],
                "exclude_keywords": ["expired", "closed"],
                "funding_sources": [
                    "https://grants.gov",
                    "https://www.nsf.gov/funding/",
                    # Add more sources as needed
                ]
            },
            "csv_settings": {
                "output_file": "grants_database.csv",
                "columns": [
                    "Grant Name","Administering Body","Grant Purpose","Application Deadline",
                    "Funding Amount","Co-contribution Requirements","Eligibility Criteria",
                    "Assessment Criteria","Application Complexity","Web Link","Level of Complexity"
                    "discovered_date",
                    "hash_key"  # For deduplication
                ]
            },
            "deduplication": {
                "key_fields": ["Grant Name","Administering Body","Application Deadline"],  # Fields to check for duplicates
                "similarity_threshold": 0.85  # For fuzzy matching if needed
            },
            "schedule": {
                "day": 1,  # First day of month
                "hour": 9,  # 9 AM
                "minute": 0
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

class GrantSpider(scrapy.Spider):
    """Scrapy spider for grant websites"""
    
    name = 'grant_spider'
    
    def __init__(self, search_terms=None, funding_sources=None, *args, **kwargs):
        super(GrantSpider, self).__init__(*args, **kwargs)
        self.search_terms = search_terms or []
        self.funding_sources = funding_sources or []
        self.found_grants = []
    
    def start_requests(self):
        """Generate initial requests based on search criteria"""
        # Use funding sources from config
        for search_term in self.search_terms:
            for funding_source in self.funding_sources:
                # Build URL based on funding source
                if 'grants.gov' in funding_source:
                    url = f"{funding_source}/search-results-xml?query={search_term}"
                else:
                    # For other sources, use the URL directly or adapt as needed
                    url = f"{funding_source}?query={search_term}"
                yield scrapy.Request(url, self.parse)
    
    def parse(self, response):
        """Parse grant listings from search results"""
        # Extract grant information based on website structure
        grants = response.css('div.grant-listing')  # Adjust selector as needed
        
        for grant in grants:
            grant_data = {
                'title': grant.css('h3::text').get(),
                'agency': grant.css('.agency::text').get(),
                'funding_amount': grant.css('.amount::text').get(),
                'deadline': grant.css('.deadline::text').get(),
                'url': grant.css('a::attr(href)').get(),
                'description': grant.css('.description::text').get(),
                'discovered_date': datetime.now().isoformat(),
            }
            
            # Generate hash for deduplication
            grant_data['hash_key'] = self.generate_hash(grant_data)
            self.found_grants.append(grant_data)
        
        # Follow pagination if exists
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def generate_hash(self, grant_data: Dict) -> str:
        """Generate hash for deduplication"""
        # Use key fields to create unique identifier
        key_string = f"{grant_data.get('title', '')}{grant_data.get('agency', '')}{grant_data.get('deadline', '')}"
        return hashlib.md5(key_string.encode()).hexdigest()

class GrantScraper:
    """Main grant scraper class"""
    
    def __init__(self, config_file: str = "grant_scraper_config.json"):
        self.config = GrantScraperConfig(config_file)
        self.csv_file = self.config.config['csv_settings']['output_file']
        self.columns = self.config.config['csv_settings']['columns']
    
    def initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.csv_file, index=False)
            logger.info(f"Initialized CSV file: {self.csv_file}")
    
    def load_existing_data(self) -> pd.DataFrame:
        """Load existing grant data from CSV"""
        if os.path.exists(self.csv_file):
            return pd.read_csv(self.csv_file)
        return pd.DataFrame(columns=self.columns)
    
    def scrape_grants_with_scrapy(self) -> List[Dict]:
        """Run Scrapy spider to collect grants"""
        logger.info("Starting Scrapy spider...")
        
        # Configure Scrapy settings
        settings = get_project_settings()
        settings.update({
            'USER_AGENT': 'Grant Scraper Bot 1.0',
            'ROBOTSTXT_OBEY': True,
            'DOWNLOAD_DELAY': 1,
            'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        })
        
        # Run spider
        process = CrawlerProcess(settings)
        spider = GrantSpider(
            search_terms=self.config.config['search_criteria']['keywords'],
            funding_sources=self.config.config['search_criteria']['funding_sources']
        )
        process.crawl(spider)
        process.start()
        
        return spider.found_grants
    
    def scrape_grants_simple(self) -> List[Dict]:
        """Alternative simple scraping method for APIs/RSS feeds"""
        logger.info("Starting simple grant scraping...")
        grants_found = []
        
        try:
            # Use funding sources from config instead of hardcoded URLs
            for keyword in self.config.config['search_criteria']['keywords']:
                for funding_source in self.config.config['search_criteria']['funding_sources']:
                    # Build URL based on funding source
                    if 'grants.gov' in funding_source:
                        url = f"{funding_source}/search-results-xml?query={keyword}"
                    elif 'health.gov.au' in funding_source:
                        # For Australian health grants, use the direct URL
                        url = funding_source
                    else:
                        # For other sources, adapt as needed
                        url = f"{funding_source}?query={keyword}"
                    
                    response = requests.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        # Parse response (implement based on actual API structure)
                        grants_data = self.parse_grants_api_response(response.content)
                        grants_found.extend(grants_data)
                
        except Exception as e:
            logger.error(f"Error during simple scraping: {e}")
        
        return grants_found
        
    def parse_grants_api_response(self, content: bytes) -> List[Dict]:
        """Parse API response to extract grant data"""
        # Implement based on actual API structure
        # This is a placeholder
        grants = []
        # Your parsing logic here
        return grants
    
    def deduplicate_grants(self, new_grants: List[Dict], existing_df: pd.DataFrame) -> List[Dict]:
        """Remove duplicates from new grants"""
        if existing_df.empty:
            return new_grants
        
        existing_hashes = set(existing_df['hash_key'].dropna())
        deduped_grants = []
        
        for grant in new_grants:
            if grant.get('hash_key') not in existing_hashes:
                deduped_grants.append(grant)
        
        logger.info(f"Found {len(new_grants)} grants, {len(deduped_grants)} are new")
        return deduped_grants
    
    def append_to_csv(self, new_grants: List[Dict]):
        """Append new grants to CSV file"""
        if not new_grants:
            logger.info("No new grants to add")
            return
        
        # Create DataFrame from new grants
        new_df = pd.DataFrame(new_grants)
        
        # Ensure all required columns exist
        for col in self.columns:
            if col not in new_df.columns:
                new_df[col] = None
        
        # Reorder columns to match configuration
        new_df = new_df[self.columns]
        
        # Append to CSV
        new_df.to_csv(self.csv_file, mode='a', header=False, index=False)
        logger.info(f"Appended {len(new_grants)} new grants to {self.csv_file}")
    
    def run_monthly_search(self):
        """Main method to run the monthly search"""
        try:
            logger.info("Starting monthly grant search...")
            
            # Initialize CSV if needed
            self.initialize_csv()
            
            # Load existing data
            existing_df = self.load_existing_data()
            logger.info(f"Loaded {len(existing_df)} existing grants")
            
            # Scrape new grants (choose method based on your needs)
            # Option 1: Use Scrapy for complex scraping
            # new_grants = self.scrape_grants_with_scrapy()
            
            # Option 2: Use simple requests for APIs
            new_grants = self.scrape_grants_simple()
            
            # Deduplicate
            unique_grants = self.deduplicate_grants(new_grants, existing_df)
            
            # Append to CSV
            self.append_to_csv(unique_grants)
            
            logger.info("Monthly grant search completed successfully")
            
        except Exception as e:
            logger.error(f"Error during monthly search: {e}")
            raise

def setup_scheduler():
    """Setup APScheduler for monthly runs"""
    scraper = GrantScraper()
    scheduler = BlockingScheduler()
    
    # Load schedule configuration
    schedule_config = scraper.config.config['schedule']
    
    # Schedule monthly job
    trigger = CronTrigger(
        day=schedule_config['day'],
        hour=schedule_config['hour'], 
        minute=schedule_config['minute']
    )
    
    scheduler.add_job(
        func=scraper.run_monthly_search,
        trigger=trigger,
        id='monthly_grant_search',
        name='Monthly Grant Search',
        replace_existing=True
    )
    
    logger.info(f"Scheduled monthly grant search for day {schedule_config['day']} at {schedule_config['hour']}:{schedule_config['minute']:02d}")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")

def run_once():
    """Run the scraper once (for testing)"""
    scraper = GrantScraper()
    scraper.run_monthly_search()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Run once for testing
        run_once()
    else:
        # Start scheduler for continuous operation
        setup_scheduler()