import logging
import random
from typing import Optional

import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

from backend import config


def fetch_url_content(url: str, timeout: int = 5) -> Optional[requests.Response]:
    """Fetches the content from a URL and returns the response object. Sets browser-like headers to avoid blocks."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Edge/91.0.864.59",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]

    # Randomly select a user-agent from the list
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.5",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
        return response
    except Exception as e:
        logging.warning(f"Error fetching URL content: {e}")
        return None


def parse_html_for_image_url(html: str, base_url: str) -> str | None:
    """Parses HTML for Open Graph, Twitter Card, or favicon image URLs."""
    soup = BeautifulSoup(html, 'html.parser')

    # amazon pages have "hiRes" as image
    # search using regex
    amazon_img = soup.find('img', attrs={'id': 'landingImage'})
    if amazon_img and amazon_img.get('data-old-hires'):
        return urljoin(base_url, amazon_img['data-old-hires'])

    # Try Open Graph
    og_img = soup.find('meta', property='og:image')
    if og_img and og_img.get('content'):
        return urljoin(base_url, og_img['content'])
    # Try Twitter Card
    tw_img = soup.find('meta', attrs={'name': 'twitter:image'})
    if tw_img and tw_img.get('content'):
        return urljoin(base_url, tw_img['content'])
    # Try favicon
    icon_link = soup.find('link', rel=lambda v: v and 'icon' in v.lower())
    if icon_link and icon_link.get('href'):
        return urljoin(base_url, icon_link['href'])
    return None


def download_and_save_image(img_url: str, fallback_name: str = 'preview_image') -> Path | None:
    """Downloads an image from a URL and saves it locally as PNG. Returns the local path."""
    try:

        img_response = fetch_url_content(img_url, timeout=5)
        img_response.raise_for_status()
        image = Image.open(BytesIO(img_response.content))
        parsed_url = urlparse(img_url)
        # Always use .png extension for consistency
        # random number as filename:
        filename = f"{random.randint(1000, 9999)}.png"
        local_path = config.previews / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)
        # Convert to RGB if needed (e.g., for JPEG or palette images)
        if image.mode in ("RGBA", "P", "LA"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")
        image.save(local_path, format="PNG")
        return local_path
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


def preview_external_links(link: str) -> str:
    """
    Fetches a preview image from the external link (Open Graph, Twitter Card, favicon, or direct image),
    stores it locally, and returns the path to the stored image.
    """
    logging.info(f"Fetching link preview for: {link}")
    response = fetch_url_content(link)
    img_path = None
    if not response:
        logging.info("No response received for link preview.")

    else:
        if 'image' in response.headers.get('Content-Type', ''):
            img_path = download_and_save_image(link)

        img_url = parse_html_for_image_url(response.text, link)
        if img_url:
            img_path = download_and_save_image(img_url)

    if img_path is None:
        logging.info("No preview image could be fetched.")
        return config.default_preview_image_path

    else:
        logging.info(f"Preview image saved at: {img_path}")
        return config.previews_url + img_path.name
