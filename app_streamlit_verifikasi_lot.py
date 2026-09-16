import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Sistem Verifikasi Nomor Lot Produksi",
    layout="centered"
)


st.markdown(
    """
    <style>
    .app-title-row {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.2rem;
    }
    .app-title-icon {
        font-size: clamp(1.4rem, 4vw, 2rem);
        line-height: 1;
    }
    .app-title {
        font-size: clamp(1.15rem, 3.4vw, 2rem);
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        line-height: 1.25;
        margin: 0;
        padding: 0;
    }
    .app-subtitle {
        color: #9CA3AF;
        font-size: 0.9rem;
        margin: 0 0 1rem 0;
    }
    </style>
    <div class="app-title-row">
        <span class="app-title-icon"></span>
        <h1 class="app-title">Sistem Verifikasi Nomor Lot Produksi </h1>
    </div>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    kandidat_file = [
        "HASIL_PEMISAHAN_CODE_UNIK.xlsx",
        "CODE_UNIK.xlsx",
        "CODE UNIK.xlsx",
    ]
    file_path = next((f for f in kandidat_file if os.path.exists(f)), None)
    if file_path is None:
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

df = load_data()

if df is None:
    st.error(" Database tidak ditemukan. Harap pastikan file 'HASIL_PEMISAHAN_CODE_UNIK.xlsx' tersedia.")
else:
    st.info(f"📊 Total Data Terdaftar dalam Database: **{len(df):,}** baris")

    st.markdown("---")
    st.subheader("1. Input Kode Unik")
    kode_input = st.text_input("Masukkan atau Scan Kode Unik Produksi:")

    if st.button(" Cari Data", type="primary", use_container_width=True):
        if not kode_input.strip():
            st.warning(" Silakan masukkan Kode Unik terlebih dahulu!")
        else:
            st.markdown("### 2. Hasil Pencarian Data")
            kode_clean = kode_input.strip()
            hasil = df[df['Kode Unik'].astype(str).str.strip() == kode_clean]

            if not hasil.empty:
                waktu = hasil.iloc[0]['Waktu']
                tgl_jam = pd.to_datetime(waktu)
                nomor_lot = f"LOT-{tgl_jam.strftime('%Y%m%d')}-{tgl_jam.strftime('%H%M%S')}"

                st.success("**BERHASIL: PRODUK ALDERON ASLI !**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Nomor Lot Produksi", value=nomor_lot)
                with col2:
                    st.metric(label="Kode Unik Valid", value=kode_clean)

                st.markdown("#### Detail Informasi Produksi:")
                st.json({
                    "Status": "Berhasil / Valid",
                    "Kode Unik": kode_clean,
                    "Nomor Lot Produksi": nomor_lot,
                    "Waktu Produksi Full": str(waktu),
                    "Tanggal Produksi": tgl_jam.strftime("%d %B %Y"),
                    "Jam Produksi": tgl_jam.strftime("%H:%M:%S WIB")
                })
            else:
                st.error("**GAGAL: PRODUK PALSU !**")
                st.warning("Kode Unik yang Anda masukkan tidak terdaftar dalam database produksi.")