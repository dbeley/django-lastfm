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

        # Python environment with all dependencies
        pythonEnv = python.withPackages (ps: with ps; [
          beautifulsoup4
          celery
          django
          django-bootstrap4
          django-widget-tweaks
          django-celery-results
          openpyxl
          pandas
          pillow
          pylast
          requests
          redis
          gunicorn
          wordcloud
          mastodon-py
          tqdm
          matplotlib
        ]);

        # Build the Django application package
        django-lastfm = pkgs.stdenv.mkDerivation {
          pname = "django-lastfm";
          version = "0.1.0";

          src = ./.;

          nativeBuildInputs = [ pkgs.makeWrapper ];

          installPhase = ''
            mkdir -p $out/share/django-lastfm
            mkdir -p $out/bin
            
            # Copy application code
            cp -r $src/lastfm_django $out/share/django-lastfm/
            cp -r $src/lastfm_cg $out/share/django-lastfm/
            cp -r $src/lastfm_pg $out/share/django-lastfm/
            cp -r $src/lastfm_wordcloud $out/share/django-lastfm/
            cp -r $src/lastfm_scraper $out/share/django-lastfm/
            cp -r $src/deps $out/share/django-lastfm/ || true
            cp $src/manage.py $out/share/django-lastfm/
            
            # Create wrapper for manage.py
            makeWrapper ${pythonEnv}/bin/python $out/bin/django-lastfm-manage \
              --add-flags "$out/share/django-lastfm/manage.py" \
              --set PYTHONPATH "$out/share/django-lastfm"
            
            # Create wrapper for gunicorn
            makeWrapper ${pythonEnv}/bin/gunicorn $out/bin/django-lastfm-web \
              --set PYTHONPATH "$out/share/django-lastfm" \
              --add-flags "lastfm_django.wsgi"
            
            # Create wrapper for celery
            makeWrapper ${pythonEnv}/bin/celery $out/bin/django-lastfm-celery \
              --set PYTHONPATH "$out/share/django-lastfm"
          '';

          meta = with pkgs.lib; {
            description = "Django frontend for Last.fm utilities";
            homepage = "https://github.com/dbeley/django-lastfm";
            license = pkgs.lib.licenses.gpl3;
            maintainers = [ ];
          };
        };
      in
      {
        packages = {
          default = django-lastfm;
          django-lastfm = django-lastfm;
        };

        # Development shell
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pythonPackages.black
            pkgs.redis
          ];

          shellHook = ''
            echo "Django Last.fm development environment"
            echo "==============================================="
            echo "Available commands:"
            echo "  python manage.py runserver  - Start dev server"
            echo "  python manage.py migrate    - Run migrations"
            echo "  redis-server                - Start Redis (for Celery)"
            echo "  celery -A lastfm_django worker -l info - Start Celery worker"
            echo ""
            echo "Make sure to configure your secrets in .env or config files"
          '';
        };
      }
    ) // {
      # NixOS module - available on all systems
      nixosModules.default = import ./nixos-module.nix;
      nixosModules.django-lastfm = import ./nixos-module.nix;
    };
}
