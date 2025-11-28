# Design Doc: The Department of Liquidation
**Builder:** Fargo
**Zone Size:** ~15 Rooms
**Theme:** Liminal Office Horror meets Dungeon Crawler.
**Setting:** A "glitched" sector of Tess where an extradimensional office complex has merged with a sewer system.

## 1. Concept & Vibe
*   **Visuals:** Water-stained drop ceilings, flickering fluorescent tubes, endless beige hallways that smell like ozone and wet dog.
*   **Audio:** A constant, maddening hum. Occasional distant phones ringing that never stop.
*   **Gameplay:** A "rat maze" feel. You're trying to find the Manager's Office to get your "severance package" (loot), but the layout fights you.

## 2. Room Layout (The Map)

It's a "U" shape, mostly, but with a nasty loop in the middle.

1.  **The Waiting Room** (Entry)
2.  **Corridor A** (Standard Room)
3.  **The Break Room** (Weapon Rack - "The Kitchenette")
4.  **Corridor B** (Weather Room - "The Sprinkler Zone")
5.  **Cubicle Farm** (Teleport Puzzle - "The Maze")
6.  **The Server Closet** (Dark Room)
7.  **Ventilation Shaft** (Hidden Exit / Bridge Room mechanics)
8.  **Executive Antechamber** (Mob Patrol Area)
9.  **The Manager's Office** (Boss/Loot)
10. **The Fire Escape** (Exit back to Tess)
11-15. **Various Filler Corridors** (Copy-pasted descriptions because *aesthetic*).

## 3. Feature Implementation Plan (The "Expo")

Here's how I'm hitting those checkmarks from the `g3` guide.

### 3.1. Weapon Rack (`TutorialWeaponRack`)
*   **Location:** **The Break Room**
*   **Object:** "The Lost & Found Box"
*   **Description:** A cardboard box labeled 'DO NOT TOUCH' in Sharpie. It smells like old pennies.
*   **Loot:** `["plastic sword", "stapler gun", "heavy clipboard"]`
*   **Fargo Note:** I love that the guide lets me set a "no more weapons" message. I'm setting it to *"The box is empty. Someone stole the good stuff."*

### 3.2. Readable Object (`TutorialReadable`)
*   **Location:** **The Waiting Room**
*   **Object:** "Sticky Note"
*   **Text:** *"THE BEATINGS WILL CONTINUE UNTIL MORALE IMPROVES. ALSO, THE COFFEE MACHINE IS MIMIC. - MGMT"*
*   **Implementation:** Simple `@create/drop`, lock it down so they can't take my lore.

### 3.3. Climbable Object & Hidden Exit (`TutorialClimbable`)
*   **Location:** **Corridor A**
*   **Object:** "Teetering File Cabinet"
*   **Description:** A tower of metal drawers, rusted shut.
*   **Action:** Climbing it tags the player with `climbed_cabinet`.
*   **Hidden Exit:** A vent grate near the ceiling that opens into **The Server Closet**. The exit will be locked with `view:tag(climbed_cabinet, tutorial_world)`.

### 3.4. Dark Room & Light Source (`DarkRoom` & `LightSource`)
*   **Location:** **The Server Closet**
*   **Mechanic:** You can't see squat in here.
*   **Light Source:** Found in **The Break Room** (on a table, separate from the rack).
*   **Object:** "Glow Stick" (It flickers, obviously).
*   **Description:** "A cracked chemical light. It hums aggressively."

### 3.5. Weather Room (`WeatherRoom`)
*   **Location:** **Corridor B**
*   **Concept:** The fire sprinklers are malfunctioning.
*   **Messages:**
    *   *"Oily water drips onto your neck."*
    *   *"The carpet squelches loudly."*
    *   *"A ceiling tile dissolves into gray mush."*
    *   *Fargo Note:* This is that "decay" vibe I was talking about.

### 3.6. Bridge Room (`BridgeRoom`)
*   **Location:** **Ventilation Shaft**
*   **Concept:** You're crawling over a flimsy plastic duct. It takes time to cross.
*   **Fall Exit:** If they fall, they drop into **The Cubicle Farm** (start of the maze).
*   **Flavor:** *"The plastic creaks under your weight. Don't look down."*

### 3.7. Teleport Puzzle (`TeleportRoom`)
*   **Location:** **Cubicle Farm**
*   **Concept:** Endless rows of gray fabric walls.
*   **Puzzle:** You need to find the "Employee ID" (a tag or object) to pass through to **The Executive Antechamber**.
*   **Failure:** If you don't have the ID, trying to leave teleports you back to **The Waiting Room**.
*   **Message:** *"Security restriction. Please return to the reception area."*

### 3.8. Active Mob (`Mob`)
*   **Location:** **Executive Antechamber**
*   **Name:** "The Shift Supervisor"
*   **Description:** A suit of armor made entirely of recycled printer parts and jagged metal. It has no face.
*   **Behavior:** Patrolling (`@set .../patrolling = True`), Aggressive (`True`).
*   **Weapon:** "Red Tape" (It's a whip).

## 4. Why This Works
It respects the "Sword & Sandal" tropes (you have a dungeon, a weapon rack, a boss) but skins it in that weird, uncomfortable "backrooms" texture. Plus, I can reuse the description "A beige hallway with a flickering light" for like, 5 rooms and claim it's a "disorientation mechanic."

Work smart, not hard.
