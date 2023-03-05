import os
from os import makedirs
import aiohttp
from pathlib import Path
from scraper import Scraper
from translator import Translator
import asyncio


class Main:

    def __init__(self, site: str, level: int = 1):
        self.site: str = site
        self.level: int = level
        self.site_loc: str = Path("./translated_site")
        self.scraper = Scraper(self.site, self.level)
        self.translator = Translator()

    async def start(self):
        await self.scraper.start()  # start scraping

        for page in self.scraper.res:
            # content = self.translator(page[1])
            self.__save_files(page[1], page[0])

    def __save_files(self, content: str, file_name: str):

        match file_name.split(".")[-1]:
            case "html":
                self._save(content, str(self.site_loc.joinpath(f"html/{file_name}")))
            case "css":
                self._save(content, str(self.site_loc.joinpath(f"static_files/css{file_name}")))
            case "js":
                self._save(content, str(self.site_loc.joinpath(f"static_files/js{file_name}")))
            case _:
                self._save(content, str(self.site_loc.joinpath(file_name)))

    @staticmethod
    def _save(content: str, location: str | Path):
        try:
            os.makedirs("/".join(location.split(os.path.sep)[:-1]), exist_ok=True)
        except FileNotFoundError:
            ...

        with open(location, 'w', encoding="utf-8") as file:
            file.write(content)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(Main("https://www.classcentral.com/").start())
    # loop.close()
    # asyncio.run(Main("https://www.classcentral.com/").start())
