import pathlib


def main() -> None:
    doc_path = pathlib.Path(__file__).parent / ".agent" / "REPO_CONTEXT.md"
    text = doc_path.read_text(encoding="utf-8")

    required_sections = [
        "# Repository Knowledge Base",
        "## Execution Flow (Text Diagram)",
        "## Change Impact Checklist",
        "## Agent Working Rules (Shared)",
    ]
    missing_sections = [s for s in required_sections if s not in text]
    if missing_sections:
        raise AssertionError(
            "Missing required sections: " + ", ".join(missing_sections)
        )

    required_paths = [
        "Open-LLM-VTuber-1.2.1/",
        "Hololive-Style-Bert-VITS2/",
    ]
    missing_paths = [p for p in required_paths if p not in text]
    if missing_paths:
        raise AssertionError("Missing required paths: " + ", ".join(missing_paths))

    print("REPO_CONTEXT.md sanity checks passed.")


if __name__ == "__main__":
    main()
