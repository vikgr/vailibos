import os
import codecs

from random import randint

from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.db.models import Count, Min
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.vary import vary_on_headers
from django.urls import reverse, reverse_lazy
from django.utils.html import strip_tags
from django.db.models import Q
from django.http import HttpResponseForbidden

from book_tools.format import create_bookfile
import opds_catalog.zipf as zipfile
from opds_catalog import models
from opds_catalog.models import Book, Author, Series, bookshelf, Counter, Catalog, Genre, lang_menu
from opds_catalog import settings
from constance import config
from opds_catalog.opds_paginator import Paginator as OPDS_Paginator

from sopds_web_backend.settings import HALF_PAGES_LINKS

LANG_MAP = {
    'ru': ['русский', 'rus', 'ru', 'рус', 'russian'],
    'en': ['английский', 'eng', 'en', 'english'],
    'de': ['немецкий', 'ger', 'deu', 'de', 'german'],
    'el': ['греческий', 'ell', 'gre', 'el', 'greek'],
    'es': ['испанский', 'spa', 'es', 'spanish'],
    'fr': ['французский', 'fra', 'fre', 'fr', 'french'],
    'ar': ['арабский', 'ara', 'ar', 'arabic'],
    'hi': ['хинди', 'hin', 'hi', 'hindi'],
    'pt': ['португальский', 'por', 'pt', 'portuguese'],
    'zh': ['китайский', 'zho', 'chi', 'zh', 'chinese'],
    'bn': ['бенгальский', 'ben', 'bn', 'bengali'],
    'nl': ['нидерландский', 'nld', 'dut', 'nl', 'dutch'],
}

LANG_NAMES = {
    'en': {'name': _('English'), 'flag': 'gb'},
    'ru': {'name': _('Russian'), 'flag': 'ru'},
    'de': {'name': _('German'), 'flag': 'de'},
    'el': {'name': _('Greek'), 'flag': 'gr'},
    'es': {'name': _('Spanish'), 'flag': 'es'},
    'fr': {'name': _('French'), 'flag': 'fr'},
    'ar': {'name': _('Arabic'), 'flag': 'sa'},
    'hi': {'name': _('Hindi'), 'flag': 'in'},
    'pt': {'name': _('Portuguese'), 'flag': 'pt'},
    'zh': {'name': _('Chinese'), 'flag': 'cn'},
    'bn': {'name': _('Bengali'), 'flag': 'bd'},
    'nl': {'name': _('Dutch'), 'flag': 'nl'},
}


def get_annotation(mybook):
    full_path = os.path.join(config.SOPDS_ROOT_LIB, mybook.path)
    # Убираем из пути INPX и INP файл
    inp_path, zip_name = os.path.split(full_path)
    inpx_path, inp_name = os.path.split(inp_path)
    path, inpx_name = os.path.split(inpx_path)
    full_path = os.path.join(path,zip_name)
    fz = codecs.open(full_path, "rb")
    z = zipfile.ZipFile(fz, 'r', allowZip64=True)
    fo = z.open(mybook.filename)
    book_data = create_bookfile(fo, mybook.filename)
    annotation = book_data.description if book_data.description else ''
    annotation = annotation.strip(' \'\&\n-.#\\\`') if isinstance(annotation, str) else annotation.decode('utf8').strip(' \'\&\n-.#\\\`')
    return annotation


def sopds_login(function=None, redirect_field_name=REDIRECT_FIELD_NAME, url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=reverse_lazy(url),
        redirect_field_name=redirect_field_name
    ) 
    if function:
        return actual_decorator(function)
    return actual_decorator

def sopds_processor(request):
    args={}
    
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    theme_cookie = getattr(request, 'vailib_theme', None) or request.COOKIES.get('vailib_theme')
    
    if theme_cookie in ['eink', 'premium']:
        args['vailib_theme'] = theme_cookie
    else:
        # Detect e-ink devices in user agent
        eink_agents = (
            'kindle', 'kobo', 'nook', 'pocketbook', 'ereader', 'sonyreader', 
            'eink', 'e-ink', 'boox', 'tolino', 'bookeen', 'onyx', 'remarkable',
            'likebook', 'boyue', 'hanvon', 'dasung', 'inkpalm', 'supernote',
            'mobiscribe', 'cybook', 'bokeen', 'inkbook',
            'opera mini', 'symbian', 'blackberry', 'netfront', 'openwave'
        )
        if any(keyword in user_agent for keyword in eink_agents):
            args['vailib_theme'] = 'eink'
        else:
            args['vailib_theme'] = 'premium'
            
    args['app_title']=settings.TITLE
    args['sopds_auth']=config.SOPDS_AUTH
    args['sopds_version']=settings.VERSION
    args['alphabet'] = config.SOPDS_ALPHABET_MENU
    args['splititems'] = config.SOPDS_SPLITITEMS
    args['fb2tomobi'] = (config.SOPDS_FB2TOMOBI!="")
    args['fb2toepub'] = (config.SOPDS_FB2TOEPUB!="")
    args['nozip'] = settings.NOZIP_FORMATS
    args['cache_t']=0

    if config.SOPDS_ALPHABET_MENU:
        args['lang_menu'] = lang_menu
    
    if config.SOPDS_AUTH:
        user=request.user
        if user.is_authenticated:
            result=[]
            for row in bookshelf.objects.filter(user=user).order_by('-readtime')[:8]:
                book = Book.objects.get(id=row.book_id)
                p = {'id':row.id, 'readtime': row.readtime, 'book_id': row.book_id, 'title': book.title, 'authors':book.authors.values()}
                result.append(p)
            args['bookshelf']=result
        
    books_count = Counter.objects.get_counter(models.counter_allbooks)
    if books_count:
        random_id = randint(1,books_count)
        try:
            random_book = Book.objects.all()[random_id-1:random_id][0]
        except Book.DoesNotExist:
            random_book= None
    else:
        random_book= None
    # Get annotation if note done yet
    if random_book and random_book.annotation == 'NotYet':
        random_book.annotation = get_annotation(random_book)
        random_book.save()
    args['random_book'] = random_book
    stats = { d['name']:d['value'] for d in Counter.obj.all().values() }
    stats['lastscan_date']=Counter.objects.get_lastscan()
    args['stats'] = stats
  
    return args

