#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        return psycopg2.connect("dbname=tournament")
    except Exception, e:
        raise e

def commitAndCloseConnect(c):
    c.commit()
    c.close()


def deleteMatches():
    """Remove all the match records from the database."""
    connection = connect()
    c = connection.cursor()
    c.execute("DELETE FROM result;")
    c.execute("DELETE FROM match;")
    commitAndCloseConnect(connection)

def deletePlayers():
    """Remove all the player records from the database."""
    connection = connect()
    c = connection.cursor()
    c.execute("DELETE FROM player;")
    commitAndCloseConnect(connection)


def deleteTournaments():
    """Remove all tournament records from the database."""
    connection = connect()
    c = connection.cursor()
    c.execute("DELETE FROM tournament;")
    commitAndCloseConnect(connection)


def countPlayers():
    """Returns the number of players currently registered."""
    connection = connect()
    c = connection.cursor()
    c.execute("SELECT COUNT(*) from player;")
    players = c.fetchone()[0]
    connection.close()
    return players


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    connection = connect()
    c = connection.cursor()
    c.execute("INSERT INTO player (name) values (%s);", (bleach.clean(name),))
    commitAndCloseConnect(connection)


def createTournament(name):
    """Adds a tournament to the tournament database.
    The database assigns a unique serial id number for the tournament.
    Args:
    name: the name of the tournament (need not be unique)
    Return:
    ID of the created tournament
    """
    connection = connect()

    cursor = connection.cursor()
    cursor.execute("""insert into tournament (name)
                    values(%s) returning id;""", (bleach.clean(name),))
    tournament_id = cursor.fetchone()[0]
    commitAndCloseConnect(connection)
    return tournament_id


def playerStandings(tournament):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player
    in first place, or a player tied for first place
    if there is currently a tie.

    Args:
      tournament: the id of the tournament

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    connection = connect()
    c = connection.cursor()
    c.execute("""SELECT player_id, player_name, wins, ties, matches
        FROM standings where tournament_id=%s""", (bleach.clean(tournament),))
    standings = c.fetchall()
    connection.close()
    return standings


def reportMatch(t, p1, p2, w):
    """Records the outcome of a single match between two players.

    Args:
      t: the id of the tournament
      p1: the id of player1
      p2: the id of player2
      w:  the id number of the player who won
    """
    connection = connect()
    c = connection.cursor()
    c.execute(
        """
        insert into match (tournament_id, player1, player2)
        values(%(tournament)s, %(player1)s, %(player2)s)
        returning id;
        """,
        {'tournament': bleach.clean(t), 'player1': bleach.clean(p1), 'player2': bleach.clean(p2)})
    match_id = c.fetchone()[0]
    if w:
        c.execute("""
                insert into result (match_id, winner)
                values(%(match_id)s, %(winner)s);
                """, {'match_id': bleach.clean(match_id), 'winner': bleach.clean(w)})
    commitAndCloseConnect(connection)


def swissPairings(tournament):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
      tournament: the id of the tournament

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    connection = connect()
    c = connection.cursor()
    #
    # Get player id, player name, and player byes
    # from player standings and opponent standings
    # where tournament is referenced in both
    # player standings and opponent standings
    # and  player id is equal to opponent id
    # store into a variable 'standings'
    c.execute(
        """
        select p.player_id, p.player_name, p.byes
        from standings p, opponent_standings o
            where p.tournament_id=%s
                and p.tournament_id=o.tournament_id
                and p.player_id=o.player_id
        order by p.wins, p.losses desc, o.wins, o.losses desc
        """,
        (tournament,))
    standings = c.fetchall()
    match = ()
    matches = []    
    # if the length of standings is divisble
    # by 2 and not equal to zero, then
    # no bye is needed at this time
    bye_needed = len(standings) % 2 != 0
    for player in standings:
        if bye_needed and player[2] == 0:
            matches.append(player[0:2] + (None, None))
        else:
            match = match + player[0:2]
            if len(match) == 4:
                matches.append(match)
                match = ()
    connection.close()
    return list(set(matches))