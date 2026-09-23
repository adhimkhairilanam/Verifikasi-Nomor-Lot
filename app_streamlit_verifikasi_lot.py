import base64
import os
import textwrap
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Portal Verifikasi Produk Alderon",
    layout="wide",
)

# ============================================================
# ===== KAMUS TERJEMAHAN (Indonesia <-> English) =====
# ============================================================
TRANSLATIONS = {
    "ID": {
        "app_title": "Portal Verifikasi Produk Alderon",
        "input_label": "MASUKKAN KODE UNIK:",
        "search_button": "Cari Data",
        "db_not_found": (
            "Database tidak ditemukan. Harap pastikan file"
            " 'HASIL_PEMISAHAN_CODE_UNIK.xlsx' tersedia."
        ),
        "empty_warning": "Silakan masukkan Kode Unik terlebih dahulu!",
        "result_header": "Hasil Pencarian Data",
        "success_msg": "**BERHASIL: PRODUK ALDERON ASLI !**",
        "fail_msg": "**GAGAL: PRODUK PALSU !**",
        "fail_warning": (
            "Kode Unik yang Anda masukkan tidak terdaftar dalam database"
            " produksi."
        ),
        "metric_lot": "Nomor Lot Produksi",
        "metric_kode": "Kode Unik Valid",
        "detail_header": "Detail Informasi Produksi:",
        "json_status": "Status",
        "json_status_val": "Berhasil / Valid",
        "json_kode": "Kode Unik",
        "json_lot": "Nomor Lot Produksi",
        "json_waktu": "Waktu Produksi Full",
        "json_tanggal": "Tanggal Produksi",
        "json_jam": "Jam Produksi",
        "jam_suffix": "WIB",
        "lang_switch_label": "🌐 Bahasa",
    },
    "EN": {
        "app_title": "Alderon Product Verification Portal",
        "input_label": "ENTER UNIQUE CODE:",
        "search_button": "Search Data",
        "db_not_found": (
            "Database not found. Please make sure the file"
            " 'HASIL_PEMISAHAN_CODE_UNIK.xlsx' is available."
        ),
        "empty_warning": "Please enter a Unique Code first!",
        "result_header": "Search Results",
        "success_msg": "**SUCCESS: GENUINE ALDERON PRODUCT !**",
        "fail_msg": "**FAILED: COUNTERFEIT PRODUCT !**",
        "fail_warning": (
            "The Unique Code you entered is not registered in the production"
            " database."
        ),
        "metric_lot": "Production Lot Number",
        "metric_kode": "Valid Unique Code",
        "detail_header": "Production Detail Information:",
        "json_status": "Status",
        "json_status_val": "Success / Valid",
        "json_kode": "Unique Code",
        "json_lot": "Production Lot Number",
        "json_waktu": "Full Production Time",
        "json_tanggal": "Production Date",
        "json_jam": "Production Time",
        "jam_suffix": "WIB",
        "lang_switch_label": "🌐 Language",
    },
}

BULAN_ID = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember",
}


def format_tanggal(tgl_jam, lang):
  """Format tanggal sesuai bahasa aktif (nama bulan ikut berubah)."""
  if lang == "ID":
    return f"{tgl_jam.day:02d} {BULAN_ID[tgl_jam.month]} {tgl_jam.year}"
  return tgl_jam.strftime("%d %B %Y")


def _get_lang_param():
  """Kompatibel dengan Streamlit versi lama & baru."""
  try:
    return st.query_params.get("lang")
  except AttributeError:
    params = st.experimental_get_query_params()
    val = params.get("lang")
    return val[0] if val else None


_query_lang = _get_lang_param()
if _query_lang in ("ID", "EN"):
  st.session_state.lang = _query_lang
elif "lang" not in st.session_state:
  st.session_state.lang = "ID"

t = TRANSLATIONS[st.session_state.lang]


def get_base64_image(path):
  """Baca file gambar lokal dan ubah ke base64 agar bisa di-embed di HTML."""
  if os.path.exists(path):
    with open(path, "rb") as f:
      return base64.b64encode(f.read()).decode()
  return None


LOGO_UPC_PATH = "upc_logo_long__1_.png"
LOGO_ALDERON_PATH = "alderon_logo.png"

