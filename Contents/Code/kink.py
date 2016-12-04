from site import Site
from abc import abstractmethod
from helper import Helper
from matcher import *


class Kink(Site):
    ARTWORK_ITEM_LIMIT = 8

    id = None
    cookies = None

    helper = Helper()

    def __init__(self, siteId, name, baseUrl):
        Site.__init__(self, siteId, name, baseUrl)

    @abstractmethod
    def create(self):
        pass

    def get_id(self):
        return "{}-{}".format(self.siteId, self.id)

    def set_id(self, id):
        Log("set_id({})".format(id))
        parts = id.split("-")
        self.id = parts[1]
        return self

    def get_url(self):
        return "http://www.kink.com/shoot/{}".format(self.id)

    def init_cookies(self):
        if self.cookies is not None:
            return
        self.cookies = HTTP.CookiesForURL("http://www.kink.com")
        if self.cookies is not None:
            return
#        HTTP.ClearCookies()
        HTTP.Request("http://www.kink.com", headers={'Cookie': 'viewing-preferences=straight%2Cgay'}).content
        self.cookies = HTTP.CookiesForURL("http://www.kink.com")
        if self.cookies is None:
            Log.Error("init_cookies() FAILED!")

    def search(self, results, filename, media, lang, manual):
        self.init_cookies()
        self.update()

        self.helper.set_date_from_filename(self, filename)

        # Initialize best-match search
        words = set(re.findall(r'\W*(\w+)', filename.upper()))
        if self.year is not None:
            # Log("date: {}-{}-{}".format(self.year, self.month, self.day))
            words.add(self.year)
            words.add(self.month)
            words.add(self.day)
        bestMatch = len(words)
        Log("Words we look for: {}".format(words))

        # See if the filename contains a kink.com shoot number
        shootId = None
        shootIds = re.findall(r'\D*(\d\d\d\d\d)\D*', filename)
        if len(shootIds) == 1:
            shootId = self.siteId + "-" + str(shootIds[0])

        date = self.get_date()
        for id in Dict[self.siteId]['idToRecordMap']:
            record = Dict[self.siteId]['idToRecordMap'][id]
            if record['date'] == date:
                Log("Date Match -- Creating 100% match on: {}".format(record['title']))
                results.Append(MetadataSearchResult(id=id, name=record['title'], score=100,
                                                    year=int(self.year), lang=lang))
                continue

            if shootId is not None and id == shootId:
                Log("Shoot ID Match -- Creating 90% match on: {}".format(record['title']))
                results.Append(MetadataSearchResult(id=id, name=record['title'], score=90,
                                                    year=record['date'].split("-")[0], lang=lang))
                continue

            intersection = words & record['words']
            percentage = (len(intersection) * 100) / bestMatch
            # Log("{} -> {} or {}".format(record['words'], intersection, percentage))
            if percentage > 40:
                Log("Creating {}% match on: {}".format(percentage, record['title']))
                results.Append(MetadataSearchResult(id=id, name=record['title'], score=percentage,
                                                    year=record['date'].split("-")[0], lang=lang))


    def update(self):
        if not self.siteId in Dict:
            Dict[self.siteId] = {}
            Dict[self.siteId]['dateToIdMap'] = {}
            Dict[self.siteId]['idToRecordMap'] = {}
            Dict.Save()

        page = 0
        matched_movie = False
        changed = False
        # cookies = HTTP.CookiesForURL("http://www.kink.com")
        while not matched_movie:
            url = "http://www.kink.com/api/channels/shoots?category=latest&sitename={}&page={}&limit=20&includePrefs=true".format(self.siteId.lower(), page)
            req = HTTP.Request(url, headers = {'Cookie': self.cookies})
            json = req.content

            json_obj = JSON.ObjectFromString(json)
            html = HTML.ElementFromString("html" + json_obj['html'] + "</html>")
            # Log(json_obj['html'])

            shoots = html.xpath("//div[@class='shoot']")
            for shoot in shoots:
                shoot_href = shoot.xpath("./div[@class='shoot-thumb-image']/a/@href")[0]
                self.id = str(shoot_href).split("/")[2]

                date = shoot.xpath("./div[@class='shoot-thumb-info']/div[@class='top-row-info']/div[@class='date']/text()")[0]
                date = Datetime.ParseDate(str(date).strip()).date()
                self.year = "{:04d}".format(date.year)
                self.month = "{:02d}".format(date.month)
                self.day = "{:02d}".format(date.day)

                if self.get_date() in Dict[self.siteId]['dateToIdMap']:
                    matched_movie = True
                    continue

                Log("update - Indexing {}".format(self.id))

                title = str(shoot.xpath("./div[@class='shoot-thumb-info']/div[@class='shoot-thumb-title']/div/a/text()")[0]).strip()
                words = set(re.findall(r'\W*(\w+)', title.upper()))

                models = shoot.xpath("./div[@class='shoot-thumb-info']/div[@class='shoot-thumb-models']/a/text()")
                modelList = []
                for model in models:
                    name = str(model).replace(",\xc2\xa0", "").strip()
                    modelList.append(name)
                    for word in name.split(" "):
                        words.add(word.upper())
                Log("{} - {} - {}".format(shoot_href, self.get_date(), title))

                words.add(self.year)
                words.add(self.month)
                words.add(self.day)

                if len(modelList) == 0:
                    t = title
                elif len(modelList) == 1:
                    t = "{} ({})".format(title, modelList[0])
                else:
                    t = "{} ({}, {})".format(title, modelList[0], modelList[1])

                id = self.get_id()
                Dict[self.siteId]['dateToIdMap'][self.get_date()] = id
                Dict[self.siteId]['idToRecordMap'][id] = {}
                Dict[self.siteId]['idToRecordMap'][id]['words'] = words
                Dict[self.siteId]['idToRecordMap'][id]['date'] = self.get_date()
                Dict[self.siteId]['idToRecordMap'][id]['title'] = t
                changed = True

            if len(shoots) == 20:
                page += 1
            else:
                break

        if changed:
            Dict.Save()

    def get_metadata(self, metadata, media, lang, force):
        self.init_cookies()

        record = Dict[self.siteId]['idToRecordMap'][self.get_id()]

        # Retrieve the page
        href = self.get_url()
        html = HTML.ElementFromURL(href, headers = {'Cookie': self.cookies})

        # use site name as movie studio
        metadata.studio = self.name

        # add site name to genres
        metadata.genres.clear()
        metadata.genres.add(self.name)

        # add channels to genres
        # add other tags to collections
        metadata.collections.clear()
        tags = html.xpath('//div[@class="shoot-info"]//a[starts-with(@href,"/tag/")]')
        for tag in tags:
            if tag.get('href').endswith(':channel'):
                metadata.genres.add(tag.text_content().strip())
            else:
                metadata.collections.add(tag.text_content().strip())

        # set movie title to shoot title
        metadata.title = html.xpath('//div[@class="shoot-info"]//h1')[0].text_content() + " (" + record['date'] + ")"

        # set content rating to XXX
        metadata.content_rating = 'XXX'

        # set episode ID as tagline for easy visibility
        metadata.tagline = metadata.studio + " – " + self.id

        # set movie release date to shoot release date
        try:
            release_date = html.xpath('//div[@class="shoot-info"]//p[contains(.,"date:")]')[0].text_content().split('date: ', 1)[1]
            metadata.originally_available_at = Datetime.ParseDate(release_date).date()
            metadata.year = metadata.originally_available_at.year
        except: pass

        # Add posters and backdrops
        self.process_images(metadata, html)

        # summary
        try:
            metadata.summary = ""
            summary = html.xpath('//div[@class="shoot-info"]/div[@class="description"]')
            if len(summary) > 0:
                for paragraph in summary:
                    metadata.summary = metadata.summary + paragraph.text_content().strip().replace('<br>',"\n") + "\n"
                metadata.summary.strip()
        except: pass

        # director
        try:
            metadata.directors.clear()
            director_id = html.xpath('//div[@class="shoot-page"]/@data-director')[0]
            director_html = HTML.ElementFromURL("http://www.kink.com/model/%s" % director_id, headers={'Cookie': self.cookies})
            # 'viewing-preferences=straight%2Cgay'})
            director_name = director_html.xpath('//h1[@class="page-title"]')[0].text_content()
            try:
                director = metadata.directors.new()
                director.name = director_name
            except:
                try:
                    metadata.directors.add(director_name)
                except: pass
        except: pass

        # starring
        try:
            starring = html.xpath('//p[@class="starring"]/*[@class="names"]/a')
            metadata.roles.clear()
            for member in starring:
                role = metadata.roles.new()
                lename = member.text_content().strip()
                try:
                    role.name = lename
                except:
                    try:
                        role.actor = lename
                    except: pass
        except: pass

        # rating
        # cookies = self.cookies
        # Log(cookies)
        # cookies.add('viewing-preferences=straight%2Cgay')
        # Log(cookies)
        rating_dict = JSON.ObjectFromURL(url='http://www.kink.com/api/ratings/%s' % self.id, headers={'Cookie': self.cookies})
        metadata.rating = float(rating_dict['avgRating']) * 2

    def process_images(self, metadata, html):
        valid_posters = list()
        valid_backdrops = list()
        posterIndex = 0
        backdropIndex = 0
        posterUrls = html.xpath('//video/@poster')
        for posterUrl in posterUrls:
            url = str(posterUrl).strip()
            if posterIndex < self.ARTWORK_ITEM_LIMIT:
                valid_posters.append(self.add_poster(metadata, url, posterIndex))
            if backdropIndex < self.ARTWORK_ITEM_LIMIT:
                valid_backdrops.append(self.add_backdrop(metadata, url, backdropIndex))
            posterIndex += 1
            backdropIndex += 1
        posterUrls = html.xpath('//div[@id="previewImages"]//img/@src')
        for posterUrl in posterUrls:
            url = str(posterUrl).strip()
            if posterIndex < self.ARTWORK_ITEM_LIMIT:
                valid_posters.append(self.add_poster(metadata, url, posterIndex))
            if backdropIndex < self.ARTWORK_ITEM_LIMIT:
                valid_backdrops.append(self.add_backdrop(metadata, url, backdropIndex))
            posterIndex += 1
            backdropIndex += 1
        metadata.posters.validate_keys(valid_posters)
        metadata.art.validate_keys(valid_backdrops)

    def add_poster(self, metadata, url, index):
        thumbnail = re.sub(r'/h/[0-9]{3,3}/', r'/h/410/', url)
        full = re.sub(r'/h/[0-9]{3,3}/', r'/h/830/', url)
        Log("Adding new poster ({}): {}".format(index, full))
        metadata.posters[full] = Proxy.Preview(HTTP.Request(thumbnail), sort_order=index)
        return full

    def add_backdrop(self, metadata, url, index):
        if index >= self.ARTWORK_ITEM_LIMIT:
            return
        thumbnail = re.sub(r'/h/[0-9]{3,3}/', r'/h/410/', url)
        full = re.sub(r'/h/[0-9]{3,3}/', r'/h/830/', url)
        Log("Adding new backdrop ({}): {}".format(index, full))
        metadata.art[full] = Proxy.Preview(HTTP.Request(thumbnail), sort_order=index)
        return full


