from app.ingestion.scrapers.base_scraper import BaseScraper, ConfigDrivenScraper
from app.ingestion.scrapers.worldlink_scraper import WorldLinkScraper
from app.ingestion.scrapers.vianet_scraper import VianetScraper
from app.ingestion.scrapers.cgnet_scraper import CgnetScraper
from app.ingestion.scrapers.subisu_scraper import SubisuScraper
from app.ingestion.scrapers.dishhome_scraper import DishhomeScraper


class ScraperFactory:
    @staticmethod
    def create(isp):
        match isp.slug:
            case "worldlink": return WorldLinkScraper(isp)
            case "vianet":    return VianetScraper(isp)    # httpx table parser
            case "cgnet":     return CgnetScraper(isp)     # httpx HTML parser
            case "subisu":    return SubisuScraper(isp)    # Playwright + API intercept
            case "dishhome":  return DishhomeScraper(isp)  # Playwright + API intercept
            case _:           return WorldLinkScraper(isp)
