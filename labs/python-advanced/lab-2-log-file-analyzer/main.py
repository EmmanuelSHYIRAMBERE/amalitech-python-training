"""CLI entry point for the Log File Analyzer."""

import logging
from pathlib import Path

from src.analyzer import analyze, batch_demo, save_report
from src.pipeline import status_label

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

LOG_PATH = Path("sample_data/access.log")
REPORT_PATH = Path("reports/report.json")


def main() -> None:
    report = analyze(LOG_PATH)
    save_report(report, REPORT_PATH)

    print("\n========== LOG FILE ANALYSIS REPORT ==========")
    print(f"Log file       : {LOG_PATH}")
    print(f"Total requests : {report['total_requests']}")
    print(f"Total bytes    : {report['total_bytes']:,}")
    print(f"Error rate     : {report['error_rate_pct']}%")
    print(f"  Client errors: {report['client_error_count']}")
    print(f"  Server errors: {report['server_error_count']}")

    print("\nStatus Code Breakdown:")
    for code, count in report["status_counts"].items():
        print(f"  {code} {status_label(int(code)):<25} {count}")

    print("\nHTTP Method Counts:")
    for method, count in sorted(report["method_counts"].items()):
        print(f"  {method:<8} {count}")

    print("\nTop 10 URLs:")
    for i, (url, count) in enumerate(report["top_urls"], 1):
        print(f"  {i:>2}. {url:<35} {count}")

    print("\nTop 10 Client IPs:")
    for i, (ip, count) in enumerate(report["top_ips"], 1):
        print(f"  {i:>2}. {ip:<18} {count}")

    print("\nHourly Traffic (requests per hour):")
    for hour, count in sorted(report["hourly_traffic"].items(), key=lambda x: int(x[0])):
        bar = "#" * (count // 5)
        print(f"  {int(hour):02d}:00  {bar} {count}")

    print(f"\nFull report saved to: {REPORT_PATH}")
    print("===============================================\n")

    print("--- Generator batch demo (batch_size=100) ---")
    batch_demo(LOG_PATH, batch_size=100)


if __name__ == "__main__":
    main()
