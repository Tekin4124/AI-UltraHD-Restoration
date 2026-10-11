import gradio as gr
import os
import subprocess
import shutil
import time
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image

WORKSPACE = "/workspace"
IN_DIR = os.path.join(WORKSPACE, "web_in")
OUT_DIR = os.path.join(WORKSPACE, "web_out")
SUPIR_LOG = os.path.join(WORKSPACE, "supir_exec.log")
CF_LOG = os.path.join(WORKSPACE, "cf_exec.log")

os.makedirs(IN_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

print("🚀 Qwen Prompt Modeli belleğe yükleniyor...")
model_name = "Qwen/Qwen2.5-1.5B-Instruct"
prompt_tokenizer = AutoTokenizer.from_pretrained(model_name)
prompt_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="cuda:0"
)
print("✅ Qwen Prompt Modeli hazır!")

def generate_diffusion_prompt(user_text, current_mode):
    if not user_text or not user_text.strip():
        return update_prompt_default(current_mode)
    try:
        system_prompt = (
            "You are a strict English translator and SDXL prompt engineer. "
            "Translate the user's request into a highly detailed ENGLISH diffusion prompt. "
            "CRITICAL RULES: "
            "1. Output MUST BE 100% IN ENGLISH. NO TURKISH WORDS ALLOWED. "
            "2. Ensure you include: fine micro textures, natural materials, sharp details, skin pores, hair strands, realistic lighting, and depth. "
            "3. Add 'ultra sharp, hyper-detailed texture, 8k uhd, masterpiece' to the end. "
            "4. Only output the comma-separated English prompt, no other text."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text.strip()}
        ]
        text = prompt_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = prompt_tokenizer([text], return_tensors="pt").to("cuda:0")
        with torch.no_grad():
            outputs = prompt_model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.2,
                top_p=0.9,
                do_sample=True
            )
        generated_ids = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, outputs)]
        response = prompt_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        response = response.strip('"').strip("'")
        return response
    except Exception as e:
        print(f"Prompt gen error: {e}")
        return update_prompt_default(current_mode)

def update_prompt_default(mode):
    return "ultra sharp photo, hyper-detailed natural texture, micro details, realistic lighting, fine material weave, razor sharp focus, 8k uhd photorealistic masterpiece"

def run_cmd_with_logging(cmd, cwd, log_file, progress_cb=None, desc_prefix="İşleniyor"):
    with open(log_file, "w") as f:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True
        )
    while proc.poll() is None:
        time.sleep(1.5)
        if os.path.exists(log_file) and progress_cb:
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        m = re.search(r"(\d+)%\|.*\|\s*(\d+/\d+)", last_line)
                        if m:
                            pct = int(m.group(1))
                            step = m.group(2)
                            progress_cb(pct / 100.0, desc=f"{desc_prefix}: {step} ({pct}%)")
                        else:
                            clean = last_line[:60]
                            progress_cb(None, desc=f"{desc_prefix}... {clean}")
            except Exception:
                pass
    return proc.returncode

