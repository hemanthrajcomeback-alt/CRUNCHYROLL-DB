
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def fetch_episodes(series_url):
    """
    Fetches the list of episodes from a Crunchyroll series page using Playwright
    to handle dynamically loaded content.
    """
    episodes = []
    seen_links = set()
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(series_url)

            # Wait for the "Episodes" text to appear on the page
            await page.wait_for_selector("xpath=//*[contains(., 'Episodes')]")

            html = await page.content()
            await browser.close()

            soup = BeautifulSoup(html, 'html.parser')

            # Look for a more specific container for the episodes
            episode_container = soup.find('div', {'data-testid': 'episodes-list'}) or soup.body

            all_links = episode_container.find_all('a')
            for link in all_links:
                href = link.get('href')
                if href and '/watch/' in href:
                    if href not in seen_links:
                        # Check for a title attribute as an additional filter
                        if link.get('title'):
                            title = link.get('title')
                            full_url = f"https://www.crunchyroll.com{href}"
                            episodes.append((title, full_url))
                            seen_links.add(href)

    except Exception as e:
        print(f"An error occurred while fetching episodes: {e}")

    return episodes
