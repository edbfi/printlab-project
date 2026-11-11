#!/usr/bin/python3 -IB
"""Local supervisor for one pinned native-uplink trial. Never run from checkout.

All trial modes are root-only. The independently armed rollback stops the apply
unit before taking any lock; DHCP stop/ExecStopPost never runs under our lock.
"""
import contextlib
import hashlib
import json
import ipaddress
import os
from pathlib import Path
import pwd
import stat
import subprocess
import sys
import time
import uuid

SELF = Path('/usr/local/libexec/printing-station/uplink-trial.py')
BASE = Path('/var/lib/printing-station/rollback/native-uplink-trial')
HELPER = Path('/usr/local/libexec/printing-station/native-uplink')
CONFIG = Path('/etc/printing-station/native-uplink.json')
POLICY = Path('/usr/local/libexec/printing-station/vpn-policy.py')
PROFILE = Path('/etc/systemd/network/05-native-uplink.network')
RUNTIME = Path('/run/printing-native-uplink')
NATIVE = 'printing-native-uplink.service'
TIMERS = ['printing-vpn-check.timer', 'printing-vpn-refresh.timer']
SERVICES = ['printing-vpn-check.service', 'printing-vpn-refresh.service']
CLI = '/opt/windscribe/windscribe-cli'
ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}


def run(argv, timeout=10, check=True):
    p = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=timeout, env=ENV)
    if check and p.returncode:
        raise RuntimeError('Command failed: ' + argv[0])
    return p


def systemctl(*args, timeout=5, check=True):
    return run(['/usr/bin/systemctl', *args], timeout, check)


def safe(path, directory=False):
    info = path.lstat()
    if (info.st_uid != 0 or info.st_mode & 0o022
            or not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode))):
        raise RuntimeError('Unsafe root-owned path: ' + str(path))


def write(path, data, mode=0o600):
    safe(path.parent, True)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.new')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        tmp.unlink(missing_ok=True)


def marker(name):
    write(BASE / name, (time.strftime('%Y-%m-%dT%H:%M:%S%z') + '\n').encode())
    print(name, flush=True)


def meta():
    safe(BASE / 'trial.json')
    return json.loads((BASE / 'trial.json').read_text())


def boot():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def load_native():
    sys.dont_write_bytecode = True
    if (HELPER / '__pycache__').exists():
        raise RuntimeError('Native helper contains bytecode cache')
    for path in (HELPER, *HELPER.parents):
        safe(path, True)
    for name in ('native_service.py', 'native_port.py', 'native_state.py',
                 'lease_lifecycle.py', 'lease_validation.py', 'lease_timing.py'):
        safe(HELPER / name)
    sys.path.insert(0, str(HELPER))
    import native_service
    return native_service


@contextlib.contextmanager
def operation():
    # Same inode/path used by all production callbacks and cleanup.
    native = load_native()
    RUNTIME.mkdir(mode=0o755, exist_ok=True)
    safe(RUNTIME, True)
    from native_port import NativePort
    from native_state import StateStore
    with NativePort(StateStore(RUNTIME, boot()), lock_timeout=15).lock():
        yield native


def config(enabled):
    value = {'allow_acquisition': enabled, 'timing_assumption_approved': enabled,
             'vpn_endpoint': meta()['endpoint'] if enabled else None}
    write(CONFIG, (json.dumps(value) + '\n').encode())


def cli(*args, timeout=15):
    account = pwd.getpwnam(meta()['user'])
    return run(['/usr/sbin/runuser', '-u', account.pw_name, '--', '/usr/bin/env', '-i',
                'HOME=' + account.pw_dir, 'XDG_RUNTIME_DIR=/run/user/' + str(account.pw_uid),
                'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/' + str(account.pw_uid) + '/bus',
                'PATH=/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL=C', CLI, *args], timeout, False)


def status():
    result = cli('status')
    if result.returncode:
        raise RuntimeError('Windscribe status unavailable')
    return dict(line.lstrip('*').split(': ', 1) for line in result.stdout.splitlines() if ': ' in line)


