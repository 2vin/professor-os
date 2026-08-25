# Professor OS v18.1 — Free Cloud Deployment

This build is designed for a free hybrid deployment:

- **Render Free Web Service** serves the real Python Professor OS UI.
- **GitHub** is the durable source/content store.
- **GitHub Actions** runs the actual nightly generation job at 21:00 IST and commits generated previews/progress back to the repository.

## Why split the system?

Free web services can sleep and have ephemeral local files. Therefore the Render process intentionally does **not** run the nightly scheduler and does **not** auto-generate on startup. The nightly GitHub Actions workflow is the durable automation layer.

## Security

The public Render deployment sets `ENABLE_MANUAL_RUN=false`, so anonymous visitors cannot trigger paid AI generation by POSTing to `/api/run`. API keys belong in GitHub Actions Secrets, not in the public web service.

## Render

Create a Render Web Service from this GitHub repository (Docker runtime, Free plan). Render can use `render.yaml`. The app listens on Render's injected `PORT`.

## GitHub repository settings

Create these **Actions Secrets** as needed:

- `OPENAI_API_KEY` (required for lesson generation)
- `GEMINI_API_KEY` (required if Gemini visuals are enabled)
- `LINKEDIN_ACCESS_TOKEN` (optional)
- `LINKEDIN_AUTHOR_URN` (optional)
- `GOOGLE_CSE_API_KEY` / `GOOGLE_CSE_ID` (optional external-media discovery)
- `YOUTUBE_API_KEY` (optional)

Create this **Actions Variable** after Render gives you the public URL:

- `PROFESSOR_OS_PUBLIC_URL=https://YOUR-SERVICE.onrender.com`

Optional variables:

- `OPENAI_MODEL=gpt-5`
- `GEMINI_IMAGE_MODEL=gemini-3.1-flash-lite-image`
- `USE_GEMINI_IMAGES=true`

## First run

1. Deploy Render.
2. Set `PROFESSOR_OS_PUBLIC_URL` in GitHub Actions Variables.
3. Open GitHub -> Actions -> **Professor OS Nightly Lecture** -> **Run workflow** to generate Class 1 immediately.
4. Once the workflow commits the generated lesson state, Render auto-deploys the updated repository.
5. Future classes are triggered by the nightly schedule.

## WordPress

Embed the Render URL on the existing WordPress Professor OS page using an iframe or a tiny shortcode plugin. WordPress remains the parent site; Professor OS runs at full Python capability on Render/GitHub.

## Important cost note

The hosting/automation layer can be free. OpenAI/Gemini/API usage is separate and may incur provider charges.
