"""Isolated HTTP integration test; run after dotnet build. No third-party modules."""
import html
import http.cookiejar
import os
from pathlib import Path
import re
import secrets
import socket
import sqlite3
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
BASE = f'http://127.0.0.1:{port}'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def request(path, data=None):
    encoded = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        response = opener.open(BASE + path, encoded, timeout=5)
    except urllib.error.HTTPError as error:
        response = error
    return response.status, response.read().decode(), response.headers

def token(page):
    match = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', page)
    assert match, 'CSRF token missing'
    return html.unescape(match[1])

with tempfile.TemporaryDirectory(prefix='voku-smoke-') as directory:
    database = str(Path(directory) / 'test.db')
    password = secrets.token_urlsafe(24)
    env = dict(os.environ, ASPNETCORE_ENVIRONMENT='Development', ASPNETCORE_URLS=BASE,
               Admin__RequireAuthentication='true', Admin__Password=password, ConnectionStrings__Default=f'Data Source={database}')
    log = open(Path(directory) / 'server.log', 'w+')
    def start():
        proc = subprocess.Popen(['dotnet', str(ROOT / 'Voku.Web/bin/Debug/net10.0/Voku.Web.dll')], cwd=ROOT / 'Voku.Web', env=env, stdout=log, stderr=log)
        for _ in range(300):
            if proc.poll() is not None:
                log.seek(0)
                raise AssertionError(log.read())
            try:
                if request('/')[0] == 200:
                    return proc
            except OSError:
                pass
            time.sleep(.1)
        proc.terminate()
        raise AssertionError('Server did not start')
    process = start()
    try:
        for path in ['/', '/about', '/skills', '/blog', '/contact', '/coming-soon', '/site-offline', '/typography', '/error', '/blog/heyecanli-bir-yolculuk', '/blog/full-review-of-my-house', '/blog/true-story-about-tim-finch', '/blog/paris-the-first-day', '/css/style.css', '/images/img-1.jpg']:
            # Binary image response is checked separately.
            if path.endswith('.jpg'):
                assert opener.open(BASE + path).status == 200
            else:
                assert request(path)[0] == 200, path
        for path in ['/', '/blog']:
            listing = request(path)[1]
            assert listing.count('data-post-slug=') == 4
            assert '27 comments' not in listing and '289 day of year' not in listing
        assert '2 Comments' not in request('/blog/heyecanli-bir-yolculuk')[1]
        assert request('/missing')[0] == 404
        assert request('/admin')[0] == 302
        assert request('/admin/pages/about/edit')[0] == 302
        assert request('/admin/login', {'Username': 'admin', 'Password': password})[0] == 400
        csrf = token(request('/admin/login')[1])
        assert 'hatalı' in html.unescape(request('/admin/login', {'Username': 'admin', 'Password': 'incorrect', '__RequestVerificationToken': csrf})[1])
        assert request('/admin/login', {'Username': 'admin', 'Password': password, '__RequestVerificationToken': csrf})[0] == 302
        assert request('/admin')[0] == 200
        csrf = token(request('/admin/pages/about/edit')[1])
        body = '<main><h1>Updated content</h1><a href="/blog/smoke-post">Test</a></main>'
        fields = {'Title': 'Updated about', 'Slug': 'about', 'BodyHtml': body, 'Description': '', 'Published': 'true', '__RequestVerificationToken': csrf}
        assert request('/admin/pages/about/edit', fields)[0] == 302
        assert 'Updated content' in request('/about')[1]
        fields['Slug'] = 'changed-fixed-route'
        result = request('/admin/pages/about/edit', fields)
        assert result[0] == 200, (result[0], result[1][:12000])
        assert request('/changed-fixed-route')[0] == 404
        fields.update(Title='Test detail', Slug='smoke-post', Published='false', CoverImageUrl='/images/img-7.jpg', Category='Test category', Author='Test writer', PublishedAtUtc='2040-01-02T12:00')
        assert request('/admin/posts/new', fields)[0] == 302
        assert request('/blog/smoke-post')[0] == 404
        for path in ['/', '/blog']:
            assert 'data-post-slug="smoke-post"' not in request(path)[1]
        fields['Published'] = 'true'
        assert request('/admin/posts/smoke-post/edit', fields)[0] == 302
        assert request('/blog/smoke-post')[0] == 200
        for path in ['/', '/blog']:
            listing = request(path)[1]
            assert 'data-post-slug="smoke-post"' in listing
            assert 'Test detail' in listing and 'Test writer' in listing
        detail = request('/blog/smoke-post')[1]
        assert '<h1>Test detail</h1>' in detail and '/images/img-7.jpg' in detail
        assert 'Test category' in detail and '02.01.2040' in detail
        filtered = request('/blog?category=Test%20category')[1]
        assert filtered.count('data-post-slug=') == 1
        assert 'data-post-slug="smoke-post"' in filtered
        assert request('/blog?category=unknown')[1].count('data-post-slug=') == 0
        assert request('/admin/posts/new', fields)[0] == 200, 'Duplicate slug accepted'
        fields['CoverImageUrl'] = 'javascript:alert(1)'
        assert request('/admin/posts/smoke-post/edit', fields)[0] == 200
        fields['CoverImageUrl'] = '/images/img-4.jpg'
        fields['Slug'] = 'INVALID SLUG'
        assert request('/admin/posts/new', fields)[0] == 200
        fields['Slug'] = 'renamed-post'
        assert request('/admin/posts/smoke-post/edit', fields)[0] == 302
        assert request('/blog/renamed-post')[0] == 200
        assert request('/blog/smoke-post')[0] == 404
        for path in ['/', '/blog']:
            listing = request(path)[1]
            assert 'data-post-slug="renamed-post"' in listing
            assert 'data-post-slug="smoke-post"' not in listing
            assert '/images/img-4.jpg' in listing
        assert '/blog/renamed-post'  in request('/about')[1], 'Link not updated'
        assert request('/contact', {'name': 'Nobody'})[0] == 405
        assert request('/php/submit.php', {'email': 'nobody@example.com'})[0] != 200
        assert request('/admin/logout', {'__RequestVerificationToken': csrf})[0] == 302
        assert request('/admin')[0] == 302
        process.terminate(); process.wait(timeout=10)
        process = start()
        assert 'Updated content' in request('/about')[1], 'Persistence failed'
        with sqlite3.connect(database) as db:
            assert db.execute('SELECT count(*) FROM Pages').fetchone()[0] == 14
            assert db.execute('SELECT PasswordHash FROM AdminUsers').fetchone()[0] != password
        # Additional records exercise ordering, filtered pagination and unpublishing.
        csrf = token(request('/admin/login')[1])
        assert request('/admin/login', {'Username':'admin', 'Password':password, '__RequestVerificationToken':csrf})[0] == 302
        fields['__RequestVerificationToken'] = token(request('/admin/posts/new')[1])
        for index in range(8):
            fields.update(Slug=f'pagination-{index}', Title=f'Pagination {index}', Category='Pagination', Published='true')
            assert request('/admin/posts/new', fields)[0] == 302
        first = request('/blog?category=Pagination')[1]
        second = request('/blog?category=Pagination&page=2')[1]
        assert first.count('data-post-slug=') == 6
        assert second.count('data-post-slug=') == 2
        assert 'category=Pagination' in first and 'rel="next"' in first
        assert 'rel="prev"' in second
        assert request('/')[1].count('data-post-slug=') == 6
        assert 'data-post-slug="pagination-7"' in request('/')[1]
        fields.update(Slug='pagination-7', Published='false')
        assert request('/admin/posts/pagination-7/edit', fields)[0] == 302
        assert 'data-post-slug="pagination-7"' not in request('/')[1]
        assert request('/blog/pagination-7')[0] == 404
        for index in range(7):
            fields.update(Slug=f'pagination-{index}', Published='false')
            assert request(f'/admin/posts/pagination-{index}/edit', fields)[0] == 302
        empty = request('/blog?category=Pagination')[1]
        assert empty.count('data-post-slug=') == 0
        assert 'Henüz' in html.unescape(empty)
        process.terminate(); process.wait(timeout=10)
        opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        env['Admin__RequireAuthentication'] = 'false'
        env.pop('Admin__Password')
        env['ConnectionStrings__Default'] = f'Data Source={directory}/open-admin.db'
        process = start()
        assert request('/admin')[0] == 200, 'Anonymous admin blocked'
        assert request('/admin/login')[0] == 302, 'Login should redirect to admin'
        csrf = token(request('/admin/pages/about/edit')[1])
        fields.update(Slug='about', Title='Anonymous edit', Published='true', __RequestVerificationToken=csrf)
        assert request('/admin/pages/about/edit', fields)[0] == 302
        assert 'Updated content' in request('/about')[1]
        assert request('/admin/pages/about/edit', {'Title': 'No token'})[0] == 400
        # Upgrade a pre-metadata database, preserving authored article HTML.
        process.terminate(); process.wait(timeout=10)
        legacy_path = str(Path(directory) / 'legacy.db')
        legacy_body = '<div id="content"><section class="post-content"><div class="tabs-link">OLD META</div><p>Preserved legacy article</p><div class="comments">OLD COMMENTS</div></section></div>'
        legacy_listing = '<header>Legacy header</header><section class="post-content"><article>LEGACY STATIC CARD</article></section><footer>Legacy footer</footer>'
        with sqlite3.connect(legacy_path) as db:
            db.executescript("""
                CREATE TABLE AdminUsers (Id INTEGER PRIMARY KEY AUTOINCREMENT, Username TEXT NOT NULL, PasswordHash TEXT NOT NULL);
                CREATE UNIQUE INDEX IX_AdminUsers_Username ON AdminUsers(Username);
                CREATE TABLE Pages (Id INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT NOT NULL, Slug TEXT NOT NULL,
                    IsDetail INTEGER NOT NULL, BodyHtml TEXT NOT NULL, Description TEXT NOT NULL, Published INTEGER NOT NULL, UpdatedUtc TEXT NOT NULL);
                CREATE UNIQUE INDEX IX_Pages_IsDetail_Slug ON Pages(IsDetail, Slug);
                CREATE TABLE __EFMigrationsHistory (MigrationId TEXT NOT NULL PRIMARY KEY, ProductVersion TEXT NOT NULL);
                INSERT INTO __EFMigrationsHistory VALUES ('20260923215013_InitialCreate','10.0.12');
            """)
            for title, slug, detail, body in [('Home','home',0,legacy_listing), ('Blog','blog',0,legacy_listing), ('Legacy title','legacy-post',1,legacy_body)]:
                db.execute('INSERT INTO Pages(Title,Slug,IsDetail,BodyHtml,Description,Published,UpdatedUtc) VALUES(?,?,?,?,?,?,?)',
                           (title,slug,detail,body,'',1,'2025-06-01 12:00:00'))
        env['ConnectionStrings__Default'] = f'Data Source={legacy_path}'
        process = start()
        for path in ['/', '/blog']:
            listing = request(path)[1]
            assert 'LEGACY STATIC CARD' not in listing
            assert 'data-post-slug="legacy-post"' in listing
            assert 'Legacy header' in listing and 'Legacy footer' in listing
        detail = request('/blog/legacy-post')[1]
        assert '<h1>Legacy title</h1>' in detail and 'Preserved legacy article' in detail
        assert 'OLD META' not in detail and 'OLD COMMENTS' not in detail
        with sqlite3.connect(legacy_path) as db:
            row = db.execute("SELECT BodyHtml, PublishedAtUtc FROM Pages WHERE Slug='legacy-post'").fetchone()
            assert row == (legacy_body, '2025-06-01 12:00:00'), row
        csrf = token(request('/admin/posts/legacy-post/edit')[1])
        fields.update(Slug='legacy-post', Published='false', __RequestVerificationToken=csrf)
        assert request('/admin/posts/legacy-post/edit', fields)[0] == 302
        assert request('/')[1].count('data-post-slug=') == 0
        assert 'Henüz' in html.unescape(request('/')[1])
        print('PASS: 13 seeded pages, assets, authentication, CSRF, editing, unique/invalid slugs, draft visibility, slug/link updates, disabled forms, restart persistence, optional authentication, dynamic cards, metadata, filtering and pagination.')
    finally:
        process.terminate()
        process.wait(timeout=10)
        log.close()
