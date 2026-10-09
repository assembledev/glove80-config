#!/usr/bin/env python3
"""Preprocess and check a keymap with the pinned ZMK headers, without a firmware build."""
import argparse
import re
import struct
import subprocess
import tempfile
from pathlib import Path


def cells(data):
    if len(data) % 4:
        raise ValueError("Device-tree property is not an array of 32-bit cells")
    return list(struct.unpack(f">{len(data) // 4}I", data))


def text(data):
    return data.rstrip(b"\0").decode()


def read_tree(data):
    """Read properties from the standard flattened device tree produced by dtc."""
    header = struct.unpack_from(">10I", data)
    if header[0] != 0xD00DFEED:
        raise ValueError("Invalid flattened device tree")
    strings = data[header[3]:header[3] + header[8]]
    offset = header[2]
    stack, nodes = [], {}
    while True:
        token = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        if token == 1:  # FDT_BEGIN_NODE
            end = data.index(b"\0", offset)
            stack.append(data[offset:end].decode())
            offset = (end + 4) & ~3
            nodes["/" + "/".join(stack[1:])] = {}
        elif token == 2:  # FDT_END_NODE
            stack.pop()
        elif token == 3:  # FDT_PROP
            size, name_offset = struct.unpack_from(">II", data, offset)
            offset += 8
            name_end = strings.index(b"\0", name_offset)
            name = strings[name_offset:name_end].decode()
            nodes["/" + "/".join(stack[1:])][name] = data[offset:offset + size]
            offset = (offset + size + 3) & ~3
        elif token == 4:  # FDT_NOP
            continue
        elif token == 9:  # FDT_END
            return nodes
        else:
            raise ValueError(f"Unknown device-tree token: {token}")


def compile_keymap(zmk, config):
    with tempfile.TemporaryDirectory(prefix="glove80-keymap-") as directory:
        source = Path(directory) / "keymap.dts"
        blob = Path(directory) / "keymap.dtb"
        source.write_text('/dts-v1/;\n#include "' + str((config / "glove80.keymap").resolve()) + '"\n')
        preprocessed = subprocess.check_output([
            "gcc", "-E", "-P", "-x", "assembler-with-cpp", "-nostdinc", "-undef",
            "-D__DTS__", "-isystem", str(zmk / "app/include"),
            "-isystem", str(zmk / "app/dts"), str(source),
        ])
        subprocess.run([
            "dtc", "-@", "-I", "dts", "-O", "dtb", "-o", str(blob), "-",
        ], input=preprocessed, check=True)
        return read_tree(blob.read_bytes())


def decode_bindings(nodes, data):
    phandles = {cells(p["phandle"])[0]: (path, p)
                for path, p in nodes.items() if "phandle" in p}
    values, decoded = cells(data), []
    while values:
        handle = values.pop(0)
        if handle not in phandles:
            raise ValueError(f"Unknown behavior phandle: {handle}")
        path, properties = phandles[handle]
        if "#binding-cells" not in properties:
            raise ValueError(f"{path}: reference is not a behavior")
        count = cells(properties["#binding-cells"])[0]
        if len(values) < count:
            raise ValueError(f"{path}: missing behavior arguments")
        decoded.append((path, values[:count]))
        del values[:count]
    return decoded


def validate(nodes, zmk):
    # The physical position order is owned by MoErgo's board, not a copied map.
    board = (zmk / "app/boards/arm/glove80/glove80.dtsi").read_text()
    positions = [(int(row), int(col)) for row, col in re.findall(r"RC\((\d+),(\d+)\)", board)]
    if len(positions) != 80 or len(set(positions)) != 80:
        raise ValueError("Unexpected Glove80 matrix transform")
    layers = [path for path in nodes if path.startswith("/keymap/")]
    if not layers or len(layers) > 32:
        raise ValueError("Invalid layer count")
    for path in layers:
        bindings = decode_bindings(nodes, nodes[path]["bindings"])
        if len(bindings) != len(positions):
            raise ValueError(f"{path}: expected 80 physical bindings, got {len(bindings)}")
        for target, arguments in bindings:
            compatible = text(nodes[target]["compatible"])
            if compatible in {"zmk,behavior-momentary-layer", "zmk,behavior-toggle-layer", "zmk,behavior-to-layer"}:
                if arguments[0] >= len(layers):
                    raise ValueError(f"{path}: out-of-range layer reference")
    for path, properties in nodes.items():
        if "bindings" not in properties or path in layers:
            continue
        compatible = text(properties.get("compatible", b""))
        if compatible == "zmk,behavior-hold-tap":
            handles = cells(properties["bindings"])
            phandles = {cells(p["phandle"])[0]: p for p in nodes.values() if "phandle" in p}
            if len(handles) != 2 or any(h not in phandles for h in handles):
                raise ValueError(f"{path}: invalid hold/tap behavior references")
            if any(cells(phandles[h]["#binding-cells"])[0] > 1 for h in handles):
                raise ValueError(f"{path}: hold/tap target accepts more than one parameter")
        else:
            decode_bindings(nodes, properties["bindings"])
        if path.startswith("/combos/"):
            keys = cells(properties["key-positions"])
            if len(keys) < 2 or len(set(keys)) != len(keys) or any(k >= 80 for k in keys):
                raise ValueError(f"{path}: invalid combo key positions")
            if any(layer >= len(layers) for layer in cells(properties.get("layers", b""))):
                raise ValueError(f"{path}: invalid combo layer scope")
    return len(layers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zmk", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    nodes = compile_keymap(args.zmk, args.config)
    count = validate(nodes, args.zmk)
    print(f"PASS: pinned ZMK headers, device-tree syntax, {count} × 80 bindings, behavior arguments and combo references")
    print("Firmware compilation and physical keyboard behaviour are not checked by this command.")


if __name__ == "__main__":
    main()
