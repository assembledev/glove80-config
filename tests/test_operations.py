import importlib.util, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
spec = importlib.util.spec_from_file_location('manage', Path(__file__).resolve().parents[1] / 'scripts/manage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
DOC = b'default_layer = 0\n'
class Fake(m.Project):
    def __init__(self, root):
        super().__init__(root); self.calls=[]; self.fail=None; self.device=DOC
    def run(self,*args):
        self.calls.append(args)
        if self.fail and self.fail(args): raise m.Failure('simulated device error')
        command = args[args.index("config"):]
        if command == ('config','show'): return self.device
        if command[:2] == ('config','pull'):
            Path(command[2]).write_bytes(self.device)
        return b''
class Transactions(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); (self.root/'config').mkdir(); (self.root/'.cache').mkdir()
        self.p=Fake(self.root); self.p.config.write_bytes(DOC)
    def writes(self):
        return [x for x in self.p.calls if x[x.index('config'):][:2]==('config','apply') and '--dry-run' not in x]
    def test_save_is_validated_and_backed_up(self):
        new=b'default_layer = 1\n'; result=self.p.save(new,m.digest(DOC))
        self.assertEqual(self.p.config.read_bytes(),new)
        self.assertEqual(Path(result['backup']).read_bytes(),DOC)
        self.assertEqual(self.p.config.stat().st_mode & 0o777,0o600)
    def test_stale_editor_cannot_overwrite(self):
        with self.assertRaises(m.Failure):self.p.save(DOC,'stale')
        self.assertEqual(self.p.config.read_bytes(),DOC)
    def test_invalid_editor_input_preserves_project(self):
        with self.assertRaises(ValueError):self.p.save(b'invalid [',m.digest(DOC))
        self.assertEqual(self.p.config.read_bytes(),DOC)
    def test_semantic_validator_failure_preserves_project(self):
        self.p.fail=lambda a:a[:2]==('config','validate')
        with self.assertRaises(m.Failure):self.p.save(DOC,m.digest(DOC))
        self.assertEqual(self.p.config.read_bytes(),DOC)
    def test_first_apply_requires_explicit_replace(self):
        with self.assertRaises(m.Failure):self.p.apply()
        self.assertFalse(self.writes());self.assertFalse(self.p.baseline.exists())
        self.assertEqual(len(list((self.root/'backups').glob('*keyboard*'))),1)
    def test_external_device_edits_block_normal_apply(self):
        m.atomic(self.p.baseline,b'default_layer = 1\n')
        with self.assertRaises(m.Failure):self.p.apply()
        self.assertFalse(self.writes())
    def test_failed_preview_cannot_reach_write(self):
        self.p.fail=lambda a:'--dry-run' in a
        with self.assertRaises(m.Failure):self.p.apply(True)
        self.assertFalse(self.writes());self.assertFalse(self.p.baseline.exists())
    def test_disconnected_device_cannot_reach_write(self):
        self.p.fail=lambda a:a[a.index('config'):]==('config','show')
        with self.assertRaises(m.Failure):self.p.apply(True)
        self.assertFalse(self.writes())
    def test_failed_readback_does_not_mark_synced(self):
        self.p.fail=lambda a:a[a.index('config'):][:2]==('config','diff')
        with self.assertRaises(m.Failure):self.p.apply(True)
        self.assertTrue(self.writes());self.assertFalse(self.p.baseline.exists())
    def test_success_records_verified_baseline(self):
        self.p.apply(True);self.assertEqual(self.p.baseline.read_bytes(),DOC)
        self.assertEqual(len(self.writes()),1);self.assertIn('--exact',self.writes()[0])
    def test_pull_keeps_previous_project(self):
        self.p.device=b'default_layer = 1\n';self.p.pull()
        self.assertEqual(self.p.config.read_bytes(),self.p.device)
        self.assertEqual(self.p.baseline.read_bytes(),self.p.device)
        self.assertEqual(next((self.root/'backups').glob('*project*')).read_bytes(),DOC)
    def test_failed_pull_preserves_project(self):
        self.p.fail=lambda a:a[a.index('config'):][:2]==('config','pull')
        with self.assertRaises(m.Failure):self.p.pull()
        self.assertEqual(self.p.config.read_bytes(),DOC)
    def test_two_transactions_cannot_interleave(self):
        with self.p.lock():
            with self.assertRaises(m.Failure):self.p.save(DOC,m.digest(DOC))
    def test_format_only_change_is_not_device_conflict(self):
        self.assertEqual(m.semantic(b'default_layer=0 # comment\n'),m.semantic(DOC))

class EditorHTTP(unittest.TestCase):
    def test_static_server_exposes_no_project_or_write_api(self):
        import threading, http.client
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'.cache/editor/dist').mkdir(parents=True)
            (root/'.cache/editor/dist/index.html').write_text('editor')
            (root/'config').mkdir();(root/'config/runtime.toml').write_bytes(DOC)
            server=m.create_server(Fake(root))
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                for method,path,expected in [('GET','/',200),('GET','/api/config',404),('PUT','/api/config',501),('GET','/../../config/runtime.toml',404)]:
                    conn=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=3)
                    conn.request(method,path);response=conn.getresponse();response.read()
                    self.assertEqual(response.status,expected);conn.close()
                self.assertEqual((root/'config/runtime.toml').read_bytes(),DOC)
            finally:server.shutdown();server.server_close();thread.join()

