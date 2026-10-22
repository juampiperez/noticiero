#!/usr/bin/env python3
"""Lee los RSS de feeds.json y genera news.json. Solo usa la biblioteca estándar."""
import json, re, sys, html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEEDS_FILE = sys.argv[1] if len(sys.argv) > 1 else "feeds.json"
PER_FEED = 12
MAX_PER_CATEGORY = 60
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NoticieroPersonal/1.0)"}


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def parse_date(value):
    if not value:
        return None
    value = value.strip()
    try:
        d = parsedate_to_datetime(value)
    except Exception:
        try:
            d = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def local(tag):
    return tag.rsplit("}", 1)[-1]


def text_of(el, names):
    for c in el:
        if local(c.tag) in names and (c.text or "").strip():
            return c.text
    return ""


def parse_feed(xml_bytes):
    root = ET.fromstring(xml_bytes)
    for el in root.iter():
        if local(el.tag) not in ("item", "entry"):
            continue
        link = text_of(el, ("link",))
        if not link:
            for c in el:
                if local(c.tag) == "link" and c.get("href"):
                    link = c.get("href")
                    break
        yield {
            "title": clean(text_of(el, ("title",))),
            "summary": clean(text_of(el, ("description", "summary", "content"))),
            "link": (link or "").strip(),
            "date": parse_date(text_of(el, ("pubDate", "published", "updated", "date"))),
        }


def main():
    with open(FEEDS_FILE, encoding="utf-8") as f:
        config = json.load(f)

    now = datetime.now(timezone.utc)
    items, errors = [], []

    for category, feeds in config.items():
        seen, bucket = set(), []
        for feed in feeds:
            try:
                req = urllib.request.Request(feed["url"], headers=HEADERS)
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = r.read()
                count = 0
                for e in parse_feed(data):
                    if not e["title"] or not e["link"] or e["link"] in seen:
                        continue
                    seen.add(e["link"])
                    summary = e["summary"]
                    if summary == e["title"]:
                        summary = ""
                    if len(summary) > 280:
                        summary = summary[:277].rsplit(" ", 1)[0] + "…"
                    bucket.append({
                        "category": category,
                        "source": feed["name"],
                        "title": e["title"],
                        "summary": summary,
                        "link": e["link"],
                        "date": (e["date"] or now).isoformat(),
                    })
                    count += 1
                    if count >= PER_FEED:
                        break
                print(f"OK    {feed['name']}: {count} notas")
            except Exception as ex:
                errors.append(feed["name"])
                print(f"ERROR {feed['name']}: {ex}", file=sys.stderr)
        bucket.sort(key=lambda x: x["date"], reverse=True)
        items.extend(bucket[:MAX_PER_CATEGORY])

    if not items:
        print("No se obtuvo ninguna nota.", file=sys.stderr)
        sys.exit(1)

    items.sort(key=lambda x: x["date"], reverse=True)
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump({"updated": now.isoformat(), "items": items}, f, ensure_ascii=False, indent=1)
    print(f"Total: {len(items)} notas. Fuentes con error: {', '.join(errors) or 'ninguna'}")


main()
