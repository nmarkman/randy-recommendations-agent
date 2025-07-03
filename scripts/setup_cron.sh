#!/bin/bash
# Randy Recommendation Agent - Cron Setup Script

# Get the current directory (where Randy lives)
RANDY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_PATH="$(which python3)"

# Create logs directory if it doesn't exist
mkdir -p "$RANDY_DIR/logs"

# Create the cron job script
cat > "$RANDY_DIR/scripts/run_randy_cron.sh" << EOF
#!/bin/bash
# Randy Cron Job Runner
# This script runs Randy and logs everything properly

# Set environment
export PATH="/usr/local/bin:/usr/bin:/bin"
cd "$RANDY_DIR"

# Log the attempt
echo "\$(date): Starting Randy cron job" >> logs/cron.log

# Run Randy with full logging
$PYTHON_PATH main.py >> logs/cron.log 2>&1

# Log completion
echo "\$(date): Randy cron job completed with exit code: \$?" >> logs/cron.log
echo "----------------------------------------" >> logs/cron.log
EOF

# Make the script executable
chmod +x "$RANDY_DIR/scripts/run_randy_cron.sh"

# Create the cron entry
CRON_JOB="0 9 * * * $RANDY_DIR/scripts/run_randy_cron.sh"

echo "🌀 Randy Cron Setup"
echo "===================="
echo "Randy Directory: $RANDY_DIR"
echo "Python Path: $PYTHON_PATH"
echo "Cron Job: $CRON_JOB"
echo ""
echo "To install the cron job, run:"
echo "  (crontab -l 2>/dev/null; echo \"$CRON_JOB\") | crontab -"
echo ""
echo "To check current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove Randy's cron job:"
echo "  crontab -l | grep -v 'run_randy_cron.sh' | crontab -"
echo ""
echo "Logs will be in: $RANDY_DIR/logs/cron.log"
echo "Randy's main logs: $RANDY_DIR/data/randy.log" 