--users
CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL
);

INSERT INTO Users (UserID, Name, Email, Password) VALUES
(1, 'Richard Yang', 'richard@example.com', 'pw_rich'),
(2, 'Alex Lim', 'alex@example.com', 'pw_alex'),
(3, 'TA Brian', 'brian@example.com', 'pw_brian'),
(4, 'Tung Sahur', 'tung@example.com', 'pw_tung'),
(5, 'David Goliath', 'david@example.com', 'pw_david'),
(6, 'Sophia Lee', 'sophia@example.com', 'pw_sophia'),
(7, 'Daniel Park', 'daniel@example.com', 'pw_daniel'),
(8, 'Olivia Garcia', 'olivia@example.com', 'pw_olivia'),
(9, 'Michael Myers', 'michael@example.com', 'pw_michael'),
(10, 'Lily Valley', 'lily@example.com', 'pw_lily');

--developers
CREATE TABLE Developers (
    DeveloperID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL
);

INSERT INTO Developers (DeveloperID, Name, Email, Password) VALUES
(1, 'Developer 1', 'dev1@example.com', 'pw_dev1'),
(2, 'Developer 2', 'dev2@example.com', 'pw_dev2'),
(3, 'Developer 3', 'dev3@example.com', 'pw_dev3'),
(4, 'Developer 4', 'dev4@example.com', 'pw_dev4'),
(5, 'Developer 5', 'dev5@example.com', 'pw_dev5');


--admins
CREATE TABLE Admins (
    AdminID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL
);

INSERT INTO Admins (AdminID, Name, Email, Password) VALUES
(1, 'Admin 1', 'admin1@example.com', 'pw_admin1'),
(2, 'Admin 2', 'admin2@example.com', 'pw_admin2'),
(3, 'Admin 3', 'admin3@example.com', 'pw_admin3'),
(4, 'Admin 4', 'admin4@example.com', 'pw_admin4'),
(5, 'Admin 5', 'admin5@example.com', 'pw_admin5');


--games
CREATE TABLE Games (
    GameID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Genre TEXT,
    ReleaseDate DATE,
    Price REAL CHECK (Price >= 0),
    DeveloperID INTEGER,
    FOREIGN KEY (DeveloperID) REFERENCES Developers(DeveloperID)
);

INSERT INTO Games (GameID, Title, Genre, ReleaseDate, Price, DeveloperID) VALUES
(1, 'Starfighter', 'Action', '2014-06-10', 19.99, 1),
(2, 'Escape', 'Puzzle', '2018-11-01', 4.99, 1),
(3, 'Build Your University', 'Simulation', '2022-02-14', 9.99, 1),
(4, 'Dungeon Online', 'RPG', '2024-09-30', 24.99, 1),
(5, 'Drift Track', 'Racing', '2023-03-18', 14.99, 2),
(6, 'Tactics Arena', 'Strategy', '2017-01-22', 29.99, 3),
(7, 'Escape Tung Sahur', 'Horror', '2024-10-05', 17.49, 3),
(8, 'Rhythm Pulse', 'Rhythm', '2015-07-12', 6.99, 4),
(9, 'Battlecraft Survivors', 'Survival', '2021-12-08', 12.99, 4),
(10, 'Legends of Merced', 'Adventure', '2010-02-15', 21.99, 5);

--dev creations
CREATE TABLE Creations (
    DeveloperID INTEGER NOT NULL,
    GameID INTEGER NOT NULL,
    PRIMARY KEY (DeveloperID, GameID),
    FOREIGN KEY (DeveloperID) REFERENCES Developers(DeveloperID) ON DELETE CASCADE,
    FOREIGN KEY (GameID) REFERENCES Games(GameID) ON DELETE CASCADE
);

INSERT INTO Creations (DeveloperID, GameID) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(2, 5),
(3, 6),
(3, 7),
(4, 8),
(4, 9),
(5, 10);


--statistics
CREATE TABLE Statistics (
    StatID INTEGER PRIMARY KEY AUTOINCREMENT,
    GameID INTEGER,
    StatName TEXT,
    StatValue REAL,
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
);

