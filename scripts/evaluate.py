#!/usr/bin/env python3
"""Offline qualification: source fidelity, dependencies, and firmware provenance."""
import argparse, hashlib, json, re, struct, subprocess, sys, tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PINS={'moergo-rmk':'6638852adf1bd6a82b9abdf2b88de5deda90f798','rynkbench':'6c04eb12fb6e3032ec4b627dfc4ab7eb3a6e78c1'}
def require(ok, message):
    if not ok: raise ValueError(message)
def mapping():
    text=(ROOT/'dependencies/moergo-rmk/crates/moergo-config/src/moergo/mod.rs').read_text()
    table=re.search(r'MOERGO_TO_MATRIX: \[usize; 80\] = \[(.*?)\];',text,re.S)[1]
    return list(map(int,re.findall(r'\d+',re.sub(r'//[^\n]*','',table))))
def fidelity(config):
    source=json.loads((ROOT/'backups/original/source-layout.json').read_text())
    aliases=dict(zip('EQUAL MINUS BSLH FSLH LSHFT RSHFT LCTRL RCTRL LGUI RALT LALT SPACE RET BSPC SEMI SQT GRAVE LEFT RIGHT DOWN UP PG_UP PG_DN LBKT RBKT PSCRN PRINTSCREEN PAUSE_BREAK C_BRI_DN C_BRI_UP C_MUTE C_VOL_DN C_VOL_UP C_PREV C_PP C_NEXT UP_ARROW LEFT_ARROW DOWN_ARROW RIGHT_ARROW KP_NUM KP_EQUAL KP_SLASH KP_MULTIPLY KP_MINUS SCROLLLOCK KP_PLUS K_APP CAPS INS KP_ENTER KP_DOT'.split(),'EQL MINS BSLS SLSH LSFT RSFT LCTL RCTL LGUI RALT LALT SPC ENT BSPC SCLN QUOT GRV LEFT RGHT DOWN UP PGUP PGDN LBRC RBRC PSCR PSCR PAUS BRID BRIU MUTE VOLD VOLU MPRV MPLY MNXT UP LEFT DOWN RGHT NUM PEQL PSLS PAST PMNS SCRL PPLS APP CAPS INS PENT PDOT'.split()))
    aliases['COMMA'] = 'COMM'
    def key(k):
        v=k['value']
        if v in ('LS','LG'):return {'LS':'LSFT','LG':'LGUI'}[v]+'('+key(k['params'][0])+')'
        if re.fullmatch('N[0-9]',v):v=v[1:]
        elif re.fullmatch('KP_N[0-9]',v):v='P'+v[-1]
        return 'KC_'+aliases.get(v,v)
    def action(k):
        v=k['value'];p=k.get('params',[])
        if v=='&kp':return key(p[0])
        if v=='&to':return f'TO({p[0]["value"]})'
        return {'&none':'--','&trans':'KC_TRNS','&magic':'MO(2)','&lower':'MO(1)'}[v]
    index=mapping();holds=0
    for layer in (0,1,3):
        keys=config['layer'][layer]['keys'].split()
        for i,k in enumerate(source['layers'][layer]):
            actual=keys[index[i]]
            if k['value']=='&mt':
                n=re.fullmatch(r'TD\((\d+)\)',actual)
                require(n is not None,f'Base position {i}: missing tap/hold')
                morse=config['morse'][int(n[1])]
                require((morse['tap'],morse['hold'])==(key(k['params'][1]),key(k['params'][0])),f'Base position {i}: changed tap/hold outputs')
                holds+=1
            else:require(actual==action(k),f'{source["layer_names"][layer]} position {i}: {actual} != {action(k)}')
    combos=config['combo']; require(len(combos)==2,'Expected two scoped Gaming toggles')
    require({x['layer'] for x in combos}=={0,3},'Gaming toggle layer scopes changed')
    positions=[list(divmod(index[i],14)) for i in (51,68)]
    require(all(x['positions']==positions and x['output']=='TG(3)' for x in combos),'Gaming toggle moved')
    require(config['behavior']['combo_timeout_ms']==50,'Gaming combo timing changed')
    firmware=tomllib.loads((ROOT/'config/firmware.toml').read_text())
    leds={tuple(x['key']):x['id'] for x in firmware['lighting']['emitter']}
    original=re.findall(r'&ug 0x([0-9a-fA-F]{6})',source['custom_devicetree'])[80:160]
    expected={leds[divmod(index[i],14)]:'#'+rgb.lower() for i,rgb in enumerate(original) if int(rgb,16)}
    require({x['led']:x['color'] for x in config['lighting']['scene']}==expected,'Lower highlight colors or physical positions changed')
    require(all(x['layer']==1 for x in config['lighting']['scene']),'Highlights leak onto another layer')
    return f'240 source positions matched: Base, Lower, Gaming; {holds} tap/hold outputs; toggle positions and 50 ms scope; eight original-intensity Lower highlights.'

