{pkgs}: {
  deps = [
    pkgs.cmake
    pkgs.libGLU
    pkgs.libGL
    pkgs.postgresql
    pkgs.openssl
  ];
}
