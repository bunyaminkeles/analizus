"""
Render native Python ortamında Chrome for Testing indirip kurar.
apt-get gerektirmez — standalone binary.
"""
import json
import os
import stat
import sys
import urllib.request
import zipfile

INSTALL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chrome")


def install_chrome():
    print("Chrome for Testing: son stable sürüm sorgulanıyor...")
    url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())

    stable = data["channels"]["Stable"]
    version = stable["version"]

    chrome_url = None
    for d in stable["downloads"]["chrome"]:
        if d["platform"] == "linux64":
            chrome_url = d["url"]
            break

    if not chrome_url:
        print("HATA: linux64 Chrome bulunamadı")
        sys.exit(1)

    print(f"Chrome {version} indiriliyor...")
    zip_path = "/tmp/chrome.zip"
    urllib.request.urlretrieve(chrome_url, zip_path)

    os.makedirs(INSTALL_DIR, exist_ok=True)

    print(f"Çıkartılıyor: {INSTALL_DIR}")
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(INSTALL_DIR)

    chrome_binary = os.path.join(INSTALL_DIR, "chrome-linux64", "chrome")
    os.chmod(chrome_binary, os.stat(chrome_binary).st_mode | stat.S_IEXEC)

    print(f"Chrome kuruldu: {chrome_binary}")
    os.remove(zip_path)


if __name__ == "__main__":
    install_chrome()
