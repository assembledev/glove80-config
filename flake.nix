{
  description = "Glove80 configuration development environment";

  inputs = {
    firmware.url = "github:colonelpanic8/moergo-rmk/6638852adf1bd6a82b9abdf2b88de5deda90f798";
    nixpkgs.follows = "firmware/nixpkgs";
  };

  outputs =
    {
      nixpkgs,
      firmware,
      ...
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = firmware.devShells.${system}.default.overrideAttrs (old: {
            nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
              pkgs.python3
              pkgs.nodejs
              pkgs.nixfmt
            ];
            shellHook = (old.shellHook or "") + ''
              if [ -f "$PWD/justfile" ] && [ -f "$PWD/config/runtime.toml" ]; then
                export GLOVE80_PROJECT_SHELL="$PWD"
              fi
            '';
          });
        }
      );
      checks = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          transactions =
            pkgs.runCommand "glove80-transaction-check"
              {
                nativeBuildInputs = [ pkgs.python3 ];
              }
              ''
                cp -r ${./scripts} scripts
                cp -r ${./tests} tests
                python3 -m unittest discover -s tests -p 'test_*.py'
                touch "$out"
              '';
          shell =
            pkgs.runCommand "glove80-shell-check"
              {
                nativeBuildInputs = [
                  pkgs.bash
                  pkgs.just
                ];
              }
              ''
                bash -n ${./keyboard} ${./scripts/keyboard} ${./scripts/build-editor}
                just --justfile ${./justfile} --list > /dev/null
                touch "$out"
              '';
          nix-format =
            pkgs.runCommand "glove80-nix-format"
              {
                nativeBuildInputs = [ pkgs.nixfmt ];
              }
              ''
                nixfmt --check ${./flake.nix}
                touch "$out"
              '';
        }
      );
      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt);
    };
}