def wait_for(predicate, seconds):
    deadline = time.monotonic() + seconds
    while True:
        try:
            if predicate():
                return
        except (OSError, RuntimeError, subprocess.SubprocessError):
            pass  # Startup/read failures remain bounded by the same local deadline.
        if time.monotonic() >= deadline:
            raise TimeoutError('Local verification deadline')
        time.sleep(1)


def disconnected():
    fields = status()
    state = fields.get('Connect state', '')
    return (fields.get('Login state') == 'Logged in'
            and not state.startswith('Error: You are out of data, or your account has been disabled')
            and (state == 'Disconnected' or state.startswith('Error: ')))


def disconnect():
    cli('disconnect', timeout=20)
    wait_for(disconnected, 15)


def ip(*args):
    return json.loads(run(['/usr/sbin/ip', '-j', *args], timeout=3).stdout)


def absent():
    if any(row.get('addr_info') for row in ip('address', 'show', 'dev', 'enp1s0')):
        return False
    if any(row.get('dev') == 'enp1s0' for row in ip('-4', 'route', 'show', 'table', 'all')):
        return False
    for row in ip('-6', 'route', 'show', 'table', 'all'):
        if row.get('dev') != 'enp1s0':
            continue
        # Kernel creates this multicast route even on a reserved addressless link.
        if not (row.get('type') == 'multicast' and row.get('dst') == 'ff00::/8'
                and str(row.get('table')) in ('local', '255')
                and row.get('protocol') == 'kernel' and 'gateway' not in row
                and row.get('metric') == 256 and not row.get('flags')):
            return False
    return True


def link_route(link, destination):
    rows = ip('-4', 'route', 'get', destination)
    if len(rows) != 1:
        return False
    row = rows[0]
    return (row.get('dev') == link['interface'] and row.get('gateway') == link['gateway']
            and row.get('prefsrc') == link['address'] and row.get('table', 'main') in ('main', 254, '254'))


def transport_peers(link):
    output = run(['/usr/bin/ss', '-4Htnp', 'state', 'established'], 5).stdout
    peers = []
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 5 or '"windscribewstun"' not in line:
            continue
        source, peer = fields[2], fields[3]
        if source.rsplit(':', 1)[0] != link['address'] or not peer.endswith(':443'):
            continue
        address = str(ipaddress.IPv4Address(peer.rsplit(':', 1)[0]))
        if link_route(link, address):
            peers.append(address)
    return peers


def connected(link, exact_endpoint=True):
    fields = status()
    expected = meta()
    if (fields.get('Connect state', '').removesuffix(' [Network interference]') != 'Connected: ' + expected['location']
            or fields.get('Protocol', '').lower() != 'stealth:443'
            or fields.get('VPN IP') != expected['static_ip']
            or fields.get('Firewall state') != 'Always On'
            ):
        return False
    peers = transport_peers(link)
    if not peers or (exact_endpoint and peers != [expected['endpoint']]):
        return False
    for url in ('https://api.ipify.org', 'https://ipv4.icanhazip.com'):
        p = run(['/usr/bin/curl', '--interface', 'tun0', '--ipv4', '--noproxy', '*',
                 '--proto', '=https', '--connect-timeout', '4', '--max-time', '8',
                 '--silent', '--fail', url], 10, False)
        if p.returncode == 0 and p.stdout.strip() == expected['static_ip']:
            return True
    return False


def connect(link, exact_endpoint=True):
    destination = meta()['endpoint'] if exact_endpoint else '1.1.1.1'
    if not disconnected() or not link_route(link, destination):
        raise RuntimeError('No verified disconnected uplink route')
    p = cli('connect', '-n', 'static', meta()['static_ip'], 'stealth:443')
    if p.returncode:
        raise RuntimeError('Static connection request failed')
    wait_for(lambda: connected(link, exact_endpoint), 100)


def pause_policy(force=False):
    systemctl('stop', *TIMERS)
    if force:
        systemctl('stop', *SERVICES, timeout=30)
    # Acquisition waits for an idle pass; rollback stops it before explicit repair.
    for unit in SERVICES:
        if systemctl('show', unit, '-p', 'ActiveState', '--value').stdout.strip() not in ('inactive', 'failed'):
            raise RuntimeError('Policy pass still active; wait for it before retrying')


