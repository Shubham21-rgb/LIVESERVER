from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import json
import os
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse

app = FastAPI()

# Enable CORS for all origins, methods, headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all domains
    allow_methods=["*"],       # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],       # Allow all headers
    expose_headers=["*"]
)


load_dotenv()  # Load environment variables from .env file

#--------------------------------------------------------------------
SYSTEM_PROMPT = """
You are an autonomous software engineer named CodeForge.

You receive a JSON 'task' describing a project assignment.
Your responsibilities:

1. Understand the 'brief' and 'checks' fields.
2. Design and generate a complete working project (HTML/CSS/JS or Python + FastAPI/Vue.js).
3. Include a professional README.md explaining setup, usage, and features.
4. Include an MIT License file.
5. Return your output as **valid JSON** in this structure:

{
  "repo_name": "string",
  "description": "string",
  "files": [
    {"path": "index.html", "content": "..."},
    {"path": "README.md", "content": "..."},
    {"path": "LICENSE", "content": "MIT License text"}
  ]
}

Rules:
- Respect all requirements listed in 'checks'.
- Do not include any secrets or credentials.
- Output only the JSON, nothing else.
"""






#--------------------------------------------------------------------



from openai import OpenAI
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)



@app.get("/")
async def root():
    with open("index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/verify",response_class=HTMLResponse)
async def verify_page():
    return """
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Enter OTP</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      color: #fff;
    }

    .otp-container {
      background: rgba(255, 255, 255, 0.05);
      padding: 40px 50px;
      border-radius: 20px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.7);
      text-align: center;
      max-width: 400px;
      width: 100%;
    }

    h1 {
      margin-bottom: 20px;
      color: #ff7f50;
      text-shadow: 1px 1px 5px rgba(0,0,0,0.5);
    }

    .otp-inputs {
      display: flex;
      justify-content: space-between;
      margin-bottom: 30px;
    }

    .otp-inputs input {
      width: 50px;
      height: 60px;
      font-size: 2rem;
      text-align: center;
      border-radius: 10px;
      border: none;
      outline: none;
      background: rgba(255,255,255,0.1);
      color: #fff;
      transition: background 0.3s;
    }

    .otp-inputs input:focus {
      background: rgba(255,255,255,0.2);
    }

    button {
      width: 100%;
      padding: 15px 0;
      font-size: 1.2rem;
      font-weight: bold;
      background: linear-gradient(135deg, #ff416c, #ff4b2b);
      border: none;
      border-radius: 50px;
      cursor: pointer;
      box-shadow: 0 5px 20px rgba(255,75,43,0.5);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      color: #fff;
    }

    button:hover {
      transform: translateY(-3px);
      box-shadow: 0 10px 30px rgba(255,75,43,0.6);
    }

    .message {
      margin-top: 20px;
      font-size: 1rem;
      color: #ffd700;
    }
  </style>
</head>
<body>
  <div class="otp-container">
    <h1>Enter OTP</h1>
    <div class="otp-inputs">
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
    </div>
    <button id="verifyBtn">Verify OTP</button>
    <div class="message" id="message">Enter the 6-digit OTP sent to your email.</div>
  </div>

  <script>
    const inputs = document.querySelectorAll('.otp-inputs input');
    const message = document.getElementById('message');

    // Auto-focus and backspace
    inputs.forEach((input, i) => {
      input.addEventListener('input', () => {
        if (input.value.length > 0 && i < inputs.length - 1) {
          inputs[i + 1].focus();
        }
      });

      input.addEventListener('keydown', (e) => {
        if (e.key === "Backspace" && input.value === "" && i > 0) {
          inputs[i - 1].focus();
        }
      });
    });

    // Verify OTP via API
    document.getElementById('verifyBtn').addEventListener('click', async () => {
      const otp = Array.from(inputs).map(input => input.value).join('');
      if (otp.length !== 6) {
        message.textContent = "Please enter all 6 digits!";
        message.style.color = "#ff4b2b";
        return;
      }

      try {
        const response = await fetch("/verification", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ otp })
        });

        const result = await response.json();
        message.textContent = result.message;
        message.style.color = result.success ? "#00ff00" : "#ff4b2b";

        if(result.success) {
          // Redirect to task input page after 1 second
          setTimeout(() => {
            window.location.href = "/task_input";
          }, 1000);
        }

      } catch (err) {
        message.textContent = "Error connecting to server!";
        message.style.color = "#ff4b2b";
      }
    });
  </script>
</body>
</html>
    """