# Create your views here.
@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def SearchBooksView(request):
    #Read searchtype, searchterms, searchterms0, page from form
    args = {}
    args.update(csrf(request))

    if request.GET:
        searchtype = request.GET.get('searchtype', 'm')
        searchterms = request.GET.get('searchterms', '')
        #searchterms0 = int(request.POST.get('searchterms0', ''))
        page_num = int(request.GET.get('page', '1'))
        page_num = page_num if page_num>0 else 1
        books = Book.objects.none()
        
        #if (len(searchterms)<3) and (searchtype in ('m', 'b', 'e')):
        #    args['errormsg'] = 'Too few symbols in search string !';
        #    return render_to_response('sopds_error.html', args)
        
        if searchtype == 'm':
            #books = Book.objects.extra(where=["upper(title) like %s"], params=["%%%s%%"%searchterms.upper()]).order_by('title','-docdate')
            books = Book.objects.filter(search_title__contains=searchterms.upper()).order_by('search_title','-docdate')
            args['vailib_breadcrumbs'] = [
                {'name': _('Books'), 'url': '/web/book/?lang=0'},
                {'name': _('Поиск по названию'), 'url': None},
                {'name': searchterms, 'url': '?searchtype=m&searchterms=%s' % searchterms}
            ]
            args['searchobject'] = 'title'
            
        elif searchtype == 'b':
            #books = Book.objects.extra(where=["upper(title) like %s"], params=["%s%%"%searchterms.upper()]).order_by('title','-docdate')
            books = Book.objects.filter(search_title__startswith=searchterms.upper()).order_by('search_title','-docdate')
            args['vailib_breadcrumbs'] = [
                {'name': _('Books'), 'url': '/web/book/?lang=0'},
                {'name': _('Поиск по названию'), 'url': None},
                {'name': searchterms, 'url': '?searchtype=b&searchterms=%s' % searchterms}
            ]
            args['searchobject'] = 'title'         
            
        elif searchtype == 'a':
            try:
                author_id = int(searchterms)
                author = Author.objects.get(id=author_id)
                #aname = "%s %s"%(author.last_name,author.first_name)
                aname = author.full_name
            except:
                author_id = 0
                aname = ""                  
            books = Book.objects.filter(authors=author_id).order_by('search_title','-docdate')  
            args['vailib_breadcrumbs'] = [
                {'name': _('Books'), 'url': '/web/book/?lang=0'},
                {'name': _('Поиск по автору'), 'url': '/web/author/?lang=0'},
                {'name': aname, 'url': '?searchtype=a&searchterms=%s' % searchterms}
            ]

            args['searchobject'] = 'author' 
            
        # Поиск книг по серии
        elif searchtype == 's':
            try:
                ser_id = int(searchterms)
                ser = Series.objects.get(id=ser_id).ser
            except:
                ser_id = 0
                ser = ""
            #books = Book.objects.filter(series=ser_id).order_by('search_title','-docdate')
            books = Book.objects.filter(series=ser_id).order_by('bseries__ser_no','search_title','-docdate')
            args['vailib_breadcrumbs'] = [
                {'name': _('Books'), 'url': '/web/book/?lang=0'},
                {'name': _('Поиск по серии'), 'url': '/web/series/?lang=0'},
                {'name': ser, 'url': '?searchtype=s&searchterms=%s' % searchterms}
            ]
            args['searchobject'] = 'series'
            
        # Поиск книг по жанру
        elif searchtype == 'g':
            try:
                genre_id = int(searchterms)
                section = Genre.objects.get(id=genre_id).section
                subsection = Genre.objects.get(id=genre_id).subsection
                args['vailib_breadcrumbs'] = [
                    {'name': _('Books'), 'url': '/web/book/?lang=0'},
                    {'name': _('Поиск по жанру'), 'url': '/web/genre/'},
                    {'name': section, 'url': None},
                    {'name': subsection, 'url': '?searchtype=g&searchterms=%s' % searchterms}
                ]
            except:
                genre_id = 0
                args['vailib_breadcrumbs'] = [
                    {'name': _('Books'), 'url': '/web/book/?lang=0'},
                    {'name': _('Поиск по жанру'), 'url': '/web/genre/'}
                ]
                
            books = Book.objects.filter(genres=genre_id).order_by('search_title','-docdate') 
            args['searchobject'] = 'genre'
                                   
        # Поиск книг на книжной полке            
        elif searchtype == 'u':
            if config.SOPDS_AUTH:
                books = Book.objects.filter(bookshelf__user=request.user).order_by('-bookshelf__readtime')
                args['vailib_breadcrumbs'] = [
                    {'name': _('Books'), 'url': '/web/book/?lang=0'},
                    {'name': _('Bookshelf'), 'url': '/web/search/books/?searchtype=u'},
                    {'name': request.user.username, 'url': None}
                ]
                #books = bookshelf.objects.filter(user=request.user).select_related('book')              
            else:
                books=Book.objects.filter(id=0)     
                args['vailib_breadcrumbs'] = [
                    {'name': _('Books'), 'url': '/web/book/?lang=0'},
                    {'name': _('Bookshelf'), 'url': '/web/search/books/?searchtype=u'}
                ]
            args['searchobject'] = 'title'
            args['isbookshelf'] = 1
                
        # Поиск дубликатов для книги            
        elif searchtype == 'd':
            #try:
            book_id = int(searchterms)
            mbook = Book.objects.get(id=book_id)
            books = Book.objects.filter(title=mbook.title, authors__in=mbook.authors.all()).exclude(id=book_id).distinct().order_by('-docdate')
            args['vailib_breadcrumbs'] = [
                {'name': _('Books'), 'url': '/web/book/?lang=0'},
                {'name': _('Doubles for book'), 'url': None},
                {'name': mbook.title, 'url': '?searchtype=d&searchterms=%s' % searchterms}
            ]
            args['searchobject'] = 'title'
            
        elif searchtype == 'l':
            target_langs = LANG_MAP.get(searchterms.lower(), [searchterms])
            from django.db.models import Q
            q_objects = Q()
            for l in target_langs:
                q_objects |= Q(lang__iexact=l)
            books = Book.objects.filter(q_objects).order_by('search_title', '-docdate')
            
            friendly_name = LANG_NAMES.get(searchterms.lower(), {}).get('name', searchterms.upper())
            args['vailib_breadcrumbs'] = [
                {'name': _('Books'), 'url': '/web/book/?lang=0'},
                {'name': _('Languages'), 'url': '/web/language/'},
                {'name': friendly_name, 'url': '?searchtype=l&searchterms=%s' % searchterms}
            ]
            args['searchobject'] = 'title'
            
        # Поиск книги по ID.
        elif searchtype == 'i':
            try:
                book_id = int(searchterms)
            except:
                book_id = 0
            books = Book.objects.filter(id=book_id) 
            
            if books.exists():
                mbook = books[0]
                # Find other formats for this book
                duplicates = Book.objects.filter(title=mbook.title, authors__in=mbook.authors.all()).distinct()
                args['all_formats'] = [{'id': b.id, 'format': b.format} for b in duplicates]
                args['has_epub'] = any(b.format.lower() == 'epub' for b in duplicates)
                
                message = request.GET.get('message')
                if message == 'converting':
                    args['system_message'] = {
                        'text': _('Manual conversion to EPUB triggered. The book will appear in the catalog shortly.'),
                        'type': 'success'
                    }

            args['vailib_breadcrumbs'] = [
                {'name': _('Books'), 'url': '/web/book/?lang=0'},
                {'name': books[0].title if books.exists() else _('Book'), 'url': '?searchtype=i&searchterms=%s' % searchterms}
            ]
            args['searchobject'] = 'title'
        
        # prefetch_related on sqlite on items >999 therow error "too many SQL variables"    
        #if len(books)>0:
        #    books = books.select_related('authors','genres','series')

        # Добавляем Left Join с таблицей BookShelfб чтобы вытащить дату прочтения книги из книжной полки
        #books = books.filter(Q(bookshelf__isnull=True)|Q(bookshelf__user=request.user))
        #books = books.prefetch_related('bookshelf_set')
        #print(books.query)

        
        # Фильтруем дубликаты и формируем выдачу затребованной страницы
        books_count = books.count()
        op = OPDS_Paginator(books_count, 0, page_num, config.SOPDS_MAXITEMS, HALF_PAGES_LINKS)
        items = []
        
        prev_title = ''
        prev_authors_set = set()
        
        # Начаинам анализ с последнего элемента на предидущей странице, чторбы он "вытянул" с этой страницы
        # свои дубликаты если они есть
        summary_DOUBLES_HIDE =  config.SOPDS_DOUBLES_HIDE and (searchtype != 'd')
        start = op.d1_first_pos if ((op.d1_first_pos==0) or (not summary_DOUBLES_HIDE)) else op.d1_first_pos-1
        finish = op.d1_last_pos
        
        for row in books[start:finish+1]:
            shortpath = row.path[row.path.rfind('/')+1:]
            # Get annotation if note done yet
            if row.annotation == 'NotYet':
                row.annotation = get_annotation(row)
                row.save()
            p = {'doubles':0, 'lang_code': row.lang_code, 'filename': row.filename, 'path': row.path, 'shortpath': shortpath, \
                  'registerdate': row.registerdate, 'id': row.id, 'annotation': strip_tags(row.annotation), \
                  'docdate': row.docdate, 'lang': row.lang, 'format': row.format, 'title': row.title, 'filesize': row.filesize,\
                  'authors': row.authors.values(), 'genres': row.genres.values(), 'series': row.series.values(),'ser_no': row.bseries_set.values('ser_no'),\
                  'readtime':row.bookshelf_set.filter(user=request.user).values('readtime') if config.SOPDS_AUTH else None
                 }
            if summary_DOUBLES_HIDE:
                title = p['title']
                authors_set = {a['id'] for a in p['authors']}         
                if title.upper()==prev_title.upper() and authors_set==prev_authors_set:
                    items[-1]['doubles']+=1
                else:
                    items.append(p)                   
                prev_title = title
                prev_authors_set = authors_set
            else:
                items.append(p)
                
        # "вытягиваем" дубликаты книг со следующей страницы и удаляем первый элемент который с предыдущей страницы и "вытягивал" дубликаты с текущей
        if summary_DOUBLES_HIDE:
            double_flag = True
            while ((finish+1)<books_count) and double_flag:
                finish += 1  
                if books[finish].title.upper()==prev_title.upper() and {a['id'] for a in books[finish].authors.values()}==prev_authors_set:
                    items[-1]['doubles']+=1
                else:
                    double_flag = False   
            
            if op.d1_first_pos!=0:     
                items.pop(0)                                   
              
        args.update(sopds_processor(request))
        args['paginator'] = op.get_data_dict()
        args['searchterms']=searchterms;
        args['searchtype']=searchtype;
        args['books']=items   
        args['current'] = 'search'
        args['cache_id']='%s:%s:%s'%(searchterms,searchtype,op.page_num)
        args['cache_t']=0
        
    return render(request,'sopds_books.html', args)

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def SearchSeriesView(request):
    #Read searchtype, searchterms, searchterms0, page from form
    args = {}
    args.update(csrf(request))

    if request.GET:
        searchtype = request.GET.get('searchtype', 'm')
        searchterms = request.GET.get('searchterms', '')
        #searchterms0 = int(request.POST.get('searchterms0', ''))
        page_num = int(request.GET.get('page', '1'))
        page_num = page_num if page_num>0 else 1
        
        if searchtype == 'm':
            series = Series.objects.filter(search_ser__contains=searchterms.upper())
        elif searchtype == 'b': 
            series = Series.objects.filter(search_ser__startswith=searchterms.upper())
        elif searchtype == 'e':
            series = Series.objects.filter(search_ser=searchterms.upper())      

        #if len(series)>0:
        #    series = series.order_by('ser')   
        series = series.annotate(count_book=Count('book')).distinct().order_by('search_ser') 
            
        # Создаем результирующее множество
        series_count = series.count()
        op = OPDS_Paginator(series_count, 0, page_num, config.SOPDS_MAXITEMS, HALF_PAGES_LINKS)        
        items = []
        for row in series[op.d1_first_pos:op.d1_last_pos+1]:
            #p = {'id':row.id, 'ser':row.ser, 'lang_code': row.lang_code, 'book_count': Book.objects.filter(series=row).count()}
            p = {'id':row.id, 'ser':row.ser, 'lang_code': row.lang_code, 'book_count': row.count_book}
            items.append(p)                     
              
        args.update(sopds_processor(request))
        args['paginator'] = op.get_data_dict()
        args['searchterms']=searchterms;
        args['searchtype']=searchtype;
        args['series']=items     
        args['searchobject'] = 'series'
        args['current'] = 'search'        
        args['vailib_breadcrumbs'] = [
            {'name': _('Series'), 'url': '/web/series/?lang=0'},
            {'name': _('Search'), 'url': None},
            {'name': searchterms, 'url': '?searchtype=%s&searchterms=%s' % (searchtype, searchterms)}
        ]
        args['cache_id']='%s:%s:%s'%(searchterms,searchtype,op.page_num)
        args['cache_t']=0

    return render(request,'sopds_series.html', args)

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def SearchAuthorsView(request):
    #Read searchtype, searchterms, searchterms0, page from form    
    args = {}
    args.update(csrf(request))

    if request.GET:
        searchtype = request.GET.get('searchtype', 'm')
        searchterms = request.GET.get('searchterms', '')
        #searchterms0 = int(request.POST.get('searchterms0', ''))
        page_num = int(request.GET.get('page', '1'))
        page_num = page_num if page_num>0 else 1
        
        if searchtype == 'm':
            authors = Author.objects.filter(search_full_name__contains=searchterms.upper()).order_by('search_full_name')   
        elif searchtype == 'b':
            authors = Author.objects.filter(search_full_name__startswith=searchterms.upper()).order_by('search_full_name')    
        elif searchtype == 'e': 
            authors = Author.objects.filter(search_full_name=searchterms.upper()).order_by('search_full_name')    
                        
        # Создаем результирующее множество
        authors_count = authors.count()
        op = OPDS_Paginator(authors_count, 0, page_num, config.SOPDS_MAXITEMS, HALF_PAGES_LINKS)        
        items = []
        
        for row in authors[op.d1_first_pos:op.d1_last_pos+1]:
            p = {'id':row.id, 'full_name':row.full_name, 'lang_code': row.lang_code, 'book_count': Book.objects.filter(authors=row).count()}
            items.append(p)                     
            
        args.update(sopds_processor(request))
        args['paginator'] = op.get_data_dict()              
        args['searchterms']=searchterms;
        args['searchtype']=searchtype;
        args['authors']=items     
        args['searchobject'] = 'author'
        args['current'] = 'search'       
        args['vailib_breadcrumbs'] = [
            {'name': _('Authors'), 'url': '/web/author/?lang=0'},
            {'name': _('Search'), 'url': None},
            {'name': searchterms, 'url': '?searchtype=%s&searchterms=%s' % (searchtype, searchterms)}
        ]
        args['cache_id']='%s:%s:%s'%(searchterms,searchtype,op.page_num)
        args['cache_t']=0
                                    
    return render(request,'sopds_authors.html', args)

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def CatalogsView(request):   
    args = {}

    if request.GET:
        cat_id = request.GET.get('cat', None)
        page_num = int(request.GET.get('page', '1'))   
    else:
        cat_id = None
        page_num = 1

    try:
        if cat_id is not None:
            cat = Catalog.objects.get(id=cat_id)
        else:
            cat = Catalog.objects.get(parent__id=cat_id)
    except Catalog.DoesNotExist:
        cat = None
    
    catalogs_list = Catalog.objects.filter(parent=cat).order_by("cat_name")
    catalogs_count = catalogs_list.count()
    # prefetch_related on sqlite on items >999 therow error "too many SQL variables"
    #books_list = Book.objects.filter(catalog=cat).prefetch_related('authors','genres','series').order_by("title")
    books_list = Book.objects.filter(catalog=cat).order_by("search_title")
    books_count = books_list.count()
    
    # Получаем результирующий список
    op = OPDS_Paginator(catalogs_count, books_count, page_num, config.SOPDS_MAXITEMS, HALF_PAGES_LINKS)
    items = []
    
    for row in catalogs_list[op.d1_first_pos:op.d1_last_pos+1]:
        p = {'is_catalog':1, 'title': row.cat_name,'id': row.id, 'cat_type':row.cat_type, 'parent_id':row.parent_id}       
        items.append(p)
          
    for row in books_list[op.d2_first_pos:op.d2_last_pos+1]:
        shortpath = row.path[row.path.rfind('/')+1:]
        p = {'is_catalog':0, 'lang_code': row.lang_code, 'filename': row.filename, 'path': row.path, 'shortpath': shortpath, \
              'registerdate': row.registerdate, 'id': row.id, 'annotation': strip_tags(row.annotation), \
              'docdate': row.docdate, 'lang': row.lang, 'format': row.format, 'title': row.title, 'filesize': row.filesize, \
              'authors':row.authors.values(), 'genres':row.genres.values(), 'series':row.series.values(), 'ser_no':row.bseries_set.values('ser_no'),\
              'readtime': row.bookshelf_set.filter(user=request.user).values('readtime') if config.SOPDS_AUTH else None
             }
        items.append(p)
                    
    args['paginator'] = op.get_data_dict()
    args['items']=items
    args['cat_id'] = cat_id
    args['current'] = 'catalog'     
    
    breadcrumbs_list = []
    if cat:
        while (cat.parent):
            breadcrumbs_list.insert(0, (cat.cat_name, cat.id))
            cat = cat.parent
        breadcrumbs_list.insert(0, (_('ROOT'), 0))  
    #breadcrumbs_list.insert(0, (_('Catalogs'),-1))    
    args['breadcrumbs_cat'] =  breadcrumbs_list  
    args['vailib_breadcrumbs'] =  [{'name': _('Catalogs'), 'url': '/web/catalog/'}]
    args['cache_id'] = '%s:%s:%s' % (args['current'],cat_id, op.page_num)
    args['cache_t'] = config.SOPDS_CACHE_TIME
      
    return render(request,'sopds_catalogs.html', args)  

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def BooksView(request):   
    args = {}

    if request.GET:
        lang_code = int(request.GET.get('lang', '0'))  
        chars = request.GET.get('chars', '')
    else:
        lang_code = 0
        chars = ''
        
    length = len(chars)+1
    if lang_code:
        sql="""select %(length)s as l, substring(search_title,1,%(length)s) as id, count(*) as cnt 
               from opds_catalog_book 
               where lang_code=%(lang_code)s and search_title like '%(chars)s%%%%'
               group by substring(search_title,1,%(length)s) 
               order by id"""%{'length':length, 'lang_code':lang_code, 'chars':chars}
    else:
        sql="""select %(length)s as l, substring(search_title,1,%(length)s) as id, count(*) as cnt 
               from opds_catalog_book 
               where search_title like '%(chars)s%%%%'
               group by substring(search_title,1,%(length)s) 
               order by id"""%{'length':length,'chars':chars}
      
    items = Book.objects.raw(sql)
          
    args['items']=items
    args['current'] = 'book'      
    args['lang_code'] = lang_code   
    args['vailib_breadcrumbs'] =  [
        {'name': _('Books'), 'url': '/web/book/?lang=0'},
        {'name': _('Select'), 'url': None},
        {'name': lang_menu[lang_code], 'url': '?lang=%s' % lang_code},
        {'name': chars, 'url': '?lang=%s&chars=%s' % (lang_code, chars)}
    ]
    args.update(sopds_processor(request))
    return render(request,'sopds_selectbook.html', args)      

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def AuthorsView(request):   
    args = {}

    if request.GET:
        lang_code = int(request.GET.get('lang', '0'))  
        chars = request.GET.get('chars', '')
    else:
        lang_code = 0
        chars = ''
        
    length = len(chars)+1
    if lang_code:
        sql="""select %(length)s as l, substring(search_full_name,1,%(length)s) as id, count(*) as cnt 
               from opds_catalog_author 
               where lang_code=%(lang_code)s and search_full_name like '%(chars)s%%%%'
               group by substring(search_full_name,1,%(length)s) 
               order by id"""%{'length':length, 'lang_code':lang_code, 'chars':chars}
    else:
        sql="""select %(length)s as l, substring(search_full_name,1,%(length)s) as id, count(*) as cnt 
               from opds_catalog_author 
               where search_full_name like '%(chars)s%%%%'
               group by substring(search_full_name,1,%(length)s) 
               order by id"""%{'length':length,'chars':chars}
      
    items = Author.objects.raw(sql)
          
    args['items']=items
    args['current'] = 'author'      
    args['lang_code'] = lang_code   
    args['vailib_breadcrumbs'] =  [
        {'name': _('Authors'), 'url': '/web/author/?lang=0'},
        {'name': _('Select'), 'url': None},
        {'name': lang_menu[lang_code], 'url': '?lang=%s' % lang_code},
        {'name': chars, 'url': '?lang=%s&chars=%s' % (lang_code, chars)}
    ]
    args.update(sopds_processor(request))
    return render(request,'sopds_selectauthor.html', args)

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def SeriesView(request):   
    args = {}

    if request.GET:
        lang_code = int(request.GET.get('lang', '0'))  
        chars = request.GET.get('chars', '')
    else:
        lang_code = 0
        chars = ''
        
    length = len(chars)+1
    if lang_code:
        sql="""select %(length)s as l, substring(search_ser,1,%(length)s) as id, count(*) as cnt 
               from opds_catalog_series 
               where lang_code=%(lang_code)s and search_ser like '%(chars)s%%%%'
               group by substring(search_ser,1,%(length)s)
               order by id"""%{'length':length, 'lang_code':lang_code, 'chars':chars}
    else:
        sql="""select %(length)s as l, substring(search_ser,1,%(length)s) as id, count(*) as cnt 
               from opds_catalog_series 
               where search_ser like '%(chars)s%%%%'
               group by substring(search_ser,1,%(length)s) 
               order by id"""%{'length':length,'chars':chars}
      
    items = Series.objects.raw(sql)
          
    args['items']=items
    args['current'] = 'series'      
    args['lang_code'] = lang_code   
    args['vailib_breadcrumbs'] =  [
        {'name': _('Series'), 'url': '/web/series/?lang=0'},
        {'name': _('Select'), 'url': None},
        {'name': lang_menu[lang_code], 'url': '?lang=%s' % lang_code},
        {'name': chars, 'url': '?lang=%s&chars=%s' % (lang_code, chars)}
    ]
    args.update(sopds_processor(request))
    return render(request,'sopds_selectseries.html', args)

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def GenresView(request):   
    args = {}

    if request.GET:
        section_id = int(request.GET.get('section', '0'))  
    else:
        section_id = 0
        
    if section_id==0:
        items = Genre.objects.values('section').annotate(section_id=Min('id'), num_book=Count('book')).filter(num_book__gt=0).order_by('section')
        args['vailib_breadcrumbs'] =  [
            {'name': _('Genres'), 'url': '/web/genre/'},
            {'name': _('Select'), 'url': None}
        ]
    else:
        section = Genre.objects.get(id=section_id).section
        items = Genre.objects.filter(section=section).annotate(num_book=Count('book')).filter(num_book__gt=0).values().order_by('subsection')   
        args['vailib_breadcrumbs'] =  [
            {'name': _('Genres'), 'url': '/web/genre/'},
            {'name': _('Select'), 'url': '/web/genre/'},
            {'name': section, 'url': '?section=%s' % section_id}
        ]
          
    args['items']=items
    args['current'] = 'genre'  
    args['parent_id'] = section_id
    args.update(sopds_processor(request))
    return render(request,'sopds_selectgenres.html', args)

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def BSDelView(request):
    if request.GET:
        book = request.GET.get('book', None)
    else:
        book = None
       
    book = int(book)
       
    bookshelf.objects.filter(user=request.user, book=book).delete()
    
    return redirect("%s?searchtype=u"%reverse("web:searchbooks"))

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def BSClearView(request):
    bookshelf.objects.filter(user=request.user).delete()
    return redirect("%s?searchtype=u" % reverse("web:searchbooks"))
