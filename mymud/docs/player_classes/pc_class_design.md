# Player Class System Design

## 1. Overview
A flexible "Job System" that allows players to mix and match classes to create unique builds. Players start with a single Basic Class but eventually gain the ability to swap classes and equip a Secondary Class (Sub-Job).

## 2. Structure & Slots

### 2.1. Primary Class (Main Job)
*   **Function:** The active class that determines the character's core level and receives all Experience Points (XP).
*   **Level Cap:** 100.
*   **Benefits:** Full access to all abilities and traits of the class up to the current level.

### 2.2. Secondary Class (Sub-Job)
*   **Function:** An equipped support class that augments the Primary Class.
*   **Level Cap:** Restricted to **1/2** of the Primary Class's current level (e.g., a Lv.100 Warrior / Lv.50 Mage). If the Primary Class is Level 30, the Secondary Class is capped at Level 15, even if the player has leveled it higher previously.
*   **XP:** The Secondary Class **never** gains XP. To level it up, the player must swap it to the Primary slot.
*   **Benefits:** Access to abilities and passive traits, subject to the reduced level cap.

## 3. Progression Stages

1.  **Novice (The Beginning):**
    *   Player selects one of the **6 Basic Classes**.
    *   Locked to this class. No swapping, no secondary slot.

2.  **Journeyman (The Awakening):**
    *   **Unlock Condition:** Reaching a specific milestone (e.g., Level 10) or completing a tutorial quest.
    *   **Feature:** Ability to **Swap** Primary Class at a sanctuary/mog house.
    *   *Design Note:* Encourages trying other basic classes early.

3.  **Master (The Dual-Class):**
    *   **Unlock Condition:** A significant quest line (The "Sub-Job Quest").
    *   **Feature:** Unlocks the **Secondary Class Slot**.

## 4. Advanced Classes

Beyond the 6 Basic Classes, players can unlock prestige jobs (Advanced Classes) through gameplay.

### 4.1. Unlock Mechanisms
Unlike basic classes, these are not available at creation. Unlocking them requires specific narrative triggers:
*   **NPC Trainers:** Locating a reclusive master in the world.
*   **Drive Prerequisites:** The character must possess specific Drives (from the Drives System) to prove their mindset aligns with the class.
    *   *Example:* Unlocking *Berserker* might require the *Obsession with Blood* Drive.
*   **Quest/Item Checks:** Traditional fetch quests or possession of a key artifact.

### 4.2. Availability
Once unlocked, an Advanced Class is added to the player's "Job Wheel" and can be equipped as either a Primary or Secondary class just like the basic ones.

## 5. Design Goals
*   **Horizontal Progression:** Players never "finish" leveling; there is always another class to level up to support their main build.
*   **Synergy:** The system rewards finding clever combinations of Primary and Secondary class abilities.
*   **Narrative Integration:** Unlocking classes isn't just a menu option; it's a roleplaying milestone tied to the world and the character's internal Drives.
