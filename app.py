"""Natural Language Search Interface for PostgreSQLSimplified Streamlit Application"""

import streamlit as st
import pandas as pd
from services.search_service import SearchService
from services.query_generator import QueryGenerator
from config import Config
from logger_config import get_logger
import traceback

logger = get_logger("StreamlitApp")

st.set_page_config(
    page_title="NL Search - PostgreSQL",
    page_icon="🔍",
    layout="centered",
)

st.markdown("""
<style>
/* App background */
.stApp {
    background: #F6F0D7;
}

/* Title */
.app-title {
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    color: black;
    margin-bottom: 0.5rem;
}

/* Subtitle */
.app-subtitle {
    text-align: center;
    color: #6b7280;
    margin-bottom: 1.8rem;
}

/* Search input */
div[data-baseweb="input"] input {
    border-radius: 10px;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
}

/* Search button */
.stButton button {
    width: 100%;
    border-radius: 10px;
    padding: 0.6rem;
    font-size: 1rem;
    font-weight: 600;
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border: none;
}

.stButton button:hover {
    background: linear-gradient(90deg, #1d4ed8, #1e40af);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_services():
    try:
        Config.validate()
        logger.info("Services initialized successfully")
        return SearchService(), QueryGenerator()
    except Exception as e:
        logger.exception("Failed to initialize services")
        st.error(f"Failed to initialize services: {str(e)}")
        return None, None

if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'current_results' not in st.session_state:
    st.session_state.current_results = None

def main():

    st.markdown("<div class='main-card'>", unsafe_allow_html=True)

    st.markdown("<div class='app-title'>🔍 Natural Language Search</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='app-subtitle'>Ask questions in plain English/Hindi and get PostgreSQL database instantly</div>",
        unsafe_allow_html=True
    )

    search_service, query_generator = init_services()
    if not search_service or not query_generator:
        st.error("❌ Services not initialized properly")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    user_query = st.text_input(
        "Enter your question",
        placeholder="e.g., Show all employees in the Engineering department",
        label_visibility="collapsed"
    )

    search_button = st.button("🔍 Search")

    if search_button and user_query:
        logger.info("User query: %s", user_query)
        with st.spinner("🔄 Processing your query..."):
            try:
                if user_query not in st.session_state.search_history:
                    st.session_state.search_history.append(user_query)

                result = search_service.search(user_query)
                st.session_state.current_results = result
                logger.info("Query executed successfully")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.exception("Error while processing query")
                if Config.DEBUG:
                    st.code(traceback.format_exc())

    if st.session_state.current_results:
        result = st.session_state.current_results

        if result.get("explanation"):
            st.info(f"📝 {result['explanation']}")

        if result.get("sql_query"):
            with st.expander("🔧 Generated SQL Query"):
                st.code(result["sql_query"], language="sql")

        if result.get("success"):
            df = pd.DataFrame(result["results"])
            if not df.empty:
                st.success(f"✅ Found {len(df)} results")

                for col in df.columns:
                    if any(k in col.lower() for k in ["salary", "price", "total"]):
                        df[col] = df[col].apply(
                            lambda x: f"${float(x):,.2f}" if pd.notnull(x) else ""
                        )
                    elif "similarity" in col.lower():
                        df[col] = df[col].apply(
                            lambda x: f"{float(x)*100:.1f}%" if pd.notnull(x) else ""
                        )

                st.dataframe(df, use_container_width=True, hide_index=True)

                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download Results (CSV)",
                    csv,
                    "search_results.csv",
                    "text/csv",
                )
            else:
                st.warning("No results found.")
        else:
            st.error(result.get("error", "Unknown error"))

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