@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def hello(request):
    args = {}
    args['vailib_breadcrumbs'] = [{'name': _('HOME'), 'url': '/web/'}]
    if request.user.is_authenticated:
        args['recent_books'] = Book.objects.all().order_by('-registerdate', '-id')[:12]
    else:
        args['recent_books'] = []
    args.update(sopds_processor(request))
    return render(request, 'sopds_hello.html', args)

def LoginView(request):
    args = {}
    args['vailib_breadcrumbs'] = [{'name': _('Login'), 'url': None}]
    args.update(csrf(request))
    args.update(sopds_processor(request))
    
    next_url = request.POST.get('next') or request.GET.get('next') or reverse("web:main")
    args['next_url'] = next_url

    try:
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        return render(request, 'sopds_login.html', args)

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect(next_url)
        else:
            args['system_message'] = {'text': _('This account is not active!'), 'type': 'alert'}
            return render(request, 'sopds_login.html', args)
    else:
        args['system_message'] = {'text': _('User does not exist or the password is incorrect!'), 'type': 'alert'}
        return render(request, 'sopds_login.html', args)

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def LogoutView(request):
    logout(request)
    args = {}
    args['vailib_breadcrumbs'] = [{'name': _('Logout'), 'url': None}]
    return redirect(reverse('web:main'))

