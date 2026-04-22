import csv
import os
import random
import statistics
import time
from datetime import datetime

from gpiozero import LED, Button, Buzzer
from signal import pause

BUTTON_PIN = 17
LED_PIN = 18
BUZZER_PIN = 23

LOG_FILE = "reaction_log.csv"
USE_BUZZER = True

led = LED(LED_PIN)
button = Button(BUTTON_PIN, pull_up=True)
buzzer = Buzzer(BUZZER_PIN) if USE_BUZZER else None


def setup_log_file():
    """
    Creates the CSV log file with headers if it does not already exist.
    """
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "round",
                "result",
                "reaction_time_ms"
            ])


def log_result(round_number, result, reaction_time_ms):
    """
    Appends one game result to the CSV file.

    :param round_number: the round number
    :param result: round outcome such as valid or false_start
    :param reaction_time_ms: reaction time in milliseconds, or blank if none
    """
    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            round_number,
            result,
            reaction_time_ms
        ])


def beep_short():
    """
    Plays a short beep if the buzzer is enabled.
    """
    if buzzer is not None:
        buzzer.on()
        time.sleep(0.08)
        buzzer.off()


def beep_success():
    """
    Plays a quick two-part success beep if the buzzer is enabled.
    """
    if buzzer is not None:
        for _ in range(2):
            buzzer.on()
            time.sleep(0.06)
            buzzer.off()
            time.sleep(0.05)


def wait_for_button_release():
    """
    Waits until the button is no longer pressed.
    """
    while button.is_pressed:
        time.sleep(0.01)


def show_stats(valid_times, false_starts):
    """
    Prints current session statistics.

    :param valid_times: list of valid reaction times in milliseconds
    :param false_starts: number of false starts
    """
    print("\n--- Session Stats ---")
    print(f"Valid rounds: {len(valid_times)}")
    print(f"False starts: {false_starts}")

    if valid_times:
        print(f"Best time: {min(valid_times):.2f} ms")
        print(f"Average time: {statistics.mean(valid_times):.2f} ms")

        if len(valid_times) > 1:
            print(f"Median time: {statistics.median(valid_times):.2f} ms")
    print("---------------------\n")


def play_round(round_number):
    """
    Runs one round of the reaction game.

    :param round_number: the round number
    :return: tuple of (result_string, reaction_time_ms or None)
    """
    led.off()
    wait_for_button_release()

    print(f"\nRound {round_number}")
    print("Get ready...")
    print("Wait for the LED, then press the button as fast as you can.")
    print("Do NOT press early.")

    delay = random.uniform(2.0, 5.0)
    start_wait = time.time()

    while time.time() - start_wait < delay:
        if button.is_pressed:
            print("Too early! False start.")
            beep_short()
            log_result(round_number, "false_start", "")
            wait_for_button_release()
            return "false_start", None
        time.sleep(0.001)

    led.on()
    start_time = time.perf_counter()

    while not button.is_pressed:
        time.sleep(0.0005)

    end_time = time.perf_counter()
    led.off()

    reaction_time_ms = (end_time - start_time) * 1000
    print(f"Your reaction time: {reaction_time_ms:.2f} ms")
    beep_success()
    log_result(round_number, "valid", f"{reaction_time_ms:.2f}")
    wait_for_button_release()
    return "valid", reaction_time_ms


def main():
    """
    Main program loop.
    """
    print("=" * 40)
    print("Raspberry Pi Reaction Time Game")
    print("=" * 40)
    print("Controls:")
    print("- Press Enter to start a round")
    print("- Type q and press Enter to quit")
    print()

    setup_log_file()

    round_number = 1
    valid_times = []
    false_starts = 0

    try:
        while True:
            user_input = input("Press Enter to play, or type q to quit: ").strip().lower()

            if user_input == "q":
                break

            result, reaction_time = play_round(round_number)

            if result == "valid":
                valid_times.append(reaction_time)
            else:
                false_starts += 1

            show_stats(valid_times, false_starts)
            round_number += 1

    except KeyboardInterrupt:
        print("\nProgram interrupted.")

    finally:
        led.off()
        if buzzer is not None:
            buzzer.off()

        print("\nFinal session summary:")
        show_stats(valid_times, false_starts)
        print(f"Results saved to: {LOG_FILE}")


if __name__ == "__main__":
    main()
