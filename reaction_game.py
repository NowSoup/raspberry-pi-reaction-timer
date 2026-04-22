from gpiozero import RGBLED, Button, Buzzer
from time import perf_counter, sleep
import random
import csv
import os

# GPIO setup
rgb = RGBLED(18, 23, 24)   # R, G, B
button = Button(17)
buzzer = Buzzer(25)

LOG_FILE = "reaction_log.csv"


# Utility
def beep(duration=0.1):
    buzzer.on()
    sleep(duration)
    buzzer.off()


def wait_for_release():
    while button.is_pressed:
        sleep(0.01)


def log_result(time_ms):
    new_file = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["reaction_time_ms"])
        writer.writerow([round(time_ms, 2)])


# Game Phases
def countdown():
    print("\nGet ready...")
    for i in [3, 2, 1]:
        print(i)
        beep(0.05)
        sleep(1)


def wait_phase():
    rgb.color = (1, 0, 0)  # red
    delay = random.uniform(2, 5)

    start = perf_counter()
    while perf_counter() - start < delay:
        if button.is_pressed:
            rgb.color = (0, 0, 1)  # blue = false start
            print("❌ Too early!")
            beep(0.4)
            wait_for_release()
            return False
        sleep(0.001)
    return True


def reaction_phase():
    rgb.color = (0, 1, 0)  # green
    beep(0.1)

    start = perf_counter()
    button.wait_for_press()
    end = perf_counter()

    rgb.off()
    wait_for_release()

    return (end - start) * 1000


# Main Loop
def main():
    scores = []

    print("=== Reaction Trainer ===")
    print("Wait for GREEN, then press the button.")
    print("Press early = fail.\n")

    while True:
        input("Press Enter to start...")

        countdown()

        if not wait_phase():
            continue

        reaction = reaction_phase()
        scores.append(reaction)
        log_result(reaction)

        best = min(scores)
        avg = sum(scores) / len(scores)

        print(f"⏱ Time: {reaction:.2f} ms")
        print(f"🏆 Best: {best:.2f} ms | 📊 Avg: {avg:.2f} ms\n")

        # best score sound
        if reaction == best:
            print("🔥 NEW BEST!")
            beep(0.3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        rgb.off()
        buzzer.off()
        print("\nExiting...")