def handler403(request,args):
    response = render(request, 'sopds_login.html', args)
    response.status_code = 403
    return response

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def ReaderView(request, book_id):
    args = {}
    try:
        book = Book.objects.get(id=book_id)
        args['book'] = book
        # Detect format
        fmt = book.format.lower()
        args['format'] = fmt
        
        # Breadcrumbs
        args['vailib_breadcrumbs'] = [
            {'name': _('Books'), 'url': '/web/book/?lang=0'},
            {'name': book.title, 'url': '/web/search/books/?searchtype=i&searchterms=%s' % book_id},
            {'name': _('Reading'), 'url': None}
        ]
    except Book.DoesNotExist:
        args['errormsg'] = _('Book not found!')
        return render(request, 'sopds_error.html', args)

    args.update(sopds_processor(request))
    return render(request, 'sopds_reader.html', args)

from django.http import JsonResponse
import threading

# Global populate task status
populate_lock = threading.Lock()
populate_status = {
    "status": "idle",       # "idle", "running", "completed", "error"
    "current_lang": "",
    "downloaded": 0,
    "total": 0,
    "message": "Ready to populate library.",
    "logs": []
}

def update_populate_progress(lang, current, total, message):
    global populate_status
    with populate_lock:
        populate_status["current_lang"] = lang
        populate_status["downloaded"] = current
        populate_status["total"] = total
        populate_status["message"] = message
        log_line = f"[{lang.upper()}] {current}/{total}: {message}"
        if not populate_status["logs"] or populate_status["logs"][-1] != log_line:
            populate_status["logs"].append(log_line)
            if len(populate_status["logs"]) > 15:
                populate_status["logs"].pop(0)

