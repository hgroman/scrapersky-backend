import json
import os
import re

from bs4 import BeautifulSoup

# Use relative paths within the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Extract orphaned files list using BeautifulSoup
print("ANALYZING STANDARD VS ENHANCED REPORTS FOR CRITICAL COMPONENTS...")
print("\nExtracting orphaned files from standard report...")

orphaned_files = []
try:
    with open(os.path.join(PROJECT_DIR, "codebase_analysis_report.html"), "r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        # Find all list items in the orphaned files section
        items = soup.find_all("li", class_="list-group-item")
        for item in items:
            text = item.get_text()
            if "%" in text:  # Only grab items with confidence percentages
                file_path = text.split(" <span")[0].strip()
                confidence_match = re.search(r"(\d+)%", text)
                confidence = int(confidence_match.group(1)) if confidence_match else 0
                orphaned_files.append({"file": file_path, "confidence": confidence})

    print(f"Found {len(orphaned_files)} files marked as orphaned")
except Exception as e:
    print(f"Error parsing HTML report: {e}")

# Load enhanced analysis data
print("\nExtracting scheduler components from enhanced report...")
try:
    with open(os.path.join(PROJECT_DIR, "enhanced_analysis_report.json"), "r") as f:
        enhanced = json.load(f)
        schedulers = enhanced["scheduler_components"]
        print(f"Found {len(schedulers)} scheduler components")
except Exception as e:
    print(f"Error loading enhanced report: {e}")

# Find orphaned files that are actually scheduler components
critical_components = []
for scheduler in schedulers:
    scheduler_path = scheduler["file"]
    matching_orphans = [o for o in orphaned_files if scheduler_path in o["file"]]

    for orphan in matching_orphans:
        critical_components.append(
            {
                "file": orphan["file"],
                "orphan_confidence": orphan["confidence"],
                "scheduler_confidence": scheduler["confidence"],
            }
        )

# Show results
print("\n" + "=" * 60)
print(
    f"CRITICAL ISSUE: Found {len(critical_components)} scheduler components incorrectly marked as orphaned:"
)
print("=" * 60)

for comp in critical_components:
    print(f"\n- {comp['file']}")
    print(
        f"  * Standard analysis: Marked as orphaned with {comp['orphan_confidence']}% confidence"
    )
    print(
        f"  * Enhanced analysis: Actually a SCHEDULER with {comp['scheduler_confidence']}% confidence"
    )

print(
    "\nThis demonstrates why enhanced analysis is necessary - static analysis alone misses critical components!"
)