INSERT INTO Statistics (GameID, StatName, StatValue) VALUES
(1, 'AveragePlaytime', 15.5),
(1, 'AverageRating', 8.2),
(2, 'AveragePlaytime', 8.0),
(2, 'AverageRating', 7.5),
(3, 'AveragePlaytime', 20.0),
(3, 'AverageRating', 9.0),
(4, 'AveragePlaytime', 25.0),
(4, 'AverageRating', 8.8),
(5, 'AveragePlaytime', 12.0),
(5, 'AverageRating', 7.9),
(6, 'AveragePlaytime', 30.0),
(6, 'AverageRating', 8.5),
(7, 'AveragePlaytime', 10.0),
(7, 'AverageRating', 7.8),
(8, 'AveragePlaytime', 5.0),
(8, 'AverageRating', 8.0),
(9, 'AveragePlaytime', 18.0),
(9, 'AverageRating', 8.3),
(10, 'AveragePlaytime', 22.0),
(10, 'AverageRating', 9.1);

--purchases
CREATE TABLE Purchases (
    PurchaseID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER,
    GameID INTEGER,
    PurchaseDate DATE,
    PaymentMethod TEXT,
    PriceAtPurchase REAL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
);

INSERT INTO Purchases (UserID, GameID, PurchaseDate, PaymentMethod, PriceAtPurchase) VALUES
(1, 1, '2014-06-12', 'CreditCard', 19.99),
(1, 8, '2015-07-10', 'CreditCard', 6.99),
(2, 1, '2018-11-02', 'PayPal', 19.99),
(2, 9, '2021-12-15', 'Debit', 12.99),
(3, 2, '2018-11-06', 'Debit', 4.99),
(3, 10, '2010-02-21', 'CreditCard', 21.99),
(4, 2, '2018-11-10', 'CreditCard', 4.99),
(5, 3, '2022-02-20', 'CreditCard', 9.99),
(6, 4, '2024-10-06', 'Debit', 24.99),
(7, 4, '2024-10-12', 'PayPal', 24.99),
(8, 5, '2023-03-20', 'CreditCard', 14.99),
(9, 6, '2017-01-23', 'Debit', 29.99),
(10, 7, '2024-10-10', 'PayPal', 17.49);


--achievements
CREATE TABLE Achievements (
    AchievementID INTEGER PRIMARY KEY AUTOINCREMENT,
    GameID INTEGER,
    Title TEXT NOT NULL,
    Description TEXT,
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
);

INSERT INTO Achievements (AchievementID, GameID, Title, Description) VALUES
(1, 1, 'First Victory', 'Win your first match in Starfighter'),
(2, 1, 'Sharpshooter', 'Achieve 100% accuracy in a single match'),
(3, 2, 'Puzzle Master', 'Solve all puzzles in under 1 hour'),
(4, 2, 'No Hints', 'Complete the game without using hints'),
(5, 3, 'Campus Creator', 'Build your first campus'),
(6, 3, 'Student Enrollment', 'Enroll 100 students in your university'),
(7, 4, 'First Quest', 'Complete your first quest'),
(8, 4, 'Dungeon Master', 'Defeat the dungeon boss'),
(9, 5, 'Rookie Racer', 'Win your first race'),
(10, 5, 'Drift King', 'Perform 50 perfect drifts'),
(11, 6, 'Strategist', 'Win 5 matches in a row'),
(12, 7, 'Fearless', 'Survive the horror level without dying'),
(13, 8, 'Perfect Beat', 'Hit 100% perfect notes in a song'),
(14, 9, 'Survivor', 'Survive 10 consecutive matches'),
(15, 10, 'First Adventure', 'Complete the first quest'),
(16, 10, 'Legendary Hero', 'Reach max level');


