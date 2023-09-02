
#! /usr/local/bin/python3.10

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/opc/bot/GitBot2/website")
from website import app as application

