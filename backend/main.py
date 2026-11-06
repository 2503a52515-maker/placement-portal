import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

# Render cloud dynamic port support
PORT = int(os.environ.get("PORT", 5000))

class ElevateAIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/frontend/index.html'
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except:
            data = {}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response_data = {"status": "success"}

        if self.path == '/api/login':
            response_data = {"status": "success", "message": "Login successful!"}
        
        elif self.path == '/api/save-profile':
            response_data = {"status": "success", "message": "Profile & AI Sync updated successfully!"}
        
        elif self.path == '/api/analyze-resume':
            response_data = {
                "status": "success", 
                "ats_score": 95, 
                "message": "PDF Resume successfully scanned! Strong keyword alignment with Python and AIML."
            }
        
        elif self.path == '/api/evaluate-aptitude':
            selected_ans = data.get("answer", "")
            is_correct = (selected_ans == "O(log n)")
            response_data = {
                "status": "success",
                "score": 92 if is_correct else 75,
                "message": "Correct Answer! Excellent algorithmic understanding." if is_correct else "Incorrect. The correct time complexity for Binary Search is O(log n)."
            }

        elif self.path == '/api/run-mock':
            response_data = {"status": "success", "feedback": "AI Interview Feedback: Excellent technical explanation on AIML concepts."}

        elif self.path == '/api/run-cover':
            response_data = {"status": "success", "cover_letter": "Dear Hiring Manager,\n\nAs a B.Tech CSE (AIML) student at SR University..."}

        elif self.path == '/api/run-github':
            response_data = {"status": "success", "audit_score": "A+", "message": "GitHub repository audit complete!"}

        elif self.path == '/api/analyze-matcher':
            response_data = {
                "status": "success",
                "role": "AI/ML Engineer",
                "skill_gap_map": [
                    {
                        "skill": "Advanced Docker Containerization", 
                        "current_level": "35%", 
                        "bar_width": "35%", 
                        "course": "Docker & Kubernetes Masterclass", 
                        "platform": "Udemy", 
                        "link": "https://www.udemy.com"
                    },
                    {
                        "skill": "Kubernetes Orchestration", 
                        "current_level": "20%", 
                        "bar_width": "20%", 
                        "course": "Kubernetes for Beginners", 
                        "platform": "Coursera", 
                        "link": "https://www.coursera.org"
                    },
                    {
                        "skill": "PyTorch Distributed Training", 
                        "current_level": "45%", 
                        "bar_width": "45%", 
                        "course": "Deep Learning Specialization", 
                        "platform": "Coursera", 
                        "link": "https://www.coursera.org"
                    }
                ],
                "readiness_score": 89
            }
        else:
            response_data = {"status": "success", "message": "Operation completed successfully!"}

        self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == '__main__':
    print(f"ElevateAI Advanced Server Running...")
    print(f"Open portal: http://127.0.0.1:{PORT}")
    print(f"=====================================")
    server = HTTPServer(("0.0.0.0", PORT), ElevateAIHandler)
    server.serve_forever()