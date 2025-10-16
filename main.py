from fastapi import FastAPI, Request ,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import json
import os
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
import requests
app = FastAPI()
load_dotenv()  # Load environment variables from .env file

api_key=os.getenv("AI_PIPE_TOKEN")
'''
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "openai/gpt-4o",
    "messages": [{"role": "user", "content": "What is 2 + 2?"}]
}

response = requests.post(
    "https://aipipe.org/openrouter/v1/chat/completions",
    headers=headers,
    json={
        "model": "openai/gpt-4o",
        "messages": [{"role": "user", "content": "Hello"}]
    }
)
print("AI_PIPE",response.json())'''
# Enable CORS for all origins, methods, headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all domains
    allow_methods=["*"],       # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],       # Allow all headers
    expose_headers=["*"]
)




#--------------------------------------------------------------------
SYSTEM_PROMPT = """
You are an autonomous software engineer named CodeForge.

You receive a JSON 'task' describing a project assignment.
Your responsibilities:

1. Understand the 'brief' and 'checks' fields.
2. Design and generate a complete working project (HTML/CSS/JS or Python + FastAPI/Vue.js).
3. Include a professional README.md explaining setup, usage, and features.
4. Include an MIT License file.


5.Checks to apply:
{checks_text}

6. Return your output as **valid JSON** in this structure:
{{
  "repo_name": "string",
  "description": "string",
  "files": [
    {{"path": "index.html", "content": "..."}},
    {{"path": "README.md", "content": "..."}},
    {{"path": "LICENSE", "content": "MIT License text"}}
  ]
}}

Rules(IMPORTANT):
- Mandatory needs to do all things in checks if possible (main).
- Do not include any secrets or credentials.
- Output only valid JSON. No explanations, no code fences, no extra text.
"""

SYSTEM_PROMPT_ROUND2 = """
You are CodeForge, an autonomous software engineer continuing an existing project you created earlier.

You receive a new task brief describing improvements or changes to the existing codebase.

Instructions:
1. Read and interpret the new brief carefully.
2. Modify or extend the previous project accordingly.
3. Maintain the same folder structure and general code style.
4. Only output the updated or new files.
5. Return only valid JSON. Do NOT wrap it in ```json or ``` code fences.
{{
  "repo_name": "string",
  "description": "string",
  "files": [
    {{"path": "index.html", "content": "..."}},
    {{"path": "README.md", "content": "..."}},
    {{"path": "LICENSE", "content": "MIT License text"}}
  ]
}}

Rules:
- Only include changed or new files.
- Preserve all other files from the previous round as-is.
- Output only valid JSON. No explanations, no code fences, no extra text.

"""
class AIPipeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://aipipe.org/openrouter/v1"

    class Chat:
        def __init__(self, parent):
            self.parent = parent

        def completions(self, model, messages, temperature=0.7):
            url = f"{self.parent.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.parent.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            resp = requests.post(url, headers=headers, json=payload)
            resp_json = resp.json()
            return resp_json

    @property
    def chat(self):
        return self.Chat(self)




#--------------------------------------------------------------------



#from openai import OpenAI
#api_key = os.getenv("OPENAI_API_KEY")
client = AIPipeClient(api_key)



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

FIXED_OTP = os.getenv("OTP_TOKEN")

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
  <title>AI Task Input</title>
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
    .task-container {
      background: rgba(255, 255, 255, 0.05);
      padding: 40px 50px;
      border-radius: 20px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.7);
      max-width: 500px;
      width: 100%;
    }
    h1 {
      text-align: center;
      margin-bottom: 20px;
      color: #ff7f50;
    }
    input, textarea {
      width: 100%;
      padding: 10px;
      margin: 10px 0;
      border-radius: 10px;
      border: none;
      outline: none;
      font-size: 1rem;
    }
    button {
      width: 100%;
      padding: 15px;
      font-size: 1.1rem;
      border-radius: 50px;
      border: none;
      background: linear-gradient(135deg, #ff416c, #ff4b2b);
      cursor: pointer;
      color: #fff;
      font-weight: bold;
      margin-top: 10px;
    }
    button:hover {
      transform: translateY(-3px);
      box-shadow: 0 10px 30px rgba(255,75,43,0.6);
    }
    pre {
      background: rgba(0,0,0,0.2);
      padding: 10px;
      border-radius: 10px;
      overflow-x: auto;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="task-container">
    <h1>AI Task Input</h1>
    <form id="taskForm">
      <label>Email:</label>
      <input type="email" id="email" required>

      <label>Task :</label>
      <input type="text" id="task" required>

      <label>Round:</label>
      <input type="number" id="round" value="1" required>

      <label>Nonce:</label>
      <input type="text" id="nonce" required>

      <label>Brief:</label>
      <textarea id="brief" required></textarea>

      <label>Signature:</label>
      <textarea id="signature" required></textarea>

      <button type="submit">Submit Task</button>
    </form>

    <h3>API Response:</h3>
    <pre id="apiResponse">No response yet</pre>
  </div>

  <script>
    const form = document.getElementById('taskForm');
    const apiResp = document.getElementById('apiResponse');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = {
        email: document.getElementById('email').value,
        task: document.getElementById('task').value,
        round: parseInt(document.getElementById('round').value),
        nonce: document.getElementById('nonce').value,
        brief: document.getElementById('brief').value,
        signature: document.getElementById('signature').value
      };
      apiResp.textContent = "Sending request...";

      try {
        const response = await fetch("/liveserver/endpoint", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data)
        });

        if(!response.ok) throw new Error(`HTTP ${response.status}`);
        const result = await response.json();
        apiResp.textContent = result.pages_url || "No page URL found";
      } catch(err) {
        apiResp.textContent = `Error: ${err}`;
      }
    });
  </script>
