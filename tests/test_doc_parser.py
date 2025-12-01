from src.service.platform_doc_parser import PlatformDocParser


def parse_doc(docs_url: str, platform: str):
    doc_parser = PlatformDocParser()
    api_info = doc_parser.get_api_info(docs_url, platform)
    print(api_info)


def test_snapchat():
    docs_url = "https://developers.snap.com/api/marketing-api/Ads-API/ads"
    platform = "Snapchat"
    parse_doc(docs_url, platform)


def test():
    test_snapchat()


if __name__ == '__main__':
    test()
