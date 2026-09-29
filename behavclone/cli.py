import argparse

from behavclone.ingestion.assignment import load_assignment


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="behavclone",
        description=(
            "Evidence-oriented similarity analysis for "
            "architecture-flexible programming assignments."
        ),
    )

    subparsers = parser.add_subparsers(dest="command")

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Load and inspect an assignment.",
    )

    analyze_parser.add_argument(
        "assignment",
        help="Path to the assignment directory.",
    )

    args = parser.parse_args()

    if args.command != "analyze":
        parser.print_help()
        return

    assignment = load_assignment(args.assignment)

    java_file_count = sum(
        len(submission.source_files)
        for submission in assignment.submissions
    )

    print()
    print("BehavClone")
    print("=" * 55)
    print(f"Assignment:        {assignment.config.name}")
    print(f"Language:          {assignment.config.language}")
    print(f"Submissions:       {len(assignment.submissions)}")
    print(f"Java files:        {java_file_count}")
    print()

    print("Discovered submissions")
    print("-" * 55)

    for submission in assignment.submissions:
        print(
            f"{submission.submission_id:<20} "
            f"{len(submission.source_files)} Java file(s)"
        )

    print()
    print("No plagiarism determination is produced.")
    print("All future evidence requires instructor review.")


if __name__ == "__main__":
    main()
