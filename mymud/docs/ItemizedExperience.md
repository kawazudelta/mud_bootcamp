# Itemized Experience System Design

This document outlines the design and implementation plan for the "Itemized Experience" feature in TessMUD, which includes equippable Obsessions, Yearnings, Resentments, and Fears.

## Core Concept

Characters will develop and equip experiences based on their actions. These experiences provide buffs, penalties, and new triggers for XP/skill gains. The system will be dynamic, with a future goal of LLM-generated unique experiences.

## Scalability: Tag-Based System

To ensure scalability and maintainability, especially for "feeling objects" (e.g., Fire, Vermin, Blood), a tag-based system will be implemented.

*   **Objects Have Tags:** In-game objects (NPCs, items, rooms) will be assigned descriptive tags (e.g., `fire`, `vermin`, `blood`, `insect`).
*   **Central Ruleset:** A single, central ruleset will define how actions interacting with these tags translate into progress points for character experiences.

## Phased Implementation Plan

### Phase 1: The Core Data Model & Manual Generation

**Objective:** Establish the fundamental data structures for experiences and character tracking.

1.  **Character Attributes (`typeclasses/characters.py`):**
    *   **Experience Slots:** Four attributes to hold the currently "equipped" Obsession, Yearning, Resentment, and Fear.
    *   **Progress Trackers:** A dictionary-like attribute (e.g., `db.experience_progress = {'fear': 15, 'obsession': 22, ...}`) to store points for the four experience *types*.
    *   **Object Trackers:** A similar attribute (e.g., `db.object_points = {'fire': 5, 'vermin': 50, ...}`) to store points for the *objects* of these feelings, based on the tag system.

    **Proposed Implementation:**

    The following code should be added to the `Character` class in `typeclasses/characters.py`. This initializes the necessary attributes when a character is first created.

    ```python
    from evennia.objects.objects import DefaultCharacter
    from .objects import ObjectParent
    import random

    class Character(ObjectParent, DefaultCharacter):
        """
        The Character class represents a character entity in-game.
        """

        def at_object_creation(self):
            """
            Called when the object is first created. This sets up
            the experience tracking attributes.
            """
            super().at_object_creation()

            # --- Experience System Attributes ---

            # Slots for equipped experiences
            self.db.obsession_slot = None
            self.db.yearning_slot = None
            self.db.resentment_slot = None
            self.db.fear_slot = None

            # Progress trackers for experience types (e.g., Fear, Obsession)
            # The value is the current progress points.
            self.db.experience_progress = {
                'obsession': 0,
                'yearning': 0,
                'resentment': 0,
                'fear': 0
            }

            # Progress trackers for feeling objects (e.g., Fire, Vermin)
            # The key is the tag, the value is the current progress points.
            self.db.object_points = {}

            # --- End Experience System Attributes ---

            # Example base stats
            self.db.strength = random.randint(3, 18)
            self.db.dexterity = random.randint(3, 18)
            self.db.intelligence = random.randint(3, 18)

        def at_pre_move(self, destination, **kwargs):
            '''
            Called before a character moves.
            '''
            if self.db.is_sitting:
                self.msg("You need to stand up first.")
                return False
            return True
    ```

2.  **Experience Typeclass (`typeclasses/experiences.py`):**
    *   A new `Experience` typeclass will be created.
    *   **Attributes:**
        *   `name` (e.g., "Fear of Fire")
        *   `desc` (description)
        *   `effects` (dictionary of mechanical effects, e.g., `{'stat_bonus': {'dexterity': 5}}`)
        *   `experience_type` (e.g., "Fear", "Obsession")
        *   `object_tag` (e.g., "Fire", "Vermin")
        *   `xp_triggers` (conditions for bonus XP/skill gains)

    **Proposed Implementation:**

    A new file should be created at `typeclasses/experiences.py` with the following content. This defines the base object for all equippable experiences.

    ```python
    """
    This file defines the Experience typeclass, which represents equippable
    Obsessions, Yearnings, Resentments, and Fears for characters.
    """

    from evennia.objects.objects import DefaultObject

    class Experience(DefaultObject):
        """
        This typeclass represents an equippable experience.
        It stores its name, description, mechanical effects, and the
        type/tag it's associated with.
        """
        def at_object_creation(self):
            """
            Called when the object is first created.
            """
            super().at_object_creation()
            self.db.desc = "A nascent feeling, shaping your very being."

            # A dictionary defining the mechanical effects.
            # Example: {'stat_bonus': {'strength': -1}, 'skill_bonus': {'athletics': 5}}
            self.db.effects = {}

            # The type of experience, e.g., "Fear", "Obsession"
            self.db.experience_type = ""

            # The tag this experience is associated with, e.g., "Fire", "Vermin"
            self.db.object_tag = ""

            # A dictionary defining custom XP gain triggers.
            # Example: {'on_flee': {'target_tag': 'fire', 'xp_gain': 10}}
            self.db.xp_triggers = {}

        def __str__(self):
            return self.name
    ```

