"""
fetch_covers.py — Vailib Cover Art Fetcher
==========================================
Fetches missing book cover images from Google Books API and Open Library,
saving them to /DATA/AppData/sopds/covers/ (persistent volume).

Usage:
    docker exec vailib python3 manage.py fetch_covers
    docker exec vailib python3 manage.py fetch_covers --limit 100
    docker exec vailib python3 manage.py fetch_covers --reset   (re-fetch all)
"""
import os
import time
import urllib.request
import urllib.parse
import json
import logging

from django.core.management.base import BaseCommand
from opds_catalog.models import Book

logger = logging.getLogger(__name__)

COVERS_DIR = '/var/lib/sopds/covers'
RATE_LIMIT_SECONDS = 6   # ~10 requests/min
GOOGLE_API = 'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1&fields=items(volumeInfo/imageLinks)'
OPENLIBRARY_API = 'https://openlibrary.org/search.json?title={title}&limit=1&fields=cover_i'
OPENLIBRARY_COVER = 'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg'


def ensure_dir():
    os.makedirs(COVERS_DIR, exist_ok=True)


def cover_path(book_id):
    return os.path.join(COVERS_DIR, '{}.jpg'.format(book_id))


def has_cover(book_id):
    p = cover_path(book_id)
    return os.path.exists(p) and os.path.getsize(p) > 5000


def download_image(url, dest_path):
    """Download image URL to dest_path. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Vailib/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        if len(data) < 2000:
            return False  # Too small — likely an error page
        with open(dest_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        logger.debug('Download failed %s: %s', url, e)
        return False


def fetch_google(title, author):
    """Try Google Books API. Returns image URL or None."""
    query = urllib.parse.quote('{} {}'.format(title[:60], author[:40]))
    url = GOOGLE_API.format(query=query)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Vailib/1.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        items = data.get('items', [])
        if items:
            links = items[0].get('volumeInfo', {}).get('imageLinks', {})
            img = links.get('thumbnail') or links.get('smallThumbnail')
            if img:
                # Upgrade to higher resolution
                img = img.replace('zoom=1', 'zoom=3').replace('http://', 'https://')
                return img
    except Exception as e:
        logger.debug('Google Books error: %s', e)
    return None


def fetch_openlibrary(title):
    """Try Open Library. Returns image URL or None."""
    query = urllib.parse.quote(title[:80])
    url = OPENLIBRARY_API.format(title=query)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Vailib/1.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        docs = data.get('docs', [])
        if docs and docs[0].get('cover_i'):
            return OPENLIBRARY_COVER.format(cover_id=docs[0]['cover_i'])
    except Exception as e:
        logger.debug('Open Library error: %s', e)
    return None


class Command(BaseCommand):
    help = 'Fetch missing book cover art from Google Books and Open Library'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=200,
                            help='Max books to process per run (default: 200)')
        parser.add_argument('--reset', action='store_true',
                            help='Re-fetch covers even for books that already have one')
        parser.add_argument('--book-id', type=int, default=None,
                            help='Fetch cover for a single specific book ID')

    def handle(self, *args, **options):
        ensure_dir()
        self.stdout.write(self.style.SUCCESS(
            'Cover fetcher started. Saving to: {}'.format(COVERS_DIR)
        ))

        if options['book_id']:
            books = Book.objects.filter(id=options['book_id'])
        else:
            books = Book.objects.all().order_by('-docdate')

        limit = options['limit']
        reset = options['reset']

        fetched = 0
        skipped = 0
        failed = 0
        processed = 0

        for book in books:
            if processed >= limit:
                break

            if not reset and has_cover(book.id):
                skipped += 1
                continue

            processed += 1

            # Build title and author strings
            title = book.title or ''
            # Clean filename-style titles
            title = title.replace('_', ' ').split('.')[0].strip()
            if len(title) < 3:
                failed += 1
                continue

            authors = list(book.authors.values_list('full_name', flat=True))
            author = authors[0] if authors else ''

            self.stdout.write('[{}/{}] {} — {}...'.format(
                processed, limit, title[:50], author[:30]
            ), ending='\r')
            self.stdout.flush()

            dest = cover_path(book.id)
            success = False

            # Try Google Books first
            img_url = fetch_google(title, author)
            if img_url:
                success = download_image(img_url, dest)

            # Fall back to Open Library
            if not success:
                img_url = fetch_openlibrary(title)
                if img_url:
                    success = download_image(img_url, dest)

            if success:
                fetched += 1
                self.stdout.write(self.style.SUCCESS(
                    '  ✓ [{}] {}'.format(book.id, title[:60])
                ))
            else:
                failed += 1

            # Rate limit
            time.sleep(RATE_LIMIT_SECONDS)

        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS(
            'Done! Fetched: {} | Skipped (already had cover): {} | Failed: {}'.format(
                fetched, skipped, failed
            )
        ))