def hashes():
    # Reject added/removed networkd inputs as well as edits before global reload.
    expected = json.loads((BASE / 'network-inputs.json').read_text())
    found = set()
    for root in ('/etc/systemd/network', '/run/systemd/network', '/usr/lib/systemd/network',
                 '/etc/systemd/networkd.conf.d', '/run/systemd/networkd.conf.d',
                 '/usr/lib/systemd/networkd.conf.d'):
        folder = Path(root)
        if folder.exists():
            found.update(str(p) for p in folder.rglob('*') if p.is_file() and p != PROFILE and not p.name.endswith('.new'))
    if Path('/etc/systemd/networkd.conf').is_file():
        found.add('/etc/systemd/networkd.conf')
    if sorted(found) != expected:
        raise RuntimeError('Networkd input inventory changed')
    # Manifest is frozen during root-local staging; contains no credential bytes.
    safe(BASE / 'protected.json')
    manifest = json.loads((BASE / 'protected.json').read_text())
    for name, digest in manifest.items():
        path = Path(name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Protected input changed: ' + name)


def armed():
    if (BASE / 'rollback-started').exists():
        raise RuntimeError('Rollback has closed apply admission')
    data = meta()
    if data['boot'] != boot() or not (BASE / 'pending').exists():
        raise RuntimeError('Trial is not armed for this boot')
    if time.time() >= data['deadline'] - 300:
        raise RuntimeError('Insufficient time before local rollback')
    if systemctl('is-active', 'printing-uplink-rollback.timer', check=False).stdout.strip() != 'active':
        raise RuntimeError('Independent rollback timer is not active')


def arm():
    if (BASE / 'pending').exists() or meta()['boot']:
        raise RuntimeError('One attempt only; preserve evidence and restage before another')
    hashes()
    if not absent():
        raise RuntimeError('Native is not reserved')
    data = meta()
    data.update(boot=boot(), deadline=time.time() + 1500)
    write(BASE / 'trial.json', (json.dumps(data) + '\n').encode())
    RUNTIME.mkdir(mode=0o755, exist_ok=True)
    RUNTIME.chmod(0o755)
    safe(RUNTIME, True)
    timer = Path('/run/systemd/system/printing-uplink-rollback.timer')
    timer.parent.mkdir(mode=0o755, exist_ok=True)
    try:
        write(timer, b'[Unit]\nDescription=Independent native trial recovery deadline\n'
              b'[Timer]\nOnActiveSec=25min\nAccuracySec=1s\nUnit=printing-uplink-rollback.service\n', 0o644)
        systemctl('daemon-reload')
        systemctl('start', 'printing-uplink-rollback.timer')
        marker('pending')
        armed()
        write(RUNTIME / 'trial-permit', b'one boot only\n')
    except Exception:
        (RUNTIME / 'trial-permit').unlink(missing_ok=True)
        (BASE / 'pending').unlink(missing_ok=True)
        systemctl('stop', 'printing-uplink-rollback.timer', check=False)
        raise
    print('Rollback begins at ' + time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(data['deadline'])), flush=True)


def acquire():
    armed()
    hashes()
    pause_policy()
    native = load_native()
    links = native.uplink_status()
    if not absent() or not links['wifi'] or links['blocked']:
        raise RuntimeError('Reserved native and usable Wi-Fi required')
    if not connected(links['wifi']):
        raise RuntimeError('Baseline static tunnel is not verified on Wi-Fi')
    with operation():
        # Persistent boot guard restores these before networkd or Windscribe.
        write(POLICY, (BASE / 'new-policy.py').read_bytes(), 0o755)
        write(PROFILE, (BASE / '05-native-uplink.network').read_bytes(), 0o644)
        config(True)
    systemctl('daemon-reload')
    run(['/usr/bin/networkctl', 'reload'], 15)
    run(['/usr/bin/networkctl', 'reconfigure', 'enp1s0'], 15)
    systemctl('start', NATIVE)
    wait_for(lambda: native.uplink_status()['native'] is not None, 100)
    marker('acquired')