def run_populate_thread(languages, limit_per_lang, outdir, trigger_scan_path, source="gutenberg"):
    global populate_status
    with populate_lock:
        populate_status["status"] = "running"
        populate_status["message"] = f"Initializing downloader for {source}..."
        populate_status["logs"] = [f"Initializing downloader for {source}..."]
        
    try:
        import download_popular_books
        download_popular_books.crawl_popular_books(
            languages=languages,
            limit_per_lang=limit_per_lang,
            outdir=outdir,
            trigger_scan_path=trigger_scan_path,
            source=source,
            progress_callback=update_populate_progress
        )
        with populate_lock:
            populate_status["status"] = "completed"
            populate_status["message"] = "Library populated successfully!"
            populate_status["logs"].append("Completed successfully.")
    except Exception as e:
        with populate_lock:
            populate_status["status"] = "error"
            populate_status["message"] = f"Fatal error: {e}"
            populate_status["logs"].append(f"Fatal error: {e}")

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def PopulateView(request):
    # Only allow superusers
    if not request.user.is_superuser:
        return HttpResponseForbidden("<h1>403 Forbidden</h1><p>Only administrators can access this feature.</p>")
        
    global populate_status
    args = {}
    args.update(csrf(request))
    args['current'] = 'populate'
    args['languages'] = [
        {"code": "en", "name": "English", "flag": "gb"},
        {"code": "ru", "name": "Russian", "flag": "ru"},
        {"code": "de", "name": "German", "flag": "de"},
        {"code": "el", "name": "Greek", "flag": "gr"},
        {"code": "es", "name": "Spanish", "flag": "es"},
        {"code": "fr", "name": "French", "flag": "fr"},
        {"code": "ar", "name": "Arabic", "flag": "sa"},
        {"code": "hi", "name": "Hindi", "flag": "in"},
        {"code": "pt", "name": "Portuguese", "flag": "pt"},
        {"code": "zh", "name": "Chinese", "flag": "cn"},
        {"code": "bn", "name": "Bengali", "flag": "bd"},
        {"code": "nl", "name": "Dutch", "flag": "nl"},
    ]
    
    if request.method == "POST":
        # Check if already running
        is_running = False
        with populate_lock:
            if populate_status["status"] == "running":
                is_running = True
                
        if not is_running:
            selected_langs = request.POST.getlist("langs")
            if not selected_langs:
                selected_langs = [lang["code"] for lang in args['languages']]
                
            try:
                count = int(request.POST.get("count", "10"))
                # Cap between 1 and 100 for server protection
                count = max(1, min(100, count))
            except ValueError:
                count = 10
                
            source = request.POST.get("source", "gutenberg")
            if source not in ["gutenberg", "standardebooks"]:
                source = "gutenberg"
                
            # Default storage and scan trigger files
            outdir = os.path.join(config.SOPDS_ROOT_LIB, "downloads")
            trigger_scan_path = os.path.join(config.SOPDS_ROOT_LIB, ".trigger_scan")
            
            # Start background thread
            t = threading.Thread(
                target=run_populate_thread,
                args=(selected_langs, count, outdir, trigger_scan_path, source)
            )
            t.daemon = True
            t.start()
            
        return redirect("web:populate")

        
    with populate_lock:
        args['populate_status'] = populate_status.copy()

    if 'upload_flash' in request.session:
        args['upload_flash'] = request.session.pop('upload_flash')
        
    args['vailib_breadcrumbs'] = [
        {'name': _('HOME'), 'url': '/web/'},
        {'name': _('Populate & Upload'), 'url': None}
    ]
    args.update(sopds_processor(request))
    return render(request, 'sopds_populate.html', args)

