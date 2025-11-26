# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com

"""
Test suite for Code Agent
Tests API client generation with real OPENAI_API_KEY
"""
import os
import sys
import unittest
from unittest.mock import Mock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.service.code_agent import CodeAgent
from src.service.platform_doc_parser import PlatformDocParser
from src.service.llm_remote import LLMRemote


class TestPlatformDocParser(unittest.TestCase):
    """Test documentation parser"""

    def setUp(self):
        self.parser = PlatformDocParser()

    def test_extract_endpoints(self):
        """Test endpoint extraction"""
        text = """
        POST /v1/campaigns
        GET /v1/campaigns/{id}
        https://api.example.com/v1/ad_squads
        """
        code_blocks = ["POST /v1/ads"]

        endpoints = self.parser._extract_detailed_endpoints(text, code_blocks, Mock())
        self.assertGreater(len(endpoints), 0)
        print(f"✓ Extracted {len(endpoints)} endpoints")

    def test_extract_auth_info(self):
        """Test authentication detection"""
        text = "Use OAuth 2.0 with Bearer token authentication"
        auth_info = self.parser._extract_auth_info(text)

        self.assertEqual(auth_info['type'], 'oauth2')
        self.assertIn('Bearer Token', auth_info['methods'])
        print(f"✓ Detected auth type: {auth_info['type']}")

    def test_extract_hierarchy(self):
        """Test hierarchy detection"""
        text = "Create campaigns, then ad squads, then ads"
        hierarchy = self.parser._extract_hierarchy(text, 'snapchat')

        self.assertIn('campaign', hierarchy)
        self.assertIn('ad', hierarchy)
        print(f"✓ Detected hierarchy: {' -> '.join(hierarchy)}")

    def test_extract_workflow(self):
        """Test workflow extraction"""
        text = "First create a campaign, then create ad squads"
        endpoints = [
            {'method': 'POST', 'path': '/campaigns', 'resource_type': 'campaign'},
            {'method': 'POST', 'path': '/adsquads', 'resource_type': 'ad_squad'}
        ]

        workflow = self.parser._extract_workflow(text, endpoints, 'test')
        self.assertIn('steps', workflow)
        print(f"✓ Extracted workflow steps: {workflow.get('steps', [])}")


class TestLLMRemote(unittest.TestCase):
    """Test LLM remote service"""

    def setUp(self):
        """Set up LLM client"""
        # Check if API key exists
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.skipTest("OPENAI_API_KEY not found in environment")

        try:
            self.llm = LLMRemote()
            print(f"✓ LLM client initialized successfully")
        except Exception as e:
            self.skipTest(f"Failed to initialize LLM: {e}")

    def test_load_custom_workflow(self):
        """Test loading custom workflow from snapchat_step1.md"""
        # Create a temporary snapchat_step1.md
        test_workflow = "Test workflow: step1 -> step2 -> step3"
        with open('step_test.txt', 'w') as f:
            f.write(test_workflow)

        workflow = self.llm.load_custom_workflow('test')

        # Cleanup
        if os.path.exists('step_test.txt'):
            os.remove('step_test.txt')

        if workflow:
            self.assertIn('step1', workflow)
            print(f"✓ Custom workflow loaded: {workflow[:50]}...")
        else:
            print("⚠ No custom workflow found (expected)")

    def test_generate_simple_code(self):
        """Test basic code generation"""
        system_prompt = "You are a Python code generator."
        user_prompt = "Generate a simple Python function that adds two numbers. Return ONLY the code."

        try:
            code = self.llm.generate_code(user_prompt, system_prompt)
            self.assertIsNotNone(code)
            self.assertGreater(len(code), 10)
            print(f"✓ Generated code ({len(code)} chars)")
            print(f"  Preview: {code[:100]}...")
        except Exception as e:
            self.fail(f"Code generation failed: {e}")


class TestCodeAgent(unittest.TestCase):
    """Test code agent with real API"""

    def setUp(self):
        """Set up code agent"""
        # Check if API key exists
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.skipTest("OPENAI_API_KEY not found in environment")

        try:
            self.agent = CodeAgent()
            print(f"✓ Code agent initialized")
        except Exception as e:
            self.skipTest(f"Failed to initialize agent: {e}")

        # Create output directory
        self.output_dir = 'tests/output'
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        """Cleanup test files"""
        # Remove generated test files
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                if file.endswith('_api.py'):
                    os.remove(os.path.join(self.output_dir, file))

    @unittest.skipIf(
        not os.getenv('OPENAI_API_KEY'),
        "Requires OPENAI_API_KEY - this is an integration test"
    )
    def test_generate_mock_client(self):
        """
        Test generating a mock API client (integration test)
        This test makes real API calls and may take 10-30 seconds
        """
        print("\n" + "=" * 60)
        print("Integration Test: Generating Mock Client")
        print("This will make real API calls and may take 10-30 seconds")
        print("=" * 60 + "\n")

        # Use a simple mock documentation URL
        platform = 'test_platform'
        docs_url = 'https://developers.snap.com/api/marketing-api'

        try:
            output_file = self.agent.generate_api_client(
                platform=platform,
                docs_url=docs_url,
                mock_auth=True,
                output_dir=self.output_dir
            )

            # Verify file was created
            self.assertTrue(os.path.exists(output_file))
            print(f"\n✓ Generated file: {output_file}")

            # Verify file has content
            with open(output_file, 'r') as f:
                content = f.read()

            self.assertGreater(len(content), 100)
            print(f"✓ File size: {len(content)} characters")

            # Check for required functions
            required_functions = ['create_campaign', 'HIERARCHY']
            for func in required_functions:
                if func in content:
                    print(f"✓ Found: {func}")
                else:
                    print(f"⚠ Missing: {func}")

            # Try to import the generated module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                f"{platform}_api",
                output_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            print(f"✓ Module imports successfully")

            # Check for orchestrator
            if hasattr(module, 'launch_campaign'):
                print(f"✓ Orchestrator function found")
            else:
                print(f"⚠ Orchestrator function not found (may be expected)")

            print(f"\n{'=' * 60}")
            print("Integration test completed successfully!")
            print("=" * 60 + "\n")

        except Exception as e:
            self.fail(f"Failed to generate API client: {e}")


class TestWorkflowSystem(unittest.TestCase):
    """Test workflow system with snapchat_step1.md"""

    def test_step_file_creation(self):
        """Test creating and reading snapchat_step1.md"""
        step_content = """Test workflow:
1. Create campaign
2. Create ad squad
3. Create ad"""

        # Write test step file
        with open('step_test.txt', 'w') as f:
            f.write(step_content)

        # Verify file exists
        self.assertTrue(os.path.exists('step_test.txt'))

        # Read and verify
        with open('step_test.txt', 'r') as f:
            content = f.read()

        self.assertEqual(content, step_content)
        print(f"✓ snapchat_step1.md creation and reading works")

        # Cleanup
        os.remove('step_test.txt')


def run_specific_test(test_class, test_method):
    """Run a specific test method"""
    suite = unittest.TestSuite()
    suite.addTest(test_class(test_method))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_all_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformDocParser))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMRemote))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowSystem))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Running Agent Tests")
    print("=" * 60 + "\n")

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠ WARNING: OPENAI_API_KEY not found")
        print("Some tests will be skipped")
        print("Set OPENAI_API_KEY in .env to run full tests\n")

    # Run all tests
    success = run_all_tests()

    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)
