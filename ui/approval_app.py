import streamlit as st
import yaml
import os

st.title("🛡️ Sentinel QA Approval Portal")

PENDING = "data/test_plans/pending"
APPROVED = "data/test_plans/approved"

if not os.path.exists(PENDING):
    os.makedirs(PENDING)

files = [f for f in os.listdir(PENDING) if f.endswith(".yaml")]

if not files:
    st.info("No pending test cases found.")

for f_name in files:
    file_path = f"{PENDING}/{f_name}"
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        
        with st.expander(f"Review: {data.get('title', f_name)}"):
            edited_steps = st.data_editor(data['steps'], key=f_name, num_rows="dynamic")
            
            if st.button("Approve", key=f"btn_{f_name}"):
                data['steps'] = edited_steps
                os.makedirs(APPROVED, exist_ok=True)
                with open(f"{APPROVED}/{f_name}", "w") as fw:
                    yaml.dump(data, fw)
                os.remove(file_path)
                st.rerun()
    except Exception as e:
        st.error(f"Error loading {f_name}: {e}")
        if st.button(f"Delete Corrupt File: {f_name}"):
            os.remove(file_path)
            st.rerun()