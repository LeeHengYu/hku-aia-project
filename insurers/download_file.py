import os
from curl_cffi import requests

def download_file_from_url(file_url, file_path, headers=None, timeout=15):
    default_headers = {
        "User-Agent": "Chrome/120.0.0.0",
        'Content-Type': 'application/pdf',
        'Accept': 'application/pdf',
        'Accept-Encoding': 'gzip, deflate, br',
        # "Cookie": "acw_tc=a3b5a09717690083473105245e59eab7a468c8a3ea3a54d55224d2ffca; cdn_sec_tc=a3b5a09717690083473105245e59eab7a468c8a3ea3a54d55224d2ffca; _ga=GA1.1.727424300.1769008349; lang=eyJpdiI6IjJ3a0YrSlgrc2M0dVZLdXQ2M3FrS3c9PSIsInZhbHVlIjoiTW8ydDZLMEdySVJobmJDTEsrTDl0VEMxdzRWUk9LdEdDZENBNzFsRkl1cnVxNTJUYzd6aCtLRzlrUjNLTTBRViIsIm1hYyI6IjhlY2YzNmYyY2VjODM0OTMyOTBlYzMzYmI3N2Y1N2VjZjk1Yjk5ODI2ZDc1ZjgzM2ViZTY4N2M2N2RjNDM2ZGEiLCJ0YWciOiIifQ%3D%3D; ssxmod_itna=YqAODK7KSQD5i7G7DgDeqWIW4Ydh5GDl4BtQdGgBDFqApxDH+NBepDUx0KfwqvC4tCQ7G=Dc7nKD/mmeqDyec3BxkgU10BK3Q5Cw+ekWi0nyxIwNNnARxjNHhjeu+AY4iTiDQKGmz4GtQDG=rCieD44DvDBYD74G+DDeDigiDGubx2DDF+Wr5pltQ/q4xweDEG+qQDiUFxi5N2WuYXkGtxAfvi2bQnqGnD0js2GwYx0fFrgHDzMoDbrEPOIODtwFVnqK3XQTQzFm48wDrf8DqOT+em0x37YxG4vZebBG1l2IeADExGHdk3eDL4DGRK5YQPE3ei4gieTu87Mo8dGkA=5Gdvow+AzHhD7gKQiegYx9i5lB+cTYvTeKh4WDYy0=oWDD; ssxmod_itna2=YqAODK7KSQD5i7G7DgDeqWIW4Ydh5GDl4BtQdGgBDFqApxDH+NBepDUx0KfwqvC4tCQ7G=Dc7WeDAergIweWjo27tDLCw+ao37mDDs6CY28LPFHeK7gx8TQYQx4kXOcYaoh5C1DantnuYMfwDwnutnDwARm0heVRAx3wDRbd5okxE5TYx9U+uXmDTyYBLtsgrR8EbqNGrnGTarsnQ9SeWWHpiBF6jt=BdHMPWhLjvXnf9n0Wbiouc=UoWxkOtiTiBkaCUhdadHo93H1AWH1=5E=sdsDT1vPVrc=SGGhHnnRe=yDMpSAAO/1wtohdrLCYYUDUba6LmwN2NVjAnAUxQrBZIShf=CvQ/K7P3KrGN6i48d5hLxi=omGSDff7p9ApVhm0i=xh=bIjYOP3E5O1G3xIKaIkYYKlP4mj1Du=lpSGw51PUm37+Ibcj5=GFf=ibK44AazrBQNz8amF5D/pZCrh3oP+Q94bH2GlWQLDpQKWi+fnAfktFK=bT2KZz3eeXRCRR2K8gc6GNn8=/oEbKto=X0ljecAQyE4l2QrKv79FCqXIRKXA3jcBnowYg0WvkUi3TL/7p5IgLnb8TOUIN7LU2mUHPUUaN0cU+qIT=c/3Qr8FqvDZ9N9io7Ow9j5EQchBShjp6XwirIXkv0XhqY4rjzyd+CmDkAqzCD3G=hQD5nz/dxknzxD; _ga_YJXFYFY2TM=GS2.1.s1769008349$o1$g1$t1769009312$j60$l0$h0; _ga_F36P04QSNV=GS2.1.s1769008349$o1$g1$t1769009312$j60$l0$h0; XSRF-TOKEN=eyJpdiI6ImxZaUU1Ny84NlJZSWtiaEpwbzJnWHc9PSIsInZhbHVlIjoiQWp3elZpYjdlTGJObUZwcXI1dDJPRGpicnZkYnB6SkdESlBpZTVyNkNhSEJYQm1HSTI2NXRveDYrQ1hXMFNBSUt2NUNWaEI0WUNQS2JpRFZXTHdUelh1bXFwRlFhL1FKbHNVNVZHRXN2Tnh2dUpuMElFZjJzTkdNWE9vem4yL04iLCJtYWMiOiJjZjVmMzNlMTgxNTQ2ZGEwZmMxZmM1YjIzNmQwODZlMWNlY2I3NDJkZDc0ZmUxMzk1ZTc0Zjc4MzAyMmQ5NGU3IiwidGFnIjoiIn0=; laravel_session=eyJpdiI6IkMxVVQ3UEhPS2FHc05aNUR2aDVkT2c9PSIsInZhbHVlIjoiZXZvbFM4c3ZESUVrTFhXZzVHTmpKWExRZ1RxcmFxaFo4UFpVdFRoSEdhemVFdFhFenFWdXcrS3ZuZytGaHNETXpUWkUzUVdmNVBNQlJGZ1NqbTIxTnRldWUzYXkxSUJrTE5JQXAreEFGaEpmWU5zbnlUOERRZTRNR2lkRndDbDAiLCJtYWMiOiJmODg4ZWRhNGJkN2UwOWM0MjRkMzhhY2E4NmYwZjEzZjFmZjY4Njc4MDJhNmVkM2M3MDcxY2Y5NWVkMzJjMWNmIiwidGFnIjoiIn0%3D"
    }

    if headers:
        default_headers.update(headers)
    
    headers = default_headers
    
    try:
        r = requests.get(file_url, headers=headers, stream=True, timeout=timeout, impersonate="chrome110")
        r.raise_for_status()

        content_type = r.headers.get("content-type", "").lower()
        if "application/pdf" not in content_type:
            print(r.text)
            return
        
        if r.status_code != 200:
            return
        
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                f.write(chunk)
    except:
        ...

def create_folder_if_not_exist(dir):
    os.makedirs(dir, exist_ok=True)