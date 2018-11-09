#! /usr/bin/env python3

"""
Filters the pagelinks table, removing broken links and changeing the target to refer
to id and not title. 

------------------------------------
PAGE FILE FORMAT
  PAGE_ID,'TITLE',IS_REDIRECT[0|1]\\n

------------------------------------
REDIRECT FILE FORMAT
  FROM_ID,TARGET_ID\\n

------------------------------------
PAGELINK FILE FORMAT BEFORE
  FROM_ID,'TARGET_TITLE'\\n

PAGELINK FILE FORMAT AFTER
  FROM_ID,TARGET_ID\\n
  
"""	