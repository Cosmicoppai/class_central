import aiohttp
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Tuple
import asyncio


class Scraper:

    def __init__(self, site: str, level: int):
        self.site: str = site
        self.level: int = level
        self.links: List[str] = []
        self.visited: Set[str] = set()
        self._level = 0  # to track current level
        self.level = level  # no_of_levels the site has to be scraped
        self.res: List[Tuple[str, str]] = []

    async def start(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-GB,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36",
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            await self.scrape(session, self.site)
            await asyncio.gather(*[self.scrape(session, link) for link in self.links])

    async def scrape(self, session: aiohttp.ClientSession, link: str):
        async with session.get(link) as resp:
            if resp.status != 200:
                print(link, resp.status)

            resp = await resp.text()
            resp = resp.replace('src="/', f'src="{self.site}')
            resp = resp.replace("/fonts", f"{self.site}fonts")
            resp = resp.replace("/webpack", f"{self.site}webpack")

            if self._level < self.level:
                self._extract_links(resp)
                self._level += 1

            resp = resp.replace('href="https://www.classcentral.com/', 'href="/')
            resp = resp.replace('href="/', 'href="./')

            page_name = link.split(self.site+"/")
            if len(page_name) < 2:
                page_name = "home.html"
            else:
                page_name = page_name[-1] + ".html"

            self.res.append((page_name, resp))
            self.visited.add(link)

    def _extract_links(self, content: str):
        bs = BeautifulSoup(content, 'html.parser')
        for link in bs.findAll('a'):
            link = link.get("href")
            link = self.site+link.strip("/") if link[0] == "/" else link
            if link not in self.visited:
                self.links.append(link)


if __name__ == "__main__":
    asyncio.run(Scraper("https://www.classcentral.com/", 1).start())
