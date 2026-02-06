"""
Render native Python ortamında Chrome for Testing + eksik sistem
kütüphanelerini indirip kurar.  apt-get gerektirmez.
"""
import json
import os
import stat
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALL_DIR = os.path.join(BASE_DIR, "chrome")
LIB_DIR = os.path.join(BASE_DIR, "chrome-libs")

# Chrome'un ihtiyaç duyduğu temel .deb paketleri  (Debian Bookworm amd64)
DEB_PACKAGES = [
    "https://deb.debian.org/debian/pool/main/n/nss/libnss3_3.87.1-1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/n/nspr/libnspr4_4.35-1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/a/at-spi2-core/libatspi2.0-0_2.46.0-5_amd64.deb",
    "https://deb.debian.org/debian/pool/main/a/at-spi2-atk/libatk-bridge2.0-0_2.38.0-4_amd64.deb",
    "https://deb.debian.org/debian/pool/main/a/atk1.0/libatk1.0-0_2.38.0-3_amd64.deb",
    "https://deb.debian.org/debian/pool/main/c/cups/libcups2_2.4.2-3+deb12u5_amd64.deb",
    "https://deb.debian.org/debian/pool/main/libd/libdrm/libdrm2_2.4.114-1+b1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/m/mesa/libgbm1_22.3.6-1+deb12u1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/libx/libxkbcommon/libxkbcommon0_1.5.0-1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/libx/libxcomposite/libxcomposite1_0.4.5-1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/libx/libxdamage/libxdamage1_1.1.6-1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/libx/libxrandr/libxrandr2_1.5.2-2+b1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/a/alsa-lib/libasound2_1.2.8-1+b1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/p/pango1.0/libpango-1.0-0_1.50.12+ds-1_amd64.deb",
    "https://deb.debian.org/debian/pool/main/p/pango1.0/libpangocairo-1.0-0_1.50.12+ds-1_amd64.deb",
]


def install_chrome():
    """Chrome for Testing indir ve kur."""
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


def extract_deb(deb_path, target_dir):
    """Bir .deb dosyasından shared library'leri çıkart."""
    tmp_dir = "/tmp/deb_extract"
    os.makedirs(tmp_dir, exist_ok=True)

    # ar x <file>.deb  →  data.tar.*
    subprocess.run(["ar", "x", deb_path], cwd=tmp_dir, check=True,
                   capture_output=True)

    # data.tar.xz veya data.tar.gz veya data.tar.zst bul
    data_tar = None
    for f in os.listdir(tmp_dir):
        if f.startswith("data.tar"):
            data_tar = os.path.join(tmp_dir, f)
            break

    if not data_tar:
        print(f"  UYARI: {deb_path} içinde data.tar bulunamadı")
        return

    # .so dosyalarını çıkart
    if data_tar.endswith(".zst"):
        # zstd destekli çıkartma
        subprocess.run(
            f"zstd -d '{data_tar}' -o /tmp/data.tar && tar xf /tmp/data.tar -C '{target_dir}'",
            shell=True, check=True, capture_output=True,
        )
    else:
        with tarfile.open(data_tar) as tar:
            tar.extractall(target_dir)

    # Temizlik
    for f in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, f))


def install_libs():
    """Chrome'un ihtiyaç duyduğu eksik sistem kütüphanelerini indir."""
    os.makedirs(LIB_DIR, exist_ok=True)

    for pkg_url in DEB_PACKAGES:
        pkg_name = pkg_url.split("/")[-1]
        deb_path = f"/tmp/{pkg_name}"

        print(f"  İndiriliyor: {pkg_name}")
        try:
            urllib.request.urlretrieve(pkg_url, deb_path)
            extract_deb(deb_path, LIB_DIR)
            os.remove(deb_path)
        except Exception as e:
            print(f"  UYARI: {pkg_name} indirilemedi: {e}")

    # Tüm .so dosyalarını tek bir dizine topla
    flat_lib = os.path.join(LIB_DIR, "lib")
    os.makedirs(flat_lib, exist_ok=True)

    for root, dirs, files in os.walk(LIB_DIR):
        if root == flat_lib:
            continue
        for f in files:
            if ".so" in f:
                src = os.path.join(root, f)
                dst = os.path.join(flat_lib, f)
                if not os.path.exists(dst):
                    os.rename(src, dst)

    print(f"Kütüphaneler kuruldu: {flat_lib}")
    print(f"  Toplam .so dosyası: {len(os.listdir(flat_lib))}")


def check_chrome():
    """Chrome binary'sinin çalışıp çalışmadığını kontrol et."""
    chrome_binary = os.path.join(INSTALL_DIR, "chrome-linux64", "chrome")
    lib_path = os.path.join(LIB_DIR, "lib")

    env = os.environ.copy()
    existing = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = f"{lib_path}:{existing}" if existing else lib_path

    result = subprocess.run(
        ["ldd", chrome_binary], capture_output=True, text=True, env=env
    )
    missing = [line.strip() for line in result.stdout.splitlines() if "not found" in line]

    if missing:
        print(f"UYARI: {len(missing)} eksik kütüphane var:")
        for m in missing:
            print(f"  {m}")
    else:
        print("Tüm kütüphaneler mevcut!")


if __name__ == "__main__":
    install_chrome()
    print("\nSistem kütüphaneleri indiriliyor...")
    install_libs()
    print("\nChrome bağımlılık kontrolü:")
    check_chrome()
