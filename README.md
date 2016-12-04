PlexAdultMetadata.bundle
========================

## Introduction

This plugin aims to provide metadata for the most popular adult (subscription) sites without needing to rename
the movies.  I've spent way too time on finding the episode number from a kink.com production and renaming the movie.

Goals for this Plex agent plugin:
* Determine website without needing to rename the file
* Determine correct movie / episode / ticket without needing to rename the file
* Provide sorted search results from the website when the filename does not contain enough information (or incorrect information)
* Provide a framework which makes it easy to support new/more websites
* Cache website data, for two reasons:
  * Limit the load on the website to the absolute minimum
  * Provide fast matching and searching such that adding a whole library of movies is easy and fast


## Installation

TO DO


## Matching

The process of finding metadata for a movie consists of the following steps:

1. Determine website the movie belongs to.
   * Can be based on both the file name and directory name. I.e. if the file names are nonsensical, placing them inside
     a directory named after the website will still yield a proper match.
   * Unless otherwise notes, matching is case-insensitive.
   * Different matches have different priorities.  The more accurate a match is, the higher its priority.  This
     prevents a small match like "filename starts with IR" to match a file to the wrong website.
   * How this is matched is documented for each Producer / Website below.

2. Find the movie / episode / show.  This usually results in one or more search results.  If the match is certain,
   the search result will show as a 100% match.  Common ways to find matching movies are:
   * Matching the movie release date (see Supported Date Formats below)
   * Matching the movie id
   * Matching words in the filename (title, actor, etc.) to movie information
   * Unless otherwise notes, matching is case-insensitive.
   * How this is matched is documented for each Producer / Website below.


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


Producers and Websites
======================

## Intersec Interactive (a.k.a. Insex)

1. Available metadata
   * Title
   * Release Date
   * Summary
   * Models/Actors
   * Posters and Backdrops (derived from the same pool of images)
1. Website matching
   * See each individual site below
1. Movie (Ticket) matching
   * Primary matching is done using the release date (if found in the filename -- see Supported Date Formats)
   * Secondary matching is done using text search (i.e. episode title and actor names in the filename will yield
     a pretty good search result.)
 

#### hardtied.com
* Website matching:
  * Filename contains "HARDTIED" (High)
  * Directory contains "HARDTIED" (High)
  * Filename starts with "HARDT" (Medium)
  * Filename starts with "HT" (Low)

#### infernalrestraints.com
* Website matching:
  * Filename contains "INFERNALRESTRAINTS" or "INFERNAL RESTRAINTS" (High)
  * Directory contains "INFERNALRESTRAINTS" or "INFERNAL RESTRAINTS" (High)
  * Filename starts with "IR" (Low)

#### realtimebondage.com
* Website matching:
  * Filename contains "REALTIMEBONDAGE" or "REALTIME BONDAGE" (High)
  * Directory contains "REALTIMEBONDAGE" or "REALTIME BONDAGE" (High)
  * Filename starts with "RB" or "RTB" (Low)

#### sexuallybroken.com
* Website matching:
  * Filename contains "SEXUALLYBROKEN" or "SEXUALLY BROKEN" (High)
  * Directory contains "SEXUALLYBROKEN" or "SEXUALLY BROKEN" (High)
  * Filename starts with "SB" or "SEB" (Low)

#### topgrl.com
* Website matching:
  * Filename contains "TOPGRL" (High)
  * Directory contains "TOPGRL" (High)
  * Filename starts with "TG" (Low)


## Kink.com

1. Available metadata
   * Title
   * Genres/Collections
   * Release Date
   * Summary
   * Models/Actors
   * Director
   * Posters and Backdrops (derived from the same pool of images)
   * Rating
1. Website matching
   * See each individual site below
1. Movie (Ticket) matching
   * Primary matching is done using the release date (if found in the filename -- see Supported Date Formats)
   * Secondary matching is done using the kink.com shoot Id.  If the filename contains a 5-digit code which matches a
     shoot for the website, the shoot is added as a 90% match.
   * Tertiary matching is done using text search (i.e. episode title and actor names in the filename will yield
     a pretty good search result.)
 

#### sexandsubmission.com
* Website matching:
  * Filename contains "SEXANDSUBMISSION" or "SEX AND SUBMISSION" (High)
  * Directory contains "SEXANDSUBMISSION" or "SEX AND SUBMISSION" (High)
  * Filename starts with or contains "SAS" (Low)

#### devicebondage.com
* Website matching:
  * Filename contains "DEVICEBONDAGE" or "DEVICE BONDAGE" (High)
  * Directory contains "DEVICEBONDAGE" or "DEVICE BONDAGE" (High)
  * Filename starts with or contains "DB" (Low)

#### theupperfloor.com
* Website matching:
  * Filename contains "THEUPPERFLOOR" or "UPPER FLOOR" (High)
  * Directory contains "THEUPPERFLOOR" or "UPPER FLOOR" (High)
  * Filename starts with or contains "TUF" (Low)

#### hardcoregangbang.com
* Website matching:
  * Filename contains "HARDCOREGANGBANG" or "HARDCORE GANGBANG" or "HARDCORE GANG BANG" (High)
  * Directory contains "HARDCOREGANGBANG" or "HARDCORE GANGBANG" or "HARDCORE GANG BANG" (High)
  * Filename starts with or contains "HGB" (Low)

#### boundgangbangs.com
* Website matching:
  * Filename contains "BOUNDGANGBANG" or "BOUND GANGBANG" or "BOUND GANG BANG" (High)
  * Directory contains "BOUNDGANGBANG" or "BOUND GANGBANG" or "BOUND GANG BANG" (High)
  * Filename starts with or contains "BGB" (Low)
  * *Note that while the site name uses "bangS", the above matches work even if the S is missing.*
