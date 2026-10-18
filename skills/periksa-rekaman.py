#!/usr/bin/env python3
"""Periksa satu berkas rekaman hasil generate.

Pakai:
    python3 skills/periksa-rekaman.py <berkas-rekaman.json> [--input <berkas-input.json>]

Yang diperiksa:
  1. Rekaman valid terhadap skills/rekaman.schema.json
  2. keluaran_skill valid terhadap output.schema.json milik skill yang dipakai
  3. dna_lock_sha256 cocok dengan dna_lock yang tersimpan
     -> ini penegak aturan "dna_lock dilarang beda antar prompt"
  4. input_sha256 cocok dengan berkas input (hanya jika --input diberikan)
  5. Setiap prompt punya tepat satu entri jejak.gambar, urutannya sama
  6. versi_skill di jejak sama dengan di keluaran_skill
  7. Konsistensi status vs aset vs catatan_qc

Keluar dengan kode 1 kalau ada yang gagal, supaya bisa dipakai di CI.

Butuh: pip install jsonschema
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    sys.exit("Butuh paket jsonschema. Jalankan: pip install jsonschema")

AKAR = Path(__file__).resolve().parent


def muat(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def kanon(obj) -> str:
    """Kanonkan JSON ala RFC 8785 (JCS): kunci terurut, tanpa spasi.

    Wajib dilakukan sebelum hashing. Tanpa ini, input yang sama dengan urutan
    kunci berbeda menghasilkan hash berbeda.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_teks(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class Lapor:
    def __init__(self) -> None:
        self.gagal = 0

    def ok(self, pesan: str) -> None:
        print(f"  OK   {pesan}")

    def salah(self, pesan: str) -> None:
        self.gagal += 1
        print(f"  GAGAL {pesan}")

    def nilai(self, kondisi: bool, pesan_ok: str, pesan_gagal: str) -> bool:
        if kondisi:
            self.ok(pesan_ok)
        else:
            self.salah(pesan_gagal)
        return kondisi


def validasi(lapor: Lapor, label: str, skema: dict, data, batas: int = 8) -> bool:
    v = Draft202012Validator(skema, format_checker=FormatChecker())
    errs = sorted(v.iter_errors(data), key=lambda e: list(e.path))
    if not errs:
        lapor.ok(label)
        return True
    lapor.salah(f"{label} — {len(errs)} error")
    for e in errs[:batas]:
        jalur = "/" + "/".join(map(str, e.path)) if e.path else "(akar)"
        print(f"         {jalur} -> {e.message[:160]}")
    if len(errs) > batas:
        print(f"         ... dan {len(errs) - batas} error lain")
    return False


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("rekaman", type=Path, help="berkas rekaman JSON")
    ap.add_argument(
        "--input",
        dest="berkas_input",
        type=Path,
        default=None,
        help="berkas input form, untuk memeriksa input_sha256",
    )
    arg = ap.parse_args()

    lapor = Lapor()
    rec = muat(arg.rekaman)

    print(f"\nMemeriksa {arg.rekaman}\n")

    # 1. rekaman vs skema rekaman
    skema_rekaman = muat(AKAR / "rekaman.schema.json")
    validasi(lapor, "rekaman valid terhadap rekaman.schema.json", skema_rekaman, rec)

    jejak = rec.get("jejak", {})
    keluaran = rec.get("keluaran_skill", {})

    # 2. keluaran_skill vs output.schema.json milik skill yang dipakai
    nama_skill = jejak.get("skill")
    if not nama_skill:
        lapor.salah("jejak.skill kosong, tidak bisa menemukan output.schema.json")
    else:
        skema_out = AKAR / nama_skill / "output.schema.json"
        if not skema_out.is_file():
            lapor.salah(f"output.schema.json tidak ada di {skema_out}")
        else:
            validasi(
                lapor,
                f"keluaran_skill valid terhadap {nama_skill}/output.schema.json",
                muat(skema_out),
                keluaran,
            )

    # 3. dna_lock_sha256 — penegak aturan dna_lock
    lock = keluaran.get("dna_lock")
    if not isinstance(lock, str):
        lapor.salah("keluaran_skill.dna_lock bukan string, hash tidak bisa diperiksa")
    else:
        hitung = sha256_teks(lock)
        tersimpan = jejak.get("dna_lock_sha256")
        lapor.nilai(
            hitung == tersimpan,
            "dna_lock_sha256 cocok dengan dna_lock",
            f"dna_lock_sha256 TIDAK cocok — tersimpan {tersimpan}, seharusnya {hitung}. "
            "dna_lock berubah setelah rekaman dibuat, atau hash salah hitung.",
        )

    # 4. input_sha256 — hanya kalau berkas input diberikan
    if arg.berkas_input is not None:
        hitung = sha256_teks(kanon(muat(arg.berkas_input)))
        tersimpan = jejak.get("input_sha256")
        lapor.nilai(
            hitung == tersimpan,
            f"input_sha256 cocok dengan {arg.berkas_input.name}",
            f"input_sha256 TIDAK cocok — tersimpan {tersimpan}, seharusnya {hitung}",
        )
    else:
        print("  LEWAT input_sha256 tidak diperiksa (beri --input untuk memeriksa)")

    # 5. prompt_id 1:1 dan urutannya sama
    pids = [p.get("id") for p in keluaran.get("prompts", [])]
    gids = [g.get("prompt_id") for g in jejak.get("gambar", [])]
    if lapor.nilai(
        pids == gids,
        f"prompt_id cocok 1:1 dan urut ({len(pids)} gambar)",
        f"prompt_id tidak cocok — prompts {pids} vs jejak.gambar {gids}",
    ):
        pass

    # 6. versi_skill konsisten
    lapor.nilai(
        jejak.get("versi_skill") == keluaran.get("versi_skill"),
        "versi_skill konsisten antara jejak dan keluaran_skill",
        f"versi_skill beda — jejak {jejak.get('versi_skill')!r} "
        f"vs keluaran {keluaran.get('versi_skill')!r}",
    )

    # 7. konsistensi status vs aset vs catatan_qc
    for g in jejak.get("gambar", []):
        pid = g.get("prompt_id", "?")
        status = g.get("status")
        aset = g.get("aset")
        qc = g.get("catatan_qc") or []
        if status == "gagal_generate" and aset is not None:
            lapor.salah(f"{pid}: status gagal_generate tapi aset tidak null")
        if status != "gagal_generate" and aset is None:
            lapor.salah(f"{pid}: status {status} tapi aset null")
        if status == "lolos_qc" and qc:
            lapor.salah(f"{pid}: status lolos_qc tapi catatan_qc tidak kosong")
        if status in ("gagal_qc", "perlu_cek_manual") and not qc:
            lapor.salah(f"{pid}: status {status} tapi catatan_qc kosong")
        if g.get("seed") is None and not jejak.get("catatan"):
            lapor.salah(
                f"{pid}: seed null tanpa penjelasan di jejak.catatan — "
                "hasil ini tidak bisa diulang dan alasannya tidak tercatat"
            )
    else:
        if jejak.get("gambar"):
            lapor.ok("konsistensi status / aset / catatan_qc / seed")

    print()
    if lapor.gagal:
        print(f"HASIL: {lapor.gagal} pemeriksaan gagal\n")
        return 1
    print("HASIL: semua pemeriksaan lolos\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
