#!/usr/bin/env python3
import os
import re
import sys
import time
import argparse
import requests
import xml.etree.ElementTree as ET

# Reconfigure stdout to use UTF-8 on Windows to prevent UnicodeEncodeError with emojis
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Default list of all 12 supported languages
DEFAULT_LANGUAGES = ["en", "ru", "de", "el", "es", "fr", "ar", "hi", "pt", "zh", "bn", "nl"]

# Gutenberg/Gutendex API base URL
GUTENDEX_URL = "https://gutendex.com/books"

# Official Project Gutenberg OPDS base URL
GUTENBERG_OPDS_URL = "https://www.gutenberg.org/ebooks/search.opds/"

# Standard Ebooks OPDS URL
STANDARD_EBOOKS_OPDS_URL = "https://standardebooks.org/opds/all"


def clean_filename(name):
    """
    Remove unsafe filesystem characters and keep it clean and robust.
    """
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', " ", name)
    return name.strip()

def get_existing_ids(directory):
    """
    Scan the target directory and extract Gutenberg IDs from filenames like:
    'Author - Title (ID).epub' or similar containing '(ID)'
    """
    existing_ids = set()
    if not os.path.exists(directory):
        return existing_ids
    
    # Match pattern like: (12345).epub or (12345)
    pattern = re.compile(r'\((\d+)\)\.[a-zA-Z0-9]+$')
    for filename in os.listdir(directory):
        match = pattern.search(filename)
        if match:
            existing_ids.add(int(match.group(1)))
    return existing_ids

def download_book(download_url, dest_path):
    """
    Download a file from download_url and save it to dest_path.
    """
    try:
        # Gutenberg uses redirects for downloads, allow them
        response = requests.get(download_url, timeout=30, stream=True)
        # If epub.images 404s, try epub.noimages
        if response.status_code == 404 and "epub.images" in download_url:
            fallback_url = download_url.replace(".epub.images", ".epub.noimages")
            response = requests.get(fallback_url, timeout=30, stream=True)
            
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to download {download_url}: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False

