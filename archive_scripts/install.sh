#!/bin/bash
# Linux/macOS installation script for Prometheus Light

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║         PROMETHEUS LIGHT - GOD MODE INSTALLER                        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Please install Python 3.11+ first."
    exit 1
fi

echo "[1/4] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo ""
echo "[2/4] Installing Prometheus Light..."
pip install -e .

echo ""
echo "[3/4] Creating data directory..."
mkdir -p ~/.mydata

echo ""
echo "[4/4] Setting up environment..."
cat > .env << EOF
# Prometheus Light Environment
MYDATA_HOME=$HOME/.mydata
EOF

echo ""
echo "[5/5] Running first-time setup..."
echo ""
mydata setup

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    INSTALLATION COMPLETE!                            ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Run:  ./launch.sh"
echo "  2. Add email:  mydata email-add chris.marinelli@vysusgroup.com"
echo "  3. Start daemon:  mydata daemon"
echo ""
echo "For help: mydata --help"
echo "Full guide: USAGE_GUIDE.md"
echo ""
