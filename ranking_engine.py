import json
import os
import csv
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define target constants
TARGET_ROLE = "Senior AI Engineer"
MIN_EXP = 5
MAX_EXP = 9

# Core skills list
CORE_SKILLS = [
    "python", "pytorch", "tensorflow", "keras", "scikit-learn", 
    "machine learning", "deep learning", "nlp", "computer vision", 
    "transformers", "llm", "llms", "bert", "gpt", 
    "reinforcement learning", "neural networks", "data science"
]

# Non-technical title keywords (keyword stuffers)
NON_TECH_KEYWORDS = [
    "marketing", "hr", "human resources", "operations", "accountant", 
    "accounting", "support", "sales", "recruiter", "recruiting", 
    "admin", "secretary", "customer service", "assistant", 
    "receptionist", "office coordinator", "writer"
]

def calculate_experience(candidate):
    """Safely calculate total years of experience, checking direct and list elements."""
    years = candidate.get("years_of_experience")
    if years is not None:
        try:
            return float(years)
        except ValueError:
            pass
            
    # Fallback to summing duration in career history
    years = 0.0
    history = candidate.get("career_history", [])
    if isinstance(history, list):
        for job in history:
            if isinstance(job, dict):
                # Try duration_years
                dur = job.get("duration_years")
                if dur is not None:
                    try:
                        years += float(dur)
                        continue
                    except ValueError:
                        pass
                # Or try parsing dates if present (optional fallback)
    return round(years, 1)

def evaluate_candidate(candidate, current_date=datetime(2026, 6, 29)):
    """Evaluate a single candidate and return base score, multiplier, final score, and reasoning."""
    cand_id = candidate.get("candidate_id", "UNKNOWN")
    name = candidate.get("name", "Unknown Candidate")
    
    # 1. EXPERIENCE SCORE (Max 30)
    years_exp = calculate_experience(candidate)
    if MIN_EXP <= years_exp <= MAX_EXP:
        exp_score = 30.0
        exp_reason = f"{years_exp}y exp (Optimal)"
    elif 3.0 <= years_exp < MIN_EXP or MAX_EXP < years_exp <= 12.0:
        exp_score = 20.0
        exp_reason = f"{years_exp}y exp (Adjacent)"
    else:
        exp_score = 10.0
        exp_reason = f"{years_exp}y exp (Suboptimal)"
        
    if years_exp == 0.0:
        exp_score = 0.0
        exp_reason = "No experience listed"

    # 2. TITLE FIT SCORE (Max 40)
    current_title = str(candidate.get("current_title", "")).strip()
    current_title_lower = current_title.lower()
    
    title_score = 0.0
    title_reason = "No matching title"
    
    # Target keywords for AI/ML/Data Science
    target_kws = ["ai engineer", "ml engineer", "data scientist", "machine learning"]
    
    current_match = any(kw in current_title_lower for kw in target_kws)
    if current_match:
        title_score = 40.0
        title_reason = f"Current title matches target: '{current_title}'"
    else:
        # Check historical titles
        history_match = False
        history_title = ""
        history = candidate.get("career_history", [])
        if isinstance(history, list):
            for job in history:
                if isinstance(job, dict):
                    t = str(job.get("title", "")).strip()
                    if any(kw in t.lower() for kw in target_kws):
                        history_match = True
                        history_title = t
                        break
        if history_match:
            title_score = 25.0
            title_reason = f"Historical title matches target: '{history_title}'"

    # 3. SKILLS FIT SCORE (Max 30)
    skills = candidate.get("skills", [])
    if not isinstance(skills, list):
        skills = []
        
    skills_lower = [str(s).lower().strip() for s in skills]
    matched_skills = []
    for skill in skills_lower:
        if any(cs in skill for cs in CORE_SKILLS):
            matched_skills.append(skill)
            
    # Dedup and count
    matched_count = len(set(matched_skills))
    # Cap matching reward at 6 skills
    skill_score = round(min(matched_count, 6) / 6 * 30.0, 1)
    skills_reason = f"{matched_count} AI/ML skills matched"

    # 4. KEYWORD STUFFER PENALTY
    # If current title is non-technical, but lists AI/ML skills
    is_non_tech = any(kw in current_title_lower for kw in NON_TECH_KEYWORDS)
    has_ml_signals = (matched_count > 0) or (title_score > 0.0)
    
    base_score = exp_score + title_score + skill_score
    is_stuffer = False
    
    if is_non_tech and has_ml_signals:
        is_stuffer = True
        original_base = base_score
        base_score = min(base_score * 0.1, 10.0)
        penalty_reason = f"KEYWORD STUFFER PENALTY: Title is non-technical ('{current_title}') but lists ML skills/history. Score slashed from {original_base:.1f} to {base_score:.1f}."
    else:
        penalty_reason = ""

    # 5. BEHAVIORAL MULTIPLIER (0.5 to 1.5)
    signals = candidate.get("redrob_signals", {})
    if not isinstance(signals, dict):
        signals = {}
        
    # Extractor with robust default fallbacks
    def get_float_signal(name, default):
        val = signals.get(name)
        if val is None:
            return default
        try:
            return float(val)
        except ValueError:
            return default

    recruiter_rate = get_float_signal("recruiter_response_rate", 0.7)
    interview_rate = get_float_signal("interview_completion_rate", 0.7)
    
    open_to_work = signals.get("open_to_work_flag")
    open_to_work = bool(open_to_work) if open_to_work is not None else False
    
    # Notice Period Penalty
    notice_days = signals.get("notice_period_days")
    if notice_days is None:
        notice_days = 30
    else:
        try:
            notice_days = int(notice_days)
        except ValueError:
            notice_days = 30
            
    notice_penalty = 0.0
    if notice_days > 90:
        notice_penalty = 0.2
    elif notice_days > 60:
        notice_penalty = 0.1
        
    # Activity Penalty
    last_active_str = signals.get("last_active_date")
    days_inactive = 60 # Default average active days
    if last_active_str:
        try:
            active_date = datetime.strptime(last_active_str, "%Y-%m-%d")
            days_inactive = (current_date - active_date).days
        except Exception:
            days_inactive = 60
            
    active_penalty = 0.0
    if days_inactive > 180:
        active_penalty = 0.2
    elif days_inactive > 90:
        active_penalty = 0.1

    # Multiplier formula
    raw_mult = 0.5 + (0.4 * recruiter_rate) + (0.3 * interview_rate) + (0.3 if open_to_work else 0.0)
    multiplier = raw_mult - notice_penalty - active_penalty
    multiplier = max(0.5, min(1.5, multiplier))
    multiplier = round(multiplier, 2)
    
    # Combined Score
    final_score = round(base_score * multiplier, 2)
    
    # Generate Reasoning Summary
    if is_stuffer:
        reasoning = f"{penalty_reason} Mult: {multiplier}x."
    else:
        reasons_list = [exp_reason, title_reason, skills_reason]
        if notice_penalty > 0:
            reasons_list.append(f"Notice: {notice_days}d (-{notice_penalty})")
        if active_penalty > 0:
            reasons_list.append(f"Inactive: {days_inactive}d (-{active_penalty})")
        reasons_list.append(f"Signals (RRR: {int(recruiter_rate*100)}%, ICR: {int(interview_rate*100)}%, OTW: {open_to_work})")
        reasoning = " | ".join(reasons_list) + f" | Mult: {multiplier}x"

    return {
        "candidate_id": cand_id,
        "name": name,
        "current_title": current_title,
        "years_of_experience": years_exp,
        "base_score": base_score,
        "multiplier": multiplier,
        "final_score": final_score,
        "reasoning": reasoning,
        "profile_completeness": get_float_signal("profile_completeness", 0.8),
        "github_activity_score": get_float_signal("github_activity_score", 50.0),
        "recruiter_response_rate": recruiter_rate
    }

