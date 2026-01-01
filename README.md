# HKU AIA project

## Installation & Setup

It is recommended to install Python3.11 or above and `pip` for downloading required packages. It is STRONGLY RECOMMENDED to create a virtual environment for this project.

To download all required files from this repo, run

```
git clone https://github.com/LeeHengYu/hku-aia-project.git
```

If you have `python3` installed on your machine, run the following:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Task 2: Data crawling

### AIA Hong Kong

The main file for this website, `crawler/aia_hk.py`, serves as a general principle of recursively crawling brochures from each product page. One can apply the similar thought processes on other insurers' websites.

#### Logics

The base URL is `https://www.aia.com.hk/en`, and we can assume all product details lie below `https://www.aia.com.hk/en/products/<product_type>`, and the product type can be inferred from `product_type`. By crawling the base URL, we can find many matches of `product_type`.

In the webpages of each product type, say `https://www.aia.com.hk/en/products/general-insurance/<optional-something>`, there can be a list of product links (sometimes categorization is more niche) or the intro page of a product. The recursion comes in here: if the page is a product intro page, we try to find the brochure link and download it, or else we explore the product list and visit each of them. Any determination of whether if it is a product page is based on HTML elements.

> Note: this exploration method is also called Depth-First Search (DFS).

### FWD (async)

No recursive hierarchy in this website. The entry point is the product list page (https://www.fwd.com.hk/en/products/), if the brochure of a certain product can be found, direct download, otherwise visit the product page and search for it. 

### Technicals

`Playwright` is needed to load the contents of the page, as most of the product information in the list is injected by JavaScript program. Using only `BeautifulSoup` can't capture these HTML elements.

This implementation successfully crawl **27** brochures from AIA websites and **50** from FWD in one run. Read the code for more details.

## Task 3 prep: OSS setup

A simple script to upload data to Alibaba OSS. Configuration of API key and secret as environment variables is needed. Follow the [official API documentation](https://www.alibabacloud.com/help/en/oss/developer-reference/getting-started-with-oss-sdk-for-python) for this setup.

`utility/main.py` is essentially a simple wrapper of Alibaba's OSS Python SDK.
