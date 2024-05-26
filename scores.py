import json

def display_scores(scores_file='scores.json'):
    try:
        with open(scores_file, 'r') as file:
            scores = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No scores available.")
        return

    print(f"{'Date':<20}{'Time (s)':<10}{'Enemies Killed':<15}{'Score':<10}")
    print("-" * 55)
    for entry in scores:
        print(f"{entry['datetime']:<20}{entry['time']:<10.2f}{entry['enemies_killed']:<15}{entry['score']:<10.2f}")

if __name__ == "__main__":
    display_scores()
