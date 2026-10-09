{
  description = "Personal Glove80 layout on supported MoErgo ZMK";

  inputs.zmk = {
    url = "github:moergo-sc/zmk/ce69e85f585c724142aae37ddf8a7e019ff19e93";
    flake = false;
  };

  outputs =
    { zmk, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems =
        f:
        builtins.listToAttrs (
          map (system: {
            name = system;
            value = f system;
          }) systems
        );
      pkgsFor = system: import "${zmk}/nix/pinned-nixpkgs.nix" { inherit system; };
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
          firmware = import zmk { inherit pkgs; };
          combined = import ./config { inherit firmware; };
        in
        {
          firmware = combined;
          default = combined;
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.just
              pkgs.python3
              pkgs.gcc
              pkgs.dtc
              pkgs.util-linux
            ];
            shellHook = ''
              export GLOVE80_ZMK_SOURCE=${zmk}
              export GLOVE80_ZMK_SHELL=1
            '';
          };
        }
      );

      checks = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
        in
        {
          keymap =
            pkgs.runCommand "glove80-keymap-check"
              {
                nativeBuildInputs = [
                  pkgs.python3
                  pkgs.gcc
                  pkgs.dtc
                  pkgs.bash
                  pkgs.just
                ];
              }
              ''
                bash -n ${./keyboard} ${./scripts/zmk-keyboard}
                just --justfile ${./justfile} --list >/dev/null
                GLOVE80_DROPPER=${./scripts/drop-firmware.py} python3 -m unittest discover -s ${./tests} -p 'test_*.py'
                python3 ${./scripts/check-zmk.py} --zmk ${zmk} --config ${./config}
                touch "$out"
              '';
        }
      );
    };
}
