import streamlit as st
import pandas as pd
import os
import json
import time
from datetime import datetime
from ranking_engine import run_ranking, evaluate_candidate, load_candidates

# Set page config
st.set_page_config(
    page_title="Redrob Candidate Ranking Terminal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply font family */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Title gradient */
    .title-gradient {
        background: linear-gradient(135deg, #6366F1 0%, #EC4899 50%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle-glow {
        color: #9CA3AF;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Premium Metric Card */
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #818CF8, #C084FC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .metric-lbl {
        font-size: 0.8rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 500;
    }
    
    /* Profile Details Card */
    .profile-card {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        margin-top: 15px;
    }
    
    /* Skills Badge */
    .skill-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 4px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(147, 51, 234, 0.2) 100%);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #E0E7FF;
        transition: all 0.2s;
    }
    
    .skill-badge:hover {
        background: rgba(99, 102, 241, 0.4);
        transform: scale(1.05);
    }
    
    /* Section headers styling */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #F3F4F6;
        border-bottom: 2px solid rgba(99, 102, 241, 0.2);
        padding-bottom: 8px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load and execute engine
@st.cache_data(ttl=60)
def get_rankings():
    # Make sure sample candidate file exists
    if not os.path.exists("candidates.jsonl") and not os.path.exists("sample_candidates.json"):
        st.info("Input files missing. Triggering mock candidate generator...")
        try:
            import candidate_generator
            candidate_generator.main()
        except Exception as e:
            st.error(f"Failed to generate mock data: {e}")
            
    # Run ranking engine
    try:
        ranked_list = run_ranking()
        return ranked_list
    except Exception as e:
        st.error(f"Error running ranking engine: {e}")
        return []

# Sidebar Content
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/artificial-intelligence.png", width=70)
    st.markdown("<h2 style='margin-top: 0;'>System Settings</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### Target Role Profile")
    st.info("""
    **Title**: Senior AI Engineer
    **Experience**: 5 - 9 Years
    **Location**: Remote / CPU Local
    """)
    
    st.markdown("### Key Matching Parameters")
    st.markdown("""
    - **Base Fit**: AI/ML Engineer, Data Scientist title matches.
    - **Skill Score**: PyTorch, LLMs, NLP, CV, Tensorflow, Python.
    - **Penalties**: Slash non-technical titles claiming ML skills.
    - **Behavioral**: Scaled on Recruiter Response, Interview Completion, and Open-to-Work flags.
    """)
    
    st.markdown("---")
    if st.button("🔄 Recalculate Rankings & Data"):
        st.cache_data.clear()
        st.success("Refreshed candidates and updated rankings!")
        st.rerun()

# Execute ranking and fetch data
top_100_details = get_rankings()

if not top_100_details:
    st.error("No candidates loaded or ranking system failed. Please run candidate generator first.")
