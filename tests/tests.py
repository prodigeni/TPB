import sys
import unittest
import urllib
import itertools

from bs4 import BeautifulSoup

from cases import RemoteTestCase
from tpb.tpb import Search, Recent, Top
from tpb.utils import URL


class ConstantsTestCase(RemoteTestCase):
    pass


class PathSegmentsTestCase(RemoteTestCase):
    def setUp(self):
        self.segments = ['alpha', 'beta', 'gamma']
        self.defaults = ['0', '1', '2']
        self.url = URL('', '/', self.segments, self.defaults)

    def test_attributes(self):
        other_segments = ['one', 'two', 'three']
        other_url = URL('', '/', other_segments, self.defaults)
        for segment, other_segment in zip(self.segments, other_segments):
            self.assertTrue(hasattr(self.url, segment))
            self.assertFalse(hasattr(other_url, segment))
            self.assertTrue(hasattr(other_url, other_segment))
            self.assertFalse(hasattr(self.url, other_segment))

    def test_propierties(self):
        self.assertEqual(str(self.url), '/0/1/2')
        self.assertEqual(self.url.alpha, '0')
        self.url.alpha = '9'
        self.url.beta = '8'
        self.url.gamma = '7'
        self.assertEqual(str(self.url), '/9/8/7')
    


class ParsingTestCase(RemoteTestCase):
    def setUp(self):
        self.torrents = Search(self.url, 'breaking bad')

    def test_items(self):
        self.assertEqual(len(list(self.torrents.items())), 30)

    def test_torrent_rows(self):
        request = urllib.urlopen(str(self.torrents.url))
        content = request.read()
        page = BeautifulSoup(content)
        rows = self.torrents._get_torrent_rows(page)
        self.assertEqual(len(rows), 30)

    def test_torrent_build(self):
        pass


class PaginationTestCase(RemoteTestCase):
    def setUp(self):
        self.torrents = Search(self.url, 'breaking bad')

    def test_page_items(self):
        self.assertEqual(len(list(self.torrents.items())), 30)

    def test_multipage_items(self):
        self.torrents.multipage()
        items = itertools.islice(self.torrents.items(), 100)
        self.assertEqual(len(list(items)), 100)
        self.assertEqual(self.torrents.page(), 3)


class SearchTestCase(RemoteTestCase):
    def setUp(self):
        self.torrents = Search(self.url, 'breaking bad')

    def test_url(self):
        self.assertEqual(str(self.torrents.url),
                self.url + '/search/breaking%20bad/0/7/0')
        self.torrents.query('something').page(1).next().previous()
        self.torrents.order(9).category(100)
        self.assertEqual(self.torrents.query(), 'something')
        self.assertEqual(self.torrents.page(), 1)
        self.assertEqual(self.torrents.order(), 9)
        self.assertEqual(self.torrents.category(), 100)
        self.assertEqual(str(self.torrents.url),
                self.url + '/search/something/1/9/100')


class RecentTestCase(RemoteTestCase):
    def setUp(self):
        self.torrents = Recent(self.url)

    def test_url(self):
        self.assertEqual(str(self.torrents.url),
                self.url + '/recent/0')
        self.torrents.page(1).next().previous()
        self.assertEqual(str(self.torrents.url),
                self.url + '/recent/1')


class TopTestCase(RemoteTestCase):
    def setUp(self):
        self.torrents = Top(self.url)

    def test_url(self):
        self.assertEqual(str(self.torrents.url),
                self.url + '/top/0')
        self.torrents.category(100)
        self.assertEqual(str(self.torrents.url),
                self.url + '/top/100')



if __name__ == '__main__':
    if '--local' in sys.argv:
        sys.argv.remove('--local')
        RemoteTestCase._is_remote_available = False
    unittest.main()
