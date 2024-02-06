# __init__.py for pysas
#
#

from . import sastask
from . import parser
from . import param
from . import error
from . import runtask
from . import configutils
from .version import *
from .odfcontrol import odfcontrol

import os, subprocess
lheasoft = os.environ.get('LHEASOFT')
headas = os.path.join(lheasoft,'headas-init.sh')
subprocess.run(["bash",headas])

__version__ = f'pysas - (pysas-{VERSION}) [{SAS_RELEASE}-{SAS_AKA}]'
