import json
import sys
from collections import defaultdict

def extract_user_time(solving_time):
    """
    Extracts the user time (float) from strings like:
    '14.77user 1.24system 0:16.02elapsed ...'
    """
    try:
        for part in solving_time.split():
            if part.endswith("user"):
                return float(part.replace("user", ""))
    except Exception:
        pass
    return None

def analyze(file_path):
    with open(file_path) as f:
        data = json.load(f)

    solved_benchmarks = defaultdict(lambda: defaultdict(set))
    line_stats = defaultdict(lambda: defaultdict(list))
    time_stats = defaultdict(lambda: defaultdict(list))

    for entry in data:
        library = entry.get("library_name")
        benchmark = entry.get("benchmark_path")

        for s in entry.get("solving", []):
            solver = s.get("solver_config")
            outcome = s.get("solving_outcome")

            if outcome is not None and outcome >= 0:
                solved_benchmarks[library][solver].add(benchmark)

                if "nr_of_lines" in s:
                    line_stats[library][solver].append(s["nr_of_lines"])

                if "solving_time" in s:
                    user_time = extract_user_time(s["solving_time"])
                    if user_time is not None:
                        time_stats[library][solver].append(user_time)

    for library in sorted(solved_benchmarks):
        print(f"Library: {library}\n")

        print(
            f"{'solver config':<18} | "
            f"{'nr benchmarks solved':>21} | "
            f"{'avg nr_of_lines':>16} | "
            f"{'avg user time (s)':>18}"
        )
        print("-" * (18 + 3 + 21 + 3 + 16 + 3 + 18))

        for solver in sorted(solved_benchmarks[library]):
            solved_count = len(solved_benchmarks[library][solver])

            lines = line_stats[library][solver]
            avg_lines = sum(lines) / len(lines) if lines else None

            times = time_stats[library][solver]
            avg_time = sum(times) / len(times) if times else None

            avg_lines_str = f"{avg_lines:.2f}" if avg_lines is not None else "N/A"
            avg_time_str = f"{avg_time:.2f}" if avg_time is not None else "N/A"

            print(
                f"{solver:<18} | "
                f"{solved_count:>21} | "
                f"{avg_lines_str:>16} | "
                f"{avg_time_str:>18}"
            )

        print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_solved_per_library_table.py merged.json")
        sys.exit(1)

    analyze(sys.argv[1])

