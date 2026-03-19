from codecarbon import EmissionsTracker

def get_tracker():
    return EmissionsTracker(
        project_name="lm-studio-chat",
        output_dir="./emissions",
        log_level="error"
    )