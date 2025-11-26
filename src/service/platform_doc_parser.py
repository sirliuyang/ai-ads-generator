# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com

"""
Enhanced Platform API Documentation Parser
Fetches and extracts detailed information from API documentation
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import re
import json


class PlatformDocParser:
    """Parse and extract comprehensive API documentation for ad platforms"""

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
        Parse API documentation to extract comprehensive information

        Args:
            html_content: Raw HTML content
            platform: Platform name

        Returns:
            Dictionary containing detailed API structure information
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract all text content
        text_content = soup.get_text(separator='\n', strip=True)

        # Extract code blocks with better parsing
        code_blocks = self._extract_code_blocks(soup)

        # Extract endpoints with detailed information
        endpoints = self._extract_detailed_endpoints(text_content, code_blocks, soup)

        # Extract authentication information
        auth_info = self._extract_auth_info(text_content)

        # Extract entity hierarchy
        hierarchy = self._extract_hierarchy(text_content, platform)

        # Extract request/response schemas
        schemas = self._extract_schemas(soup, text_content)

        # Extract dependencies and workflow
        workflow = self._extract_workflow(text_content, endpoints, platform)

        # Extract base URL patterns
        base_url = self._extract_base_url(text_content, endpoints, platform)

        return {
            'platform': platform,
            'base_url': base_url,
            'endpoints': endpoints,
            'authentication': auth_info,
            'hierarchy': hierarchy,
            'schemas': schemas,
            'workflow': workflow,
            'raw_text': text_content[:10000],  # First 10000 chars for context
            'code_examples': code_blocks[:20]  # First 20 code blocks
        }

    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[str]:
        """Extract code blocks from documentation"""
        code_blocks = []

        # Try different code block tags
        for tag in ['code', 'pre', 'div.highlight', 'div.code-block']:
            elements = soup.select(tag)
            for elem in elements:
                code_text = elem.get_text(strip=True)
                if len(code_text) > 20:  # Filter out very short snippets
                    code_blocks.append(code_text)

        return code_blocks

    def _extract_detailed_endpoints(
            self,
            text: str,
            code_blocks: List[str],
            soup: BeautifulSoup
    ) -> List[Dict]:
        """Extract detailed API endpoints with methods, paths, and descriptions"""
        endpoints = []
        seen = set()

        # Combine text and code blocks for analysis
        content = text + '\n' + '\n'.join(code_blocks)

        # Enhanced patterns for endpoint detection
        patterns = [
            # Standard REST format: POST /v1/campaigns
            r'(POST|GET|PUT|DELETE|PATCH)\s+(/[\w\-/{}:]+)',
            # URL format: https://adsapi.snapchat.com/v1/campaigns
            r'https?://[\w\-.]+(/v\d+/[\w\-/{}:]+)',
            # Path only: /adaccounts/{id}/campaigns
            r'(/adaccounts/[{\w\-}]+/[\w\-/{}:]+)',
            r'(/campaigns/[{\w\-}]+/[\w\-/{}:]+)',
            r'(/media/[{\w\-}]+/[\w\-/{}:]+)',
            r'(/creatives)',
            r'(/adsquads/[{\w\-}]+/[\w\-/{}:]+)'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match.groups(), tuple) and len(match.groups()) >= 2:
                    method = match.group(1).upper()
                    path = match.group(2)
                elif isinstance(match.groups(), tuple) and len(match.groups()) == 1:
                    path = match.group(1)
                    # Infer method from context
                    method = self._infer_http_method(path, content)
                else:
                    continue

                # Clean path
                path = path.strip()

                # Create unique key
                key = f"{method}:{path}"
                if key in seen:
                    continue
                seen.add(key)

                # Extract description
                description = self._extract_endpoint_description(path, soup, text)

                # Determine resource type
                resource_type = self._determine_resource_type(path)

                endpoint_info = {
                    'method': method,
                    'path': path,
                    'description': description,
                    'resource_type': resource_type,
                    'requires_parent': '{' in path or '/' in path[1:]  # Has path params
                }

                endpoints.append(endpoint_info)

        # Sort by typical workflow order
        priority_order = ['campaign', 'squad', 'media', 'creative', 'ad']
        endpoints.sort(key=lambda x: self._endpoint_priority(x, priority_order))

        return endpoints[:30]  # Limit to 30 most relevant endpoints

    def _infer_http_method(self, path: str, context: str) -> str:
        """Infer HTTP method from path and context"""
        path_lower = path.lower()

        # Look for method mentions near the path in context
        path_index = context.lower().find(path_lower)
        if path_index != -1:
            nearby_text = context[max(0, path_index - 100):path_index + 100].lower()
            for method in ['post', 'get', 'put', 'delete', 'patch']:
                if method in nearby_text:
                    return method.upper()

        # Default heuristics
        if '/upload' in path_lower:
            return 'POST'
        elif any(x in path_lower for x in ['create', 'new']):
            return 'POST'
        elif '{id}' in path and path.endswith('}'):
            return 'GET'

        return 'POST'  # Default

    def _extract_endpoint_description(
            self,
            path: str,
            soup: BeautifulSoup,
            text: str
    ) -> str:
        """Extract description for an endpoint"""
        # Try to find description near the endpoint mention
        path_lower = path.lower()
        lines = text.split('\n')

        for i, line in enumerate(lines):
            if path_lower in line.lower():
                # Look at surrounding lines
                context_lines = lines[max(0, i - 2):min(len(lines), i + 3)]
                description = ' '.join(context_lines).strip()
                if len(description) > 200:
                    description = description[:200] + '...'
                return description

        return f"API endpoint: {path}"

    def _determine_resource_type(self, path: str) -> str:
        """Determine the resource type from path"""
        path_lower = path.lower()

        if 'campaign' in path_lower:
            return 'campaign'
        elif 'squad' in path_lower or 'adgroup' in path_lower:
            return 'ad_squad'
        elif 'media' in path_lower:
            return 'media'
        elif 'creative' in path_lower:
            return 'creative'
        elif path_lower.endswith('/ads') or '/ads/' in path_lower:
            return 'ad'

        return 'unknown'

    def _endpoint_priority(self, endpoint: Dict, priority_order: List[str]) -> int:
        """Calculate priority for sorting endpoints"""
        resource_type = endpoint.get('resource_type', 'unknown')
        try:
            return priority_order.index(resource_type)
        except ValueError:
            return len(priority_order)

    def _extract_auth_info(self, text: str) -> Dict:
        """Extract detailed authentication information"""
        auth_info = {
            'type': 'oauth2',
            'methods': [],
            'token_location': 'header',
            'header_name': 'Authorization',
            'header_format': 'Bearer {token}'
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
            (r'authorization:\s*bearer\s+', 'Authorization', 'Bearer {token}'),
            (r'x-api-key', 'X-API-Key', '{token}'),
        ]

        for pattern, header_name, format_str in header_patterns:
            if re.search(pattern, text_lower):
                auth_info['header_name'] = header_name
                auth_info['header_format'] = format_str
                break

        return auth_info

    def _extract_hierarchy(self, text: str, platform: str) -> List[str]:
        """Extract entity hierarchy with better detection"""
        text_lower = text.lower()

        # Platform-specific hierarchies
        known_hierarchies = {
            'snapchat': ['campaign', 'ad_squad', 'ad'],
            'pinterest': ['campaign', 'ad_group', 'ad'],
            'facebook': ['campaign', 'ad_set', 'ad'],
            'google': ['campaign', 'ad_group', 'ad'],
            'tiktok': ['campaign', 'ad_group', 'ad'],
        }

        # Try to detect from text
        if 'ad squad' in text_lower or 'adsquad' in text_lower:
            return ['campaign', 'ad_squad', 'ad']
        elif 'ad group' in text_lower or 'adgroup' in text_lower:
            return ['campaign', 'ad_group', 'ad']
        elif 'ad set' in text_lower or 'adset' in text_lower:
            return ['campaign', 'ad_set', 'ad']

        # Return known hierarchy or default
        return known_hierarchies.get(platform.lower(), ['campaign', 'ad_group', 'ad'])

    def _extract_schemas(self, soup: BeautifulSoup, text: str) -> Dict:
        """Extract request/response schemas"""
        schemas = {}

        # Look for JSON examples in code blocks
        code_blocks = soup.find_all(['code', 'pre'])
        for block in code_blocks:
            code_text = block.get_text()
            if '{' in code_text and '}' in code_text:
                try:
                    # Try to parse as JSON
                    json_obj = json.loads(code_text)
                    # Try to determine what type of schema this is
                    if 'campaign' in code_text.lower():
                        schemas['campaign'] = json_obj
                    elif 'squad' in code_text.lower() or 'adgroup' in code_text.lower():
                        schemas['ad_squad'] = json_obj
                    elif 'creative' in code_text.lower():
                        schemas['creative'] = json_obj
                except:
                    pass

        return schemas

    def _extract_workflow(self, text: str, endpoints: List[Dict], platform: str) -> Dict:
        """Extract workflow information and dependencies"""
        workflow = {
            'steps': [],
            'dependencies': {},
            'notes': []
        }

        # Analyze text for workflow clues
        text_lower = text.lower()

        # Common workflow patterns
        if 'first' in text_lower and 'campaign' in text_lower:
            workflow['notes'].append('Create campaign first')

        if 'before' in text_lower or 'after' in text_lower:
            # Extract sentences with workflow information
            sentences = text.split('.')
            for sentence in sentences:
                if 'before' in sentence.lower() or 'after' in sentence.lower():
                    workflow['notes'].append(sentence.strip())

        # Infer workflow from endpoints
        resource_order = []
        for endpoint in endpoints:
            resource_type = endpoint.get('resource_type')
            if resource_type and resource_type not in resource_order:
                resource_order.append(resource_type)

        workflow['steps'] = resource_order

        # Build dependency map from endpoints
        for endpoint in endpoints:
            if endpoint.get('requires_parent'):
                resource = endpoint.get('resource_type')
                path = endpoint.get('path', '')

                # Detect parent dependencies from path
                if '{campaign' in path.lower():
                    workflow['dependencies'][resource] = workflow['dependencies'].get(resource, []) + ['campaign']
                if '{squad' in path.lower() or '{adgroup' in path.lower():
                    workflow['dependencies'][resource] = workflow['dependencies'].get(resource, []) + ['ad_squad']
                if '{media' in path.lower():
                    workflow['dependencies'][resource] = workflow['dependencies'].get(resource, []) + ['media']

        return workflow

    def _extract_base_url(self, text: str, endpoints: List[Dict], platform: str) -> str:
        """Extract base URL from documentation"""
        # Look for base URL in text
        base_url_pattern = r'https?://[\w\-.]+\.com/v\d+'
        matches = re.findall(base_url_pattern, text)

        if matches:
            # Return most common base URL
            from collections import Counter
            counter = Counter(matches)
            return counter.most_common(1)[0][0]

        # Common base URLs for known platforms
        known_base_urls = {
            'snapchat': 'https://adsapi.snapchat.com/v1',
            'pinterest': 'https://api.pinterest.com/v5',
            'facebook': 'https://graph.facebook.com/v18.0',
            'tiktok': 'https://business-api.tiktok.com/open_api/v1.3',
        }

        return known_base_urls.get(platform.lower(), f'https://api.{platform}.com/v1')

    def get_api_info(self, url: str, platform: str) -> Dict:
        """
        Main method to fetch and parse comprehensive API documentation

        Args:
            url: API documentation URL
            platform: Platform name

        Returns:
            Comprehensive API information
        """
        print(f"Fetching documentation from: {url}")
        html_content = self.fetch_documentation(url)

        print(f"Parsing comprehensive API structure for {platform}...")
        api_info = self.parse_api_structure(html_content, platform)

        print(f"✓ Found {len(api_info['endpoints'])} endpoints")
        print(f"✓ Detected auth type: {api_info['authentication']['type']}")
        print(f"✓ Entity hierarchy: {' -> '.join(api_info['hierarchy'])}")
        print(f"✓ Base URL: {api_info['base_url']}")
        if api_info['workflow']['steps']:
            print(f"✓ Workflow steps: {' -> '.join(api_info['workflow']['steps'])}")

        return api_info
