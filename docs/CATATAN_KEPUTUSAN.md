# Catatan Keputusan & Error

Cek file ini sebelum menulis kode baru. Perbarui setiap fase selesai.

## Keputusan yang sudah disepakati

| Tanggal | Keputusan | Sumber |
|---|---|---|
| 2026-10-15 | Model bisnis: membership Rp149.000 sekali bayar + top-up kredit, tanpa langganan | Brief awal |
| 2026-10-15 | Pembayaran via Lynk.id | Brief awal |
| 2026-10-15 | Mobile-first, sidebar gelap, min. 3 tema gelap | Brief awal |
| 2026-10-15 | Google Flow **tidak** dipakai (produk konsumen, tanpa API) | Verifikasi lisensi |
| 2026-10-15 | Kredit langganan web Kling **tidak** dipakai; hanya Kling API resmi (prabayar) atau agregator | Verifikasi lisensi |
| 2026-10-15 | Suno **tidak** dipakai (tidak ada API publik resmi) | Verifikasi lisensi |
| 2026-10-15 | BRIA RMBG 2.0 versi open-weights **tidak** dipakai (CC BY-NC) | Verifikasi lisensi |
| 2026-10-15 | **Setiap menu = generator mandiri** (input → generate → hasil). Alur antar tool hanya pintasan opsional ("Pakai DNA", "Kirim ke…") | Koreksi pemilik produk |
| 2026-10-15 | DNA Produk & Karakter: input upload foto/teks → output sheet konsisten multi-sudut + profil tersimpan | Koreksi pemilik produk |
| 2026-10-15 | Pemilik produk membangun website sendiri dengan aplikasi lain. Tugas Claude: menyusun skill per tool (instruksi Bahasa Indonesia + JSON schema), satu per satu, diuji bergantian. Folder `skills/` | Arahan pemilik produk |
| 2026-10-15 | Prompt gambar ditulis dalam bahasa Inggris (paling akurat untuk engine), teks label tetap sesuai aslinya | Skill 01 |
| 2026-10-15 | Konsistensi pakai pola bintang: anchor dulu, semua gambar lain merujuk anchor + foto user | Skill 01 |
| 2026-10-15 | Platform tes skill: Gemini Canvas. Engine gambar utama untuk tes: GPT Image (jadi salah satu pilihan engine, bukan satu-satunya) | Arahan pemilik produk |
| 2026-10-15 | Skill 01 v1.1.0: aturan per engine (GPT Image: kata photorealistic sekali, rasio hanya 1:1/2:3/3:2) + schema versi Gemini | Skill 01 |
| 2026-10-18 | REA (`rea-agents` v6.7.0) dipakai sebagai alat analisa shipped artifact web. Skill + `.mcp.json` disimpan di repo agar tidak hilang saat container sesi cloud dihapus. Lihat `docs/REA_SETUP.md` | Arahan pemilik produk |
| 2026-10-18 | Batas pemakaian REA: membaca & menganalisa kode web yang sudah terkirim ke browser untuk memahami pola implementasi — **bukan** menyalin utuh website pihak lain untuk diterbitkan sebagai milik nexamind | Arahan pemilik produk |

## Menunggu persetujuan

- Alur video multi-scene (draft 480p, review per klip, gabung otomatis): tetap ada di Studio Animasi/Storyboard, atau dihapus?
- Stack: Vercel Pro + Supabase + Cloudflare R2 + Trigger.dev + Upstash
- Pilihan model per tool (lihat tabel verifikasi di rencana build)
- File "sistem harga nexamind.ai" (wajib sebelum Fase 1 bagian kredit)

## Bug & solusi

| Tanggal | Bug | Penyebab | Solusi |
|---|---|---|---|
| 2026-10-15 | Aplikasi tes di Gemini Canvas menampilkan gambar placeholder (bentuk ungu) dan meminta API key saat diminta generate gambar | Canvas hanya bisa memakai model Google tanpa API key; GPT Image butuh key OpenAI. Gemini membuat placeholder sendiri dan menggabung sudut jadi 1 sheet | Larang placeholder di `CANVAS_PROMPT.md`. Generate otomatis di Canvas hanya untuk Nano Banana (`CANVAS_PROMPT_GENERATE.md`). GPT Image dites manual di ChatGPT. API key tidak boleh ditaruh di Canvas |
