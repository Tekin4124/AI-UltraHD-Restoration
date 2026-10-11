FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /workspace

# Sistem gereksinimleri
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git wget curl ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Repoları çek
RUN git clone https://github.com/Fanghua-Yu/SUPIR.git
RUN git clone https://github.com/sczhou/CodeFormer.git

# SUPIR Gereksinimleri
WORKDIR /workspace/SUPIR
RUN pip install --no-cache-dir \
    llava==1.2.2.post1 \
    transformers==4.37.2 \
    xformers==0.0.24 \
    gradio==4.38.1 \
    diffusers==0.27.0
RUN pip install --no-cache-dir -r requirements.txt

# CodeFormer Gereksinimleri
WORKDIR /workspace/CodeFormer
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 basicsr/setup.py develop
RUN python3 scripts/download_pretrained_models.py facelib
RUN python3 scripts/download_pretrained_models.py CodeFormer

# Modelleri indirmek için özel scriptimizi kopyalayalım
COPY download_weights.sh /workspace/
RUN chmod +x /workspace/download_weights.sh
# NOT: Ağırlık indirme işlemi build sırasında çok uzun sürebilir,
# Dilerseniz bu satırı yorum satırı yapıp runtime'da da indirebilirsiniz.
# RUN /workspace/download_weights.sh

# Uygulama kodlarını kopyalayalım
COPY app.py webui_security.py /workspace/

WORKDIR /workspace

EXPOSE 7860

CMD ["python3", "app.py"]