@sopds_login(url='web:login')
def PopulateStatusView(request):
    if not request.user.is_superuser:
        return JsonResponse({"error": "Forbidden"}, status=403)
        
    global populate_status
    with populate_lock:
        status_copy = populate_status.copy()
        
    return JsonResponse(status_copy)

@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def UploadView(request):
    if not request.user.is_superuser:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return JsonResponse({"success": False, "error": "Only administrators can upload books."}, status=403)
        return HttpResponseForbidden("<h1>403 Forbidden</h1><p>Only administrators can access this feature.</p>")

    if request.method != "POST":
        return redirect("web:populate")

    files = request.FILES.getlist("books")
    if not files:
        single = request.FILES.get("book")
        if single:
            files = [single]

    if not files:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return JsonResponse({"success": False, "error": "No files provided for upload."}, status=400)
        request.session['upload_flash'] = {"type": "error", "message": "No files selected for upload."}
        return redirect("web:populate")

    subfolder = request.POST.get("subfolder", "uploads").strip()
    subfolder = os.path.normpath(subfolder).lstrip('/\\').replace('..', '')
    if not subfolder:
        subfolder = "uploads"

    extract_zips = request.POST.get("extract_zips", "true").lower() in ("true", "1", "yes", "on")
    trigger_scan = request.POST.get("trigger_scan", "true").lower() in ("true", "1", "yes", "on")

    dest_dir = os.path.join(config.SOPDS_ROOT_LIB, subfolder)
    try:
        os.makedirs(dest_dir, exist_ok=True)
        os.chmod(dest_dir, 0o777)
    except Exception:
        pass

    ALLOWED_EXTS = {
        '.epub', '.fb2', '.pdf', '.mobi', '.djvu', '.cbr', '.cbz',
        '.azw', '.azw3', '.txt', '.doc', '.docx', '.rtf', '.chm', '.zip'
    }
    BOOK_EXTS = {
        '.epub', '.fb2', '.pdf', '.mobi', '.djvu', '.cbr', '.cbz',
        '.azw', '.azw3', '.txt', '.doc', '.docx', '.rtf', '.chm'
    }

    import zipfile as py_zipfile
    saved_files = []
    extracted_files = []
    errors = []

    for f in files:
        orig_name = f.name
        base_name = os.path.basename(orig_name)
        _, ext = os.path.splitext(base_name)
        ext = ext.lower()

        is_fb2_zip = base_name.lower().endswith('.fb2.zip')
        if ext not in ALLOWED_EXTS and not is_fb2_zip:
            errors.append(f"Skipped {base_name}: unsupported file type ({ext}).")
            continue

        if ext == '.zip' and extract_zips and not is_fb2_zip:
            try:
                with py_zipfile.ZipFile(f, 'r') as zf:
                    extracted_from_this_zip = 0
                    for member in zf.infolist():
                        if member.is_dir():
                            continue
                        member_name = member.filename
                        try:
                            if not (member.flag_bits & 0x800):
                                member_name = member_name.encode('cp437').decode('cp866')
                        except Exception:
                            pass

                        m_base = os.path.basename(member_name)
                        _, m_ext = os.path.splitext(m_base)
                        m_is_fb2_zip = m_base.lower().endswith('.fb2.zip')
                        if m_ext.lower() not in BOOK_EXTS and not m_is_fb2_zip:
                            continue

                        norm_member = os.path.normpath(member_name).lstrip('/\\')
                        if norm_member.startswith('..'):
                            continue

                        target_path = os.path.join(dest_dir, norm_member)
                        # Security: Prevent Zip Slip path traversal
                        if not os.path.abspath(target_path).startswith(os.path.abspath(dest_dir)):
                            continue

                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with zf.open(member) as src, open(target_path, 'wb') as dst:
                            while True:
                                chunk = src.read(65536)
                                if not chunk:
                                    break
                                dst.write(chunk)
                        try:
                            os.chmod(target_path, 0o666)
                        except OSError:
                            pass
                        extracted_files.append(m_base)
                        extracted_from_this_zip += 1

                    if extracted_from_this_zip == 0:
                        # If no recognized book files were inside, save the zip archive as a whole
                        f.seek(0)
                        target_path = os.path.join(dest_dir, base_name)
                        with open(target_path, 'wb') as dst:
                            for chunk in f.chunks():
                                dst.write(chunk)
                        try:
                            os.chmod(target_path, 0o666)
                        except OSError:
                            pass
                        saved_files.append(base_name)
            except Exception as e:
                errors.append(f"Failed extracting {base_name}: {str(e)}")
        else:
            target_path = os.path.join(dest_dir, base_name)
            if os.path.exists(target_path):
                name_root, name_ext = os.path.splitext(base_name)
                c = 1
                while os.path.exists(target_path):
                    target_path = os.path.join(dest_dir, f"{name_root}_{c}{name_ext}")
                    c += 1
            try:
                with open(target_path, 'wb') as dst:
                    for chunk in f.chunks():
                        dst.write(chunk)
                try:
                    os.chmod(target_path, 0o666)
                except OSError:
                    pass
                saved_files.append(os.path.basename(target_path))
            except Exception as e:
                errors.append(f"Failed saving {base_name}: {str(e)}")

    total_count = len(saved_files) + len(extracted_files)
    scan_triggered = False
    if total_count > 0 and trigger_scan:
        trigger_path = os.path.join(config.SOPDS_ROOT_LIB, ".trigger_scan")
        try:
            with open(trigger_path, 'a'):
                os.utime(trigger_path, None)
            scan_triggered = True
        except Exception:
            pass

    msg_parts = []
    if saved_files:
        msg_parts.append(f"Saved {len(saved_files)} file(s)")
    if extracted_files:
        msg_parts.append(f"Extracted {len(extracted_files)} book(s) from ZIP archive")
    if not msg_parts and errors:
        summary_msg = "; ".join(errors)
        success = False
    else:
        summary_msg = ", ".join(msg_parts) + "."
        if scan_triggered:
            summary_msg += " Library scanner triggered."
        success = True

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return JsonResponse({
            "success": success,
            "message": summary_msg,
            "saved_files": saved_files,
            "extracted_files": extracted_files,
            "errors": errors,
            "total_count": total_count,
            "scan_triggered": scan_triggered
        })

    request.session['upload_flash'] = {
        "type": "success" if success else "error",
        "message": summary_msg,
        "errors": errors
    }
    return redirect("web:populate")


