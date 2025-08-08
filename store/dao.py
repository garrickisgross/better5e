import sqlite3
from uuid import UUID
from typing import List

from store.game_obj import GameObject

DB = "better5e_v1.db"

def get_db_connection():
    """Create a new database connection."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_game_object_by_id(object_id: UUID) -> GameObject: 
    """Retrieve a game object by its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM game_objects WHERE id = ?", (str(object_id),))
        row = cursor.fetchone()
        if row:
            return GameObject(
                id=UUID(row['id']),
                name=row['name'],
                type=row['type'],
                data=row['data']
            )
        else:
            raise ValueError(f"GameObject with ID {object_id} not found.")
        
def get_all_by_type(object_type: str) -> List[GameObject]:
    """Retrieve all game objects of a specific type."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM game_objects WHERE type = ?", (object_type,))
        rows = cursor.fetchall()
        return [
            GameObject(
                id=UUID(row['id']),
                name=row['name'],
                type=row['type'],
                data=row['data']
            )
            for row in rows
        ]
    
def insert_game_object(game_object: GameObject) -> None:
    """Insert a new game object into the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try: 
            cursor.execute(
                "INSERT INTO game_objects (id, name, type, data) VALUES (?, ?, ?, ?)",
                (str(game_object.id), game_object.name, game_object.type, game_object.data)
            )
        except sqlite3.IntegrityError as e:
            raise ValueError(f"GameObject with ID {game_object.id} already exists.") from e
        
        conn.commit()

def delete_game_object(object_id: UUID) -> None:
    """Delete a game object by its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM game_objects WHERE id = ?", (str(object_id),))
        conn.commit()

def update_game_object(game_object: GameObject) -> None:
    """Update an existing game object."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE game_objects SET name = ?, type = ?, data = ? WHERE id = ?",
            (game_object.name, game_object.type, game_object.data, str(game_object.id))
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"GameObject with ID {game_object.id} not found for update.")

class GameObjectDAO:
    """Data Access Object for GameObject."""
    
    def get_by_id(self, object_id: UUID) -> GameObject:
        """Retrieve a game object by its ID."""
        return get_game_object_by_id(object_id)
    
    def get_all_by_type(self, object_type: str) -> List[GameObject]:
        """Retrieve all game objects of a specific type."""
        return get_all_by_type(object_type)
    
    def insert(self, game_object: GameObject) -> None:
        """Insert a new game object into the database."""
        insert_game_object(game_object)

    def delete(self, object_id: UUID) -> None:
        """Delete a game object by its ID."""
        delete_game_object(object_id)
    
    def update(self, game_object: GameObject) -> None:
        """Update an existing game object."""
        update_game_object(game_object)
    
