# cli.py
# ─────────────────────────────────────────────────────────────────
# Command-line version of the AI Resume Analyzer.
# Use this if you prefer the terminal over a browser UI.
#
# Usage:
#   python cli.py --resume path/to/resume.pdf --jd path/to/jd.txt
#   python cli.py --resume resume.pdf          (will prompt for JD)
# ─────────────────────────────────────────────────────────────────

import argparse
import sys
from analyzer import analyze_resume


def print_divider(char="─", width=60):
    print(char * width)


def print_header():
    print_divider("═")
    print("        AI RESUME ANALYZER  •  100% Free & Local")
    print_divider("═")
    print()


def print_results(results: dict):
    score    = results["score"]
    matching = results["matching"]
    missing  = results["missing"]
    suggestions = results["suggestions"]

    # ── Score ──────────────────────────────────────────────────
    if score >= 70:
        verdict = "EXCELLENT ✦"
    elif score >= 50:
        verdict = "GOOD ✓"
    elif score >= 30:
        verdict = "FAIR ◈"
    else:
        verdict = "WEAK ✗"

    print_divider()
    print(f"  MATCH SCORE : {score} / 100   [{verdict}]")
    print_divider()
    print()

    # ── Matching keywords ──────────────────────────────────────
    print(f"  ✅  MATCHING KEYWORDS ({len(matching)} found)")
    print_divider("-")
    if matching:
        # Print in 3 columns
        for i in range(0, len(matching), 3):
            row = matching[i:i+3]
            print("  " + "   ".join(f"• {kw:<22}" for kw in row))
    else:
        print("  No strong keyword matches found.")
    print()

    # ── Missing keywords ───────────────────────────────────────
    print(f"  ❌  MISSING KEYWORDS ({len(missing)} gaps)")
    print_divider("-")
    if missing:
        for i in range(0, len(missing), 3):
            row = missing[i:i+3]
            print("  " + "   ".join(f"  {kw:<22}" for kw in row))
    else:
        print("  No major gaps found — great coverage!")
    print()

    # ── Suggestions ────────────────────────────────────────────
    print("  💡  SUGGESTIONS")
    print_divider("-")
    for i, tip in enumerate(suggestions, 1):
        # Word-wrap long suggestions at 55 characters
        words = tip.split()
        line = f"  {i}. "
        for word in words:
            if len(line) + len(word) + 1 > 63:
                print(line)
                line = "     " + word + " "
            else:
                line += word + " "
        print(line)
        print()

    print_divider("═")
    print("  Analysis complete!")
    print_divider("═")


def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Analyzer — free, local, no API key needed."
    )
    parser.add_argument(
        "--resume", required=True,
        help="Path to your resume PDF (e.g. resume.pdf)"
    )
    parser.add_argument(
        "--jd",
        help="Path to a .txt file containing the job description (optional)"
    )
    args = parser.parse_args()

    print_header()

    # Load job description
    if args.jd:
        with open(args.jd, "r", encoding="utf-8") as f:
            job_description = f.read()
        print(f"  Loaded job description from: {args.jd}\n")
    else:
        print("  Paste the job description below.")
        print("  Press Enter twice then type END and press Enter to finish.\n")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        job_description = "\n".join(lines)

    print("\n  Analyzing… please wait.\n")

    try:
        results = analyze_resume(args.resume, job_description)
    except FileNotFoundError:
        print(f"  ERROR: Could not find PDF at '{args.resume}'")
        sys.exit(1)
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    print_results(results)


if __name__ == "__main__":
    main()
