import streamlit as st
import re

from html import escape

from document_processor import extract_text
from chunker import chunk_text
from embedder import create_embeddings
from retriever import retrieve_top_chunks
from llm import generate_answer


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ASTRA",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "documents" not in st.session_state:
    st.session_state.documents = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chunks" not in st.session_state:
    st.session_state.chunks = {}

if "embeddings" not in st.session_state:
    st.session_state.embeddings = {}


# ============================================================
# ANSWER FORMATTING
# ============================================================

def format_answer_html(text):
    """
    Converts Gemini's basic Markdown formatting
    into HTML suitable for ASTRA's UI.
    """

    text = escape(text)

    # Bold: **text**
    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"<strong>\1</strong>",
        text
    )

    # Headings
    text = re.sub(
        r"(?m)^#{1,6}\s*(.*)$",
        r"<strong>\1</strong>",
        text
    )

    # Bullet points
    text = re.sub(
        r"(?m)^[\-\*]\s+(.*)$",
        r"• \1",
        text
    )

    # Numbered lists
    text = re.sub(
        r"(?m)^(\d+)\.\s+(.*)$",
        r"<strong>\1.</strong> \2",
        text
    )

    # Preserve line breaks
    text = text.replace(
        "\n",
        "<br>"
    )

    return text


# ============================================================
# COSMIC / AURORA UI
# ============================================================

