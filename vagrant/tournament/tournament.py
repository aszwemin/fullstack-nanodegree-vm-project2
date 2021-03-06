#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach
from contextlib import contextmanager


@contextmanager
def db_connection():
    """Context manager to simplify opening and closing connection
    in the below defined functions
    """
    connection = connect()
    cursor = connection.cursor()
    yield cursor, connection
    connection.close()


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    with db_connection() as (cursor, connection):
        cursor.execute("delete from matches;")
        connection.commit()


def deletePlayers():
    """Remove all the player records from the database."""
    with db_connection() as (cursor, connection):
        cursor.execute("delete from players;")
        connection.commit()


def countPlayers():
    """Returns the number of players currently registered."""
    with db_connection() as (cursor, connection):
        cursor.execute("select count(id) from players;")
        return cursor.fetchone()[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    with db_connection() as (cursor, connection):
        name = bleach.clean(name)
        cursor.execute("insert into players (name) values (%s);", (name,))
        connection.commit()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or
    a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    with db_connection() as (cursor, connection):
        cursor.execute("""
            select * from standings;
        """)
        return cursor.fetchall()


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    with db_connection() as (cursor, connection):
        cursor.execute("""
            insert into matches (winner_id, loser_id)
            values (%s, %s);
        """, (winner, loser))
        connection.commit()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    with db_connection() as (cursor, connection):
        cursor.execute("""
            select id, name, wins, matches from standings order by wins desc;
        """)
        standings = cursor.fetchall()
        # group query results into tuples of matched players
        result = []
        for counter in range(0, len(standings), 2):
            player1 = standings[counter]
            player2 = standings[counter + 1]
            result.append((player1[0], player1[1], player2[0], player2[1]))
        return result
