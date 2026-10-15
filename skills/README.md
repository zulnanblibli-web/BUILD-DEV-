# Skills nexamind.ai

Setiap folder = satu skill untuk satu tool. Dibuat satu per satu, dites, baru lanjut ke skill berikutnya.

| No | Skill | Status |
|---|---|---|
| 01 | DNA Produk & Karakter | Siap dites |

## Isi setiap folder

| File | Fungsi |
|---|---|
| `SKILL.md` | Instruksi untuk AI (system prompt). Ditempel utuh di kolom instruksi platform |
| `input.schema.json` | Daftar isian form yang dikirim ke AI |
| `output.schema.json` | Bentuk jawaban AI (standar JSON Schema). Untuk platform umum dan untuk website versi sendiri nanti |
| `output.schema.gemini.json` | Versi khusus Gemini (Canvas / Gemini API `responseSchema`). **Ini yang dipakai di Gemini Canvas** |
| `CANVAS_PROMPT.md` | Prompt siap tempel untuk membuat aplikasi tes di Gemini Canvas |
| `contoh-input-*.json` | Contoh isian form |
| `contoh-output-*.json` | Contoh jawaban yang benar. Pakai sebagai pembanding saat tes |

## Cara pakai di Gemini Canvas

Ikuti `01-dna-produk-karakter/CANVAS_PROMPT.md`. File yang dilampirkan ke Canvas hanya 2: `SKILL.md` dan `output.schema.gemini.json`.

## Cara pakai di platform lain (skill 01)

1. Buat 1 asisten AI yang **bisa membaca gambar** di platform pilihanmu.
2. Tempel seluruh isi `SKILL.md` di kolom instruksi.
3. Jika ada opsi output JSON atau schema, tempel isi `output.schema.json`.
4. Kirim pesan berisi JSON input (lihat `contoh-input-produk.json`) dan lampirkan foto sesuai urutan.
5. AI menjawab dengan JSON. Cek `status`:
   - `ok`: lanjut ke langkah 6.
   - `butuh_input` atau `ditolak`: tampilkan `pesan_user` ke user, jangan generate gambar.
6. Jalankan `prompts` ke engine gambar **sesuai `urutan`**:
   - Generate `anchor` dulu dan tunggu sampai selesai.
   - Prompt lain boleh dijalankan bersamaan. Lampirkan gambar sesuai field `referensi` (`hasil:anchor` = gambar hasil anchor).
   - Pakai `rasio` dari setiap prompt. Isi kolom negative prompt hanya jika `negative_prompt` tidak kosong.
7. Cek setiap gambar dengan `qc_checklist`. Gambar yang gagal di-generate ulang, maksimal 2 kali.
8. Simpan JSON `dna` + gambar anchor sebagai profil DNA user. Profil ini dipakai oleh skill lain.