def artifacts():
    bundle=ROOT/'artifacts/current'
    if not bundle.exists(): bundle=ROOT/'artifacts/initial-trial'
    if not (bundle/'manifest.json').exists(): return ['no local trial bundle; build-firmware creates fresh images']
    manifest=json.loads((bundle/'manifest.json').read_text())
    compiled=tomllib.loads((ROOT/'config/firmware.toml').read_text())
    canonical=hashlib.sha256(json.dumps(compiled,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    require(canonical==manifest['configurationHashes']['canonical'],'Images are stale for config/firmware.toml; rebuild firmware')
    require(manifest['source']['commit']==PINS['moergo-rmk'],'Images use another firmware revision')
    if bundle.name=='current': require(not manifest['source']['dirty'],'Current images came from a modified firmware tree')
    results=[]
    for a in manifest['artifacts']:
        info=a['uf2'];data=(bundle/info['file']).read_bytes()
        require(hashlib.sha256(data).hexdigest()==info['sha256'],'UF2 checksum mismatch')
        family=int(info['familyId'],16);addresses=[]
        require(len(data)%512==0,'Truncated UF2')
        count=len(data)//512
        for i in range(count):
            block=data[i*512:(i+1)*512]; magic1,magic2,flags,address,size,number,total,fam=struct.unpack_from('<8I',block)
            require((magic1,magic2)==(0x0a324655,0x9e5d5157) and struct.unpack_from('<I',block,508)[0]==0x0ab16f30,'Invalid UF2 magic')
            require(flags&0x2000 and fam==family and number==i and total==count and 0<size<=476,'Invalid UF2 block')
            require(0x26000<=address and address+size<=0xdc000,'UF2 outside application partition')
            addresses.append((address,address+size))
        require(len(set(addresses))==count,'Duplicate UF2 blocks')
        results.append(f'{a["half"]}: {count} blocks, family {family:#x}, checksum and application range valid')
    return results

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--status',action='store_true');parser.add_argument('--migration',action='store_true');args=parser.parse_args()
    config=tomllib.loads((ROOT/'config/runtime.toml').read_text())
    lock=json.loads((ROOT/'flake.lock').read_text())
    require(lock['nodes']['firmware']['locked']['rev']==PINS['moergo-rmk'], 'Flake firmware pin differs from the reviewed submodule pin')
    require(len(config['layer'])<=16 and all(len(x['keys'].split())==84 for x in config['layer']),'Invalid layer dimensions')
    for name,pin in PINS.items():
        actual=subprocess.check_output(['git','-C',str(ROOT/'dependencies'/name),'rev-parse','HEAD'],text=True).strip()
        require(actual==pin,f'{name}: unreviewed dependency change')
        dirty=subprocess.check_output(['git','-C',str(ROOT/'dependencies'/name),'status','--porcelain'],text=True)
        require(not dirty,f'{name}: upstream source has local changes')
    nested=subprocess.check_output(['git','-C',str(ROOT/'dependencies/moergo-rmk'),'submodule','status','--recursive'],text=True)
    require(all(line.startswith(' ') for line in nested.splitlines()),'Nested firmware dependencies are not initialized at their pins')
    print('PASS: runtime structure and pinned firmware/editor revisions')
    if args.migration:print('PASS:',fidelity(config))
    for result in artifacts():print('PASS:',result)
    if args.status:
        print('Editor:', 'ready; run ./keyboard edit' if (ROOT/'.cache/editor/dist/index.html').exists() else 'first ./keyboard edit will build it')
        print('Device sync:', 'recorded; apply checks for intervening device edits' if (ROOT/'backups/last-synced.toml').exists() else 'not yet performed')
        print('Hardware qualification: pending; USB typing, BLE, sleep/wake, power-cycle, RGB and battery must be measured.')
        print('First-install prerequisite: a known-working ZMK rollback UF2; see docs/first-install.md.')
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError) as e:print(f'FAIL: {e}',file=sys.stderr);sys.exit(1)