FIXED_OTP = "003200" 
@app.post("/verification")
async def verification(request: Request):
    data = await request.json()
    user_otp = data.get("otp", "")
    
    if user_otp == FIXED_OTP:
        return JSONResponse({"success": True, "message": "OTP Verified Successfully!"})
    else:
        return JSONResponse({"success": False, "message": "Invalid OTP, try again."})


@app.get("/task_input", response_class=HTMLResponse)
async def task_input_page():
    return """
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Enter OTP</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      color: #fff;
    }

    .otp-container {
      background: rgba(255, 255, 255, 0.05);
      padding: 40px 50px;
      border-radius: 20px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.7);
      text-align: center;
      max-width: 400px;
      width: 100%;
    }

    h1 {
      margin-bottom: 20px;
      color: #ff7f50;
      text-shadow: 1px 1px 5px rgba(0,0,0,0.5);
    }

    .otp-inputs {
      display: flex;
      justify-content: space-between;
      margin-bottom: 30px;
    }

    .otp-inputs input {
      width: 50px;
      height: 60px;
      font-size: 2rem;
      text-align: center;
      border-radius: 10px;
      border: none;
      outline: none;
      background: rgba(255,255,255,0.1);
      color: #fff;
      transition: background 0.3s;
    }

    .otp-inputs input:focus {
      background: rgba(255,255,255,0.2);
    }

    button {
      width: 100%;
      padding: 15px 0;
      font-size: 1.2rem;
      font-weight: bold;
      background: linear-gradient(135deg, #ff416c, #ff4b2b);
      border: none;
      border-radius: 50px;
      cursor: pointer;
      box-shadow: 0 5px 20px rgba(255,75,43,0.5);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      color: #fff;
    }

    button:hover {
      transform: translateY(-3px);
      box-shadow: 0 10px 30px rgba(255,75,43,0.6);
    }

    .message {
      margin-top: 20px;
      font-size: 1rem;
      color: #ffd700;
    }
  </style>
</head>
<body>
  <div class="otp-container">
    <h1>Enter OTP</h1>
    <div class="otp-inputs">
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
      <input type="text" maxlength="1" />
    </div>
    <button id="verifyBtn">Verify OTP</button>
    <div class="message" id="message">Enter the 6-digit OTP sent to your email.</div>
  </div>

  <script>
    const inputs = document.querySelectorAll('.otp-inputs input');
    const message = document.getElementById('message');

    // Auto-focus and backspace
    inputs.forEach((input, i) => {
      input.addEventListener('input', () => {
        if (input.value.length > 0 && i < inputs.length - 1) {
          inputs[i + 1].focus();
        }
      });

      input.addEventListener('keydown', (e) => {
        if (e.key === "Backspace" && input.value === "" && i > 0) {
          inputs[i - 1].focus();
        }
      });
    });

    // Verify OTP via API
    document.getElementById('verifyBtn').addEventListener('click', async () => {
      const otp = Array.from(inputs).map(input => input.value).join('');
      if (otp.length !== 6) {
        message.textContent = "Please enter all 6 digits!";
        message.style.color = "#ff4b2b";
        return;
      }

      try {
        const response = await fetch("/verification", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ otp })
        });

        const result = await response.json();
        message.textContent = result.message;
        message.style.color = result.success ? "#00ff00" : "#ff4b2b";

        if(result.success) {
          // Redirect to task input page after 1 second
          setTimeout(() => {
            window.location.href = "/task_input";
          }, 1000);
        }

      } catch (err) {
        message.textContent = "Error connecting to server!";
        message.style.color = "#ff4b2b";
      }
    });
  </script>
</body>
</html>

    """


