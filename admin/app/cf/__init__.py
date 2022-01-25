# -*- coding: utf-8 -*-
"""
app.cf
~~~~~~~~~~~~~~~~~~~

cf = config 配置
"""

from flask import (Blueprint)

cf = Blueprint('cf', __name__)

from . import vo
