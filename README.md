# 🚀 AI Ultra HD Super-Resolution & Restoration Hub

Bu proje, fotoğrafları bozmadan, plastikleştirmeden ve bulanıklaştırmadan **mikro dokulara, kumaş liflerine ve cilt gözeneklerine kadar** 4K/8K (20 MB - 60 MB) boyutlarında kristal netliğinde restore eden hepsi-bir-arada yapay zeka sistemidir.

---

## 🌟 Neler İçerir?

1. **SUPIR (SDXL Diffusion Tabanlı Restorasyon):** Fotoğrafı körü körüne büyütmez; dikişleri, kumaş liflerini, saç tellerini ve mikro dokuları fotogerçekçi difüzyonla yeniden inşa eder.
2. **Qwen 2.5 AI Prompt Engineer:** Doğal Türkçe isteklerinizi (Örn: *"fotoğraftaki adamın kot pantolonunu netleştir ve kumaşı aşırı belirgin yap"*) otomatik olarak difüzyon modelinin en iyi anlayacağı profesyonel İngilizce yönlendirici prompta çevirir.
3. **Real-ESRGAN x2 / x4:** Kristal netlikte 4800px+ çözünürlük ölçekleme.
4. **CodeFormer:** Yüz portrelerinde kimliği ve yüz hatlarını bozmadan göz, kirpik ve sakal restorasyonu.
5. **Gradio WebUI:** Tarayıcıdan tek tıkla fotoğraf yükleme, mod seçme ve indirme arayüzü.

---

## ⚡ Hızlı Kurulum

### Yöntem 1: Yeni Bir GPU Sunucusunda (Vast.ai / RunPod / Ubuntu + CUDA)

Projeyi sunucuya çekip tek komutla her şeyi başlatabilirsiniz:

```bash
git clone https://github.com/Tekin4124/AI-UltraHD-Restoration.git
cd AI-UltraHD-Restoration
chmod +x start_on_server.sh
./start_on_server.sh
```
> Bu script PyTorch, CUDA 12.4 xFormers, SUPIR, CodeFormer ve Qwen modellerini otomatik kurar ve port 7860 üzerinden WebUI'ı başlatır.

### Yöntem 2: Docker ile Çalıştırma

```bash
docker compose up -d
```

Tarayıcınızdan açın: `http://localhost:7860`

---

## 🎯 Restorasyon Modları

- **👖 Kumaş / Doku / Kot Pantolon Modu:** SUPIR 3x (CFG 4.0, Wavelet Renk Düzeltme) + Real-ESRGAN 2x hibrit. Lif lif dikiş ve kumaş dokusu üretir (~40-50 MB dosya boyutu).
- **👤 Portre / Yüz Modu:** CodeFormer (w=0.75) + Real-ESRGAN 4x. Yüz kimliğini koruyarak pürüzsüz ve keskin yüz çıktısı verir.
- **⚡ Hızlı SUPIR 2x Modu:** Hızlı genel nesne ve manzara keskinleştirme.

---

## 🙏 Teşekkürler & Referanslar (Acknowledgements)

Bu proje, açık kaynak yapay zeka topluluğunun harika çalışmalarını bir araya getiren bir pipeline ve arayüz çözümüdür:
- **[SUPIR](https://github.com/Fanghua-Yu/SUPIR)** — Scaling-Up Text-to-Image Diffusion Models for Photorealistic Image Restoration
- **[CodeFormer](https://github.com/sczhou/CodeFormer)** — Robust Face Restoration Algorithm for Real-World Scenarios
- **[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)** — Practical Algorithms for General Image Restoration
- **[Qwen 2.5](https://github.com/QwenLM/Qwen2.5)** — Powerful LLM by Alibaba Cloud used for prompt engineering
- **[Stability AI SDXL](https://github.com/Stability-AI/generative-models)** — Foundation text-to-image diffusion architecture
