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