logo_id_b64 = get_base64_image("indonesiaa.jpg")
logo_en_b64 = get_base64_image("amerika.jpg")


def flag_class(lang_code):
  return (
      "flag-btn flag-active"
      if st.session_state.lang == lang_code
      else "flag-btn"
  )


flag_switcher_html = f"""
<div class="flag-switcher">
    <a href="?lang=ID" target="_self" class="{flag_class('ID')}">
        <img src="data:image/jpeg;base64,{logo_id_b64}" alt="Indonesia" />
    </a>
    <a href="?lang=EN" target="_self" class="{flag_class('EN')}">
        <img src="data:image/jpeg;base64,{logo_en_b64}" alt="English" />
    </a>
</div>
"""

st.markdown(
    textwrap.dedent(f"""
    <style>
    /* ===== Background Luar Halaman ===== */
    .stApp {{
        background-color: #F1F5F9 !important;
    }}

    /* Sembunyikan header Streamlit agar tidak menutupi border atas */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
        height: 0px !important;
        min-height: 0px !important;
        z-index: 0 !important;
    }}

    /* ===== Kartu Bingkai Utama (Border 4 Sisi) ===== */
    div[data-testid="stMainBlockContainer"],
    .main .block-container {{
        background-color: #FFFFFF !important;
        border: 2.5px solid #7DD3FC !important; /* Garis Biru Muda Soft */
        border-radius: 16px !important;
        padding: 2.5rem 2rem !important;
        margin-top: 1rem !important;
        margin-bottom: 2rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
        width: 94% !important;
        max-width: 1350px !important;
        box-shadow: 0 8px 25px rgba(125, 211, 252, 0.25) !important;
    }}
    
    /* Memaksa semua teks umum menjadi gelap */
    h1, h2, h3, h4, h5, h6, p, span {{
        color: #0F172A !important;
    }}

    /* ===== Bendera Switch Bahasa ===== */
    .flag-switcher {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.7rem;
    }}
    .flag-btn {{
        display: inline-block;
        line-height: 0;
        border-radius: 6px;
        overflow: hidden;
        border: 2px solid transparent;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.18);
        opacity: 0.55;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
    }}
    .flag-btn img {{
        display: block;
        width: 44px;
        height: 30px;
        object-fit: cover;
    }}
    .flag-btn:hover {{
        opacity: 0.9;
        transform: translateY(-1px);
    }}
    .flag-btn.flag-active {{
        opacity: 1;
        border-color: #0B4C8C;
        box-shadow: 0 3px 10px rgba(11, 76, 140, 0.35);
    }}

    /* ===== Header kartu logo ===== */
    .st-key-logo_card {{
        background: #FFFFFF !important;
        border: 1px solid #BFDBFE !important;
        border-bottom: 4px solid #0B4C8C !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 14px rgba(11, 76, 140, 0.08);
        padding: 0.4rem 0.6rem;
        margin-bottom: 1.6rem;
    }}
    .logo-divider-native {{
        width: 1px;
        height: 54px;
        background: #CBD5E1;
        margin: 0 auto;
    }}

    /* ===== Judul ===== */
    .app-title-row {{
        margin-bottom: 0.3rem;
        text-align: center;
    }}
    .app-title {{
        font-size: clamp(1.4rem, 3vw, 2.3rem) !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        line-height: 1.25;
        margin: 0;
        padding: 0;
        color: #0B2A4A !important;
    }}

    /* ===== Label Input ===== */
    label[data-testid="stWidgetLabel"] p,
    .stTextInput label p {{
        color: #00246E !important;
        font-weight: 600 !important;
        font-size: 2.15rem !important;
    }}

    /* Focus Input Box */
    .stTextInput > div:focus-within,
    div[data-testid="stTextInputRootElement"]:focus-within,
    div[data-baseweb="input"]:focus-within {{
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }}

    /* Teks Input Box Hitam */
    .stTextInput input,
    div[data-baseweb="input"] input {{
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        background-color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 2.05rem !important;
    }}
    
    /* ===== Tombol Cari Data ===== */
    div.stButton > button:first-child {{
        background-color: #0B4C8C !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1rem !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }}
    
    div.stButton > button:first-child p,
    div.stButton > button:first-child span {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.50rem !important;
        margin: 0 !important;
    }}

    div.stButton > button:first-child:hover {{
        background-color: #083A6B !important;
        box-shadow: 0 6px 18px rgba(11, 76, 140, 0.3) !important;
        transform: translateY(-2px);
    }}

    /* ===== Alert / Result ===== */
    div[data-testid="stAlert"] p {{
        font-size: 1.35rem !important;
        font-weight: 800 !important;
    }}

    /* ===== Metric ===== */
    div[data-testid="stMetric"] {{
        background: #EAF2FB;
        border: 1px solid #DCE9F7;
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }}

    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] span {{
        color: #000000 !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stMetricValue"] div,
    div[data-testid="stMetricValue"] span {{
        color: #000000 !important;
        font-weight: 800 !important;
    }}

    /* ===== Khusus Teks Detail Informasi Produksi (st.json) Teks dipaksa PUTIH ===== */
    div[data-testid="stJson"] {{
        border-radius: 10px !important;
        padding: 1rem !important;
    }}

    div[data-testid="stJson"] *,
    div[data-testid="stJson"] span,
    div[data-testid="stJson"] div,
    div[data-testid="stJson"] pre,
    div[data-testid="stJson"] code {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}
    </style>
    {flag_switcher_html}
    """),
    unsafe_allow_html=True,
)

