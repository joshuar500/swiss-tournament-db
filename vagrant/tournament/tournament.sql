-- Table definitions for the tournament project.


-- Create table 'player'
-- example:
-- ---------------------
-- |  id  |     name   |
-- ---------------------
-- |   1  |   Josh R   |
-- ---------------------
-- |   2  |   Matt B   |
-- ---------------------
-- |   3  |   Dave L   |
-- ---------------------
-- |   4  |  George P  |
-- ---------------------
CREATE TABLE player(
    id serial PRIMARY KEY,
    name text NOT NULL
);


-- Create table 'tournament'
-- example:
-- -----------------------------
-- |  id  |        name        |
-- -----------------------------
-- |   1  |   ALLSTAR TOURNY   |
-- -----------------------------
-- |   2  |  QUALIFIERS 2015   |
-- -----------------------------
-- |   3  |   KICKASS MAJORS   |
-- -----------------------------
CREATE TABLE tournament (
    id serial PRIMARY KEY,
    name text NOT NULL
);


-- Create table 'match'
-- tournament_id references the table 'tournament' primary key
-- player1 and player2 reference the table 'player' primary key
-- example:
-- --------------------------------------------
-- |  id  | tournament_id | player1 | player2 |
-- --------------------------------------------
-- |   3  |       3       |     1   |    3    |  
-- --------------------------------------------
-- id is the primary key
-- tournament_id references KICKASS MAJORS in the 'tournament' table
-- player1 references the primary key (id) for Josh R
-- player2 references the primary key (id) for Dave L
-- the CONSTRAINT makes sure the players do not compete with themselves
CREATE TABLE match (
    id serial PRIMARY KEY,
    tournament_id integer REFERENCES tournament(id) NOT NULL,
    player1 integer REFERENCES player(id) NOT NULL,
    player2 integer REFERENCES player(id) NOT NULL,
    CONSTRAINT not_same CHECK (player1!=player2)
);


-- Create table 'result'
-- example:
-- -----------------------
-- | match_id |  winner  |
-- -----------------------
-- |     1    |     3    |
-- -----------------------
-- |     2    |     1    |
-- -----------------------
-- match_id references the primary key (id) of 'match'
-- winner references the primary key (id) in 'player'
CREATE TABLE result (
    match_id integer REFERENCES match(id) NOT NULL,
    winner integer REFERENCES player(id) NOT NULL    
);


-- Create view 'standings'
-- example:
-- -----------------------------------------------------------------------------------
-- | tournament_id | player_id | player_name | matches | wins | losses | ties | byes |
-- -----------------------------------------------------------------------------------
-- |       1       |     3     |    Dave L   |    1    |   1  |    0   |   0  |   0  |
-- -----------------------------------------------------------------------------------
-- from the 'tournament' table, we use a cross join to get all player ids
-- we left join the match table to 
CREATE VIEW standings AS
    SELECT t.id AS tournament_id,
        p.id AS player_id,
        p.name AS player_name,
        count(m.*) AS matches,
        count(w.*) AS wins,
        count(l.*) AS losses,
        count(m.*)-(count(w.*)+count(l.*)) AS ties,
        count(b.*) AS byes
    FROM tournament t
        CROSS JOIN player p
        LEFT JOIN match m ON m.tournament_id=t.id AND p.id IN (m.player1, m.player2)
        LEFT JOIN result w ON w.match_id=m.id AND w.winner=p.id
        LEFT JOIN result l ON l.match_id=m.id AND l.winner!=p.id
        LEFT JOIN match b ON b.id=m.id AND b.player2 is NULL
    GROUP BY t.id, p.id;


-- Create view 'opponent_standings'
-- example:
-- ----------------------------------------------------
-- | tournament_id | player_id | wins | losses | ties |
-- ----------------------------------------------------
-- |       1       |     1     |   1  |    1   |   0  |
-- ----------------------------------------------------
CREATE VIEW opponent_standings AS
    SELECT t.id AS tournament_id,
        p.id AS player_id,
        sum(o.wins) AS wins,
        sum(o.losses) AS losses,
        sum(o.ties) AS ties
    FROM tournament t
        CROSS JOIN player p
        LEFT JOIN match m ON m.tournament_id=t.id AND p.id IN (m.player1, m.player2)
        LEFT JOIN standings o ON o.tournament_id=t.id AND o.player_id=case when p.id=m.player1 then m.player2 else m.player1 end
    GROUP BY t.id, p.id;