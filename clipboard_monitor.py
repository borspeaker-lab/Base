import time
import re
import subprocess
import os

CLIPBOARD_FILE = "links.txt"
CHECK_INTERVAL = 1

URL_PATTERN = re.compile(
    r'https?://[^\s<>"\'`\)\]\},]+|'
    r'www\.[^\s<>"\'`\)\]\},]+'
)

def get_clipboard():
    try:
        result = subprocess.run(
            ["powershell", "-command", "Get-Clipboard"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return ""

def extract_urls(text):
    urls = []
    for match in URL_PATTERN.finditer(text):
        url = match.group(0)
        end = match.end()
        while url.count("(") > url.count(")"):
            rest = text[end:]
            close = rest.find(")")
            if close == -1:
                break
            url += rest[:close + 1]
            end += close + 1
        urls.append(url)
    return urls

def main():
    last_content = ""
    seen_urls = set()

    if os.path.exists(CLIPBOARD_FILE):
        with open(CLIPBOARD_FILE, "r", encoding="utf-8") as f:
            for line in f:
                seen_urls.add(line.strip())

    print("Monitor boba zahyplennyu zapysheno. Dlia zupynky natysnit' Ctrl+C.\n")

    try:
        while True:
            content = get_clipboard()
            if content and content != last_content:
                last_content = content
                urls = extract_urls(content)
                for url in urls:
                    if url not in seen_urls:
                        seen_urls.add(url)
                        with open(CLIPBOARD_FILE, "a", encoding="utf-8") as f:
                            f.write(url + "\n")
                        print(f"[+] {url}")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\nZupyneno.")

if __name__ == "__main__":
    main()
