{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.django-lastfm;
  stateDir = "/var/lib/django-lastfm";
in {
  options.services.django-lastfm = {
    enable = mkEnableOption "Django Last.fm Tools service";

    package = mkOption {
      type = types.package;
      default = pkgs.django-lastfm or (throw "django-lastfm package not found. Make sure the flake overlay is applied.");
      description = "The django-lastfm package to use";
    };

    settings = {
      secretKeyFile = mkOption {
        type = types.path;
        description = "Path to file containing the Django secret key";
        example = "/run/secrets/django-secret";
      };

      allowedHosts = mkOption {
        type = types.listOf types.str;
        default = [ "localhost" "127.0.0.1" ];
        description = "List of allowed hosts for Django";
        example = [ "lastfm-tools.example.com" "localhost" ];
      };

      debug = mkOption {
        type = types.bool;
        default = false;
        description = "Enable Django debug mode (DO NOT use in production)";
      };

      csrfTrustedOrigins = mkOption {
        type = types.listOf types.str;
        default = [ ];
        description = "List of trusted origins for CSRF";
        example = [ "https://*.example.com" ];
      };
    };

    lastfm = {
      usernameFile = mkOption {
        type = types.path;
        description = "Path to file containing Last.fm username";
        example = "/run/secrets/lastfm-username";
      };

      apiKeyFile = mkOption {
        type = types.path;
        description = "Path to file containing Last.fm API key";
        example = "/run/secrets/lastfm-api-key";
      };

      apiSecretFile = mkOption {
        type = types.path;
        description = "Path to file containing Last.fm API secret";
        example = "/run/secrets/lastfm-api-secret";
      };
    };

    web = {
      host = mkOption {
        type = types.str;
        default = "127.0.0.1";
        description = "Host address to bind the web server to";
      };

      port = mkOption {
        type = types.port;
        default = 8001;
        description = "Port to bind the web server to";
      };

      workers = mkOption {
        type = types.int;
        default = 4;
        description = "Number of Gunicorn worker processes";
      };

      timeout = mkOption {
        type = types.int;
        default = 600;
        description = "Gunicorn worker timeout in seconds";
      };
    };

    user = mkOption {
      type = types.str;
      default = "django-lastfm";
      description = "User account under which django-lastfm runs";
    };

    group = mkOption {
      type = types.str;
      default = "django-lastfm";
      description = "Group under which django-lastfm runs";
    };
  };

  config = mkIf cfg.enable {
    users.users.${cfg.user} = {
      isSystemUser = true;
      group = cfg.group;
      home = stateDir;
      createHome = true;
      description = "Django Last.fm service user";
    };

    users.groups.${cfg.group} = {};

    systemd.services.django-lastfm-web = {
      description = "Django Last.fm Web Service";
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];

      environment = {
        PYTHONPATH = "${cfg.package}/${pkgs.python3.sitePackages}";
        DJANGO_SETTINGS_MODULE = "lastfm_django.settings";
        ALLOWED_HOSTS = concatStringsSep " " cfg.settings.allowedHosts;
      };

      serviceConfig = {
        Type = "simple";
        User = cfg.user;
        Group = cfg.group;
        WorkingDirectory = stateDir;

        ExecStartPre = pkgs.writeShellScript "django-lastfm-init" ''
          set -e
          mkdir -p ${stateDir}
          cd ${stateDir}

          if [ ! -d "lastfm_django" ]; then
            cp -r ${cfg.package}/${pkgs.python3.sitePackages}/lastfm_* .
          fi

          export DJANGO_SECRET_KEY=$(cat ${cfg.settings.secretKeyFile})
          export PYLAST_USERNAME=$(cat ${cfg.lastfm.usernameFile})
          export PYLAST_API_KEY=$(cat ${cfg.lastfm.apiKeyFile})
          export PYLAST_API_SECRET=$(cat ${cfg.lastfm.apiSecretFile})
          export ALLOWED_HOSTS="${concatStringsSep " " cfg.settings.allowedHosts}"

          ${cfg.package}/bin/django-lastfm-manage migrate --noinput
          ${cfg.package}/bin/django-lastfm-manage collectstatic --noinput --clear
        '';

        ExecStart = ''
          ${cfg.package}/bin/django-lastfm-web \
            --bind ${cfg.web.host}:${toString cfg.web.port} \
            --workers ${toString cfg.web.workers} \
            --timeout ${toString cfg.web.timeout}
        '';

        Restart = "always";
        RestartSec = "10s";

        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ReadWritePaths = stateDir;
        ProtectKernelTunables = true;
        ProtectKernelModules = true;
        ProtectControlGroups = true;
      };
    };
  };
}
