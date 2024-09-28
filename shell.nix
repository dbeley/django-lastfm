with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell {
  buildInputs = [
    python3
    pythonPackages.pip
    pythonPackages.beautifulsoup4
    pythonPackages.celery
    pythonPackages.django
    pythonPackages.django-bootstrap4
    pythonPackages.django-widget-tweaks
    pythonPackages.django-celery-results
    pythonPackages.openpyxl
    pythonPackages.pandas
    pythonPackages.pillow
    pythonPackages.pylast
    pythonPackages.requests
    pythonPackages.redis
    pythonPackages.gunicorn
    pythonPackages.wordcloud
    pythonPackages.black
  ];

}
