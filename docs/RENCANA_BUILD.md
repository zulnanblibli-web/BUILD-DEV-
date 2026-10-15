# Rencana Build nexamind.ai

Status: **DRAFT — menunggu persetujuan pemilik produk.** Belum ada kode yang ditulis.
Tanggal: 2026-10-15

---

## 1. Arsitektur

```
 HP / Desktop (browser)
        │
        ▼
 ┌──────────────────────────┐      ┌──────────────────────────┐
 │ Vercel (Pro)             │      │ Supabase                 │
 │ Next.js: halaman + API   │◄────►│ Postgres + Auth + MFA    │
 │ - form, dashboard        │      │ + Realtime (status live) │
 │ - validasi, cek kredit   │      └──────────────────────────┘
 │ - webhook Lynk.id        │                ▲
 └──────────┬───────────────┘                │ update status job
            │ kirim job                      │
            ▼                                │
 ┌──────────────────────────┐      ┌─────────┴────────────────┐
 │ Trigger.dev (antrean)    │─────►│ Provider AI              │
 │ - panggil model AI       │      │ Gemini API (Veo, gambar, │
 │ - polling hasil          │◄─────│ TTS), BytePlus (Seedance)│
 │ - FFmpeg (gabung video)  │      │ Kling API, ElevenLabs,   │
 └──────────┬───────────────┘      │ fal.ai (cadangan)        │
            │ simpan file          └──────────────────────────┘
            ▼
 ┌──────────────────────────┐
 │ Cloudflare R2 (file)     │  ← browser upload/unduh langsung (presigned URL)
 └──────────────────────────┘
```

### Stack

| Bagian | Pilihan | Alasan |
|---|---|---|
| Web + API | Next.js di **Vercel Pro** | Sudah dipakai; paket Hobby dilarang untuk penggunaan komersial |
| Database + Auth | **Supabase** (Postgres) | Login, 2FA admin, RLS, Realtime dalam satu layanan |
| File gambar/video/audio | **Cloudflare R2** | Tanpa biaya bandwidth unduh; cocok untuk video besar |
| Antrean + proses lama | **Trigger.dev** | Tanpa batas waktu Vercel, retry otomatis, bisa jalankan FFmpeg |
| Rate limit | **Upstash Redis** | Batas request per user, murah, serverless |
| Pembayaran | **Lynk.id** webhook | Sesuai model bisnis |
| Error monitoring | Sentry (gratis) | Lihat error di konsol/server tanpa menunggu laporan user |

### Batasan Vercel & solusinya

| Batasan | Dampak | Solusi |
|---|---|---|
| Body request fungsi maks ±4,5 MB | Upload video/foto besar gagal | Browser upload langsung ke R2 via presigned URL |
| Durasi fungsi terbatas (menit) | Generate video & FFmpeg bisa lebih lama | Semua proses lama dijalankan di Trigger.dev, Vercel hanya menerima & mengembalikan status |
| Tidak ada penyimpanan file permanen | File hilang setelah fungsi selesai | Semua file disimpan di R2, database menyimpan alamatnya |
| Hobby = non-komersial | Melanggar syarat Vercel | Wajib Vercel Pro sebelum live |

---

## 2. Skema database (ringkas)

| Tabel | Isi utama |
|---|---|
| `profiles` | user, role (user/admin), status membership, tema, kode referral |
| `payments` | transaksi Lynk.id: ref unik, jenis (membership/topup), nominal, kredit, bonus, status, payload mentah |
| `credit_wallets` | saldo & kredit yang sedang di-hold per user |
| `credit_ledger` | buku besar kredit (hanya tambah, tak pernah diubah): topup, bonus, hold, capture, release, refund, admin |
| `pricing` | harga kredit per tool/model/unit + biaya modal USD (diisi dari file "sistem harga") |
| `fx_rates` | kurs USD/IDR harian (untuk laporan margin, tidak mengubah harga kredit) |
| `admin_spend_daily` | biaya modal admin per hari (batas Rp150.000) |
| `dna_profiles` | DNA Produk & Karakter: nama, deskripsi, atribut, aset referensi |
| `projects` | wadah kerja: judul, rasio, status, langkah terakhir |
| `scenes` | per project: urutan, prompt JSON, durasi, referensi, klip draft, klip final, status setuju |
| `jobs` | setiap generate: tool, model, input, status, kredit di-hold, id job provider, kode error |
| `assets` | semua file: jenis, lokasi R2, ukuran, durasi, asal job, induk aset, masa simpan |
| `notifications`, `referrals`, `moderation_logs`, `audit_logs` | pendukung |

