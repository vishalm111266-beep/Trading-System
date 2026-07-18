name: "task-decomposition"
description: "Use to break down a complex engineering task into smaller, manageable sub-tasks. Useful for planning implementation of a large feature."
---
When faced with a complex task, decompose it using the following methodology:

1.  **Identify the Goal:** What is the final, user-visible outcome?
2.  **List Major Components:** What are the high-level pieces? (e.g., UI, API, Database).
3.  **Deconstruct Each Component:**
    *   **Inputs:** What data or triggers does this component need?
    *   **Outputs:** What does it produce?
    *   **Dependencies:** What other components must exist first?
    *   **Steps:** What are the discrete implementation steps within this component?
4.  **Sequence the Steps:** Arrange all steps into a dependency graph or a numbered list.
5.  **Identify Parallelizable Work:** Group independent tasks that can be worked on simultaneously.
