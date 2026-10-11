# 🚀 AI Ultra HD Super-Resolution & Restoration Hub

Bu proje; düşük çözünürlüklü, eski veya bulanık fotoğrafları plastikleştirmeden ve yapaylaştırmadan **mikro dokulara, yüzey desenlerine, saç tellerine ve cilt gözeneklerine kadar** 4K/8K kalitesinde kristal netliğinde restore eden hepsi-bir-arada yapay zeka restorasyon merkezidir.

---

## 🌟 Neler İçerir?

1. **SUPIR (SDXL Diffusion Tabanlı Fotogerçekçi Restorasyon):** Fotoğrafı sadece pikselleri büyüterek bulanıklaştırmaz; mikro dokuları, yüzey desenlerini ve ince ayrıntıları fotogerçekçi difüzyon mimarisiyle yeniden inşa eder.
2. **Qwen 2.5 LLM Prompt Engineer:** Doğal Türkçe isteklerinizi (Örn: *"fotoğraftaki detayları keskinleştir, arka plan grenini temizle ve nesne dokularını belirginleştir"*) analiz ederek difüzyon modelinin en iyi anlayacağı profesyonel İngilizce yönlendirici prompta çevirir.
3. **Real-ESRGAN x2 / x4:** Kristal netlikte 4800px+ çözünürlük ölçekleme ve arka plan keskinleştirme.
4. **CodeFormer:** Yüz portrelerinde kimliği ve yüz hatlarını bozmadan göz, kirpik, cilt ve sakal restorasyonu.
5. **Gradio WebUI:** Tarayıcıdan tek tıkla fotoğraf yükleme, mod seçme ve indirme arayüzü.

---

## ⚡ Hızlı Kurulum

### Yöntem 1: Yeni Bir GPU Sunucusunda (Vast.ai / RunPod / Ubuntu + CUDA)

Projeyi sunucuya çekip başlatabilirsiniz. Varsayılan WebUI yalnız `127.0.0.1:7860` üzerinde dinler; uzak sunucuya SSH tüneliyle bağlanabilirsiniz:

```bash
git clone https://github.com/Tekin4124/AI-UltraHD-Restoration.git
cd AI-UltraHD-Restoration
chmod +x start_on_server.sh
./start_on_server.sh
```
> Bu script PyTorch, CUDA 12.4 xFormers, SUPIR, CodeFormer ve Qwen modellerini otomatik kurar. SSH tüneli: `ssh -L 7860:127.0.0.1:7860 kullanici@sunucu`, ardından bilgisayarınızda `http://localhost:7860`.

Doğrudan dış ağda dinletmek gerekiyorsa başlamadan önce `GRADIO_SERVER_NAME=0.0.0.0`, `GRADIO_USER` ve `GRADIO_PASSWORD` tanımlayın. Dış erişimi HTTPS sağlayan bir proxy arkasında sunun.

### Yöntem 2: Docker ile Çalıştırma

```bash
export GRADIO_USER=admin
read -rs -p 'WebUI parolası: ' GRADIO_PASSWORD
echo
export GRADIO_PASSWORD
docker compose up -d --build
```

Tarayıcınızdan açın: `http://localhost:7860`

Compose iki giriş değişkenini konteynere aktarır; eksik veya boş ayarlarda başlatmayı reddeder. Host portu yalnız `127.0.0.1` üzerinde yayınlanır. Uzak erişim için SSH tüneli veya HTTPS proxy kullanın.

Her iki değişken doğrudan çalıştırmada isteğe bağlıdır ancak biri tanımlandıysa diğeri de zorunludur. Dış ağ adresinde parola olmadan başlatma reddedilir. İndirilebilir dosya alanı yalnız `web_out/` dizinidir; modeller, kod ve loglar bu alana konulmamalıdır. Parolayı Git'e eklemeyin; `.env` dosyaları yok sayılır.

Güvenlik ayarı testleri GPU ve model indirme gerektirmez:

```bash
python3 -m unittest discover -s tests
```

---

## 🎯 Restorasyon Modları

- **🎨 Yüksek Doku & Makro Detay Modu:** SUPIR 3x (Wavelet Renk Düzeltme) + Real-ESRGAN hibrit mimarisi. Nesneler, kumaşlar, mimari ve doğa fotoğraflarında derinlemesine doku rekonstrüksiyonu (~40-50 MB kristal netlikte çıktı).
- **👤 Portre & Yüz Restorasyon Modu:** CodeFormer (w=0.75) + Real-ESRGAN 4x. Portrelerde yüz kimliğini bozmadan göz, kirpik ve doğal cilt hatlarını restore eder.
- **⚡ Hızlı Genel Restorasyon:** SUPIR 2x difüzyon ile genel görüntü keskinleştirme ve gürültü giderme.

---

## 🙏 Teşekkürler & Referanslar (Acknowledgements)

Bu proje, açık kaynak yapay zeka topluluğunun harika çalışmalarını bir araya getiren bir pipeline ve arayüz çözümüdür:
- **[SUPIR](https://github.com/Fanghua-Yu/SUPIR)** — Scaling-Up Text-to-Image Diffusion Models for Photorealistic Image Restoration
- **[CodeFormer](https://github.com/sczhou/CodeFormer)** — Robust Face Restoration Algorithm for Real-World Scenarios
- **[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)** — Practical Algorithms for General Image Restoration
- **[Qwen 2.5](https://github.com/QwenLM/Qwen2.5)** — Powerful LLM by Alibaba Cloud used for prompt engineering
- **[Stability AI SDXL](https://github.com/Stability-AI/generative-models)** — Foundation text-to-image diffusion architecture
