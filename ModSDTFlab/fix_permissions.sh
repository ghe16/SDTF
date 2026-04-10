#!/bin/bash

# Quick fix for Ubuntu permission issues
# Run this if npm install fails with permission errors

echo "Fixing permissions for npm..."
mkdir -p "$HOME/.npm"
chmod -R 755 "$HOME/.npm"

# Fix node_modules permissions
if [ -d "node_modules" ]; then
    echo "Fixing node_modules permissions..."
    chmod -R 755 node_modules
    chmod +x node_modules/.bin/* 2>/dev/null || true
fi

# Try npm install again
echo "Running npm install..."
npm install

echo "Done! Run 'npm run dev' to start the frontend."