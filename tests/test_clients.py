# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
"""
Test generated API clients (Mock mode)
Tests that generated clients work correctly
"""
import os
import sys
import unittest
import json
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestGeneratedClients(unittest.TestCase):
    """Test generated API clients in mock mode"""

    def setUp(self):
        """Set up test environment"""
        self.clients_dir = 'src/generated_clients'
        self.available_clients = self._discover_clients()

    def _discover_clients(self):
        """Discover all generated client files"""
        if not os.path.exists(self.clients_dir):
            return []

        clients = []
        for file in os.listdir(self.clients_dir):
            if file.endswith('_api.py') and not file.startswith('__'):
                platform = file.replace('_api.py', '')
                clients.append(platform)

        return clients

    def _load_client(self, platform):
        """Dynamically load a client module"""
        client_file = os.path.join(self.clients_dir, f"{platform}_api.py")

        if not os.path.exists(client_file):
            return None

        spec = importlib.util.spec_from_file_location(
            f"{platform}_api",
            client_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def test_snapchat_mock_client(self):
        """Test Snapchat mock client if it exists"""
        if 'snapchat' not in self.available_clients:
            self.skipTest("Snapchat client not generated yet")

        print("\n" + "=" * 60)
        print("Testing Snapchat Mock Client")
        print("=" * 60)

        client = self._load_client('snapchat')
        self.assertIsNotNone(client, "Failed to load snapchat client")

        # Check module info
        self.assertTrue(hasattr(client, '__mode__'))
        print(f"✓ Mode: {getattr(client, '__mode__', 'unknown')}")

        self.assertTrue(hasattr(client, 'HIERARCHY'))
        hierarchy = getattr(client, 'HIERARCHY')
        print(f"✓ Hierarchy: {' -> '.join(hierarchy)}")

        # Test individual functions
        self._test_create_campaign(client)
        self._test_create_ad_squad(client)
        self._test_create_ad(client)

        # Test orchestrator if available
        if hasattr(client, 'launch_campaign'):
            self._test_launch_campaign_orchestrator(client)
        else:
            print("⚠ No orchestrator function found")

        print("=" * 60 + "\n")

    def _test_create_campaign(self, client):
        """Test create_campaign function"""
        if not hasattr(client, 'create_campaign'):
            print("⚠ create_campaign not found")
            return

        print("\nTesting create_campaign...")
        campaign = client.create_campaign(
            account_id='test_account',
            name='Test Campaign',
            daily_budget_micro=100000000
        )

        # Verify response structure
        self.assertIn('id', campaign)
        self.assertIn('name', campaign)
        self.assertEqual(campaign['name'], 'Test Campaign')

        print(f"✓ Campaign created: {campaign['id']}")
        print(f"  Name: {campaign['name']}")
        if 'daily_budget_micro' in campaign:
            print(f"  Budget: {campaign['daily_budget_micro']}")

    def _test_create_ad_squad(self, client):
        """Test create_ad_squad function"""
        hierarchy = getattr(client, 'HIERARCHY', ['campaign', 'ad_squad', 'ad'])
        second_level = hierarchy[1]

        func_name = f'create_{second_level}'
        if not hasattr(client, func_name):
            print(f"⚠ {func_name} not found")
            return

        print(f"\nTesting {func_name}...")
        create_func = getattr(client, func_name)

        result = create_func(
            campaign_id='camp_test_123',
            account_id='test_account',
            name='Test Ad Squad',
            bid_micro=5000000
        )

        # Verify response structure
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertEqual(result['name'], 'Test Ad Squad')

        print(f"✓ {second_level.replace('_', ' ').title()} created: {result['id']}")
        print(f"  Name: {result['name']}")
        if 'bid_micro' in result:
            print(f"  Bid: {result['bid_micro']}")

    def _test_create_ad(self, client):
        """Test create_ad function"""
        if not hasattr(client, 'create_ad'):
            print("⚠ create_ad not found")
            return

        print("\nTesting create_ad...")

        hierarchy = getattr(client, 'HIERARCHY', ['campaign', 'ad_squad', 'ad'])
        second_level = hierarchy[1]

        ad = client.create_ad(
            **{f'{second_level}_id': 'squad_test_123'},
            account_id='test_account',
            name='Test Ad',
            headline='Test Headline'
        )

        # Verify response structure
        self.assertIn('id', ad)
        self.assertIn('name', ad)
        self.assertEqual(ad['name'], 'Test Ad')

        print(f"✓ Ad created: {ad['id']}")
        print(f"  Name: {ad['name']}")
        if 'headline' in ad:
            print(f"  Headline: {ad['headline']}")

    def _test_launch_campaign_orchestrator(self, client):
        """Test launch_campaign orchestrator function"""
        print("\nTesting launch_campaign orchestrator...")

        result = client.launch_campaign(
            account_id='test_account_123',
            campaign_data={
                'name': 'Orchestrator Test Campaign',
                'daily_budget_micro': 100000000
            },
            ad_squads_data=[
                {
                    'name': 'Test Ad Squad 1',
                    'bid_micro': 5000000
                }
            ],
            ads_data=[
                {
                    'name': 'Test Ad 1',
                    'headline': 'Test Headline',
                    'image_url': 'https://example.com/image.jpg'
                }
            ]
        )

        # Verify response structure
        self.assertIn('status', result)
        self.assertIn('campaign_id', result)

        print(f"✓ Orchestrator completed")
        print(f"  Status: {result['status']}")
        print(f"  Campaign ID: {result['campaign_id']}")

        # Check for all resource types
        if 'ad_squad_ids' in result and result['ad_squad_ids']:
            print(f"  Ad Squads: {len(result['ad_squad_ids'])}")

        if 'media_ids' in result and result['media_ids']:
            print(f"  Media: {len(result['media_ids'])}")

        if 'creative_ids' in result and result['creative_ids']:
            print(f"  Creatives: {len(result['creative_ids'])}")

        if 'ad_ids' in result and result['ad_ids']:
            print(f"  Ads: {len(result['ad_ids'])}")

        # Assertions
        self.assertEqual(result['status'], 'success')
        self.assertIsNotNone(result['campaign_id'])


class TestFlaskAPIIntegration(unittest.TestCase):
    """Test Flask API integration with generated clients"""

    @classmethod
    def setUpClass(cls):
        """Start Flask test client once for all tests"""
        os.environ['FLASK_DEBUG'] = 'False'

        try:
            from src.flask_api.api import app
            cls.client = app.test_client()
            cls.app = app
            print("\n✓ Flask test client initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize Flask: {e}")
            cls.client = None

    def setUp(self):
        """Check if Flask is available"""
        if self.client is None:
            self.skipTest("Flask client not available")

    def test_health_endpoint(self):
        """Test health check"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        print("✓ Health check passed")

    def test_list_platforms(self):
        """Test platforms listing"""
        response = self.client.get('/api/platforms')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('platforms', data)
        self.assertIsInstance(data['platforms'], list)

        print(f"✓ Platforms endpoint works")
        if data['platforms']:
            print(f"  Available platforms: {', '.join(data['platforms'])}")

    def test_client_info_snapchat(self):
        """Test client info endpoint for Snapchat"""
        response = self.client.get('/api/client-info/snapchat')

        if response.status_code == 404:
            self.skipTest("Snapchat client not available")

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('platform', data)
        self.assertIn('has_orchestrator', data)

        print(f"✓ Client info endpoint works")
        print(f"  Platform: {data['platform']}")
        print(f"  Has Orchestrator: {data['has_orchestrator']}")
        print(f"  Mode: {data.get('mode', 'unknown')}")

    def test_launch_campaign_snapchat_mock(self):
        """Test launch campaign with Snapchat mock client"""
        response = self.client.post(
            '/api/launch-campaign',
            json={
                'platform': 'snapchat',
                'account_id': 'test_account',
                'campaign': {
                    'name': 'Flask Test Campaign',
                    'daily_budget_micro': 100000000
                },
                'ad_squads': [
                    {
                        'name': 'Flask Test Squad',
                        'bid_micro': 5000000
                    }
                ],
                'ads': [
                    {
                        'name': 'Flask Test Ad',
                        'headline': 'Test Headline',
                        'image_url': 'https://example.com/test.jpg'
                    }
                ]
            }
        )

        if response.status_code == 404:
            self.skipTest("Snapchat client not available")

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        print("\n" + "=" * 60)
        print("Flask API Launch Campaign Test")
        print("=" * 60)
        print(f"Status: {data.get('status')}")
        print(f"Campaign ID: {data.get('campaign_id')}")

        if 'ad_squad_ids' in data:
            print(f"Ad Squad IDs: {data['ad_squad_ids']}")

        if 'media_ids' in data:
            print(f"Media IDs: {data['media_ids']}")

        if 'creative_ids' in data:
            print(f"Creative IDs: {data['creative_ids']}")

        if 'ad_ids' in data:
            print(f"Ad IDs: {data['ad_ids']}")

        print("=" * 60 + "\n")

        # Assertions
        self.assertEqual(data['status'], 'success')
        self.assertIsNotNone(data['campaign_id'])


def run_client_tests():
    """Run all client tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGeneratedClients))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskAPIIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Running Client Tests (Mock Mode)")
    print("=" * 60 + "\n")

    success = run_client_tests()

    print("\n" + "=" * 60)
    if success:
        print("✅ All client tests passed!")
    else:
        print("❌ Some client tests failed")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)
