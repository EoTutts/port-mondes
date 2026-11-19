"""Offline functional gate. Actual Engine and SDK dispatch; fake devices only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
PACKAGE = Path(os.environ.get('PORT_MONDES_TEST_PACKAGE', str(REPO/'base/port-mondes')))


def child(lang, display_mode='gui'):
    os.environ['A11Y_GAME_DIR'] = str(PACKAGE)
    os.environ['A11Y_LANG'] = lang
    if display_mode == 'headless':
        os.environ['PORT_MONDES_GRAPHICS']='0'
    sys.path.insert(0, str(PACKAGE/'sdk'))
    import main as candidate
    import r36s_a11y.game as sdk_module
    from r36s_a11y.input import InputState
    from r36s_a11y.buttons import BUTTON_CODES, FN_CODE
    events, frames, captures = [], [], {}
    class Sound:
        def __init__(self):
            self.sounds, self.voices, self.free = {}, {}, []
        def load(self, name, path):
            from r36s_a11y.audio import Sound as SDKSound
            sound = SDKSound(self, name, None, 1)
            self.sounds[name] = sound
            return sound
        def _play(self, *args, **kwargs):
            from r36s_a11y.audio import _NullVoice
            return _NullVoice()
        stream = load
        def update(self, dt): pass
        def close(self): pass
    sdk_module.Audio = lambda *args: Sound()
    class Speech:
        def __init__(self, **kw): self.language = kw['language']
        def say(self, text, **kw): events.append((self.language, text))
        def poll(self): return []
        def close(self): pass
        def set_language(self, language): self.language = language
    sdk_module.Speech = Speech
    class Display:
        def __init__(self):
            if display_mode=='failed': raise OSError('simulated SDL unavailable')
        def present(self, raw): frames.append(len(raw))
        def poll_quit(self): return False
        def close(self): pass
    import sdl_display
    sdl_display.Display = Display
    # Use Windows Pillow 3.8 rather than loading an ARM64 extension on PC.
    sys.path.insert(0, str(REPO/'out/port-mondes-interface-runtime/windows'))
    checks = []
    def check(name, value):
        assert value, name
        checks.append(name)
    original_run = sdk_module.Game.run
    def run(sdk):
        engine = candidate.legacy.GameAudio.engine
        captures['engine'] = engine
        check('A11Y language selected', engine.language == lang)
        check('startup logo', engine.mode == 'logo')
        engine.open_title()
        state = InputState()
        reverse = {name:code for code,name in BUTTON_CODES.items()}
        def push(button):
            for value in (1,0):
                for event in state.feed(1, reverse[button], value, 0): sdk._dispatch(event)
        push('b')
        check('SDK B opens menu', engine.mode == 'menu')
        push('b')
        check('SDK B opens adventure', engine.mode == 'adventure')
        push('down')
        check('SDK down selection', engine.position == 1)
        push('b')
        check('locked campaign remains locked', engine.mode=='adventure' and engine.position==1)
        push('up'); push('b')
        check('new adventure chooses a save slot', engine.host.screen.screen_kind=='save_slots')
        push('b')
        check('original Francois opening', engine.mode=='scene' and engine.host.screen is not None)
        before = (engine.mode, engine.position, engine.last_message)
        # Fn suppression comes from the real SDK, not the game adapter.
        for value,code in ((1,FN_CODE),(1,reverse['b']),(0,reverse['b']),(0,FN_CODE)):
            for event in state.feed(1,code,value,0): sdk._dispatch(event)
        check('Fn combo does not advance story', before==(engine.mode,engine.position,engine.last_message))
        push('select')
        check('repeat speaks current screen', bool(events[-1][1]))
        # Returned/held keys cannot run the original action a second time.
        count=len(events)
        sdk._dispatch(('button','b','up',0))
        check('button release ignored', len(events)==count)
        for fn in sdk._handlers['update']: fn(.033)
        check('SDL present or spoken fallback active',
              (len(frames)>0 and set(frames)=={614400}) if display_mode=='gui' else not frames)
        config=Path(os.environ['A11Y_SISTEMA_CONF'])
        config.write_text('SCREEN=0\n')
        for fn in sdk._handlers['update']: fn(.033)
        check('SCREEN zero disables rasterizer', not engine.graphics and engine.original_ui is None)
        count=len(frames);config.write_text('SCREEN=1\n')
        for fn in sdk._handlers['update']: fn(.033)
        check('SCREEN transition respects display availability',
            engine.graphics and len(frames)>count if display_mode=='gui' else
            (not engine.graphics if display_mode=='headless' else engine.graphics and not frames))
        check('speech uses selected language', all(language==lang for language,_ in events))
        slots = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in Path(sdk.save_dir).rglob('*.sav')}
        # Original initialization creates None placeholders; closing must not
        # convert those into a new save outside the original SaveUI path.
        for fn in sdk._handlers['quit']: fn()
        check('shutdown does not write saves', slots == {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
              for p in Path(sdk.save_dir).rglob('*.sav')})
        check('audio channels closed', engine.audio.closed.is_set())
        sdk.sound.close();sdk.speech.close()
    sdk_module.Game.run = run
    with tempfile.TemporaryDirectory(prefix='port-mondes-sdk-') as tmp:
        os.environ['A11Y_SAVE_DIR'] = tmp
        os.environ['A11Y_SISTEMA_CONF'] = str(Path(tmp)/'sistema.conf')
        candidate.main()
        check('runtime pending stopped', not captures['engine'].sound_queue.pending)
    print(json.dumps({'language':lang,'display_mode':display_mode,'checks':checks,'frame_count':len(frames),'speech_count':len(events)}))


if __name__ == '__main__':
    if len(sys.argv)>1:
        child(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'gui')
    else:
        results=[]
        for lang,mode in (('pt-BR','gui'),('en-US','gui'),('fr-FR','gui'),('pt-BR','headless'),('pt-BR','failed')):
            run=subprocess.run([sys.executable,__file__,lang,mode],capture_output=True,text=True,encoding='utf-8')
            if run.returncode:
                print(run.stderr);raise SystemExit(run.returncode)
            results.append(json.loads(run.stdout))
        output=Path(os.environ.get('PORT_MONDES_TEST_REPORT_DIR',
                                   str(REPO/'out/port-mondes-audit/integration/sdk-migration')))
        output.mkdir(parents=True,exist_ok=True)
        (output/'functional.json').write_text(json.dumps({'passed':True,'scope':'offline actual Engine and SDK input; mocked audio/speech/SDL devices','results':results},indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'passed':True,'cases':len(results),'checks':sum(len(r['checks']) for r in results)}))
