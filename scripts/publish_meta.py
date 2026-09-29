#!/usr/bin/env python3
"""Post a built card set to Instagram and the Facebook Page as carousels.

Talks to Meta's Graph API directly -- no scheduler in between. Kannada goes out
first, English second, as two separate posts on each platform, cards in
filename order (docs/distribution.md).

Instagram does not take uploads: it fetches each image from a public URL. The
repo is public and the built PNGs are committed, so every card already has one
on raw.githubusercontent.com once it is pushed. Before anything is posted, each
URL is downloaded and its hash compared with the local file -- a card that is
not pushed yet, or pushed in an older version, stops the run.

Dry run is the default: it finds the cards, checks every one is 1080x1350,
checks the public URLs and the caption files, and prints what it would post.
Nothing reaches Meta without --publish.

    python3 scripts/publish_meta.py editions/2026-09-24/today
    python3 scripts/publish_meta.py editions/2026-09-24/today --publish
    python3 scripts/publish_meta.py --whoami

Captions come from <set>/work/caption-kn.txt and caption-en.txt. They follow
the same rules as the cards -- report, don't advise; attribute; spoken Kannada.
A missing caption file stops the run rather than posting a bare carousel.

Credentials come from the environment, never from the repo:

  META_PAGE_ID         the Facebook Page's numeric id
  META_IG_USER_ID      the Instagram professional account's id (--whoami finds it)
  META_PAGE_TOKEN      a Page access token with pages_manage_posts,
                       pages_read_engagement, instagram_basic and
                       instagram_content_publish. Derived from a long-lived user
                       token, it does not expire; it dies if the password changes
                       or the app loses access.
  META_GRAPH_VERSION   optional, default v23.0

Exit codes
  0  everything asked for was posted (or, in a dry run, would be)
  1  some posts went out, some failed -- the summary says which
  2  nothing posted: a check failed before the first post
"""

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
GRAPH = "https://graph.facebook.com/" + os.environ.get("META_GRAPH_VERSION", "v23.0")
CARD_SIZE = (1080, 1350)
MAX_CARDS = 10          # Instagram carousel limit
LANGS = ("kn", "en")    # posting order


class Fail(Exception):
    pass


# ---------------------------------------------------------------- cards

def find_cards(set_dir, lang):
    """Carousel cards for one language, in number order. Tall WhatsApp images
    (tall-*, whatsapp-*) are skipped -- they never go in a carousel."""
    pat = re.compile(rf"^(?!tall-|whatsapp-).*-{lang}-(\d+)\.png$")
    cards = [(int(m.group(1)), p) for p in (set_dir / "out").glob("*.png")
             if (m := pat.match(p.name))]
    return [p for _, p in sorted(cards)]


def check_cards(cards, lang):
    if not cards:
        raise Fail(f"{lang}: no carousel cards in out/")
    if len(cards) > MAX_CARDS:
        raise Fail(f"{lang}: {len(cards)} cards, Instagram takes at most {MAX_CARDS}")
    for p in cards:
        with Image.open(p) as im:
            if im.size != CARD_SIZE:
                raise Fail(f"{p.name} is {im.size[0]}x{im.size[1]}, not 1080x1350")


