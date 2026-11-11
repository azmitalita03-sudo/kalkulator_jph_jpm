import io
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import streamlit as st

# =========================================================
# 1. KONFIGURASI HALAMAN & TEMA
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

# Inisialisasi Session State
if 'riwayat_jph' not in st.session_state:
    st.session_state.riwayat_jph = []
if 'riwayat_jpm' not in st.session_state:
    st.session_state.riwayat_jpm = []

# =========================================================
# FUNGSI PEMBANTU UNTUK MENGGAMBAR KENDARAAN (VISUALISASI)
# =========================================================
def draw_car(ax, x_center, y_center, text, color, direction='right'):
    """Fungsi untuk menggambar kotak mobil beserta lampu depan/arahnya"""
    car_len, car_wid = 4.5, 1.8
    rect = patches.Rectangle((x_center - car_len/2, y_center - car_wid/2), 
                             car_len, car_wid, color=color, zorder=3, alpha=0.85)
    ax.add_patch(rect)
    ax.text(x_center, y_center, text, ha='center', va='center', 
            color='white', fontweight='bold', fontsize=7, zorder=4)
    
    # Menggambar indikator lampu depan (headlights) untuk arah
    if direction == 'right':
        ax.plot([x_center + car_len/2, x_center + car_len/2], 
                [y_center - car_wid/3, y_center + car_wid/3], color='yellow', lw=2, zorder=4)
    else:
        ax.plot([x_center - car_len/2, x_center - car_len/2], 
                [y_center - car_wid/3, y_center + car_wid/3], color='yellow', lw=2, zorder=4)

