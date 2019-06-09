import re
from bs4 import BeautifulSoup, Comment
import logging
from scrapy.conf import settings
from models.models import Person
from .utils import convert_date, compare_url_existing_parameters


class PageSelector:
    def __init__(self, SUBJECT):
        self.SUBJECT = SUBJECT
        self.url_regex = re.compile(r'/\w+(\.(\w+\.?)+)?\d*')
        self.friend_urL_regex = re.compile(r'/\w+(\.(\w+\.?)+)?\d*\?')
        self.date_regex = re.compile(r'\d\d?\s\w+\s\d{4}$')
        self.year_regex = re.compile(r'\d{4}$')
        self.siblings = ['Frate', 'Soră', 'Mamă', 'Tată', "Fiică", "Fiu"]

    def __get_soup(self, response):
        return BeautifulSoup(response.text, 'html.parser')

    def _re_url_filter(self, href, current_person, regex):
        return href and regex.search(href) and \
               ('profile.php' in href or 'php' not in href) and \
               self.SUBJECT.identifier not in href and \
               current_person.identifier not in href

    def _find_sibling_url(self, trace, find_trace, i):
        if i == 0:
            return
        current_trace = trace.parent
        result = find_trace(current_trace)

        if result:
            return result
        return self._find_sibling_url(current_trace, find_trace, i - 1)

    def select_hrefs_and_next_url(self, response, current_person):
        def _find_trace(trace):
            return trace.find('img', src=lambda x: x and x not in settings['NOT_FACES_LIST'])

        soup = self.__get_soup(response)
        friends_urls = soup.find_all(href=lambda href: self._re_url_filter(href, current_person, self.friend_urL_regex))

        next_url = None
        next_text = soup.find(string='Vezi mai mulţi prieteni')  # pune tot explicit

        if next_text:
            next_url = next_text.find_parent('a')
            if next_url:
                next_url = next_url.get('href')

        if len(friends_urls) < 24 and next_url:
            logging.debug(f"{self.select_hrefs_and_next_url.__name__} this page should contain 24 urls. "
                          f"urls matched: {friends_urls}")

        friends_urls = [friend_url for friend_url in friends_urls
                        if self._find_sibling_url(friend_url, _find_trace, 3)]

        return friends_urls, next_url

        # method to extract url from the actual facebook
    def _select_picture_url(self, soup, person):
        urls = []
        # AICI
        for img in soup.find_all('img', alt=lambda x: x and person.name.lower() == x.lower()):
            url = img.find_parent('a')
            if url is not None:
                urls.append(url)

        if not urls or len(urls) > 1:
            logging.debug(f"{self._select_picture_url.__name__} one single url should match for the picture "
                          f"urls matched: {urls}")
            return None

        return urls[0].get('href')

    def select_person_info_and_picture_url(self, response, person):
        soup = self.__get_soup(response)
        url = self._select_picture_url(soup, person)
        if url is None:
            return None, None

        self._select_sex_birthday(soup, person)
        siblings = self._select_siblings(soup, person)

        return url, siblings

    def select_profile_image(self, response):
        soup = self.__get_soup(response)

        def picture_match(a):
            href = a.get('href')
            if href:
                return a.find('img') and compare_url_existing_parameters(a.get('href'), response.url)
                # or without 'facebook'
            return False

        profile_comments = soup.find_all(string=lambda x: isinstance(x, Comment))

        for comment in profile_comments:
            cur_soup = BeautifulSoup(comment.string, 'html.parser')
            rez = cur_soup.find_all(picture_match)
            for el in rez:
                for attr, val in el.attrs.items():
                    if 'scontent' in val:
                        return val

    def _select_sex_birthday(self, soup, person):
        def _trace_date(x):
            return x.find(string=lambda y: y and self.year_regex.match(y))

        dates = soup.find_all(string=lambda x: x and self.date_regex.match(x))
        if not dates:
            traces = soup.find_all(string="Anul naşterii")
            dates = []
            for trace in traces:
                r_trace = self._find_sibling_url(trace, _trace_date, 4)
                if r_trace:
                    dates.append(r_trace)
        if len(dates) > 1:
            logging.debug(f"{self._select_sex_birthday.__name__} one single date should match for the birthday "
                          f"dates matched: {dates}")

        male = soup.find_all(string='Masculin')
        female = soup.find_all(string='Feminin')

        if len(male) > 1 or len(female) > 1 or\
                (len(male) > 0 and len(female) > 0):
            logging.debug(f"{self._select_sex_birthday.__name__} one single gender should match for sex "
                          f"genders: {male} {female}")

        sex = None
        if len(male) != 0:
            sex = True
        elif len(female) != 0:
            sex = False

        if sex is not None:
            person.sex = sex

        if dates:
            try:
                date = convert_date(str(dates[0]))
                person.birthday = date
            except Exception as exc:
                logging.debug(f"{self._select_picture_url.__name__} date format is not expected: {dates} {repr(exc)}")

    def _select_siblings(self, soup, person):
        def _find_trace(t):
            return t.find(href=lambda href: self._re_url_filter(href, person, self.url_regex))

        rez = []
        for sibling in self.siblings:
            traces = soup.find_all(string=sibling)
            for trace in traces:
                result = self._find_sibling_url(trace, _find_trace, 3)
                if result:
                    pers, created = Person.objects.get_or_create(identifier=result.get('href'), name=result.get_text())
                    if created:
                        rez.append((sibling, pers))
                else:
                    logging.debug(f"{self._select_siblings.__name__} found the word {sibling} but couldn't find its url")

        return rez

    def select_profile_image_mobile(self, response):
        soup = self.__get_soup(response)
        imgs = soup.find_all('img', src=lambda x: x and 'scontent' in x)

        if len(imgs) != 1:
            logging.debug(f"{self.select_profile_image_mobile.__name__} only one image should match")
        else:
            return imgs[0].get('src')
