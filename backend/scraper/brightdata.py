import os
import urllib.parse
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

# Load .env variables from root or backend directory
load_dotenv()

class BrightDataManager:
    """
    Bright Data Scraping Adapter with Smart Credit Conservation.
    - Local/mock targets: Routes to local Playwright (0 Bright Data credits consumed).
    - Live external targets: Routes through Bright Data Scraping Browser (CDP)
      to bypass Cloudflare, CAPTCHAs, and anti-bot obstacles.
    """
    def __init__(self):
        self.wss_url = os.getenv("BRIGHT_DATA_WSS_URL", "").strip()
        self.proxy_url = os.getenv("BRIGHT_DATA_PROXY_URL", "").strip()
        self.customer_id = os.getenv("BRIGHT_DATA_CUSTOMER_ID", "").strip()
        self.zone_name = os.getenv("BRIGHT_DATA_ZONE_NAME", "scraping_browser").strip()
        self.password = os.getenv("BRIGHT_DATA_PASSWORD", "").strip()
        self.enabled = os.getenv("BRIGHT_DATA_ENABLED", "true").lower() in ["true", "1", "yes"]

    def is_configured(self) -> bool:
        if not self.enabled:
            return False
        if self.wss_url or self.proxy_url:
            return True
        if self.customer_id and self.password:
            return True
        return False

    def get_wss_url(self) -> Optional[str]:
        """Returns the WebSocket URL for Bright Data Scraping Browser."""
        if self.wss_url:
            return self.wss_url
        if self.customer_id and self.password:
            # Construct standard Bright Data Scraping Browser endpoint
            auth = f"brd-customer-{self.customer_id}-zone-{self.zone_name}:{self.password}"
            return f"wss://{auth}@brd.superproxy.io:9222"
        return None

    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """Returns proxy configuration for Chromium launch if using Web Unlocker."""
        if self.proxy_url:
            parsed = urllib.parse.urlparse(self.proxy_url)
            server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
            res = {"server": server}
            if parsed.username:
                res["username"] = parsed.username
            if parsed.password:
                res["password"] = parsed.password
            return res
        if self.customer_id and self.password:
            return {
                "server": "http://brd.superproxy.io:22225",
                "username": f"brd-customer-{self.customer_id}-zone-{self.zone_name}",
                "password": self.password
            }
        return None

    def should_use_brightdata(self, target_url: str) -> Tuple[bool, str]:
        """
        Credit Conservation Check:
        Returns (should_use, reason).
        """
        parsed = urllib.parse.urlparse(target_url)
        host = (parsed.hostname or "").lower()

        # 1. Localhost / Mock checks -> Always conserve credits
        if host in ["localhost", "127.0.0.1", "0.0.0.0", "::1"] or "mock" in parsed.path:
            return False, "Local/Mock Testground detected -> Conserving Bright Data credits (using local engine)."

        # 2. Check configuration
        if not self.is_configured():
            return False, "Bright Data not configured in .env -> Using local Playwright engine."

        return True, f"Live external target ({host}) -> Routing through Bright Data Scraping Browser."

