# -*- coding: utf-8 -*-
"""
CLI Tool for EnterPick24 OTT Automation Engine.
Commands:
- `python -m core.ott_engine.cli publish "Stranger Things"`
- `python -m core.ott_engine.cli schedule_today`
- `python -m core.ott_engine.cli reset_all_posts`
"""

import sys
import argparse
import logging
from core.ott_engine.ott_writer import OTTWriter
from core.ott_engine.publisher import OTTPublisher
from core.ott_engine.tvmaze_client import TVmazeClient
from core.ott_engine.config import WP_URL, WP_USER, WP_PASS
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ott_cli")


def reset_all_posts():
    """Deletes all posts on EnterPick24 completely."""
    url = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/posts"
    auth = (WP_USER, WP_PASS)
    res = requests.get(url, params={"per_page": 100, "status": "any"}, auth=auth)
    if not res.ok:
        logger.error(f"Failed to fetch posts: {res.status_code}")
        return
    posts = res.json()
    logger.info(f"Deleting {len(posts)} posts from {WP_URL}...")
    for p in posts:
        pid = p["id"]
        del_res = requests.delete(f"{url}/{pid}", params={"force": True}, auth=auth)
        logger.info(f" - Deleted post #{pid}: {del_res.status_code}")
    logger.info("EnterPick24 posts reset complete.")


def publish_show(query: str, status: str = "publish"):
    """Generates and publishes an OTT article for the specified show."""
    logger.info(f"Starting OTT pipeline for '{query}' (status: {status})...")
    writer = OTTWriter()
    article = writer.generate_article_for_show(query)
    if not article:
        logger.error("Failed to generate article.")
        return False

    logger.info(f"Article generated: '{article['title']}' ({len(article['content'])} bytes)")
    logger.info(f"Quality gate: {article['quality_gate']}")

    publisher = OTTPublisher()
    result = publisher.publish_article(article, status=status)
    if result.get("success"):
        logger.info(f"SUCCESS! Published Post #{result.get('post_id')}: {result.get('link')}")
        return True
    else:
        logger.error(f"Failed to publish: {result.get('error')}")
        return False


def main():
    parser = argparse.ArgumentParser(description="EnterPick24 OTT Automation CLI")
    subparsers = parser.add_subparsers(dest="command")

    # publish command
    pub_parser = subparsers.add_parser("publish", help="Publish article for a show")
    pub_parser.add_argument("query", type=str, help="Show name to search (e.g. 'Stranger Things')")
    pub_parser.add_argument("--status", type=str, default="publish", choices=["publish", "future", "draft"])

    # reset command
    subparsers.add_parser("reset", help="Reset and delete all posts on EnterPick24")

    args = parser.parse_args()

    if args.command == "publish":
        publish_show(args.query, status=args.status)
    elif args.command == "reset":
        reset_all_posts()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
