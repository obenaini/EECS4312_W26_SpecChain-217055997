
import subprocess
import sys

def run_script(script_path, description):
    """Runs a Python script using subprocess and prints status messages."""
    print(f"\nRunning: {description}")
    print(f"Script: {script_path}")
    try:
        subprocess.run([sys.executable, script_path], check=True)
        print(f"Successfully completed: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}")
        print(e)
        sys.exit(1)

def main():
    # Step 1: Collect or import raw reviews
    run_script("src/01_collect_or_import.py", "Collecting or importing raw reviews")

    # Step 2: Clean the raw reviews
    run_script("src/02_clean.py", "Cleaning raw reviews")

    # Step 3: Generate automated personas and review groups
    run_script("src/05_personas_auto.py", "Generating automated personas")

    # Step 4: Generate automated specifications
    run_script("src/06_spec_generate.py", "Generating automated specifications")

    # Step 5: Generate automated tests
    run_script("src/07_tests_generate.py", "Generating automated tests")

    # Step 6: Compute metrics for automated pipeline
    run_script("src/08_metrics.py", "Computing metrics")

if __name__ == "__main__":
    main()