else:
    # 1. Main Header
    st.markdown("<div class='title-gradient'>Redrob AI Ranker</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-glow'>High-performance, CPU-optimized matching engine for Senior AI Engineers</div>", unsafe_allow_html=True)
    
    # Calculate top-level stats
    total_processed = 200 # We generated 200 candidates
    max_score = top_100_details[0]["final_score"] if top_100_details else 0.0
    avg_score = round(sum(c["final_score"] for c in top_100_details) / len(top_100_details), 1) if top_100_details else 0.0
    
    # Calculate stuffers dynamically
    stuffers_caught = 0
    all_raw_cands = []
    # Try reading all to see how many got stuffers penalty
    for path in ["candidates.jsonl", "sample_candidates.json"]:
        if os.path.exists(path):
            all_raw_cands = load_candidates(path)
            break
    for c in all_raw_cands:
        # evaluate base score and check stuffer
        evaluation = evaluate_candidate(c)
        if "KEYWORD STUFFER" in evaluation["reasoning"]:
            stuffers_caught += 1

    # 2. Key Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-val'>{total_processed}</div>
            <div class='metric-lbl'>Candidates Evaluated</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-val'>{max_score:.2f}</div>
            <div class='metric-lbl'>Top Match Score</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-val'>{avg_score:.1f}</div>
            <div class='metric-lbl'>Average Score (Top 100)</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-val' style='background: linear-gradient(90deg, #F87171, #EF4444); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{stuffers_caught}</div>
            <div class='metric-lbl'>Stuffers Flagged & Slashed</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. Main Dashboard Layout (Grid Split)
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        st.markdown("<div class='section-header'>Top 100 Ranked Candidates</div>", unsafe_allow_html=True)
        
        # Build search box
        search_query = st.text_input("🔍 Search candidates by ID, Title, or Reasoning", "").lower().strip()
        
        # Format table data
        table_rows = []
        for idx, c in enumerate(top_100_details, 1):
            table_rows.append({
                "Rank": idx,
                "Candidate ID": c["candidate_id"],
                "Name": c["name"],
                "Current Title": c["current_title"],
                "Final Score": c["final_score"],
                "Reasoning Summary": c["reasoning"]
            })
            
        df = pd.DataFrame(table_rows)
        
        # Apply search filter
        if search_query:
            df = df[
                df["Candidate ID"].str.lower().str.contains(search_query) |
                df["Name"].str.lower().str.contains(search_query) |
                df["Current Title"].str.lower().str.contains(search_query) |
                df["Reasoning Summary"].str.lower().str.contains(search_query)
            ]
            
        # Display data table
        st.dataframe(
            df,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width=50),
                "Candidate ID": st.column_config.TextColumn("Candidate ID", width=100),
                "Name": st.column_config.TextColumn("Candidate Name", width=140),
                "Current Title": st.column_config.TextColumn("Current Title", width=180),
                "Final Score": st.column_config.NumberColumn("Final Score", format="%.2f", width=100),
                "Reasoning Summary": st.column_config.TextColumn("Reasoning details", width=380)
            },
            hide_index=True,
            use_container_width=True,
            height=500
        )
        
        # Download button
        st.markdown("<br>", unsafe_allow_html=True)
        if os.path.exists("submission.csv"):
            with open("submission.csv", "rb") as file:
                btn = st.download_button(
                    label="📥 Download Validated CSV Submission",
                    data=file,
                    file_name="submission.csv",
                    mime="text/csv",
                    type="primary"
                )
        else:
            st.warning("submission.csv not found. Click 'Recalculate Rankings & Data' to generate.")

    with right_col:
        st.markdown("<div class='section-header'>Candidate Deep Dive Analysis</div>", unsafe_allow_html=True)
        
        # Dropdown selection for the analysis panel
        available_ids = df["Candidate ID"].tolist() if not df.empty else [c["candidate_id"] for c in top_100_details]
        
        selected_id = st.selectbox(
            "Select Candidate to Profile:",
            options=available_ids,
            index=0 if available_ids else None
        )
        
        if selected_id:
            # Find candidate record
            cand_record = next((c for c in top_100_details if c["candidate_id"] == selected_id), None)
            
            if cand_record:
                # Render Candidate Details Card
                st.markdown(f"""
                <div class='profile-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                        <span style='font-size: 1.5rem; font-weight: 700; color: #EEF2F6;'>{cand_record["name"]}</span>
                        <span style='font-size: 0.95rem; font-weight: 600; color: #A5B4FC; background: rgba(99, 102, 241, 0.15); padding: 4px 10px; border-radius: 12px;'>ID: {cand_record["candidate_id"]}</span>
                    </div>
                    <div style='color: #9CA3AF; font-size: 0.9rem; margin-bottom: 12px;'>
                        <strong style='color: #E5E7EB;'>Current Role:</strong> {cand_record["current_title"]}
                    </div>
                    <div style='color: #9CA3AF; font-size: 0.9rem; margin-bottom: 12px;'>
                        <strong style='color: #E5E7EB;'>Experience:</strong> {cand_record["years_of_experience"]} Years
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render key signals in columns with metric cards
                c1, c2, c3 = st.columns(3)
                with c1:
                    # Fetch profile completeness
                    comp = cand_record.get("profile_completeness", 0.0)
                    st.metric("Profile Comp.", f"{int(comp * 100)}%")
                with c2:
                    rrr = cand_record.get("recruiter_response_rate", 0.0)
                    st.metric("Response Rate", f"{int(rrr * 100)}%")
                with c3:
                    github = cand_record.get("github_activity_score", 0.0)
                    st.metric("GitHub Score", f"{github:.0f}/100")
                
                # Score components explanation
                st.markdown("<div style='margin-top: 20px; font-weight: 600; color: #F3F4F6;'>Score Breakdown</div>", unsafe_allow_html=True)
                
                # Fetch base evaluation of the candidate to show base components
                # Find original candidate data first
                original_cand = next((c for c in all_raw_cands if c.get("candidate_id") == selected_id), None)
                if original_cand:
                    eval_res = evaluate_candidate(original_cand)
                    base_score = eval_res["base_score"]
                    mult = eval_res["multiplier"]
                    final = eval_res["final_score"]
                    
                    st.markdown(f"""
                    <table style='width: 100%; border-collapse: collapse; font-size: 0.9rem; color: #9CA3AF;'>
                        <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.05);'>
                            <td style='padding: 8px 0; color: #E5E7EB;'>Base Score</td>
                            <td style='padding: 8px 0; text-align: right; font-weight: 600; color: #818CF8;'>{base_score:.1f} / 100.0</td>
                        </tr>
                        <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.05);'>
                            <td style='padding: 8px 0; color: #E5E7EB;'>Behavioral Multiplier</td>
                            <td style='padding: 8px 0; text-align: right; font-weight: 600; color: #C084FC;'>{mult:.2f}x</td>
                        </tr>
                        <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                            <td style='padding: 8px 0; color: #E5E7EB; font-weight: 600;'>Final Match Score</td>
                            <td style='padding: 8px 0; text-align: right; font-weight: 700; color: #10B981; font-size: 1.15rem;'>{final:.2f}</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)
                    
                    # Display reasoning
                    st.markdown("<div style='margin-top: 15px; font-weight: 600; color: #F3F4F6;'>Matching Summary</div>", unsafe_allow_html=True)
                    st.caption(eval_res["reasoning"])
                    
                    # Display skills as badges
                    st.markdown("<div style='margin-top: 15px; font-weight: 600; color: #F3F4F6;'>Candidate Skills</div>", unsafe_allow_html=True)
                    skills_list = original_cand.get("skills", [])
                    if skills_list:
                        badges_html = "".join([f"<span class='skill-badge'>{s}</span>" for s in skills_list])
                        st.markdown(badges_html, unsafe_allow_html=True)
                    else:
                        st.write("No skills listed.")
                    
                    # Display career history
                    st.markdown("<div style='margin-top: 15px; font-weight: 600; color: #F3F4F6;'>Career Timeline</div>", unsafe_allow_html=True)
                    history_list = original_cand.get("career_history", [])
                    if history_list:
                        for job in history_list:
                            duration = job.get("duration_years", job.get("years", 0))
                            st.markdown(f"🔹 **{job.get('title')}** — *{duration} Years*")
                    else:
                        st.write("No historical career data listed.")
            else:
                st.info("Select a candidate to inspect details.")
        else:
            st.info("No candidates matching the criteria.")
