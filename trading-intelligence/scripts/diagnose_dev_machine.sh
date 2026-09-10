#!/usr/bin/env bash
# ============================================
# PHASE 0 — DIAGNOSTIC SCRIPT
# ============================================
# Run this script on the NEW LAPTOP (AI Workstation)
# to verify hardware and software readiness.
#
# Usage:
#   chmod +x scripts/diagnose_dev_machine.sh
#   ./scripts/diagnose_dev_machine.sh
# ============================================

set -e

echo "============================================"
echo "  TRADING INTELLIGENCE SYSTEM"
echo "  Development Machine Diagnostic"
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

# ---- GPU ----
echo "--- GPU ---"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,driver_version \
               --format=csv 2>/dev/null
    echo ""
    echo "CUDA:"
    nvcc --version 2>/dev/null || echo "CUDA toolkit not installed (nvcc not found)"
    echo ""
    echo "PyTorch CUDA check:"
    python3 -c "
import torch
if torch.cuda.is_available():
    print(f'  CUDA available: {torch.cuda.get_device_name(0)}')
    print(f'  VRAM total: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB')
    print(f'  CUDA version: {torch.version.cuda}')
else:
    print('  CUDA NOT available in PyTorch')
" 2>/dev/null || echo "  PyTorch not installed"
else
    echo "  NVIDIA driver not found (nvidia-smi not available)"
    echo "  Run: sudo apt install nvidia-driver-535"
fi
echo ""

# ---- Python ----
echo "--- Python ---"
python3 --version 2>/dev/null || echo "Python not installed"
pip3 --version 2>/dev/null || echo "pip not installed"
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

# ---- Ollama ----
echo "--- Ollama ---"
if command -v ollama &> /dev/null; then
    ollama --version 2>/dev/null
    echo "  Models:"
    ollama list 2>/dev/null | head -10
else
    echo "  Ollama not installed"
    echo "  Install: curl -fsSL https://ollama.com/install.sh | sh"
fi
echo ""

# ---- SSH ----
echo "--- SSH ---"
if command -v ssh &> /dev/null; then
    echo "  SSH client available"
    echo "  SSH keys:"
    ls -la ~/.ssh/*.pub 2>/dev/null || echo "  No SSH public keys found"
else
    echo "  SSH not installed"
fi
echo ""

echo "============================================"
echo "  Diagnostic Complete"
echo "============================================"
echo ""
echo "Review the output above and address any missing components."
echo "PHASE 0 requires: Git, Docker, Python 3.12+, Tailscale, SSH"
echo "PHASE 7+ requires: Ollama, CUDA, GPU drivers"
