import json
import re
import requests
from requests_html import HTMLSession
import zstandard as zstd 
import xml.etree.ElementTree as ET
def getVideoId(url):

    pattern = r"https:\/\/www\.instagram\.com\/reels\/([A-Za-z0-9_-]+)"

    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        print("No video ID found.")
def getManifest(url):
    videoId=getVideoId(url)
    session = HTMLSession()
    url = "https://www.instagram.com/graphql/query/"
    headers = {
        "Host": "www.instagram.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "zstd",
        "Referer": "https://www.instagram.com/reel/CvKqTbLRu9s/?hl=en",
        "Origin": "https://www.instagram.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-FB-Friendly-Name": "PolarisPostActionLoadPostQueryQuery",
        "X-BLOKS-VERSION-ID": "abaff5d09a530689e609e838538ae53475ff0cac083a548efad6633e0e625cff",
        "X-CSRFToken": "HDA4CQj7SrfnHXdGEi_DFm",
        "X-IG-App-ID": "936619743392459",
        "X-FB-LSD": "AVrlX3sBhnQ",
        "X-ASBD-ID": "129477",
        "Alt-Used": "www.instagram.com",
        "Priority": "u=4",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session.headers.update(headers)
    cookies = {
        "ig_did": "DF538F4A-593F-447A-A579-6F2FD05E9219",
        "csrftoken": "HDA4CQj7SrfnHXdGEi_DFm",
        "datr": "FXJ1Z-ctfbqqT8i21ZGBnPSY",
        "mid": "Z3VyFQALAAFWMrEOfqOb5fAfZGGH",
        "wd": "1536x411",
        "dpr": "1.25",
        "ps_l": "1",
        "ps_n": "1",
        "ig_nrcb": "1"
    }

    session.cookies.update(cookies)
    data = {
        "__d": "www",
        "__user": "0",
        "__a": "1",
        "__req": "b",
        "__hs": "20090.HYP:instagram_web_pkg.2.1.0.0.0",
        "dpr": "1",
        "__ccg": "EXCELLENT",
        "__rev": "1019116287",
        "__s": "77jlxr:i677os:ujm0vi",
        "__hsi": "7455441947661879090",
        "__dyn": "7xeUjG1mxu1syUbFp41twpUnwgU7SbzEdF8aUco2qwJw5ux609vCwjE1EE2Cw8G11wBz81s8hwGxu786a3a1YwBgao6C0Mo2swtUd8-U2zxe2GewGw9a361qw8Xxm16wa-0nKq2-azo7u3C2u2J0bS1LwTwKG1pg2fwxyo6O1FwlEcUed6goK2O4UrAwCAxW1oCz84u0N9Wy9rDyo",
        "__csr": "g9IAt79RExill17HFVKihlBijKjqvBADjGGBy94AVeqh12S9pqqx2Au-499rKvK6VrV6up4iCXBDmJ4iDUG9K4oGcK-mUojDzqzoKuta9AGipyEB9udDCKLUyF4aCxa8DHy9UymcxmQGx64-00kei19w7yw5SwgU9A3meG1mg463x0604woE1N89U0Pm0d2Iwrw13S3uZ38covG4o9k2y8PwbC8y8Ghwb1Un57gGl0FUco9IWx55gQkawa67CbDa1agNbeiaz86e0PWwioapEaUhgkO0oE1m21m7wJ20kS01YIw2z80-q09jw",
        "__comet_req": "7",
        "lsd": "AVrlX3sBhnQ",
        "jazoest": "2988",
        "__spin_r": "1019116287",
        "__spin_b": "trunk",
        "__spin_t": "1735855347",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "PolarisPostActionLoadPostQueryQuery",
        "variables": "{\"shortcode\":\""+videoId+"\",\"fetch_tagged_user_count\":null,\"hoisted_comment_id\":null,\"hoisted_reply_id\":null}",
        "server_timestamps": "true",
        "doc_id": "8845758582119845"
    }

    response = session.post(url, data=data)    
    dctx = zstd.ZstdDecompressor()
    decompressed_data = dctx.decompress(response.content)
    data:dict = json.loads(decompressed_data.decode('utf-8', errors='ignore'))
    data=data.get('data','')
    xdt_shortcode_media=data.get('xdt_shortcode_media')
    dash_info=xdt_shortcode_media.get("dash_info")
    video_dash_manifest=dash_info.get("video_dash_manifest")
    download_video(video_dash_manifest,f"{videoId}.mp4")

    


def download_video(manifest, output_filename):
    tree = ET.ElementTree(ET.fromstring(manifest))
    root = tree.getroot()

    namespaces = {'': 'urn:mpeg:dash:schema:mpd:2011'}
    base_url = root.find(".//AdaptationSet[@contentType='video']/Representation/BaseURL", namespaces)
    
    if base_url is not None:
        video_url = base_url.text
        print(f"Downloading video from: {video_url}")

        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()  

            with open(output_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Video downloaded successfully as {output_filename}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while downloading the video: {e}")
    else:
        print("No video URL found in the XML.")


while True:
    url=input("Enter url: ")
    getManifest(url)