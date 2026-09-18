import { readFileSync, writeFileSync } from "node:fs";
import { beforeAll, expect, it } from "vitest";
import { initSync as initConfig } from "./vendor/moergo-config-wasm/moergo_config_wasm";
import { initSync as initRynk } from "./vendor/rynk-wasm/rynk_wasm";
import { parseDocument, renderDocument } from "./config/document";
import { exportDocument } from "./config/transfer";
import { openOfflineGlove80, offlineGlove80Catalog } from "./session/offline/glove80";
import { openBundle } from "./ui/bundle";
import { initialWorkbenchState } from "./ui/state";
const root = process.env.GLOVE80_PROJECT_ROOT!;
const text = readFileSync(`${root}/config/runtime.toml`, "utf8");
beforeAll(() => {
  initConfig({ module: readFileSync("src/vendor/moergo-config-wasm/moergo_config_wasm_bg.wasm") });
  initRynk({ module: readFileSync("src/vendor/rynk-wasm/rynk_wasm_bg.wasm") });
});
it("preserves every configured resource through the exact editor codec", () => {
  const catalog = offlineGlove80Catalog();
  const source = parseDocument(text, catalog);
  const result = parseDocument(renderDocument(source.snapshot, catalog, "toml", text), catalog);
  expect(result.snapshot).toEqual(source.snapshot);
});
it("opens the personal workspace, retains priority bindings and lighting, and exports a valid project", async () => {
  const catalog = offlineGlove80Catalog();
  const source = parseDocument(text, catalog);
  const session = openOfflineGlove80(source.snapshot);
  try {
    const bundle = await openBundle(session);
    expect(bundle.incompleteReads).toEqual([]);
    const state = initialWorkbenchState(bundle);
    const output = exportDocument(state, catalog, "toml", text);
    const actual = parseDocument(output, catalog).snapshot;
    expect(actual.layers).toEqual(source.snapshot.layers);
    expect(actual.default_layer).toEqual(source.snapshot.default_layer);
    expect(actual.behaviors?.morses).toEqual(source.snapshot.behaviors?.morses);
    expect(actual.behaviors?.combos).toEqual(source.snapshot.behaviors?.combos);
    expect(actual.lighting?.scenes).toEqual(source.snapshot.lighting?.scenes);
    expect(actual.lighting?.conditional_scenes).toEqual(source.snapshot.lighting?.conditional_scenes);
    expect(actual.lighting?.effects).toEqual(source.snapshot.lighting?.effects);
    expect(actual.lighting?.brightness).toBe(source.snapshot.lighting?.brightness);
    expect(actual.lighting?.wake_layers).toEqual([2]);
    writeFileSync(`${root}/.cache/editor-roundtrip.toml`, output);
  } finally { await session.close(); }
});
