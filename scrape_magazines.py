from rss.eurogamer import EurogamerScraper
from rss.gamasutra import GamasutraScraper
from rss.gameinformer import GameinformerScraper
from rss.ign import IgnScraper
from rss.kotaku import KotakuScraper
from rss.gamespot import GamespotScraper

if __name__ == "__main__":
    print("eurogamer ...")
    eurogamer = EurogamerScraper()
    print("gamasutra ...")
    gamasutra = GamasutraScraper()
    print("gameinformer ...")
    gameinformer = GameinformerScraper()
    print("ign ...")
    ign = IgnScraper()
    print("kotaku ...")
    kotaku = KotakuScraper()
    print("Gamespot")
    gamespot = GamespotScraper()