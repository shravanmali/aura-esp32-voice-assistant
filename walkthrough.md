# Persistent Recipe Ingredient Memory & Adaptive Voice Guidance

This walkthrough explains how the voice assistant now **permanently remembers your ingredient limitations across all conversational turns** when guiding you through any recipe.

---

## 1. What Went Wrong Previously

When following a recipe:
1. You said: *"I don't have any garlic or ginger. I only have sugar, chai patti, milk and water."*
2. The assistant acknowledged it on that single turn.
3. But on the **very next turn** when you asked *"What is the next step?"* or said *"Next"*, the assistant went right back to the static hardcoded Masala Chai recipe that assumed you had ginger and cardamom!
4. It had amnesia about what you told it, because the recipe state was not storing your available ingredients, and the step advancer was pulling from the static dictionary instead of generating customized steps!

---

## 2. How the Persistent Memory Engine Works

```
                     [User Declares Ingredients]
                     "I only have sugar, chai patti, milk, water"
                                  │
                                  ▼
                ┌───────────────────────────────────┐
                │ Lock into active_briefing:        │
                │ - user_constraints = "{inventory}"│
                │ - source = "custom"               │
                └─────────────────┬─────────────────┘
                                  │
                                  ▼
             ┌─────────────────────────────────────────┐
             │ When user says "Next" / "Aage" / "What next"│
             └────────────────────┬────────────────────┘
                                  │
               ┌──────────────────┴──────────────────┐
               ▼                                     ▼
        source == "deterministic"             source == "custom"
        (Static 0ms dictionary)              (Dynamic Groq with Constraints)
                                             • Strictly uses ONLY declared items
                                             • NEVER mentions ginger/garlic/cardamom
                                             • Injects [CRITICAL ACTIVE CONSTRAINTS]
                                               directly into system prompt!
```

---

## 3. Verified Multi-Turn Dialogue

````carousel
```text
User: "How to make a tea?" (4.1 ms)
Assistant: "Yes, I know how to make fragrant Adrak Elaichi Masala Chai! Shall we start with boiling water and crushed spices?"
```
<!-- slide -->
```text
User: "I don't have any garlic or ginger. I only have sugar, chai patti, milk and water." (736 ms)
Assistant: "No problem! Simple chai is delicious. Boil one cup of water in a saucepan."
```
<!-- slide -->
```text
User: "What is the next step?" (1416 ms)
Assistant: "Add your chai patti to the boiling water."
(Note: ZERO mention of garlic, ginger, or cardamom!)
```
<!-- slide -->
```text
User: "Next" (802 ms)
Assistant: "Add sugar and milk to the pot, then let it simmer gently for two minutes."
(Note: Uses ONLY sugar and milk!)
```
<!-- slide -->
```text
User: "Repeat that" (419 ms)
Assistant: "Add sugar and milk to the pot, then let it simmer gently for two minutes."
```
````

---

## 4. Live Server Daemon Status

The server daemon is online and operational:
- **Task ID:** `task-8282`
- **Dashboard:** `http://localhost:8080`
- **ESP32 Connection:** Active at `192.168.31.200:6053`
