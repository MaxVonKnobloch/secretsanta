#!/usr/bin/env bash
set -euo pipefail

# Build frontend for production with the correct base path and copy it to the target directory
# Usage:
#  ./scripts/build_and_copy_frontend.sh                 # builds and rsyncs to default remote home-server:/var/www/secretsanta
#  DEST=server:/var/www/secretsanta ./scripts/build_and_copy_frontend.sh   # rsync to another remote server (user@host:path)
#  DEST=/some/local/path ./scripts/build_and_copy_frontend.sh             # copy to custom local path
#  SKIP_BUILD=1 ./scripts/build_and_copy_frontend.sh  # don't attempt to build, just deploy existing frontend/build

: "${DEST:=home-server:/var/www/secretsanta}"
: "${SKIP_BUILD:=0}"

echo "Preparing frontend deployment (DEST=$DEST, SKIP_BUILD=$SKIP_BUILD)"

BUILD_DIR=frontend/build

if [[ "$SKIP_BUILD" != "1" ]]; then
  # If there's an existing build directory already committed, we can optionally skip building
  if [[ -f "$BUILD_DIR/index.html" ]]; then
    echo "Found existing '$BUILD_DIR/index.html' — skipping build step. Set SKIP_BUILD=0 to force a rebuild."
  else
    echo "No existing build found; running build..."
    cd frontend

    # Install dependencies robustly: try npm ci first, but fall back to npm install if ci fails (lockfile issues)
    if [[ -f package-lock.json || -f npm-shrinkwrap.json ]]; then
      echo "Found lockfile, attempting: npm ci --legacy-peer-deps"
      if ! npm ci --legacy-peer-deps; then
        echo "npm ci failed, attempting: npm install --legacy-peer-deps"
        if ! npm install --legacy-peer-deps; then
          echo "npm install also failed. Trying to recover by removing lockfile and reinstalling."
          # Backup lockfile then try a fresh install
          if [[ -f package-lock.json ]]; then
            mv package-lock.json package-lock.json.bak || true
            echo "Backed up package-lock.json -> package-lock.json.bak"
          fi
          # Clean npm cache to avoid stale cache issues
          npm cache clean --force || true
          echo "Running npm install --legacy-peer-deps (fresh, without lockfile)"
          npm install --legacy-peer-deps
        fi
      fi
    else
      echo "No lockfile found, running: npm install --legacy-peer-deps"
      npm install --legacy-peer-deps
    fi

    # Ensure local node binaries are on PATH (so react-scripts can be found)
    export PATH="$(pwd)/node_modules/.bin:$PATH"

    # Verify react-scripts available
    if ! command -v react-scripts >/dev/null 2>&1; then
      echo "react-scripts not found after install. Listing node_modules/.bin:"
      ls -la node_modules/.bin || true
      echo "Please ensure 'react-scripts' is a dependency in frontend/package.json and that npm install succeeded."
      exit 1
    fi

    # Ensure PUBLIC_URL is set so built assets reference /secretsanta
    PUBLIC_URL=/secretsanta npm run build
    cd ..
  fi
else
  echo "SKIP_BUILD=1 — not attempting to build; will deploy existing $BUILD_DIR"
fi

# At this point BUILD_DIR should exist
if [[ ! -d "$BUILD_DIR" || ! -f "$BUILD_DIR/index.html" ]]; then
  echo "ERROR: Build output not found at '$BUILD_DIR'. Aborting."
  exit 1
fi

if [[ "$DEST" == *":"* ]]; then
  # remote sync (rsync over ssh)
  echo "Syncing build/ to remote destination $DEST"
  rsync -av --delete "$BUILD_DIR/" "$DEST/"
  echo "Remote sync complete. Remember to set correct permissions on the server: sudo chown -R www-data:www-data /var/www/secretsanta"
else
  # local copy
  TARGET_DIR="$DEST"
  echo "Copying build/ to local target $TARGET_DIR"
  mkdir -p "$TARGET_DIR"
  rsync -av --delete "$BUILD_DIR/" "$TARGET_DIR/"
  echo "Local copy complete. Setting owner to www-data (may prompt for sudo)."
  if command -v sudo >/dev/null 2>&1; then
    sudo chown -R www-data:www-data "$TARGET_DIR" || true
    sudo chmod -R 755 "$TARGET_DIR" || true
  else
    chown -R www-data:www-data "$TARGET_DIR" || true
    chmod -R 755 "$TARGET_DIR" || true
  fi
  echo "Frontend deployed to $TARGET_DIR"
fi

# Print a small check list
cat <<EOF
Done.
- Frontend build is at: $BUILD_DIR
- Deployed to: $DEST
- Ensure nginx config serves /secretsanta from the target directory and proxies /secretsanta/api/ to http://127.0.0.1:8000
EOF