3.  **Manual Commands (Temporary):**
    *   Admin-level commands to manually grant progress points and create/equip experiences for testing.

### Phase 2: Action-Based Progress Tracking

**Objective:** Integrate player actions with the experience tracking system using the tag-based approach.

1.  **Central Ruleset (`world/experience_rules.py`):**
    *   A new Python module to define the `OBJECT_POINT_MAP` dictionary.
    *   **Structure:** `OBJECT_POINT_MAP = { ("action_verb", "object_tag"): points_value }`
    *   **Examples:**
        ```python
        OBJECT_POINT_MAP = {
            ("kill", "vermin"): 5,
            ("eat", "vermin"): 10,
            ("light", "fire"): 1,
            ("wield", "fire"): 2,
            ("eat", "blood"): 1,
            ("spill", "blood"): 10,
            ("observe", "insect"): 1,
        }
        ```

    **Proposed Implementation:**

    A new file should be created at `world/experience_rules.py` with the following content. This file will act as the central, easily editable ruleset for how actions and tags interact to generate experience points.

    ```python
    """
    This module defines the central ruleset for the Itemized Experience system.
    It maps actions and object tags to point values.
    """

    # This dictionary maps a tuple of (action, tag) to the number of points
    # a character should receive for their object_points tracker.
    #
    # The 'action' is a verb representing what the character did.
    # The 'tag' is a string tag attached to the object being interacted with.
    #
    # This central location makes it easy to add new interactions and balance
    # point values without changing any game code.

    OBJECT_POINT_MAP = {
        # Action: "kill"
        ("kill", "vermin"): 5,
        ("kill", "animal"): 2,
        ("kill", "humanoid"): 10,
        ("kill", "undead"): 3,

        # Action: "eat"
        ("eat", "vermin"): 10,
        ("eat", "food"): 1,
        ("eat", "blood"): 2,

        # Action: "wield" / "use"
        ("wield", "fire"): 2,
        ("light", "fire"): 1,
        ("wield", "holy"): 3,

        # Action: "spill" / "cause_bleeding"
        ("spill", "blood"): 10,

        # Action: "observe" / "witness"
        ("observe", "insect"): 1,
        ("observe", "beautiful"): 1,
        ("observe", "celestial"): 5,

        # Action: "flee"
        ("flee", "fire"): 3, # Gain 'fire' points when fleeing from a 'fire' tagged enemy
        ("flee", "undead"): 2,
    }
    ```

2.  **Modify Existing Commands:**
    *   Update relevant game commands (e.g., combat, item interaction) to:
        *   Identify the action performed (e.g., "kill", "light").
        *   Retrieve tags from the involved objects.
        *   Look up the action-tag pair in `OBJECT_POINT_MAP`.
        *   Award corresponding points to the character's `db.object_points` and `db.experience_progress` attributes.

3.  **Implement "Rest" Logic:**
    *   Modify or create a `rest` command.
    *   When a character rests, this command will:
        *   Check if any `experience_progress` and `object_points` bars are full.
        *   If so, generate a new `Experience` object (e.g., "Fear of Fire").
        *   Equip the new experience to the character.
        *   Reset the relevant progress bars.

### Phase 3: LLM Integration for Unique Experiences

**Objective:** Introduce dynamic, LLM-generated experiences based on player behavior.

1.  **Action Logging System:**
    *   Create a mechanism to log significant player actions and behaviors in a format suitable for LLM input.

2.  **LLM API Hook:**
    *   Develop a function to send character action logs to an LLM with a prompt to generate a unique experience (name, description, effects, XP triggers).

3.  **Experience Creation from LLM Output:**
    *   Implement logic to parse the LLM's response and instantiate a new `Experience` typeclass object with the generated details.
