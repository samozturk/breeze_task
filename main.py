from src.utils.data_loader import load_venues_csv, write_to_sqlite
import pandas as pd
import logging
import sys
from src.scrapers.venue_enricher import VenueEnricher
from src.qualification.classifier import VenueClassifier
from src.email.generator import EmailGenerator



# Configure logging
def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/output/processing_log.txt'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


csv_file_path = 'data/input/venues.csv'
df = pd.read_csv(csv_file_path)
print(df.head())
df = load_venues_csv(csv_file_path)
write_to_sqlite(df)
print("CSV data has been written to SQLite database.")

enricher = VenueEnricher()
enricher.enrich_all()

classifier = VenueClassifier()
classifier.classify_venue()

generator = EmailGenerator()
generator.generate_emails()