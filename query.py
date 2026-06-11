import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sopds.settings')
django.setup()

from opds_catalog.models import Book

pdf_book = Book.objects.filter(format='pdf').first()
djvu_book = Book.objects.filter(format='djvu').first()

print("PDF BOOK:", pdf_book.id if pdf_book else "NONE")
print("DJVU BOOK:", djvu_book.id if djvu_book else "NONE")
