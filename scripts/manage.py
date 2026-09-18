#!/usr/bin/env python3
"""Project file transactions and device synchronization. No firmware flashing."""
import argparse, contextlib, fcntl, hashlib, http.server, os
from pathlib import Path
import secrets, subprocess, sys, tempfile, time, tomllib, webbrowser

ROOT = Path(__file__).resolve().parents[1]
class Failure(Exception): pass

def digest(data): return hashlib.sha256(data).hexdigest()
def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)

def semantic(data):
    obj = tomllib.loads(data.decode())
    for layer in obj.get('layer', []):
        layer.pop('name', None); layer.pop('id', None)
        layer['keys'] = layer['keys'].split()
    for table in ('morse', 'combo', 'macro'):
        for row in obj.get(table, []): row.pop('name', None)
    return obj

class Project:
    def __init__(self, root=ROOT, control=None, selector=()):
        self.root = Path(root)
        self.config = self.root / 'config/runtime.toml'
        self.control = control or [str(self.root / '.cache/bin/moergo-control')]
        self.selector = tuple(selector)
        self.baseline = self.root / 'backups/last-synced.toml'
    @contextlib.contextmanager
    def lock(self):
        (self.root / '.cache').mkdir(exist_ok=True)
        with (self.root / '.cache/operation.lock').open('w') as f:
            try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError: raise Failure('Another save or device operation is running. Try again when it finishes.')
            yield
    def run(self, *args):
        p = subprocess.run([*self.control, *map(str, args)], capture_output=True)
        if p.returncode:
            raise Failure((p.stderr or p.stdout).decode().strip() or 'Device command failed.')
        return p.stdout
    def run_device(self, *args):
        return self.run(*self.selector, *args)
    def validate(self, data):
        tomllib.loads(data.decode())
        fd, name = tempfile.mkstemp(suffix='.toml', dir=self.root / '.cache')
        try:
            with os.fdopen(fd, 'wb') as f: f.write(data)
            self.run('config', 'validate', name)
        finally: os.unlink(name)
    def backup(self, data, kind):
        path = self.root / 'backups' / (time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-' + kind + '-' + secrets.token_hex(3) + '.toml')
        atomic(path, data)
        return path
    def save(self, data, expected):
        with self.lock():
            old = self.config.read_bytes()
            if expected != digest(old): raise Failure('The project changed since this window opened. Download your edits, reopen the project, and merge them before saving.')
            self.validate(data)
            backup = self.backup(old, 'project')
            atomic(self.config, data)
            return {'revision': digest(data), 'backup': str(backup)}
    def live(self):
        data = self.run_device('config', 'show')
        self.validate(data)
        return data
    def backup_device(self):
        with self.lock():
            print(f'Backup: {self.backup(self.live(), "keyboard")}')
    def diff(self):
        # Upstream uses exit 1 for differences as well as failures; preserve
        # its output and status instead of interpreting it as write permission.
        return subprocess.run([*self.control, *self.selector, 'config', 'diff', str(self.config)]).returncode
    def pull(self):
        with self.lock():
            live = self.live()
            backup = self.backup(self.config.read_bytes(), 'project')
            # Upstream pull preserves file-owned layer labels using its template.
            fd, name = tempfile.mkstemp(suffix='.toml', dir=self.root / '.cache')
            try:
                with os.fdopen(fd, 'wb') as f: f.write(self.config.read_bytes())
                self.run_device('config', 'pull', name)
                data = Path(name).read_bytes(); self.validate(data)
                atomic(self.config, data)
                atomic(self.baseline, live)
            finally: os.unlink(name)
            print(f'Saved keyboard configuration to {self.config}\nPrevious project: {backup}')
    def apply(self, replace_live=False):
        with self.lock():
            data = self.config.read_bytes(); self.validate(data)
            live = self.live()
            backup = self.backup(live, 'keyboard')
            if not replace_live:
                if not self.baseline.exists():
                    raise Failure(f'First application: review with ./keyboard diff, then use ./keyboard apply --replace-live. Current keyboard saved: {backup}')
                if semantic(live) != semantic(self.baseline.read_bytes()):
                    raise Failure(f'The keyboard changed since the last sync. Use ./keyboard pull to keep those edits, or ./keyboard apply --replace-live to replace them. Backup: {backup}')
            # dry-run is a successful command with differences; unlike diff, a
            # nonzero exit here is unambiguously a failure and must stop writes.
            preview = self.run_device('config', 'apply', self.config, '--dry-run', '--exact')
            print(preview.decode().strip())
            print(self.run_device('config', 'apply', self.config, '--exact').decode().strip())
            self.run_device('config', 'diff', self.config, '--exact')
            atomic(self.baseline, self.live())
            print(f'Applied and read back successfully. Previous keyboard: {backup}')

def create_server(project):
    dist = project.root / '.cache/editor/dist'
    if not (dist / 'index.html').exists(): raise Failure('Editor is not built. Run ./keyboard build-editor once.')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(dist), **kwargs)
        def log_message(self, *_): pass
    return http.server.HTTPServer(('127.0.0.1', 0), Handler)

def serve(project, open_browser=True):
    server = create_server(project)
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Rynkbench: {url}\nOffline: choose Open file, then {project.config}\nAfter editing: Download TOML, then ./keyboard save PATH_TO_DOWNLOAD\nFor live edits: connect by USB or Bluetooth in the editor, then close it and run ./keyboard pull (or pull --ble).\nKeep this terminal open; Ctrl+C stops the editor.', flush=True)
    if open_browser: webbrowser.open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

def argument_parser():
    parser = argparse.ArgumentParser(description='Manage the personal Glove80 configuration.')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('pull', 'apply', 'diff', 'backup'):
        command = commands.add_parser(name)
        transport = command.add_mutually_exclusive_group()
        transport.add_argument('--usb', action='store_true', help='Require USB; do not fall back to BLE')
        transport.add_argument('--ble', action='store_true', help='Require Bluetooth; do not use USB')
        command.add_argument('--device', help='Select a USB hidraw path or full BLE address')
        if name == 'apply': command.add_argument('--replace-live', action='store_true')
    commands.add_parser('edit').add_argument('--no-browser', action='store_true')
    commands.add_parser('save').add_argument('file')
    return parser

def main(argv=None):
    args = argument_parser().parse_args(argv)
    selector = []
    if getattr(args, 'usb', False): selector.append('--usb')
    if getattr(args, 'ble', False): selector.append('--ble')
    if getattr(args, 'device', None): selector.extend(('--device', args.device))
    project = Project(selector=selector)
    try:
        if args.command == 'edit': serve(project, not args.no_browser)
        elif args.command == 'pull': project.pull()
        elif args.command == 'backup': project.backup_device()
        elif args.command == 'diff': return project.diff()
        elif args.command == 'apply': project.apply(args.replace_live)
        elif args.command == 'save':
            if not args.file: raise Failure('Usage: ./keyboard save DOWNLOADED.toml')
            print(project.save(Path(args.file).read_bytes(), digest(project.config.read_bytes())))
    except (Failure, OSError, ValueError) as e:
        print(f'Error: {e}', file=sys.stderr); return 1
    return 0
if __name__ == '__main__': sys.exit(main())
