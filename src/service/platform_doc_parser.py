# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
"""
Platform API Documentation Parser
Fetches and extracts relevant information from API documentation
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import re


class PlatformDocParser:
    """Parse and extract API documentation for ad platforms"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_documentation(self, url: str) -> str:
        """
        Fetch raw documentation content from URL

        Args:
            url: API documentation URL

        Returns:
            Raw HTML/text content
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Failed to fetch documentation from {url}: {str(e)}")

    def parse_api_structure(self, html_content: str, platform: str) -> Dict:
        """
        Parse API documentation to extract key information

        Args:
            html_content: Raw HTML content
            platform: Platform name

        Returns:
            Dictionary containing API structure information
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract all text content
        text_content = soup.get_text(separator="\n", strip=True)

        # Extract code blocks
        code_blocks = []
        for code_tag in soup.find_all(['code', 'pre']):
            code_blocks.append(code_tag.get_text(strip=True))

        # Look for common API patterns
        endpoints = self._extract_endpoints(text_content, code_blocks)
        auth_info = self._extract_auth_info(text_content)
        hierarchy = self._extract_hierarchy(text_content, platform)

        return {
            'platform': platform,
            'endpoints': endpoints,
            'authentication': auth_info,
            'hierarchy': hierarchy,
            'raw_text': text_content[:5000],  # First 5000 chars for context
            'code_examples': code_blocks[:10]  # First 10 code blocks
        }

    def _extract_endpoints(self, text: str, code_blocks: List[str]) -> List[Dict]:
        """Extract API endpoints from documentation"""
        endpoints = []

        # Common patterns for REST endpoints
        patterns = [
            r'(POST|GET|PUT|DELETE|PATCH)\s+(/[/\w\-{}:]+)',
            r'https?://[^/]+(/api/[/\w\-{}:]+)',
            r'(/v\d+/[/\w\-{}:]+)'
        ]

        text_to_search = text + '\n'.join(code_blocks)

        for pattern in patterns:
            matches = re.findall(pattern, text_to_search, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    endpoints.append({
                        'method': match[0] if len(match) > 1 else 'POST',
                        'path': match[1] if len(match) > 1 else match[0]
                    })
                else:
                    endpoints.append({'path': match})

        # Remove duplicates
        unique_endpoints = []
        seen = set()
        for ep in endpoints:
            key = f"{ep.get('method', 'POST')}:{ep.get('path', '')}"
            if key not in seen:
                seen.add(key)
                unique_endpoints.append(ep)

        return unique_endpoints[:20]  # Limit to 20 endpoints

    def _extract_auth_info(self, text: str) -> Dict:
        """Extract authentication information"""
        auth_info = {
            'type': 'oauth2',  # Default assumption
            'methods': []
        }

        text_lower = text.lower()

        # Detect OAuth
        if 'oauth' in text_lower or 'access token' in text_lower or 'bearer' in text_lower:
            auth_info['type'] = 'oauth2'
            auth_info['methods'].append('Bearer Token')

        # Detect API Key
        if 'api key' in text_lower or 'api_key' in text_lower:
            auth_info['methods'].append('API Key')

        # Extract header information
        header_patterns = [
            r'authorization:\s*bearer\s+',
            r'x-api-key',
            r'api-key'
        ]

        for pattern in header_patterns:
            if re.search(pattern, text_lower):
                auth_info['header_pattern'] = pattern
                break

        return auth_info

    def _extract_hierarchy(self, text: str, platform: str) -> List[str]:
        """
        Extract entity hierarchy (e.g., campaign -> ad_squad -> ad)
        """
        text_lower = text.lower()

        # Common ad platform hierarchy patterns
        hierarchies = {
            'snapchat': ['campaign', 'ad_squad', 'ad'],
            'pinterest': ['campaign', 'ad_group', 'ad'],
            'facebook': ['campaign', 'ad_set', 'ad'],
            'google': ['campaign', 'ad_group', 'ad'],
            'tiktok': ['campaign', 'ad_group', 'ad'],
            'default': ['campaign', 'ad_group', 'ad']
        }

        # Try to detect from text
        if 'ad squad' in text_lower or 'ad_squad' in text_lower:
            return ['campaign', 'ad_squad', 'ad']
        elif 'ad group' in text_lower or 'ad_group' in text_lower:
            return ['campaign', 'ad_group', 'ad']
        elif 'adset' in text_lower or 'ad set' in text_lower:
            return ['campaign', 'ad_set', 'ad']

        # Return platform-specific or default hierarchy
        return hierarchies.get(platform.lower(), hierarchies['default'])

    def get_api_info(self, url: str, platform: str) -> Dict:
        """
        Main method to fetch and parse API documentation

        Args:
            url: API documentation URL
            platform: Platform name

        Returns:
            Parsed API information
        """
        print(f"Fetching documentation from: {url}")
        html_content = self.fetch_documentation(url)

        print(f"Parsing API structure for {platform}...")
        api_info = self.parse_api_structure(html_content, platform)

        print(f"✓ Found {len(api_info['endpoints'])} endpoints")
        print(f"✓ Detected auth type: {api_info['authentication']['type']}")
        print(f"✓ Entity hierarchy: {' -> '.join(api_info['hierarchy'])}")

        return api_info
