"""
Utilities for mermaid2 module
"""
import logging 

from mkdocs.utils import warning_filter

# -------------------
# Logging
# -------------------
log = logging.getLogger("mkdocs.plugins." + __name__)
log.addFilter(warning_filter)

MERMAID_LABEL = "MERMAID2  -" # plugin's signature label
def info(*args) -> str:
    "Write information on the console, preceded by the signature label"
    args = [MERMAID_LABEL] + [str(arg) for arg in args]
    msg = ' '.join(args)
    log.info(msg)
