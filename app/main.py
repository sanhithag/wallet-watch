import os, json, time, sqlite3
import streamlit as st
from model_loader import load_pipeline
from utils import emi, sip_future_value, savings_goal_needed, simple_tax_estimator
from pathlib import Path

# UI theme: Warm Beige Notebook style (CSS via markdown)
CSS = '''
<style>
.stApp { background-color: #fbf7f3; color: #0f1724; }
.card { background: white; border-radius: 12px; padding: 14px; box-shadow: 0 4px 12px rgba(15,23,36,0.06); }
.header { font-family: "Segoe UI", Roboto, Arial; }
.user { color: #0f1724; }
.assistant { color: #0f4c81; }
</style>
'''

st.set_page_config(page_title='Granite Chatbot — Warm Notebook', layout='wide')
st.markdown(CSS, unsafe_allow_html=True)
st.title('Granite Chatbot — Warm Notebook UI')

# Load assets
ASSETS = Path(__file__).parent.parent / 'assets'

# Load model (pipeline)
with st.spinner('Loading model / pipeline (this may take a while)...'):
    pipe, mode = load_pipeline()
if pipe is None:
    st.warning('Pipeline not loaded locally. The app expects local pipeline; if you prefer remote HF inference, set HF_TOKEN and adapt code.')
else:
    st.success(f'Pipeline loaded (mode={mode})')

# DB for memory
DATA_DIR = Path(__file__).parent.parent / 'data'
DB = DATA_DIR / 'conversations.db'
os.makedirs(DATA_DIR, exist_ok=True)
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS conv (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, message TEXT, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
conn.commit()

# Sidebar controls
st.sidebar.header('Controls')
persona = st.sidebar.selectbox('Persona', ['Helpful Mentor', 'Strict Finance Coach', 'Casual Friend'])
eli5 = st.sidebar.checkbox("Explain like I'm 5", value=False)
st.sidebar.markdown('---')
st.sidebar.image(str(ASSETS / 'walkthrough.gif'))

if 'history' not in st.session_state:
    st.session_state.history = []

# load history from DB on startup
if not st.session_state.history:
    rows = c.execute('SELECT role, message FROM conv ORDER BY id ASC').fetchall()
    for r in rows:
        st.session_state.history.append((r[0], r[1]))

# layout
col1, col2 = st.columns([3,1])
with col1:
    st.subheader('Chat')
    for role, msg in st.session_state.history:
        if role == 'user':
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"**Bot:** {msg}")

    user_msg = st.text_input('Type your message...')
    if st.button('Send') and user_msg.strip():
        st.session_state.history.append(('user', user_msg))
        c.execute('INSERT INTO conv (role, message) VALUES (?,?)', ('user', user_msg))
        conn.commit()

        # build prompt
        prompt = f"<instruction>You are a helpful finance assistant. Use <think> and <response> tags.</instruction>\n<user>{user_msg}</user>"
        if eli5:
            prompt = 'Explain like I am 5.\n' + prompt
        if persona == 'Strict Finance Coach':
            prompt = 'Answer concisely and firmly.\n' + prompt
        elif persona == 'Casual Friend':
            prompt = 'Answer casually and with encouragement.\n' + prompt

        # generate using pipeline
        if pipe is not None:
            out = pipe([{'role':'user','content': prompt}], max_new_tokens=256)
            # normalize output
            if isinstance(out, list) and len(out)>0 and isinstance(out[0], dict):
                text = out[0].get('generated_text', str(out[0]))
            else:
                text = str(out)
            # attempt to extract <response>
            import re
            m = re.search(r'<response>(.*?)</response>', text, flags=re.DOTALL|re.IGNORECASE)
            reply = m.group(1).strip() if m else text.strip()
        else:
            reply = 'Model not available locally.'

        st.session_state.history.append(('assistant', reply))
        c.execute('INSERT INTO conv (role, message) VALUES (?,?)', ('assistant', reply))
        conn.commit()
        st.experimental_rerun()

with col2:
    st.subheader('Tools')
    st.markdown('**Calculators**')
    calc = st.selectbox('Choose', ['EMI','SIP FV','Savings Goal','Tax Estimator'])
    if calc == 'EMI':
        p = st.number_input('Principal', value=500000.0)
        rate = st.number_input('Annual rate (%)', value=7.5)
        months = st.number_input('Months', value=60, step=1)
        if st.button('Compute EMI'):
            val = emi(p, rate, months)
            st.metric('EMI', f'{val:,.2f}')
    elif calc == 'SIP FV':
        m = st.number_input('Monthly investment', value=5000.0)
        ar = st.number_input('Annual return (%)', value=10.0)
        yrs = st.number_input('Years', value=10.0)
        if st.button('Compute FV'):
            fv = sip_future_value(m, ar, yrs)
            st.metric('Future Value', f'{fv:,.2f}')
    elif calc == 'Savings Goal':
        target = st.number_input('Target', value=1000000.0)
        current = st.number_input('Current savings', value=100000.0)
        ar = st.number_input('Annual return (%)', value=7.0)
        yrs = st.number_input('Years', value=5.0)
        if st.button('Plan'):
            needed = savings_goal_needed(target, current, ar, yrs)
            st.metric('Monthly needed', f'{needed:,.2f}')
    else:
        ai = st.number_input('Annual income', value=600000.0)
        if st.button('Estimate'):
            r = simple_tax_estimator(ai)
            st.write(r)

    st.markdown('---')
    st.subheader('Conversation')
    st.write('Messages:', len(st.session_state.history))
    if st.button('Export JSON'):
        st.download_button('Download JSON', json.dumps(st.session_state.history, indent=2), file_name='conv.json')
    if st.button('Clear conversation'):
        st.session_state.history = []
        c.execute('DELETE FROM conv')
        conn.commit()
