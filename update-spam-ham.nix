with import <nixpkgs> {};
stdenv.mkDerivation {
  name = "update-spam-ham";
  dontUnpack = true;
  pythonPath = [ python3.pkgs.requests ];
  nativeBuildInputs = [ python3.pkgs.wrapPython ];

  postFixup = "wrapPythonPrograms";
  installPhase = ''
    install -D -m755 ${./update-spam-ham.py} $out/bin/update-spam-ham
  '';
}
