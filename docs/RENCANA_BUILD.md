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
| `projects` | (opsional) folder pengelompokan hasil; tidak wajib untuk generate |
| `jobs` | setiap generate: tool, model, input, status, kredit di-hold, id job provider, kode error |
| `assets` | semua file: jenis, lokasi R2, ukuran, durasi, asal job, induk aset, masa simpan |
| `notifications`, `referrals`, `moderation_logs`, `audit_logs` | pendukung |

Semua tabel milik user dilindungi RLS (user hanya bisa membaca datanya sendiri).

---

## 3. Prinsip: setiap menu = generator mandiri (revisi 2026-10-15)

Setiap menu bisa langsung dipakai sendiri: **isi input → klik Generate → hasil jadi.**
Tidak ada alur bertahap yang wajib. Fitur penghubung hanya **pintasan opsional**:
- Dropdown **"Pakai DNA"** (opsional) di tool gambar & video, agar karakter/produk tetap konsisten.
- Tombol **"Kirim ke…"** (opsional) di kartu hasil, untuk memakai hasil di tool lain tanpa unduh-unggah.

### Spesifikasi input → output per tool

| Menu | Input user | Output |
|---|---|---|
| **DNA Produk & Karakter** | Upload 1–4 foto produk/karakter **atau** deskripsi teks; jenis (produk/karakter); gaya | Sheet konsisten. Karakter: 4 sudut (depan, samping, belakang, 3/4) + 3 ekspresi. Produk: 4 sudut + packshot latar putih + 1 foto lifestyle. Tersimpan sebagai profil DNA |
| Buat Gambar | Prompt, opsional foto referensi, gaya, rasio, jumlah (1–4) | 1–4 gambar |
| Buat Mascot | Deskripsi atau upload logo/foto, gaya (3D, kartun, chibi, flat) | Mascot + 3 pose |
| Buat Banner | Foto produk, judul, teks promo, ukuran (Feed, Story, marketplace) | Banner siap pakai |
| Virtual Try On | Foto orang + foto pakaian | Foto orang memakai pakaian tersebut |
| Extract Image | Foto + nama objek yang diambil | Objek PNG transparan |
| Design PRO | Foto produk, nama, harga, gaya | Materi jualan (poster/katalog/feed) |
| Remove Background | Foto | PNG transparan |
| Upscale | Foto + 2x/4x | Foto resolusi tinggi |
| Buat Video | Prompt, opsional gambar awal (dan akhir), durasi, rasio, model | 1 klip video |
| Motion Control | Foto karakter + video gerakan referensi | Video karakter meniru gerakan |
| Vision Prompt | Upload gambar/video | Prompt siap pakai (tombol salin / kirim ke Buat Gambar/Video) |
| Gabung Video | Upload/pilih beberapa klip, opsional audio & subtitle | 1 file MP4 |
| Ide Konten | Niche/produk, platform | Daftar ide + hook |
| Storyboard | Brief/ide, jumlah scene, jenis (UGC/animasi) | Daftar scene + prompt per scene (+ opsional gambar per scene) |
| Studio Animasi | Karakter (upload/DNA) + cerita singkat | Klip animasi |
| Script Voice Over | Topik/produk, durasi, gaya bahasa | Naskah VO |
| Product Finder | Kategori/kata kunci | Rekomendasi produk + alasan (analisis AI) |
| Campaign Blueprint | Produk + target | Rencana kampanye |
| Promo Planner | Produk + periode | Kalender promo |
| Music | Mood, genre, durasi | Track musik |
| Text to Speech | Naskah + pilihan suara | File audio |

Semua tool memakai komponen yang sama: form sederhana → biaya kredit di dekat tombol → kartu hasil → tersimpan otomatis di Riwayat.

---

## 4. Alur generate (berlaku untuk semua tool)

```
Isi form ─► Biaya kredit tampil di dekat tombol
   ▼ klik Generate
Server: validasi + moderasi + HOLD kredit (atomik)
   ▼
Antrean: menunggu → diproses → selesai / gagal
   │                              │
   ▼                              ▼
Kredit dipotong (capture)    Kredit dikembalikan otomatis + pesan error yang mudah dipahami
   ▼
Kartu hasil: unduh | generate ulang (biaya tampil) | Kirim ke… (opsional) | simpan sebagai DNA
   ▼
Tersimpan di Riwayat (filter jenis & tanggal, unduh ulang, masa simpan jelas)
```

Catatan: alur video multi-scene (draft 480p → review per klip → final → VO → gabung) dari brief awal **ditunda/menunggu keputusan** — lihat pertanyaan di catatan keputusan.

---

## 5. Urutan fase

Urutan mengikuti usulan pemilik produk, dengan satu penyesuaian: **fondasi (lapisan AI, antrean, storage) dibangun di Fase 1** walau belum ada tool yang memakainya.

| Fase | Isi | Hasil yang bisa dites |
|---|---|---|
| 1 | Auth, membership, kredit (hold/capture/refund), top-up Lynk.id, dashboard kosong, admin + 2FA, fondasi | Daftar, bayar (sandbox), saldo bertambah, admin login 2FA |
| 2 | DNA Produk & Karakter + Buat Gambar + Mascot + Banner | Upload foto → sheet konsisten; generate gambar dengan/tanpa DNA |
| 3 | Remove BG, Upscale, Extract, Virtual Try On, Design PRO | Semua tool memakai form & kartu hasil yang sama |
| 4 | Ide Konten, Storyboard, Script VO | Masing-masing generate langsung |
| 5 | Buat Video (1 klip, langsung generate) | Prompt/gambar → klip |
| 6 | Motion Control + Vision Prompt + Studio Animasi | Masing-masing generate langsung |
| 7 | TTS + Music | Naskah → audio, mood → musik |
| 8 | Gabung Video + export | Upload klip → MP4 9:16/1:1/16:9 |
| 9 | Affiliate tools | Product Finder, Campaign Blueprint, Promo Planner |
| 10 | Asisten AI, Referral, penyempurnaan | — |

---

## 6. Fondasi yang dibuat lebih dulu

1. **Lapisan pemanggil AI** (`lib/ai`) — satu fungsi `runModel()` + adapter per provider + registri model (kemampuan, biaya, resolusi) + penerjemah error.
2. **Mesin kredit** — fungsi Postgres atomik `credit_hold / capture / release / refund`, buku besar, mode admin + batas harian.
3. **Sistem antrean** — tabel `jobs` + task Trigger.dev + status live via Supabase Realtime + refund otomatis saat gagal.
4. **Storage** — upload/unduh langsung ke R2, registri aset, pembersihan otomatis saat masa simpan habis.
5. **Registri tool** — satu file konfigurasi per tool (isian, pilihan gaya, model, biaya) → halaman tool terbentuk otomatis.
6. **Komponen UI** — AppShell (sidebar + header + pil saldo), GenerateForm, ResultCard (dengan "Kirim ke…" opsional), JobStatus, CostBadge, ConfirmCostDialog, EmptyState, 3 tema gelap.
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
