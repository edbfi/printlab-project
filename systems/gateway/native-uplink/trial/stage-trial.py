#!/usr/bin/python3 -IB
"""Install an inert pinned trial bundle. Requires root and explicit bundle hash.

Use only after review. The bundle must be root-owned and immutable to other users.
No service start, network reload, policy replacement, or acquisition here.
"""
import hashlib
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import pwd
import stat
import subprocess
import sys

BASE = Path('/var/lib/printing-station/rollback/native-uplink-trial')
DEST = Path('/usr/local/libexec/printing-station')
ETC = Path('/etc/printing-station')
UNITS = Path('/etc/systemd/system')
FILES = ('native-uplink', 'native-uplink-hook', 'native_service.py', 'native_port.py',
         'native_state.py', 'lease_lifecycle.py', 'lease_validation.py', 'lease_timing.py')


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=15,
                          env={'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}).stdout.strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs():
    result = set()
    for root in ('/etc/systemd/network', '/run/systemd/network', '/usr/lib/systemd/network',
                 '/etc/systemd/networkd.conf.d', '/run/systemd/networkd.conf.d',
                 '/usr/lib/systemd/networkd.conf.d'):
        folder = Path(root)
        if folder.exists():
            result.update(str(p) for p in folder.rglob('*') if p.is_file())
    if Path('/etc/systemd/networkd.conf').is_file():
        result.add('/etc/systemd/networkd.conf')
    return sorted(result)


def main():
    if os.geteuid() != 0 or len(sys.argv) != 4:
        raise SystemExit('Usage (root): stage-trial.py ROOT_BUNDLE MANIFEST_SHA256 ENDPOINT')
    os.umask(0o022)
    bundle = Path(sys.argv[1]).resolve()
    endpoint = ipaddress.IPv4Address(sys.argv[3])
    if not endpoint.is_global or endpoint.is_multicast:
        raise SystemExit('Expected public unicast endpoint')
    for p in (bundle, *bundle.parents, *bundle.rglob('*')):
        info = p.lstat()
        if (info.st_uid != 0 or info.st_mode & 0o022 or
                not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode))):
            raise SystemExit('Bundle is not root-owned source-only storage')
    manifest_path = bundle / 'manifest.json'
    if digest(manifest_path) != sys.argv[2]:
        raise SystemExit('Bundle manifest hash differs from reviewed value')
    manifest = json.loads(manifest_path.read_text())
    for name, value in manifest['files'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or digest(bundle / name) != value['sha256']:
            raise SystemExit('Bundle file verification failed')
    spec = importlib.util.spec_from_file_location('trial', bundle / 'uplink-trial.py')
    trial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trial)
    for directory in (DEST, *DEST.parents, *BASE.parents, ETC, *ETC.parents,
                      Path('/etc/systemd/network'), UNITS):
        trial.safe(directory, True)
    recovery_units = ('printing-native-uplink.service', 'printing-uplink-boot-reset.service',
                      'printing-uplink-boot-recover.service', 'printing-uplink-rollback.service')
    drop_units = ('systemd-networkd.service', 'windscribe-helper.service', 'user@1000.service',
                  'printing-vpn-check.service', 'printing-vpn-refresh.service')
    absent_paths = [UNITS / name for name in recovery_units]
    absent_paths.append(UNITS / 'printing-native-uplink.service.d')
    for unit in drop_units:
        folder = UNITS / (unit + '.d')
        if folder.exists():
            trial.safe(folder, True)
        absent_paths.append(folder / '90-native-trial-recovery.conf')
    if not trial.absent():
        raise SystemExit('Native is not reserved/addressless')
    if digest(Path('/etc/systemd/networkd.conf.d/10-keep-foreign-routes.conf')) != digest(bundle / '10-keep-foreign-routes.conf'):
        raise SystemExit('Foreign-route preservation setting differs')
    for p in (*absent_paths, BASE, DEST / 'native-uplink', DEST / 'uplink-trial.py', ETC / 'native-uplink.json',
              Path('/etc/systemd/network/05-native-uplink.network'), UNITS / 'printing-native-uplink.service'):
        if p.exists() or p.is_symlink():
            raise SystemExit('Staging requires absent new deployment paths: ' + str(p))
    if run('/usr/bin/systemctl', 'show', 'printing-native-uplink.service', '-p', 'LoadState', '--value') != 'not-found':
        raise SystemExit('Native unit already loaded')
    user = run('/usr/bin/systemctl', 'show', 'printing-vpn-check.service', '-p', 'User', '--value')
    account = pwd.getpwnam(user)
    if account.pw_uid != 1000:
        raise SystemExit('Review boot unit account ordering for a different UID')
    policy_config = json.loads((ETC / 'vpn-policy.json').read_text())
    static_ip = str(ipaddress.IPv4Address(policy_config['static_ip']))
    env = dict(PATH='/usr/sbin:/usr/bin:/sbin:/bin', LC_ALL='C', HOME=account.pw_dir, XDG_RUNTIME_DIR='/run/user/1000',
               DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
    observed = subprocess.run(['/usr/sbin/runuser', '-u', user, '--', '/opt/windscribe/windscribe-cli', 'status'],
                              check=True, capture_output=True, text=True, timeout=15, stdin=subprocess.DEVNULL, env=env).stdout
    fields = dict(line.lstrip('*').split(': ', 1) for line in observed.splitlines() if ': ' in line)
    location = fields.get('Connect state', '').removeprefix('Connected: ').removesuffix(' [Network interference]')
    if (fields.get('Connect state', '').removesuffix(' [Network interference]') != 'Connected: ' + location or fields.get('VPN IP') != static_ip
            or fields.get('Protocol', '').lower() != 'stealth:443'):
        raise SystemExit('Expected currently connected static Stealth tunnel')
    if str(endpoint) == static_ip:
        raise SystemExit('Outer endpoint must differ from static exit address')
    route = trial.ip('-4', 'route', 'get', str(endpoint))
    if len(route) != 1 or route[0].get('dev') != 'wlan0':
        raise SystemExit('Current endpoint is not on Wi-Fi')
    link = {'interface': 'wlan0', 'address': route[0]['prefsrc'], 'gateway': route[0]['gateway']}
    if trial.transport_peers(link) != [str(endpoint)]:
        raise SystemExit('Current Windscribe socket does not establish endpoint authority')
    lan = Path('/var/lib/printing-station/rollback/20261110-lan-usb')
    if not (lan / 'school-attachment-allowed').is_file():
        raise SystemExit('Accepted USB LAN marker missing')
    for name in ('accepted-lan.sha256', 'protected.sha256'):
        run('/usr/bin/sha256sum', '-c', str(lan / name))
    protected = set(inputs())
    for name in ('accepted-lan.sha256', 'protected.sha256'):
        for line in (lan / name).read_text().splitlines():
            protected.add(line[66:])
    protected.add(str(ETC / 'vpn-policy.json'))
    if protected.intersection({str(DEST / 'vpn-policy.py'), str(ETC / 'native-uplink.json'), str(trial.PROFILE)}):
        raise SystemExit('Protected manifest contains a trial mutation target')
    BASE.mkdir(mode=0o700)
    def save(name, data, mode=0o600):
        p = BASE / name
        trial.write(p, data, mode)
    save('manifest.json', manifest_path.read_bytes())
    save('protected.json', json.dumps({p: digest(Path(p)) for p in sorted(protected)}).encode())
    save('network-inputs.json', json.dumps(inputs()).encode())
    save('old-policy.py', (DEST / 'vpn-policy.py').read_bytes())
    save('new-policy.py', (bundle / 'vpn-policy.py').read_bytes())
    save('disabled.json', (bundle / 'native-uplink.json').read_bytes())
    save('05-native-uplink.network', (bundle / '05-native-uplink.network').read_bytes())
    save('trial.json', json.dumps({'user': user, 'static_ip': static_ip, 'location': location,
                                 'endpoint': str(endpoint), 'boot': '', 'deadline': 0,
                                 'source': manifest['source']}).encode())
    def install(name, path, mode):
        tmp = path.with_name(path.name + '.trial-new')
        with tmp.open('xb') as stream:
            stream.write((bundle / name).read_bytes())
            stream.flush()
            os.fsync(stream.fileno())
        tmp.chmod(mode)
        os.replace(tmp, path)
    (DEST / 'native-uplink').mkdir(mode=0o755)
    for name in FILES:
        install(name, DEST / 'native-uplink' / name, 0o755 if name in FILES[:2] else 0o644)
    install('native-uplink.json', ETC / 'native-uplink.json', 0o600)
    install('uplink-trial.py', DEST / 'uplink-trial.py', 0o755)
    for name in ('printing-native-uplink.service', 'printing-uplink-boot-reset.service',
                 'printing-uplink-boot-recover.service', 'printing-uplink-rollback.service'):
        install(name, UNITS / name, 0o644)
    # Persist prerequisites before publishing boot dependencies.
    run('/usr/bin/sync', '-f', str(BASE))
    # Order early actors after best-effort reset, without gating networking on its success.
    for unit in ('systemd-networkd.service', 'windscribe-helper.service', 'user@1000.service'):
        folder = UNITS / (unit + '.d')
        folder.mkdir(mode=0o755, exist_ok=True)
        p = folder / '90-native-trial-recovery.conf'
        trial.write(p, b'[Unit]\nWants=printing-uplink-boot-reset.service\nAfter=printing-uplink-boot-reset.service\n', 0o644)
    folder = UNITS / 'printing-native-uplink.service.d'
    folder.mkdir(mode=0o755)
    trial.write(folder / 'trial.conf', b'[Unit]\nConditionPathExists=/run/printing-native-uplink/trial-permit\n', 0o644)
    for unit in ('printing-vpn-check.service', 'printing-vpn-refresh.service'):
        folder = UNITS / (unit + '.d')
        folder.mkdir(mode=0o755, exist_ok=True)
        p = folder / '90-native-trial-recovery.conf'
        trial.write(p, b'[Unit]\nAfter=printing-uplink-boot-recover.service\nConditionPathExists=|!/var/lib/printing-station/rollback/native-uplink-trial/pending\nConditionPathExists=|/run/printing-native-uplink/policy-permit\n', 0o644)
    run('/usr/bin/sync', '-f', str(BASE))
    run('/usr/bin/systemctl', 'daemon-reload')
    run('/usr/bin/systemctl', 'enable', 'printing-uplink-boot-recover.service')
    print('Inert trial staged; no policy/profile/acquisition activation')


if __name__ == '__main__':
    main()
