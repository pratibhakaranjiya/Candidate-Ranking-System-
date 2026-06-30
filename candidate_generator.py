import json
import random
import os
from datetime import datetime, timedelta

def generate_candidates(num_candidates=200):
    first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Oliver", "Sophia", "Elijah", "Isabella", "James",
                   "Amelia", "Benjamin", "Mia", "Lucas", "Charlotte", "Mason", "Harper", "Logan", "Evelyn", "Alexander",
                   "Abigail", "Ethan", "Emily", "Jacob", "Elizabeth", "Michael", "Sofia", "Daniel", "Avery", "Henry",
                   "Raj", "Priya", "Amit", "Anjali", "Kenji", "Yuki", "Mei", "Chen", "Aris", "Elena"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                  "Patel", "Sharma", "Singh", "Sato", "Tanaka", "Wang", "Li", "Kim", "Park", "Papadopoulos"]

    tech_titles = ["AI Engineer", "ML Engineer", "Data Scientist", "Senior AI Engineer", "Senior ML Engineer", 
                   "Lead Data Scientist", "Principal AI Researcher", "Software Engineer (ML)", "Computer Vision Engineer"]
    
    other_tech_titles = ["Software Engineer", "Full Stack Developer", "Backend Engineer", "DevOps Engineer", 
                         "Database Administrator", "System Administrator", "Frontend Engineer", "QA Engineer"]
                         
    non_tech_titles = ["Marketing Manager", "HR Specialist", "Operations Coordinator", "Accountant", 
                       "Customer Support Representative", "Sales Executive", "Office Assistant", "Receptionist", 
                       "Content Writer", "Social Media Strategist", "Product Marketing Associate"]

    all_skills = [
        "Python", "PyTorch", "TensorFlow", "Scikit-Learn", "Machine Learning", "Deep Learning",
        "Natural Language Processing", "Computer Vision", "Transformers", "LLMs", "BERT", "GPT",
        "Reinforcement Learning", "Neural Networks", "Data Science", "SQL", "Git", "Docker",
        "AWS", "Linux", "Kubernetes", "C++", "Java", "R", "Keras", "Pandas", "NumPy"
    ]
    
    non_ml_skills = ["HTML", "CSS", "React", "Node.js", "Marketing", "Recruiting", "Excel", "Accounting", 
                     "Customer Relations", "Salesforce", "Copywriting", "SEO", "Project Management"]

    candidates = []
    
    # Let's seed for deterministic generation so output is stable for testing
    random.seed(42)

    current_date = datetime(2026, 6, 29)

    for i in range(1, num_candidates + 1):
        candidate_id = f"CAND_{i:03d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Decide candidate profile type
        # 1: Ideal Target (Senior AI/ML, 5-9 years)
        # 2: Junior AI/ML (< 5 years)
        # 3: Super Senior AI/ML (> 9 years)
        # 4: Tech, but non-ML (Software Engineer, Backend, etc.)
        # 5: Keyword Stuffers (Non-tech title, but claims AI/ML skills)
        # 6: Edge Case (Missing data, null fields, etc.)
        profile_type = random.choices(
            [1, 2, 3, 4, 5, 6],
            weights=[30, 20, 15, 15, 10, 10],
            k=1
        )[0]
        
        skills = []
        career_history = []
        current_title = ""
        years_of_experience = 0
        
        # Behavioral signals
        recruiter_response_rate = round(random.uniform(0.3, 1.0), 2)
        interview_completion_rate = round(random.uniform(0.4, 1.0), 2)
        open_to_work_flag = random.choice([True, False])
        
        # Active date (within last year)
        days_ago = random.randint(0, 365)
        last_active = current_date - timedelta(days=days_ago)
        last_active_date = last_active.strftime("%Y-%m-%d")
        
        notice_period_days = random.choice([0, 15, 30, 45, 60, 90, 120])
        profile_completeness = round(random.uniform(0.5, 1.0), 2)
        github_activity_score = round(random.uniform(10.0, 100.0), 1)

        # Build profiles based on type
        if profile_type == 1:
            # Ideal: Senior AI/ML, 5-9 years
            years_of_experience = round(random.uniform(5.0, 9.0), 1)
            current_title = random.choice([t for t in tech_titles if "Senior" in t or "Lead" in t or "AI" in t])
            # Add strong ML skills
            skills = random.sample(all_skills[:15], random.randint(5, 10)) + ["Python"]
            # Remove duplicates
            skills = list(set(skills))
            
            # Setup career history
            prev_title = "ML Engineer" if "Senior" in current_title else "Software Engineer"
            career_history = [
                {"title": current_title, "duration_years": round(years_of_experience * 0.6, 1)},
                {"title": prev_title, "duration_years": round(years_of_experience * 0.4, 1)}
            ]
            # Good signals mostly
            recruiter_response_rate = round(random.uniform(0.8, 1.0), 2)
            interview_completion_rate = round(random.uniform(0.8, 1.0), 2)
            open_to_work_flag = random.choice([True, True, False]) # high probability OTW
            notice_period_days = random.choice([15, 30, 45, 60])
            days_ago = random.randint(0, 45) # active recently
            last_active_date = (current_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
        elif profile_type == 2:
            # Junior: AI/ML, < 5 years
            years_of_experience = round(random.uniform(1.0, 4.9), 1)
            current_title = random.choice([t for t in tech_titles if "Senior" not in t and "Lead" not in t and "Principal" not in t])
            skills = random.sample(all_skills[:12], random.randint(3, 7)) + ["Python"]
            skills = list(set(skills))
            career_history = [
                {"title": current_title, "duration_years": years_of_experience}
            ]
            
        elif profile_type == 3:
            # Super Senior: AI/ML, > 9 years
            years_of_experience = round(random.uniform(9.1, 15.0), 1)
            current_title = random.choice(["Lead Data Scientist", "Principal AI Researcher", "Senior AI Engineer"])
            skills = random.sample(all_skills[:18], random.randint(6, 12)) + ["Python"]
            skills = list(set(skills))
            career_history = [
                {"title": current_title, "duration_years": round(years_of_experience * 0.4, 1)},
                {"title": "Senior ML Engineer", "duration_years": round(years_of_experience * 0.4, 1)},
                {"title": "Software Engineer", "duration_years": round(years_of_experience * 0.2, 1)}
            ]
            
        elif profile_type == 4:
            # Tech, but non-ML (Software Engineer, Frontend, Backend)
            years_of_experience = round(random.uniform(3.0, 10.0), 1)
            current_title = random.choice(other_tech_titles)
            # Mix of general tech skills, maybe 1 ML skill
            skills = random.sample(non_ml_skills[:5], random.randint(2, 4)) + ["Python", "SQL", "Git"]
            if random.random() < 0.3:
                skills.append(random.choice(all_skills[:10]))
            skills = list(set(skills))
            career_history = [
                {"title": current_title, "duration_years": years_of_experience}
            ]
            
        elif profile_type == 5:
            # Keyword Stuffers: Non-tech title, but lists AI/ML skills
            years_of_experience = round(random.uniform(2.0, 8.0), 1)
            current_title = random.choice(non_tech_titles)
            # Claims highly technical skills
            skills = random.sample(all_skills[:15], random.randint(6, 11)) + ["Excel", "Marketing"]
            skills = list(set(skills))
            career_history = [
                {"title": current_title, "duration_years": years_of_experience}
            ]
            
        else:
            # Edge Case: Missing or corrupted fields
            years_of_experience = round(random.uniform(2.0, 10.0), 1)
            current_title = random.choice(tech_titles + other_tech_titles + non_tech_titles)
            skills = random.sample(all_skills[:10], random.randint(2, 6))
            career_history = [
                {"title": current_title, "duration_years": years_of_experience}
            ]
            
            # We will set some fields to None (null) or omit them
            edge_type = random.randint(1, 4)
            if edge_type == 1:
                recruiter_response_rate = None
            elif edge_type == 2:
                interview_completion_rate = None
            elif edge_type == 3:
                notice_period_days = None
            elif edge_type == 4:
                last_active_date = None

        # Build candidate object
        cand_obj = {
            "candidate_id": candidate_id,
            "name": name,
            "current_title": current_title,
            "years_of_experience": years_of_experience,
            "skills": skills,
            "career_history": career_history,
            "redrob_signals": {}
        }
        
        # Populate redrob_signals with potential None/missing values
        signals = {}
        if recruiter_response_rate is not None:
            signals["recruiter_response_rate"] = recruiter_response_rate
        if interview_completion_rate is not None:
            signals["interview_completion_rate"] = interview_completion_rate
        if open_to_work_flag is not None:
            signals["open_to_work_flag"] = open_to_work_flag
        if last_active_date is not None:
            signals["last_active_date"] = last_active_date
        if notice_period_days is not None:
            signals["notice_period_days"] = notice_period_days
        if profile_completeness is not None:
            signals["profile_completeness"] = profile_completeness
        if github_activity_score is not None:
            signals["github_activity_score"] = github_activity_score
            
        cand_obj["redrob_signals"] = signals
        candidates.append(cand_obj)
        
    return candidates

def main():
    candidates = generate_candidates(200)
    
    # Save as sample_candidates.json (JSON Array)
    json_path = "sample_candidates.json"
    with open(json_path, "w") as f:
        json.dump(candidates, f, indent=2)
    print(f"Generated {len(candidates)} candidates in {json_path}")
    
    # Save as candidates.jsonl (JSON Lines)
    jsonl_path = "candidates.jsonl"
    with open(jsonl_path, "w") as f:
        for cand in candidates:
            f.write(json.dumps(cand) + "\n")
    print(f"Generated {len(candidates)} candidates in {jsonl_path}")

if __name__ == "__main__":
    main()
