#!/usr/bin/python3 -IB
"""Boot validation and bounded Wi-Fi fallback for the accepted native uplink."""
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

SELF = Path('/usr/local/libexec/printing-station/uplink-boot.py')
CONTROLLER = SELF.with_name('uplink-trial.py')
BASE = Path('/var/lib/printing-station/rollback/native-uplink-trial')
SNAPSHOT = BASE / 'boot-baseline'
WAIT_ONLINE = Path('/etc/systemd/system/systemd-networkd-wait-online.service.d/printing-station.conf')
BOOT_EVIDENCE = Path('/usr/local/libexec/printing-station/boot-evidence')
NATIVE = 'printing-native-uplink.service'


def controller():
    for p in (CONTROLLER, SELF):
        i=p.lstat()
        if i.st_uid != 0 or i.st_mode & 0o022 or not stat.S_ISREG(i.st_mode):
            raise RuntimeError('Unsafe boot recovery source')
    for p in (SELF.parent, *SELF.parent.parents, BASE, *BASE.parents):
        i=p.lstat()
        if i.st_uid != 0 or i.st_mode & 0o022 or not stat.S_ISDIR(i.st_mode):
            raise RuntimeError('Unsafe boot recovery directory')
    spec=importlib.util.spec_from_file_location('trial',CONTROLLER)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ready(t):
    # networkd READY does not mean its first native-link configuration is done.
    # DHCP is permitted even with the cable absent, once the link is admin-up.
    def configured():
        links=t.ip('link','show','dev','enp1s0')
        profile=json.loads(t.run(['/usr/bin/networkctl','--json=short','status','enp1s0'],5).stdout)
        return (profile.get('AdministrativeState') in ('configuring','configured')
                and profile.get('NetworkFile')==str(t.PROFILE)
                and len(links)==1 and links[0].get('address')=='00:48:54:21:66:96'
                and 'UP' in links[0].get('flags',[]) and t.absent())
    t.wait_for(configured,50)


def healthy(t):
    links=t.load_native().uplink_status()
    if links['blocked']:
        return None
    for link in (links['native'],links['wifi']):
        if link and t.connected(link,exact_endpoint=link['interface']=='enp1s0'):
            return link['interface']
    return None


def check(t):
    link=None
    def verified():
        nonlocal link
        link=healthy(t)
        return link is not None
    t.wait_for(verified,300)
    if not (BASE/'boot-enabled').exists() or (BASE/'boot-fallback').exists():
        raise RuntimeError('Boot acceptance revoked during verification')
    t.RUNTIME.mkdir(mode=0o755,exist_ok=True)
    t.write(t.RUNTIME/'boot-verified',(link+'\n').encode())
    t.marker('boot-verified')
    print('Verified boot transport: '+link,flush=True)


def remove_marker(name):
    (BASE/name).unlink(missing_ok=True)
    fd=os.open(BASE,os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def fallback(t):
    enabled=(BASE/'boot-enabled').exists()
    if not enabled and not (BASE/'boot-fallback-pending').exists():
        return
    # Only this systemd service runs recovery. The permanent audit marker also
    # denies native starts/checks if a reset interrupts the queue/unlink window.
    t.marker('boot-fallback')
    t.marker('boot-fallback-pending')
    if enabled:
        t.marker('pending')
        # Queue proven rollback before optional file restoration can fail.
        # Failed submission retains enablement for a bounded retry. Once queued,
        # retries only finish preparation and never recreate rollback's pending.
        t.systemctl('start','--no-block','printing-uplink-rollback.service')
        remove_marker('boot-enabled')
    t.systemctl('disable','--no-reload',NATIVE)
    t.safe(SNAPSHOT,True)
    for target,name,mode in ((WAIT_ONLINE,'wait-online.conf',0o644),
                             (BOOT_EVIDENCE,'boot-evidence',0o755)):
        t.safe(SNAPSHOT/name)
        t.write(target,(SNAPSHOT/name).read_bytes(),mode)
    t.systemctl('daemon-reload',timeout=15)
    remove_marker('boot-fallback-pending')


def watchdog(t):
    if ((BASE/'boot-fallback-pending').exists()
            or ((BASE/'boot-enabled').exists() and not (t.RUNTIME/'boot-verified').exists())):
        # Stop an overdue checker before revocation; systemd serializes recovery.
        t.systemctl('stop','printing-uplink-boot-check.service',timeout=15)
        t.systemctl('start','--no-block','printing-uplink-boot-fallback.service')


def main():
    if os.geteuid()!=0 or Path(__file__)!=SELF or len(sys.argv)!=2:
        raise SystemExit('Boot controller requires its reviewed root installation')
    t=controller()
    mode=sys.argv[1]
    try:
        if mode=='ready': ready(t)
        elif mode=='check': check(t)
        elif mode=='watchdog': watchdog(t)
        elif mode=='fallback': fallback(t)
        else: raise ValueError('Unknown boot operation')
    except Exception as error:
        print(type(error).__name__+': '+str(error),flush=True)
        if mode=='check':
            # OnFailure is independent if this process is killed by systemd.
            t.systemctl('start','--no-block','printing-uplink-boot-fallback.service',check=False)
        raise SystemExit(1) from None


if __name__=='__main__':
    main()
