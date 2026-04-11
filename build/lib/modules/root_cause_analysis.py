def detect_root_cause(error_analysis):
    """
    Detect probable root cause from analyzed error patterns.
    """

    if not error_analysis or error_analysis.get("total_errors", 0) == 0:
        return {
            "summary": "No root cause detected",
            "category": "unknown",
            "confidence": "low",
            "evidence": [],
        }

    evidence = []
    normalized_patterns = error_analysis.get("normalized_error_counts", {})
    affected_modules = error_analysis.get("affected_modules", {})

    if _has_module_resolution_failures(normalized_patterns):
        modules = list(affected_modules.keys())[:10]
        evidence.append("Repeated module resolution failures detected during build")
        if modules:
            evidence.append(
                "Affected modules: " + ", ".join(modules)
            )
        evidence.append(
            "Errors indicate Node.js built-in modules are being bundled in an unsupported target environment"
        )
        return {
            "summary": "Missing or unsupported Node.js built-in modules during build",
            "category": "dependency_or_runtime_mismatch",
            "confidence": "high",
            "evidence": evidence,
        }

    if _has_build_failure(normalized_patterns):
        evidence.append("Build failure messages dominate the incident timeline")
        return {
            "summary": "Build process failure",
            "category": "build_failure",
            "confidence": "medium",
            "evidence": evidence,
        }

    if _has_configuration_signal(normalized_patterns):
        evidence.append("Configuration-related warnings or failures were detected")
        return {
            "summary": "Deployment or configuration issue",
            "category": "configuration_issue",
            "confidence": "medium",
            "evidence": evidence,
        }

    evidence.append("No dominant error signature matched the current rule set")
    return {
        "summary": "Unknown root cause",
        "category": "unknown",
        "confidence": "low",
        "evidence": evidence,
    }


def _has_module_resolution_failures(normalized_patterns):
    for message, count in normalized_patterns.items():
        lowered = message.lower()
        if count <= 0:
            continue
        if "could not resolve" in lowered:
            return True
        if "wasn't found on the file system but is built into node" in lowered:
            return True
    return False


def _has_build_failure(normalized_patterns):
    for message in normalized_patterns:
        lowered = message.lower()
        if "build failed" in lowered or "failed building" in lowered:
            return True
    return False


def _has_configuration_signal(normalized_patterns):
    for message in normalized_patterns:
        lowered = message.lower()
        if "configuration" in lowered or "wrangler.toml" in lowered:
            return True
    return False
