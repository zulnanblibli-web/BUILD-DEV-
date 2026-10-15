# Prompt untuk Gemini Canvas (aplikasi tes skill 01)

Salin semua teks di dalam kotak di bawah, lalu tempel di Gemini Canvas. Lampirkan 2 file bersamaan:
1. `SKILL.md`
2. `output.schema.gemini.json`

Kalau Canvas menolak lampiran file, buka kedua file itu, salin isinya, lalu tempel di bagian paling bawah pesan dengan judul `=== ISI SKILL.md ===` dan `=== ISI output.schema.gemini.json ===`.

```
Buatkan aplikasi web satu halaman bernama "Tes Skill 01: DNA Produk & Karakter". Tampilan gelap, mobile first, bahasa Indonesia.

FORM (urutan dari atas):
1. Jenis: pilihan "produk" atau "karakter". Wajib.
2. Nama: teks, maksimal 60 karakter. Wajib.
3. Deskripsi: textarea, maksimal 1000 karakter. Opsional.
4. Gaya visual: pilihan "foto_realistis", "ilustrasi_2d", "render_3d", "ikuti_referensi". Default "ikuti_referensi".
5. Engine: pilihan "gpt_image", "nano_banana", "seedream", "flux_kontext". Default "gpt_image".
6. Upload foto: 0 sampai 4 gambar (JPG, PNG, WEBP), masing-masing maksimal 5 MB. Tampilkan thumbnail berurutan dengan label "foto_user_1", "foto_user_2", dan seterusnya. Ada tombol hapus per foto.
7. Ukuran asli (cm): tiga angka tinggi, lebar, dalam. Hanya muncul jika jenis = produk. Opsional.
8. Teks label manual: textarea. Hanya muncul jika jenis = produk. Opsional.
9. Tombol besar "Analisis & Buat DNA".

SAAT TOMBOL DIKLIK:
1. Susun objek JSON input dengan field persis: jenis, nama, deskripsi, gaya_visual, engine, jumlah_foto, ukuran_asli_cm, teks_label_manual.
   - jumlah_foto dihitung otomatis dari jumlah foto yang diupload, jangan diisi manual.
   - ukuran_asli_cm bernilai null jika ketiga angka kosong.
   - deskripsi dan teks_label_manual bernilai "" jika kosong.
2. Panggil model Gemini yang bisa membaca gambar dengan:
   - systemInstruction: seluruh isi file SKILL.md yang saya lampirkan, tanpa diubah satu karakter pun.
   - contents: satu pesan user berisi teks JSON input, diikuti foto-foto sesuai urutan upload (inline base64).
   - generationConfig: responseMimeType "application/json", responseSchema = seluruh isi file output.schema.gemini.json yang saya lampirkan, temperature 0.2.
3. Jika jawaban gagal di-parse sebagai JSON, ulangi panggilan 1 kali. Jika tetap gagal, tampilkan pesan "Terjadi kesalahan, coba lagi" dan tampilkan jawaban mentah di bagian yang bisa dibuka-tutup.
4. Selama proses, tombol dinonaktifkan dan muncul indikator "Menganalisis foto...".

TAMPILAN HASIL:
1. Badge status: hijau "ok", kuning "butuh_input", merah "ditolak". Di bawahnya tampilkan pesan_user.
2. Jika status bukan "ok", berhenti di sini.
3. Kartu "DNA": tampilkan isi dna dalam tabel dua kolom (field, nilai). Warna hex tampil dengan kotak warna kecil di sebelahnya.
4. Kartu "DNA Lock": teks dna_lock dengan tombol "Salin".
5. Daftar kartu prompt, diurutkan berdasarkan urutan. Setiap kartu berisi: nomor urutan, id, tujuan, badge vonis (LANGSUNG hijau, TURUNAN biru, KARANG oranye), rasio, daftar referensi, teks prompt dengan tombol "Salin prompt", negative_prompt (hanya jika tidak kosong) dengan tombol "Salin", dan risiko (hanya jika tidak kosong) dalam kotak peringatan. Kartu "anchor" diberi label "GENERATE PERTAMA".
6. Kartu "Checklist QC": qc_checklist dalam bentuk checkbox yang bisa dicentang.
7. Kartu "Asumsi": daftar asumsi.
8. Tombol "Salin semua JSON" dan "Unduh JSON".

ATURAN:
- Jangan memanggil API gambar apa pun. Aplikasi ini hanya menghasilkan DNA dan prompt.
- Jangan membuat gambar placeholder, SVG, bentuk, atau ilustrasi buatan sendiri untuk mewakili hasil.
- Jangan menyimpan API key apa pun di dalam kode.
- Jangan mengubah, meringkas, atau menerjemahkan isi SKILL.md maupun schema.
```

## Setelah aplikasi jadi

1. Tes dengan data dari `contoh-input-produk.json` dan 2 foto produk.
2. Bandingkan hasilnya dengan `contoh-output-produk.json`. Yang dibandingkan strukturnya dan aturannya, bukan kata per kata.
3. Salin prompt `anchor`, tempel ke ChatGPT bersama foto produk, lalu generate. Setelah itu salin prompt lain, lampirkan foto produk dan hasil anchor.
4. Cek setiap gambar dengan checklist QC.
5. Kirim ke Claude: JSON hasil, gambar hasil, dan bagian yang meleset.
