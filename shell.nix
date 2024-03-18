{
  pkgs ? import (builtins.fetchGit {
    url = "https://github.com/NixOS/nixpkgs/";
    ref = "refs/tags/23.11";
  }) {},
  dev ? true,
}:
let
  py310 = pkgs.python310;
  poetryExtras = if dev then ["dev"] else [];
  poetryInstallExtras = (
    if poetryExtras == [] then ""
    else pkgs.lib.concatStrings [ " --with=" (pkgs.lib.concatStringsSep "," poetryExtras) ]
  );
in
pkgs.mkShell {
  name = "numpy-deco-env";
  buildInputs = with pkgs; [
    poetry
    py310
    python311
    python312
  ];
  shellHook = ''
    poetry env use "${py310}/bin/python"
    poetry install -vv --sync${poetryInstallExtras}
    source "$(poetry env info --path)/bin/activate"
  '';
}
