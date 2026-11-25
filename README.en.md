# Adaptive Learning

[繁體中文](README.md) · **English** · [日本語](README.ja.md)

A conversation-based framework for learning any subject. The aim is to apply what you learn on your own, not to rack up answered questions.

**v0.1.0 · [MIT License](LICENSE).** This first regular release is suitable for a small trial. It does not guarantee learning gains, unique questions, or equivalence to a real exam.

## Quick start

1. Give your AI assistant the **full text** of the [project instructions](docs/PROJECT_INSTRUCTIONS.md) and any study material you may use. The canonical instructions are in Traditional Chinese; they still govern the workflow when you ask to study in English. A link alone does not give the assistant access.
2. Say: “I want to learn ___ so I can ___. Start with general tutoring in English. If a setting is unclear, suggest a simple default.”
3. The assistant asks only for what it needs now, such as your goal, available sources, current level, and constraints. It produces a self-contained setup you can copy to project instructions or the top of a new chat. Say “Start” when ready, and work one question or task at a time.

No study material? You can explicitly opt in to general-knowledge practice with clear limits. A regular chat is enough; no installation, database, or paid API is required.

| Goal | Mode |
| --- | --- |
| Build a skill step by step | General tutoring (default) |
| Work on a specific gap | Targeted practice with a stopping point and a return to the main lesson |
| Take a mock test on agreed material | Chat-based mock exam with scoring configured only when selected |

## What stays with you

The assistant can use only sources and history it can actually read. It does not automatically save progress or sync across chats. When switching chats, ask for a handoff and carry it over yourself. Do not submit private study materials, real answers or scores, conversation links, or credentials to the repository.

See the [maintainer's design notes](docs/LEARNING_DESIGN.md), [validation scope](docs/VALIDATION.md), and [license and attribution notice](NOTICE.md), currently in Traditional Chinese. Repository examples use synthetic data. Structural checks and synthetic trials do not establish real-world learning outcomes.
