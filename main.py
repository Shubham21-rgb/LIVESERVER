from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import json
import os

app = FastAPI()

# Enable CORS for all origins, methods, headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all domains
    allow_methods=["*"],       # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],       # Allow all headers
    expose_headers=["*"]
)


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

    return JSONResponse(
        content={"email": body['email'],
                "task": body["task"],
                 "round": body["round"],
                "nonce": body["nonce"],
                "repo_url": "https://github.com/user/repo",
                "commit_sha": "abc123",
                "pages_url": "https://user.github.io/repo/"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

from openai import OpenAI
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)
client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-4o-mini",   # or gpt-4o, gpt-4.1, gpt-3.5-turbo etc.
    messages=[
        {"role": "system", "content": "You are a helpful assistant."}
    ]
)

print(response.choices[0].message.content)

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
