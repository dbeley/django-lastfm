{
  description = "Django Last.fm Tools - A web frontend for Last.fm utilities";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;
        pythonPackages = python.pkgs;

        pythonEnv = python.withPackages (ps: with ps; [
          beautifulsoup4
          django
          django-bootstrap4
          django-widget-tweaks
          openpyxl
          pandas
          pillow
          pylast
          requests
          gunicorn
          wordcloud
          mastodon-py
          tqdm
          matplotlib
        ]);
      in
      {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "django-lastfm";
          version = "0.2.0";

          src = ./.;

          nativeBuildInputs = [ pkgs.makeWrapper ];

          installPhase = ''
            mkdir -p $out/share/django-lastfm
            mkdir -p $out/bin

            cp -r $src/lastfm_django $out/share/django-lastfm/
            cp -r $src/lastfm_cg $out/share/django-lastfm/
            cp -r $src/lastfm_pg $out/share/django-lastfm/
            cp -r $src/lastfm_wordcloud $out/share/django-lastfm/
            cp -r $src/lastfm_scraper $out/share/django-lastfm/
            cp $src/manage.py $out/share/django-lastfm/

            makeWrapper ${pythonEnv}/bin/python $out/bin/django-lastfm-manage \
              --add-flags "$out/share/django-lastfm/manage.py" \
              --set PYTHONPATH "$out/share/django-lastfm"

            makeWrapper ${pythonEnv}/bin/gunicorn $out/bin/django-lastfm-web \
              --set PYTHONPATH "$out/share/django-lastfm" \
              --add-flags "lastfm_django.wsgi"
          '';

          meta = with pkgs.lib; {
            description = "Django frontend for Last.fm utilities";
            homepage = "https://github.com/dbeley/django-lastfm";
            license = pkgs.lib.licenses.gpl3;
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pythonPackages.ruff
          ];

          shellHook = ''
            echo "Django Last.fm development environment"
            echo "==============================================="
            echo "Available commands:"
            echo "  python manage.py runserver  - Start dev server"
            echo "  python manage.py migrate    - Run migrations"
            echo ""
            echo "Make sure to configure your secrets in .env or config files"
          '';
        };
      }
    ) // {
      nixosModules.default = import ./nixos-module.nix;
      nixosModules.django-lastfm = import ./nixos-module.nix;
    };
}