def process_image(input_img, mode, user_request, prompt_text, cfg_val, steps_val, progress=gr.Progress()):
    if input_img is None:
        return None, None, "⚠️ Lütfen bir görsel yükleyin!"
    
    shutil.rmtree(IN_DIR, ignore_errors=True)
    shutil.rmtree(OUT_DIR, ignore_errors=True)
    os.makedirs(IN_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    
    input_path = os.path.join(IN_DIR, "input.png")
    input_img.save(input_path, format="PNG")
    orig_w, orig_h = input_img.size
    
    start_time = time.time()
    
    final_prompt = prompt_text.strip() if prompt_text and prompt_text.strip() else ""
    if not final_prompt and user_request and user_request.strip():
        progress(0.05, desc="Yapay zeka promptu hazırlıyor...")
        final_prompt = generate_diffusion_prompt(user_request, mode)
    elif not final_prompt:
        final_prompt = update_prompt_default(mode)
        
    final_output_path = None
    
    upscale_ratio = "3" if "Doku" in mode or "Kumaş" in mode or "Detay" in mode else "2"
    
    progress(0.1, desc=f"Adım 1/2: SUPIR {upscale_ratio}x Difüzyon başlıyor (Geniş Kare İzleri Yok Edildi)...")
    supir_out = os.path.join(OUT_DIR, "supir")
    os.makedirs(supir_out, exist_ok=True)
    
    cmd_supir = [
        "python3", "test.py",
        "--img_dir", IN_DIR,
        "--save_dir", supir_out,
        "--no_llava",
        "--loading_half_params",
        "--use_tile_vae",
        "--encoder_tile_size", "1024",
        "--decoder_tile_size", "128",
        "--upscale", upscale_ratio,
        "--edm_steps", str(int(steps_val)),
        "--s_cfg", str(float(cfg_val)),
        "--spt_linear_CFG", "1.0",
        "--s_churn", "5",
        "--color_fix_type", "Wavelet",
        "--a_prompt", final_prompt
    ]
    
    ret1 = run_cmd_with_logging(cmd_supir, os.path.join(WORKSPACE, "SUPIR"), SUPIR_LOG, progress, "SUPIR Difüzyon")
    cand1 = os.path.join(supir_out, "input_0.png")
    
    if not (ret1 == 0 and os.path.exists(cand1)):
        return None, None, f"SUPIR Hatası."

    progress(0.85, desc="Adım 2/2: Real-ESRGAN ile Keskinleştirme...")
    cf_dir = os.path.join(OUT_DIR, "final")
    cmd_esr = [
        "python3", "inference_codeformer.py",
        "-i", cand1,
        "-o", cf_dir,
        "-w", "0.95",
        "-s", "2",
        "--bg_upsampler", "realesrgan",
        "--bg_tile", "400"
    ]
    run_cmd_with_logging(cmd_esr, os.path.join(WORKSPACE, "CodeFormer"), CF_LOG, progress, "Real-ESRGAN")
    cand2 = os.path.join(cf_dir, "final_results", "input_0.png")
    if os.path.exists(cand2):
        final_output_path = cand2
    else:
        final_output_path = cand1

    progress(1.0, desc="Tamamlandı!")
    elapsed = round(time.time() - start_time, 1)
    
    out_img = Image.open(final_output_path)
    out_w, out_h = out_img.size
    size_mb = round(os.path.getsize(final_output_path) / (1024 * 1024), 1)
    
    status_txt = f"✅ İşlem Tamamlandı! ({elapsed} sn)\n📐 Çözünürlük: {orig_w}x{orig_h} ➡️ {out_w}x{out_h} px\n💾 Dosya Boyutu: {size_mb} MB\n📝 Kullanılan Prompt: {final_prompt}"
    return final_output_path, final_output_path, status_txt

with gr.Blocks(title="AI Ultra HD Restoration Hub") as demo:
    gr.HTML("<div style='text-align:center; font-size:26px; font-weight:bold; margin-bottom:6px;'>🚀 AI Ultra HD Super-Resolution Hub</div>")
    
    with gr.Row():
        with gr.Column(scale=1):
            in_img = gr.Image(type="pil", label="📁 Orijinal Görseli Yükle", sources=["upload", "clipboard"])
            
            mode = gr.Radio(
                choices=[
                    "Yüksek Doku & Makro Detay (SUPIR 3x + RealESRGAN -> Ultra HD)",
                    "Portre & Yüz Restorasyonu (CodeFormer + RealESRGAN 4x)",
                    "Hızlı Genel Restorasyon (SUPIR 2x Difüzyon)"
                ],
                value="Yüksek Doku & Makro Detay (SUPIR 3x + RealESRGAN -> Ultra HD)",
                label="🎯 Restorasyon Modu"
            )
            
            with gr.Group():
                user_req_box = gr.Textbox(
                    label="🗣️ Ne Yapılsın? (Doğal Türkçe İstek)",
                    placeholder="Örn: eski fotoğraftaki greni ve bulanıklığı gider, kumaş/nesne dokusunu ve yüz detaylarını netleştir...",
                    lines=3
                )
                ai_prompt_btn = gr.Button("✨ Qwen AI ile Difüzyon Promptu Oluştur", variant="secondary")
            
            prompt_box = gr.Textbox(
                label="✍️ Yönlendirici Prompt",
                value=update_prompt_default("Kumaş"),
                lines=3
            )
            
            with gr.Accordion("⚙️ İleri Düzey Ayarlar", open=False):
                cfg_slider = gr.Slider(minimum=1.0, maximum=10.0, value=5.5, step=0.5, label="CFG Scale (Düşük=Orijinal, Yüksek=Agresif Detay)")
                steps_slider = gr.Slider(minimum=20, maximum=80, value=30, step=5, label="Difüzyon Adım Sayısı (Steps) - Süreyi Etkiler")
                
            run_btn = gr.Button("🚀 Fotoğrafı Netleştir & Ultra HD Büyüt", variant="primary", size="lg")
            
        with gr.Column(scale=1):
            out_img = gr.Image(label="🖼️ Restore Edilmiş Çıktı", type="filepath")
            out_file = gr.File(label="📥 Orijinal Tam Çözünürlüklü Dosyayı İndir (PNG)")
            status_box = gr.Textbox(label="📊 İşlem Durumu", lines=4, interactive=False)
            
    mode.change(fn=update_prompt_default, inputs=[mode], outputs=[prompt_box])
    ai_prompt_btn.click(fn=generate_diffusion_prompt, inputs=[user_req_box, mode], outputs=[prompt_box])
    run_btn.click(
        fn=process_image,
        inputs=[in_img, mode, user_req_box, prompt_box, cfg_slider, steps_slider],
        outputs=[out_img, out_file, status_box]
    )

demo.queue().launch(server_name="0.0.0.0", server_port=7860, share=False, allowed_paths=["/workspace"])
