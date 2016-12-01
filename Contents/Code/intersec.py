from site import Site
from abc import abstractmethod
from helper import Helper
from matcher import *


class Intersec(Site):
    ARTWORK_ITEM_LIMIT = 8

    episode = None

    helper = Helper()

    def __init__(self, siteId, name, baseUrl):
        Site.__init__(self, siteId, name, baseUrl)

    @abstractmethod
    def create(self):
        pass

    def get_id(self):
        return "{}-{}-{}-{}-{}".format(self.siteId, self.year, self.month, self.day, self.episode)

    def get_id_without_episode(self):
        return "{}-{}-{}-{}-".format(self.siteId, self.year, self.month, self.day)

    def set_id(self, id):
        Log("set_id({})".format(id))
        parts = id.split("-")
        self.year = parts[1]
        self.month = parts[2]
        self.day = parts[3]
        self.episode = parts[4]
        return self

    def get_url(self):
        return "{}trailer.php?y={}&p={}_{}{}".format(self.baseUrl, self.year, self.month, self.day, self.episode)

    def search(self, results, filename, media, lang, manual):
        self.update()

        self.helper.set_date_from_filename(self, filename)

        if not manual and self.year is not None:
            if self.get_date() in Dict[self.siteId]['dateToIdMap']:
                id = Dict[self.siteId]['dateToIdMap'][self.get_date()]
                self.set_id(id)
                Log("Found {}, creating 100% match".format(id))
                results.Append(MetadataSearchResult(id=id, name=media.title, score=100, year=int(self.year), lang=lang))
                return

        # Initialize best-match search
        words = set(re.findall(r'\W*(\w+)', filename))
        if self.year is not None:
            # Log("date: {}-{}-{}".format(self.year, self.month, self.day))
            words.add(self.year)
            words.add(self.month)
            words.add(self.day)
        bestMatch = len(words)
        Log("Words we look for: {}".format(words))

        save = False
        id_without_episode = self.get_id_without_episode()
        for id in Dict[self.siteId]['idToRecordMap']:
            if id.startswith(id_without_episode):
                record = Dict[self.siteId]['idToRecordMap'][id]
                if 'title' not in record:
                    title = self.get_title(id)
                    record['title'] = title
                    save = True
                Log("Found {}, creating 100% match".format(id))
                results.Append(MetadataSearchResult(id=id, name=record['title'], score=100, year=int(self.year), lang=lang))
                continue

            intersection = words & Dict[self.siteId]['idToRecordMap'][id]['words']
            percentage = (len(intersection) * 100) / bestMatch
            if percentage > 40:
                record = Dict[self.siteId]['idToRecordMap'][id]
                if 'title' not in record:
                    title = self.get_title(id)
                    record['title'] = title
                    save = True
                Log("Creating {}% match ticket: {}".format(percentage, record['title']))
                results.Append(MetadataSearchResult(id=id, name=record['title'], score=percentage,
                                                    year=record['date'].split("-")[0], lang=lang))

        if save:
            Dict.Save()

    def update(self):
        if not self.siteId in Dict:
            Dict[self.siteId] = {}
            Dict[self.siteId]['dateToIdMap'] = {}
            Dict[self.siteId]['idToRecordMap'] = {}
            Dict.Save()

        page = 1
        matched_movie = False
        changed = False
        encountered = set()
        while not matched_movie:
            url = "{}gallery.php?page={}".format(self.baseUrl, page)
            html = HTML.ElementFromURL(url)

            matches = html.xpath("//a[contains(@href,'/bondage/20')]/@href")
            for match in matches:
                if match in encountered:
                    continue
                encountered.add(match)

                date = re.match(".*\/bondage\/(\d+)\/(\d\d)_(\d\d)([a-zA-Z]+[0-9]*)", match)
                if date is None:
                    # Not a valid ticket
                    continue

                self.year = date.group(1)
                self.month = date.group(2)
                self.day = date.group(3)
                self.episode = date.group(4)

                if self.get_date() in Dict[self.siteId]['dateToIdMap']:
                    matched_movie = True
                    continue

                Log("update - Indexing {}".format(match))

                words = set(re.findall(r'\W*(\w+)', " ".join(match.lower().split("/")[5:])))
                words.add(date.group(1))
                words.add(date.group(2))
                words.add(date.group(3))
                if "php" in words:
                    words.remove("php")

                id = self.get_id()
                Dict[self.siteId]['dateToIdMap'][self.get_date()] = id
                Dict[self.siteId]['idToRecordMap'][id] = {}
                Dict[self.siteId]['idToRecordMap'][id]['words'] = words
                # Dict[self.siteId]['idToRecordMap'][id]['href'] = str(match)
                Dict[self.siteId]['idToRecordMap'][id]['date'] = self.get_date()
                # Dict[self.siteId]['idToRecordMap'][id]['title'] = "/".join(match.split("/")[3:])
                changed = True

            next = html.xpath("//a[@id='next_page']")
            if len(next) > 0:
                page += 1
            else:
                break

        if changed:
            Dict.Save()

    def get_metadata(self, metadata, media, lang, force):
        # record = Dict[self.siteId]['idToRecordMap'][self.get_id()]

        # Retrieve the page
        href = self.get_url()
        html = HTML.ElementFromURL(href)

        # use site name as movie studio
        metadata.studio = self.name

        # add site name to genres
        metadata.genres.clear()
        metadata.genres.add(self.name)

        # set movie title to shoot title
        metadata.title = html.xpath("//span[@class='articleTitleText']/a/text()")[0]
        Log("Set title to {}".format(metadata.title))

        # set content rating to XXX
        metadata.content_rating = 'XXX'

        # set movie release date to shoot release date
        release_date = html.xpath("//span[@class='articlePostDateText'][1]/text()")[0]
        release_date = Datetime.ParseDate(release_date).date()
        metadata.originally_available_at = release_date
        metadata.year = release_date.year
        Log("Set originally available to {}".format(metadata.originally_available_at))

        # set episode ID as tagline for easy visibility
        metadata.tagline = "{} - {}-{}-{}".format(metadata.studio, "{:04d}".format(release_date.year),
                                                  "{:02d}".format(release_date.month),
                                                  "{:02d}".format(release_date.day))
        Log("Set tagline to {}".format(metadata.tagline))

        # Add posters and backdrops
        self.process_images(metadata, html)

        # summary
        metadata.summary = ""
        summary = html.xpath("//td[@class='articleCopyText']")
        if len(summary) > 0:
            for paragraph in summary:
                metadata.summary = metadata.summary + paragraph.text_content().strip().replace('<br>', "\n") + "\n"
            metadata.summary.strip()

        # starring
        starring = html.xpath("//span[@class='articleTitleText']/text()[2]")[0]
        metadata.roles.clear()
        actors = starring.split("|")
        for member in actors:
            if len(member.strip()) < 2:
                continue
            role = metadata.roles.new()
            lename = member.strip()
            try:
                role.name = lename
            except:
                try:
                    role.actor = lename
                except:
                    pass

    def get_title(self, id):
        # Retrieve the page
        parts = id.split("-")
        href = "{}trailer.php?y={}&p={}_{}{}".format(self.baseUrl, parts[1], parts[2], parts[3], parts[4])
        html = HTML.ElementFromURL(href)

        # title
        title = html.xpath("//span[@class='articleTitleText']/a/text()")[0]

        # starring
        starring = html.xpath("//span[@class='articleTitleText']/text()[2]")[0]
        stars = []
        actors = starring.split("|")
        for member in actors:
            if len(member.strip()) < 2:
                continue
            stars.append(member.strip())
        if len(stars) == 0:
            return title
        elif len(stars) == 1:
            return "{} ({})".format(title, stars[0])
        else:
            return "{} ({}, {})".format(title, stars[0], stars[1])


    def process_images(self, metadata, html):
        valid_posters = list()
        valid_backdrops = list()
        posterIndex = 0
        backdropIndex = 0
        posterUrls = html.xpath("//img[contains(@src,'/poster.jpg')]/@src")
        for posterUrl in posterUrls:
            if posterIndex < self.ARTWORK_ITEM_LIMIT:
                valid_posters.append(self.add_poster(metadata, posterUrl, posterIndex))
            posterIndex += 1
        posterUrls = html.xpath("//img[contains(@src,'/images/')]/@src")
        for posterUrl in posterUrls:
            if posterIndex < self.ARTWORK_ITEM_LIMIT:
                valid_posters.append(self.add_poster(metadata, posterUrl, posterIndex))
            if backdropIndex < self.ARTWORK_ITEM_LIMIT:
                valid_backdrops.append(self.add_backdrop(metadata, posterUrl, backdropIndex))
            posterIndex += 1
            backdropIndex += 1
        metadata.posters.validate_keys(valid_posters)
        metadata.art.validate_keys(valid_backdrops)

    def add_poster(self, metadata, url, index):
        Log("Adding new poster ({}): {}".format(index, url))
        metadata.posters[url] = Proxy.Media(HTTP.Request(url), sort_order=index)
        return url

    def add_backdrop(self, metadata, url, index):
        if index >= self.ARTWORK_ITEM_LIMIT:
            return
        Log("Adding new backdrop ({}): {}".format(index, url))
        metadata.art[url] = Proxy.Media(HTTP.Request(url), sort_order=index)
        return url


