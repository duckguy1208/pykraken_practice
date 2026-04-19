# Wither's Wake

A high-stakes platformer prototype where essence is your only lifeline. Built using the [Kraken Engine](https://krakenengine.org/).

## The Core Mechanic: Essence
In *Wither's Wake*, your life essence is constantly decaying.
- **Stable Platforms:** Stand on gray platforms to slowly recharge your essence.
- **Bloom Platforms:** Left-click to create temporary platforms. Creating a platform costs 20% essence.
- **Decay:** Essence decays naturally over time. If it reaches zero, you wither.

## Setup Instructions

To ensure the game runs correctly with all dependencies, please follow these steps:

### 1. Create a Virtual Environment
```bash
python -m venv venv
```

### 2. Activate the Environment
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Game
```bash
python main.py
```

## Controls
- **A / D**: Move Left/Right
- **SPACE**: Jump
- **L-CLICK**: Bloom temporary platform (Costs 20% Essence)
- **Goal**: Reach the far side (X > 1000) while standing on stable ground to win!
