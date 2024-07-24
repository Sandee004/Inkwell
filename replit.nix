{ pkgs }: {
  deps = [
    pkgs.cargo
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargopkgs.mailutils

  ];
}