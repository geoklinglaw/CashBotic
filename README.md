# 💸 CashBotic

**CashBotic** is a lightweight Telegram bot for fast expense logging that automatically syncs your data to **Google Sheets**, giving you clear spending insights with minimal effort.

The goal is simple:  
**log quickly, reflect meaningfully.**

---

### 🤖 Commands

- `/oneoff` — Log an expense for today  
- `/past` — Log an expense for a past date  
- `/insights` — View insights for the current month  

---

### 🧾 Expense Structure

Each expense entry includes:

- **Date**
- **Product**
- **Price**
- **Category**
- **Spend Type**

#### 🗂️ Categories & Spend Types
Spend types are **automatically assigned by default** based on the selected category.  
They describe how an expense behaves over time (day-to-day, optional, recurring, or irregular) and are used to power the built-in analysis.  
Defaults can be adjusted manually if needed.

| Category        | Default Spend Type |
|-----------------|--------------------|
| Income          | Income             |
| Food            | Essential          |
| Transport       | Essential          |
| Education       | Essential          |
| Shopping        | Discretionary      |
| Gifts           | Discretionary      |
| Lifestyle       | Discretionary      |
| Travel          | One-off            |
| Subscriptions   | Recurring          |



### 📊 Data Organization
- Expenses are stored in **Google Sheets**
- Expenses are organized into monthly sheets.
- When an entry belongs to a new month, a new sheet is created automatically.

### 📈 Built-in Insights

All analysis is derived directly from the sheet structure.

- Category-wise cost breakdown  
- Daily spending (day-to-day expenses only)  
- Spend type breakdown  
- Weekday vs weekend comparison  
- Total monthly spend  



---

## Setting up the Project and Running the Bot Locally

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
ENV=local
TOKEN="<your-telegram-bot-token>"
SPREADSHEET_ID="<your-google-spreadsheet-id>"
```


### 3. Obtaining Google Auth Token

#### Generate Google Auth Token
Run the following script once to generate a token.pickle file for Google authentication:
```
python generate_token.py
```
This will open a browser window for Google login. After successful login, a `token.pickle` file will be created in your project directory.

#### Convert to readable token in .env file

Run the following script to convert the `token.pickle` file to a base64 string:
```
base64 -i token.pickle -o token.pickle.b64
```

Open the `token.pickle.b64` file and copy its content into .env file like this:
```
GOOGLE_TOKEN_PICKLE_B64="<your-base64-encoded-google-token>"
```

### 4. Install dependencies
```
pip install -r requirements.txt
```

### 5. Start the bot! 🎉

```
python bot.py
```

## Telegram Bot Deployment
This bot is deployed using Railway. To set up webhooks, use the following API endpoints:

#### Delete Webhook

```
https://api.telegram.org/bot<TOKEN>/deleteWebhook
```

#### Get Webhook Info
```
https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

#### Set Webhook 

```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<your-railway-domain>/webhook
```