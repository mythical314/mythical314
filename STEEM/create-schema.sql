--users
CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL
);

--developers
CREATE TABLE Developers (
    DeveloperID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL
);

--admins
CREATE TABLE Admins (
    AdminID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL
);

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

--dev creations
CREATE TABLE Creations (
    DeveloperID INTEGER NOT NULL,
    GameID INTEGER NOT NULL,
    PRIMARY KEY (DeveloperID, GameID),
    FOREIGN KEY (DeveloperID) REFERENCES Developers(DeveloperID) ON DELETE CASCADE,
    FOREIGN KEY (GameID) REFERENCES Games(GameID) ON DELETE CASCADE
);

--statistics
CREATE TABLE Statistics (
    StatID INTEGER PRIMARY KEY AUTOINCREMENT,
    GameID INTEGER,
    StatName TEXT,
    StatValue REAL,
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
);

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

--achievements
CREATE TABLE Achievements (
    AchievementID INTEGER PRIMARY KEY AUTOINCREMENT,
    GameID INTEGER,
    Title TEXT NOT NULL,
    Description TEXT,
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
);

--achieved
CREATE TABLE Achieved (
    UserID INTEGER,
    AchievementID INTEGER,
    DateAchieved DATE,
    PRIMARY KEY (UserID, AchievementID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (AchievementID) REFERENCES Achievements(AchievementID)
);

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

--forum members (many-to-many)
CREATE TABLE Members (
    UserID INTEGER,
    ForumID INTEGER,
    JoinedOn DATE,
    PRIMARY KEY (UserID, ForumID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (ForumID) REFERENCES Forums(ForumID)
);

--friends (self-referencing many-to-many)
CREATE TABLE Friends (
    UserID1 INTEGER,
    UserID2 INTEGER,
    FriendSince DATE,
    PRIMARY KEY (UserID1, UserID2),
    FOREIGN KEY (UserID1) REFERENCES Users(UserID),
    FOREIGN KEY (UserID2) REFERENCES Users(UserID)
);

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
