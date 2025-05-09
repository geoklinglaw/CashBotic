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

### 4. Start the bot! 🎉

```
python bot.py
```

#### Todos:
1. Fix write to old dates in `/past` command
<br>
2. Feature: check expenditure by time or category
<br>
3. Feature: add recurring expense or income
<br>
4. Feature: connect to DBS API (not sure how possible is this) or some way to automate this process but then again it would render this bot useless :(
<br>
5. Feature: generate piechart or any analytics to track my spending