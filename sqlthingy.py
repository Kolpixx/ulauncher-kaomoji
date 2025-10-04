# Followed this tutorial cuz I have no idea how to do this: https://www.freecodecamp.org/news/work-with-sqlite-in-python-handbook/

import sqlite3
import json

# Connect to database (or create one if it doesn't exist yet) and automatically close it once it's done
with sqlite3.connect("kaomojis.sqlite") as connection:
    # Cursor object to interact with the databse
    cursor = connection.cursor()
    print(f"Succesfully connected to Kaomoji database with SQL version {sqlite3.sqlite_version}!! :3")

    # Create table (basic structure)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS Kaomojis (
        kaomoji TEXT NOT NULL,
        keywords TEXT NOT NULL
    );
    """

    # Execute the create_table_query SQL command
    cursor.execute(create_table_query)

    # Uh, loop through  all kaomojis in the kaomoji JSON file and add them to the database (yay!)
    with open("kaomojis.json") as file:
        kaomojiJSON = json.load(file)
        print(kaomojiJSON)

        for kaomoji in kaomojiJSON["kaomojis"]:
            kaomojiText = kaomoji["text"]
            kaomojiKeywords = kaomoji["keywords"]

            # Insert a Kaomoji record into Kaomojis table
            insert_query = """
            INSERT INTO Kaomojis (kaomoji, keywords)
            VALUES (?, ?)
            """

            kaomoji_data = (kaomojiText, kaomojiKeywords)

            # Execute insert_entries SQL command
            cursor.execute(insert_query, kaomoji_data)

            print(f"Added: {kaomojiText} with following keywords: {kaomojiKeywords}")

    # Commit the CHANGES WHOAAAA
    connection.commit()

    # Confirmation messages
    print('Successfully created table ("Kaomojis"), yippie!')