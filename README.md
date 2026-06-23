# 🌤️ Weather Dashboard

A responsive weather dashboard web application built with **Python Flask** and vanilla **HTML/CSS/JavaScript**. It fetches real-time weather data from the [OpenWeatherMap API](https://openweathermap.org/api) and displays temperature, humidity, wind speed, visibility, and more.

---

## ✨ Features

- 🔍 Search weather by city name
- 🌡️ Displays temperature, feels-like temperature, humidity, wind speed, and visibility
- 🎨 Dynamic weather icons based on weather condition codes
- 💾 In-memory response caching (configurable TTL) to reduce API calls
- 🧪 Built-in mock data for development and testing without a live API key
- ⌨️ Keyboard-friendly (press **Enter** to search)
- 📱 Responsive design that works on mobile and desktop

---

## 🛠️ Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3, Flask                   |
| Frontend  | HTML5, CSS3, Vanilla JavaScript   |
| Weather   | OpenWeatherMap API                |
| Hosting   | Azure App Service (Linux)         |

---

## 📁 Project Structure

```
accazharapp/
├── app.py          # Flask application – routes, caching, API integration
├── index.html      # Single-page frontend
├── style.css       # Styling
└── README.md
```

---

## ⚙️ Environment Variables

| Variable                  | Default          | Description                                              |
|---------------------------|------------------|----------------------------------------------------------|
| `OPENWEATHER_API_KEY`     | `YOUR_API_KEY_HERE` | Your OpenWeatherMap API key                           |
| `USE_MOCK_DATA`           | `true`           | Set to `false` to use the live OpenWeatherMap API        |
| `WEATHER_CACHE_TTL_SECONDS` | `300`          | How long (in seconds) to cache weather responses         |

---

## 🚀 Running Locally

### Prerequisites

- Python 3.8 or higher
- pip

### 1. Clone the repository

```bash
git clone https://github.com/ibnehussain/accazharapp.git
cd accazharapp
```

### 2. Install dependencies

```bash
pip install flask requests
```

### 3. Set environment variables (optional)

To use the real OpenWeatherMap API, set your API key and disable mock data:

```bash
# macOS / Linux
export OPENWEATHER_API_KEY="your_api_key_here"
export USE_MOCK_DATA="false"

# Windows (Command Prompt)
set OPENWEATHER_API_KEY=your_api_key_here
set USE_MOCK_DATA=false
```

To run with built-in mock data (no API key needed), leave `USE_MOCK_DATA` as `true` (the default).

### 4. Start the server

```bash
python app.py
```

Open your browser at **http://localhost:5000**.

### Mock data cities

When `USE_MOCK_DATA=true`, the following cities are available: **London**, **New York**, **Tokyo**, **Sydney**, **Dubai**, **Paris**, **Moscow**.

---

## ☁️ Deploy to Azure App Service

### Prerequisites

- An [Azure account](https://azure.microsoft.com/free/)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and logged in (`az login`)
- [Python 3.8+](https://www.python.org/downloads/) installed locally

### Step 1 – Add a `requirements.txt`

Azure App Service uses `requirements.txt` to install Python dependencies. Create it in the project root:

```bash
pip freeze > requirements.txt
```

Or create it manually with the minimum required packages:

```
flask
requests
gunicorn
```

> **Note:** `gunicorn` is the production WSGI server used by Azure on Linux.

### Step 2 – Add a startup command file (optional but recommended)

Create a file named `startup.txt` in the project root:

```
gunicorn --bind=0.0.0.0 --timeout 600 app:app
```

### Step 3 – Create a Resource Group

```bash
az group create \
  --name weatherdashboard-rg \
  --location eastus
```

### Step 4 – Create an App Service Plan

```bash
az appservice plan create \
  --name weatherdashboard-plan \
  --resource-group weatherdashboard-rg \
  --sku B1 \
  --is-linux
```

> Replace `B1` with a different SKU if needed (e.g., `F1` for the free tier).

### Step 5 – Create the Web App

```bash
az webapp create \
  --resource-group weatherdashboard-rg \
  --plan weatherdashboard-plan \
  --name <YOUR_APP_NAME> \
  --runtime "PYTHON:3.11"
```

> `<YOUR_APP_NAME>` must be globally unique and will be your app's URL: `https://<YOUR_APP_NAME>.azurewebsites.net`

### Step 6 – Configure Application Settings

Set your environment variables on the Azure Web App:

```bash
az webapp config appsettings set \
  --resource-group weatherdashboard-rg \
  --name <YOUR_APP_NAME> \
  --settings \
    OPENWEATHER_API_KEY="your_api_key_here" \
    USE_MOCK_DATA="false" \
    WEATHER_CACHE_TTL_SECONDS="300"
```

### Step 7 – Set the startup command

```bash
az webapp config set \
  --resource-group weatherdashboard-rg \
  --name <YOUR_APP_NAME> \
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
```

### Step 8 – Deploy the code

**Option A – Deploy via ZIP (simplest)**

```bash
# Create a ZIP of the project files
zip -r app.zip app.py index.html style.css requirements.txt

# Deploy the ZIP to Azure
az webapp deploy \
  --resource-group weatherdashboard-rg \
  --name <YOUR_APP_NAME> \
  --src-path app.zip \
  --type zip
```

**Option B – Deploy via GitHub Actions (CI/CD)**

1. In the Azure Portal, go to your Web App → **Deployment Center**.
2. Select **GitHub** as the source and authorize Azure.
3. Select your repository and branch.
4. Azure will automatically create a GitHub Actions workflow that builds and deploys on every push.

**Option C – Deploy via Azure CLI (local Git)**

```bash
az webapp deployment source config-local-git \
  --name <YOUR_APP_NAME> \
  --resource-group weatherdashboard-rg

# Push your code using the remote URL printed by the command above
git remote add azure <DEPLOYMENT_URL>
git push azure main
```

### Step 9 – Open the app

```bash
az webapp browse \
  --resource-group weatherdashboard-rg \
  --name <YOUR_APP_NAME>
```

Or navigate to `https://<YOUR_APP_NAME>.azurewebsites.net` in your browser.

---

## 🔑 Getting an OpenWeatherMap API Key

1. Register for a free account at [https://openweathermap.org](https://openweathermap.org).
2. Go to **API Keys** in your account dashboard.
3. Copy your default key (or generate a new one).
4. Set it as the `OPENWEATHER_API_KEY` environment variable locally or on Azure.

> Free-tier keys are activated within a few hours of registration.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
