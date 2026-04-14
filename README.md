# Rust Runner Practice MVP

This is a prototype for the Rust Runner game jam submission, built using the [Kraken Engine](https://krakenengine.org/).

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
- **D**: Drive Forward
- **A**: Reverse
- **Q / E**: Balance Chassis (Air Rotation)
- **Goal**: Reach 6,000 units distance without flipping or decaying!
