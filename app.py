import pandas as pd
import streamlit as st
from piiscan.core import scan, mask

st.set_page_config(page_title="piiscan", page_icon="🛡️", layout="centered")
st.title("🛡️ piiscan")
st.write("Upload a CSV to check it for personal data (emails, phones, cards, Aadhaar, PAN, IPs) and download a masked copy.")
st.warning("Don't upload real sensitive data to a public demo. Use sample or already-anonymised files.")

file = st.file_uploader("CSV file", type="csv")
if file:
    df = pd.read_csv(file, dtype=str)
    st.caption(f"{df.shape[0]} rows × {df.shape[1]} columns")

    report = scan(df)
    if not report:
        st.success("No PII detected.")
    else:
        st.error(f"PII found in {len(report)} column(s)")
        rows = [{"column": c, "type": k, "count": n} for c, counts in report.items() for k, n in counts.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        masked = mask(df)
        st.subheader("Masked preview")
        st.dataframe(masked.head(10), use_container_width=True)
        st.download_button("Download masked CSV", masked.to_csv(index=False).encode("utf-8"),
                           file_name="masked.csv", mime="text/csv", type="primary")
else:
    st.info("Upload a CSV to get started.")