class Transports(unittest.TestCase):
    setUp = Transactions.setUp
    writes = Transactions.writes
    def test_each_transport_covers_entire_apply_and_pull(self):
        for selector in ((), ('--usb',), ('--ble',), ('--ble','--device','AA:BB:CC:DD:EE:FF'), ('--device','/dev/hidraw9')):
            with self.subTest(selector=selector):
                self.p.selector=selector;self.p.calls=[]
                self.p.apply(True);self.p.pull();self.p.backup_device()
                device_calls=[a for a in self.p.calls if a[a.index('config'):][:2]!=('config','validate')]
                self.assertEqual(len(device_calls),8)
                self.assertTrue(all(a[:a.index('config')]==selector for a in device_calls))
                validations=[a for a in self.p.calls if a[a.index('config'):][:2]==('config','validate')]
                self.assertTrue(all(a[0]=='config' for a in validations))
    def test_ble_failure_does_not_retry_usb_or_write(self):
        self.p.selector=('--ble','--device','AA:BB:CC:DD:EE:FF')
        self.p.fail=lambda a:'--dry-run' in a
        with self.assertRaises(m.Failure):self.p.apply(True)
        self.assertFalse(self.writes())
        self.assertFalse(any('--usb' in a for a in self.p.calls))
        self.assertFalse(self.p.baseline.exists())
    def test_diff_preserves_selector_and_upstream_exit_status(self):
        self.p.selector=('--ble','--device','AA:BB:CC:DD:EE:FF')
        with patch.object(m.subprocess,'run') as run:
            run.return_value.returncode=1
            self.assertEqual(self.p.diff(),1)
            self.assertEqual(run.call_args.args[0], [*self.p.control,*self.p.selector,'config','diff',str(self.p.config)])
    def test_cli_routes_selector_to_all_device_commands(self):
        for command,method in [('apply','apply'),('pull','pull'),('backup','backup_device'),('diff','diff')]:
            with self.subTest(command=command), patch.object(m,'Project') as project:
                getattr(project.return_value,method).return_value=0
                m.main([command,'--ble','--device','AA:BB:CC:DD:EE:FF'])
                project.assert_called_once_with(selector=['--ble','--device','AA:BB:CC:DD:EE:FF'])
                getattr(project.return_value,method).assert_called_once()
    def test_cli_rejects_conflicting_transports(self):
        import contextlib,io
        for command in ('apply','pull','backup','diff'):
            with self.subTest(command=command), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:m.argument_parser().parse_args([command,'--ble','--usb'])
                self.assertEqual(error.exception.code,2)
    def test_cli_defaults_to_upstream_auto_selection(self):
        with patch.object(m,'Project') as project:
            m.main(['pull']);project.assert_called_once_with(selector=[])

if __name__=='__main__':unittest.main()
