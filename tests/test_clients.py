# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
"""
Test generated API clients
"""
import os
import sys
import unittest
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestGeneratedClients(unittest.TestCase):
    """Test generated API clients"""

    def test_snapchat_mock_client(self):
        """Test Snapchat mock client if it exists"""
        try:
            from src.generated_clients import snapchat_api

            # Test create_campaign
            if hasattr(snapchat_api, 'create_campaign'):
                campaign = snapchat_api.create_campaign(
                    account_id='test_account',
                    name='Test Campaign'
                )

                self.assertIn('id', campaign)
                self.assertIn('name', campaign)
                self.assertEqual(campaign['name'], 'Test Campaign')

            # Test create_ad_squad if exists
            if hasattr(snapchat_api, 'create_ad_squad'):
                ad_squad = snapchat_api.create_ad_squad(
                    campaign_id='camp_123',
                    account_id='test_account',
                    name='Test Ad Squad'
                )

                self.assertIn('id', ad_squad)
                self.assertIn('name', ad_squad)

            print("✅ Snapchat mock client tests passed")

        except ImportError:
            self.skipTest("Snapchat client not generated yet")

    def test_client_has_required_functions(self):
        """Verify generated clients have required functions"""
        clients_dir = 'src/generated_clients'

        if not os.path.exists(clients_dir):
            self.skipTest("No clients generated yet")

        for file in os.listdir(clients_dir):
            if file.endswith('_api.py') and not file.startswith('__'):
                platform = file.replace('_api.py', '')

                # Import dynamically
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    f"{platform}_api",
                    os.path.join(clients_dir, file)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check for create_campaign
                self.assertTrue(
                    hasattr(module, 'create_campaign'),
                    f"{platform}_api missing create_campaign"
                )

                print(f"✅ {platform}_api has required functions")


class TestFlaskAPI(unittest.TestCase):
    """Test Flask API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Start Flask test client"""
        os.environ['FLASK_DEBUG'] = 'False'

        from src.flask_api.api import app
        cls.client = app.test_client()
        cls.app = app

    def test_health_endpoint(self):
        """Test health check"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_list_platforms(self):
        """Test platforms listing"""
        response = self.client.get('/api/platforms')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('platforms', data)
        self.assertIsInstance(data['platforms'], list)

    def test_launch_campaign_missing_platform(self):
        """Test launch campaign without platform"""
        response = self.client.post(
            '/api/launch-campaign',
            json={}
        )
        self.assertEqual(response.status_code, 400)

    def test_launch_campaign_unknown_platform(self):
        """Test launch campaign with unknown platform"""
        response = self.client.post(
            '/api/launch-campaign',
            json={'platform': 'unknown_platform'}
        )
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
