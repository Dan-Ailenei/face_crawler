import logging
import requests
from collections import deque
from django.utils.safestring import mark_safe

from utils import print_dict

BASE_URL = 'https://www.facebook.com'


def login_facebook(subject, credentials, session):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml',
        # 'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
    }
    session.headers.update(headers)
    LOGIN_URL = f'{BASE_URL}/login'

    response = session.get(LOGIN_URL, headers=headers)
    print_dict(response.cookies)
    print_dict(session.cookies)
    payload = {
        'email': 'aileneidan@yahoo.com',
        'pass': 'chineziiardmeleaguri'
    }
    response = session.post(LOGIN_URL, data=payload, allow_redirects=False,
                            headers={'content-type': 'application/x-www-form-urlencoded'})
    print_dict(response.cookies)
    print_dict(session.cookies)
    response = session.get('https://www.facebook.com/mouna.joudar.massaoudi')
    print_dict(response.cookies)
    print_dict(session.cookies)
    print(response.content)


def add_friends_to_queue(friends, people):
    for friend in friends:
        # incerc sa-l iau din db
        current_person = check_if_friend_saved(friend)
        if not current_person:
            picture_url = get_profile_picture_url(friend)
            if not picture_url:
                picture_url = try_get_other_picture_with_face_url(friend)
            # salvam persoana in db chiar daca poza este None
            save_individual(friend, picture_url)
            current_person = Person(friend, get_picture_from_url(picture_url))

        people.append(current_person)


def crawl(subject, credentials):
    session = requests.Session()
    login_facebook(subject, credentials, session)
    people = deque()

    friends = get_friends_urls(subject)
    add_friends_to_queue(friends, people)

    while people:
        person = people.popleft()
        if person.picture and check_kinship(person, subject):
            # log l-am gas pe tac-tu
            return

        friends = get_friends_urls(person)
        add_friends_to_queue(friends, people)


class Person:
    def __init__(self, identifier, picture):
        self.identifier = identifier
        self.picture = picture


if __name__ == '__main__':
    format_string = '%(asctime)s %(levelname)s - %(message)s'
    date_format = '%H:%M:%S %d-%b-%y'
    logging.basicConfig(filename='app.log', format=format_string, datefmt=date_format)
    logging.warning("tata")

    subject = Person("dan.ailenei.9", None)
    crawl(subject, None)
