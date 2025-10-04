from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import json
import os
from dotenv import load_dotenv

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
    return {"message": "Hello World its me Shubham"}

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
    response = client.chat.completions.create(
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
    commit_sha=push_to_repo("https://github.com/Shubham21-rgb/APPGPT", project["files"])
    

    return JSONResponse(
        content={"email": body['email'],
                "task": body["task"],
                "round": body["round"],
                "nonce": body["nonce"],
                "repo_url": "https://github.com/Shubham21-rgb/APPGPT",
                "commit_sha": commit_sha,
                "pages_url": pages_url},
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
