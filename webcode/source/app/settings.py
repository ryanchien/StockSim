import os

IS_PRODUCTION = os.environ.get('IS_PRODUCTION')
ENABLE_USER_ACTIVATION = False

if IS_PRODUCTION:
    from .conf.production.settings import *
else:
    from .conf.development.settings import *

