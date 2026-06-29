import subprocess, sys, tempfile, os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sg = os.path.join(root, 'check-stage-guardrails.py')

results = []

r = subprocess.run([sys.executable, sg, '--demo'], capture_output=True, encoding='utf-8')
ok = r.returncode == 0 and '[STRICT MODE]' not in r.stdout
results.append(('demo normal exit=0', ok))

r = subprocess.run([sys.executable, sg, '--demo', '--strict'], capture_output=True, encoding='utf-8')
ok = r.returncode == 1 and '[STRICT MODE]' in r.stdout
results.append(('demo strict exit=1 with header', ok))

clean_log = (
    '[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S1 | role=developer | session=test | msg=enter S1 | ctx={"entry_condition":"ok","prev_stage":null}\n'
    '[PDR-LOG] | level=INFO | event=PDR_START | stage=S1 | role=developer | session=test | msg=start PDR | ctx={"required_count":1}\n'
    '[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S1 | role=developer | session=test | msg=read doc | ctx={"doc":"README.md","bytes":100,"key_points":["a"]}\n'
    '[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S1 | role=developer | session=test | msg=PDR done | ctx={"read_count":1,"missing_count":0,"missing_with_risk":0,"ready_to_proceed":true}\n'
    '[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S1 | role=developer | session=test | msg=exit S1 | ctx={"exit_criteria_met":["done"],"duration":"1min","output_artifacts":["x"],"next_stage":"S2"}\n'
)
with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
    f.write(clean_log)
    tmpname = f.name
r = subprocess.run([sys.executable, sg, '--log-file', tmpname, '--strict'], capture_output=True, encoding='utf-8')
os.unlink(tmpname)
ok = r.returncode == 0
results.append(('clean log strict exit=0', ok))

warn_log = (
    '[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S1 | role=developer | session=test | msg=enter S1 | ctx={"entry_condition":"ok","prev_stage":null}\n'
    '[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S4 | role=developer | session=test | msg=skip to S4 | ctx={"entry_condition":"direct","prev_stage":"S1"}\n'
)
with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
    f.write(warn_log)
    tmpname = f.name
r = subprocess.run([sys.executable, sg, '--log-file', tmpname, '--strict'], capture_output=True, encoding='utf-8')
os.unlink(tmpname)
ok = r.returncode == 1 and 'NO_PDR_FOR_STAGE' in r.stdout
results.append(('warn log strict exit=1', ok))

all_ok = True
for name, ok in results:
    status = 'PASS' if ok else 'FAIL'
    print(f'  [{status}] {name}')
    if not ok:
        all_ok = False

print()
print('All tests passed!' if all_ok else 'SOME TESTS FAILED!')
sys.exit(0 if all_ok else 1)
