from app.ingestion.scrapers.base_scraper import BaseScraper, ConfigDrivenScraper
from app.ingestion.scrapers.vianet_scraper import VianetScraper
from app.ingestion.scrapers.worldlink_scraper import WorldLinkScraper

class ScraperFactory:
    @staticmethod
    def create(isp) -> BaseScraper:
        match isp.slug:
            case "worldlink": return WorldLinkScraper(isp)
            case "vianet":    return WorldLinkScraper(isp)  # use HTTP scraper
            case "subisu":    return WorldLinkScraper(isp)  # use HTTP scraper
            case "dishhome":  return WorldLinkScraper(isp)  # use HTTP scraper
            case "cgnet":     return WorldLinkScraper(isp)  # use HTTP scraper
            case _:           return WorldLinkScraper(isp)