def read_caption(set_dir, lang):
    path = set_dir / "work" / f"caption-{lang}.txt"
    if not path.exists():
        raise Fail(f"{lang}: no caption at {path.relative_to(ROOT).as_posix()}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise Fail(f"{lang}: {path.name} is empty")
    if len(text) > 2200:
        raise Fail(f"{lang}: caption is {len(text)} characters, Instagram allows 2200")
    return text


# ---------------------------------------------------------------- public URLs

def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def raw_base():
    """https://raw.githubusercontent.com/<owner>/<repo>/<commit>/ for HEAD.
    Pinned to the commit, not the branch, so a later push cannot swap a card
    between the check and Instagram's fetch."""
    remote = git("remote", "get-url", "origin")
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", remote)
    if not m:
        raise Fail(f"origin is not a GitHub repo: {remote}")
    return f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{git('rev-parse', 'HEAD')}/"


def public_url(base, path):
    rel = path.resolve().relative_to(ROOT).as_posix()
    return base + urllib.parse.quote(rel)


def check_public(url, path):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        raise Fail(f"{path.name}: {e.code} at {url} -- is the commit pushed?")
    if hashlib.sha256(body).digest() != hashlib.sha256(path.read_bytes()).digest():
        raise Fail(f"{path.name}: the pushed copy differs from the local file")


# ---------------------------------------------------------------- Graph API

def graph(method, path, token, **params):
    """One Graph call. The token rides in the Authorization header, never in
    the URL, so it cannot end up in a log line."""
    url = f"{GRAPH}/{path}"
    data = None
    if method == "GET":
        if params:
            url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            err = json.load(e).get("error", {})
            msg = f"{err.get('type')} {err.get('code')}: {err.get('message')}"
        except ValueError:
            msg = str(e)
        raise Fail(f"Graph {method} {path}: {msg}")


def env(name):
    val = os.environ.get(name)
    if not val:
        raise Fail(f"{name} is not set")
    return val


def wait_ready(container, token, label):
    """Instagram processes each image after the container is created; publishing
    before it reports FINISHED fails."""
    for _ in range(30):
        status = graph("GET", container, token, fields="status_code").get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise Fail(f"{label}: Instagram reports {status}")
        time.sleep(5)
    raise Fail(f"{label}: still processing after 150s")


def post_instagram(urls, caption, token):
    ig = env("META_IG_USER_ID")
    children = []
    for i, url in enumerate(urls, 1):
        cid = graph("POST", f"{ig}/media", token, image_url=url, is_carousel_item="true")["id"]
        wait_ready(cid, token, f"card {i}")
        children.append(cid)
    parent = graph("POST", f"{ig}/media", token, media_type="CAROUSEL",
                   children=",".join(children), caption=caption)["id"]
    wait_ready(parent, token, "carousel")
    media = graph("POST", f"{ig}/media_publish", token, creation_id=parent)["id"]
    return graph("GET", media, token, fields="permalink").get("permalink", media)


def post_facebook(urls, caption, token):
    page = env("META_PAGE_ID")
    photos = [graph("POST", f"{page}/photos", token, url=url, published="false")["id"]
              for url in urls]
    attached = {f"attached_media[{i}]": json.dumps({"media_fbid": pid})
                for i, pid in enumerate(photos)}
    post = graph("POST", f"{page}/feed", token, message=caption, **attached)["id"]
    return f"https://www.facebook.com/{post}"


def whoami():
    token, page = env("META_PAGE_TOKEN"), env("META_PAGE_ID")
    info = graph("GET", page, token, fields="name,instagram_business_account{id,username}")
    print(f"Page       {info.get('name')}  ({page})")
    ig = info.get("instagram_business_account")
    if ig:
        print(f"Instagram  @{ig.get('username')}  ->  META_IG_USER_ID={ig['id']}")
    else:
        print("Instagram  none linked -- link the professional account to this Page")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("set_dir", nargs="?", help="a card set, e.g. editions/2026-09-24/today")
    ap.add_argument("--lang", choices=("kn", "en", "both"), default="both")
    ap.add_argument("--platform", choices=("instagram", "facebook", "both"), default="both")
    ap.add_argument("--publish", action="store_true", help="actually post (default is a dry run)")
    ap.add_argument("--whoami", action="store_true", help="check the token and print the account ids")
    a = ap.parse_args()

    try:
        if a.whoami:
            whoami()
            return 0
        if not a.set_dir:
            ap.error("set_dir is required")

        set_dir = (pathlib.Path.cwd() / a.set_dir).resolve()
        langs = LANGS if a.lang == "both" else (a.lang,)
        platforms = ("instagram", "facebook") if a.platform == "both" else (a.platform,)

        # every check runs before the first post, so a bad English card cannot
        # leave the Kannada post live on its own
        base = raw_base()
        plan = []
        for lang in langs:
            cards = find_cards(set_dir, lang)
            check_cards(cards, lang)
            caption = read_caption(set_dir, lang)
            urls = [public_url(base, p) for p in cards]
            for p, url in zip(cards, urls):
                check_public(url, p)
            plan.append((lang, cards, urls, caption))
        token = env("META_PAGE_TOKEN") if a.publish else None
    except Fail as e:
        print(f"STOP  {e}", file=sys.stderr)
        return 2

    posted = failed = 0
    for lang, cards, urls, caption in plan:
        print(f"\n[{lang}] {len(cards)} cards: {', '.join(p.name for p in cards)}")
        print(f"  caption: {caption.splitlines()[0][:70]}")
        for platform in platforms:
            if not a.publish:
                print(f"  {platform:9}  would post")
                continue
            try:
                post = post_instagram if platform == "instagram" else post_facebook
                print(f"  {platform:9}  {post(urls, caption, token)}")
                posted += 1
            except Fail as e:
                print(f"  {platform:9}  FAILED  {e}", file=sys.stderr)
                failed += 1

    if not a.publish:
        print("\nDry run -- nothing posted. Add --publish to post.")
        return 0
    return 0 if not failed else (1 if posted else 2)


if __name__ == "__main__":
    sys.exit(main())
