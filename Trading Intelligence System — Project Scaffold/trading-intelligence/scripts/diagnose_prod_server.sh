#!/usr/bin/env bash
# ============================================
# PHASE 0 — DIAGNOSTIC SCRIPT
# ============================================
# Run this script on the OLD LAPTOP (Ubuntu Server)
# to verify production server readiness.
#
# Usage:
#   chmod +x scripts/diagnose_prod_server.sh
#   ./scripts/diagnose_prod_server.sh
# ============================================

set -e

echo "============================================"
echo "  TRADING INTELLIGENCE SYSTEM"
echo "  Production Server Diagnostic"
echo "============================================"
echo ""

# ---- OS ----
echo "--- Operating System ---"
cat /etc/os-release 2>/dev/null | head -5 || echo "OS info not available"
echo ""

# ---- CPU ----
echo "--- CPU ---"
lscpu | grep -E "^(Model name|CPU\(s\)|Architecture)" 2>/dev/null || echo "CPU info not available"
echo ""

# ---- RAM ----
echo "--- RAM ---"
free -h 2>/dev/null || echo "RAM info not available"
echo ""

# ---- Disk ----
echo "--- Disk ---"
df -h / 2>/dev/null || echo "Disk info not available"
echo ""

# ---- GPU (940M — should NOT be used for AI) ----
echo "--- GPU (display only, not for AI inference) ---"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv 2>/dev/null
else
    echo "  NVIDIA driver not found (OK for production server)"
fi
echo ""

# ---- Python ----
echo "--- Python ---"
python3 --version 2>/dev/null || echo "Python not installed"
echo ""

# ---- Git ----
echo "--- Git ---"
git --version 2>/dev/null || echo "Git not installed"
echo ""

# ---- Docker ----
echo "--- Docker ---"
if command -v docker &> /dev/null; then
    docker --version
    docker compose version 2>/dev/null || docker-compose --version 2>/dev/null
    echo "  Docker daemon: $(docker info --format '{{.ServerVersion}}' 2>/dev/null || echo 'NOT running')"
    if docker info &> /dev/null; then
        echo "  Running containers:"
        docker ps --format "  {{.Names}}: {{.Status}}" 2>/dev/null || echo "  No containers running"
    fi
else
    echo "  Docker not installed"
    echo "  Install: curl -fsSL https://get.docker.com | sh"
fi
echo ""

# ---- Tailscale ----
echo "--- Tailscale ---"
if command -v tailscale &> /dev/null; then
    tailscale status 2>/dev/null || echo "  Tailscale installed but not running"
    echo "  IP: $(tailscale ip -4 2>/dev/null || echo 'not assigned')"
else
    echo "  Tailscale not installed"
    echo "  Install: curl -fsSL https://tailscale.com/install.sh | sh"
fi
echo ""

# ---- SSH ----
echo "--- SSH ---"
if command -v sshd &> /dev/null; then
    echo "  SSH server available"
    echo "  Config:"
    grep -E "^(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)" /etc/ssh/sshd_config 2>/dev/null || echo "  Could not read SSH config"
    echo "  SSH keys:"
    ls -la ~/.ssh/*.pub 2>/dev/null || echo "  No SSH public keys found"
else
    echo "  SSH server not installed"
    echo "  Install: sudo apt install openssh-server"
fi
echo ""

# ---- Firewall ----
echo "--- Firewall (UFW) ---"
if command -v ufw &> /dev/null; then
    sudo ufw status 2>/dev/null || echo "  UFW status requires sudo"
else
    echo "  UFW not installed"
fi
echo ""

# ---- PostgreSQL (if installed) ----
echo "--- PostgreSQL ---"
if command -v psql &> /dev/null; then
    psql --version 2>/dev/null
else
    echo "  PostgreSQL not installed (will run in Docker)"
fi
echo ""

# ---- Redis (if installed) ----
echo "--- Redis ---"
if command -v redis-cli &> /dev/null; then
    redis-cli --version 2>/dev/null
else
    echo "  Redis not installed (will run in Docker)"
fi
echo ""

echo "============================================"
echo "  Diagnostic Complete"
echo "============================================"
echo ""
echo "PHASE 0 requirements for production server:"
echo "  1. Ubuntu Server (LTS)"
echo "  2. SSH (key-based auth)"
echo "  3. Tailscale (connected to tailnet)"
echo "  4. Docker + Docker Compose"
echo "  5. UFW firewall (deny incoming, allow Tailscale)"
echo ""
echo "Do NOT install PostgreSQL or Redis directly —"
echo "they will run as Docker containers."
