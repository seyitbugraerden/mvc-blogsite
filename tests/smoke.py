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
        fields.update(Title='Test detail', Slug='smoke-post', Published='false')
        assert request('/admin/posts/new', fields)[0] == 302
        assert request('/blog/smoke-post')[0] == 404
        fields['Published'] = 'true'
        assert request('/admin/posts/smoke-post/edit', fields)[0] == 302
        assert request('/blog/smoke-post')[0] == 200
        assert '/blog/smoke-post' in request('/blog')[1]
        assert request('/admin/posts/new', fields)[0] == 200, 'Duplicate slug accepted'
        fields['Slug'] = 'INVALID SLUG'
        assert request('/admin/posts/new', fields)[0] == 200
        fields['Slug'] = 'renamed-post'
        assert request('/admin/posts/smoke-post/edit', fields)[0] == 302
        assert request('/blog/renamed-post')[0] == 200
        assert request('/blog/smoke-post')[0] == 404
        assert '/blog/renamed-post' in request('/about')[1], 'Link not updated'
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
        print('PASS: 13 seeded pages, assets, authentication, CSRF, editing, unique/invalid slugs, draft visibility, slug/link updates, disabled forms, restart persistence, optional authentication and anonymous editing.')
    finally:
        process.terminate()
        process.wait(timeout=10)
        log.close()
