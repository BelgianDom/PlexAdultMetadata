# PlexAdultMetadata.bundle

## Introduction

This plugin aims to provide metadata for the most popular adult (subscription) sites without needing to rename
the movies.  I've spent way too time on finding the episode number from a kink.com production and renaming the movie.

Goals for this Plex agent plugin:
* Determine website without needing to rename the file
* Determine correct movie / episode / ticket without needing to rename the file
* Provide sorted search results from the website when the filename does not contain enough information (or incorrect information)
* Provide a framework which makes it easy to support new/more websites


## Supported Date Formats

Most adult websites release only a couple of new movies per month.  Hence, finding the movie by its release
date tends to be very accurate.  Of course, that requires knowing the release date.  Most of the movies contain
it in their filename, but it needs to be in one of the supported formats for this plugin to be able to extract it.

*Note: if you encounter an unsupported date format which you believe we should be able to extract automatically,
send a message or open up a bug with more information.  The intention is that this plugin will find the correct
date if at all possible without you needing to rename the file.*

* YYYY-MM-DD (i.e. 2016.12.01)
  
  Instead of a dash (-), the separator can be dot (.), underscore (_), or space ( ).
  
* YY-MM-DD (i.e. 16_12_01)
  
  Instead of a dash (-), the separator can be dot (.), underscore (_), or space ( ).
  
* MMM DD, YYYY (i.e. Dec 01, 2016)

  Months must be in English!
  
* YYMMDD (i.e. 161201)

  Dates in this format must be exactly 6 digits (no digits before or behind it.)


## Supported Websites

| Website                     | Producer                      |
|:--------------------------- |:-----------------------------:|
| hardtied.com                | Intersec Interactive          |
| infernalrestraints.com      | Intersec Interactive          |
| realtimebondage.com         | Intersec Interactive          |
| sexuallybroken.com          | Intersec Interactive          |
| topgrl.com                  | Intersec Interactive          |

## Matching Websites

**Unless noted otherwise, all matching is done case-insensitive!**

### hardtied.com (Intersec Interactive)
* Site matching:
  * Filename contains "Hardtied"
  * Directory contains "Hardtied"
  * Filename starts with "Hardt"
  * Filename starts with "HT"
* Movie/episode matching:
  * Filename should contain the date of the episode (see Supported Date Formats)
  * If no date match can be made, search will match based on keywords (i.e. episode title and actor names in the filename will yield a pretty good search result.)
  