st.html("""
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap'
);


/* ==========================================================
   GLOBAL BACKGROUND
   ========================================================== */

.stApp {

    min-height: 100vh;

    background:

        radial-gradient(
            ellipse at 72% 5%,
            rgba(146, 74, 255, 0.34) 0%,
            rgba(93, 55, 190, 0.16) 20%,
            transparent 44%
        ),

        radial-gradient(
            ellipse at 45% 25%,
            rgba(0, 190, 255, 0.18) 0%,
            transparent 35%
        ),

        radial-gradient(
            ellipse at 10% 75%,
            rgba(41, 70, 255, 0.13) 0%,
            transparent 38%
        ),

        linear-gradient(
            135deg,
            #020611 0%,
            #05091b 45%,
            #09051d 100%
        );

    color: #f8fafc;
}


/* ==========================================================
   AURORA GLOW
   ========================================================== */

.stApp::before {

    content: "";

    position: fixed;

    width: 900px;
    height: 430px;

    top: -100px;
    right: 2%;

    background:

        radial-gradient(
            ellipse,
            rgba(53, 211, 255, 0.52) 0%,
            rgba(83, 82, 255, 0.40) 30%,
            rgba(196, 66, 255, 0.30) 50%,
            transparent 73%
        );

    filter: blur(48px);

    transform: rotate(-14deg);

    opacity: 0.78;

    pointer-events: none;

    z-index: 0;
}


/* SECOND AURORA */

.stApp::after {

    content: "";

    position: fixed;

    width: 700px;
    height: 280px;

    top: 100px;
    left: 17%;

    background:

        radial-gradient(
            ellipse,
            rgba(0, 221, 255, 0.19),
            rgba(107, 78, 255, 0.14),
            transparent 70%
        );

    filter: blur(42px);

    transform: rotate(18deg);

    pointer-events: none;

    z-index: 0;
}


/* ==========================================================
   STARS
   ========================================================== */

.stars {

    position: fixed;

    inset: 0;

    pointer-events: none;

    z-index: 0;

    background-image:

        radial-gradient(
            circle at 8% 18%,
            rgba(255,255,255,.75) 0 1px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 18% 32%,
            rgba(255,255,255,.55) 0 1px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 28% 12%,
            rgba(255,255,255,.75) 0 1px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 42% 22%,
            rgba(255,255,255,.45) 0 1px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 56% 9%,
            rgba(255,255,255,.75) 0 1px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 68% 31%,
            rgba(255,255,255,.55) 0 1px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 79% 18%,
            rgba(255,255,255,.75) 0 1px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 91% 38%,
            rgba(255,255,255,.45) 0 1px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 34% 54%,
            rgba(255,255,255,.45) 0 1px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 73% 63%,
            rgba(255,255,255,.55) 0 1px,
            transparent 1.5px
        );
}


/* ==========================================================
   STREAMLIT MAIN AREA
   ========================================================== */

.block-container {

    max-width: 1420px;

    padding-top: 1rem;
    padding-bottom: 4rem;

    position: relative;

    z-index: 2;
}


/* ==========================================================
   TOP NAVIGATION
   ========================================================== */

.topbar {

    height: 70px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 0 12px;

    margin-bottom: 5px;
}


.brand {

    font-family: 'DM Sans', sans-serif;

    font-size: 21px;

    font-weight: 600;

    letter-spacing: 0.30em;

    color: #f8fafc;
}


.brand-star {

    color: #55eaff;

    margin-right: 8px;

    text-shadow:
        0 0 14px rgba(85,234,255,.85);
}


/* NAV BUTTONS */

div[data-testid="stHorizontalBlock"] {

    align-items: center !important;
}


div[data-testid="stHorizontalBlock"] button {

    min-height: 43px !important;

    padding:
        8px 17px !important;

    border-radius: 999px !important;

    background:
        rgba(7, 15, 35, .42) !important;

    border:
        1px solid rgba(120, 190, 255, .12) !important;

    color:
        #aebbd0 !important;

    font-family:
        'DM Sans', sans-serif !important;

    font-size:
        13px !important;

    font-weight:
        500 !important;

    letter-spacing:
        .02em !important;

    transition:
        all .25s ease !important;
}


div[data-testid="stHorizontalBlock"] button:hover {

    color: #ffffff !important;

    border-color:
        rgba(77, 218, 255, .38) !important;

    background:
        rgba(39, 118, 180, .18) !important;

    box-shadow:
        0 0 20px rgba(41, 192, 255, .08) !important;
}


/* ONLINE PILL */

.online {

    display: inline-block;

    font-size: 10px;

    letter-spacing: .16em;

    color: #79eaff;

    padding:
        8px 14px;

    border-radius: 999px;

    background:
        rgba(27, 196, 255, .07);

    border:
        1px solid rgba(73, 219, 255, .22);

    box-shadow:
        0 0 18px rgba(73,219,255,.04);
}


/* ==========================================================
   HERO
   ========================================================== */

.hero {

    text-align: center;

    padding-top: 12px;

    margin-bottom: 34px;
}


.hero-kicker {

    font-family: 'DM Sans', sans-serif;

    font-size: 11px;

    letter-spacing: .38em;

    color: #66ddff;

    margin-bottom: 16px;

    text-transform: uppercase;
}


.hero-title {

    font-family:
        'Playfair Display',
        serif;

    font-size:
        clamp(62px, 7vw, 94px);

    line-height: 1;

    font-weight: 500;

    letter-spacing: .04em;

    background:

        linear-gradient(
            100deg,
            #65e9ff,
            #a8a5ff 42%,
            #e48aff 75%,
            #ffffff
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;

    filter:
        drop-shadow(
            0 0 28px
            rgba(113, 130, 255, .27)
        );
}


.hero-tagline {

    margin-top: 18px;

    color: #d3dcf0;

    font-family:
        'DM Sans',
        sans-serif;

    font-size: 17px;

    letter-spacing: .01em;
}


/* ==========================================================
   MAIN GLASS PANEL
   ========================================================== */

.main-panel {

    position: relative;

    width:
        min(920px, 100%);

    margin:
        0 auto;

    padding:
        42px 48px 34px;

    border-radius:
        28px;

    background:

        linear-gradient(
            145deg,
            rgba(8, 25, 54, .64),
            rgba(10, 11, 38, .58)
        );

    border:
        1px solid
        rgba(67, 215, 255, .27);

    box-shadow:

        0 0 70px
        rgba(25, 112, 255, .10),

        inset 0 1px 0
        rgba(255,255,255,.05);

    backdrop-filter:
        blur(25px);
}


/* ==========================================================
   UPLOAD AREA
   ========================================================== */

.upload-inner {

    min-height:
        235px;

    display:
        flex;

    flex-direction:
        column;

    align-items:
        center;

    justify-content:
        center;

    text-align:
        center;

    border-radius:
        20px;

    background:

        radial-gradient(
            circle at 50% 0%,
            rgba(25, 204, 255, .09),
            transparent 65%
        );

    border:
        1px dashed
        rgba(72, 216, 255, .34);

    box-shadow:

        inset 0 0 50px
        rgba(45, 99, 255, .05);
}


.upload-icon {

    font-size:
        45px;

    color:
        #61eaff;

    text-shadow:
        0 0 20px
        rgba(72, 227, 255, .65);

    margin-bottom:
        13px;
}


.upload-heading {

    font-size:
        19px;

    font-weight:
        600;

    color:
        #e7f7ff;
}


.upload-description {

    color:
        #8292b2;

    font-size:
        13px;

    margin-top:
        9px;
}


/* ==========================================================
   FILE UPLOADER
   ========================================================== */

[data-testid="stFileUploader"] {

    margin-top:
        14px;

    position:
        relative;

    z-index:
        4;
}


[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {

    background:
        rgba(7, 15, 35, .42);

    border:
        1px solid rgba(120, 190, 255, .18);

    border-radius:
        14px;
}


[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] button {

    background:
        rgba(39, 118, 180, .18);

    border:
        1px solid rgba(77, 218, 255, .38);

    border-radius:
        999px;

    color:
        #e7f7ff;
}


/* ==========================================================
   RECENT DOCUMENTS
   ========================================================== */

.recent-header {

    display:
        flex;

    justify-content:
        space-between;

    align-items:
        center;

    margin-top:
        34px;

    margin-bottom:
        16px;
}


.recent-title {

    font-size:
        17px;

    font-weight:
        600;

    color:
        #e4edff;

    letter-spacing:
        .01em;
}


.view-all {

    color:
        #48dcff;

    font-size:
        13px;

    font-weight:
        500;

    letter-spacing:
        .03em;
}


/* ==========================================================
   DOCUMENT CARDS
   ========================================================== */

.doc-card {

    min-height:
        112px;

    padding:
        16px;

    border-radius:
        16px;

    background:

        linear-gradient(
            145deg,
            rgba(27, 45, 82, .58),
            rgba(13, 21, 47, .50)
        );

    border:
        1px solid
        rgba(128, 172, 255, .12);

    box-shadow:

        inset 0 1px 0
        rgba(255,255,255,.025);

    transition:
        .25s ease;
}


.doc-card:hover {

    transform:
        translateY(-3px);

    border-color:
        rgba(85, 222, 255, .30);

    box-shadow:

        0 8px 30px
        rgba(41, 143, 255, .10);
}


.doc-icon {

    font-size:
        23px;

    margin-bottom:
        11px;
}


.doc-name {

    font-size:
        14px;

    color:
        #dce7f9;

    font-weight:
        500;

    white-space:
        nowrap;

    overflow:
        hidden;

    text-overflow:
        ellipsis;
}


.doc-meta {

    color:
        #8293b2;

    font-size:
        12px;

    margin-top:
        7px;
}


/* ==========================================================
   CHAT PAGE
   ========================================================== */

.chat-panel {

    width:
        min(920px, 100%);

    margin:
        0 auto;

    min-height:
        600px;

    padding:
        25px;

    border-radius:
        28px;

    background:

        linear-gradient(
            145deg,
            rgba(8, 22, 49, .72),
            rgba(10, 10, 34, .64)
        );

    border:
        1px solid
        rgba(68, 208, 255, .22);

    backdrop-filter:
        blur(25px);

    box-shadow:

        0 0 80px
        rgba(41, 108, 255, .08);
}


.chat-header {

    display:
        flex;

    justify-content:
        space-between;

    align-items:
        center;

    padding-bottom:
        20px;

    border-bottom:
        1px solid
        rgba(148,163,184,.09);

    margin-bottom:
        28px;
}


.chat-file {

    color:
        #c9d7ee;

    font-size:
        14px;
}


.chat-document-list {

    display:
        grid;

    grid-template-columns:
        repeat(auto-fill, minmax(180px, 1fr));

    gap:
        14px;
}


.message-user {

    margin-left:
        auto;

    width:
        fit-content;

    max-width:
        65%;

    padding:
        14px 18px;

    border-radius:
        17px 17px 5px 17px;

    background:

        linear-gradient(
            135deg,
            #087fc1,
            #4f46e5
        );

    color:
        white;

    font-size:
        13px;

    margin-bottom:
        24px;

    box-shadow:
        0 7px 25px
        rgba(42, 117, 255, .18);
}


.message-ai {

    max-width:
        82%;

    padding:
        19px;

    border-radius:
        18px 18px 18px 5px;

    background:
        rgba(15, 29, 57, .75);

    border:
        1px solid
        rgba(104, 153, 222, .13);

    color:
        #d7e3f4;

    line-height:
        1.7;

    font-size:
        13px;

    margin-bottom:
        25px;
}


.source-title {

    font-size:
        11px;

    letter-spacing:
        .15em;

    color:
        #8a9bb7;

    text-transform:
        uppercase;

    margin-bottom:
        10px;
}


.source-card {

    padding:
        14px;

    border-radius:
        13px;

    background:
        rgba(7, 17, 38, .65);

    border:
        1px solid
        rgba(115, 161, 225, .12);

    margin-bottom:
        8px;
}


.source-name {

    color:
        #e0eaff;

    font-size:
        12px;

    font-weight:
        600;
}


.source-text {

    color:
        #71839f;

    font-size:
        11px;

    margin-top:
        5px;

    line-height:
        1.5;
}


/* ==========================================================
   CHAT INPUT
   ========================================================== */

[data-testid="stChatInput"] {

    background:
        rgba(7, 14, 32, .80) !important;

    border:
        1px solid
        rgba(75, 213, 255, .18) !important;

    border-radius:
        18px !important;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.footer {

    text-align:
        center;

    margin-top:
        40px;

    color:
        #3c4c69;

    font-size:
        10px;

    letter-spacing:
        .2em;
}


/* ==========================================================
   HIDE DEFAULT STREAMLIT ELEMENTS
   ========================================================== */

#MainMenu {

    visibility:
        hidden;
}


footer {

    visibility:
        hidden;
}


[data-testid="stToolbar"] {

    display:
        none;
}


[data-testid="stHeader"] {

    display:
        none;
}

</style>
""")