@vary_on_headers("HTTP_ACCEPT_LANGUAGE")
@sopds_login(url='web:login')
def LanguagesView(request):
    args = {}
    from django.db.models import Count
    raw_langs = Book.objects.values('lang').annotate(book_count=Count('id')).filter(book_count__gt=0)
    
    # Reverse lang map to helper dict for fast resolution
    reverse_map = {}
    for std_code, aliases in LANG_MAP.items():
        for alias in aliases:
            reverse_map[alias] = std_code
            
    aggregated = {}
    for row in raw_langs:
        raw_val = row['lang'].lower().strip()
        if not raw_val:
            continue
        std_code = reverse_map.get(raw_val, raw_val)
        
        if std_code not in aggregated:
            aggregated[std_code] = 0
        aggregated[std_code] += row['book_count']
        
    languages = []
    for std_code, count in aggregated.items():
        info = LANG_NAMES.get(std_code, {'name': std_code.upper(), 'flag': None})
        languages.append({
            'code': std_code,
            'name': info['name'],
            'flag': info['flag'],
            'book_count': count
        })
    languages.sort(key=lambda x: x['book_count'], reverse=True)
    
        
    args['languages'] = languages
    args['current'] = 'language'
    args['vailib_breadcrumbs'] = [
        {'name': _('Books'), 'url': '/web/book/?lang=0'},
        {'name': _('Languages'), 'url': None}
    ]
    args.update(sopds_processor(request))
    return render(request, 'sopds_languages.html', args)


