# AynuKids TikTok Backend Pipeline

This repository contains the automated pipeline for collecting TikTok videos from the `@aynukids` channel and discovering fan videos that reuse AynuKids original sounds. 

It runs on a free **GitHub Actions** cron job and stores data in a free **Supabase** (PostgreSQL) database.

---

## 🚀 Setup Guide

### 1. Supabase Database Setup

Supabase is an open-source Firebase alternative that gives us a powerful PostgreSQL database and a ready-to-use REST API for your Flutter app.

#### Step 1.1: Create Project
1. Go to [database.new](https://database.new/) or [supabase.com](https://supabase.com) and sign in.
2. Click **New Project**.
3. Choose your organization, give it a name (e.g., `aynukids-backend`), and generate a strong database password (save this securely).
4. Choose a region closest to your users.
5. Click **Create new project**. Wait ~1 minute for it to provision.

#### Step 1.2: Run Database Migrations
1. In the left sidebar of your Supabase dashboard, click on **SQL Editor** (the `</>` icon).
2. Click **New query**.
3. Copy the contents of `database/schema.sql` from this repo, paste it into the editor, and hit **Run**. This creates your tables.
4. Clear the editor, copy the contents of `database/rls_policies.sql`, paste it, and hit **Run**. This secures your data so nobody can write to it without the admin key.
5. Clear the editor, copy the contents of `database/functions.sql`, paste it, and hit **Run**. This creates the random feed generator.

#### Step 1.3: Get Your API Keys
1. In the left sidebar, go to **Project Settings** (the gear icon) > **API**.
2. Under "Project URL", copy the URL. This goes into your `.env` as `SUPABASE_URL`.
3. Under "Project API keys", copy the **`service_role` (secret)** key. This goes into your `.env` as `SUPABASE_SERVICE_ROLE_KEY`. **NEVER share this key or put it in your Flutter app**.
4. *(For your Flutter App)*: Also copy the **`anon` (public)** key. You will use this in your Flutter app to read the data.

---

### 2. Local Environment Setup

1. Make sure you have Python 3.9+ installed.
2. Rename `.env.example` to `.env`.
3. Fill in the keys you got from Supabase:
```env
SUPABASE_URL="https://YOUR-PROJECT-ID.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="eyJh..."
```
4. Create a virtual environment and install dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
5. Run a test sync locally:
```bash
python main.py
```

---

### 3. GitHub Actions (Automated Cron Job)

GitHub Actions allows you to run code automatically on a schedule for free (you get 2,000 minutes per month on the free tier; this pipeline uses maybe 10-20 minutes a month).

**How it works:**
The code in `.github/workflows/sync.yml` tells GitHub: "Every 6 hours, boot up a tiny Linux server, install Python, and run `main.py`."

**To set it up:**
1. Push this code to a new GitHub repository.
2. Go to your repository on GitHub.
3. Click on the **Settings** tab.
4. In the left sidebar, expand **Secrets and variables**, then click **Actions**.
5. Click **New repository secret**.
6. Create two secrets:
   - Name: `SUPABASE_URL` | Secret: (paste your URL)
   - Name: `SUPABASE_SERVICE_ROLE_KEY` | Secret: (paste your service role key)
7. That's it! GitHub will now run the pipeline automatically.

**To run it manually:**
1. Go to the **Actions** tab in your GitHub repository.
2. Click on **AynuKids Content Sync** in the left menu.
3. Click the **Run workflow** dropdown on the right side and click the green button to trigger it immediately.

---

## 🗄️ How the Flutter App Gets Data

You don't need to build an API. Supabase auto-generates it based on your tables!

In Flutter, using the `supabase_flutter` package:

**Initialize:**
```dart
await Supabase.initialize(
  url: 'YOUR_SUPABASE_URL',
  anonKey: 'YOUR_SUPABASE_ANON_KEY', // The public key, NOT the service role key!
);
```

**Get the latest official videos:**
```dart
final data = await Supabase.instance.client
  .from('videos')
  .select()
  .eq('is_active', true)
  .order('created_at', ascending: false);
```

**Get a random mix of official + approved fan videos:**
```dart
final data = await Supabase.instance.client
  .rpc('get_random_feed', params: {'limit_count': 10});
```
