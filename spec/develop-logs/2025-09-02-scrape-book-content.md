# Task: Scrape book content from a given URL

## 1. Environment Setup

### 1.1. Create `requirements.txt`

```
pydoll-python
lxml
```

### 1.2. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Script Development

### 2.1. Create `scraper.py`

```python
import argparse
import asyncio
from lxml import html
from pydoll import Doll

async def main():
    parser = argparse.ArgumentParser(description="Scrape a webpage.")
    parser.add_argument("url", help="The URL to scrape.")
    parser.add_argument("--proxy", help="The proxy to use (e.g., 127.0.0.1:10808).")
    parser.add_argument("--xpath", help="The XPath expression to use.", default="//body")
    args = parser.parse_args()

    doll = Doll(args.url, proxy=args.proxy)
    await doll.load()
    
    tree = html.fromstring(doll.html)
    result = tree.xpath(args.xpath)
    
    if isinstance(result, list):
        for item in result:
            print(item)
    else:
        print(result)

    await doll.quit()

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Execution & Testing

### 3.1. Run the script

```bash
python scraper.py "https://www.69shuba.com/book/51872/" --xpath "//div[@class='container']//div[@class='book-title']/h1/text()"
```
