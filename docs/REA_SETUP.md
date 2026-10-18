# REA (rea-agents) — Setup & Cara Pakai

Tanggal: 2026-10-18

REA = *Reverse Engineer Anything*. Dipakai untuk membaca kode yang sudah
dikirim sebuah aplikasi/website ke klien (shipped artifact), lalu
menjelaskan cara kerjanya. Berguna saat kita mau memahami pola
implementasi sebuah fitur sebelum membangun versi nexamind sendiri.

Paket: [`rea-agents`](https://www.npmjs.com/package/rea-agents) v6.7.0
(153 perintah CLI, 207 tool MCP).

---

## 1. Yang sudah tersimpan di repo ini

| Isi | Lokasi | Fungsi |
|---|---|---|
| Skill REA v42 | `.claude/skills/reverse-engineer-anything/` | Instruksi cara memakai REA. Otomatis aktif di tiap sesi Claude Code. |
| Registrasi MCP | `.mcp.json` | Mendaftarkan server MCP `rea` untuk project ini. |

Keduanya ikut versi project, jadi **tidak hilang** walau container sesi
cloud dihapus.

## 2. Catatan penting

- **Skill ≠ tool.** Skill hanya memberi instruksi. Tool MCP (`mcp__rea__*`)
  baru terbaca saat sesi **mulai**, bukan di tengah sesi. Kalau `.mcp.json`
  baru ditambahkan, tool-nya aktif di sesi berikutnya.
- Selama tool MCP belum aktif, REA tetap bisa dipakai lewat CLI:
  `npx -y rea-agents@6.7.0 <perintah>`.
- Cek kesiapan: `npx -y rea-agents@6.7.0 doctor`

## 3. Engine analisis — harus disediakan sendiri

REA sengaja **tidak** mengunduh engine apa pun. Tanpa engine, perintah
yang butuh engine akan menolak jalan (bukan diam-diam gagal).

| Engine | Environment variable | Keterangan |
|---|---|---|
| Ghidra | `GHIDRA_INSTALL_DIR` | Gratis (NSA). Butuh Ghidra 12.1.x |
| IDA | `REA_IDA_MCP_CONFIG` | Berlisensi |
| jadx | `REA_JADX_MCP_JAR` | Gratis. jadx-headless-mcp 0.7.1 |
| Kuna | `REA_KUNA_COMMAND` | Berlisensi |
| Hopper | `HOPPER_LAUNCHER_PATH` | macOS saja |

**Untuk kebutuhan nexamind (analisa website), engine di atas tidak
diperlukan.** Analisa JavaScript/web bundle tidak memakai engine native.

## 4. Perintah yang relevan untuk analisa website

```bash
npx -y rea-agents@6.7.0 analyze-web-bundle        # ambil + analisa bundle halaman
npx -y rea-agents@6.7.0 export-web-scripts        # simpan script untuk analisa statis
npx -y rea-agents@6.7.0 analyze-javascript-application
npx -y rea-agents@6.7.0 compare-web-captures      # bandingkan dua versi
npx -y rea-agents@6.7.0 capture-web-screenshot
```

## 5. Batasan pemakaian

Membaca dan menganalisa kode yang sudah dikirim ke browser: wajar, sama
seperti `view-source` atau devtools. Dipakai untuk **memahami pola**
implementasi, lalu membangun versi sendiri.

Yang **tidak** dilakukan: menyalin utuh kode/aset website pihak lain lalu
menerbitkannya sebagai milik nexamind. Itu pelanggaran hak cipta dan
risikonya ditanggung pemilik produk.

## 6. Pasang ulang di mesin lain

```bash
npx -y rea-agents@latest setup --yes --all-detected
```

Perintah ini melakukan dua hal, keduanya lokal:
1. menambahkan registrasi MCP `rea` ke config agent (`~/.claude.json`),
   dengan backup ke `~/.claude.json.rea.backup`;
2. memasang skill REA ke direktori skill personal.

Untuk melepas: `npx -y rea-agents@6.7.0 uninstall`
