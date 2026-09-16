import pandas as pd
import sys
import os

def load_database():
    """Memuat database dari file Excel, dengan deteksi struktur kolom otomatis."""
    # Cari file yang tersedia (toleran terhadap nama file spasi/underscore)
    kandidat_file = [
        "HASIL_PEMISAHAN_CODE_UNIK.xlsx",
        "CODE_UNIK.xlsx",
        "CODE UNIK.xlsx",
    ]
    file_path = next((f for f in kandidat_file if os.path.exists(f)), None)

    if file_path is None:
        print("[ERROR] File database tidak ditemukan! Cari salah satu dari:", kandidat_file)
        return None

    print(f"Memuat database dari '{file_path}'...")
    df = pd.read_excel(file_path)

    # Jika kolom 'Kode Unik' belum ada, normalisasi strukturnya
    if 'Kode Unik' not in df.columns:
        if df.shape[1] >= 2:
            # File sudah punya kolom terpisah, misal 'WAKTU' & 'NOMOR UNIK'
            # -> tinggal rename kolom ke-1 dan ke-2, JANGAN di-split lagi
            df = df.rename(columns={df.columns[0]: 'Waktu', df.columns[1]: 'Kode Unik'})
        else:
            # Fallback lama: kolom tunggal gabungan "waktu kodeunik"
            col = df.columns[0]
            split_df = df[col].astype(str).str.rsplit(' ', n=1, expand=True)
            split_df.columns = ['Waktu', 'Kode Unik']
            df = split_df

    # Bersihkan whitespace agar pencarian exact-match konsisten
    df['Kode Unik'] = df['Kode Unik'].astype(str).str.strip()
    return df

def cari_nomor_lot(kode_unik, df):
    """
    Validasi dan Pencarian Data berdasarkan Kode Unik:
    Returns: (status: bool, data_lot: dict)
    """
    kode_clean = str(kode_unik).strip()
    
    # Pencarian exact match
    hasil = df[df['Kode Unik'].astype(str).str.strip() == kode_clean]
    
    if not hasil.empty:
        waktu = hasil.iloc[0]['Waktu']
        
        # Format Nomor Lot Produksi (Gabungan/Standardized Lot Number)
        # Contoh format Lot: LOT-YYYYMMDD-HHMMSS atau langsung dari Waktu Produksi
        tgl_jam = pd.to_datetime(waktu)
        lot_number = f"LOT-{tgl_jam.strftime('%Y%m%d')}-{tgl_jam.strftime('%H%M%S')}"
        
        return True, {
            'kode_unik': kode_clean,
            'nomor_lot': lot_number,
            'waktu_produksi': waktu,
            'tanggal': tgl_jam.strftime('%d-%m-%Y'),
            'jam': tgl_jam.strftime('%H:%M:%S WIB')
        }
    else:
        return False, None

def main():
    print("="*60)
    print("      SISTEM VERIFIKASI KODE UNIK & NOMOR LOT PRODUKSI      ")
    print("="*60)
    
    # Load database
    df = load_database()
    if df is None:
        return

    print(f"[INFO] Database berhasil dimuat: {len(df)} data terdaftar.\n")
    
    while True:
        # Step 1: Input Kode Unik
        kode_input = input("-> Masukkan Kode Unik (atau ketik 'exit' untuk keluar): ").strip()
        
        if kode_input.lower() in ['exit', 'keluar', 'q']:
            print("\nTerima kasih telah menggunakan sistem verifikasi.")
            break
            
        if not kode_input:
            print("[WARNING] Kode Unik tidak boleh kosong! Silakan coba lagi.\n")
            continue
            
        # Step 2: Validasi & Pencarian Data
        berhasil, data = cari_nomor_lot(kode_input, df)
        
        # Step 3: Percabangan Hasil (Sesuai Flowchart)
        print("-" * 50)
        if berhasil:
            print("STATUS          : BERHASIL (VALID)")
            print(f"KODE UNIK       : {data['kode_unik']}")
            print(f"NOMOR LOT       : {data['nomor_lot']}")
            print(f"WAKTU PRODUKSI  : {data['waktu_produksi']}")
            print(f"DETAIL TANGGAL  : {data['tanggal']}")
            print(f"DETAIL JAM      : {data['jam']}")
        else:
            print("STATUS          : GAGAL (INVALID)")
            print("KETERANGAN      : Nomor Lot Tidak Ditemukan!")
        print("-" * 50 + "\n")

if __name__ == '__main__':
    main()