def parse_opds_feed(xml_text):
    """
    Parse Gutenberg OPDS Atom XML and extract book list.
    Returns: (list of dicts, next_page_url)
    """
    books = []
    try:
        root = ET.fromstring(xml_text)
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'opds': 'http://opds-spec.org/2010/catalog'
        }
        
        # Find all <ns0:entry> elements
        for entry in root.findall('atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            title = title_el.text.strip() if title_el is not None else "Unknown Title"
            
            # Strip trailing language suffix like " (Dutch)" or " (English)"
            title = re.sub(r'\s*\([^)]*\)$', '', title).strip()
            
            # Find author name in <content> (search results feed format) or <author><name>
            author_name = "Unknown Author"
            content_el = entry.find('atom:content', ns)
            if content_el is not None and content_el.text:
                author_name = content_el.text.strip()
            else:
                author_el = entry.find('atom:author', ns)
                if author_el is not None:
                    name_el = author_el.find('atom:name', ns)
                    if name_el is not None:
                        author_name = name_el.text.strip()
            
            # Find book ID from <id> tag or links
            book_id = None
            id_el = entry.find('atom:id', ns)
            if id_el is not None and id_el.text:
                match = re.search(r'/ebooks/(\d+)', id_el.text)
                if match:
                    book_id = int(match.group(1))
            
            if not book_id:
                for link in entry.findall('atom:link', ns):
                    href = link.get('href', '')
                    match = re.search(r'/ebooks/(\d+)', href)
                    if match:
                        book_id = int(match.group(1))
                        break
            
            if book_id:
                author_name = author_name.replace('\ufffd', '').strip()
                # Format "Lastname, Firstname" to "Firstname Lastname"
                if "," in author_name and " and " not in author_name:
                    parts = author_name.split(",", 1)
                    author_name = f"{parts[1].strip()} {parts[0].strip()}"
                
                # Construct direct download URL (prefer images, fall back to noimages in download_book)
                epub_url = f"https://www.gutenberg.org/ebooks/{book_id}.epub.images"
                
                books.append({
                    "id": book_id,
                    "title": title,
                    "author": author_name,
                    "epub_url": epub_url
                })
        
        # Extract next page link
        next_url = None
        for link in root.findall('atom:link', ns):
            if link.get('rel') == 'next':
                next_url = link.get('href')
                if next_url and next_url.startswith('/'):
                    next_url = "https://www.gutenberg.org" + next_url
                break
                
        return books, next_url
    except Exception as e:
        print(f"  [ERROR] XML parsing failed: {e}")
        return [], None

def fetch_via_gutenberg_opds(lang, page_url_or_none=None):
    """
    Fetch popular books for a language using the official Gutenberg OPDS feed.
    """
    url = page_url_or_none or f"{GUTENBERG_OPDS_URL}?query=l.{lang}"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return parse_opds_feed(resp.text)
    except Exception as e:
        print(f"  [WARNING] Gutenberg OPDS fetch failed: {e}")
        return [], None

def fetch_via_gutendex(lang, page=1):
    """
    Fallback method: Fetch popular books for a language using Gutendex REST API.
    """
    params = {
        "languages": lang,
        "page": page
    }
    try:
        resp = requests.get(GUTENDEX_URL, params=params, timeout=15)
        if resp.status_code == 404:
            return [], None
        resp.raise_for_status()
        data = resp.json()
        
        books = []
        for book in data.get("results", []):
            book_id = book.get("id")
            formats = book.get("formats", {})
            epub_url = formats.get("application/epub+zip")
            
            if book_id and epub_url:
                authors = book.get("authors", [])
                author_name = "Unknown Author"
                if authors:
                    author_name = authors[0].get("name", "Unknown Author")
                    if "," in author_name:
                        parts = author_name.split(",", 1)
                        author_name = f"{parts[1].strip()} {parts[0].strip()}"
                
                title = book.get("title", "Unknown Title")
                books.append({
                    "id": book_id,
                    "title": title,
                    "author": author_name.replace('\ufffd', '').strip(),
                    "epub_url": epub_url
                })
                
        next_page = page + 1 if data.get("next") else None
        return books, next_page
    except Exception as e:
        print(f"  [WARNING] Gutendex fetch failed: {e}")
        return [], None

def parse_standard_ebooks_opds(xml_text):
    books = []
    try:
        root = ET.fromstring(xml_text)
        ns = {
            'atom': 'http://www.w3.org/2005/Atom'
        }
        
        for entry in root.findall('atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            title = title_el.text.strip() if title_el is not None else "Unknown Title"
            
            author_name = "Unknown Author"
            author_el = entry.find('atom:author', ns)
            if author_el is not None:
                name_el = author_el.find('atom:name', ns)
                if name_el is not None:
                    author_name = name_el.text.strip()
            
            # Find epub link
            epub_url = None
            for link in entry.findall('atom:link', ns):
                href = link.get('href', '')
                type_attr = link.get('type', '')
                if href.endswith('.epub') or type_attr == 'application/epub+zip':
                    epub_url = href
                    break
                    
            if epub_url:
                import hashlib
                book_id = int(hashlib.md5(epub_url.encode('utf-8')).hexdigest()[:8], 16)
                
                books.append({
                    "id": book_id,
                    "title": title,
                    "author": author_name,
                    "epub_url": epub_url
                })
                
        next_url = None
        for link in root.findall('atom:link', ns):
            if link.get('rel') == 'next':
                next_url = link.get('href')
                if next_url and not next_url.startswith('http'):
                    next_url = "https://standardebooks.org" + next_url
                break
                
        return books, next_url
    except Exception as e:
        print(f"  [ERROR] Standard Ebooks XML parsing failed: {e}")
        return [], None

def fetch_via_standard_ebooks(page_url_or_none=None):
    url = page_url_or_none or STANDARD_EBOOKS_OPDS_URL
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return parse_standard_ebooks_opds(resp.text)
    except Exception as e:
        print(f"  [WARNING] Standard Ebooks fetch failed: {e}")
        return [], None

def crawl_popular_books(languages, limit_per_lang, outdir, trigger_scan_path, source="gutenberg", progress_callback=None):
    """
    Crawl and download popular books for the selected languages.
    """
    os.makedirs(outdir, exist_ok=True)
    
    if source == "standardebooks":
        languages = ["en"]
        print("  [INFO] Standard Ebooks source is English-only. Forcing target language to 'en'.")
        
    print(f"Starting popular books downloader...")
    print(f"Source Catalog: {source.upper()}")
    print(f"Target languages: {', '.join(languages)}")
    print(f"Active download limit: {limit_per_lang} books per language")
    print(f"Output directory: {outdir}\n")

    for lang in languages:
        lang_dir = os.path.join(outdir, lang)
        os.makedirs(lang_dir, exist_ok=True)
        
        existing_ids = get_existing_ids(lang_dir)
        print(f"🌐 Processing language: {lang.upper()}")
        print(f"  Found {len(existing_ids)} existing books in local folder: {lang_dir}")
        
        if progress_callback:
            progress_callback(lang, 0, limit_per_lang, f"Scanning {source} catalog...")
            
        downloaded_count = 0
        has_more = True
        
        opds_next_url = None
        gutendex_page = 1
        engine = "gutenberg_opds" if source == "gutenberg" else source
        
        while downloaded_count < limit_per_lang and has_more:
            books = []
            
            if engine == "standardebooks":
                time.sleep(1.0)
                books, next_ref = fetch_via_standard_ebooks(opds_next_url)
                if books:
                    opds_next_url = next_ref
                    if not next_ref:
                        has_more = False
                else:
                    has_more = False
                    
            elif engine == "gutenberg_opds":
                time.sleep(1.0)
                books, next_ref = fetch_via_gutenberg_opds(lang, opds_next_url)
                if books:
                    opds_next_url = next_ref
                    if not next_ref:
                        has_more = False
                else:
                    # Switch to fallback engine if primary fails
                    print("  [INFO] Switching to fallback engine (Gutendex)...")
                    engine = "gutendex"
                    
            elif engine == "gutendex":
                time.sleep(1.0)
                books, next_ref = fetch_via_gutendex(lang, gutendex_page)
                if books:
                    gutendex_page = next_ref if next_ref else 1
                    if not next_ref:
                        has_more = False
                else:
                    has_more = False
                    
            if not books:
                break
                
            print(f"  Scanned {len(books)} books from catalog (Engine: {engine})")
            
            for book in books:
                if downloaded_count >= limit_per_lang:
                    break
                    
                book_id = book["id"]
                
                # Skip if already downloaded
                if book_id in existing_ids:
                    continue
                
                epub_url = book["epub_url"]
                author_name = book["author"]
                title = book["title"]
                
                # Generate safe and clean filename
                safe_author = clean_filename(author_name)
                safe_title = clean_filename(title)
                
                # Limit length to prevent filesystem path length errors
                if len(safe_title) > 80:
                    safe_title = safe_title[:77] + "..."
                if len(safe_author) > 50:
                    safe_author = safe_author[:47] + "..."
                    
                filename = f"{safe_author} - {safe_title} ({book_id}).epub"
                dest_path = os.path.join(lang_dir, filename)
                
                print(f"  📥 Downloading [{downloaded_count+1}/{limit_per_lang}]: '{author_name} - {title}'")
                print(f"     URL: {epub_url}")
                
                if progress_callback:
                    progress_callback(lang, downloaded_count, limit_per_lang, f"Downloading '{safe_author} - {safe_title}'")
                
                # Download book file
                time.sleep(1.0)
                success = download_book(epub_url, dest_path)
                
                if success:
                    print(f"     ✅ Saved: {filename}")
                    downloaded_count += 1
                    existing_ids.add(book_id)
                    if progress_callback:
                        progress_callback(lang, downloaded_count, limit_per_lang, f"Saved: {safe_author} - {safe_title}")
                else:
                    print(f"     ❌ Download failed")
                    if progress_callback:
                        progress_callback(lang, downloaded_count, limit_per_lang, f"Failed to download: {safe_title}")
                    
        print(f"  ✨ Completed processing {lang.upper()}. Successfully downloaded {downloaded_count} new books.\n")
        
    # Trigger scanner if requested and downloads were made
    if trigger_scan_path:
        try:
            with open(trigger_scan_path, 'w') as f:
                f.write(str(time.time()))
            print(f"🔔 System scanner triggered via trigger file: {trigger_scan_path}")
        except Exception as e:
            print(f"⚠️ Failed to write trigger file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Polite bulk public-domain eBook downloader utilizing Gutenberg OPDS, Gutendex APIs, and Standard Ebooks OPDS.")
    parser.add_argument(
        "--languages", 
        type=str, 
        default=",".join(DEFAULT_LANGUAGES),
        help="Comma-separated list of target language codes (default: all 12)."
    )
    parser.add_argument(
        "--count", 
        type=int, 
        default=10, 
        help="Number of new popular books to download per language (default: 10)."
    )
    parser.add_argument(
        "--outdir", 
        type=str, 
        default="/library/downloads", 
        help="Target library directory for saving files (default: /library/downloads)."
    )
    parser.add_argument(
        "--trigger-scan", 
        type=str, 
        default="/library/.trigger_scan", 
        help="Path to the scan trigger file (default: /library/.trigger_scan)."
    )
    parser.add_argument(
        "--source",
        type=str,
        default="gutenberg",
        choices=["gutenberg", "standardebooks"],
        help="Source catalog to download from (default: gutenberg)."
    )
    
    args = parser.parse_args()
    
    lang_list = [lang.strip().lower() for lang in args.languages.split(",") if lang.strip()]
    
    crawl_popular_books(lang_list, args.count, args.outdir, args.trigger_scan, args.source)

