# Breeze Venue Screening & Outreach Automation

## Overview

This project implements an automated workflow to identify, qualify, and reach out to ideal first-date venues for Breeze. The system processes a CSV file of 500 Brighton venues, enriches the data through web scraping, applies qualification criteria to identify suitable venues, and generates personalized outreach emails.

## Architecture

The solution consists of several key components:

1. **Database Layer**: SQLite database for storing and organizing venue data
2. **Data Enrichment**: Mockup web scraping module to gather additional venue information
3. **Qualification Engine**: Rule-based system to classify venues based on specified criteria
4. **Email Generation**: Automated personalized email creation for qualified venues
5. **Export System**: CSV output generation for qualified venues

## Qualification Criteria

The system should identify ideal first-date venues based on:

- **Venue Types**: Bars, wine bars, cocktail bars, cafes, taverns, pubs, breweries, restaurants
- **Location**: Centrally located or easily accessible via public transport
- **Atmosphere**: Cozy, inviting with ambient lighting and conversation-friendly music levels
- **Target Demographics**: Suitable for ages 25-35 (flexible 23-45)
- **Pricing**: Reasonable to slightly upscale (excludes high-end Michelin establishments)
- **Size**: Medium to large (8+ tables for 2+ people)
- **Hours**: Open late afternoon weekdays, early afternoon weekends (especially Fri/Sat)
- **Reviews**: Preferably 10+ reviews, but new venues meeting other criteria included
- **Quality**: High ratings and positive feedback on review platforms

**Exclusions**: Fast food establishments, kebab shops, burger joints, Michelin-starred restaurants

</br>
But only identifies type for a mockup service. In production, it should use google places api and OSM to add extra features.


## Project Structure

```
breeze-venue-automation/
├── src/
│   ├── scrapers/
│   │   ├── venue_enricher.py  # Web scraping for venue data
│   │   └── geo_loc.py # Still not function, to add distance from town center using geopy and OSM
│   ├── qualification/
│   │   ├── classifier.py      # Venue qualification logic
│   │   └── criteria.py        # Qualification criteria definitions
│   ├── email/
│   │   ├── generator.py       # Email template and generation
│   │   └── templates/         # Email templates
│   └── utils/
│       └── data_loader.py     # CSV processing utilities
├── data/
│   ├── input/
│   │   └── venues.csv         # Original venue data
│   └── output/
│       └── generated_emails.txt
├── tests/                    # Should be populated when moving from MVP to PRD
├── docker/
│   └── Dockerfile
├── main.py                    # Main application entry point
└── README.md
```

## Key Features

### Data Enrichment
- Web scraping for venue websites, descriptions, and contact information
- Mock data generation for MVP (with production scaling notes)

### Intelligent Qualification
- Criteria based venue assessment
- Flexible scoring system

### Personalized Outreach
- Dynamic email generation based on venue characteristics
- Template-based messaging with venue-specific details
- Bulk email preparation for qualified venues

## Setup & Installation

### Prerequisites
- Docker (recommended)
- Python 3.12 (if running locally)

### Using Docker (Recommended)

1. Clone the repository
2. Build the Docker image:
   ```bash
   docker build -t breeze .
   ```
3. Run the container:
   ```bash
   docker run -v $(pwd)/data:/app/data breeze
   ```

### Local Installation

1. Clone the repository

2. Install dependencies:
   ```bash
   uv sync
   ```
3. Run the application:
   ```bash
   uv run main.py
   ```

## Configuration


### API Keys (Production Mode)
For production deployment, the following APIs would be integrated:
- Google Places API for venue details
- Email service provider API (SendGrid, Mailgun, etc.)
- Review aggregation services

**Note**: MVP version includes mock data and doesn't require external API keys.

## Running the Application

### MVP Mode (Default)
```bash
uv run main.py
```
This mode uses mock data for quick demonstration and testing.

### Production Mode
```bash
# Placeholder
```

## Output Files

The system generates:
1. **generated_emails.txt**: Personalized outreach emails for each qualified venue
2.  Writes enriched and qualified venues to sqlite databased as well as the original csv.

## Scaling for Production

### Web Scraping Enhancement
- Implement rate limiting and retry mechanisms
- Add proxy rotation for large-scale scraping
- Integrate with commercial data providers
- Implement caching to avoid redundant requests
- Develop an image classifier based on google places api venue images to detect if it is a suitable venue for a first date

### Email Delivery
- Integration with email service providers
- Email template A/B testing
- Delivery tracking and analytics
- Bounce handling and list management
- Use agents to write (and maybe send) emails

### Database Optimization
- Migration to PostgreSQL for production
- Indexing strategy for large datasets
- Data backup and recovery procedures
- Multi-city expansion support
- Add schema constraints on tables

### Monitoring & Maintenance
- Automated quality checks for scraped data
- Performance monitoring and alerting
- Regular data freshness validation
- Error handling and notification systems

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

For specific test categories:
```bash
python -m pytest tests/test_qualification.py -v
python -m pytest tests/test_scraping.py -v
```

## Performance Considerations

- **Processing Time**: ~2-3 minutes for 500 venues in MVP mode
- **Memory Usage**: ~50MB for dataset processing
- **Storage**: ~10MB for enriched venue database
- **Network**: Respectful scraping with 1-second delays

## Troubleshooting

### Common Issues
1. **Scraping Failures**: Check internet connection and target website availability
2. **Database Errors**: Ensure write permissions in data directory
3. **Memory Issues**: Reduce batch size for large datasets


---

*This README provides a comprehensive overview of the automated venue screening and outreach system. The implementation prioritizes getting a working MVP within the 4-hour timeframe while providing clear paths for production scaling.*



