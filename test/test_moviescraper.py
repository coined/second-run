#!/usr/local/bin/python3

import unittest
from moviescraper import moviescraper

class TestMovieSite(unittest.TestCase):
    def test_init(self):
        test_theater = moviescraper.MovieSite(
            site_url = 'http://testtheatersite.com/', theater_name = 'Test Theater',
            list_selector = 'div.test_1 > div#test_2 > span',
            text_search = 'Test: (.+)$'
        )
        self.assertEqual(test_theater.site_url, 'http://testtheatersite.com/')
        self.assertEqual(test_theater.theater_name, 'Test Theater')
        self.assertEqual(test_theater.list_selector, 'div.test_1 > div#test_2 > span')
        self.assertEqual(test_theater.text_search, 'Test: (.+)$')

if __name__ == '__main__':
    unittest.main()
