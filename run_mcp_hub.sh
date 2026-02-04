#!/usr/bin/env bash
set -euo pipefail

REPO_SSH="git@github.com:fengyue-95/mcp_hub.git"
REPO_DIR="mcp_hub"
BRANCH="main"

if [ -d "$REPO_DIR/.git" ]; then
  echo "Repo exists. Pulling latest $BRANCH..."
  git -C "$REPO_DIR" fetch origin
  git -C "$REPO_DIR" checkout "$BRANCH"
  git -C "$REPO_DIR" pull --ff-only origin "$BRANCH"
else
  echo "Cloning repo..."
  git clone -b "$BRANCH" "$REPO_SSH" "$REPO_DIR"
fi

cd "$REPO_DIR"

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting app..."
python main.py
