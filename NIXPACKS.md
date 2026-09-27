# Coolify Nixpacks deployment

Use the Nixpacks build pack, branch `main`, and Base Directory `/` for this
repository. Keep Install, Build, and Start command overrides empty so that
Coolify uses `nixpacks.toml`. Remove old `NIXPACKS_INSTALL_CMD`,
`NIXPACKS_BUILD_CMD`, and `NIXPACKS_START_CMD` overrides if present.
Set Ports Exposes to `8000` and deploy the latest commit.

The configuration installs the MariaDB client headers and pkg-config needed to
compile mysqlclient. These client libraries work with the application's MySQL
server. It installs CPU PyTorch wheels and verifies the native Python imports
during the build. Runtime OpenSSL, database, and OpenCV libraries are explicitly
listed in `nixLibs` so Nix Python can locate them. Installing Apt development
packages alone does not configure Nix's runtime library search path.
`python nixpacks-check.py` checks each dependency independently and reports all
failures, without connecting to the database. Installation also runs `pip check`
to detect incompatible package dependencies.
The startup script runs migrations, collects static files,
and starts Gunicorn on `0.0.0.0:8000`.

Configure runtime environment variables in Coolify:

- `DJANGO_DEBUG=0`
- `DJANGO_SECRET_KEY`: a unique random secret of at least 50 characters
- `DJANGO_ALLOWED_HOSTS=api.dormitorykc.online`
- `CSRF_TRUSTED_ORIGINS=https://api.dormitorykc.online,https://dormitorykc.online`
- `CORS_ALLOWED_ORIGINS`: the frontend HTTPS origin when hosted separately
- `DB_ENGINE=mysql`
- `MYSQL_HOST`: the database hostname reachable from the deployed application
- `MYSQL_PORT=3306`
- `MYSQL_DATABASE=dormitory`
- `MYSQL_USER` and `MYSQL_PASSWORD`: the deployed database credentials

For the current frontend deployment, set
`CORS_ALLOWED_ORIGINS=https://dormitorykc.online`.
Use the origin only, without `/login` or a trailing slash. This origin is also
in the code defaults; a Coolify environment value replaces those defaults.
Route `https://api.dormitorykc.online` to this backend on port `8000` in Coolify.
The frontend uses HTTPS for API requests; an HTTP API URL would be blocked by
the browser when the frontend is served over HTTPS.
Redeploy the backend after changing it.

Use a supported database server, such as MySQL 8.4. The local MariaDB 10.4
instance is too old for the current Django version. Configure persistent
storage for `/app/media` and, if using uploaded model weights, `/app/models`.
This repository deploys the backend API; the frontend is a separate project.

Reference: https://nixpacks.com/docs/configuration/file
