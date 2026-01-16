# This file provides backward compatibility for non-flake users
# For the best experience with flakes, use: nix develop
# For traditional nix-shell, this file will still work

let
  flake-compat = fetchTarball {
    url = "https://github.com/edolstra/flake-compat/archive/master.tar.gz";
  };
  flake = (import flake-compat { src = ./.; }).defaultNix;
in
  flake.devShells.${builtins.currentSystem}.default