def preserve():
    armed()
    hashes()
    with operation() as native:
        before = native.uplink_status()
        if before['native'] is None:
            raise RuntimeError('No eligible native lease')
        a = ip('-4', 'address', 'show', 'dev', 'enp1s0')[0]['addr_info']
        routes = ip('-4', 'route', 'show', 'table', 'all')
        owned_routes = [r for r in routes if r.get('dev') == 'enp1s0']
        start = time.monotonic()
        run(['/usr/bin/networkctl', 'reconfigure', 'enp1s0'], 2)
    time.sleep(1.2)  # Let queued callbacks take their short lock between observations.
    with operation():
        after = native.uplink_status()
        b = ip('-4', 'address', 'show', 'dev', 'enp1s0')[0]['addr_info']
        later_routes = [r for r in ip('-4', 'route', 'show', 'table', 'all') if r.get('dev') == 'enp1s0']
        if len(a) != 1 or len(b) != 1 or before['native'] != after['native'] or owned_routes != later_routes:
            raise RuntimeError('Native resources changed during reconfiguration')
        for key in ('valid_life_time', 'preferred_life_time'):
            if not 0 < b[0][key] < a[0][key] or a[0][key] - b[0][key] > time.monotonic() - start + 3:
                raise RuntimeError('Finite lifetime did not continue decreasing')
    marker('preserved')


def cutover():
    armed()
    hashes()
    pause_policy()
    if not (BASE / 'preserved').exists():
        raise RuntimeError('Preservation has not passed')
    native = load_native()
    links = native.uplink_status()
    if links['native'] is None or links['blocked']:
        raise RuntimeError('No eligible native lease')
    disconnect()
    links = native.uplink_status()
    if links['native'] is None or links['blocked']:
        raise RuntimeError('Native changed during disconnect')
    connect(links['native'])
    if native.uplink_status()['native'] != links['native']:
        raise RuntimeError('Native changed during static connection')
    marker('native-connected')


def stopped(unit):
    if systemctl('show', unit, '-p', 'LoadState', '--value').stdout.strip() == 'not-found':
        return True
    state = systemctl('show', unit, '-p', 'ActiveState', '--value').stdout.strip()
    group = systemctl('show', unit, '-p', 'ControlGroup', '--value').stdout.strip()
    if group:
        events = Path('/sys/fs/cgroup') / group.lstrip('/') / 'cgroup.events'
        if events.exists() and 'populated 1' in events.read_text():
            return False
    return state in ('inactive', 'failed')


def stop_apply():
    unit = 'printing-uplink-apply.service'
    if systemctl('show', unit, '-p', 'LoadState', '--value').stdout.strip() != 'not-found':
        systemctl('stop', unit, timeout=25, check=False)
    if not stopped(unit):
        raise RuntimeError('Apply unit has not stopped')


def stop_native():
    (RUNTIME / 'trial-permit').unlink(missing_ok=True)
    try:
        with operation():
            config(False)
    except (OSError, RuntimeError, TimeoutError):
        print('Revocation incomplete; stopping client before retry', flush=True)
    # A lock failure must never suppress cgroup shutdown; no lock is held here.
    systemctl('stop', NATIVE, timeout=230, check=False)
    if not stopped(NATIVE):
        raise RuntimeError('Native client/cgroup has not stopped')
    with operation():
        config(False)


def cleanup_native():
    run(['/usr/bin/python3', '-IB', str(HELPER / 'native-uplink'), 'stop'], 70)
    if not absent():
        raise RuntimeError('Unexpected native resources remain; retaining profile and evidence')


