    diagnostics = payload.get("diagnostics", [])
    reported = summary.get("errors")
    if reported is not None:
        observed = sum(d.get("severity") == "error" for d in diagnostics)
        if type(reported) is not int or reported != observed:
            raise RuntimeError(
                f"checker error count mismatch for {hy_path}: "
                f"summary.errors={reported!r}, diagnostics={observed}"
            )
    return summary, diagnostics
