# Arena Elo Simulation

This project simulates an assessment environment (Arena) where students and questions interact to calibrate their respective skill and difficulty levels using the **Elo Rating** system.

## 🚀 Features
- **Elo Rating System:** Probability of success calculation and rating updates.
- **Dynamic K-Factor:** Logarithmic decay of the K-factor for fast calibration of new items.
- **Adaptive Matchmaking:** $\epsilon$-greedy strategy to balance exploration of new questions and exploitation of questions at the student's level.
- **MLE Recalibration:** Batch adjustment via *Maximum Likelihood Estimation* for higher statistical precision.
- **Anchoring:** Use of benchmark items to keep the system scale fixed.

## 🛠️ Structure
- `engine/elo_engine.py`: The system's mathematical engine.
- `models/`: Definitions for Players and Challenges.
- `main.py`: Simulation script and convergence plot generation.

## 📊 How to Run
```bash
python main.py
```
The script will generate MAE (Mean Absolute Error) metrics and plots comparing real (hidden) skill vs. the Elo-estimated skill.
