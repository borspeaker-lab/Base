import re

URL_PATTERN = re.compile(
    r'https?://[^\s<>"\'`\)\]\},]+|'
    r'www\.[^\s<>"\'`\)\]\},]+'
)

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

tests = [
    # --- Basic URLs (1-10) ---
    ("Visit https://google.com", ["https://google.com"]),
    ("Open http://example.com/page", ["http://example.com/page"]),
    ("Go to www.example.com", ["www.example.com"]),
    ("Check https://github.com/user/repo", ["https://github.com/user/repo"]),
    ("Link: http://test.org/path?q=1", ["http://test.org/path?q=1"]),
    ("https://stackoverflow.com/questions/123", ["https://stackoverflow.com/questions/123"]),
    ("http://localhost:8080/api", ["http://localhost:8080/api"]),
    ("www.google.com/search?q=python", ["www.google.com/search?q=python"]),
    ("https://sub.domain.example.com/path", ["https://sub.domain.example.com/path"]),
    ("http://192.168.1.1/admin", ["http://192.168.1.1/admin"]),

    # --- Multiple URLs in one text (11-20) ---
    ("See https://a.com and https://b.com", ["https://a.com", "https://b.com"]),
    ("http://x.com http://y.com http://z.com", ["http://x.com", "http://y.com", "http://z.com"]),
    ("one www.a.com two www.b.com", ["www.a.com", "www.b.com"]),
    ("Mix: https://a.com and http://b.com and www.c.com", ["https://a.com", "http://b.com", "www.c.com"]),
    ("Urls: https://one.com/path, https://two.com/path", ["https://one.com/path", "https://two.com/path"]),
    ("Ahttps://tricky.com", ["https://tricky.com"]),
    ("prefix-https://also.com", ["https://also.com"]),
    ("(https://in-parens.com)", ["https://in-parens.com"]),
    ("https://a.com/b/c/d/e/f/g", ["https://a.com/b/c/d/e/f/g"]),
    ("test http://short.io x", ["http://short.io"]),

    # --- No URLs (21-30) ---
    ("Hello world", []),
    ("No links here!", []),
    ("Just some text 12345", []),
    ("email@gmail.com is not a URL with scheme", []),
    ("ftp://files.server.com should not match", []),
    ("://invalid.com should not match", []),
    ("", []),
    ("   ", []),
    ("\n\n\n", []),
    ("Just numbers: 123 456 789", []),

    # --- URLs with paths and parameters (31-40) ---
    ("https://example.com/path/to/page?foo=bar&baz=1", ["https://example.com/path/to/page?foo=bar&baz=1"]),
    ("http://example.com/page#section", ["http://example.com/page#section"]),
    ("https://example.com/path(1)", ["https://example.com/path(1)"]),
    ("https://en.wikipedia.org/wiki/Python_(programming_language)", ["https://en.wikipedia.org/wiki/Python_(programming_language)"]),
    ("http://a.com/page?key=value&key2=value2#frag", ["http://a.com/page?key=value&key2=value2#frag"]),
    ("https://example.com/~user/page", ["https://example.com/~user/page"]),
    ("http://example.com/path/to/page.", ["http://example.com/path/to/page."]),
    ("https://example.com/path,more", ["https://example.com/path"]),
    ("https://example.com/path;params", ["https://example.com/path;params"]),
    ("https://example.com/a%20b%20c", ["https://example.com/a%20b%20c"]),

    # --- Edge cases with surrounding characters (41-50) ---
    ("url: https://test.com.", ["https://test.com."]),
    ("see (https://brackets.com)", ["https://brackets.com"]),
    ("click [https://bracket.com]", ["https://bracket.com"]),
    ("text 'https://quoted.com' more", ["https://quoted.com"]),
    ('text "https://dquot.com" more', ["https://dquot.com"]),
    ("https://end.com!", ["https://end.com!"]),
    ("https://trail.com;", ["https://trail.com;"]),
    ("https://comma.com,", ["https://comma.com"]),
    ("https://colon.com:", ["https://colon.com:"]),
    ("https://quest.com?", ["https://quest.com?"]),

    # --- www without http (51-60) ---
    ("www site: www.mysite.com", ["www.mysite.com"]),
    ("go to www.google.com now", ["www.google.com"]),
    ("www.a.com www.b.com www.c.com", ["www.a.com", "www.b.com", "www.c.com"]),
    ("www.sub.domain.co.uk", ["www.sub.domain.co.uk"]),
    ("visit www.test.com/path?q=1&r=2", ["www.test.com/path?q=1&r=2"]),
    ("www.has-hyphen.com", ["www.has-hyphen.com"]),
    ("www.under_score.com", ["www.under_score.com"]),
    ("www.numbers123.com", ["www.numbers123.com"]),
    ("prefix www.link.com suffix", ["www.link.com"]),
    ("www.dots.in.name.co.jp/path", ["www.dots.in.name.co.jp/path"]),

    # --- http vs https (61-70) ---
    ("http://plain.com", ["http://plain.com"]),
    ("https://secure.com", ["https://secure.com"]),
    ("http a.com - no match", []),
    ("httpsa.com - no match", []),
    ("http://a.com https://b.com", ["http://a.com", "https://b.com"]),
    ("both: http://x.com and https://x.com", ["http://x.com", "https://x.com"]),
    ("http://login:pass@host.com", ["http://login:pass@host.com"]),
    ("https://user:pwd@server.org/path", ["https://user:pwd@server.org/path"]),
    ("http://example.com:8080", ["http://example.com:8080"]),
    ("https://example.com:443/path", ["https://example.com:443/path"]),

    # --- Multiline text (71-80) ---
    ("line1\nhttps://multiline.com\nline3", ["https://multiline.com"]),
    ("a\nb\nhttp://between.com\nc", ["http://between.com"]),
    ("https://first.com\nhttps://second.com", ["https://first.com", "https://second.com"]),
    ("text\nwww.inline.com\ntext", ["www.inline.com"]),
    ("\n\nhttps://gaps.com\n\n", ["https://gaps.com"]),
    ("https://a.com\n\n\nhttps://b.com", ["https://a.com", "https://b.com"]),
    ("line1\nline2\nline3", []),
    ("\n\n\n", []),
    ("start\nwww.a.com\nmiddle\nwww.b.com\nend", ["www.a.com", "www.b.com"]),
    ("https://x.com\n\n\n\nhttps://y.com", ["https://x.com", "https://y.com"]),

    # --- Duplicates (81-85) ---
    ("https://dup.com https://dup.com", ["https://dup.com", "https://dup.com"]),
    ("www.dup.com www.dup.com www.dup.com", ["www.dup.com", "www.dup.com", "www.dup.com"]),
    ("http://a.com http://a.com http://a.com", ["http://a.com", "http://a.com", "http://a.com"]),
    ("same https://x.com different https://x.com", ["https://x.com", "https://x.com"]),
    ("https://one.com https://two.com https://one.com", ["https://one.com", "https://two.com", "https://one.com"]),

    # --- Tricky / realistic (86-95) ---
    ("Ссылка: https://yandex.ru/search/?text=python", ["https://yandex.ru/search/?text=python"]),
    ("GitHub: https://github.com/python/cpython", ["https://github.com/python/cpython"]),
    ("Docs: https://docs.python.org/3/library/re.html", ["https://docs.python.org/3/library/re.html"]),
    ("Prices on https://amazon.com/dp/B08N5WRWNW?tag=123", ["https://amazon.com/dp/B08N5WRWNW?tag=123"]),
    ("Watch: https://www.youtube.com/watch?v=dQw4w9WgXcQ", ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]),
    ("Tweet: https://twitter.com/user/status/123456789", ["https://twitter.com/user/status/123456789"]),
    ("Chat: https://t.me/joinchat/ABC123", ["https://t.me/joinchat/ABC123"]),
    ("Reddit: https://old.reddit.com/r/python/top/?t=month", ["https://old.reddit.com/r/python/top/?t=month"]),
    ("News: https://news.ycombinator.com/item?id=12345", ["https://news.ycombinator.com/item?id=12345"]),
    ("API: https://api.example.com/v2/users?page=1&limit=10", ["https://api.example.com/v2/users?page=1&limit=10"]),

    # --- Negative / edge (96-100) ---
    ("not a link: htp://wrong.com", []),
    ("almost: //missing-scheme.com", []),
    ("ftp://not-http.com", []),
    ("file:///local/path", []),
    ("just text with dots... www.", []),
]

passed = 0
failed = 0
fail_details = []

for i, (text, expected) in enumerate(tests, 1):
    result = extract_urls(text)
    if result == expected:
        passed += 1
    else:
        failed += 1
        fail_details.append((i, text, expected, result))

print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
if fail_details:
    print("\nFailed tests:")
    for idx, text, exp, got in fail_details:
        print(f"  #{idx}: text={repr(text)}")
        print(f"       expected: {exp}")
        print(f"       got:      {got}")
