{ pkgs ? import <nixpkgs> {}}:

with pkgs;
python3.pkgs.buildPythonApplication {
  pname = "rspamd-learn-spam-ham";
  version = "1.0.0";

  src = ./.;

  propagatedBuildInputs = [ python3.pkgs.requests ];

  buildInputs = [ makeWrapper ];
  checkInputs = [ mypy python3.pkgs.black python3.pkgs.flake8 ];
  checkPhase = ''
    echo -e "\x1b[32m## run black\x1b[0m"
    black --check .
    echo -e "\x1b[32m## run flake8\x1b[0m"
    flake8 .
    echo -e "\x1b[32m## run mypy\x1b[0m"
    mypy --strict .
  '';
}
