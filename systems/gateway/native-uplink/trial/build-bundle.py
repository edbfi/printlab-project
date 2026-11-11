#!/usr/bin/python3
"""Offline source-only packaging. Does not install or execute any trial code."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[4]
component = root / 'systems/gateway/native-uplink'
trial = component / 'trial'
output = Path(sys.argv[1]).absolute()
output.mkdir(mode=0o700)
files = {}
for name in ('native-uplink', 'native-uplink-hook', 'native_service.py', 'native_port.py',
             'native_state.py', 'lease_lifecycle.py', 'lease_validation.py', 'lease_timing.py',
             'native-uplink.json', '05-native-uplink.network', 'printing-native-uplink.service'):
    files[name] = component / name
for name in ('uplink-trial.py', 'stage-trial.py', 'printing-uplink-boot-reset.service',
             'printing-uplink-boot-recover.service', 'printing-uplink-rollback.service'):
    files[name] = trial / name
files['10-keep-foreign-routes.conf'] = component / 'networkd.conf.d/10-keep-foreign-routes.conf'
files['vpn-policy.py'] = root / 'systems/gateway/vpn-policy/vpn-policy.py'
dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip())
manifest = {'dirty': dirty, 'source': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(), 'files': {}}
for name, source in sorted(files.items()):
    data = source.read_bytes()
    mode = 0o755 if name in ('native-uplink', 'native-uplink-hook', 'uplink-trial.py', 'stage-trial.py', 'vpn-policy.py') else 0o644
    (output / name).write_bytes(data)
    (output / name).chmod(mode)
    manifest['files'][name] = {'sha256': hashlib.sha256(data).hexdigest(), 'mode': mode,
                               'source': str(source.relative_to(root))}
raw = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
(output / 'manifest.json').write_bytes(raw)
(output / 'manifest.json').chmod(0o644)
print(hashlib.sha256(raw).hexdigest(), output / 'manifest.json')
