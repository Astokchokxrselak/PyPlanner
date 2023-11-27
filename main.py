import threading

import ui
import alerts

if __name__ == "__main__":
    # Start the assignment checking thread
    assignment_thread = threading.Thread(target=alerts.check_assignments, daemon=True)
    assignment_thread.start()

    # Continue with your UI code or other components
    ui.ui()
