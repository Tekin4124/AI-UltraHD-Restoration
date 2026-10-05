#!/bin/bash
set -e

echo "======================================================"
echo "🚀 AI Ultra HD Super-Resolution: Model Ağırlıkları İndiriliyor..."
echo "======================================================"

WEIGHTS_DIR=${WEIGHTS_DIR:-"/workspace/weights"}
mkdir -p "$WEIGHTS_DIR/SUPIR" "$WEIGHTS_DIR/CodeFormer/weights/facelib" "$WEIGHTS_DIR/CodeFormer/weights/CodeFormer" "$WEIGHTS_DIR/CodeFormer/weights/realesrgan"

# 1. SUPIR & SDXL Ağırlıkları
if [ ! -f "$WEIGHTS_DIR/SUPIR/sd_xl_base_1.0_0.9vae.safetensors" ]; then
    echo "⬇️ SDXL Base 1.0 indiriliyor (6.5 GB)..."
    huggingface-cli download stabilityai/stable-diffusion-xl-base-1.0 sd_xl_base_1.0_0.9vae.safetensors --local-dir "$WEIGHTS_DIR/SUPIR" --local-dir-use-symlinks False
else
    echo "✅ SDXL Base 1.0 mevcut."
fi

if [ ! -f "$WEIGHTS_DIR/SUPIR/SUPIR-v0Q.ckpt" ]; then
    echo "⬇️ SUPIR-v0Q indiriliyor (5.0 GB)..."
    huggingface-cli download camenduru/SUPIR SUPIR-v0Q.ckpt --local-dir "$WEIGHTS_DIR/SUPIR" --local-dir-use-symlinks False
else
    echo "✅ SUPIR-v0Q mevcut."
fi

# 2. OpenCLIP ViT-bigG Ağırlığı
OPENCLIP_DIR="/root/.cache/huggingface/hub/models--laion--CLIP-ViT-bigG-14-laion2B-39B-b160k/snapshots/743c27bd53dfe508a0ade0f50698f99b39d03bec"
mkdir -p "$OPENCLIP_DIR"
if [ ! -f "$OPENCLIP_DIR/open_clip_model.safetensors" ]; then
    echo "⬇️ OpenCLIP ViT-bigG safetensors indiriliyor (9.5 GB)..."
    huggingface-cli download laion/CLIP-ViT-bigG-14-laion2B-39B-b160k open_clip_model.safetensors --local-dir "$OPENCLIP_DIR" --local-dir-use-symlinks False
else
    echo "✅ OpenCLIP ViT-bigG mevcut."
fi

# 3. CodeFormer & FaceLib Ağırlıkları
if [ -d "/workspace/CodeFormer" ]; then
    echo "⬇️ CodeFormer & Real-ESRGAN ağırlıkları kontrol ediliyor..."
    cd /workspace/CodeFormer
    python3 scripts/download_pretrained_models.py facelib || true
    python3 scripts/download_pretrained_models.py CodeFormer || true
    
    if [ ! -f "weights/realesrgan/RealESRGAN_x2plus.pth" ]; then
        mkdir -p weights/realesrgan
        wget -q -c "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/RealESRGAN_x2plus.pth" -O weights/realesrgan/RealESRGAN_x2plus.pth || true
    fi
fi

echo "======================================================"
echo "✅ Tüm yapay zeka ağırlıkları hazır!"
echo "======================================================"

# 4. Qwen Prompt Engineer Modeli (1.5B)
echo "⬇️ Qwen2.5-1.5B-Instruct Prompt Modeli indiriliyor (~2.9 GB)..."
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct --local-dir-use-symlinks False || true

