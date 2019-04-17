

def get_profile_picture_url(friend):
    return None


def try_get_other_picture_with_face_url(friend):
    return None


def save_individual(friend, picture_url):
    pass


def check_kinship(person, subject):
    return False


def get_picture_from_url(picture_url):
    pass


def add_friends_to_queue(friends):
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


class Person:
    def __init__(self, identifier, picture):
        self.identifier = identifier
        self.picture = picture
