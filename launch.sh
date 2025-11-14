#!/bin/bash
# Bash launcher for Prometheus Light - God Mode

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Clear screen
clear

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ██████╗ ██████╗  ██████╗ ███╗   ███╗███████╗████████╗██╗  ██╗   ║
║    ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██║  ██║   ║
║    ██████╔╝██████╔╝██║   ██║██╔████╔██║█████╗     ██║   ███████║   ║
║    ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║   ║
║    ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║   ║
║    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝   ║
║                                                                      ║
EOF
echo -e "${GREEN}"
cat << "EOF"
║             ██╗     ██╗ ██████╗ ██╗  ██╗████████╗                   ║
║             ██║     ██║██╔════╝ ██║  ██║╚══██╔══╝                   ║
║             ██║     ██║██║  ███╗███████║   ██║                      ║
║             ██║     ██║██║   ██║██╔══██║   ██║                      ║
║             ███████╗██║╚██████╔╝██║  ██║   ██║                      ║
║             ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝                      ║
║                                                                      ║
EOF
echo -e "${YELLOW}"
echo "║                        ══ GOD MODE ══                                ║"
echo -e "${CYAN}"
echo "║                                                                      ║"
echo -e "${WHITE}║         Encrypted · Local · ML-Powered Knowledge Base               ║${CYAN}"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}Initializing...${NC}"
sleep 0.5

# Check if initialized
if [ ! -f "$HOME/.mydata/master.key" ]; then
    echo ""
    echo -e "${YELLOW}⚠ First time setup required${NC}"
    echo ""
    echo -e "${CYAN}Running setup...${NC}"
    mydata setup
fi

echo ""
echo -e "${GREEN}Ready. Type 'mydata --help' for commands${NC}"
echo ""

# Start interactive session
if [ $# -eq 0 ]; then
    echo -e "${CYAN}Quick commands:${NC}"
    echo -e "${WHITE}  mydata daemon          - Start background services${NC}"
    echo -e "${WHITE}  mydata ask 'query'     - Search your knowledge base${NC}"
    echo -e "${WHITE}  mydata ls              - List documents${NC}"
    echo -e "${WHITE}  mydata stats           - Show statistics${NC}"
    echo ""
else
    # Run command
    mydata "$@"
fi
