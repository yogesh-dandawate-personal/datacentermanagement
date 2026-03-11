import sys
sys.path.insert(0, '/Users/yogesh/00_MyCode/01_PersonalProjects/datacentermanagement')

from scripts.sprint_queue_manager import SprintQueueManager
import sys

duration = int(sys.argv[1]) if len(sys.argv) > 1 else 0

manager = SprintQueueManager()
manager.register_all_sprints()

print("\n" + "="*60)
print("AUTONOMOUS SPRINT QUEUE SYSTEM INITIALIZED")
print("="*60)
print(f"Total Sprints: 13")
print(f"Max Concurrent: 2")
print(f"Duration: {duration} minutes" if duration > 0 else "Duration: Unlimited")
print("Ralph Loop: Enabled")
print("Auto Recovery: Enabled")
print("="*60 + "\n")

try:
    manager.run_autonomous_loop(duration_minutes=duration)
except KeyboardInterrupt:
    print("\n[INTERRUPTED] Saving state...")
    manager.save_state()
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    manager.save_state()
    raise
