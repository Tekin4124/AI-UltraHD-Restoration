#!/bin/bash
set -e

echo "=========================================================="
echo "⚡ AI Ultra HD Restoration - Tek Tıkla Sunucu Kurulumu"
echo "=========================================================="

# 1. Paketler
echo "📦 Gerekli kütüphaneler kuruluyor..."
pip install -q gradio>=6.0.0 huggingface-hub open-clip-torch==2.24.0 einops omegaconf pytorch-lightning timm lpips facexlib basicsr
pip install -q --no-deps https://download.pytorch.org/whl/cu124/xformers-0.0.29.post3-cp311-cp311-manylinux_2_28_x86_64.whl || true

# 2. CodeFormer
if [ ! -d "/workspace/CodeFormer" ]; then
    echo "📥 CodeFormer klonlanıyor..."
    git clone https://github.com/sczhou/CodeFormer.git /workspace/CodeFormer
    echo '__version__ = "1.4.2"\n__gitsha__ = "none"' > /workspace/CodeFormer/basicsr/version.py
fi

# 3. SUPIR
if [ ! -d "/workspace/SUPIR" ]; then
    echo "📥 SUPIR klonlanıyor..."
    git clone https://github.com/Fanghua-Yu/SUPIR.git /workspace/SUPIR
fi

# 4. Yamalar
echo "🔧 Uyumluluk yamaları uygulanıyor..."
python3 -c '
path = "/opt/conda/lib/python3.11/site-packages/open_clip/factory.py"
try:
    text = open(path).read()
    old_fn = "def load_state_dict(checkpoint_path: str, map_location=\x27cpu\x27):\n    checkpoint = torch.load(checkpoint_path, map_location=map_location)"
    new_fn = "def load_state_dict(checkpoint_path: str, map_location=\x27cpu\x27):\n    if checkpoint_path.endswith(\x27.safetensors\x27):\n        import safetensors.torch\n        return safetensors.torch.load_file(checkpoint_path, device=map_location)\n    try:\n        checkpoint = torch.load(checkpoint_path, map_location=map_location, weights_only=False)\n    except TypeError:\n        checkpoint = torch.load(checkpoint_path, map_location=map_location)"
    if old_fn in text:
        open(path, "w").write(text.replace(old_fn, new_fn))
except Exception as e:
    pass
'

sed -i "s/captions = \[\]/captions = \[''\]/" /workspace/SUPIR/test.py 2>/dev/null || true

cat << 'EOF' > /workspace/SUPIR/CKPT_PTH.py
LLAVA_CLIP_PATH = None
LLAVA_MODEL_PATH = None
SDXL_CLIP1_PATH = None
SDXL_CLIP2_CKPT_PTH = '/root/.cache/huggingface/hub/models--laion--CLIP-ViT-bigG-14-laion2B-39B-b160k/snapshots/743c27bd53dfe508a0ade0f50698f99b39d03bec/open_clip_model.safetensors'
EOF

# 5. Ağırlıklar
bash download_weights.sh

# 6. WebUI Başlat
echo "🚀 WebUI Başlatılıyor (Port 7860)..."
python3 app.py
