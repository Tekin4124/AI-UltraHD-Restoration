#!/bin/bash
set -e

echo "🚀 AI Ultra HD Super-Resolution Başlatılıyor..."

# Ağırlıkların eksik olup olmadığını kontrol et
if [ ! -f "/workspace/weights/SUPIR/sd_xl_base_1.0_0.9vae.safetensors" ] || [ ! -f "/workspace/weights/SUPIR/SUPIR-v0Q.ckpt" ]; then
    echo "⚠️ Ağırlıklar eksik tespit edildi, otomatik indirme başlatılıyor..."
    bash /workspace/download_weights.sh
fi

echo "🌐 Web Arayüzü başlatılıyor (Port 7860)..."
exec python3 /workspace/app.py
