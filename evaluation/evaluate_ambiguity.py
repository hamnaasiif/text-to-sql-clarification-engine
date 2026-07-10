import json
from app.services.schema_service import get_database_schema
from app.services.ambiguity_service import check_ambiguity


def load_dataset(path="evaluation/dataset.json"):
    with open(path, "r") as f:
        return json.load(f)


def run_evaluation():
    schema = get_database_schema()
    dataset = load_dataset()

    correct = 0
    false_negatives = []  # system said clear, but it was actually ambiguous
    false_positives = []  # system said ambiguous, but it was actually clear

    for item in dataset:
        result = check_ambiguity(item["question"], schema)
        predicted = result.is_ambiguous
        actual = item["is_ambiguous"]

        if predicted == actual:
            correct += 1
        elif predicted is False and actual is True:
            false_negatives.append(item["question"])
        elif predicted is True and actual is False:
            false_positives.append(item["question"])

        print(f"[{item['id']}] Predicted: {predicted} | Actual: {actual} | {'✅' if predicted == actual else '❌'}")

    total = len(dataset)
    accuracy = correct / total * 100

    print("\n" + "=" * 50)
    print(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    print(f"\nFalse Negatives (dangerous — missed real ambiguity): {len(false_negatives)}")
    for q in false_negatives:
        print(f"  - {q}")
    print(f"\nFalse Positives (annoying — flagged clear question): {len(false_positives)}")
    for q in false_positives:
        print(f"  - {q}")


if __name__ == "__main__":
    run_evaluation()