# Tutorial: Implementing Containers (Loot Chests) in TestAdv

This tutorial guides you through creating interactive containers (chests, bags, crates) that function within our `TestAdv` system. While Evennia has a "Containers Contrib," we will build a custom version to ensure it integrates perfectly with our specific features (like `size` attributes and the `EquipmentHandler`).

## 1. The Concept

A **Container** is just an Object that:
1.  Can hold other objects (which all Evennia objects can do by default).
2.  Can be **opened** or **closed**.
3.  Hides its contents when closed.
4.  Limits what you can put inside based on **Capacity** (Slots).

## 2. The Typeclass (`testadv/objects.py`)

We need a class that tracks whether it is open and how much it can hold.

### Key Logic:
*   **`at_object_creation`**: We set a special lock called `view` logic. If the container is closed, people shouldn't be able to see the *contents* (though they can see the container itself). Evennia handles this via the `get_from` lock type, but we also want to hide the contents list in descriptions.

```python
# Add this to testadv/objects.py

class TestAdvContainer(TestAdvObject):
    """
    An object that can hold other objects.
    """
    obj_type = ObjType.GEAR # Or a new ObjType.CONTAINER
    
    # Capacity in 'slots' (sum of size of items inside)
    capacity = AttributeProperty(10, autocreate=False)
    
    # State
    is_open = AttributeProperty(False, autocreate=False)

    def at_object_creation(self):
        super().at_object_creation()
        # By default, containers are closed.
        self.db.is_open = False
        # Locks:
        # get_from: Who can take things OUT? Only if open.
        # put: Who can put things IN? Only if open.
        self.locks.add("get_from:is_open();put:is_open()")

    def at_desc(self, looker=None, **kwargs):
        """
        Called when looking at the object. We add the contents list if open.
        """
        desc = super().get_display_desc(looker, **kwargs)
        
        if not self.db.is_open:
            desc += "\n\nIt is closed."
        else:
            desc += "\n\n|wContents:|n"
            contents = self.contents
            if not contents:
                desc += "\n  (Empty)"
            else:
                for obj in contents:
                    desc += f"\n  {obj.key}"
        return desc

    # Helper for lock checking
    def check_open(self, accessing_obj, **kwargs):
        return self.db.is_open
```

> **Note:** We need to register the `is_open` lock function in `server/conf/lockfuncs.py` for `get_from:is_open()` to work! (See Section 5).

## 3. The Commands (`commands/mycommands.py`)

We need three commands: `open`, `close`, and `put`. (`get` usually handles `get x from y` already, but we might need to tweak it).

### CmdOpen & CmdClose

```python
class CmdOpen(default_cmds.MuxCommand):
    """
    Open a container.
    
    Usage:
      open <obj>
    """
    key = "open"
    
    def func(self):
        obj = self.caller.search(self.args)
        if not obj: return
        
        if not hasattr(obj, "is_open"):
            self.caller.msg("You can't open that.")
            return
            
        if obj.db.is_open:
            self.caller.msg(f"{obj.key} is already open.")
            return
            
        obj.db.is_open = True
        self.caller.msg(f"You open {obj.key}.")
        # Optional: Echo to room
        self.caller.location.msg_contents(f"{self.caller.key} opens {obj.key}.", exclude=self.caller)

class CmdClose(default_cmds.MuxCommand):
    """
    Close a container.
    
    Usage:
        close <obj>
    """
    key = "close"
    
    def func(self):
        obj = self.caller.search(self.args)
        if not obj: return

        if not hasattr(obj, "is_open"):
            self.caller.msg("You can't close that.")
            return

        if not obj.db.is_open:
            self.caller.msg(f"{obj.key} is already closed.")
            return

        obj.db.is_open = False
        self.caller.msg(f"You close {obj.key}.")
```

### CmdPut (Moving items IN)

This is where we enforce the `capacity` limit.

```python
class CmdPut(default_cmds.MuxCommand):
    """
    Put an object into a container.
    
    Usage:
      put <obj> in <container>
    """
    key = "put"
    
    def func(self):
        if not self.args or " in " not in self.args:
            self.caller.msg("Usage: put <obj> in <container>")
            return
            
        obj_name, container_name = self.args.split(" in ", 1)
        
        # Search for both
        container = self.caller.search(container_name)
        if not container: return
        
        obj = self.caller.search(obj_name)
        if not obj: return
        
        # 1. Check if container IS a container
        if not hasattr(container, "capacity"):
            self.caller.msg(f"You can't put things in {container.key}.")
            return
            
        # 2. Check if open (using the lock we set on the typeclass)
        if not container.access(self.caller, "put"):
            self.caller.msg(f"{container.key} is closed.")
            return
            
        # 3. Check Capacity
        current_size = sum(o.size for o in container.contents if hasattr(o, 'size'))
        if current_size + obj.size > container.capacity:
            self.caller.msg(f"{container.key} is too full.")
            return
            
        # 4. Move logic
        # If we were holding it, we might need to remove from EquipmentHandler?
        # Standard .move_to() handles location, but EquipmentHandler needs 'remove' call if equipped.
        
        # Check if equipped
        if hasattr(self.caller, "equipment") and obj in self.caller.equipment.all_objects():
             self.caller.equipment.remove(obj)
             
        # Perform move
        if obj.move_to(container, quiet=True):
            self.caller.msg(f"You put {obj.key} in {container.key}.")
        else:
            self.caller.msg("You can't put that there.")
```

## 4. The `Get` Command issue

Evennia's default `CmdGet` handles `get <obj> from <container>`.
It checks the `get_from` lock on the container.
Since we added `self.locks.add("get_from:is_open()")` to our `TestAdvContainer`, the default `get` command should *automatically* respect our open/closed state!

## 5. Registering the Lock Function

For `is_open()` to work in a lock definition, we must tell Evennia what `is_open()` means.

1.  Open `server/conf/lockfuncs.py`.
2.  Add:

```python
def is_open(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Returns True if the accessed_obj is open.
    """
    if hasattr(accessed_obj, "db") and accessed_obj.db.is_open:
        return True
    return False
```

## Summary of Implementation Steps

1.  **Modify `server/conf/lockfuncs.py`**: Add the `is_open` check.
2.  **Modify `testadv/objects.py`**: Add `TestAdvContainer` class.
3.  **Modify `commands/mycommands.py`**: Add `CmdOpen`, `CmdClose`, `CmdPut`.
4.  **Register Commands**: Add to `MyCmdSet` (and default cmdset).
5.  **Test**: Spawn a container, try to use it.
