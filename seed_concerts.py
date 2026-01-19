import asyncio
import sqlite3
from datetime import datetime, timedelta

def seed_concerts():
    """Seed sample concerts to the database."""
    conn = sqlite3.connect('test_concert.db')
    cursor = conn.cursor()
    
    concerts = [
        {
            'name': 'Summer Festival 2026',
            'venue': 'Central Park',
            'date': (datetime.now() + timedelta(days=30)).isoformat(),
            'description': 'Annual summer music festival'
        },
        {
            'name': 'Jazz Night',
            'venue': 'Blue Note',
            'date': (datetime.now() + timedelta(days=15)).isoformat(),
            'description': 'Evening of smooth jazz'
        },
        {
            'name': 'Rock Concert',
            'venue': 'Madison Square Garden',
            'date': (datetime.now() + timedelta(days=45)).isoformat(),
            'description': 'Live rock music event'
        },
    ]
    
    for concert in concerts:
        try:
            cursor.execute('''
                INSERT INTO concerts (name, venue, date, description)
                VALUES (?, ?, ?, ?)
            ''', (concert['name'], concert['venue'], concert['date'], concert['description']))
        except sqlite3.IntegrityError:
            print(f"Concert '{concert['name']}' already exists")
    
    conn.commit()
    
    # Display all concerts
    cursor.execute('SELECT id, name, venue, date FROM concerts')
    rows = cursor.fetchall()
    print('\nSeeded Concerts:')
    for row in rows:
        print(f"  ID: {row[0]}, Name: {row[1]}, Venue: {row[2]}, Date: {row[3]}")
    
    conn.close()

if __name__ == '__main__':
    seed_concerts()