# OPTIONS preflight handler for /api/index
@app.options("/api/index")
async def preflight(request: Request):
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
        content=""
    )


# POST endpoint for /api/index
@app.post("/liveserver/endpoint")
async def compute_metrics(request: Request):
    body = await request.json()

    response = {}
    print(body)
    '''response = client.chat.completions.create(
    model="gpt-4o-mini",   # or gpt-4o, gpt-4.1, gpt-3.5-turbo etc.
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": body["task"]}
    ],
    temperature=0.4
    )

    print(response.choices[0].message.content)
    raw_output = response.choices[0].message.content
    try:
        project = json.loads(raw_output)
    except json.JSONDecodeError as e:
        return JSONResponse(
            content={"error": f"Invalid JSON output from model: {e}", "raw_output": raw_output},
            status_code=500
        )
    token = os.getenv("GITHUB_TOKEN")
    g = Github(token)
    username="Shubham21-rgb"
    repo_name="APPGPT"
    repo = g.get_user(username).get_repo(repo_name)
    pages_url = f"https://{username}.github.io/{repo_name}/"
    print(pages_url)
    commit_sha=push_to_repo("https://github.com/Shubham21-rgb/APPGPT", project["files"])'''
    

    return JSONResponse(
        content={"email": '''body['email']''',
                "task": '''body["task"]''',
                "round": '''body["round"]''',
                "nonce": '''body["nonce"]''',
                "repo_url": "https://github.com/Shubham21-rgb/APPGPT",
                "commit_sha": '''commit_sha''',
                "pages_url": '''pages_url'''},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


from github import Github
def push_to_repo(repo_url, files, commit_message="Auto commit from LLM"):
    token = os.getenv("GITHUB_TOKEN")
    g = Github(token)

    # Extract username/repo name from URL
    username, repo_name = repo_url.split("github.com/")[1].split("/")
    repo_name = repo_name.replace(".git", "")
    repo = g.get_user(username).get_repo(repo_name)

    last_commit = None

    for f in files:
        try:
            repo_file = repo.get_contents(f["path"])
            commit = repo.update_file(
                repo_file.path,
                commit_message,
                f["content"],
                repo_file.sha
            )
        except Exception:
            commit = repo.create_file(f["path"], commit_message, f["content"])
        
        last_commit = commit["commit"].sha  # save the latest commit SHA

    return last_commit



'''
{
  // Student email ID
  "email": "student@example.com",
  // A unique task ID.
  "task": "captcha-solver-...",
  // There will be multiple rounds per task. This is the round index
  "round": 1,
  // Pass this nonce back to the evaluation URL below
  "nonce": "ab12-...",
  // brief: mentions what the app needs to do
  "brief": "Create a captcha solver that handles ?url=https://.../image.png. Default to attached sample.",
  // checks: mention how it will be evaluated
  "checks": [
    "Repo has MIT license"
    "README.md is professional",
    "Page displays captcha URL passed at ?url=...",
    "Page displays solved captcha text within 15 seconds",
  ],
  // Send repo & commit details to the URL below
  "evaluation_url": "https://example.com/notify",
  // Attachments will be encoded as data URIs
  "attachments": [{ "name": "sample.png", "url": "data:image/png;base64,iVBORw..." }],
  // Signature to ensure this is an official request
  "signature": "..."
}

'''



#Respone
'''
{
  // Copy these from the request
  "email": "...",
  "task": "captcha-solver-...",
  "round": 1,
  "nonce": "ab12-...",
  // Send these based on your GitHub repo and commit
  "repo_url": "https://github.com/user/repo",
  "commit_sha": "abc123",
  "pages_url": "https://user.github.io/repo/"
}

'''
