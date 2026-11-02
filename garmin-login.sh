#!/bin/bash
echo "============================================================"
echo " LIFE OS PRIME // GARMIN CONNECT AUTHENTICATION"
echo "============================================================"
echo "This will refresh your Garmin Connect security tokens in"
echo "~/.garminconnect so LIFE OS PRIME can pull your daily sleep,"
echo "body battery, VO2 max, and workout metrics automatically."
echo ""
/Users/farahfarah/.local/bin/uv run --python 3.12 --with git+https://github.com/Taxuspt/garmin_mcp python -m garmin_mcp.auth_cli --force-reauth
echo ""
echo "Authentication complete! LIFE OS PRIME is now synchronized."