class SexAndSubmission(Kink):
    def __init__(self):
        Kink.__init__(self, "SEXANDSUBMISSION", "Sex and Submission", "")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*SEXANDSUBMISSION.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*SEXANDSUBMISSION.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*SEX AND SUBMISSION.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*SEX AND SUBMISSION.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^SAS\W.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, ".*\WSAS\W.*", re.IGNORECASE))

    def create(self):
        return SexAndSubmission()


class DeviceBondage(Kink):
    def __init__(self):
        Kink.__init__(self, "DEVICEBONDAGE", "Device Bondage", "")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*DEVICEBONDAGE.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*DEVICEBONDAGE.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*DEVICE BONDAGE.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*DEVICE BONDAGE.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^DB\W.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, ".*\WDB\W.*", re.IGNORECASE))

    def create(self):
        return DeviceBondage()


class TheUpperFloor(Kink):
    def __init__(self):
        Kink.__init__(self, "THEUPPERFLOOR", "The Upper Floor", "")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*THEUPPERFLOOR.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*THEUPPERFLOOR.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*UPPER FLOOR.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*UPPER FLOOR.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^TUF\W.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, ".*\WTUF\W.*", re.IGNORECASE))

    def create(self):
        return TheUpperFloor()


class HardcoreGangBang(Kink):
    def __init__(self):
        Kink.__init__(self, "HARDCOREGANGBANG", "Hardcore Gangbang", "")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*HARDCOREGANGBANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*HARDCOREGANGBANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*HARDCORE GANGBANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*HARDCORE GANGBANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*HARDCORE GANG BANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*HARDCORE GANG BANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^HGB\W.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, ".*\WHGB\W.*", re.IGNORECASE))

    def create(self):
        return HardcoreGangBang()


class BoundGangBangs(Kink):
    def __init__(self):
        Kink.__init__(self, "BOUNDGANGBANGS", "Bound Gang Bangs", "")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*BOUNDGANGBANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*BOUNDGANGBANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*BOUND GANGBANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*BOUND GANGBANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*BOUND GANG BANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*BOUND GANG BANG.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^BGB\W.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, ".*\WBGB\W.*", re.IGNORECASE))

    def create(self):
        return HardcoreGangBang()
