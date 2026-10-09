{ firmware }:
let
  left = firmware.zmk.override {
    board = "glove80_lh";
    keymap = ./glove80.keymap;
    kconfig = ./glove80.conf;
  };
  right = firmware.zmk.override {
    board = "glove80_rh";
    keymap = ./glove80.keymap;
    kconfig = ./glove80.conf;
  };
in
firmware.combine_uf2 left right