def restore_files():
    write(CONFIG, (BASE / 'disabled.json').read_bytes())
    write(POLICY, (BASE / 'old-policy.py').read_bytes(), 0o755)
    PROFILE.unlink(missing_ok=True)
    fd = os.open(PROFILE.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def boot_reset():
    # Runs BEFORE networkd/helper/user-manager; no CLI, lock, or network wait.
    if not (BASE / 'pending').exists() or meta()['boot'] == boot():
        return
    restore_files()
    marker('boot-reset')


def restore_automation():
    # Used only after verified native absence and restoration of baseline files.
    systemctl('start', *TIMERS)
    (BASE / 'pending').unlink(missing_ok=True)


def resume_matching_policy():
    # Preserve retry admission while allowing the native-aware policy to run.
    # Never authorize a different/older policy over remaining native resources.
    if POLICY.read_bytes() != (BASE / 'new-policy.py').read_bytes():
        (RUNTIME / 'policy-permit').unlink(missing_ok=True)
        raise RuntimeError('Cannot resume a policy that differs from the native snapshot')
    write(RUNTIME / 'policy-permit', b'matching policy after rejected rollback\n')
    systemctl('start', *TIMERS)


def recover_wifi(native):
    wait_for(lambda: (native.uplink_status()['wifi'] is not None
                     and status().get('Login state') == 'Logged in'), 150)
    links = native.uplink_status()
    if not absent() or not links['wifi'] or links['blocked']:
        raise RuntimeError('Wi-Fi recovery route is unavailable')
    if not connected(links['wifi'], exact_endpoint=False):
        disconnect()
        connect(links['wifi'], exact_endpoint=False)


def rollback():
    if not (BASE / 'pending').exists():
        return
    marker('rollback-started')
    stop_apply()
    # Drift must reject rollback before it disables working automation. Pending
    # also gates policy units, so explicitly release only the matching policy.
    try:
        hashes()
    except (RuntimeError, OSError, ValueError):
        resume_matching_policy()
        raise
    (RUNTIME / 'trial-permit').unlink(missing_ok=True)
    (RUNTIME / 'policy-permit').unlink(missing_ok=True)
    pause_policy(force=True)
    native = load_native()
    try:
        disconnect()
    except (RuntimeError, OSError, subprocess.SubprocessError):
        print('Initial disconnect incomplete; stopping native before retry', flush=True)
    stop_native()
    if not disconnected():
        disconnect()
    # Retry supported disconnect BEFORE final cleanup: it may remove an unexpected
    # Windscribe pin that correctly prevented ExecStopPost's last-address deletion.
    cleanup_native()
    with operation():
        restore_files()
    hashes()
    run(['/usr/bin/networkctl', 'reload'], 15)
    run(['/usr/bin/networkctl', 'reconfigure', 'enp1s0'], 15)
    if not absent():
        raise RuntimeError('Native resources appeared after reserved restoration')
    if (BASE / 'native-link-down').exists():
        restore_link()
    marker('baseline-restored')
    try:
        recover_wifi(native)
        hashes()
    finally:
        # A transient provider/CLI failure must not permanently suppress the old
        # Wi-Fi policy after native resources and candidate files are gone.
        restore_automation()
        systemctl('stop', 'printing-uplink-rollback.timer', check=False)
    marker('rollback-complete')


def boot_recover():
    if not (BASE / 'pending').exists() or meta()['boot'] == boot():
        return
    native = load_native()
    if not absent() or PROFILE.exists():
        raise RuntimeError('Native baseline was not restored at boot')
    if (CONFIG.read_bytes() != (BASE / 'disabled.json').read_bytes()
            or POLICY.read_bytes() != (BASE / 'old-policy.py').read_bytes()):
        raise RuntimeError('Boot baseline files differ')
    try:
        recover_wifi(native)
    finally:
        restore_automation()
    marker('rollback-complete')


def restore_link():
    links = ip('link', 'show', 'dev', 'enp1s0')
    if len(links) != 1 or links[0].get('address') != '00:48:54:21:66:96':
        raise RuntimeError('Native identity changed during carrier test')
    run(['/usr/sbin/ip', 'link', 'set', 'dev', 'enp1s0', 'up'], 3)


def policy_enable():
    armed()
    native = load_native()
    links = native.uplink_status()
    if not links['native'] or links['blocked'] or not connected(links['native']):
        raise RuntimeError('Native static tunnel is not verified')
    if POLICY.read_bytes() != (BASE / 'new-policy.py').read_bytes():
        raise RuntimeError('Policy does not match native helper integration')
    write(RUNTIME / 'policy-permit', b'matching policy live trial\n')
    systemctl('start', *TIMERS)
    marker('policy-enabled')


def carrier_fallback():
    armed()
    if not (BASE / 'policy-enabled').exists() or not (RUNTIME / 'policy-permit').exists():
        raise RuntimeError('Matching policy must be enabled before fallback test')
    native = load_native()
    links = native.uplink_status()
    if not links['native'] or not connected(links['native']):
        raise RuntimeError('Carrier test requires verified native transport')
    with operation():
        marker('native-link-down')
        run(['/usr/sbin/ip', 'link', 'set', 'dev', 'enp1s0', 'down'], 3)
    wait_for(absent, 25)
    wait_for(lambda: (native.uplink_status()['wifi'] is not None
                     and connected(native.uplink_status()['wifi'], exact_endpoint=False)), 330)
    marker('wifi-fallback')


def carrier_return():
    armed()
    if not (BASE / 'wifi-fallback').exists() or not absent():
        raise RuntimeError('Verified Wi-Fi fallback is required before link return')
    with operation():
        restore_link()
    native = load_native()
    wait_for(lambda: native.uplink_status()['native'] is not None, 100)
    wait_for(lambda: connected(native.uplink_status()['native']), 100)
    marker('carrier-return')


def accept_live():
    armed()
    hashes()
    for name in ('preserved', 'wifi-fallback', 'carrier-return', 'external-native-ssh', 'external-wifi-ssh'):
        if not (BASE / name).exists():
            raise RuntimeError('Missing live acceptance evidence: ' + name)
    native = load_native()
    links = native.uplink_status()
    if not links['native'] or links['blocked'] or not connected(links['native']):
        raise RuntimeError('Native static connection is not verified for acceptance')
    if POLICY.read_bytes() != (BASE / 'new-policy.py').read_bytes():
        raise RuntimeError('Matching policy is not installed')
    # Commit acceptance only after every checked systemd operation succeeds.
    # main() requests rollback on any failure while pending still exists.
    systemctl('start', *TIMERS)
    systemctl('stop', 'printing-uplink-rollback.timer')
    marker('live-accepted')
    (BASE / 'pending').unlink()
    # Boot enablement remains separately controlled. Keep all snapshots/helpers.


def main():
    if os.geteuid() != 0 or Path(__file__) != SELF:
        raise SystemExit('Trial requires its reviewed root-owned installation')
    mode = sys.argv[1] if len(sys.argv) == 2 else ''
    if mode in ('boot-reset', 'boot-recover') and not (BASE / 'pending').exists():
        return
    for path in (SELF.parent, *SELF.parent.parents, BASE, *BASE.parents):
        safe(path, True)
    safe(SELF)
    names = ('trial.json', 'old-policy.py', 'disabled.json') if mode == 'boot-reset' else (
        'trial.json', 'protected.json', 'old-policy.py', 'new-policy.py',
        '05-native-uplink.network', 'disabled.json', 'network-inputs.json')
    for name in names:
        safe(BASE / name)
    mode = sys.argv[1] if len(sys.argv) == 2 else ''
    actions = {'arm': arm, 'acquire': acquire, 'preserve': preserve, 'cutover': cutover,
               'rollback': rollback, 'boot-reset': boot_reset, 'boot-recover': boot_recover,
               'policy-enable': policy_enable, 'carrier-fallback': carrier_fallback,
               'carrier-return': carrier_return, 'accept-live': accept_live}
    if mode not in actions:
        raise SystemExit('Unknown trial operation')
    try:
        actions[mode]()
    except Exception as error:
        if mode == 'rollback':
            try:
                native = load_native()
                links = native.uplink_status()
                if absent() and not links['blocked'] and links['wifi'] and disconnected():
                    # Availability rescue remains route/eligibility checked. Never
                    # blindly connect through unknown native resources.
                    connect(links['wifi'], exact_endpoint=False)
            except Exception:
                print('Bounded Wi-Fi rescue did not verify a tunnel', flush=True)
        if mode in ('acquire', 'preserve', 'cutover', 'policy-enable', 'carrier-fallback', 'carrier-return', 'accept-live'):
            systemctl('start', '--no-block', 'printing-uplink-rollback.service', check=False)
        marker(mode + '-failed')
        print(type(error).__name__ + ': ' + str(error), flush=True)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