# ============================================================
# STAR LAYER
# ============================================================

st.html("""
<div class="stars"></div>
""")


# ============================================================
# TOP NAVIGATION
# ============================================================

top_left, nav1, nav2, nav3, top_right = st.columns(
    [3.2, 1.15, 1.45, 1.05, 1.2]
)


with top_left:

    st.html("""
    <div class="topbar">

        <div class="brand">
            <span class="brand-star">✦</span>
            ASTRA
        </div>

    </div>
    """)


with nav1:

    if st.button(
        "Home",
        use_container_width=True
    ):

        st.session_state.page = "home"

        st.rerun()


with nav2:

    if st.button(
        "Documents",
        use_container_width=True
    ):

        st.session_state.page = "documents"

        st.rerun()


with nav3:

    if st.button(
        "Chat",
        use_container_width=True
    ):

        st.session_state.page = "chat"

        st.rerun()


with top_right:

    st.html("""
    <div style="
        text-align:right;
        padding-top:9px;
    ">

        <span class="online">
            ● ONLINE
        </span>

    </div>
    """)


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "home":

    st.html("""
    <div class="hero">

        <div class="hero-kicker">
            ✦ YOUR PERSONAL KNOWLEDGE SPACE
        </div>

        <div class="hero-title">
            ASTRA
        </div>

        <div class="hero-tagline">
            Your knowledge, at your command.
        </div>

    </div>
    """)


    st.html("""
    <div class="main-panel">

        <div class="upload-inner">

            <div class="upload-icon">
                ♧
            </div>

            <div class="upload-heading">
                Drop your files here
            </div>

            <div class="upload-description">
                PDF / TXT
                &nbsp; · &nbsp;
                Multiple files supported
            </div>

        </div>

    </div>
    """)


    uploaded_files = st.file_uploader(
        "＋ Upload files from device",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="visible"
    )


    if uploaded_files:

        # --------------------------------------------------------
        # KEEP PREVIOUSLY UPLOADED DOCUMENTS
        # --------------------------------------------------------

        existing_documents = {
            document.name: document
            for document in st.session_state.documents
        }

        # Add the newly uploaded documents
        for document in uploaded_files:
            existing_documents[document.name] = document

        # Save all documents together
        st.session_state.documents = list(
            existing_documents.values()
        )

        # --------------------------------------------------------
        # PROCESS NEW DOCUMENTS
        # --------------------------------------------------------

        for document in uploaded_files:

            # If this document was already processed,
            # don't process it again.
            if document.name in st.session_state.chunks:
                continue

            try:

                # STEP 1: Extract text from the document
                text = extract_text(document)

                if text.strip():

                    # STEP 2: Split the text into chunks
                    chunks = chunk_text(text)

                    # STEP 3: Convert chunks into embeddings
                    embeddings = create_embeddings(chunks)

                    # STEP 4: Store chunks and embeddings
                    if "chunks" not in st.session_state:
                        st.session_state.chunks = {}

                    if "embeddings" not in st.session_state:
                        st.session_state.embeddings = {}

                    st.session_state.chunks[
                        document.name
                    ] = chunks

                    st.session_state.embeddings[
                        document.name
                    ] = embeddings

                    # STEP 5: Tell the user that indexing worked
                    st.success(
                        f"✓ {document.name} indexed successfully"
                    )

                    st.caption(
                        f"{len(text):,} characters · "
                        f"{len(chunks)} chunks · "
                        f"{len(embeddings)} embeddings created"
                    )

                else:

                    st.warning(
                        f"⚠️ {document.name} contains no readable text."
                    )

            except Exception as e:

                st.error(
                    f"Could not process {document.name}: {e}"
                )


    # --------------------------------------------------------
    # RECENT DOCUMENTS
    # --------------------------------------------------------

    st.html("""
    <div class="recent-header">

        <div class="recent-title">
            Recent Documents
        </div>

        <div class="view-all">
            View all →
        </div>

    </div>
    """)


    docs = st.session_state.documents


    if docs:

        columns = st.columns(
            min(4, len(docs))
        )

        for i, document in enumerate(docs):

            with columns[i]:

                extension = (
                    document.name
                    .split(".")[-1]
                    .upper()
                )

                size = round(
                    document.size / 1024,
                    1
                )

                st.html(f"""
                <div class="doc-card">

                    <div class="doc-icon">
                        📄
                    </div>

                    <div class="doc-name">
                        {escape(document.name)}
                    </div>

                    <div class="doc-meta">
                        {extension} · {size} KB
                    </div>

                </div>
                """)

                if st.button(
                    "Remove",
                    key=f"remove_{document.name}"
                ):

                    # Remove document
                    st.session_state.documents = [
                        doc
                        for doc in st.session_state.documents
                        if doc.name != document.name
                    ]

                    # Remove its chunks
                    if document.name in st.session_state.chunks:
                        del st.session_state.chunks[
                            document.name
                        ]

                    # Remove its embeddings
                    if document.name in st.session_state.embeddings:
                        del st.session_state.embeddings[
                            document.name
                        ]

                    st.rerun()

        # --------------------------------------------------------
        # CLEAR ALL DOCUMENTS
        # --------------------------------------------------------

        st.write("")

        if st.button(
            "Clear all documents",
            key="clear_all_documents"
        ):

            st.session_state.documents = []
            st.session_state.chunks = {}
            st.session_state.embeddings = {}

            st.rerun()

    else:

        columns = st.columns(4)


        sample_docs = [

            (
                "📕",
                "Physics Notes",
                "24 pages"
            ),

            (
                "📘",
                "EVS Notes",
                "18 pages"
            ),

            (
                "📗",
                "Maths Module",
                "31 pages"
            ),

            (
                "📙",
                "Lab Manual",
                "27 pages"
            )

        ]


        for column, (
            icon,
            name,
            meta
        ) in zip(
            columns,
            sample_docs
        ):

            with column:

                st.html(f"""
                <div class="doc-card">

                    <div class="doc-icon">
                        {icon}
                    </div>

                    <div class="doc-name">
                        {name}
                    </div>

                    <div class="doc-meta">
                        {meta}
                    </div>

                </div>
                """)


