import re

class Helper(object):
    def set_date_from_filename(self, site, filename):
        site.year = None
        site.month = None
        site.day = None
        date_match = re.match(r'.*(\d\d\d\d)[\._\-\s](\d\d)[\._\-\s](\d\d).*', filename)
        if date_match is not None:
            Log("Matched date format YYYY.MM.DD: {}".format(date_match.group(0)))
            site.year = date_match.group(1)
            site.month = date_match.group(2)
            site.day = date_match.group(3)
            return True
        date_match = re.match(r'.*(\d\d)[\._\-\s](\d\d)[\._\-\s](\d\d).*', filename)
        if date_match is not None:
            Log("Matched date format YY.MM.DD: {}".format(date_match.group(0)))
            year = int(date_match.group(1))
            if year > 40:
                year += 1900
            else:
                year += 2000
            site.year = str(year)
            site.month = date_match.group(2)
            site.day = date_match.group(3)
            return True
        date_match = re.match(r'.*([a-zA-Z][a-zA-Z][a-zA-Z] \d?\d, \d\d\d\d).*', filename)
        if date_match is not None:
            Log("Matched date format MMM DD, YYYY: {}".format(date_match.group(1)))
            date = Datetime.ParseDate(date_match.group(1)).date()
            site.year = "{:04d}".format(date.year)
            site.month = "{:02d}".format(date.month)
            site.day = "{:02d}".format(date.day)
            return True
        date_match = re.match(r'.*\D(\d\d)(\d\d)(\d\d)\D.*', filename)
        if date_match is not None:
            Log("Matched date format YYMMDD: {}".format(date_match.group(0)))
            year = int(date_match.group(1))
            if year > 40:
                year += 1900
            else:
                year += 2000
            site.year = str(year)
            site.month = date_match.group(2)
            site.day = date_match.group(3)
            return True
        return False
