# Use the firmware's locked nixpkgs; this does not configure the host OS.
let
  firmware = builtins.getFlake ("path:" + toString ./dependencies/moergo-rmk);
  system = builtins.currentSystem;
  pkgs = import firmware.inputs.nixpkgs { inherit system; };
in firmware.devShells.${system}.default.overrideAttrs (old: {
  nativeBuildInputs = (old.nativeBuildInputs or []) ++ [ pkgs.python3 pkgs.nodejs ];
})
