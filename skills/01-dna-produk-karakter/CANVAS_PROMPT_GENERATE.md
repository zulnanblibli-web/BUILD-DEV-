# Prompt lanjutan Gemini Canvas: generate gambar otomatis (khusus Nano Banana)

Dipakai jika aplikasi tes sudah jadi tapi gambarnya hanya placeholder. Tempel teks di dalam kotak ini ke Canvas yang sama.

Batasan yang perlu diketahui:
- Canvas hanya bisa memakai model milik Google (Gemini, Nano Banana) tanpa API key.
- GPT Image butuh API key OpenAI. API key itu **jangan** dimasukkan ke Canvas, karena kodenya bisa dilihat orang lain. Tes GPT Image dilakukan manual di ChatGPT.

```
Perbaiki aplikasi ini. Gambar di bagian "Hasil Generate Visual" sekarang hanya bentuk placeholder. Ubah menjadi seperti ini:

1. Hapus semua gambar placeholder, SVG, bentuk, atau ilustrasi buatan sendiri. Aplikasi hanya boleh menampilkan gambar asli hasil model.
2. Tambahkan tombol "Generate Gambar" di bawah daftar prompt. Tombol hanya aktif jika status = "ok" dan engine = "nano_banana".
3. Saat tombol diklik, panggil model gambar Gemini (Nano Banana) dengan cara yang sama seperti aplikasi ini memanggil model teks, memakai mekanisme bawaan Canvas tanpa API key di kode.
   a. Generate prompt dengan id "anchor" lebih dulu. Lampirkan foto sesuai field referensi miliknya (foto_user_1 = foto upload pertama, dan seterusnya). Tunggu sampai selesai.
   b. Setelah anchor berhasil, generate prompt lain satu per satu sesuai field urutan. Untuk setiap prompt, lampirkan gambar sesuai field referensinya: "hasil:anchor" = gambar hasil langkah a, "foto_user_N" = foto upload ke N.
   c. Kirim teks prompt persis apa adanya, tanpa ditambah, diringkas, atau diterjemahkan. Rasio gambar mengikuti field rasio.
4. Tampilkan setiap gambar di dalam kartu prompt masing-masing. Jangan digabung menjadi satu sheet. Setiap kartu punya status: menunggu, diproses, selesai, gagal. Ada tombol "Unduh" dan "Ulangi" per gambar. Tombol "Ulangi" memakai prompt dan referensi yang sama persis.
5. Jika anchor gagal, hentikan proses dan jangan generate gambar lain.
6. Jika pemanggilan model gambar ditolak (diminta API key, atau error 401, 403, 404), jangan tampilkan placeholder dan jangan meminta API key. Tampilkan pesan: "Model gambar tidak tersedia di Canvas. Salin prompt per kartu lalu generate manual di Gemini chat atau ChatGPT."
7. Jika engine = "gpt_image", "seedream", atau "flux_kontext", sembunyikan tombol "Generate Gambar" dan tampilkan catatan: "Engine ini dijalankan di luar Canvas. Salin prompt per kartu."
```