--achieved
CREATE TABLE Achieved (
    UserID INTEGER,
    AchievementID INTEGER,
    DateAchieved DATE,
    PRIMARY KEY (UserID, AchievementID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (AchievementID) REFERENCES Achievements(AchievementID)
);

INSERT INTO Achieved (UserID, AchievementID, DateAchieved) VALUES
(1, 1, '2014-06-16'),
(1, 2, '2014-06-17'),
(1, 13, '2015-07-16'),
(2, 1, '2014-06-21'),
(2, 14, '2021-12-16'),
(3, 3, '2018-11-06'),
(3, 4, '2018-11-07'),
(3, 15, '2010-02-21'),
(4, 4, '2018-11-11'),
(5, 5, '2022-02-20'),
(5, 6, '2022-02-21'),
(6, 7, '2024-10-06'),
(7, 8, '2024-10-11'),
(8, 9, '2023-03-19'),
(9, 11, '2017-01-23'),
(10, 12, '2024-10-11');

--reviews
CREATE TABLE Reviews (
    ReviewID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER,
    GameID INTEGER,
    Rating INTEGER CHECK (Rating BETWEEN 1 AND 10),
    Comment TEXT,
    ReviewDate DATE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
);

--forums
CREATE TABLE Forums (
    ForumID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Description TEXT,
    CreatedOn DATE,
    AdminID INTEGER,
    FOREIGN KEY (AdminID) REFERENCES Admins(AdminID)
);

INSERT INTO Forums (ForumID, Title, Description, CreatedOn, AdminID) VALUES
(1, 'Starfighter Community', 'Discuss Starfighter tips and tricks', '2014-06-10', 1),
(2, 'Escape Puzzle Club', 'Talk about Escape and other puzzles', '2018-11-01', 2),
(3, 'Build Your University Hub', 'Share strategies for building your university', '2022-02-14', 3),
(4, 'Dungeon Online Realm', 'RPG discussions for Dungeon Online', '2024-09-30', 4),
(5, 'Drift Track Racers', 'Share racing strategies and records', '2023-03-18', 5),
(6, 'Tactics Arena Strategists', 'Discuss strategy and competitive play', '2017-01-22', 1),
(7, 'Escape Tung Sahur Fans', 'Horror and gameplay discussions', '2024-10-05', 2);

--forum members (many-to-many)
CREATE TABLE Members (
    UserID INTEGER,
    ForumID INTEGER,
    JoinedOn DATE,
    PRIMARY KEY (UserID, ForumID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (ForumID) REFERENCES Forums(ForumID)
);

INSERT INTO Members (UserID, ForumID, JoinedOn) VALUES
(1, 1, '2014-06-12'),
(2, 1, '2018-11-02'),
(3, 2, '2018-11-06'),
(4, 2, '2018-11-10'),
(5, 3, '2022-02-20'),
(6, 4, '2024-10-06'),
(7, 4, '2024-10-12'),
(8, 5, '2023-03-20'),
(9, 6, '2017-01-30'),
(10, 7, '2024-10-10');

--friends (self-referencing many-to-many)
CREATE TABLE Friends (
    UserID1 INTEGER,
    UserID2 INTEGER,
    FriendSince DATE,
    PRIMARY KEY (UserID1, UserID2),
    FOREIGN KEY (UserID1) REFERENCES Users(UserID),
    FOREIGN KEY (UserID2) REFERENCES Users(UserID)
);

INSERT INTO Friends (UserID1, UserID2, FriendSince) VALUES
(1, 2, '2015-01-10'),
(2, 1, '2015-01-10'),
(1, 3, '2025-03-02'),
(3, 1, '2025-03-02'),
(1, 4, '2024-04-15'),
(4, 1, '2024-04-15'),
(1, 5, '2010-02-28'),
(5, 1, '2010-02-28'),
(2, 6, '2022-03-10'),
(6, 2, '2022-03-10'),
(2, 7, '2020-03-15'),
(7, 2, '2020-03-15'),
(3, 8, '2019-01-20'),
(8, 3, '2019-01-20'),
(3, 9, '2020-04-05'),
(9, 3, '2020-04-05'),
(4, 10, '2025-05-01'),
(10, 4, '2025-05-01'),
(6, 7, '2023-03-20'),
(7, 6, '2023-03-20'),
(8, 9, '2022-02-12'),
(9, 8, '2022-02-12'),
(9, 10, '2021-04-18'),
(10, 9, '2021-04-18');

CREATE TABLE FriendRequests (
    RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
    SenderID INTEGER,
    ReceiverID INTEGER,
    Status TEXT DEFAULT 'pending',
    FOREIGN KEY (SenderID) REFERENCES Users(UserID),
    FOREIGN KEY (ReceiverID) REFERENCES Users(UserID)
);


CREATE TABLE Posts (
    PostID INTEGER PRIMARY KEY AUTOINCREMENT,
    ForumID INTEGER,
    UserID INTEGER,
    Title TEXT NOT NULL,
    Body TEXT NOT NULL,
    CreatedOn DATE,
    FOREIGN KEY (ForumID) REFERENCES Forums(ForumID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE Comments (
    CommentID INTEGER PRIMARY KEY AUTOINCREMENT,
    PostID INTEGER,
    UserID INTEGER,
    Content TEXT NOT NULL,
    CreatedOn DATE,
    FOREIGN KEY (PostID) REFERENCES Posts(PostID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_statistics_unique
ON Statistics(GameID, StatName);

CREATE TRIGGER UpdateAverageRatingAfterInsert
AFTER INSERT ON Reviews
BEGIN
    -- Recompute the average rating for this game
    INSERT INTO Statistics (GameID, StatName, StatValue)
    VALUES (
        NEW.GameID,
        'AverageRating',
        (SELECT AVG(Rating) FROM Reviews WHERE GameID = NEW.GameID)
    )
    ON CONFLICT(GameID, StatName)
    DO UPDATE SET StatValue = excluded.StatValue;
END;

CREATE TRIGGER UpdateAverageRatingAfterUpdate
AFTER UPDATE OF Rating ON Reviews
BEGIN
    INSERT INTO Statistics (GameID, StatName, StatValue)
    VALUES (
        NEW.GameID,
        'AverageRating',
        (SELECT AVG(Rating) FROM Reviews WHERE GameID = NEW.GameID)
    )
    ON CONFLICT(GameID, StatName)
    DO UPDATE SET StatValue = excluded.StatValue;
END;

INSERT INTO Reviews (UserID, GameID, Rating, Comment, ReviewDate) VALUES
(1, 1, 9, 'Starfighter is fantastic! Really enjoyed the gameplay.', '2014-06-15'),
(1, 8, 7, 'Rhythm Pulse is fun and enjoyable, but could use more songs.', '2015-07-16'),
(2, 1, 5, 'Starfighter was okay, had some fun but not enough content.', '2014-06-20'),
(2, 9, 10, 'Battlecraft Survivors is epic! Loved every match.', '2021-12-16'),
(3, 2, 8, 'Escape is challenging and rewarding, great puzzle game.', '2018-11-07'),
(3, 10, 6, 'Legends of Merced is good, but could be longer.', '2010-02-21'),
(4, 2, 3, 'Escape was too frustrating, some puzzles felt unfair.', '2018-11-10'),
(5, 3, 9, 'Build Your University is amazing, so satisfying to manage!', '2022-02-20'),
(6, 4, 10, 'Dungeon Online is perfect! Loved every quest and challenge.', '2024-10-06'),
(7, 4, 7, 'Dungeon Online is fun but a bit repetitive at times.', '2024-10-12'),
(8, 1, 9, 'Starfighter is fantastic! Really enjoyed the gameplay.', '2014-06-15'),
(9, 8, 7, 'Rhythm Pulse is fun and enjoyable, but could use more songs.', '2015-07-16'),
(10, 1, 5, 'Starfighter was okay, had some fun but not enough content.', '2014-06-20'),
(9, 9, 10, 'Battlecraft Survivors is epic! Loved every match.', '2021-12-16'),
(9, 2, 8, 'Escape is challenging and rewarding, great puzzle game.', '2018-11-07'),
(10, 10, 6, 'Legends of Merced is good, but could be longer.', '2010-02-21'),
(10, 2, 3, 'Escape was too frustrating, some puzzles felt unfair.', '2018-11-10'),
(9, 3, 9, 'Build Your University is amazing, so satisfying to manage!', '2022-02-20'),
(10, 4, 10, 'Dungeon Online is perfect! Loved every quest and challenge.', '2024-10-06'),
(9, 4, 7, 'Dungeon Online is fun but a bit repetitive at times.', '2024-10-12');