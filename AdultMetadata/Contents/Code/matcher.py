import re


class MatchType(object):
    Filename = 1
    Directory = 2


class MatchPriority(object):
    High = 100
    Medium = 50
    Low = 10


class Pattern(object):
    def __init__(self, site, priority, type, pattern, re_flags):
        self.site = site
        self.priority = priority
        self.type = type
        self.pattern = pattern
        self.flags = re_flags


class Matcher(object):
    def Find(self, filename, path, sites):
        Log("Matcher.Find({}, {})".format(filename, path))

        matches = []

        for site in sites:
            for pattern in site.patterns:
                # What to match against
                if MatchType.Filename == pattern.type:
                    text = filename
                else:
                    text = path

                if re.match(pattern.pattern, text, pattern.flags) is not None:
                    matches.append(pattern)

        if len(matches) > 0:
            matches.sort(key=lambda x: x.priority)
            Log("Matcher -- Result: {}".format(matches[0].site.name))
            return matches[0].site

        Log("Matcher -- NO MATCH!")
        return None

    def get_by_id(self, id, sites):
        Log("Matcher.get_by_id({})".format(id))
        parts = id.split("-")
        siteId = parts[0]

        for site in sites:
            if site.siteId == siteId:
                newSite = site.create()
                newSite.set_id(id)
                return newSite
