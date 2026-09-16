import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

BULAN_ID = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}

class AppVerifikasiLot:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Verifikasi Kode Unik & Nomor Lot Produksi")
        self.root.geometry("600x640")
        self.root.resizable(False, False)
        self.root.configure(bg="#F4F6F9")

        # Load Data
        self.df = self.load_database()

        # Build UI
        self.create_widgets()

    def load_database(self):
        kandidat_file = [
            "HASIL_PEMISAHAN_CODE_UNIK.xlsx",
            "CODE_UNIK.xlsx",
            "CODE UNIK.xlsx",
        ]
        file_path = next((f for f in kandidat_file if os.path.exists(f)), None)

        try:
            if file_path is None:
                messagebox.showerror("Error Database", "File database ('CODE_UNIK.xlsx') tidak ditemukan!")
                return None

            df = pd.read_excel(file_path)

            if 'Kode Unik' not in df.columns:
                if df.shape[1] >= 2:
                    # File sudah punya kolom terpisah, misal 'WAKTU' & 'NOMOR UNIK'
                    df = df.rename(columns={df.columns[0]: 'Waktu', df.columns[1]: 'Kode Unik'})
                else:
                    # Fallback lama: kolom tunggal gabungan "waktu kodeunik"
                    col = df.columns[0]
                    split_df = df[col].astype(str).str.rsplit(' ', n=1, expand=True)
                    split_df.columns = ['Waktu', 'Kode Unik']
                    df = split_df

            df['Kode Unik'] = df['Kode Unik'].astype(str).str.strip()
            return df
        except PermissionError:
            messagebox.showerror(
                "Akses Ditolak", 
                "File Excel sedang dibuka! Tutup file Excel terlebih dahulu."
            )
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca database: {e}")
            return None

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1E3A8A", height=75)
        header_frame.pack(fill="x")
        
        lbl_title = tk.Label(
            header_frame, 
            text="VERIFIKASI NOMOR LOT PRODUKSI", 
            font=("Helvetica", 14, "bold"), 
            fg="white", 
            bg="#1E3A8A"
        )
        lbl_title.pack(pady=(12, 2))

        # Content Frame
        content = tk.Frame(self.root, bg="#F4F6F9")
        content.pack(fill="both", expand=True, padx=25, pady=15)

        # Label & Counter Frame
        input_header_frame = tk.Frame(content, bg="#F4F6F9")
        input_header_frame.pack(fill="x", pady=(0, 5))

        lbl_input = tk.Label(input_header_frame, text="Masukkan Kode Unik:", font=("Helvetica", 11, "bold"), bg="#F4F6F9", fg="#1F2937")
        lbl_input.pack(side="left")

        self.lbl_counter = tk.Label(input_header_frame, text="0 / 10 Karakter", font=("Helvetica", 9, "bold"), bg="#F4F6F9", fg="#6B7280")
        self.lbl_counter.pack(side="right")

        # Entry Input
        self.ent_kode = tk.Entry(content, font=("Helvetica", 13), bd=2, relief="groove")
        self.ent_kode.pack(anchor="w", ipady=6, fill="x")
        self.ent_kode.focus()
        
        # Real-time event binding
        self.ent_kode.bind("<KeyRelease>", self.update_counter)
        self.ent_kode.bind("<Return>", lambda event: self.proses_pencarian())

        # Button
        btn_cari = tk.Button(
            content, 
            text="Cari & Validasi Data", 
            font=("Helvetica", 11, "bold"), 
            bg="#2563EB", 
            fg="white", 
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.proses_pencarian
        )
        btn_cari.pack(fill="x", pady=15)

        # Result Card (bingkai luar tipis + shadow-ish look)
        outer = tk.Frame(content, bg="#E5E7EB")
        outer.pack(fill="both", expand=True)

        self.result_frame = tk.Frame(outer, bg="#FFFFFF")
        self.result_frame.pack(fill="both", expand=True, padx=1, pady=1)

        lbl_result_header = tk.Label(
            self.result_frame, text="HASIL PENCARIAN",
            font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#9CA3AF"
        )
        lbl_result_header.pack(anchor="w", padx=20, pady=(16, 4))

        # Wadah konten hasil - dibangun ulang setiap kali pencarian dilakukan
        self.result_content = tk.Frame(self.result_frame, bg="#FFFFFF")
        self.result_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.tampilkan_placeholder()

    def bersihkan_result_content(self):
        for widget in self.result_content.winfo_children():
            widget.destroy()

    def tampilkan_placeholder(self):
        self.bersihkan_result_content()
        tk.Label(
            self.result_content, text="Silakan masukkan Kode Unik untuk memulai pencarian",
            font=("Helvetica", 10, "italic"), bg="#FFFFFF", fg="#9CA3AF"
        ).pack()

    def buat_badge(self, parent, text, bg, fg):
        badge = tk.Frame(parent, bg=bg)
        tk.Label(
            badge, text=text, font=("Helvetica", 10, "bold"),
            bg=bg, fg=fg, padx=12, pady=5
        ).pack()
        return badge

    def buat_info_chip(self, parent, label, value, mono=False):
        chip = tk.Frame(parent, bg="#F9FAFB", highlightbackground="#F3F4F6", highlightthickness=1)
        tk.Label(
            chip, text=label.upper(), font=("Helvetica", 8, "bold"),
            bg="#F9FAFB", fg="#9CA3AF"
        ).pack(anchor="w", padx=12, pady=(8, 0))
        tk.Label(
            chip, text=value,
            font=("Consolas" if mono else "Helvetica", 12, "bold"),
            bg="#F9FAFB", fg="#1F2937"
        ).pack(anchor="w", padx=12, pady=(0, 8))
        return chip

    def update_counter(self, event=None):
        teks = self.ent_kode.get().strip()
        length = len(teks)
        if length == 10:
            self.lbl_counter.config(text=f" {length} / 10 Karakter", fg="#059669")
        elif length < 10:
            self.lbl_counter.config(text=f" {length} / 10 Karakter (Kurang {10-length})", fg="#D97706")
        else:
            self.lbl_counter.config(text=f" {length} / 10 Karakter (Kelebihan {length-10})", fg="#DC2626")

    def proses_pencarian(self):
        if self.df is None:
            messagebox.showerror("Error", "Database belum terhubung!")
            return

        kode_input = self.ent_kode.get().strip()

        if not kode_input:
            messagebox.showwarning("Peringatan", "Kode Unik tidak boleh kosong!")
            return

        # 1. Exact Match
        hasil = self.df[self.df['Kode Unik'].astype(str).str.strip() == kode_input]
        catatan_text = ""

        # 2. Case-Insensitive Match
        if hasil.empty:
            hasil = self.df[self.df['Kode Unik'].astype(str).str.strip().str.lower() == kode_input.lower()]

        # 3. Toleransi Karakter 'I' (i besar) / 'l' (L kecil) / '1'
        if hasil.empty:
            kode_alt = kode_input.replace('I', 'l').replace('1', 'l')
            hasil = self.df[self.df['Kode Unik'].astype(str).str.strip() == kode_alt]

        # 4. Prefix Match (Otomatis cocok jika input kurang 1 karakter)
        if hasil.empty:
            hasil = self.df[self.df['Kode Unik'].astype(str).str.strip().str.startswith(kode_input)]
            if not hasil.empty:
                catatan_text = f"💡 Dicocokkan otomatis berdasarkan awalan kode '{kode_input}'"

        # 5. Partial Substring Match
        if hasil.empty:
            hasil = self.df[self.df['Kode Unik'].astype(str).str.strip().str.contains(kode_input, case=False, regex=False)]
            if not hasil.empty:
                catatan_text = f"💡 Dicocokkan otomatis dengan potongan kode terdekat"

        # Tampilkan Hasil
        self.bersihkan_result_content()

        if not hasil.empty:
            waktu = hasil.iloc[0]['Waktu']
            kode_res = hasil.iloc[0]['Kode Unik']
            tgl_jam = pd.to_datetime(waktu)
            nomor_lot = f"LOT-{tgl_jam.strftime('%Y%m%d')}-{tgl_jam.strftime('%H%M%S')}"
            tanggal_str = f"{tgl_jam.day:02d} {BULAN_ID[tgl_jam.month]} {tgl_jam.year}"
            jam_str = f"{tgl_jam.strftime('%H:%M:%S')} WIB"

            # Badge status
            badge = self.buat_badge(self.result_content, " DATA DITEMUKAN", "#DCFCE7", "#059669")
            badge.pack(anchor="w", pady=(4, 14))

            # Card Nomor Lot (highlight utama)
            lot_card = tk.Frame(self.result_content, bg="#EFF6FF", highlightbackground="#BFDBFE", highlightthickness=1)
            lot_card.pack(fill="x", pady=(0, 14))
            tk.Label(
                lot_card, text="NOMOR LOT PRODUKSI", font=("Helvetica", 8, "bold"),
                bg="#EFF6FF", fg="#2563EB"
            ).pack(anchor="w", padx=14, pady=(10, 0))
            tk.Label(
                lot_card, text=nomor_lot, font=("Consolas", 18, "bold"),
                bg="#EFF6FF", fg="#1E3A8A"
            ).pack(anchor="w", padx=14, pady=(0, 12))

            # Grid chip info: Kode Unik | Tanggal | Jam
            grid = tk.Frame(self.result_content, bg="#FFFFFF")
            grid.pack(fill="x")
            grid.columnconfigure((0, 1), weight=1)

            chip_kode = self.buat_info_chip(grid, "Kode Unik", kode_res, mono=True)
            chip_kode.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))

            chip_tanggal = self.buat_info_chip(grid, "Tanggal Produksi", tanggal_str)
            chip_tanggal.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 6))

            chip_jam = self.buat_info_chip(grid, "Jam Produksi", jam_str)
            chip_jam.grid(row=1, column=0, columnspan=2, sticky="nsew")

            if catatan_text:
                tip = tk.Frame(self.result_content, bg="#FFFBEB", highlightbackground="#FDE68A", highlightthickness=1)
                tip.pack(fill="x", pady=(14, 0))
                tk.Label(
                    tip, text=catatan_text, font=("Helvetica", 9, "italic"),
                    bg="#FFFBEB", fg="#B45309", wraplength=500, justify="left"
                ).pack(anchor="w", padx=12, pady=8)
        else:
            badge = self.buat_badge(self.result_content, " TIDAK DITEMUKAN", "#FEE2E2", "#DC2626")
            badge.pack(anchor="w", pady=(4, 14))
            tk.Label(
                self.result_content,
                text=f"Kode Unik \"{kode_input}\" tidak terdaftar dalam database produksi.",
                font=("Helvetica", 10), bg="#FFFFFF", fg="#6B7280",
                wraplength=500, justify="left"
            ).pack(anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppVerifikasiLot(root)
    root.mainloop()