</body>
</html>
"""

def build_prompt(task: dict) -> str:
  checks_list = task.get("checks", [])
  checks_text = "\n".join(f"- {c}" for c in checks_list) if checks_list else "No checks provided."
  prompt = SYSTEM_PROMPT.format(checks_text=checks_text)
  return prompt



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


################################# Background Task to handle the request asynchronously ##############################
async def round_1_task(body,secret_key,ROUND1_STATE={}):
  if body['round']==1 and body['secret']==secret_key:
    user_brief = body.get("brief", "")

        # Check attachments
    attachments = body.get("attachments", [])
    remote_url=body.get("evaluation_url","")
    if attachments:
      attachments_text = ""
      for idx, att in enumerate(attachments, 1):
        attachments_text += f"{idx}. Name: {att['name']}\n"
        attachments_text += f"   Data (base64): {att['url']}\n\n"

            # Prompt tells model to use attachments
      user_message = f"""
          {user_brief}
          Escape all backslashes as \\ and do not include any single unescaped backslash.
            You are given the following attachments. Use them to assist in your response.
            Attachments: (decode base64)
            {attachments_text}
            Checks to apply:Only include this section if there are actual checks.
            {body.get("checks", [])}
          Instructions:
          - Analyze or extract information from the attachments if relevant.
          - Combine your findings with the main brief.
          - If an attachment is irrelevant, you can ignore it but mention that you considered it.
          - have a look at the checks and do the needful
          - Review the checks carefully and apply them to your analysis.
          """
    else:
      user_message = user_brief  # no attachments
    print("Inside background Task ######",user_message)
    def run_chat():
      try:
        resp = client.chat.completions(
          model="openai/gpt-4o",
          messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.4
        )
        print("LLM response raw:", resp)
        return resp
      except Exception as e:
        print("LLM call failed as too large to handle:", e)
        raise

    response = await asyncio.to_thread(run_chat)
    raw_output = response['choices'][0]['message']['content']
    cleaned_output = re.sub(r'^```json\s*|\s*```$', '', raw_output.strip(), flags=re.MULTILINE)
    try:
      project = json.loads(cleaned_output)
    except json.JSONDecodeError as e:
      return JSONResponse(
                content={"error": f"Invalid JSON output from model: {e}", "raw_output": cleaned_output},
                status_code=500
      )
    token = os.getenv("GITHUB_TOKEN")
    g = Github(token)
    username="Shubham21-rgb"
    repo_name=body["task"].replace(" ","-")
    user = g.get_user()
    try:
      repo = user.get_repo(repo_name)
      print(f"Repository '{repo_name}' already exists. Using existing repo.")
    except:
      repo = user.create_repo(
      name=repo_name,
      description="Repository created via LLM with Pages enabled",
      private=False,
      auto_init=True
      )
    print(f"Repository '{repo_name}' created successfully!")
    pages_url = f"https://api.github.com/repos/{username}/{repo_name}/pages"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    pages_data = {
        "source": {
          "branch": "main",  # or "master" if your repo default branch is master
          "path": "/"        # serve from root
          }
    }
    response = requests.post(pages_url, headers=headers, json=pages_data)

    if response.status_code in [201, 202]:
      print("GitHub Pages enabled successfully!")
      print("Your site URL:", response.json().get("html_url"))
    else:
      print("Error enabling Pages:", response.json())
    commit_sha,pages_url,folder=push_to_repo(repo.clone_url, project["files"])
    ROUND1_STATE[body["task"]] = {"folder": folder, "project": project}
    ROUND1_STATE['repo']=repo.clone_url
    print(pages_url)
    content={"email": body['email'],
                "task": body["task"],
                "round": body["round"],
                "nonce": body["nonce"],
                "repo_url": repo.clone_url,
                "commit_sha": commit_sha,
                "pages_url": pages_url},
    requests.post(remote_url, json=content, headers={
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "*",
          "Content-Type": "application/json"
        })
    with open("/tmp/ROUND1_STATE.json", "w") as f:
      json.dump(ROUND1_STATE, f, indent=4)



async def round_2_task(body,secret_key):
  if body['round']==2 and body['secret']==secret_key:
    remote_url=body.get("evaluation_url","")
    user_brief = body.get("brief", "")

        # Check attachments
    attachments = body.get("attachments", [])

    with open("/tmp/ROUND1_STATE.json") as f:
      ROUND1_STATE = json.load(f)
    state = ROUND1_STATE.get(body["task"])
    if not state:
      return JSONResponse(content={"error": "WIHOUT ROUND 1 YOU CANNOT GIVE ROUND 2"}, status_code=400)
    folder = state["folder"]
    project = state["project"]

        # Compact the project context (optional: only include key files)
    summary = "\n".join([f"- {f['path']}" for f in project['files']])
    context_code = "\n\n".join([
            f"File: {f['path']}\n{f['content']}"  # first 600 chars per file for context
            for f in project['files']
            if f['path'].endswith((".html", ".js", ".py", ".vue", ".md"))
    ])
    if attachments:
      attachments_text = ""
      for idx, att in enumerate(attachments, 1):
        attachments_text += f"{idx}. Name: {att['name']}\n"
        attachments_text += f"   Data (base64): {att['url']}\n\n"

            # Prompt tells model to use attachments
      user_message = f"""

  Escape all backslashes (use \\ for each \).
  Do not include raw backslashes.

  You are working on Round 2: only update or modify the project as needed. Do not rewrite the entire project. Focus on making changes relevant to the brief.

  Project Summary:
  {summary}

  Project Context (key parts of files):
  {context_code}

  Attachments:(decode base64)
  {attachments_text if attachments else 'No attachments provided'}

  Please note the following checks to apply:Only include this section if there are actual checks.
  {body.get("checks", [])}
  Please ensure you adhere to these checks while making modifications.
  No other files should be changed.

  Instructions:
  - Use the attachments if relevant to the update.
  - attachement is given in base64 decode it and use it if url is given then fetch the data from url
  - Only modify files necessary for the task described.
  - Keep the rest of the code unchanged.
  - If an attachment or part of the project is irrelevant, mention that you considered it.
  - Your response should clearly indicate which files are being updated and what changes are being made.
  - Also upadate the README.md to reflect any new features or changes.
  -keeping all above conditons in mind please do the following task:
    {user_brief}
          """
    else:
      user_message = user_brief  # no attachments
    print("Inside background task rnd 2",user_message)










    SYSTEM_PROMPT = SYSTEM_PROMPT_ROUND2
    def run_chat():
      try:
        resp = client.chat.completions(
          model="openai/gpt-4o",
          messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
          ],
          temperature=0.4
        )
        print("LLM response raw:", resp)
        return resp
      except Exception as e:
        print("LLM call failed as too large to handle:", e)
        raise

    response = await asyncio.to_thread(run_chat)
    raw_output = response['choices'][0]['message']['content']
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
    repo=ROUND1_STATE.get('repo')
    commit_sha,pages_url,folder=push_to_repo(repo, project["files"],folder=folder)
    print(pages_url)
    content={"email": body['email'],
                "task": body["task"],
                "round": body["round"],
                "nonce": body["nonce"],
                "repo_url": repo,
                "commit_sha": commit_sha,
                "pages_url": pages_url}
    requests.post(remote_url, json=content, headers={
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "*",
          "Content-Type": "application/json"
        }) 




###############################################################################################################


















import asyncio
import requests
# POST endpoint for /api/index
@app.post("/liveserver/endpoint")
async def compute_metrics(request: Request,background_tasks: BackgroundTasks):
    body = await request.json()

    response = {}
    secret_key=os.getenv("SECRET_KEY")
    build_prompt_response=build_prompt(body)
    SYSTEM_PROMPT=build_prompt_response
    print(SYSTEM_PROMPT)
    remote_url=body.get("evaluation_url","")
    ROUND1_STATE = {}  
    if body['secret'] == secret_key:
      background_tasks.add_task(round_1_task,body,secret_key,ROUND1_STATE={})
  
      '''if body['round']==1 and body['secret']==secret_key:

        user_brief = body.get("brief", "")

        # Check attachments
        attachments = body.get("attachments", [])

        if attachments:
          attachments_text = ""
          for idx, att in enumerate(attachments, 1):
            attachments_text += f"{idx}. Name: {att['name']}\n"
            attachments_text += f"   Data (base64): {att['url']}\n\n"

            # Prompt tells model to use attachments
          user_message = f"""
          {user_brief}
          Escape all backslashes (use \\ for each \).
          Do not include raw backslashes.
            You are given the following attachments. Use them to assist in your response.
            Attachments: (decode base64 if needed else if url is given then fetch the data from url)
            {attachments_text}

          Instructions:
          - Analyze or extract information from the attachments if relevant.
          - Combine your findings with the main brief.
          - If an attachment is irrelevant, you can ignore it but mention that you considered it.
          """
        else:
          user_message = user_brief  # no attachments
        print("############3**********",user_message)


        response = client.chat.completions(
        model="openai/gpt-4o",   # or gpt-4o, gpt-4.1, gpt-3.5-turbo etc.
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.4
        )
        raw_output = response['choices'][0]['message']['content']
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
        repo_name=body["task"].replace(" ","-")
        user = g.get_user()
        try:
          repo = user.get_repo(repo_name)
          print(f"Repository '{repo_name}' already exists. Using existing repo.")
        except:
          repo = user.create_repo(
          name=repo_name,
          description="Repository created via LLM with Pages enabled",
          private=False,
          auto_init=True
          )
          print(f"Repository '{repo_name}' created successfully!")
        pages_url = f"https://api.github.com/repos/{username}/{repo_name}/pages"
        headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
        }
        pages_data = {
        "source": {
          "branch": "main",  # or "master" if your repo default branch is master
          "path": "/"        # serve from root
          }
        }
        response = requests.post(pages_url, headers=headers, json=pages_data)

        if response.status_code in [201, 202]:
          print("GitHub Pages enabled successfully!")
          print("Your site URL:", response.json().get("html_url"))
        else:
          print("Error enabling Pages:", response.json())
        commit_sha,pages_url,folder=push_to_repo(repo.clone_url, project["files"])
        ROUND1_STATE[body["task"]] = {"folder": folder, "project": project}
        ROUND1_STATE['repo']=repo.clone_url
        print(pages_url)
        content={"email": body['email'],
                "task": body["task"],
                "round": body["round"],
                "nonce": body["nonce"],
                "repo_url": repo.clone_url,
                "commit_sha": commit_sha,
                "pages_url": pages_url},
        requests.post(remote_url, json=content, headers={
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "*",
          "Content-Type": "application/json"
        }) 

        with open("/tmp/ROUND1_STATE.json", "w") as f:
          json.dump(ROUND1_STATE, f, indent=4)
        return JSONResponse(
          content={"status": "OK"},
          status_code=200
        )'''
#################################################################################################################################################
      if body['round']==2 and body['secret']==secret_key:
        with open("/tmp/ROUND1_STATE.json") as f:
          ROUND1_STATE = json.load(f)
        if not ROUND1_STATE.get(body["task"]):
          return JSONResponse(content={"error": "WIHOUT ROUND 1 YOU CANNOT GIVE ROUND 2"}, status_code=400)
        background_tasks.add_task(round_2_task,body,secret_key)
        return JSONResponse(
        content={"status": "OK"},
        status_code=200
        )

        '''user_brief = body.get("brief", "")

        # Check attachments
        attachments = body.get("attachments", [])





        with open("/tmp/ROUND1_STATE.json") as f:
          ROUND1_STATE = json.load(f)
        state = ROUND1_STATE.get(body["task"])
        if not state:
          return JSONResponse(content={"error": "WIHOUT ROUND 1 YOU CANNOT GIVE ROUND 2"}, status_code=400)
        folder = state["folder"]
        project = state["project"]

        # Compact the project context (optional: only include key files)
        summary = "\n".join([f"- {f['path']}" for f in project['files']])
        context_code = "\n\n".join([
            f"File: {f['path']}\n{f['content']}"  # first 600 chars per file for context
            for f in project['files']
            if f['path'].endswith((".html", ".js", ".py", ".vue", ".md"))
        ])
        if attachments:
          attachments_text = ""
          for idx, att in enumerate(attachments, 1):
            attachments_text += f"{idx}. Name: {att['name']}\n"
            attachments_text += f"   Data (base64): {att['url']}\n\n"

            # Prompt tells model to use attachments
          user_message = f"""

  Escape all backslashes (use \\ for each \).
  Do not include raw backslashes.

  You are working on Round 2: only update or modify the project as needed. Do not rewrite the entire project. Focus on making changes relevant to the brief.

  Project Summary:
  {summary}

  Project Context (key parts of files):
  {context_code}

  Attachments:
  {attachments_text if attachments else 'No attachments provided'}

  Please note the following checks to apply:
  {body.get("checks", [])}
  Please ensure you adhere to these checks while making modifications.
  No other files should be changed.

  Instructions:
  - Use the attachments if relevant to the update.
  - attachement is given in base64 decode it and use it if url is given then fetch the data from url
  - Only modify files necessary for the task described.
  - Keep the rest of the code unchanged.
  - If an attachment or part of the project is irrelevant, mention that you considered it.
  - Your response should clearly indicate which files are being updated and what changes are being made.
  - Also upadate the README.md to reflect any new features or changes.
  -keeping all above conditons in mind please do the following task:
    {user_brief}
          """
        else:
          user_message = user_brief  # no attachments
        print("############3**********",user_message)










        SYSTEM_PROMPT = SYSTEM_PROMPT_ROUND2
        response = client.chat.completions(
        model="openai/gpt-4o",   # or gpt-4o, gpt-4.1, gpt-3.5-turbo etc.
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content":user_message}
        ],
        temperature=0.4
        )
        raw_output = response['choices'][0]['message']['content']
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
        repo=ROUND1_STATE.get('repo')
        commit_sha,pages_url,folder=push_to_repo(repo, project["files"],folder=folder)
        print(pages_url)
        content={"email": body['email'],
                "task": body["task"],
                "round": body["round"],
                "nonce": body["nonce"],
                "repo_url": repo,
                "commit_sha": commit_sha,
                "pages_url": pages_url},
        requests.post(remote_url, json=content, headers={
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "*",
          "Content-Type": "application/json"
        }) 

      else:
        data={"pages_url": "Check the JSON values you have entered"}
        requests.post(remote_url, json=data, headers={
          "Content-Type": "application/json"
        })
        return JSONResponse(
            content={"pages_url": "Unauthoeized To get the values"},
            status_code=403,
            headers={
              "Access-Control-Allow-Origin": "*",
              "Access-Control-Allow-Methods": "POST, OPTIONS",
              "Access-Control-Allow-Headers": "*"
            }
        )'''
      return JSONResponse(
        content={"status": "OK"},
        status_code=200
      )
    else:
        return JSONResponse(
            content={"error": "WRONG SECRET KEY"},
            status_code=401,
            headers={
              "Access-Control-Allow-Origin": "*",
              "Access-Control-Allow-Methods": "POST, OPTIONS",
              "Access-Control-Allow-Headers": "*",
            })


from github import Github
import random
import string
def random_folder_name(length=6):
    """Generate a random folder name with letters+digits"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def push_to_repo(repo_url, files, commit_message="Auto commit from LLM",folder=None):
    """
    Push files to a GitHub repo in random folders, returning latest commit SHA and page URLs.
    """
    token = os.getenv("GITHUB_TOKEN")
    g = Github(token)

    # Extract username/repo from URL
    username, repo_name = repo_url.split("github.com/")[1].split("/")
    repo_name = repo_name.replace(".git", "")
    repo = g.get_user(username).get_repo(repo_name)
    branch = "main"  # branch used for GitHub Pages

    last_commit = None
    if folder is None:
      folder = random_folder_name() 
    page_urls = f"https://{username}.github.io/{repo_name}/{folder}/"

    for f in files:
        file_name = f["path"].split("/")[-1]  # keep original filename
        path = f"{folder}/{file_name}"  # full path including folder

        try:
            repo_file = repo.get_contents(path, ref=branch)
            commit = repo.update_file(
                repo_file.path,
                commit_message,
                f["content"],
                repo_file.sha,
                branch=branch
            )
        except Exception as e:
            # If file doesn't exist, create it
            commit = repo.create_file(path, commit_message, f["content"], branch=branch)

        last_commit = commit["commit"].sha  # update latest commit SHA

    return last_commit, page_urls,folder


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
