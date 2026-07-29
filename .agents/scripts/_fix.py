# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import os

with open('path-migration-ci.ps1', 'r', encoding='utf-8') as f:
    ps1 = f.read()

ps1 = ps1.replace('[switch]$Verbose,', '[Alias("v")][switch]$VerboseLog,')
ps1 = ps1.replace('-Verbose', '-VerboseLog')
ps1 = ps1.replace('if ($Verbose)', 'if ($VerboseLog)')

with open('path-migration-ci.ps1', 'w', encoding='utf-8') as f:
    f.write(ps1)
print('PS1 fixed')

print('SH exists:', os.path.exists('path-migration-ci.sh'))

if os.path.exists('_temp_gen.py'):
    os.remove('_temp_gen.py')
    print('Temp gen removed')
if os.path.exists('_fix.py'):
    print('Will self-remove after run')

