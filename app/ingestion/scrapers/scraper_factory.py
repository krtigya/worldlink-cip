from app.ingestion.scrapers.base_scraper import BaseScraper, ConfigDrivenScraper
from app.ingestion.scrapers.worldlink_scraper import WorldLinkScraper
from app.ingestion.scrapers.vianet_scraper import VianetScraper
from app.ingestion.scrapers.cgnet_scraper import CgnetScraper
from app.ingestion.scrapers.subisu_scraper import SubisuScraper
from app.ingestion.scrapers.dishhome_scraper import DishhomeScraper


class ScraperFactory:
    @staticmethod
    def create(isp) -> BaseScraper:
        match isp.slug:
            case "worldlink": return WorldLinkScraper(isp)
            case "vianet":    return VianetScraper(isp)
            case "cgnet":     return CgnetScraper(isp)
            case "subisu":    return SubisuScraper(isp)
            case "dishhome":  return DishhomeScraper(isp)
            case _:           return WorldLinkScraper(isp)
