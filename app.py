import io
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# =========================================================
# 1. KONFIGURASI HALAMAN & TEMA (HARUS PALING ATAS)
# =========================================================
st.set_page_config(
    page_title="Analisis Jarak Pandang - Bina Marga",
    page_icon="🛣️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #f4f6f9; }
    [data-testid="stSidebar"] { background-color: #e3e8ee; }
    h1 { color: #1b4332; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Inisialisasi Session State untuk menyimpan riwayat tabel
if 'riwayat_jph' not in st.session_state:
    st.session_state.riwayat_jph = []
if 'riwayat_jpm' not in st.session_state:
    st.session_state.riwayat_jpm = []

# =========================================================
# 2. MODUL 1: JARAK PANDANG HENTI (JPH)
# =========================================================
def modul_jph():
    st.title("🛣️ Kalkulator Jarak Pandang Henti (JPH)")
    st.caption("Aplikasi Perhitungan Geometri Jalan Berdasarkan **Pedoman Desain Geometrik Jalan (Bina Marga 2021)**")
    st.markdown("---")

    # Sidebar Parameter JPH
    st.sidebar.header("📋 Parameter Perencanaan (JPH)")
    vr = st.sidebar.number_input("Kecepatan Rencana / Desain (VR) [km/jam]", min_value=20, max_value=120, value=80, step=5)
    g_percent = st.sidebar.number_input("Kelandaian Jalan (G) [%]", min_value=-15.0, max_value=15.0, value=-0.63, step=0.1, format="%.2f")
    jph_lapangan = st.sidebar.number_input("Jarak Pandang Eksisting Lapangan (m) [Opsional]", min_value=0.0, value=150.0, step=5.0)

    with st.sidebar.expander("⚙️ Parameter Standar Bina Marga 2021"):
        t_reaksi = st.number_input("Waktu Tanggap / Reaksi (t) [detik]", min_value=1.0, max_value=5.0, value=2.5, step=0.1)
        a_decel = st.number_input("Tingkat Perlambatan (a) [m/detik²]", min_value=1.0, max_value=10.0, value=3.4, step=0.1)
        g_grav = 9.81

    # Logika Perhitungan
    g_decimal = g_percent / 100.0
    jht = 0.278 * vr * t_reaksi
    f_eq = a_decel / g_grav
    denom = f_eq + g_decimal

    if denom <= 0:
        st.error("⚠️ **Peringatan Bahaya:** Kombinasi kelandaian turunan terlalu curam melebihi batas koefisien gesek! Kendaraan tidak dapat berhenti.")
        st.stop()

    jhf = (vr**2) / (254 * denom)
    jph_total = jht + jhf
    jph_pembulatan = math.ceil(jph_total)
    status_aman = "AMAN" if jph_lapangan >= jph_total else "TIDAK AMAN"

    # Tampilan Hasil & Metrik
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="1. Jarak Tanggap (Jht)", value=f"{jht:.2f} m", delta=f"Waktu Reaksi: {t_reaksi}s", delta_color="off")
    with col2:
        st.metric(label="2. Jarak Pengereman (Jhf)", value=f"{jhf:.2f} m", delta=f"Kelandaian: {g_percent:+.2f}%", delta_color="off")
    with col3:
        st.metric(label="3. Total JPH Desain", value=f"{jph_total:.2f} m", delta=f"Dibulatkan: {jph_pembulatan} m")

    # Tombol Simpan ke Tabel
    if st.button("💾 Simpan Hasil JPH ke Tabel", type="primary"):
        st.session_state.riwayat_jph.append({
            "Kecepatan (km/jam)": vr,
            "Kelandaian (%)": g_percent,
            "Jarak Tanggap (m)": round(jht, 2),
            "Jarak Pengereman (m)": round(jhf, 2),
            "Total JPH (m)": round(jph_total, 2),
            "Jarak Lapangan (m)": jph_lapangan,
            "Status Keamanan": status_aman
        })
        st.success("✅ Data berhasil ditambahkan ke tabel di bawah!")

    st.markdown("---")

    # Evaluasi Keamanan & Grafik
    col_eval1, col_eval2 = st.columns([1, 1])
    with col_eval1:
        st.subheader("🛡️ Evaluasi Keamanan Lokasi")
        if status_aman == "AMAN":
            st.success(f"### **DESAIN AMAN**\n* **Jarak Lapangan:** {jph_lapangan:.2f} m\n* **JPH Minimum:** {jph_total:.2f} m\n* **Kelebihan Jarak:** +{jph_lapangan - jph_total:.2f} m\n\nKondisi ruang bebas pandang di lokasi memenuhi syarat.")
        else:
            st.error(f"### **TIDAK AMAN**\n* **Jarak Lapangan:** {jph_lapangan:.2f} m\n* **JPH Minimum:** {jph_total:.2f} m\n* **Kekurangan Jarak:** -{jph_total - jph_lapangan:.2f} m\n\n**Rekomendasi Teknis:** Turunkan batas Kecepatan Rencana.")

    with col_eval2:
        st.subheader("📊 Grafik Komposisi JPH")
        fig, ax = plt.subplots(figsize=(6, 2.8))
        ax.barh(["JPH Desain"], [jht], color="#2E7D32", label=f"Jht: {jht:.1f} m")
        ax.barh(["JPH Desain"], [jhf], left=[jht], color="#E65100", label=f"Jhf: {jhf:.1f} m")
        ax.set_xlabel("Jarak (meter)")
        ax.set_xlim(0, max(jph_total * 1.25, jph_lapangan * 1.15))
        ax.axvline(x=jph_lapangan, color="red", linestyle="--", linewidth=2, label=f"Batas Lapangan: {jph_lapangan:.0f} m")
        ax.legend(loc="upper right", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")
    
    # Menampilkan Tabel Riwayat & Export Excel
    st.subheader("📑 Tabel Rekapitulasi Data JPH")
    if len(st.session_state.riwayat_jph) > 0:
        df_jph = pd.DataFrame(st.session_state.riwayat_jph)
        st.dataframe(df_jph, use_container_width=True)

        # Proses pembuatan file Excel di memori
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_jph.to_excel(writer, index=False, sheet_name='Rekap JPH')
        
        st.download_button(
            label="📥 Download Excel Rekap JPH",
            data=buffer.getvalue(),
            file_name="Rekap_Data_JPH.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if st.button("🗑️ Hapus Semua Data JPH"):
            st.session_state.riwayat_jph = []
            st.rerun()
    else:
        st.info("Belum ada data yang disimpan. Klik tombol 'Simpan Hasil JPH ke Tabel' untuk mulai merekap.")


# =========================================================
# 3. MODUL 2: JARAK PANDANG MENYUSIP (JPM)
# =========================================================
def modul_jpm():
    st.header("🚗 Jarak Pandang Menyusip (JPM)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Input Kecepatan")
        v = st.number_input("Kecepatan Kendaraan Penyusip (v) [km/jam]", min_value=30.0, max_value=120.0, value=80.0, step=5.0)
        m = st.number_input("Beda Kecepatan dengan Kendaraan Lambat (m) [km/jam]", min_value=10.0, max_value=25.0, value=15.0, step=1.0)

        # Regresi otomatis
        t1_auto = 2.12 + (0.026 * v)
        t2_auto = 6.56 + (0.052 * v)
        a_auto = 2.05 + (0.0035 * v)
        d3_auto = 10.0 + (0.6 * v)

        with st.expander("⚙️ Penyesuaian Parameter Empiris"):
            t1 = st.number_input("Waktu Awal t1 (detik)", value=round(t1_auto, 2), step=0.1)
            t2 = st.number_input("Waktu Lajur Lawan t2 (detik)", value=round(t2_auto, 2), step=0.1)
            a = st.number_input("Percepatan a (km/jam/s)", value=round(a_auto, 2), step=0.05)
            d3 = st.number_input("Jarak Bebas d3 (meter)", value=round(d3_auto, 2), step=5.0)

    with col2:
        d1 = 0.278 * t1 * (v - m + (a * t1 / 2))
        d2 = 0.278 * v * t2
        d4 = (2 / 3) * d2
        jpm_total = d1 + d2 + d3 + d4

        st.subheader("📊 Hasil Perhitungan Komponen JPM")
        df_jpm_komponen = pd.DataFrame({
            "Komponen": ["d1 (Persepsi & Akselerasi)", "d2 (Lajur Lawan)", "d3 (Jarak Bebas)", "d4 (Jarak Lawan)"],
            "Nilai (Meter)": [d1, d2, d3, d4],
        })
        df_jpm_komponen["Nilai (Meter)"] = df_jpm_komponen["Nilai (Meter)"].round(2)
        st.table(df_jpm_komponen.set_index("Komponen"))
        st.metric(label="Total Jarak Pandang Menyusip (JPM) Minimum", value=f"{jpm_total:.2f} m")

    st.markdown("---")
    st.subheader("🛣️ Evaluasi Lapangan & Marka Jalan")
    jarak_lapangan = st.number_input("Jarak Pandang Eksisting Lapangan [meter]", min_value=0.0, value=float(jpm_total + 20.0), step=10.0)
    
    status_marka = "Marka Putus-putus" if jarak_lapangan >= jpm_total else "Marka Utuh (No Passing)"

    if jarak_lapangan >= jpm_total:
        st.success(f"**ZONA DIPERBOLEHKAN MENYUSIP**\n\nJarak lapangan ({jarak_lapangan} m) >= JPM ({jpm_total:.2f} m).\n\n**Rekomendasi Marka:** {status_marka}.")
    else:
        st.error(f"**ZONA DILARANG MENYUSIP (NO PASSING ZONE)**\n\nJarak lapangan ({jarak_lapangan} m) < JPM ({jpm_total:.2f} m).\n\n**Rekomendasi Marka:** {status_marka}.")

    # Tombol Simpan ke Tabel
    if st.button("💾 Simpan Hasil JPM ke Tabel", type="primary"):
        st.session_state.riwayat_jpm.append({
            "Kecepatan Penyusip (v)": v,
            "Beda Kecepatan (m)": m,
            "Komponen d1 (m)": round(d1, 2),
            "Komponen d2 (m)": round(d2, 2),
            "Komponen d3 (m)": round(d3, 2),
            "Komponen d4 (m)": round(d4, 2),
            "Total JPM (m)": round(jpm_total, 2),
            "Jarak Lapangan (m)": jarak_lapangan,
            "Rekomendasi Marka": status_marka
        })
        st.success("✅ Data berhasil ditambahkan ke tabel JPM di bawah!")

    st.markdown("---")
    
    # Menampilkan Tabel Riwayat & Export Excel
    st.subheader("📑 Tabel Rekapitulasi Data JPM")
    if len(st.session_state.riwayat_jpm) > 0:
        df_jpm_rekap = pd.DataFrame(st.session_state.riwayat_jpm)
        st.dataframe(df_jpm_rekap, use_container_width=True)

        buffer_jpm = io.BytesIO()
        with pd.ExcelWriter(buffer_jpm, engine='openpyxl') as writer:
            df_jpm_rekap.to_excel(writer, index=False, sheet_name='Rekap JPM')
        
        st.download_button(
            label="📥 Download Excel Rekap JPM",
            data=buffer_jpm.getvalue(),
            file_name="Rekap_Data_JPM.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if st.button("🗑️ Hapus Semua Data JPM"):
            st.session_state.riwayat_jpm = []
            st.rerun()
    else:
        st.info("Belum ada data yang disimpan. Klik tombol 'Simpan Hasil JPM ke Tabel' untuk mulai merekap.")


# =========================================================
# 4. TAMPILAN UTAMA (TAB NAVIGASI)
# =========================================================
tab_jph, tab_jpm = st.tabs(["Hitung JPH", "Hitung JPM"])

with tab_jph:
    modul_jph()

with tab_jpm:
    modul_jpm()