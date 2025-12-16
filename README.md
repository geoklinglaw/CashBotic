# 💸 CashBotic

**CashBotic** is a Telegram bot that tracks your expenses and logs them directly to Google Sheets — effortlessly and adorably.

---

## Setting up the Project

### 1. Create a Python Virtual Environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Obtain API Credentials
🔹 Telegram Bot Token <br>
Create a Telegram bot using @BotFather and retrieve your bot token.

🔹 Google Spreadsheet ID <br>
Create a new Google Sheet and copy the spreadsheet ID from the URL:
`https://docs.google.com/spreadsheets/d/<your-spreadsheet-id>/edit`

Add your credentials to a .env file like this:

```
TOKEN=<your-telegram-bot-token>
SPREADSHEET_ID=<your-google-spreadsheet-id>
```


### 3. Generate Google Auth Token
Run the following script once to generate a token.pickle file for Google authentication:
```
python generate_token.py
```
This will open a browser window for Google login.

### 4. Convert token pickle to base 64
Run the following script to convert the token.pickle file to a base64 string:
```
base64 -i token.pickle -o token.pickle.b64
```

### 4. Start the bot! 🎉

```
python bot.py
```