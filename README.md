# SO_B_01
Telegram bot for managing stone locations. 01
# StoneBot (SO_B_01) 🗿📍✨

**Telegram Bot for Collecting and Mapping Unique Stones Tied to NFTs and Real-World Locations.**

## 🌟 Project Overview

StoneBot is an innovative Telegram bot designed for adventurers and collectors. It allows users to document and share unique "stones" found in real-world locations, linking them to a digital presence (eventually NFTs). This project aims to blend the physical world of exploration with the digital realm of collectibles, creating a unique experience for tracking discoveries, sharing geographical data, and building a community around shared interests.

### Core Concepts:
* **Stones as Collectibles:** Each "stone" represents a unique discovery, documented with a photo, description, and precise geographical coordinates.
* **Location-Based Tracking:** Users record the exact latitude and longitude where a stone was found, along with altitude and even local air quality data.
* **NFT Integration (Future):** The vision is to integrate with blockchain technology, allowing each documented stone to be minted as a unique Non-Fungible Token (NFT), providing verifiable ownership and a digital record of physical finds.
* **Community and Exploration:** Share your finds, explore where others have found stones, and discover new places.

## ✨ Features (Current & Planned)

### Current Features:
* **User Registration:** Automatic user registration upon first interaction with the bot (`/start`).
* **Add a Stone (`/add_stone`):**
    * Guided step-by-step process using FSM (Finite State Machine).
    * Collects: Photo, Description, Geographical Coordinates (Latitude, Longitude), Altitude (optional).
    * **Automatic Air Quality Index (AQI) Retrieval:** Fetches AQI data for the given location using OpenWeatherMap API.
    * Data confirmation step before saving.
* **View My Stones (`/my_stones`):**
    * Lists all stones added by the current user with detailed information (ID, Description, Coordinates, Altitude, AQI, Creation Date, Photo ID).
* **Location Mapping (`/map`):**
    * Requests user's current location.
    * (Currently displays coordinates; future will show nearby stones on a map).
* **Interactive Keyboards:** User-friendly reply keyboards for common actions (main menu, location sharing, confirmation).
* **Database Integration:** Uses SQLAlchemy with SQLite for persistent storage of user and stone data.

### Planned Features:
* **Interactive Map Integration:** Visualize all collected stones on an interactive map.
* **NFT Minting:** Functionality to mint each unique stone entry as an NFT on a blockchain.
* **Stone Sharing & Discovery:** Explore stones found by other users, filter by location, date, or type.
* **User Profiles:** Enhanced user profiles with statistics on collected stones.
* **Admin Panel:** Tools for moderation and management.
* **Public Gallery:** A web-based gallery of all unique stone findings.

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.9+
* `pip` (Python package installer)
* Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
* OpenWeatherMap API Key (for Air Quality data - [OpenWeatherMap API](https://openweathermap.org/api/air-pollution))

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/22moves/SO_B_01.git](https://github.com/22moves/SO_B_01.git)
    cd SO_B_01
    ```
    *(Note: If the above link doesn't work for cloning, please replace it with the correct public URL of your repository once it's accessible.)*

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate.bat  # On Windows (CMD)
    # .venv\Scripts\Activate.ps1  # On Windows (PowerShell)
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(If `requirements.txt` doesn't exist, create it first by running `pip freeze > requirements.txt` after installing all necessary packages manually, e.g., `pip install aiogram aiosqlite sqlalchemy httpx`)*

4.  **Configure environment variables:**
    Create a `config.py` file in the root directory of the project:
    ```python
    # config.py
    BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY_HERE"
    ```
    Replace `"YOUR_TELEGRAM_BOT_TOKEN_HERE"` and `"YOUR_OPENWEATHER_API_KEY_HERE"` with your actual tokens.

### Running the Bot

```bash
python main.py
The bot will start polling for updates. You can interact with it on Telegram.

📁 Project Structure
SO_B_01/
├── main.py                     # Main bot entry point, dispatcher setup, middleware
├── config.py                   # Configuration for tokens and API keys
├── database/                   # Database related files
│   ├── db.py                   # SQLAlchemy engine, session setup, init_db function
│   └── models.py               # SQLAlchemy ORM models (User, Stone)
├── handlers/                   # Bot command handlers
│   ├── __init__.py             # Makes handlers a Python package
│   ├── start.py                # Handler for /start command
│   ├── map.py                  # Handler for /map command
│   └── stone.py                # Handlers for /add_stone, /my_stones, FSM for stone data
├── keyboards/                  # Custom keyboards for Telegram UI
│   ├── __init__.py             # Makes keyboards a Python package
│   └── reply.py                # ReplyKeyboardMarkups (main menu, location, confirm)
├── states/                     # FSM states definitions
│   ├── __init__.py             # Makes states a Python package
│   └── stone.py                # FSM States for stone adding process
├── .env                        # (Optional) Environment variables for local development
├── .gitignore                  # Specifies untracked files Git should ignore
├── README.md                   # This file!
└── requirements.txt            # Project dependencies
🤝 Contributing
Contributions are welcome! If you have suggestions or find bugs, please open an issue or submit a pull request.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
(Note: You might need to create a LICENSE file if you don't have one.)
