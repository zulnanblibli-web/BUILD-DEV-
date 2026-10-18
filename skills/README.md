# Skills nexamind.ai

Setiap folder = satu skill untuk satu tool. Dibuat satu per satu, dites, baru lanjut ke skill berikutnya.

| No | Skill | Status |
|---|---|---|
| 01 | DNA Produk & Karakter | Siap dites |

## Berkas bersama (dipakai semua skill)

| Berkas | Fungsi |
|---|---|
| `rekaman.schema.json` | Bentuk satu baris simpanan hasil generate. Membungkus keluaran AI + jejak yang dihitung kode |
| `periksa-rekaman.py` | Pemeriksa rekaman. Keluar dengan kode 1 kalau ada yang gagal, bisa dipakai di CI |

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
| `contoh-rekaman-*.json` | Contoh satu baris simpanan lengkap (keluaran AI + jejak) |

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
   Bentuk simpanannya ikuti `rekaman.schema.json` — lihat bagian di bawah.

## Cara menyimpan hasil (wajib, supaya hasil bisa diulang)

Simpanan dipisah dua lapis, dan pemisahan ini **tidak boleh dicampur**:

| Lapis | Diisi oleh | Isi |
|---|---|---|
| `keluaran_skill` | AI | Jawaban JSON apa adanya, tanpa diedit |
| `jejak` | Kode | ID, waktu, hash, versi model, seed, lokasi aset, status QC |

Alasan dipisah: AI **tidak bisa** menghitung SHA-256 dan **tidak tahu** seed yang
dipakai engine. Kalau field itu ditaruh di `output.schema.json`, AI akan
mengarang isinya — presisi palsu, lebih berbahaya daripada tidak ada. Jadi
`output.schema.json` tetap bersih sebagai kontrak AI, dan `rekaman.schema.json`
membungkusnya dari luar.

Empat hal yang membuat hasil bisa diulang persis:

1. **`seed`** per gambar. Engine gambar non-deterministik; tanpa seed, hasil yang
   sudah pas tidak bisa dibuat ulang. Kalau engine tidak mengembalikan seed,
   isi `null` dan catat alasannya di `jejak.catatan` — jangan diisi angka karangan.
2. **`engine.versi_model`**. Engine di-update tanpa pemberitahuan. Prompt dan seed
   yang sama bisa beda hasil kalau versi modelnya geser.
3. **`input_sha256`** dan **`foto_sha256`**. Input dikanonkan dulu (RFC 8785 JCS)
   sebelum di-hash, supaya urutan kunci yang berbeda tidak menghasilkan hash berbeda.
4. **`dna_lock_sha256`**. Ini penegak aturan "`dna_lock` dilarang beda antar prompt"
   di `SKILL.md`. Hitung ulang dari setiap prompt yang dikirim ke engine dan
   bandingkan; kalau beda, tolak dan jangan generate.

Periksa setiap rekaman sebelum disimpan:

```bash
pip install jsonschema
python3 skills/periksa-rekaman.py <rekaman.json> --input <input.json>
```

Keluar dengan kode 1 kalau ada yang gagal, jadi bisa dipasang di CI. Contoh
rekaman yang lolos semua pemeriksaan: `01-dna-produk-karakter/contoh-rekaman-produk.json`.