def load_candidates(file_path):
    """Load candidates from a JSON or JSONL file."""
    candidates = []
    
    if not os.path.exists(file_path):
        logging.warning(f"File {file_path} not found.")
        return candidates

    try:
        # Check if JSONL format (ends with .jsonl or lines are readable)
        if file_path.endswith(".jsonl"):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        candidates.append(json.loads(line))
        else:
            # Try reading as single JSON array
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    candidates = data
                elif isinstance(data, dict):
                    # Edge case where JSON is single dict or candidates key
                    candidates = data.get("candidates", [data])
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        
    return candidates

def run_ranking(input_path=None, output_path="submission.csv"):
    """Core ranking execution loop."""
    # Automatic fallback search
    candidates = []
    
    if input_path:
        logging.info(f"Attempting to load specified file: {input_path}")
        candidates = load_candidates(input_path)
    else:
        # Check defaults
        for path in ["candidates.jsonl", "sample_candidates.json"]:
            if os.path.exists(path):
                logging.info(f"Loading candidates from default path: {path}")
                candidates = load_candidates(path)
                break
                
    # If still empty, trigger data generator
    if not candidates:
        logging.info("No candidate source files found. Triggering automated candidate generator...")
        try:
            import candidate_generator
            candidate_generator.main()
            candidates = load_candidates("candidates.jsonl")
        except ImportError:
            logging.error("Could not import candidate_generator. No input data available.")
            return []
            
    logging.info(f"Loaded {len(candidates)} candidates. Beginning scoring operations...")
    
    scored_candidates = []
    for cand in candidates:
        scored = evaluate_candidate(cand)
        scored_candidates.append(scored)
        
    # Sort: Descending by final_score, Ascending by candidate_id
    # Key trick: -x['final_score'] sorts float descending, x['candidate_id'] sorts string ascending (case-insensitive)
    scored_candidates.sort(key=lambda x: (-x["final_score"], str(x["candidate_id"]).upper()))
    
    # Slice top 100
    top_100 = scored_candidates[:100]
    logging.info(f"Scoring complete. Selected Top {len(top_100)} candidates.")
    
    # Save CSV
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Header
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for idx, cand in enumerate(top_100, 1):
            writer.writerow([
                cand["candidate_id"],
                idx,
                f"{cand['final_score']:.2f}",
                cand["reasoning"]
            ])
            
    logging.info(f"Rankings successfully written to {output_path}")
    return top_100

if __name__ == "__main__":
    import sys
    inp = sys.argv[1] if len(sys.argv) > 1 else None
    out = sys.argv[2] if len(sys.argv) > 2 else "submission.csv"
    run_ranking(inp, out)