# ===== Render Logo =====
with st.container(border=True, key="logo_card"):
  col_upc, col_div, col_alderon = st.columns(
      [3, 0.3, 2.2], vertical_alignment="center"
  )
  with col_upc:
    if os.path.exists(LOGO_UPC_PATH):
      st.image(LOGO_UPC_PATH, width=280)
  with col_div:
    st.markdown(
        '<div class="logo-divider-native"></div>', unsafe_allow_html=True
    )
  with col_alderon:
    if os.path.exists(LOGO_ALDERON_PATH):
      st.image(LOGO_ALDERON_PATH, width=210)

st.markdown(
    '<div class="app-title-row"><h1'
    f' class="app-title">{t["app_title"]}</h1></div>',
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

  if "Kode Unik" not in df.columns:
    if df.shape[1] >= 2:
      df = df.rename(
          columns={df.columns[0]: "Waktu", df.columns[1]: "Kode Unik"}
      )
    else:
      col = df.columns[0]
      split_df = df[col].astype(str).str.rsplit(" ", n=1, expand=True)
      split_df.columns = ["Waktu", "Kode Unik"]
      df = split_df

  df["Kode Unik"] = df["Kode Unik"].astype(str).str.strip()
  return df


df = load_data()

if df is None:
  st.error(t["db_not_found"])
else:
  st.markdown("---")
  kode_input = st.text_input(t["input_label"])

  if st.button(t["search_button"], type="primary", use_container_width=True):
    if not kode_input.strip():
      st.warning(t["empty_warning"])
    else:
      st.markdown(f"### {t['result_header']}")
      kode_clean = kode_input.strip()
      hasil = df[df["Kode Unik"].astype(str).str.strip() == kode_clean]

      if not hasil.empty:
        waktu = hasil.iloc[0]["Waktu"]
        tgl_jam = pd.to_datetime(waktu)
        nomor_lot = (
            f"LOT-{tgl_jam.strftime('%Y%m%d')}-{tgl_jam.strftime('%H%M%S')}"
        )

        st.success(t["success_msg"])

        col1, col2 = st.columns(2)
        with col1:
          st.metric(label=t["metric_lot"], value=nomor_lot)
        with col2:
          st.metric(label=t["metric_kode"], value=kode_clean)

        st.markdown(f"#### {t['detail_header']}")
        st.json({
            t["json_status"]: t["json_status_val"],
            t["json_kode"]: kode_clean,
            t["json_lot"]: nomor_lot,
            t["json_waktu"]: str(waktu),
            t["json_tanggal"]: format_tanggal(tgl_jam, st.session_state.lang),
            t["json_jam"]: f"{tgl_jam.strftime('%H:%M:%S')} {t['jam_suffix']}",
        })
      else:
        st.error(t["fail_msg"])
        st.warning(t["fail_warning"])
