import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time
from arabic_reshaper import reshape 
from bidi.algorithm import get_display
from sklearn.feature_extraction.text import TfidfVectorizer
import base64
from bidi.algorithm import get_display
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from sklearn.metrics.pairwise import cosine_similarity
import plotly.io as pio
from io import BytesIO



from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO

def generate_pdf(summary_text, stats_dict, ai_insights):

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = []

    # TITLE
    content.append(Paragraph("🕋 Hajj Sentiment Analysis Report", styles["Title"]))
    content.append(Spacer(1, 15))

    # SUMMARY
    content.append(Paragraph("📄 Summary", styles["Heading2"]))
    content.append(Paragraph(summary_text, styles["Normal"]))
    content.append(Spacer(1, 15))

    # STATS
    content.append(Paragraph("📊 Quick Statistics", styles["Heading2"]))

    table_data = [["Sentiment", "Count"]]
    for k, v in stats_dict.items():
        table_data.append([k, str(v)])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))

    content.append(table)
    content.append(Spacer(1, 20))
    # ================= AI INSIGHTS =================
    content.append(Paragraph("🤖 AI Insights Panel", styles["Heading2"]))
    content.append(Spacer(1, 10))

    sections = ai_insights.split("\n")

    for line in sections:
       line = line.strip()

    
       if not line:
           continue

    # Titles formatting
       if line.startswith(("1.", "2.", "3.", "4.")):
           content.append(Paragraph(f"<b>{line}</b>", styles["Heading3"]))
           content.append(Spacer(1, 6))
       else:
           content.append(Paragraph(line, styles["Normal"]))
           content.append(Spacer(1, 4))

    

    pdf.build(content)
    buffer.seek(0)

    return buffer
# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Hajj Sentiment Dashboard",
    layout="wide"
)