Semua tabel milik user dilindungi RLS (user hanya bisa membaca datanya sendiri).

---

## 3. Alur data antar tools

```
DNA Produk/Karakter ─────────────┐ (referensi otomatis ke semua tool gambar & video)
                                 ▼
Ide Konten → Storyboard → Buat Gambar → Buat Video → Voice Over → Gabung Video → Export
                 ▲                          ▲   ▲
Vision Prompt ───┴──────────────────────────┘   └── Motion Control (opsional per klip)
```

- Semua hasil = `asset` yang terikat ke `project`. Tombol **"Pakai di…"** di kartu hasil mengirim aset ke tool lain tanpa unduh/unggah ulang.
- Project menyimpan langkah terakhir, jadi user bisa menutup halaman dan melanjutkan nanti.

---

## 4. Diagram alur video end-to-end

```
[Project] DNA + Storyboard + Gambar + Prompt JSON (otomatis dari tool sebelumnya)
   │
   ▼
① Pecah scene: 1 scene = 1 klip → user bisa edit prompt JSON tiap scene
   │
   ▼
② Estimasi biaya semua scene ──► [Konfirmasi?] ──tidak──► berhenti, 0 kredit
   │ ya → kredit di-HOLD (dicadangkan, belum terpotong)
   ▼
③ DRAFT 480p semua scene → antrean
   │   status per klip: menunggu → diproses → selesai / gagal (hold dilepas otomatis)
   │   user boleh menutup halaman; hasil tetap tersimpan
   ▼
④ Review per klip:  ✔ setujui | ↻ regenerate (tampil biaya) | ✎ edit prompt lalu ulang
   │
   ▼
⑤ FINAL (720p/1080p) klip yang disetujui → estimasi + konfirmasi lagi
   │   frame terakhir klip N → gambar awal klip N+1 (jika model mendukung)
   │
   ├──► (opsional) Motion Control per klip → menggantikan klip setelah disetujui
   ▼
⑥ Voice Over dari script → bandingkan durasi VO vs video (peringatan jika selisih > 10%)
   ▼
⑦ Gabung (FFmpeg di worker): klip + VO + musik + subtitle → PREVIEW wajib
   ▼
⑧ Export 9:16 (utama) / 1:1 / 16:9 → MP4 di R2 → Riwayat project (masa simpan jelas)

Semua error ditampilkan dalam bahasa user, mis. "Video gagal dibuat karena prompt
mengandung konten yang dilarang. Kredit kamu sudah dikembalikan."
```

Catatan teknis:
- Veo tidak menyediakan 480p, jadi draft 480p memakai Seedance (Mini/Fast). Draft = cek komposisi; hasil final bisa sedikit berbeda jika modelnya beda.
- Kredit: hold saat konfirmasi → capture per klip yang sukses → release otomatis untuk klip gagal.

---

## 5. Urutan fase

Urutan mengikuti usulan pemilik produk, dengan satu penyesuaian: **fondasi (lapisan AI, antrean, storage) dibangun di Fase 1** walau belum ada tool yang memakainya.

| Fase | Isi | Hasil yang bisa dites |
|---|---|---|
| 1 | Auth, membership, kredit (hold/capture/refund), top-up Lynk.id, dashboard kosong, admin + 2FA, fondasi | Daftar, bayar (sandbox), saldo bertambah, admin login 2FA |
| 2 | Buat Gambar + DNA Produk & Karakter | Generate gambar memakai DNA, kredit terpotong benar |
| 3 | Remove BG, Upscale, Extract | 3 tool memakai form & kartu hasil yang sama |
| 4 | Ide Konten, Storyboard, Script VO | Storyboard tersimpan di project |
| 5 | Buat Video + draft + antrean | Alur ①–⑤ |
| 6 | Motion Control + Vision Prompt | Klip diganti, prompt terisi otomatis |
| 7 | TTS + Music | Alur ⑥ |
| 8 | Gabung Video + export | Alur ⑦–⑧ |
| 9 | Affiliate tools | Product Finder, Campaign Blueprint, Promo Planner |
| 10 | Asisten AI, Referral, penyempurnaan | — |

---

## 6. Fondasi yang dibuat lebih dulu