class HardTied(Intersec):
    def __init__(self):
        Intersec.__init__(self, "HARDTIED", "HardTied", "http://www.hardtied.com/hogtied/bondage/")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*HARDTIED.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*HARDTIED.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Medium, MatchType.Filename, "^HARDT\W.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^HT\W.*", re.IGNORECASE))

    def create(self):
        return HardTied()


class InfernalRestraints(Intersec):
    def __init__(self):
        Intersec.__init__(self, "INFERNAL", "Infernal Restraints", "http://www.infernalrestraints.com/device/bondage/")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*INFERNALRESTRAINTS.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*INFERNALRESTRAINTS.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*INFERNAL RESTRAINTS.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*INFERNAL RESTRAINTS.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^IR\W.*", re.IGNORECASE))

    def create(self):
        return InfernalRestraints()


class TopGrl(Intersec):
    def __init__(self):
        Intersec.__init__(self, "TOPGRL", "TopGrl", "http://www.topgrl.com/female/bondage/")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*TOPGRL.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*TOPGRL.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^TG\W.*", re.IGNORECASE))

    def create(self):
        return TopGrl()


class RealTimeBondage(Intersec):
    def __init__(self):
        Intersec.__init__(self, "RTBNDG", "RealTime Bondage", "http://www.realtimebondage.com/live/bondage/")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*REALTIMEBONDAGE.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*REALTIMEBONDAGE.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*REALTIME BONDAGE.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*REALTIME BONDAGE.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^RB\W.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^RTB\W.*", re.IGNORECASE))

    def create(self):
        return RealTimeBondage()


class SexuallyBroken(Intersec):
    def __init__(self):
        Intersec.__init__(self, "SEXBROKEN", "Sexually Broken", "http://www.sexuallybroken.com/sexual/bondage/")
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*SEXUALLYBROKEN.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*SEXUALLYBROKEN.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Filename, ".*SEXUALLY BROKEN.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.High, MatchType.Directory, ".*SEXUALLY BROKEN.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^SB\W.*", re.IGNORECASE))
        self.patterns.append(Pattern(self, MatchPriority.Low, MatchType.Filename, "^SEB\W.*", re.IGNORECASE))

    def create(self):
        return SexuallyBroken()