# =========================================================
# CSS — CINEMATIC SAAS STYLE
# =========================================================
st.markdown("""
<style>

/* ================= BACKGROUND ================= */

.stApp {
    background-image:
    linear-gradient(
        rgba(0,0,0,0.68),
        rgba(0,0,0,0.68)
    ),
    url("https://images.unsplash.com/photo-1564769625905-50e93615e769");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* REMOVE WHITE CONTAINER */
.block-container {
    padding: 2rem 3rem;
    background: transparent !important;
}

/* TEXT */
h1, h2, h3, h4, p, div, span, label {
    color: white !important;
    font-family: "Segoe UI";
}

/* BUTTONS */
.stButton button {
    background: rgba(17,24,39,0.82) !important;
    color: white !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    padding: 14px 22px;
    font-size: 16px;
    font-weight: 600;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.03);
    background: rgba(30,41,59,0.95) !important;
}

.stButton button * {
    color: white !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.85);
    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* UPLOADER */
[data-testid="stFileUploader"] {
    background: rgba(17,24,39,0.72);
    border-radius: 18px;
    padding: 18px;
}
/* STREAMLIT METRICS */
[data-testid="stMetric"] {
    background: rgba(17,24,39,0.78);
    padding: 20px;
    border-radius: 20px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.35);
}

/* METRIC LABEL */
[data-testid="stMetricLabel"] {
    color: white !important;
    font-size: 18px !important;
    justify-content: center;
}

/* METRIC NUMBER */
[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 28px !important;
    font-weight: 800 !important;
    justify-content: center;
}
/* AI PANEL */
.ai-panel {
    background: rgba(17,24,39,0.78);
    border-radius: 22px;
    padding: 22px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(14px);
}
 /* ===============================
   GLASSMORPHISM FILE UPLOADER
   =============================== */

[data-testid="stFileUploader"] {
    background: rgba(17, 24, 39, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 22px;
    padding: 24px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow: 0 10px 35px rgba(0,0,0,0.35);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

/* Hover animation */
[data-testid="stFileUploader"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 50px rgba(0,0,0,0.5);
    border: 1px solid rgba(255, 255, 255, 0.25);
}

/* Title text */
[data-testid="stFileUploader"] label {
    color: white !important;
    font-size: 18px !important;
    font-weight: 600;
}

/* Drag & drop text */
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #e5e7eb !important;
    font-size: 14px;
    opacity: 0.9;
}

/* Button styling */
[data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #1f2937, #111827) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    padding: 10px 18px !important;
    font-weight: 600;
    transition: all 0.3s ease;
}

/* Button hover */
[data-testid="stFileUploader"] button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #374151, #1f2937) !important;
}

/* ICON BEFORE TITLE */
[data-testid="stFileUploader"]::before {
    content: "📁 Upload Dataset";
    display: block;
    font-size: 16px;
    font-weight: 700;
    color: white;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# GEMINI
# =========================================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    "gemini-3.1-flash-lite-preview"
)


def classify_sentiment_llm(text):
    prompt = f"""
You are a sentiment classifier.

Classify this text into ONLY one label:
Positive, Negative, Neutral

Text:
{text}

Return ONLY one word.
"""

    response = model.generate_content(prompt)
    return response.text.strip().capitalize()

# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page
def card(container, title, value, color):
    container.markdown(f"""
    <div style="
        background: rgba(17,24,39,0.78);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0px 10px 30px rgba(0,0,0,0.35);
    ">
        <div style="color:white; font-size:16px;">{title}</div>
        <div style="color:white; font-size:28px; font-weight:800;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def retrieve_context(df, query):

    if "text" not in df.columns:
        return "No text column found."

    texts = df["text"].dropna().astype(str)

    # TF-IDF
    vectorizer = TfidfVectorizer(stop_words=None)

    tfidf_matrix = vectorizer.fit_transform(texts)

    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(
        query_vector,
        tfidf_matrix
    ).flatten()

    # TOP COMMENTS
    top_indices = similarities.argsort()[-5:][::-1]

    top_comments = texts.iloc[top_indices]

    summary = df["sentiment"].value_counts().to_dict()

    context = f"""
DATASET SUMMARY:
{summary}

MOST RELEVANT COMMENTS:
"""

    for i, comment in enumerate(top_comments):
        context += f"\n{i+1}. {comment}"

    return context  


# =========================================================
# HOME PAGE
# =========================================================
if st.session_state.page == "home":

    st.markdown("""
    <div style="
        text-align:center;
        padding-top:140px;
        padding-bottom:100px;
    ">

    <h1 style="
        font-size:72px;
        font-weight:800;
        margin-bottom:20px;
    ">
    🕋 Hajj & Omrah Sentiment Dashboard
    </h1>

    <p style="
        font-size:24px;
        color:#e5e7eb;
        max-width:900px;
        margin:auto;
    ">
    AI-powered platform for analyzing pilgrims feedback using
    Large Language Models and interactive visual analytics.
    </p>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    

    with col1:
        if st.button(" Dataset Analysis", use_container_width=True):
            go("dataset")

    with col2:
        if st.button(" Single Analysis", use_container_width=True):
            go("single")
    with col3:
        if st.button(" AI Chatbot", use_container_width=True):
            go("chatbot")        



# =========================================================
# SINGLE ANALYSIS
# =========================================================
elif st.session_state.page == "single":

    if st.button("⬅ Back to Home"):
        go("home")

    st.title(" AI Comment Analysis")

    comment = st.text_area(
        "Enter pilgrim comment",
        height=200
    )

    if st.button("Analyze Comment"):

        if comment.strip() == "":
            st.warning("Please enter a comment")

        else:

           prompt = f"""
           You are a professional NLP and sentiment analysis system.

           Analyze the following comment:

           {comment}

           Return ONLY valid JSON. No explanations. No markdown.

           JSON format:
           {{
              "sentiment": "Positive | Negative | Neutral",
              "confidence": 0.0,
              "problems": ["problem1", "problem2"],
              "emotion": "joy | anger | sadness | neutral"
            }}

           Rules:
           - output MUST be valid JSON
           - confidence must be between 0 and 1
           """

        try:

                with st.spinner("Analyzing with Gemini AI..."):

                    response = model.generate_content(prompt)
                    st.session_state.ai_insights = response.text
                    st.info(response.text)

                    cleaned = (
                        response.text
                        .replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )

                    try:
                        result = json.loads(cleaned)
                    except Exception:
                        st.error("AI returned invalid format")
                        st.code(cleaned)
                        st.stop()

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.markdown(f"""
                        <div class="kpi-card">
                        <div class="metric-title">
                        Sentiment
                        </div>

                        <div class="metric-number">
                        {result["sentiment"]}
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with c2:
                        st.markdown(f"""
                        <div class="kpi-card">
                        <div class="metric-title">
                        Confidence
                        </div>

                        <div class="metric-number">
                        {result["confidence"]}
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with c3:
                        st.markdown(f"""
                        <div class="kpi-card">
                        <div class="metric-title">
                        Problems
                        </div>

                        <div class="metric-number">
                        {len(result["problems"])}
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    st.info(result["problems"])

        except Exception as e:
            st.error("AI Analysis Error")
            st.write(e)

# =========================================================
# DATASET ANALYSIS
# =========================================================
elif st.session_state.page == "dataset":

    if st.button("⬅ Back to Home"):
        go("home")

    st.title("📁 Dataset Analysis Dashboard")

    uploaded_file = st.file_uploader(
        "Upload CSV Dataset",
        type=["csv"]
    )
    

    if uploaded_file:

        df = pd.read_csv(uploaded_file)
        st.session_state.df = df


        if "sentiment" in df.columns:
            st.success("Sentiment column detected.")
            st.info("Using existing sentiment labels.")

        else:
            if "text" not in df.columns:
                st.error("Dataset must contain a text column.")
                st.stop()
            st.info("Generating sentiment labels with Gemini AI...")
            progress = st.progress(0)
            results = []

            for i, text in enumerate(df["text"].fillna("")):

                results.append(
                    classify_sentiment_llm(text)
                )

                progress.progress(
                    (i + 1) / len(df)
                )

            df["sentiment"] = results
           


            # CLEAN
        df["sentiment"] = (
            df["sentiment"]
            .astype(str)
            .str.strip()
            .str.lower()
        )
            
            # =================================================
            # SIDEBAR FILTERS
            # =================================================
        with st.sidebar:

                st.header("🔎 Filters")

                sentiment_filter = st.multiselect(
                    "Sentiment",
                    df["sentiment"].unique(),
                    default=df["sentiment"].unique()
                )

            # FILTERED DF
        df_filtered = df[
               df["sentiment"].isin(sentiment_filter)
            ].copy()

            # =================================================
            # KPIs
            # =================================================
        total = len(df_filtered)
        positive = (
                df_filtered["sentiment"] == "positive"
            ).sum()

        negative = (
                df_filtered["sentiment"] == "negative"
            ).sum()

        neutral = (
                df_filtered["sentiment"] == "neutral"
            ).sum()

        st.markdown("##  Key Performance Indicators")

        c1, c2, c3, c4 = st.columns(4)

        card(c1, "📊 Total", total, "#93c5fd")
        card(c2, "😊 Positive", positive, "#22c55e")
        card(c3, "😡 Negative", negative, "#ef4444")
        card(c4, "😐 Neutral", neutral, "#9ca3af")
        st.markdown("<br>", unsafe_allow_html=True)
 
            # =================================================
            # MAIN GRID
            # =================================================
        left, right = st.columns([2.2, 1])

            # =================================================
            # LEFT
            # =================================================
        with left:
                st.markdown("### 📊 Sentiment Distribution") 
                counts = ( 
        df_filtered["sentiment"]
                    .value_counts()
                    .reset_index() )
                
                counts.columns = [ "sentiment", "count" ]

                fig = px.bar(
                    counts, 
                    x="sentiment", 
                    y="count", 
                    color="sentiment", 
                    text="count", 
                    height=380 
                )

                fig.update_layout( 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font_color="white" 
                ) 

                st.plotly_chart( fig, use_container_width=True ) 
                
                st.markdown("###  Sentiment Ratio") 

                fig2 = px.pie( 
                    counts, 
                    names="sentiment", 
                    values="count", 
                    hole=0.5, 
                    height=380 
                ) 
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font_color="white" 
                ) 
                st.plotly_chart( fig2, use_container_width=True )

                if "text" in df_filtered.columns:

                    st.markdown("##  Interactive WordCloud")

                    option = st.radio(
                       "Choose sentiment:",
                       ["Positive", "Negative", "Neutral"],
                       horizontal=True
                    )
                    if option == "Positive":
                        text_data = df_filtered[df_filtered["sentiment"] == "positive"]["text"]
                    elif option == "Negative":
                        text_data = df_filtered[df_filtered["sentiment"] == "negative"]["text"]
                    else:
                        text_data = df_filtered[df_filtered["sentiment"] == "neutral"]["text"]
                    text_data = " ".join(text_data.astype(str))

                    if text_data.strip():

                 # =========================
                 # ARABIC FIX
                 # =========================
                     text_data = get_display(reshape(text_data))

                  # =========================
                  # WORDCLOUD
                  # =========================
                     wc = WordCloud(
                        width=1000,
                        height=400,
                        background_color="black",
                        font_path="C:/Windows/Fonts/arial.ttf"
                    ).generate(text_data)

                     fig, ax = plt.subplots()
                     ax.imshow(wc)
                     ax.axis("off")
                     st.pyplot(fig)

                    else:
                      st.warning("No text available for this sentiment")
                      st.markdown("##  AI Keywords Extraction (TF-IDF)")
                    texts = df_filtered["text"].dropna().astype(str)
                    custom_stopwords = [
                        "و", "في", "على", "من", "إلى", "عن", "هذا", "هذه",
                        "كان", "كانت", "ما", "لا", "لم", "لن", "كل", "قد"
                    ]
                    vectorizer = TfidfVectorizer(
                    stop_words=custom_stopwords,
                    max_features=10
                    )
                    X = vectorizer.fit_transform(texts)

                    words = vectorizer.get_feature_names_out()
                    scores = X.toarray().sum(axis=0)
                    keywords_df = pd.DataFrame({
                     "keyword": words,
                     "score": scores
                    }).sort_values("score", ascending=False)

                    fig = px.bar(
                      keywords_df,
                      x="keyword",
                      y="score",
                      text="score",
                      height=400,
                      color="keyword"
                    )
                    fig.update_layout(
                     paper_bgcolor="rgba(0,0,0,0)",
                     plot_bgcolor="rgba(0,0,0,0)",
                     font_color="white"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(keywords_df)
                    bar_fig = px.bar(counts, x="sentiment", y="count", color="sentiment")
                    pie_fig = px.pie(counts, names="sentiment", values="count")
                    tfidf_fig = px.bar(keywords_df, x="keyword", y="score")

            

            # =================================================
            # RIGHT
            # =================================================
        with right:

                st.markdown("""
                <div class="ai-panel">
                <h3> AI Insights Panel</h3>
                <p>Generate automatic thesis insights.</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button(
                    "Generate AI Insights",
                    use_container_width=True
                ):
                   

                    summary = (
                        df_filtered["sentiment"]
                        .value_counts()
                        .to_dict()
                    )

                    prompt = f"""
You are a senior data analyst.

Analyze this pilgrims dataset.

Sentiment summary:
{summary}

Total records:
{len(df_filtered)}

Provide:
1. General summary
2. Main problems
3. Recommendations
4. Academic interpretation
"""
                
                    response = model.generate_content(
                        prompt
                    )
                    st.session_state["ai_insights"] = response.text
                    st.info(response.text)

            

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("###  Quick Statistics")

                st.write(
                    df_filtered["sentiment"]
                    .value_counts()
                )
                st.markdown("<br>", unsafe_allow_html=True)

                if st.button(
                    "📄 Generate PDF Report",
                    use_container_width=True
                ):

                    summary_text = """
                    This report presents sentiment analysis results
                    for pilgrims feedback using AI and NLP techniques.
                    """
                    pos_text = " ".join(df_filtered[df_filtered["sentiment"] == "positive"]["text"].astype(str))
                    neg_text = " ".join(df_filtered[df_filtered["sentiment"] == "negative"]["text"].astype(str))
                    neu_text = " ".join(df_filtered[df_filtered["sentiment"] == "neutral"]["text"].astype(str))

                    pdf_buffer = generate_pdf(
                       summary_text="Hajj sentiment analysis report",
                       stats_dict=df_filtered["sentiment"].value_counts().to_dict(),
                       ai_insights=st.session_state.get("ai_insights", "No AI insights available.")
                    )
                    pdf_bytes = pdf_buffer.getvalue()

                    st.download_button(
                       label="⬇ Download PDF Report",
                       data=pdf_buffer.getvalue(),
                       file_name="hajj_report.pdf",
                       mime="application/pdf"
                    )
# =========================================================
# chat bot
# =========================================================            
elif st.session_state.page == "chatbot":

    if st.button("⬅ Back to Home"):
        go("home")

    st.title(" RAG AI Data Analyst Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask about Hajj dataset:")

    if st.button("Ask AI") and user_input:

        df = st.session_state.get("df", None)

        if df is None:
            st.error("⚠️ Please upload dataset first in Dataset page")
            st.stop()

        # 🔥 RETRIEVAL STEP
        context = retrieve_context(df, user_input)

        # 🔥 LLM STEP
        prompt = f"""
You are a senior AI Data Analyst specialized in Hajj & Omrah feedback.

You MUST answer ONLY using the dataset context below.

CONTEXT:
{context}

QUESTION:
{user_input}

Return JSON ONLY:
{{
  "answer": "clear explanation based on data",
  "insights": "key insights",
  "recommendations": "improvements"
}}
"""

        response = model.generate_content(prompt)

        cleaned = response.text.replace("```json", "").replace("```", "").strip()


        try:
            result = json.loads(cleaned)
        except:
            st.error("Invalid AI response")
            st.code(cleaned)
            st.stop()

        st.markdown(f"""
        <div style="
        background: rgba(17,24,39,0.85);
        padding:20px;
        border-radius:18px;
        margin-top:15px;
        border:1px solid rgba(255,255,255,0.08);
        ">
        <h3 style="color:white;"> Insights</h3>
        <p style="color:#e5e7eb;">
        {result["insights"]}
        </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
        background: rgba(17,24,39,0.85);
        padding:20px;
        border-radius:18px;
        margin-top:15px;
        border:1px solid rgba(255,255,255,0.08);
        ">
        <h3 style="color:white;"> Recommendations</h3>
        <p style="color:#e5e7eb;">
        {result["recommendations"]}
        </p>
        </div>
        """, unsafe_allow_html=True)
    if st.button("🗑 Clear Conversation"):
       st.session_state.chat_history = []
       st.rerun()

    # CHAT UI
    st.markdown("###  Conversation")

    for role, msg in st.session_state.chat_history:

        if role == "User":

            st.markdown(f"""
            <div style="
            background: rgba(59,130,246,0.18);
            padding:16px;
            border-radius:18px;
            margin-bottom:12px;
            text-align:right;
            border:1px solid rgba(255,255,255,0.08);
            ">
            <b>🧑 You:</b><br><br>
            {msg}
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown(f"""
            <div style="
            background: rgba(17,24,39,0.85);
            padding:16px;
            border-radius:18px;
            margin-bottom:12px;
            border:1px solid rgba(255,255,255,0.08);
            ">
           <b>🤖 AI Analyst:</b><br><br>
           {msg}
           </div>
           """, unsafe_allow_html=True) 