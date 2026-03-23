/**
 * vailib_ui.js — Vailib UI Logic
 * Phase 5 refactor: extracted from inline <script> blocks in templates.
 *
 * Requires: jQuery (loaded before this script via sopds_main.html)
 */

// --- Cover Placeholder Helper ---
// Detects SOPDS 'no cover' image (83×100) and shows the themed placeholder instead.
function checkEinkCover(img) {
    function process() {
        if (img.naturalWidth === 83 && img.naturalHeight === 100) {
            img.style.display = 'none';
            var next = img.nextElementSibling;
            if (next && (next.classList.contains('eink-placeholder') || next.classList.contains('modern-placeholder'))) {
                next.style.display = 'flex';
            }
        }
    }
    if (img.complete) {
        process();
    } else {
        img.onload = process;
    }
}

// --- Online Reader ---
// Opens the book in omnireader.ru. 'downloadUrlTemplate' contains '999999' as placeholder for bid.
function readOnline(bid, downloadUrlTemplate) {
    if (!downloadUrlTemplate && typeof VAILIB_DOWNLOAD_URL_TMPL !== 'undefined') {
        downloadUrlTemplate = VAILIB_DOWNLOAD_URL_TMPL;
    }
    if (!downloadUrlTemplate) return;
    var hostUrl = window.location.protocol + '//' + window.location.host;
    var downloadUrl = downloadUrlTemplate.replace('999999', bid);
    var url = 'https://omnireader.ru/#/reader?url=' + hostUrl + downloadUrl;
    window.open(url, '_blank');
}

// --- Bookshelf Delete Modal ---
function del_bsbook(b_id, b_t) {
    var deleteUrl  = (typeof VAILIB_DELETE_URL !== 'undefined')      ? VAILIB_DELETE_URL      : '/web/bsdel/';
    var coverTmpl  = (typeof VAILIB_COVER_URL_TMPL !== 'undefined')  ? VAILIB_COVER_URL_TMPL  : '';
    var coverUrl   = coverTmpl.replace('999999', b_id);
    $('#DeleteBook_btnYes').attr('href', deleteUrl + '?book=' + b_id);
    $('#DeleteBook_image').attr('src', coverUrl);
    $('#DeleteBook_title').text(b_t);
    $('#DeleteBookModal').foundation('open');
}

// --- Universal Breadcrumb Fix ---
// Parses stringified Python dicts that SOPDS occasionally returns as crumb text.
function fixVailibCrumbs() {
    $('.crumb').each(function () {
        var text = $(this).text().trim();
        if (text.indexOf('{') === 0 && text.indexOf('}') !== -1) {
            try {
                var mName = text.match(/['"](?:name|NAME)['"]\s*:\s*['"](.*?)['"]/);
                var mUrl  = text.match(/['"](?:url|URL)['"]\s*:\s*['"](.*?)['"]/);
                if (mName) {
                    var name = mName[1];
                    var url  = (mUrl && mUrl[1] !== 'None' && mUrl[1] !== 'null') ? mUrl[1] : null;
                    if (url) {
                        $(this).html('<a href="' + url + '" style="color:var(--accent); text-decoration:none; font-weight:500;">' + name + '</a>');
                    } else {
                        $(this).html('<span style="font-weight:400;">' + name + '</span>');
                    }
                }
            } catch (e) {
                console.warn('Crumb fix failed', e);
            }
        }
    });
}

// --- Foundation & App Init ---
$(document).ready(function () {
    $(document).foundation();
    if (typeof SetSearch === 'function') SetSearch();

    // Re-check any images that loaded before this script ran
    $('img').each(function () {
        if (this.complete) checkEinkCover(this);
    });

    // Theme switcher button (premium → e-ink)
    var btn = document.getElementById('vailib-theme-switcher');
    if (btn) {
        btn.onclick = function (e) {
            if (e && e.preventDefault) e.preventDefault();
            document.cookie = 'vailib_theme=eink; path=/';
            location.reload();
        };
    }

    // Event delegation for .read-online-btn (data-attribute pattern)
    $(document).on('click', '.read-online-btn', function (e) {
        e.preventDefault();
        var bid  = $(this).data('book-id');
        var tmpl = $(this).data('download-url-tmpl') || (typeof VAILIB_DOWNLOAD_URL_TMPL !== 'undefined' ? VAILIB_DOWNLOAD_URL_TMPL : null);
        if (bid && tmpl) readOnline(bid, tmpl);
    });

    // Event delegation for .del-bsbook-btn (data-attribute pattern)
    $(document).on('click', '.del-bsbook-btn', function (e) {
        e.preventDefault();
        var bid   = $(this).data('book-id');
        var title = $(this).data('book-title');
        del_bsbook(bid, title);
    });

    // Breadcrumb fix — run immediately and retry for late renders
    fixVailibCrumbs();
    setTimeout(fixVailibCrumbs, 500);
    setTimeout(fixVailibCrumbs, 1500);
});

// --- Foundation Abide Validator ---
if (typeof Foundation !== 'undefined' && Foundation.Abide) {
    Foundation.Abide.defaults.validators['check_search'] = function ($el, required, parent) {
        var box = document.getElementById('main_searchbox');
        if (box && box.value.length < 3) return false;
        return true;
    };
}
