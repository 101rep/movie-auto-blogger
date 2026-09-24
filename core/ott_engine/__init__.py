# -*- coding: utf-8 -*-
"""
EnterPick24 OTT Automation Engine Package.
"""

from core.ott_engine.tvmaze_client import TVmazeClient
from core.ott_engine.fanart_client import FanartClient
from core.ott_engine.template_renderer import DarkMagazineRenderer
from core.ott_engine.ott_writer import OTTWriter
from core.ott_engine.publisher import OTTPublisher

__all__ = [
    "TVmazeClient",
    "FanartClient",
    "DarkMagazineRenderer",
    "OTTWriter",
    "OTTPublisher"
]
