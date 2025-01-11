from flask import Flask, request, jsonify
import json
import requests
import zstandard as zstd


app = Flask(__name__)


headers = {
    "Host": "www.instagram.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "zstd",
    "X-CSRFToken": "t5ilmvi5KvH38_3s_I7QH0",
    "X-IG-App-ID": "936619743392459",
    "X-ASBD-ID": "129477",
    "X-IG-WWW-Claim": "0",
    "X-Web-Session-ID": "v10v3v:7j32p6:4har7m",
    "X-Requested-With": "XMLHttpRequest",
    "Alt-Used": "www.instagram.com",
    "Connection": "keep-alive",
    "Referer": "https://www.instagram.com/instagram/reels/",
    "Cookie": "csrftoken=t5ilmvi5KvH38_3s_I7QH0; datr=BTyCZ-O2ZwvPu9IEUUOmLRCX; ig_did=43179D4A-6B05-4E8C-9004-729A150473F2; wd=1536x411; dpr=1.25; mid=Z4I8BQALAAG_lzz3UvxDimrlbmWi; ig_nrcb=1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}


def fetch_page_data(uid, max_id=None):
    clip_url = "https://www.instagram.com/api/v1/clips/user/"
    form_data = {
        "include_feed_video": "true",
        "page_size": "12",
        "target_user_id": uid
    }
    if max_id:
        form_data['max_id'] = max_id

    response = requests.post(clip_url, data=form_data, headers=headers)
    content_encoding = response.headers.get('Content-Encoding')

    if content_encoding == "zstd":
        decompressed_data = dctx.decompress(response.content)
    else:
        decompressed_data = response.content

    data = json.loads(decompressed_data.decode('utf-8', errors='ignore'))
    items = data.get("items")
    paging_info = data.get('paging_info')
    max_id = paging_info.get('max_id')
    more_avail = paging_info.get('more_available')

    return items, more_avail, max_id



def get_reels_page(uid, page_no):
    count = 1
    max_id = None
    more_avail = True
    reels = []

    while more_avail and count <= page_no:
        items, more_avail, max_id = fetch_page_data(uid, max_id)
        
        if count == page_no:
            for item in items:
                media = item.get('media')
                videos = media.get('video_versions')
                caption = media.get('caption')
                caption_text = caption.get('text') if caption else ""
                user = media.get('user')
                user_name = user.get('username')
                profile_pic = user.get('profile_pic_url')
                video_url = videos[0].get('url')

                reels.append({
                    'id': media.get('code'),
                    'username': user_name,
                    'caption_text': caption_text,
                    'pfURL': profile_pic,
                    'url': video_url
                })
        count += 1

    return reels



def get_user_reels(username, page_no):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            global dctx
            dctx = zstd.ZstdDecompressor()

            decompressed_data = dctx.decompress(response.content)
            data = json.loads(decompressed_data.decode('utf-8', errors='ignore'))
            user = data.get('data').get('user')
            
            uid = user.get('id')

            reels = get_reels_page(uid, page_no)

            
            return {
                "response": {
                    "username": username,
                    "page_no": page_no,
                    "pfPhoto": user.get('profile_pic_url_hd'),  
                    "reels": reels
                }
            }
        else:
            return {"error": f"Request failed with status code {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}



@app.route('/get_reels', methods=['get'])
def api_get_reels():
    
    username = request.args.get('username')
    page_count = int(request.args.get('page_no', 1))
    
    
    # username = data.get('username')
    # page_count = data.get('page_no', 1)  
    
    
    if not username:
        return jsonify({"error": "Username is required"}), 400

    reels_data = get_user_reels(username, page_count)

    
    if "error" in reels_data:
        return jsonify(reels_data), 500
    else:
        return jsonify(reels_data), 200


if __name__ == "__main__":
    app.run(debug=True)
