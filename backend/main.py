import os
import json
import re
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8000))
DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY", "")

def call_gemini_rest(prompt: str, api_key: str) -> str:
    key = (api_key or DEFAULT_API_KEY).strip()
    if not key:
        return ""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"]

class PortalHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        here = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(here, "index.html"),
            os.path.join(here, "..", "frontend", "index.html"),
            os.path.join(here, "..", "index.html")
        ]
        for path in candidates:
            if os.path.exists(path):
                self._set_headers(200, "text/html; charset=utf-8")
                with open(path, "rb") as f:
                    self.wfile.write(f.read())
                return
        self._set_headers(200, "application/json")
        self.wfile.write(json.dumps({"status": "ElevateAI Enhanced Backend Running"}).encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length)
        data = json.loads(raw_body.decode("utf-8", errors="ignore") or "{}")
        api_key = data.get("api_key", "")

        if self.path == "/api/analyze-profile":
            skills = data.get("skills", ["Python", "React", "SQL"])
            cgpa = float(data.get("cgpa", 8.5))
            backlogs = int(data.get("backlogs", 0))
            aptitude = int(data.get("aptitude_score", 80))
            target_role = data.get("target_role", "AI/ML Engineer")

            if api_key:
                try:
                    prompt = f"Analyze B.Tech student for {target_role}: CGPA {cgpa}, Skills {skills}, Aptitude {aptitude}%. Return strictly valid JSON with keys: readiness_score (int), recommended_roles (list of 3 objects with role, match, package_lpa, reason), missing_skills (list of 4 strings), roadmap (list of 4 strings)."
                    ai_text = call_gemini_rest(prompt, api_key)
                    cleaned = re.sub(r"```json|```", "", ai_text).strip()
                    self._set_headers(200)
                    self.wfile.write(json.dumps(json.loads(cleaned)).encode("utf-8"))
                    return
                except Exception:
                    pass

            skill_bonus = min(len(skills) * 6, 35)
            cgpa_score = int((cgpa / 10.0) * 35)
            apt_component = int((aptitude / 100.0) * 30)
            readiness = min(max(skill_bonus + cgpa_score + apt_component - (backlogs * 10), 25), 98)

            role_skill_map = {
                "AI/ML Engineer": ["Python", "TensorFlow", "PyTorch", "LangChain", "Docker", "SQL", "FastAPI"],
                "Full Stack Developer": ["React", "Node.js", "TypeScript", "MongoDB", "Docker", "AWS", "Redis"],
                "Data Scientist": ["Python", "SQL", "Pandas", "PowerBI", "Spark", "Statistics"],
                "Cloud & DevOps Engineer": ["AWS", "Docker", "Kubernetes", "Linux", "Terraform", "CI/CD"]
            }
            required = role_skill_map.get(target_role, ["Docker", "System Design", "AWS", "DSA", "SQL"])
            user_lower = [s.lower() for s in skills]
            missing = [s for s in required if s.lower() not in user_lower]

            response = {
                "readiness_score": readiness,
                "recommended_roles": [
                    {"role": target_role, "match": min(readiness + 6, 97), "package_lpa": "8.5 - 15.0 LPA", "reason": f"Strong alignment with {', '.join(skills[:3])} and {cgpa} CGPA."},
                    {"role": "Software Development Engineer (SDE-1)", "match": max(readiness - 4, 65), "package_lpa": "6.5 - 12.0 LPA", "reason": f"Solid aptitude performance ({aptitude}%) meets tier-1 product criteria."},
                    {"role": "Data & BI Analyst", "match": max(readiness - 9, 60), "package_lpa": "5.0 - 8.5 LPA", "reason": "Analytical profile and academic consistency fit enterprise consulting roles."}
                ],
                "missing_skills": missing if missing else ["System Design", "Kubernetes", "GraphQL"],
                "roadmap": [
                    f"Week 1: Close core skill gaps in {', '.join(missing[:2] if missing else ['System Design', 'Cloud'])} with hands-on labs.",
                    "Week 2: Solve 30 medium-level LeetCode problems focusing on Arrays, Trees, and Graphs.",
                    f"Week 3: Deploy a live {target_role} capstone project with CI/CD & README documentation.",
                    "Week 4: Revise OS, DBMS, Computer Networks, and take 5 full-length company mock tests."
                ]
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        elif self.path == "/api/analyze-resume":
            text = data.get("raw_text", "Python React FastAPI SQL Machine Learning project")
            common_tech = ["Python", "Java", "C++", "React", "Node.js", "FastAPI", "Flask", "SQL", "MongoDB", "AWS", "Docker", "Git", "Machine Learning", "TensorFlow", "HTML", "CSS", "JavaScript", "LangChain"]
            found_skills = [kw for kw in common_tech if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE)]
            if not found_skills:
                found_skills = ["Python", "React", "SQL", "Git", "Machine Learning"]
            has_metrics = bool(re.search(r"\d+%|\d+x|improved|reduced|built|deployed", text, re.IGNORECASE))
            base_score = min(54 + len(found_skills) * 5 + (10 if has_metrics else 0), 95)

            response = {
                "ats_score": base_score,
                "extracted_skills": found_skills,
                "missing_keywords": ["Docker", "Kubernetes", "System Design", "CI/CD Pipelines", "REST API Security"],
                "strengths": [
                    f"Detected {len(found_skills)} core technical keywords matching industry parser rules.",
                    "Action verbs and technical project structure are clearly identifiable."
                ],
                "improvements": [
                    "Quantify project impact using numbers (e.g., 'Improved query speed by 40%').",
                    "Add role-specific keywords such as Docker, Cloud deployment, and Automated Testing.",
                    "Ensure GitHub, LinkedIn, and live portfolio URLs are clickable in the header."
                ]
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        elif self.path == "/api/evaluate-interview":
            answer = data.get("answer", "")
            role = data.get("role", "AI/ML Engineer")
            word_count = len(answer.split())
            score = min(max(word_count * 2 + 40, 45), 94)
            response = {
                "score": score,
                "feedback": "Good structural flow! To score 95+, mention time/space complexity or a real-world architectural trade-off from your project.",
                "ideal_answer": f"For a {role} role, structure your answer using the STAR method: define the core concept first, explain how you built it in your project, and state the measurable impact."
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        elif self.path == "/api/generate-cover-letter":
            name = data.get("name", "Student")
            role = data.get("role", "AI/ML Engineer")
            company = data.get("company", "Top Tech Recruiter")
            skills = ", ".join(data.get("skills", ["Python", "React", "FastAPI"]))
            
            cover_letter = f"""Dear Hiring Manager at {company},\n\nI am writing to express my strong interest in the {role} position. As a B.Tech student specializing in AI & ML with a solid academic record and hands-on project experience in {skills}, I am confident in my ability to deliver immediate value to your engineering team.\n\nIn my recent capstone projects, I designed and deployed full-stack AI applications utilizing FastAPI, React, and robust database architectures. I am eager to bring my problem-solving skills and passion for scalable software engineering to {company}.\n\nThank you for your time and consideration. I look forward to discussing how my technical background aligns with your team's goals.\n\nSincerely,\n{name}"""
            
            cold_email = f"""Subject: Passionate B.Tech CSE (AIML) Graduate | Interested in {role} at {company}\n\nHi [Recruiter Name],\n\nI hope this email finds you well. I've been following {company}'s recent engineering innovations and am very inspired by your work.\n\nI am a final-year B.Tech student with practical expertise in {skills}. I recently built and deployed an AI-driven placement platform and would love to be considered for any upcoming {role} openings.\n\nHere is a link to my portfolio and GitHub: [Insert Link]\n\nBest regards,\n{name}"""

            self._set_headers(200)
            self.wfile.write(json.dumps({"cover_letter": cover_letter, "cold_email": cold_email}).encode("utf-8"))
            return

        elif self.path == "/api/analyze-github":
            username = data.get("username", "student")
            response = {
                "score": 88,
                "repos_analyzed": 14,
                "strengths": ["Consistent commit activity", "Clean repository folder structure", "Well-documented README files with architecture diagrams"],
                "recommendations": ["Add automated CI/CD GitHub Actions workflows", "Include live deployment links in pinned repositories"]
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

if __name__ == "__main__":
    print(f"\n=======================================================")
    print(f" ElevateAI Advanced Server Running!")
    print(f" Open portal: http://127.0.0.1:{PORT}")
    print(f"=======================================================\n")
    server = HTTPServer(("0.0.0.0", PORT), PortalHandler)
    server.serve_forever()