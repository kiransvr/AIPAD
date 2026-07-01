"""Health controller responses."""


def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "AI Portfolio Analytics Dashboard",
        "version": "1.0.0",
    }


def liveness() -> dict[str, str]:
    return {"status": "alive"}


def readiness() -> dict[str, str]:
    return {"status": "ready"}
