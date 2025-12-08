# !/usr/bin/env python3
# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
import argparse
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.service.code_agent import CodeAgent

# Load environment variables
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description='Generate platform-specific API clients for ad campaigns'
    )
    parser.add_argument(
        '--platform',
        required=True,
        help='Platform name (e.g., snapchat, pinterest)'
    )
    parser.add_argument(
        '--docs',
        required=True,
        help='API documentation URL'
    )
    parser.add_argument(
        '--mock-auth',
        action='store_true',
        help='Generate mock client (no real API calls, for testing)'
    )
    parser.add_argument(
        '--output-dir',
        default=None,
        help='Output directory for generated code (default: src/generated_clients)'
    )

    args = parser.parse_args()

    # Verify API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in environment")
        print("Please copy .env.example to .env and set your API key")
        sys.exit(1)

    # Set output directory
    if args.output_dir is None:
        # Default to src/generated_clients
        script_dir = os.path.dirname(__file__)
        args.output_dir = os.path.join(script_dir, 'generated_clients')

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize agent
    agent = CodeAgent()

    print(f"\n{'=' * 60}")
    print(f"Generating API client for: {args.platform}")
    print(f"Documentation URL: {args.docs}")
    print(f"Mode: {'MOCK (Testing)' if args.mock_auth else 'PRODUCTION (Real API)'}")
    print(f"Output: {args.output_dir}")
    print(f"{'=' * 60}\n")

    try:
        # Generate the API client
        output_file = agent.generate_api_client(
            platform=args.platform,
            docs_url=args.docs,
            mock_auth=args.mock_auth,
            output_dir=args.output_dir
        )

        print(f"\n{'=' * 60}")
        print(f"✅ Success! Generated: {output_file}")
        print(f"{'=' * 60}\n")
        print("Next steps:")
        print("1. Test the client directly:")
        print(f"   python {output_file}")
        print("\n2. Start Flask server:")
        print("   python src/flask_api/api.py")
        print(f"\n3. Test the API with platform='{args.platform}':")
        print('   curl -X POST http://localhost:5000/api/launch-campaign \\')
        print('     -H "Content-Type: application/json" \\')
        print(f'     -d \'{{"platform": "{args.platform}", "account_id": "test", ...}}\'')

        if not args.mock_auth:
            print(f"\n4. Set {args.platform.upper()}_ACCESS_TOKEN in .env for production")

    except Exception as e:
        print(f"\n❌ Error generating API client: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
