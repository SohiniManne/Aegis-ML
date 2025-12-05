import time
import subprocess
import sys

def run_monitor():
    """Runs the monitor.py script as a subprocess."""
    print("⏰ Scheduler: Triggering Drift Detection...")
    try:
        # We use the same python interpreter that is running this script
        result = subprocess.run(
            [sys.executable, "src/monitor.py"], 
            capture_output=True, 
            text=True
        )
        
        # Print the output from monitor.py so we can see it in this window
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errors:", result.stderr)
            
    except Exception as e:
        print(f"❌ Scheduler Error: {e}")

if __name__ == "__main__":
    print("🚀 Aegis ML Scheduler Started.")
    print("   Running drift checks every 10 seconds...")
    print("   (Press Ctrl+C to stop)")
    
    try:
        while True:
            run_monitor()
            # Wait 10 seconds before next check
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped.")