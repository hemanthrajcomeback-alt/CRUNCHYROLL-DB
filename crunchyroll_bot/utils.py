import aiohttp
from bs4 import BeautifulSoup

async def get_episodes(series_url):
    """
    Returns a list of tuples: [(episode_title, episode_url), ...]
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(series_url, headers=headers) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")

            episodes = []
            # Crunchyroll episode links
            for a in soup.select("a[data-qa='episode-link']"):
                title = a.get_text(strip=True)
                url = "https://www.crunchyroll.com" + a["href"]
                episodes.append((title, url))

            return episodes