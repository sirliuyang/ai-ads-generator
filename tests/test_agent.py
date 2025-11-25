# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.service import Agent
from src.service.platform_doc_parser import DocParser
from src.service.llm_remote import CodeGenerator


class TestAgent:
    """Tests for the AI Agent."""

    def test_agent_initialization(self):
        agent = Agent()
        assert agent is not None
        assert hasattr(agent, 'fetcher')
        assert hasattr(agent, 'generator')

    def test_generate_api_client_mock_mode(self, tmp_path):
        agent = Agent()

        # Test mock generation
        result = agent.generate_api_client(
            platform="test_platform",
            docs_url="https://example.com/docs",
            mock_auth=True,
            output_dir=str(tmp_path)
        )

        assert result is not None
        assert os.path.exists(result)
        assert result.endswith("test_platform_api.py")

        # Verify mock content
        with open(result, 'r') as f:
            content = f.read()
            assert "Mock Mode" in content
            assert "_generate_mock_id" in content

    def test_generate_api_client_production_mode(self, tmp_path):
        agent = Agent()

        # Test production generation
        result = agent.generate_api_client(
            platform="test_prod_platform",
            docs_url="https://example.com/docs",
            mock_auth=False,
            output_dir=str(tmp_path)
        )

        assert result is not None
        assert os.path.exists(result)

        # Verify production content
        with open(result, 'r') as f:
            content = f.read()
            assert "Production Mode" in content
            assert "requests.post" in content


class TestDocumentationFetcher:
    """Tests for documentation fetching."""

    def test_fetcher_initialization(self):
        fetcher = DocParser()
        assert fetcher is not None

    def test_extract_api_structure(self):
        fetcher = DocParser()

        # Mock HTML content
        mock_html = """
        <html>
            <body>
                <h1>API Documentation</h1>
                <p>OAuth2 authentication required</p>
                <p>Base URL: https://ads.api.snapchat.com</p>
                <code>/v1/campaigns</code>
                <code>/v1/ad_squads</code>
                <code>/v1/ads</code>
            </body>
        </html>
        """

        structure = fetcher.extract_api_structure(mock_html, "test")

        assert structure['platform'] == "test"
        assert structure['authentication']['type'] == 'oauth2'
        assert len(structure['endpoints']['campaigns']) > 0


class TestCodeGenerator:
    """Tests for code generation."""

    def test_generator_initialization(self):
        generator = CodeGenerator()
        assert generator is not None

    def test_generate_mock_client(self):
        generator = CodeGenerator()

        api_structure = {
            'platform': 'test',
            'authentication': {
                'type': 'oauth2',
                'token_env_var': 'TEST_TOKEN',
                'base_url': 'https://api.test.com'
            },
            'endpoints': {
                'campaigns': [],
                'ad_squads': [],
                'ads': []
            },
            'schemas': {
                'campaign': {'required': ['name'], 'properties': {'name': 'string'}},
                'ad_squad': {'required': ['name'], 'properties': {'name': 'string'}},
                'ad': {'required': ['name'], 'properties': {'name': 'string'}}
            }
        }

        code = generator.generate_client(platform='test', api_structure=api_structure, mock_mode=True)

        assert "Mock Mode" in code
        assert "mock_campaigns = {}" in code
        assert "def create_campaign" in code

    def test_generate_production_client(self):
        generator = CodeGenerator()

        api_structure = {
            'platform': 'test',
            'authentication': {
                'type': 'oauth2',
                'token_env_var': 'TEST_TOKEN',
                'base_url': 'https://api.test.com'
            },
            'endpoints': {
                'campaigns': [],
                'ad_squads': [],
                'ads': []
            },
            'schemas': {
                'campaign': {'required': ['name'], 'properties': {'name': 'string'}},
                'ad_squad': {'required': ['name'], 'properties': {'name': 'string'}},
                'ad': {'required': ['name'], 'properties': {'name': 'string'}}
            }
        }

        code = generator.generate_client(platform='test', api_structure=api_structure, mock_mode=False)

        assert "Production Mode" in code
        assert "import requests" in code
        assert "ACCESS_TOKEN" in code