# =========================================================
# 2. MODUL 1: JARAK PANDANG HENTI (JPH)
# =========================================================
def modul_jph():
    st.title("🛣️ Kalkulator Jarak Pandang Henti (JPH)")
    st.caption("Aplikasi Perhitungan Geometri Jalan Berdasarkan **Pedoman Desain Geometrik Jalan (Bina Marga 2021)**")
    st.markdown("---")

    st.sidebar.header("📋 Parameter Perencanaan (JPH)")
    vr = st.sidebar.number_input("Kecepatan Rencana / Desain (VR) [km/jam]", min_value=20, max_value=120, value=80, step=5)
    g_percent = st.sidebar.number_input("Kelandaian Jalan (G) [%]", min_value=-15.0, max_value=15.0, value=-0.63, step=0.1, format="%.2f")
    jph_lapangan = st.sidebar.number_input("Jarak Pandang Eksisting Lapangan (m) [Opsional]", min_value=0.0, value=150.0, step=5.0)

    with st.sidebar.expander("⚙️ Parameter Standar Bina Marga 2021"):
        t_reaksi = st.number_input("Waktu Tanggap / Reaksi (t) [detik]", min_value=1.0, max_value=5.0, value=2.5, step=0.1)
        a_decel = st.number_input("Tingkat Perlambatan (a) [m/detik²]", min_value=1.0, max_value=10.0, value=3.4, step=0.1)
        g_grav = 9.81

    # Perhitungan
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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="1. Jarak Tanggap (Jht)", value=f"{jht:.2f} m", delta=f"Waktu Reaksi: {t_reaksi}s", delta_color="off")
    with col2:
        st.metric(label="2. Jarak Pengereman (Jhf)", value=f"{jhf:.2f} m", delta=f"Kelandaian: {g_percent:+.2f}%", delta_color="off")
    with col3:
        st.metric(label="3. Total JPH Desain", value=f"{jph_total:.2f} m", delta=f"Dibulatkan: {jph_pembulatan} m")

    if st.button("💾 Simpan Hasil JPH ke Tabel", type="primary"):
        st.session_state.riwayat_jph.append({
            "Kecepatan (km/jam)": vr, "Kelandaian (%)": g_percent,
            "Jarak Tanggap (m)": round(jht, 2), "Jarak Pengereman (m)": round(jhf, 2),
            "Total JPH (m)": round(jph_total, 2), "Jarak Lapangan (m)": jph_lapangan, "Status": status_aman
        })
        st.success("✅ Data ditambahkan ke tabel!")

    st.markdown("---")
    
    # ---------------- VISUALISASI JPH ----------------
    st.subheader("🚗 Visualisasi Skematik Pergerakan Kendaraan (JPH)")
    fig, ax = plt.subplots(figsize=(10, 3.5))
    
    # Gambar Jalan
    ax.axhline(0, color='gray', lw=1, ls='--') 
    # Gambar Mobil dan Halangan
    draw_car(ax, 0, 0, 'MOBIL', '#1565C0')
    ax.plot(jph_total, 0, marker='X', color='red', markersize=12, label='Halangan')
    
    # Anotasi Panah Jarak
    ax.annotate('', xy=(jht, -1.5), xytext=(0, -1.5), arrowprops=dict(arrowstyle='|-|', color='#2E7D32', lw=2))
    ax.text(jht/2, -2.5, f'Jht (Reaksi)\n{jht:.1f} m', ha='center', va='top', fontsize=9, color='#2E7D32')
    
    ax.annotate('', xy=(jph_total, -1.5), xytext=(jht, -1.5), arrowprops=dict(arrowstyle='|-|', color='#E65100', lw=2))
    ax.text(jht + jhf/2, -2.5, f'Jhf (Pengereman)\n{jhf:.1f} m', ha='center', va='top', fontsize=9, color='#E65100')
    
    ax.axvline(x=jph_lapangan, color="red", linestyle="--", linewidth=1.5)
    ax.text(jph_lapangan, 2, f' Jarak Lapangan ({jph_lapangan}m)', color='red', fontsize=9, va='center')

    ax.set_xlim(-5, max(jph_total, jph_lapangan) + 15)
    ax.set_ylim(-4, 3)
    ax.axis('off')
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("📑 Tabel Rekapitulasi Data JPH")
    if len(st.session_state.riwayat_jph) > 0:
        df_jph = pd.DataFrame(st.session_state.riwayat_jph)
        st.dataframe(df_jph, use_container_width=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_jph.to_excel(writer, index=False, sheet_name='Rekap JPH')
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            st.download_button("📥 Download Excel", data=buffer.getvalue(), file_name="Rekap_JPH.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col_btn2:
            if st.button("🗑️ Hapus Data"):
                st.session_state.riwayat_jph = []
                st.rerun()
    else:
        st.info("Belum ada data yang disimpan.")


# =========================================================
# 3. MODUL 2: JARAK PANDANG MENDAHULUI (JPM)
# =========================================================
def modul_jpm():
    st.header("🚗 Jarak Pandang Mendahului (JPM)")
    st.markdown("Menghitung panjang minimum yang dibutuhkan kendaraan untuk mendahului kendaraan lain di jalan 2-lajur 2-arah tanpa menabrak kendaraan dari arah berlawanan.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Input Kecepatan (V)")
        v = st.number_input("Kecepatan Kendaraan yang Mendahului (v) [km/jam]", min_value=30.0, max_value=120.0, value=80.0, step=5.0)
        m = st.number_input("Beda Kecepatan dengan Kendaraan Lambat (m) [km/jam]", min_value=10.0, max_value=25.0, value=15.0, step=1.0)

        # Regresi otomatis
        t1_auto = 2.12 + (0.026 * v)
        t2_auto = 6.56 + (0.052 * v)
        a_auto = 2.05 + (0.0035 * v)
        d3_auto = 10.0 + (0.6 * v)

        st.info("Berdasarkan kecepatan di atas, parameter empiris dihitung otomatis menggunakan persamaan regresi linier.")

        with st.expander("⚙️ Penyesuaian Parameter Empiris (Manual)"):
            t1 = st.number_input("Waktu Manuver Awal t1 (detik)", value=round(t1_auto, 2), step=0.1)
            t2 = st.number_input("Waktu di Lajur Lawan t2 (detik)", value=round(t2_auto, 2), step=0.1)
            a = st.number_input("Percepatan a (km/jam/detik)", value=round(a_auto, 2), step=0.05)
            d3 = st.number_input("Jarak Bebas d3 (meter)", value=round(d3_auto, 2), step=5.0)

    with col2:
        st.subheader("📐 Rumus Empiris yang Digunakan")
        st.markdown("Parameter waktu dan jarak bebas bergantung pada Kecepatan ($V$):")
        st.latex(r"t_1 = 2.12 + 0.026 \cdot V")
        st.latex(r"t_2 = 6.56 + 0.052 \cdot V")
        st.latex(r"a = 2.05 + 0.0035 \cdot V")
        st.latex(r"d_3 = 10 + 0.6 \cdot V")

    st.markdown("---")
    
    # Perhitungan Komponen JPM
    d1 = 0.278 * t1 * (v - m + (a * t1 / 2))
    d2 = 0.278 * v * t2
    d4 = (2 / 3) * d2
    jpm_total = d1 + d2 + d3 + d4

    st.subheader("📊 Hasil Perhitungan Komponen JPM")
    df_jpm_komponen = pd.DataFrame({
        "Komponen Geometrik": ["d1 (Jarak Persepsi & Manuver Awal)", "d2 (Jarak Berada di Lajur Lawan)", "d3 (Jarak Bebas Aman)", "d4 (Jarak Tempuh Kendaraan Berlawanan)"],
        "Nilai (Meter)": [d1, d2, d3, d4],
    })
    df_jpm_komponen["Nilai (Meter)"] = df_jpm_komponen["Nilai (Meter)"].round(2)
    st.dataframe(df_jpm_komponen.set_index("Komponen Geometrik"), use_container_width=True)
    st.metric(label="Total Jarak Pandang Mendahului (JPM) Minimum", value=f"{jpm_total:.2f} m")

    st.markdown("---")
    # ---------------- VISUALISASI JPM ----------------
    st.subheader("🚗 Visualisasi Skematik Pergerakan Kendaraan (JPM)")
    fig2, ax2 = plt.subplots(figsize=(10, 4.5))
    
    # Gambar Garis Jalan (2 Lajur)
    ax2.axhline(1.5, color='gray', lw=2) # Tepi atas
    ax2.axhline(0, color='black', lw=1.5, ls='--') # Marka putus-putus tengah
    ax2.axhline(-1.5, color='gray', lw=2) # Tepi bawah
    
    # Gambar Posisi Kendaraan
    draw_car(ax2, 0, -0.75, 'A1 (Mulai)', '#1565C0') # Mobil Mendahului (Start)
    draw_car(ax2, d1, -0.75, 'B (Lambat)', '#616161') # Mobil Lambat (Diasumsikan bergerak hingga d1)
    draw_car(ax2, d1+d2, -0.75, 'A2 (Selesai)', '#1565C0') # Mobil Mendahului (Kembali ke kiri)
    draw_car(ax2, d1+d2+d3+d4, 0.75, 'C1 (Awal)', '#C62828', direction='left') # Mobil Lawan (Start)
    draw_car(ax2, d1+d2+d3, 0.75, 'C2 (Akhir)', '#C62828', direction='left') # Mobil Lawan (Berpapasan)
    
    # Garis lintasan mendahului
    ax2.plot([2, d1/2, d1, d1+d2-d1/2, d1+d2-2], [-0.75, 0.75, 0.75, 0.75, -0.75], color='#1565C0', ls='--', alpha=0.5)

    # Anotasi Jarak (d1, d2, d3, d4)
    ax2.annotate('', xy=(d1, -2.5), xytext=(0, -2.5), arrowprops=dict(arrowstyle='|-|', color='#1565C0'))
    ax2.text(d1/2, -3.2, f'd1\n{d1:.1f}m', ha='center', va='top', fontsize=9, color='#1565C0')
    
    ax2.annotate('', xy=(d1+d2, -2.5), xytext=(d1, -2.5), arrowprops=dict(arrowstyle='|-|', color='#2E7D32'))
    ax2.text(d1+d2/2, -3.2, f'd2\n{d2:.1f}m', ha='center', va='top', fontsize=9, color='#2E7D32')
    
    ax2.annotate('', xy=(d1+d2+d3, -2.5), xytext=(d1+d2, -2.5), arrowprops=dict(arrowstyle='|-|', color='#E65100'))
    ax2.text(d1+d2+d3/2, -3.2, f'd3\n{d3:.1f}m', ha='center', va='top', fontsize=9, color='#E65100')
    
    ax2.annotate('', xy=(d1+d2+d3+d4, 2.5), xytext=(d1+d2+d3, 2.5), arrowprops=dict(arrowstyle='|-|', color='#C62828'))
    ax2.text(d1+d2+d3+d4/2, 2.7, f'd4 (Mobil Lawan)\n{d4:.1f}m', ha='center', va='bottom', fontsize=9, color='#C62828')

    ax2.set_xlim(-5, d1+d2+d3+d4 + 15)
    ax2.set_ylim(-4, 4)
    ax2.axis('off')
    st.pyplot(fig2)

    st.markdown("---")
    st.subheader("🛣️ Evaluasi Lapangan & Marka Jalan")
    jarak_lapangan = st.number_input("Jarak Pandang Eksisting Lapangan [meter]", min_value=0.0, value=float(jpm_total + 20.0), step=10.0)
    status_marka = "Marka Putus-putus" if jarak_lapangan >= jpm_total else "Marka Utuh (No Passing)"

    if jarak_lapangan >= jpm_total:
        st.success(f"**ZONA DIPERBOLEHKAN MENDAHULUI**\n\nJarak lapangan ({jarak_lapangan} m) >= JPM ({jpm_total:.2f} m).\n\n**Rekomendasi Marka:** {status_marka}.")
    else:
        st.error(f"**ZONA DILARANG MENDAHULUI (NO PASSING ZONE)**\n\nJarak lapangan ({jarak_lapangan} m) < JPM ({jpm_total:.2f} m).\n\n**Rekomendasi Marka:** {status_marka}.")

    if st.button("💾 Simpan Hasil JPM ke Tabel", type="primary"):
        st.session_state.riwayat_jpm.append({
            "V (km/jam)": v, "Beda Kecepatan (m)": m,
            "d1 (m)": round(d1, 2), "d2 (m)": round(d2, 2), "d3 (m)": round(d3, 2), "d4 (m)": round(d4, 2),
            "Total JPM (m)": round(jpm_total, 2), "Jarak Lap (m)": jarak_lapangan, "Marka": status_marka
        })
        st.success("✅ Data berhasil ditambahkan ke tabel JPM!")

    st.markdown("---")
    st.subheader("📑 Tabel Rekapitulasi Data JPM")
    if len(st.session_state.riwayat_jpm) > 0:
        df_jpm_rekap = pd.DataFrame(st.session_state.riwayat_jpm)
        st.dataframe(df_jpm_rekap, use_container_width=True)

        buffer_jpm = io.BytesIO()
        with pd.ExcelWriter(buffer_jpm, engine='openpyxl') as writer:
            df_jpm_rekap.to_excel(writer, index=False, sheet_name='Rekap JPM')
        
        col_btn3, col_btn4 = st.columns([1, 4])
        with col_btn3:
            st.download_button("📥 Download Excel", data=buffer_jpm.getvalue(), file_name="Rekap_JPM.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col_btn4:
            if st.button("🗑️ Hapus Data JPM"):
                st.session_state.riwayat_jpm = []
                st.rerun()
    else:
        st.info("Belum ada data yang disimpan.")

# =========================================================
# 4. TAMPILAN UTAMA (TAB NAVIGASI)
# =========================================================
tab_jph, tab_jpm = st.tabs(["Hitung JPH", "Hitung JPM"])

with tab_jph:
    modul_jph()

with tab_jpm:
    modul_jpm()
