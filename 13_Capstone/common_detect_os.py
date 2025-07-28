import os

def detect_runtime_env() -> str:
    """Detect if running in Docker, Kubernetes, or locally."""
    if os.path.exists("/.dockerenv"):
        return "docker"
    elif os.getenv("KUBERNETES_SERVICE_HOST"):
        return "k8s"
    return "local"

if __name__ == "__main__":
    env = detect_runtime_env()
    print(f"Running in '{env}' environment")
