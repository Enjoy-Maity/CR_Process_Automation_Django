"""
CR Process Automation Django package.

Forces a UTF-8 stdio policy at import time so console output behaves the same
on every platform and console code page.  Windows consoles default to a
"charmap" codec (e.g. cp1252) which cannot encode Unicode symbols returned by
ITSM (such as the magnifier status emoji, U+1F50E); printing such characters
used to raise UnicodeEncodeError and crash task batches.
"""
import sys


def _force_utf8_stdio():
    """Make print()/stdout/stderr Unicode-safe regardless of the OS console."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            # Stream without reconfigure() (or already closed); leave as-is.
            pass


_force_utf8_stdio()
del _force_utf8_stdio