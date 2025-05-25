
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Fatura - Çek Eşleştirme", layout="wide")

st.title("Fatura - Çek Eşleştirme ve Ortalama Vade Hesaplama")

st.subheader("1. Fatura Bilgileri")
fatura_df = st.experimental_data_editor(
    pd.DataFrame(columns=["Fatura Tarihi", "Fatura Tutarı (TL)"]),
    num_rows="dynamic",
    use_container_width=True
)

st.subheader("2. Çek Bilgileri")
cek_df = st.experimental_data_editor(
    pd.DataFrame(columns=["Çek Vade Tarihi", "Çek Tutarı (TL)"]),
    num_rows="dynamic",
    use_container_width=True
)

if st.button("EŞLEŞTİR"):
    try:
        faturalar = fatura_df.dropna()
        cekler = cek_df.dropna()
        faturalar["Fatura Tarihi"] = pd.to_datetime(faturalar["Fatura Tarihi"])
        cekler["Çek Vade Tarihi"] = pd.to_datetime(cekler["Çek Vade Tarihi"])
        faturalar = faturalar.sort_values("Fatura Tarihi").reset_index(drop=True)
        cekler = cekler.sort_values("Çek Vade Tarihi").reset_index(drop=True)

        eslesmeler = []
        f_index, c_index = 0, 0
        toplam_gun = 0
        toplam_tutar = 0

        while f_index < len(faturalar) and c_index < len(cekler):
            f_tutar = faturalar.at[f_index, "Fatura Tutarı (TL)"]
            c_tutar = cekler.at[c_index, "Çek Tutarı (TL)"]
            eslesen_tutar = min(f_tutar, c_tutar)
            gun_fark = (cekler.at[c_index, "Çek Vade Tarihi"] - faturalar.at[f_index, "Fatura Tarihi"]).days

            eslesmeler.append({
                "Fatura Tarihi": faturalar.at[f_index, "Fatura Tarihi"].date(),
                "Çek Vade Tarihi": cekler.at[c_index, "Çek Vade Tarihi"].date(),
                "Eşleşen Tutar": eslesen_tutar,
                "Gün Farkı": gun_fark
            })

            toplam_gun += eslesen_tutar * gun_fark
            toplam_tutar += eslesen_tutar

            faturalar.at[f_index, "Fatura Tutarı (TL)"] -= eslesen_tutar
            cekler.at[c_index, "Çek Tutarı (TL)"] -= eslesen_tutar

            if faturalar.at[f_index, "Fatura Tutarı (TL)"] == 0:
                f_index += 1
            if cekler.at[c_index, "Çek Tutarı (TL)"] == 0:
                c_index += 1

        st.subheader("3. Eşleşme Sonuçları")
        st.dataframe(pd.DataFrame(eslesmeler), use_container_width=True)

        if toplam_tutar > 0:
            ort_vade = toplam_gun / toplam_tutar
            ort_vade_tarih = datetime.today() + pd.to_timedelta(ort_vade, unit="d")
            st.success(f"**Ağırlıklı Ortalama Vade: {round(ort_vade, 2)} gün**")
            st.success(f"**Vade Tarihi: {ort_vade_tarih.strftime('%d.%m.%Y')}**")
        else:
            st.warning("Eşleşecek veri bulunamadı.")

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