@sopds_login(url='web:login')
def ConvertManualView(request, book_id):
    import threading
    import subprocess
    
    try:
        book_id = int(book_id)
        book = Book.objects.get(id=book_id)
    except (ValueError, Book.DoesNotExist):
        raise Http404
        
    if book.format.lower() not in ['pdf', 'djvu']:
        return redirect('/web/search/books/?searchtype=i&searchterms=%s' % book_id)
        
    # Paths setup
    in_path = os.path.join(config.SOPDS_ROOT_LIB, book.path, book.filename)
    out_name = os.path.splitext(book.filename)[0] + ".epub"
    out_path = os.path.join(config.SOPDS_ROOT_LIB, book.path, out_name)
    trigger_path = os.path.join(config.SOPDS_ROOT_LIB, ".trigger_scan")
    
    # Run conversion in a background thread to prevent HTTP timeouts
    def run_conversion():
        try:
            # calibre's ebook-convert
            subprocess.run(["ebook-convert", in_path, out_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # touch trigger scan
            with open(trigger_path, 'a'):
                os.utime(trigger_path, None)
        except Exception:
            pass

    t = threading.Thread(target=run_conversion)
    t.daemon = True
    t.start()
    
    # Redirect back to the book's details page with message
    return redirect('/web/search/books/?searchtype=i&searchterms=%s&message=converting' % book_id)


def update_container_timezone(new_tz):
    settings_path = '/sopds/sopds/settings.py'
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            import re
            pattern = r"TIME_ZONE\s*=\s*['\"][^'\"]+['\"]"
            if re.search(pattern, content):
                content = re.sub(pattern, f"TIME_ZONE = '{new_tz}'", content)
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        except Exception:
            pass
    return False


def SetupWriteTestView(request):
    if request.method != 'POST':
        return HttpResponseForbidden("<h1>403 Forbidden</h1>")
        
    path = request.POST.get('path', '/library')
    try:
        os.makedirs(path, exist_ok=True)
        test_file = os.path.join(path, '.vailib_write_test')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('Vailib write test')
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        os.remove(test_file)
        return JsonResponse({"status": "success", "message": "Write permission verified successfully!"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Permission Error: {str(e)}"})


def SetupWizardView(request):
    from django.contrib.auth.models import User
    # If a superuser already exists, redirect to catalog main
    if User.objects.filter(is_superuser=True).exists():
        return redirect('/web/')
        
    from django.conf import settings
    from constance import config
    import pytz
    import threading
    
    args = {}
    
    if request.method == 'POST':
        admin_username = request.POST.get('admin_username')
        admin_password = request.POST.get('admin_password')
        library_path = request.POST.get('library_path', '/library')
        language = request.POST.get('language', 'en')
        timezone = request.POST.get('timezone', 'Europe/Madrid')
        extensions = request.POST.getlist('extensions')
        
        # Online feeds configuration
        enable_gutenberg = request.POST.get('enable_gutenberg') == 'on'
        gutenberg_langs = request.POST.getlist('gutenberg_langs')
        enable_standardebooks = request.POST.get('enable_standardebooks') == 'on'

        # Telegram Bot configuration
        telegram_token = request.POST.get('telegram_token')
        telegram_chat_id = request.POST.get('telegram_chat_id', '')
        enable_telegram_bot = request.POST.get('enable_telegram_bot') == 'on'
        
        try:
            # 1. Create Django Administrator
            User.objects.create_superuser(username=admin_username, email='', password=admin_password)
            
            # 2. Save Constance Configs
            lang_mapping = {
                'en': 'en-us', 'zh': 'zh-hans', 'ru': 'ru', 'el': 'el',
                'de': 'de', 'es': 'es', 'fr': 'fr', 'ar': 'ar',
                'hi': 'hi', 'pt': 'pt', 'bn': 'bn', 'nl': 'nl'
            }
            config.SOPDS_LANGUAGE = lang_mapping.get(language, 'en-US')
            config.SOPDS_ROOT_LIB = library_path
            if extensions:
                config.SOPDS_BOOK_EXTENSIONS = ' '.join(extensions)

            # Save Telegram configs in DB Constance backend
            if telegram_token:
                config.SOPDS_TELEBOT_API_TOKEN = telegram_token
            config.SOPDS_TELEBOT_CHAT_ID = telegram_chat_id
            config.SOPDS_TELEBOT_ENABLED = enable_telegram_bot
                
            # 3. Patch System Timezone
            update_container_timezone(timezone)
            
            # 4. Programmatic Session Login (Guaranteed login, bypasses authenticate lookup)
            from django.contrib.auth import login
            user = User.objects.get(username=admin_username)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
                
            # 5. Populate and scan
            if (enable_gutenberg and gutenberg_langs) or enable_standardebooks:
                outdir = os.path.join(library_path, "downloads")
                trigger_scan_path = os.path.join(library_path, ".trigger_scan")
                os.makedirs(outdir, exist_ok=True)
                
                global populate_status
                is_running = False
                with populate_lock:
                    if populate_status["status"] == "running":
                        is_running = True
                        
                if not is_running:
                    source = "standardebooks" if (enable_standardebooks and not enable_gutenberg) else "gutenberg"
                    langs = ["en"] if source == "standardebooks" else gutenberg_langs
                    t = threading.Thread(
                        target=run_populate_thread,
                        args=(langs, 10, outdir, trigger_scan_path, source)
                    )
                    t.daemon = True
                    t.start()
            else:
                trigger_scan_path = os.path.join(library_path, ".trigger_scan")
                try:
                    os.makedirs(library_path, exist_ok=True)
                    with open(trigger_scan_path, 'a'):
                        os.utime(trigger_scan_path, None)
                except Exception:
                    pass

                    
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
            
    args['timezones'] = pytz.common_timezones
    args['languages'] = [
        {"code": "en", "name": "English", "flag": "gb"},
        {"code": "ru", "name": "Russian", "flag": "ru"},
        {"code": "de", "name": "German", "flag": "de"},
        {"code": "el", "name": "Greek", "flag": "gr"},
        {"code": "es", "name": "Spanish", "flag": "es"},
        {"code": "fr", "name": "French", "flag": "fr"},
        {"code": "ar", "name": "Arabic", "flag": "sa"},
        {"code": "hi", "name": "Hindi", "flag": "in"},
        {"code": "pt", "name": "Portuguese", "flag": "pt"},
        {"code": "zh", "name": "Chinese", "flag": "cn"},
        {"code": "bn", "name": "Bengali", "flag": "bd"},
        {"code": "nl", "name": "Dutch", "flag": "nl"},
    ]
    args.update(sopds_processor(request))
    return render(request, 'sopds_setup.html', args)


@sopds_login(url='web:login')
def SettingsView(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("<h1>403 Forbidden</h1>")
        
    from django.conf import settings
    from constance import config
    from collections import OrderedDict
    import pytz
    
    args = {}
    
    # 5-step wizard groupings
    steps_schema = OrderedDict([
        ('system', {
            'title': _('System & Language'),
            'icon': 'fi-widget',
            'fields': ['SOPDS_LANGUAGE', 'SOPDS_CACHE_TIME']
        }),
        ('storage', {
            'title': _('Library & Storage'),
            'icon': 'fi-folder',
            'fields': ['SOPDS_ROOT_LIB', 'SOPDS_BOOK_EXTENSIONS', 'SOPDS_SPLITITEMS', 'SOPDS_MAXITEMS', 'SOPDS_TITLE_AS_FILENAME', 'SOPDS_NOCOVER_PATH', 'SOPDS_DELETE_LOGICAL']
        }),
        ('integrations', {
            'title': _('Integrations'),
            'icon': 'fi-comment',
            'fields': ['SOPDS_TELEBOT_API_TOKEN', 'SOPDS_TELEBOT_AUTH', 'SOPDS_TELEBOT_MAXITEMS']
        }),
        ('scanner', {
            'title': _('Scanner & Schedule'),
            'icon': 'fi-clock',
            'fields': ['SOPDS_SCAN_START_DIRECTLY', 'SOPDS_FB2SAX', 'SOPDS_ZIPSCAN', 'SOPDS_ZIPCODEPAGE', 'SOPDS_INPX_ENABLE', 'SOPDS_INPX_SKIP_UNCHANGED', 'SOPDS_INPX_TEST_ZIP', 'SOPDS_INPX_TEST_FILES', 'SOPDS_SCAN_SHED_MIN', 'SOPDS_SCAN_SHED_HOUR', 'SOPDS_SCAN_SHED_DAY', 'SOPDS_SCAN_SHED_DOW']
        }),
        ('logs', {
            'title': _('Logs & Diagnostics'),
            'icon': 'fi-page',
            'fields': ['SOPDS_SERVER_LOG', 'SOPDS_SCANNER_LOG', 'SOPDS_TELEBOT_LOG', 'SOPDS_SERVER_PID', 'SOPDS_SCANNER_PID', 'SOPDS_TELEBOT_PID', 'SOPDS_FB2TOEPUB', 'SOPDS_FB2TOMOBI', 'SOPDS_TEMP_DIR']
        })
    ])
    
    # Handle Form Submission (Step-by-step or full POST)
    if request.method == 'POST':
        step_name = request.POST.get('step_name')
        if step_name in steps_schema:
            fields_to_update = steps_schema[step_name]['fields']
            for field in fields_to_update:
                default_val = settings.CONSTANCE_CONFIG[field][0]
                if isinstance(default_val, bool):
                    val = (field in request.POST)
                else:
                    val = request.POST.get(field, default_val)
                    if isinstance(default_val, int):
                        try:
                            val = int(val)
                        except ValueError:
                            val = default_val
                setattr(config, field, val)
                
            # Timezone handling if system step is posted
            if step_name == 'system':
                new_tz = request.POST.get('timezone')
                if new_tz and new_tz in pytz.common_timezones:
                    update_container_timezone(new_tz)
                    
            if request.is_ajax():
                return JsonResponse({"status": "success", "message": _("Settings saved successfully.")})
            else:
                args['system_message'] = {
                    'text': _('Settings saved successfully.'),
                    'type': 'success'
                }
        else:
            if request.is_ajax():
                return JsonResponse({"status": "error", "message": _("Invalid step configuration.")})
                
    # Get current configurations grouped by wizard step
    config_data = OrderedDict()
    for step_id, step_info in steps_schema.items():
        step_fields = []
        for field in step_info['fields']:
            current_val = getattr(config, field)
            default_val, help_text = settings.CONSTANCE_CONFIG[field][:2]
            
            field_type = 'str'
            choices = None
            if isinstance(default_val, bool):
                field_type = 'bool'
            elif isinstance(default_val, int):
                field_type = 'int'
                
            if len(settings.CONSTANCE_CONFIG[field]) > 2:
                field_name = settings.CONSTANCE_CONFIG[field][2]
                add_field = settings.CONSTANCE_ADDITIONAL_FIELDS.get(field_name)
                if add_field and len(add_field) > 1 and 'choices' in add_field[1]:
                    field_type = 'choice'
                    choices = add_field[1]['choices']
                    
            step_fields.append({
                'name': field,
                'value': current_val,
                'help_text': help_text,
                'type': field_type,
                'choices': choices
            })
            
        config_data[step_id] = {
            'title': step_info['title'],
            'icon': step_info['icon'],
            'fields': step_fields
        }
        
    args['config_data'] = config_data
    args['timezones'] = pytz.common_timezones
    args['current_timezone'] = getattr(settings, 'TIME_ZONE', 'Europe/Madrid')
    args['current'] = 'settings'
    args['vailib_breadcrumbs'] = [
        {'name': _('Books'), 'url': '/web/book/?lang=0'},
        {'name': _('Settings'), 'url': None}
    ]
    args.update(sopds_processor(request))
    return render(request, 'sopds_settings.html', args)


@sopds_login(url='web:login')
def SettingsLogView(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("<h1>403 Forbidden</h1>")
        
    from constance import config
    log_type = request.GET.get('type', 'server')
    
    log_file_path = None
    if log_type == 'server':
        log_file_path = config.SOPDS_SERVER_LOG
    elif log_type == 'scanner':
        log_file_path = config.SOPDS_SCANNER_LOG
    elif log_type == 'telebot':
        log_file_path = config.SOPDS_TELEBOT_LOG
        
    if not log_file_path or not os.path.exists(log_file_path):
        return JsonResponse({"status": "error", "message": f"Log file not found at: {log_file_path}"})
        
    try:
        from collections import deque
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = list(deque(f, 200))
        return JsonResponse({"status": "success", "lines": lines})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})



