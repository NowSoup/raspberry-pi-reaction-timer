# Raspberry Pi Reaction Trainer

A reaction-time game built with a Raspberry Pi 5 using an RGB LED, push button, and buzzer. The system measures reaction time, detects false starts, gives visual and audio feedback, and logs results to a CSV file.

## Features
- 3-second countdown before each round
- Random wait period to prevent guessing
- False start detection
- RGB LED status feedback
- Buzzer feedback
- Reaction time measurement in milliseconds
- Best score and average score tracking
- CSV logging for saved results

## Hardware Used
- Raspberry Pi 5
- RGB LED
- Push button
- Buzzer
- Breadboard
- Jumper wires
- Resistors

## GPIO Pin Setup
- RGB LED: GPIO 18, 23, 24
- Button: GPIO 17
- Buzzer: GPIO 25

## How It Works
1. The game starts after the user presses Enter.
2. A countdown begins.
3. The LED turns red during a random delay.
4. If the button is pressed too early, the round fails.
5. When the LED turns green, the player presses the button as fast as possible.
6. The reaction time is displayed and saved to `reaction_log.csv`.

## How to Run
```bash
python3 reaction_game.py
