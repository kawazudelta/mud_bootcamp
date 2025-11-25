# System Design: Character Drives

## 1. Overview
The **Drives System** introduces a dynamic, behavioral progression mechanic. Similar to equipment, characters possess four distinct "slots" for Drives. However, unlike standard gear, Drives are generated organically based on a character's actions and experiences within the game world.

## 2. Core Mechanics

### 2.1. Drive Categories (Feelings)
There are four primary categories of Drives, corresponding to the four equippable slots:
1.  **Obsession**
2.  **Yearning**
3.  **Resentment**
4.  **Fear**

**Acquisition:**
Character actions contribute to hidden progress bars for these Feelings.
*   **Fear:** Fleeing combat, being ambushed.
*   **Resentment:** Taking damage from enemies.
*   *(Implied/TBD: Actions triggering Obsession and Yearning)*

### 2.2. Drive Subjects (Focuses)
Simultaneously, the system tracks "Focus" progress bars based on interactions with specific elements or creature types.
*   **Fire:** Lighting torches, using fire-based items.
*   **Vermin:** Killing or eating rats.
*   **Blood:** Eating blood sausage, stabbing enemies (causing bleeding).

### 2.3. Drive Generation
A complete Drive is formed when a character maxes out both a **Feeling** bar and a **Focus** bar.
*   **Trigger:** The new Drive is realized the next time the character rests.
*   **Examples:** *Fear of Fire*, *Obsession with Vermin*, *Yearning for Blood*.
*   **Player Feedback:** Progress is largely hidden ("black box"). Players may receive vague narrative hints (e.g., "You feel ready to develop a Yearning," or "You have been thinking about Rats a lot lately").

## 3. Inventory & Management

### 3.1. Equipping
*   **Automatic:** When a Drive is generated, it automatically fills the corresponding Feeling slot if it is empty.
*   **Conflict:** If a slot is already filled (e.g., the character already has an *Obsession*), the player must choose between the existing Drive and the new one. This requires explicit confirmation (e.g., typing the name of the Drive to keep).

### 3.2. Removal
*   **Restricted:** Drives cannot be unequipped or swapped freely like standard gear.
*   **Specialized Removal:** Removing an unwanted Drive likely requires a specialized NPC or specific in-game service.

## 4. Gameplay Effects

### 4.1. Experience & Progression
Drives provide unique, contextual triggers for gaining Experience Points (XP) or Skill Points.
*   **Fear of Fire:** Gain XP for fleeing from flaming enemies.
*   **Obsession with Fire:** Gain bonus XP for fighting while carrying a torch or wielding a flaming weapon.

### 4.2. Stats & Recovery
Drives serve as a major modifier for core vitality and motivation stats.
*   **Primary Benefit:** Bonus HP and increased Healing Recovery.
*   **Secondary Potential:** Bonuses to Mana Points (MP) or Stamina Points (SP).
*   **Traditional Bonuses:** Where appropriate, Drives may also confer standard equipment bonuses (e.g., +Dodge, +Stat).

### 4.3. Class Unlocks
Specific Drives or combinations of Drives can serve as prerequisites for unlocking Advanced Classes.
*   **Mischief Mane:** Requires *Resentment of Poison* AND *Obsession with Rats*.
*   **Draconymus:** Requires *Yearning for Dragons* AND *Fear of Dragons*.
