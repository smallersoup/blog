#!/usr/bin/env python3
"""Check the production HTML, not only the source templates, before deployment."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import sys


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.head = False
        self.ad_loaders = []
        self.ad_units = []
        self.scripts = []
        self.links = []
        self.robots = []
        self.invalid_head_elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self.head = True
        if self.head and tag in {"div", "article", "section", "p", "img"}:
            self.invalid_head_elements.append(tag)
        if tag == "script":
            src = attrs.get("src", "")
            self.scripts.append(src)
            if "pagead/js/adsbygoogle.js" in src:
                self.ad_loaders.append((src, self.head))
        if tag == "ins" and "adsbygoogle" in attrs.get("class", ""):
            self.ad_units.append(attrs)
        if tag == "a":
            self.links.append(attrs.get("href") or "")
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots.append(attrs.get("content", ""))

    def handle_endtag(self, tag):
        if tag == "head":
            self.head = False


root = Path(sys.argv[1] if len(sys.argv) > 1 else "public").resolve()
assert root.is_dir(), f"Build output does not exist: {root}"
pages = {}
for path in root.rglob("*.html"):
    relative = path.relative_to(root).as_posix()
    page = Page(path.read_text())
    pages[relative] = page
    assert not page.invalid_head_elements, (relative, page.invalid_head_elements)
    assert len(page.ad_loaders) <= 1, f"Duplicate AdSense loader: {relative}"
    assert all(in_head for _, in_head in page.ad_loaders), f"AdSense outside head: {relative}"
    assert not any("/go/?target=" in href for href in page.links), f"New redirect links: {relative}"
    if page.ad_units:
        assert len(page.ad_loaders) == 1, f"Ad unit without loader: {relative}"

for prefix in ("", "en/"):
    home = pages[prefix + "index.html"]
    assert len(home.ad_loaders) == 1, f"Missing homepage AdSense loader: {prefix}"
    for name in ("about", "contact", "privacy"):
        relative = prefix + name + "/index.html"
        page = pages[relative]
        assert not page.ad_loaders and not page.ad_units, f"Advertising on information page: {relative}"
        html = (root / relative).read_text()
        for tracking in ("analytics.umami.is", "hm.baidu.com/hm.js", "ga.kubeinfo.cn/gtag",
                         "clarity.ms/tag", "cdn.webpushr.com", "hzh.sealos.run/js"):
            assert tracking not in html, f"Tracking on information page: {relative}: {tracking}"
        assert any(urlsplit(href).path == "/" + prefix + name + "/" for href in home.links), (
            f"Missing information link on homepage: {relative}"
        )
    redirect = pages[prefix + "go/index.html"]
    assert not redirect.ad_loaders and not redirect.ad_units
    assert any("noindex" in value for value in redirect.robots)

posts = [page for path, page in pages.items()
         if path.startswith(("posts/", "en/posts/")) and page.ad_units]
assert posts, "No article ad units found in the production build"
ads_txt = (root / "ads.txt").read_text().strip()
assert ads_txt == "google.com, pub-4709798421083568, DIRECT, f08c47fec0942fa0"

# Navigation and article links pointing into the site must resolve to real output.
broken = set()
for relative, page in pages.items():
    base = "https://kubeinfo.cn/" + relative.removesuffix("index.html")
    for href in page.links:
        url = urlsplit(urljoin(base, href))
        if url.hostname != "kubeinfo.cn":
            continue
        path = unquote(url.path).lstrip("/")
        target = root / path
        if not target.is_file() and not (target / "index.html").is_file():
            broken.add((relative, url.path))
assert not broken, "Broken internal links:\n" + "\n".join(map(str, sorted(broken)))
print(f"PASS: {len(pages)} HTML pages; unique head loaders; policy pages without tracking; "
      f"{len(posts)} article ad units; ads.txt; internal links")