1. **Lapisan pemanggil AI** (`lib/ai`) — satu fungsi `runModel()` + adapter per provider + registri model (kemampuan, biaya, resolusi) + penerjemah error.
2. **Mesin kredit** — fungsi Postgres atomik `credit_hold / capture / release / refund`, buku besar, mode admin + batas harian.
3. **Sistem antrean** — tabel `jobs` + task Trigger.dev + status live via Supabase Realtime + refund otomatis saat gagal.
4. **Storage** — upload/unduh langsung ke R2, registri aset, pembersihan otomatis saat masa simpan habis.
5. **Registri tool** — satu file konfigurasi per tool (isian, pilihan gaya, model, biaya) → halaman tool terbentuk otomatis.
6. **Komponen UI** — AppShell (sidebar + header + pil saldo), GenerateForm, ResultCard (dengan "Pakai di…"), JobStatus, CostBadge, ConfirmCostDialog, EmptyState, 3 tema gelap.
7. **Pengaman** — validasi input (zod), rate limit, moderasi prompt, audit log.

---

## 7. Verifikasi lisensi model AI (2026-10-15)

Catatan: halaman resmi provider tidak bisa dibuka langsung dari lingkungan kerja ini (jaringan dibatasi). Temuan di bawah berasal dari hasil pencarian; yang bertanda ⚠️ bersumber pihak ketiga dan **wajib dicek ulang di halaman resmi sebelum fase terkait**.

| Model / layanan | Boleh untuk layanan komersial yang dijual ulang? | Jalur API | Penagihan |
|---|---|---|---|
| Google Flow | ❌ Tidak. Produk langganan konsumen, tanpa API | — | Langganan konsumen |
| Veo 3.1 / Fast / Lite | ✅ Ya, lewat paid tier. Syarat: developer 18+, tidak membangun model pesaing, patuhi Prohibited Use Policy | Gemini API / Vertex AI | Pascabayar (Google Cloud Billing) |
| Seedance Mini / Fast / 2.5 | ✅ Ya lewat API resmi. ⚠️ Ketersediaan 2.5 di BytePlus internasional belum pasti | BytePlus ModelArk; cadangan: fal.ai | Per token, bayar sesuai pemakaian; hanya video sukses yang ditagih ⚠️ |
| Kling (motion control) | ✅ Ya lewat API. ❌ Kredit langganan web tidak bisa dipakai di API | Kling API resmi; cadangan: fal.ai | Prabayar resource package, kedaluwarsa 30/180 hari ⚠️ |
| fal.ai (agregator) | ✅ Hasil boleh dipakai komersial; ❌ menjual ulang akses API mentah butuh izin tertulis | fal.ai | Prabayar kredit |
| Gambar: Nano Banana (Gemini Image) | ✅ Ya (paid tier) | Gemini API | Pascabayar |
| Gambar: Seedream | ✅ Ya | BytePlus ModelArk / fal.ai | Bayar sesuai pemakaian |
| Remove BG: BRIA RMBG 2.0 open weights | ❌ Tidak (CC BY-NC); ✅ hanya lewat API/lisensi berbayar BRIA | BRIA API | Berbayar |
| Remove BG: BiRefNet | ✅ Kemungkinan (⚠️ lisensi MIT belum terverifikasi) | fal.ai | Prabayar |
| Upscale: Real-ESRGAN / Topaz | ✅ Ya (cek lisensi saat Fase 3) | fal.ai / Topaz API | Prabayar |
| TTS: ElevenLabs | ✅ Hanya di plan berbayar (Starter ke atas); paket gratis tanpa hak komersial | ElevenLabs API | Langganan bulanan prabayar + overage |
| TTS: Gemini TTS | ✅ Ya (paid tier) | Gemini API | Pascabayar |
| Musik: ElevenLabs Music | ✅ Ya di plan berbayar ⚠️ | ElevenLabs API | Kredit plan bulanan |
| Musik: Lyria (Google) | ✅ Ya (paid tier) ⚠️ | Gemini API / Vertex AI | Pascabayar |
| Musik: Suno | ❌ Tidak. Belum ada API publik resmi; wrapper tidak resmi berisiko melanggar ToS | — | — |
| Teks/LLM (asisten, ide, storyboard, script) | ✅ Ya | Gemini API (mendukung input video untuk Vision Prompt) / Claude API | Pascabayar / prabayar |
