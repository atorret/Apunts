"""Syllabus database, strict markdown, readings, and folder layout.

Standard library only. The database is the working copy. EDITORIAL_ORGANIZATION.md
is parsed once by seed, then rewritten as a reading.

The implementation is split across the sibling modules. Names are re-exported
here so existing imports keep working.
"""

from base import *
from syllabus import *
from exchange import *
from readings import *
from xref import *
from changes import *
from layout import *
from page import *
