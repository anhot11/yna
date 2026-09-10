import urllib.request
import os
import sys

def upload(filepath, target_url="https://sendit.sh/"):
    filename = os.path.basename(filepath)
    url = target_url.rstrip("/") + "/" + filename
    filesize = os.path.getsize(filepath)
    print(f"Uploading {filepath} ({filesize} bytes) to {url}...")
    
    with open(filepath, "rb") as f:
        req = urllib.request.Request(url, data=f, method="PUT")
        req.add_header("Content-Length", str(filesize))
        req.add_header("User-Agent", "curl/7.68.0")
        try:
            with urllib.request.urlopen(req, timeout=300) as response:
                status = response.status
                body = response.read().decode("utf-8", errors="replace")
                print(f"Status: {status}")
                print(f"Response:\n{body}")
                return body.strip()
        except urllib.error.HTTPError as e:
            print(f"HTTPError: {e.code} - {e.reason}")
            body = e.read().decode("utf-8", errors="replace")
            print(body)
            raise
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else r"I:\yna-v1.7-release.apk"
    upload(file_path)
