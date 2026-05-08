"""
Vailib custom template tags and filters.
Phase 2: Title cleaning — strips file extensions and underscores from raw filenames.
Phase 3: Format color/class utilities for placeholder covers.
"""
import re
from django import template

register = template.Library()

# --- Phase 2: Title Cleaning ---

_EXTENSIONS = re.compile(
    r'\.(djvu|djv|pdf|epub|fb2|mobi|azw3?|cbz|cbr|zip|rar)$',
    re.IGNORECASE
)
_BRACKETED_SUFFIX = re.compile(r'\s*[\(\[].{1,60}[\)\]]\s*$')
_UNDERSCORES = re.compile(r'_+')


@register.filter(name='clean_title')
def clean_title(value):
    """
    Cleans a raw filename-based book title for display.
    Steps:
      1. Strip file extension
      2. Remove trailing bracketed author/year (Konysheva_NM) or [2020]
      3. Replace underscores with spaces
      4. Strip leading/trailing whitespace
    Returns the cleaned string, or the original if it appears to already be clean
    (i.e., contains spaces and no extension).
    """
    if not value:
        return value
    title = str(value)
    # If title has spaces and no file extension → already clean metadata
    if ' ' in title and not _EXTENSIONS.search(title):
        return title
    # 1. Strip extension
    title = _EXTENSIONS.sub('', title)
    # 2. Remove trailing bracketed content (e.g. "(Konysheva_NM)", "[2020]")
    title = _BRACKETED_SUFFIX.sub('', title)
    # 3. Replace underscores with spaces
    title = _UNDERSCORES.sub(' ', title)
    # 4. Strip
    return title.strip()


# --- Phase 3: Format Color/Class Mapping ---

FORMAT_COLORS = {
    'djvu': {'bg': 'linear-gradient(135deg, #0d1b3e 0%, #1a2f6e 100%)', 'accent': '#4dabf7', 'icon': '📘', 'badge_class': 'badge-djvu'},
    'djv':  {'bg': 'linear-gradient(135deg, #0d1b3e 0%, #1a2f6e 100%)', 'accent': '#4dabf7', 'icon': '📘', 'badge_class': 'badge-djvu'},
    'pdf':  {'bg': 'linear-gradient(135deg, #3e1a00 0%, #6e2f00 100%)', 'accent': '#ffa94d', 'icon': '📋', 'badge_class': 'badge-pdf'},
    'epub': {'bg': 'linear-gradient(135deg, #0d3e1a 0%, #1a6e2f 100%)', 'accent': '#69db7c', 'icon': '📗', 'badge_class': 'badge-epub'},
    'fb2':  {'bg': 'linear-gradient(135deg, #2a0d3e 0%, #4e1a6e 100%)', 'accent': '#cc5de8', 'icon': '📙', 'badge_class': 'badge-fb2'},
    'mobi': {'bg': 'linear-gradient(135deg, #3e300d 0%, #6e521a 100%)', 'accent': '#ffd43b', 'icon': '📔', 'badge_class': 'badge-mobi'},
}

_FORMAT_DEFAULT = {'bg': 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)', 'accent': '#adb5bd', 'icon': '📄', 'badge_class': 'badge-other'}


@register.filter(name='format_bg')
def format_bg(fmt):
    """Returns the CSS gradient background for a given file format string."""
    return FORMAT_COLORS.get(str(fmt).lower(), _FORMAT_DEFAULT)['bg']


@register.filter(name='format_accent')
def format_accent(fmt):
    """Returns the accent colour hex for a given file format."""
    return FORMAT_COLORS.get(str(fmt).lower(), _FORMAT_DEFAULT)['accent']


@register.filter(name='format_icon')
def format_icon(fmt):
    """Returns an emoji icon for the given file format."""
    return FORMAT_COLORS.get(str(fmt).lower(), _FORMAT_DEFAULT)['icon']


@register.filter(name='format_badge_class')
def format_badge_class(fmt):
    """Returns a CSS class name for styling the format badge."""
    return FORMAT_COLORS.get(str(fmt).lower(), _FORMAT_DEFAULT)['badge_class']
