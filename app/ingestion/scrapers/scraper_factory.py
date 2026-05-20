from app.ingestion.scrapers.base_scraper import BaseScraper, ConfigDrivenScraper
from app.ingestion.scrapers.vianet_scraper import VianetScraper
from app.ingestion.scrapers.worldlink_scraper import WorldLinkScraper

class ScraperFactory:
    @staticmethod
    def create(isp) -> BaseScraper:
        match isp.slug:
            case "worldlink": return WorldLinkScraper(isp)
            case "vianet":    return VianetScraper(isp)
            case _:           return ConfigDrivenScraper(isp)