# ============================================================
# DOCUMENTS PAGE
# ============================================================

elif st.session_state.page == "documents":

    st.html("""
    <div class="hero">

        <div class="hero-kicker">
            ✦ YOUR KNOWLEDGE LIBRARY
        </div>

        <div class="hero-title">
            Documents
        </div>

        <div class="hero-tagline">
            Everything you've given ASTRA to understand.
        </div>

    </div>
    """)


    if st.session_state.documents:

        columns = st.columns(4)


        for i, document in enumerate(
            st.session_state.documents
        ):

            with columns[i % 4]:

                st.html(f"""
                <div class="doc-card">

                    <div class="doc-icon">
                        📄
                    </div>

                    <div class="doc-name">
                        {escape(document.name)}
                    </div>

                    <div class="doc-meta">
                        PDF / TXT
                    </div>

                </div>
                """)


    else:

        st.html("""
        <div class="main-panel">

            <div class="upload-inner">

                <div class="upload-icon">
                    ✦
                </div>

                <div class="upload-heading">
                    Your library is waiting.
                </div>

                <div class="upload-description">
                    Upload your first document
                    from the Home page.
                </div>

            </div>

        </div>
        """)


# ============================================================
# CHAT PAGE
# ============================================================

elif st.session_state.page == "chat":

    st.html("""
    <div class="hero">

        <div class="hero-kicker">
            ✦ KNOWLEDGE CONVERSATION
        </div>

        <div class="hero-title">
            ASTRA
        </div>

        <div class="hero-tagline">
            Your knowledge, at your command.
        </div>

    </div>
    """)


    chat_header, new_chat_column = st.columns(
        [8, 1.5]
    )


    with chat_header:

        st.html("""
        <div class="chat-header">

            <div class="chat-file">
                ◫ &nbsp; Your documents
            </div>

        </div>
        """)


    with new_chat_column:

        if st.button(
            "+ New Chat",
            key="new_chat_button",
            use_container_width=True
        ):

            st.session_state.messages = []

            st.rerun()


    # --------------------------------------------------------
    # DOCUMENTS AVAILABLE IN CHAT
    # --------------------------------------------------------

    if st.session_state.documents:

        document_cards = "".join(

            f"""
            <div class="doc-card">

                <div class="doc-icon">
                    📄
                </div>

                <div class="doc-name">
                    {escape(document.name)}
                </div>

                <div class="doc-meta">
                    PDF / TXT
                </div>

            </div>
            """

            for document in st.session_state.documents

        )

    else:

        document_cards = """

        <div class="upload-description">
            No documents uploaded yet.
        </div>

        """


    st.html(f"""

    <div class="chat-panel">

        <div class="chat-document-list">

            {document_cards}

        </div>

    </div>

    """)


    # --------------------------------------------------------
    # DISPLAY PREVIOUS MESSAGES
    # --------------------------------------------------------

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.html(f"""

            <div class="message-user">
                {escape(message["content"])}
            </div>

            """)

        else:

            st.html(f"""

            <div class="message-ai">
                {message["content"]}
            </div>

            """)


    # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    prompt = st.chat_input(
        "Ask ASTRA anything about your documents..."
    )

    if st.button("Clear chat", key="clear_chat"):
        st.session_state.messages = []
        st.rerun()


    if prompt:

        # Store user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )


        # Display user message immediately
        st.html(f"""

        <div class="message-user">
            {escape(prompt)}
        </div>

        """)


        # Temporary loading message
        response_placeholder = st.empty()

        response_placeholder.html("""

        <div class="message-ai">

            ✦ ASTRA is searching your documents
            and preparing an answer...

        </div>

        """)


        # --------------------------------------------------------
        # CHECK WHETHER DOCUMENTS ARE AVAILABLE
        # --------------------------------------------------------

        if not st.session_state.documents:

            st.warning(
                "Please upload at least one PDF or TXT document "
                "before asking a question."
            )

            st.stop()


        # --------------------------------------------------------
        # STEP 1: Convert the user's question into an embedding
        # --------------------------------------------------------

        query_embedding = create_embeddings(
            [prompt]
        )[0]


        # ====================================================
        # STEP 2: COLLECT ALL CHUNKS
        # ====================================================

        all_chunks = []

        all_embeddings = []

        all_sources = []


        if "chunks" in st.session_state:

            for document_name in (
                st.session_state.chunks
            ):

                document_chunks = (
                    st.session_state.chunks[
                        document_name
                    ]
                )

                document_embeddings = (
                    st.session_state.embeddings[
                        document_name
                    ]
                )


                all_chunks.extend(
                    document_chunks
                )

                all_embeddings.extend(
                    document_embeddings
                )


                # Remember which document
                # each chunk belongs to
                all_sources.extend(
                    [document_name]
                    * len(document_chunks)
                )


        # ====================================================
        # STEP 3: RETRIEVE TOP 3 CHUNKS
        # ====================================================

        results = retrieve_top_chunks(

            query_embedding=query_embedding,

            chunks=all_chunks,

            chunk_embeddings=all_embeddings,

            top_k=3

        )


        # ====================================================
        # STEP 4: GENERATE ANSWER
        # ====================================================

        if results:

            try:

                with st.spinner(
                    "Generating your answer..."
                ):

                    answer_text = generate_answer(

                        query=prompt,

                        retrieved_chunks=results

                    )


                # Format Gemini response
                formatted_answer = (
                    format_answer_html(
                        answer_text
                    )
                )


                # Start answer card
                answer = f"""

                <div class="message-ai">

                    <div style="
                        font-size:18px;
                        font-weight:600;
                        color:#e8f7ff;
                        margin-bottom:14px;
                    ">

                        ✦ ASTRA

                    </div>


                    <div style="
                        line-height:1.8;
                        color:#dbeafe;
                    ">

                        {formatted_answer}

                    </div>


                    <div style="
                        margin-top:22px;
                        margin-bottom:10px;
                        font-size:14px;
                        font-weight:600;
                        color:#67e8f9;
                    ">

                        ✦ Referenced document sections

                    </div>

                """


                # ====================================================
                # SHOW SOURCES
                # ====================================================

                for i, result in enumerate(
                    results,
                    start=1
                ):

                    score = result["score"]

                    chunk = result["chunk"]

                    chunk_index = result.get(
                        "index",
                        i - 1
                    )


                    # Find source document
                    if (
                        chunk_index
                        < len(all_sources)
                    ):

                        source_name = (
                            all_sources[
                                chunk_index
                            ]
                        )

                    else:

                        source_name = (
                            "Uploaded document"
                        )


                    safe_source = escape(
                        source_name
                    )

                    safe_chunk = escape(
                        chunk[:1000]
                    )


                    answer += f"""

                    <div class="source-card">

                        <div class="source-name">

                            ✦ {safe_source}

                            <span style="
                                color:#67e8f9;
                                font-weight:500;
                            ">

                                · similarity
                                {score:.3f}

                            </span>

                        </div>


                        <div class="source-text">

                            {safe_chunk}

                        </div>

                    </div>

                    """


                answer += """

                </div>

                """


                # Store answer
                st.session_state.messages.append(

                    {
                        "role": "assistant",
                        "content": answer
                    }

                )


                # Display answer
                response_placeholder.html(
                    answer
                )


            except Exception:

                error_answer = f"""

                <div class="message-ai">

                    ✦ ASTRA couldn't generate an answer right now.
                    Please try again shortly.

                </div>

                """


                st.session_state.messages.append(

                    {
                        "role": "assistant",
                        "content": error_answer
                    }

                )


                response_placeholder.html(
                    error_answer
                )

            else:

                st.rerun()


        else:

            no_results_answer = """

            <div class="message-ai">

                ✦ ASTRA couldn't find relevant information
                in your uploaded documents.

            </div>

            """


            st.session_state.messages.append(

                {
                    "role": "assistant",
                    "content": no_results_answer
                }

            )


            response_placeholder.html(
                no_results_answer
            )

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.html("""

<div class="footer">

    ✦ ASTRA · YOUR KNOWLEDGE, AT YOUR COMMAND ✦

</div>

""")