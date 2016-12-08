############################
#   Adult Metadata Agent   #
############################

import urllib
import ntpath
from matcher import Matcher
from site import Site
from intersec import *
from kink import *


def Start():
    HTTP.CacheTime = CACHE_1MINUTE
    # CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'


class AdultMetadataAgent(Agent.Movies):
    name = 'AdultMetadata'
    languages = [Locale.Language.English]
    primary_provider = True

    matcher = Matcher()
    websites = [HardTied(),
                InfernalRestraints(),
                TopGrl(),
                RealTimeBondage(),
                SexuallyBroken(),
                Hogtied(),
                DeviceBondage(),
                TheUpperFloor(),
                TheTrainingOfO(),
                KinkUniversity(),
                SadisticRope(),
                WaterBondage(),
                SexAndSubmission(),
                FuckingMachines(),
                PublicDisgrace(),
                HardcoreGangBang(),
                BoundGangBangs(),
                DungeonSex(),
                AnimatedKink(),
                WhippedAss(),
                DivineBitches(),
                UltimateSurrender(),
                EverythingButt(),
                ElectroSluts(),
                MenInPain(),
                WiredPussy(),
                FootWorship(),
                TSSeduction(),
                TSPussyHunters(),
                BoundGods(),
                MenOnEdge(),
                NakedCombat(),
                BoundInPublic(),
                ThirthyMinutesOfTorment(),
                ButtMachineBoys()
                ]

    def search(self, results, media, lang, manual):
        fn = urllib.unquote(media.filename)
        filename = ntpath.basename(fn)
        path = ntpath.dirname(fn)

        website = self.matcher.Find(filename, path, self.websites)
        if website is None:
            Log("No matching site found!")
            return

        website.search(results, filename, media, lang, manual)
        results.Sort('score', descending=True)

    def update(self, metadata, media, lang, force=False):
        content_id = metadata.id
        Log("update({})".format(content_id))
        website = self.matcher.get_by_id(content_id, self.websites)
        website.get_metadata(metadata, media, lang, force)
