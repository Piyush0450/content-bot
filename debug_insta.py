import instaloader
import os
import shutil
import time

url = "https://www.instagram.com/p/DTP8jQOjRIC/?utm_source=ig_w"
output_dir = "debug_downloads"

def test_download():
    try:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)
        
        # Extract shortcode
        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0].split("?")[0]
        elif "/reel/" in url:
            shortcode = url.split("/reel/")[1].split("/")[0].split("?")[0]
        
        print(f"Shortcode: {shortcode}")
        
        L = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        print(f"Downloading post {shortcode}...")
        L.download_post(post, target=output_dir)
        
        print("Download complete. Files found:")
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                print(f" - {file}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_download()
