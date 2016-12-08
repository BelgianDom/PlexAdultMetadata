from abc import abstractmethod


class Site(object):
    siteId = None
    name = None
    baseUrl = None
    year = None
    month = None
    day = None
    patterns = []

    def __init__(self, siteId, name, baseUrl):
        self.siteId = siteId
        self.name = name
        self.baseUrl = baseUrl

    def get_site_id(self):
        return self.siteId

    def get_date(self):
        return "{}-{}-{}".format(self.year, self.month, self.day)

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def set_id(self, id):
        pass

    @abstractmethod
    def search(self, results, filename, media, lang, manual):
        pass

    @abstractmethod
    def get_metadata(self, metadata, media, lang, force):
        pass
