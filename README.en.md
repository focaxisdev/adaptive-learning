# Adaptive Learning

[繁體中文](README.md) · **English** · [日本語](README.ja.md)

A conversation-based framework for learning any subject. The aim is to apply what you learn on your own, not to rack up answered questions.

**v0.2.0 · [MIT License](LICENSE) · [Release history](https://github.com/focaxisdev/adaptive-learning/releases)**

## Quick start

1. Give your AI assistant the **full text** of the [project instructions](docs/PROJECT_INSTRUCTIONS.md) and any study material you may use. The canonical instructions are in Traditional Chinese; they still govern the workflow when you ask to study in English. A link alone does not give the assistant access.
2. Say: “I want to learn ___ so I can ___. Start with general tutoring in English. If a setting is unclear, suggest a simple default.”
3. Once you confirm your goal, available sources, current level and constraints, answer the first short diagnostic question in the same chat. To set up a project or move to another chat, ask for the complete reusable instructions or a handoff of your current progress.

No study material? You can explicitly opt in to general-knowledge practice with clear limits. A regular chat is enough; no installation, database, or paid API is required.

| Goal | Mode |
| --- | --- |
| Build a skill step by step | General tutoring (default) |
| Work on a specific gap | Targeted practice with a stopping point and a return to the main lesson |
| Take a standalone quiz | Agree on scope and scoring. A blueprint is optional for a one-off quiz with no running score, coverage record or cross-quiz repeat check. |
| Run a series of mock exams | Build or load a knowledge and skills blueprint, confirm the version, then explicitly start the cycle. |

If you move a quiz to a new chat, the handoff includes progress, the pending question and the source passages you may carry over. Paste any missing passage identified in the handoff before the assistant sets or grades a question that depends on it.

## Start or resume a mock exam marathon

Ask the assistant to list skills from **all readable chapters** and any additional in-scope skills in sample or past questions. Check the sources, versions, locations and gaps. Official questions also calibrate difficulty for formal exams. When ready, say “I confirm this blueprint version. Start a new cycle.” Confirmation alone leaves the exam waiting. General tutoring and targeted practice can start without a blueprint.

The full scope remains eligible across chapters. After every ten valid questions, a coverage check links skills to question numbers. The final report lists untested skills. Coverage alone cannot establish mastery or guarantee that a short exam reaches every skill. A separate record of visible questions and their essential reasoning helps detect repeats within the available history.

The assistant checks recent answer positions for repeating cycles before presenting a multiple-choice question. A same-cycle handoff carries the available recent positions and marks gaps.

To change chats mid-cycle, paste the handoff and answer the original pending question. The question number and score carry over. At cycle end you receive two independent handoffs, one for targeted practice and one for starting a new exam.

## What stays with you

The assistant can use only sources and history it can actually read. It does not automatically save progress or sync across chats. When switching chats, ask for a handoff and carry it over yourself. Do not submit private study materials, real answers or scores, conversation links, or credentials to the repository.

See the [maintainer's design notes](docs/LEARNING_DESIGN.md), [validation scope](docs/VALIDATION.md), and [license and attribution notice](NOTICE.md), currently in Traditional Chinese. Repository examples use synthetic data. Structural checks and synthetic trials do not establish real-world learning outcomes.
