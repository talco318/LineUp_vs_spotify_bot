# 🚀 מדריך העלאת האתר ל-tomorrowland.talcohen.co.il

## אפשרות 1: Render.com (מומלץ - חינם!)

### שלב 1: העלאה ל-GitHub
```bash
cd C:\Users\talco\PycharmProjects\LineUp_vs_spotify_bot
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### שלב 2: יצירת חשבון ב-Render
1. היכנס ל-https://render.com
2. הירשם עם GitHub

### שלב 3: יצירת Web Service חדש
1. לחץ על **New** → **Web Service**
2. חבר את ה-GitHub repository
3. הגדרות:
   - **Name**: `tomorrowland-lineup`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.flask_app:app --bind 0.0.0.0:$PORT`

### שלב 4: הגדרת Environment Variables ב-Render
הוסף את המשתנים הבאים ב-Dashboard:
- `SPOTIFY_CLIENT_ID_API` - ה-Client ID שלך מ-Spotify
- `SPOTIFY_CLIENT_SECRET_API` - ה-Client Secret שלך
- `SPOTIFY_REDIRECT_URI` - `https://tomorrowland.talcohen.co.il/spotify/callback`
- `GOOGLE_API_KEY` - ה-API Key של Gemini

### שלב 5: הגדרת Custom Domain ב-Render
1. לאחר ה-deploy, לך ל-**Settings** → **Custom Domains**
2. הוסף: `tomorrowland.talcohen.co.il`
3. Render יציג לך את הכתובת שצריך להפנות אליה (משהו כמו `xxx.onrender.com`)

### שלב 6: הגדרת DNS אצל ספק הדומיין
1. היכנס לפאנל הניהול של הדומיין שלך (אולי ב-Cloudflare, GoDaddy, או אחר)
2. הוסף רשומת **CNAME** חדשה:
   - **Name/Host**: `tomorrowland`
   - **Type**: `CNAME`
   - **Value/Points to**: `xxx.onrender.com` (הכתובת שקיבלת מ-Render)
   - **TTL**: 3600 (או Auto)

### שלב 7: עדכון Spotify Redirect URI
1. היכנס ל-https://developer.spotify.com/dashboard
2. בחר את האפליקציה שלך
3. Settings → Redirect URIs
4. הוסף: `https://tomorrowland.talcohen.co.il/spotify/callback`
5. שמור

---

## אפשרות 2: Railway.app (גם חינם עד גבול מסוים)

1. היכנס ל-https://railway.app
2. חבר GitHub
3. New Project → Deploy from GitHub
4. הגדר Environment Variables
5. Settings → Domains → Add Custom Domain

---

## אפשרות 3: VPS (שרת וירטואלי)

אם יש לך שרת VPS (כמו DigitalOcean, Linode, או AWS):

### שלב 1: העתקת הקוד לשרת
```bash
ssh user@your-server-ip
git clone https://github.com/YOUR_USERNAME/LineUp_vs_spotify_bot.git
cd LineUp_vs_spotify_bot
```

### שלב 2: התקנת Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### שלב 3: הרצה עם Gunicorn
```bash
gunicorn app.flask_app:app --bind 0.0.0.0:8000 --daemon
```

### שלב 4: הגדרת Nginx
```nginx
server {
    listen 80;
    server_name tomorrowland.talcohen.co.il;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### שלב 5: HTTPS עם Let's Encrypt
```bash
sudo certbot --nginx -d tomorrowland.talcohen.co.il
```

---

## 📝 הגדרת DNS - סיכום

בין אם אתה משתמש ב-Render, Railway, או VPS, צריך להוסיף רשומת DNS:

| Type | Name | Value |
|------|------|-------|
| CNAME | tomorrowland | הכתובת של השרת (למשל: xxx.onrender.com) |

**או** אם יש לך IP קבוע:

| Type | Name | Value |
|------|------|-------|
| A | tomorrowland | 123.456.789.0 (ה-IP של השרת) |

---

## ❓ איפה הדומיין שלך מנוהל?

- **Cloudflare** - הכי קל, יש ממשק נוח
- **GoDaddy** - DNS Management
- **NameCheap** - Advanced DNS
- **חברת האחסון** - בדרך כלל יש פאנל DNS

ספר לי איפה הדומיין מנוהל ואעזור לך עם השלבים הספציפיים!
