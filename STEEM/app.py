import sqlite3
from flask import Flask, g, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "i love brainrot"
DATABASE = "mydatabase.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db:
        db.close()

# login process, checking user/dev/admin
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()

        # --- Admin login ---
        admin = db.execute("""
            SELECT * FROM Admins WHERE Email = ?
        """, (email,)).fetchone()

        if admin and check_password_hash(admin["Password"], password):
            session["role"] = "admin"
            session["admin_id"] = admin["AdminID"]
            return redirect(url_for("admin_dashboard"))

        # --- Developer login ---
        dev = db.execute("""
            SELECT * FROM Developers WHERE Email = ?
        """, (email,)).fetchone()

        if dev and check_password_hash(dev["Password"], password):
            session["role"] = "developer"
            session["dev_id"] = dev["DeveloperID"]
            return redirect(url_for("developer_dashboard"))

        # --- User login ---
        user = db.execute("""
            SELECT * FROM Users WHERE Email = ?
        """, (email,)).fetchone()

        if user and check_password_hash(user["Password"], password):
            session["role"] = "user"
            session["user_id"] = user["UserID"]
            return redirect(url_for("user_dashboard"))

        return "Invalid email or password", 400

    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# user dashboard
@app.route("/user")
def user_dashboard():
    if session.get("role") != "user":
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()

    incoming = db.execute("""
        SELECT fr.RequestID, u.Name AS SenderName, u.UserID AS SenderID
        FROM FriendRequests fr
        JOIN Users u ON fr.SenderID = u.UserID
        WHERE fr.ReceiverID=? AND fr.Status='pending'
    """, (user_id,)).fetchall()

    outgoing = db.execute("""
        SELECT fr.RequestID, u.Name AS ReceiverName, u.UserID AS ReceiverID
        FROM FriendRequests fr
        JOIN Users u ON fr.ReceiverID = u.UserID
        WHERE fr.SenderID=? AND fr.Status='pending'
    """, (user_id,)).fetchall()

    purchases = db.execute("""
        SELECT g.*
        FROM Games g
        JOIN Purchases p ON g.GameID = p.GameID
        WHERE p.UserID = ?
    """, (user_id,)).fetchall()

    # friend list (had to remove duplicates)
    friends = db.execute("""
        SELECT DISTINCT
            CASE WHEN UserID1=? THEN UserID2 ELSE UserID1 END AS FriendID,
            (SELECT Name FROM Users WHERE UserID =
                CASE WHEN UserID1=? THEN UserID2 ELSE UserID1 END
            ) AS FriendName
        FROM Friends
        WHERE ? IN (UserID1, UserID2)
        ORDER BY FriendName ASC
    """, (user_id, user_id, user_id)).fetchall()

    # forums the user is a member in
    forums = db.execute("""
        SELECT F.ForumID, F.Title
        FROM Members M
        JOIN Forums F ON F.ForumID = M.ForumID
        WHERE M.UserID = ?
        ORDER BY F.Title ASC
    """, (user_id,)).fetchall()

    return render_template(
        "user_dashboard.html",
        purchases=purchases,
        incoming=incoming,
        outgoing=outgoing,
        friends=friends,
        forums=forums
    )


# dev dashboard
@app.route("/developer")
def developer_dashboard():
    if session.get("role") != "developer":
        return redirect(url_for("login"))

    dev_id = session["dev_id"]
    db = get_db()

    games = db.execute("""
        SELECT 
            g.GameID,
            g.Title,
            g.Genre,
            g.Price,
            g.ReleaseDate,
            d.Name AS DeveloperName
        FROM Games g
        JOIN Creations c ON g.GameID = c.GameID
        JOIN Developers d ON c.DeveloperID = d.DeveloperID
        WHERE c.DeveloperID = ?
        ORDER BY g.Title ASC
    """, (dev_id,)).fetchall()

    return render_template("developer_dashboard.html", games=games)


# admin dashboard
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")


# user prof
@app.route("/user/<int:userID>")
def user_profile(userID):
    db = get_db()

    user = db.execute(
        "SELECT * FROM Users WHERE UserID=?",
        (userID,)
    ).fetchone()
    if not user:
        return f"User {userID} not found.", 404

    # show another user friend list
    friends = db.execute("""
        SELECT DISTINCT FriendID, FriendName
        FROM (
            SELECT
                CASE WHEN UserID1 = ? THEN UserID2 ELSE UserID1 END AS FriendID,
                (SELECT Name FROM Users WHERE UserID =
                    CASE WHEN UserID1=? THEN UserID2 ELSE UserID1 END
                ) AS FriendName
            FROM Friends
            WHERE ? IN (UserID1, UserID2)
        )
        ORDER BY FriendName ASC
    """, (userID, userID, userID)).fetchall()

    library = db.execute("""
        SELECT g.GameID, g.Title, g.Genre, g.Price
        FROM Purchases p
        JOIN Games g ON g.GameID = p.GameID
        WHERE p.UserID = ?
        ORDER BY g.Title ASC
    """, (userID,)).fetchall()

    return render_template(
        "user_profile.html",
        user=user,
        friends=friends,
        library=library
    )


# friend adding
@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        db.execute(
            "INSERT INTO Users (Name, Email, Password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        db.commit()

        return redirect(url_for("login"))

    return render_template("add_user.html")

@app.route("/add_developer", methods=["GET", "POST"])
def add_developer():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        db.execute(
            "INSERT INTO Developers (Name, Email, Password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        db.commit()

        return redirect(url_for("login"))

    return render_template("add_dev.html")

@app.route("/add_admin", methods=["GET", "POST"])
def add_admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        db.execute(
            "INSERT INTO Admins (Name, Email, Password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        db.commit()

        return redirect(url_for("admin_dashboard"))

    return render_template("add_admin.html")

# search for ppl to add
@app.route("/find_friends", methods=["GET", "POST"])
def find_friends():
    if session.get("role") != "user":
        return redirect(url_for("login"))

    db = get_db()
    results = None
    user_id = session["user_id"]

    if request.method == "POST":
        term = "%" + request.form["search"] + "%"

        results = db.execute("""
            SELECT 
                u.UserID, 
                u.Name,
                u.Email,

                -- 1. Is already friend?
                CASE 
                    WHEN u.UserID IN (
                        SELECT CASE WHEN UserID1=? THEN UserID2 ELSE UserID1 END
                        FROM Friends
                        WHERE ? IN (UserID1, UserID2)
                    ) THEN 'friend'
                    ELSE NULL
                END AS FriendStatus,

                -- 2. Pending request YOU sent
                (SELECT Status 
                 FROM FriendRequests 
                 WHERE SenderID=? AND ReceiverID=u.UserID AND Status='pending'
                 LIMIT 1
                ) AS PendingSent,

                -- 3. Pending request THEY sent to YOU
                (SELECT Status 
                 FROM FriendRequests 
                 WHERE ReceiverID=? AND SenderID=u.UserID AND Status='pending'
                 LIMIT 1
                ) AS PendingReceived

            FROM Users u
            WHERE u.Name LIKE ?
              AND u.UserID != ?
            ORDER BY u.Name ASC
        """, (user_id, user_id, user_id, user_id, term, user_id)).fetchall()
    
    recommended=db.execute("""
    SELECT DISTINCT u.UserID, u.Name, u.Email,
        CASE 
            WHEN u.UserID IN (
                SELECT CASE WHEN UserID1=? THEN UserID2 ELSE UserID1 END
                FROM Friends
                WHERE ? IN (UserID1, UserID2)
            ) THEN 'friend'
            ELSE NULL
        END AS FriendStatus,

        -- 2. Pending request YOU sent
        (SELECT Status 
            FROM FriendRequests 
            WHERE SenderID=? AND ReceiverID=u.UserID AND Status='pending'
            LIMIT 1
        ) AS PendingSent,

        -- 3. Pending request THEY sent to YOU
        (SELECT Status 
            FROM FriendRequests 
            WHERE ReceiverID=? AND SenderID=u.UserID AND Status='pending'
            LIMIT 1
        ) AS PendingReceived
    FROM (
        -- Step 1: Get direct friends of the user
        SELECT 
            CASE 
                WHEN UserID1 = ? THEN UserID2 
                ELSE UserID1 
            END AS FriendID
        FROM Friends
        WHERE ? IN (UserID1, UserID2)
    ) ff
    JOIN Friends f2 
        ON ff.FriendID IN (f2.UserID1, f2.UserID2)
    -- Step 2: Get the friends-of-friends
    JOIN Users u
        ON u.UserID = CASE 
                        WHEN f2.UserID1 = ff.FriendID THEN f2.UserID2 
                        ELSE f2.UserID1 
                    END
    -- Step 3: Exclude original user and their direct friends
    WHERE u.UserID != ?
    AND u.UserID NOT IN (
        SELECT 
            CASE 
                WHEN UserID1 = ? THEN UserID2 
                ELSE UserID1 
            END
        FROM Friends
        WHERE ? IN (UserID1, UserID2)
    );
""", (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id)).fetchall()

    return render_template("find_friends.html", results=results, recommended=recommended)

# send request
@app.route("/friends/send/<int:receiver_id>")
def send_friend_request(receiver_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    sender_id = session["user_id"]
    db = get_db()

    # check if already friends
    already = db.execute("""
        SELECT 1 FROM Friends
        WHERE (UserID1=? AND UserID2=?) OR (UserID1=? AND UserID2=?)
    """, (sender_id, receiver_id, receiver_id, sender_id)).fetchone()

    if already:
        return redirect(url_for("user_dashboard"))

    # show friend requests on both sides of users
    existing = db.execute("""
        SELECT 1 FROM FriendRequests
        WHERE ((SenderID=? AND ReceiverID=?) OR (SenderID=? AND ReceiverID=?))
        AND Status='pending'
    """, (sender_id, receiver_id, receiver_id, sender_id)).fetchone()

    if not existing:
        db.execute("""
            INSERT INTO FriendRequests (SenderID, ReceiverID, Status)
            VALUES (?, ?, 'pending')
        """, (sender_id, receiver_id))
        db.commit()

    return redirect(url_for("user_dashboard"))

# accepting request
@app.route("/friends/accept/<int:request_id>")
def accept_friend_request(request_id):
    db = get_db()
    req = db.execute("SELECT * FROM FriendRequests WHERE RequestID=?", (request_id,)).fetchone()

    if not req:
        return "Request not found.", 404

    sender = req["SenderID"]
    receiver = req["ReceiverID"]

    db.execute("UPDATE FriendRequests SET Status='accepted' WHERE RequestID=?", (request_id,))

    # adding to db
    db.execute("INSERT INTO Friends (UserID1, UserID2, FriendSince) VALUES (?, ?, DATE('now'))", (sender, receiver))
    db.execute("INSERT INTO Friends (UserID1, UserID2, FriendSince) VALUES (?, ?, DATE('now'))", (receiver, sender))

    db.commit()
    return redirect(url_for("user_dashboard"))

# declining
@app.route("/friends/decline/<int:request_id>")
def decline_friend_request(request_id):
    db = get_db()
    db.execute("UPDATE FriendRequests SET Status='declined' WHERE RequestID=?", (request_id,))
    db.commit()
    return redirect(url_for("user_dashboard"))

# removing
@app.route("/friends/remove/<int:friend_id>")
def remove_friend(friend_id):
    user = session["user_id"]
    db = get_db()

    db.execute("""
        DELETE FROM Friends
        WHERE (UserID1=? AND UserID2=?) OR (UserID1=? AND UserID2=?)
    """, (user, friend_id, friend_id, user))

    db.commit()
    return redirect(url_for("user_dashboard"))


# game setup
@app.route("/games")
def games():
    db = get_db()

    user_id = session.get("user_id") if session.get("role") == "user" else -1

    best_rated = db.execute("""
        SELECT 
            G.*,
            D.Name AS DeveloperName,
            (SELECT 1 
            FROM Purchases P 
            WHERE P.UserID = ? AND P.GameID = G.GameID
            ) AS UserHasGame,
            CAST(S.StatValue AS REAL) AS AvgRating
        FROM Games G
        LEFT JOIN Developers D 
            ON G.DeveloperID = D.DeveloperID
        LEFT JOIN Statistics S
            ON G.GameID = S.GameID 
            AND S.StatName = 'AverageRating'
        ORDER BY AvgRating DESC
        LIMIT 3;
        """, (user_id,)).fetchall()
    
    new_releases = db.execute("""
        SELECT 
            G.*,
            D.Name AS DeveloperName,
            (SELECT 1 
            FROM Purchases P 
            WHERE P.UserID = ? AND P.GameID = G.GameID
            ) AS UserHasGame
        FROM Games G
        LEFT JOIN Developers D 
            ON G.DeveloperID = D.DeveloperID
        ORDER BY G.ReleaseDate DESC
        LIMIT 3;
        """, (user_id,)).fetchall()

    rows = db.execute("""
        SELECT 
            G.*,
            D.Name AS DeveloperName,
            (SELECT 1 FROM Purchases P WHERE P.UserID=? AND P.GameID=G.GameID) AS UserHasGame
        FROM Games G
        LEFT JOIN Developers D ON G.DeveloperID = D.DeveloperID
        ORDER BY G.Title ASC
    """, (user_id,)).fetchall()



    return render_template("games.html", rows=rows, best_rated=best_rated, new_releases=new_releases)

# showcasing the game info
@app.route("/game/<int:game_id>")
def game_details(game_id):
    db = get_db()

    # get game info
    game = db.execute("""
        SELECT G.*, D.Name AS DeveloperName
        FROM Games G
        LEFT JOIN Developers D ON G.DeveloperID = D.DeveloperID
        WHERE G.GameID = ?
    """, (game_id,)).fetchone()

    if not game:
        return "Game not found.", 404

    # is the user a normal user
    user_has_game = False
    if session.get("role") == "user":
        owned = db.execute("""
            SELECT 1 FROM Purchases
            WHERE UserID = ? AND GameID = ?
        """, (session["user_id"], game_id)).fetchone()
        user_has_game = owned is not None

    # get multiple game information

    achievements = db.execute("""
        SELECT * FROM Achievements
        WHERE GameID = ?
    """, (game_id,)).fetchall()

    reviews = db.execute("""
        SELECT 
            R.UserID,
            R.Rating,
            R.Comment,
            R.ReviewDate,
            U.Name AS UserName
        FROM Reviews R
        JOIN Users U ON R.UserID = U.UserID
        WHERE R.GameID = ?
    """, (game_id,)).fetchall()

    stats = db.execute("""
        SELECT StatName, StatValue
        FROM Statistics
        WHERE GameID = ?
        AND StatName != 'AverageRating'
    """, (game_id,)).fetchall()

    avg_rating = db.execute("""
        SELECT MAX(StatValue) AS StatValue
        FROM Statistics
        WHERE GameID = ?
        AND StatName = 'AverageRating';
    """, (game_id,)).fetchone()[0]

    return render_template(
        "game_details.html",
        game=game,
        achievements=achievements,
        reviews=reviews,
        stats=stats,
        avg_rating=avg_rating,
        user_has_game=user_has_game
    )

# user achievements
@app.route("/user/<int:userID>/game/<int:gameID>/achievements")
def user_game_achievements(userID, gameID):
    db = get_db()

    # achievement query
    rows = db.execute(
        """
        WITH AmountsPurchased AS (
            SELECT GameID, COUNT(*) AS PurchaseCount
            FROM Purchases
            GROUP BY GameID
        ),
        AchievementCounts AS (
            SELECT a.AchievementID, COUNT(ac.UserID) AS AchievementCount
            FROM Achievements a
            LEFT JOIN Achieved ac ON ac.AchievementID = a.AchievementID
            GROUP BY a.AchievementID
        )
        SELECT 
            a.AchievementID,
            a.Title AS AchievementTitle,
            a.Description,

            CASE WHEN ua.UserID IS NOT NULL THEN 1 ELSE 0 END AS UserHasAchieved,

            COALESCE(
                (1.0 * ac.AchievementCount) 
                / NULLIF(ap.PurchaseCount, 0),
            0) AS AchievementRate

        FROM Achievements a
        JOIN AchievementCounts ac ON a.AchievementID = ac.AchievementID
        LEFT JOIN AmountsPurchased ap ON a.GameID = ap.GameID
        LEFT JOIN Achieved ua 
               ON ua.AchievementID = a.AchievementID AND ua.UserID = ?

        WHERE a.GameID = ?
        ORDER BY a.Title ASC;
        """,
        (userID, gameID)
    ).fetchall()

    # avg completion rate
    avg_game_completion = db.execute(
        """
        WITH UserAchievements AS (
            SELECT ac.UserID, a.GameID, COUNT(*) AS AchievedCount
            FROM Achievements a
            JOIN Achieved ac ON ac.AchievementID = a.AchievementID
            GROUP BY ac.UserID, a.GameID
        ),
        TotalAchievements AS (
            SELECT GameID, COUNT(*) AS TotalAchievements
            FROM Achievements
            GROUP BY GameID
        )
        SELECT COALESCE(
            ROUND(AVG(1.0 * ua.AchievedCount / ta.TotalAchievements), 3),
            0
        )
        FROM UserAchievements ua
        JOIN TotalAchievements ta ON ua.GameID = ta.GameID
        WHERE ua.GameID = ?;
        """,
        (gameID,)
    ).fetchone()[0]

    # user personal completion
    user_game_completion = db.execute(
        """
        WITH UserAchieved AS (
            SELECT COUNT(*) AS UserCount
            FROM Achieved ac
            JOIN Achievements a ON ac.AchievementID = a.AchievementID
            WHERE ac.UserID = ? AND a.GameID = ?
        ),
        TotalAchievements AS (
            SELECT COUNT(*) AS TotalCount
            FROM Achievements WHERE GameID = ?
        )
        SELECT COALESCE(
            ROUND(1.0 * ua.UserCount / NULLIF(t.TotalCount, 0), 3),
            0
        )
        FROM UserAchieved ua, TotalAchievements t;
        """,
        (userID, gameID, gameID)
    ).fetchone()[0]

    return render_template(
        "user_game_achievements.html",
        rows=rows,
        avg_game_completion=avg_game_completion,
        user_game_completion=user_game_completion,
        userID=userID
    )

# user to leave review
@app.route("/game/<int:game_id>/review", methods=["POST"])
def leave_review(game_id):
    if session.get("role") != "user":
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()

    rating = request.form["rating"]
    comment = request.form["comment"]

    # check if user owns the game
    has_game = db.execute("""
        SELECT 1 FROM Purchases
        WHERE UserID=? AND GameID=?
    """, (user_id, game_id)).fetchone()

    if not has_game:
        return "You must own the game to leave a review.", 403

    # check if user already reviewed
    existing = db.execute("""
        SELECT 1 FROM Reviews
        WHERE UserID=? AND GameID=?
    """, (user_id, game_id)).fetchone()

    if existing:
        # update their old rev
        db.execute("""
            UPDATE Reviews
            SET Rating=?, Comment=?, ReviewDate=DATE('now')
            WHERE UserID=? AND GameID=?
        """, (rating, comment, user_id, game_id))

    else:
        # insert new review into db
        db.execute("""
            INSERT INTO Reviews (UserID, GameID, Rating, Comment, ReviewDate)
            VALUES (?, ?, ?, ?, DATE('now'))
        """, (user_id, game_id, rating, comment))

    db.commit()
    return redirect(url_for("game_details", game_id=game_id))

# user edit
@app.route("/game/<int:game_id>/review/edit", methods=["GET"])
def edit_review(game_id):
    if session.get("role") != "user":
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()

    review = db.execute("""
        SELECT * FROM Reviews
        WHERE UserID=? AND GameID=?
    """, (user_id, game_id)).fetchone()

    if not review:
        return "You have not reviewed this game yet.", 404

    return render_template("edit_review.html", review=review, game_id=game_id)

# updating portion for reviews
@app.route("/game/<int:game_id>/review/update", methods=["POST"])
def update_review(game_id):
    if session.get("role") != "user":
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()

    rating = request.form["rating"]
    comment = request.form["comment"]

    db.execute("""
        UPDATE Reviews
        SET Rating=?, Comment=?, ReviewDate=DATE('now')
        WHERE UserID=? AND GameID=?
    """, (rating, comment, user_id, game_id))

    avg_rating = db.execute("""
        SELECT ROUND(AVG(Rating), 2)
        FROM Reviews
        WHERE GameID = ?
    """, (game_id,)).fetchone()[0]

    db.execute("""
        UPDATE Statistics
        SET StatValue = ?
        WHERE GameID = ? AND StatName = "AverageRating";""", (avg_rating, game_id,))

    db.commit()
    return redirect(url_for("game_details", game_id=game_id))


#  buying/removing game stuff
@app.route("/buy/<int:game_id>", methods=["POST"])
def buy_game(game_id):
    if session.get("role") != "user":
        return "Only users can purchase games.", 403

    db = get_db()
    user_id = session.get("user_id")

    # game info
    game = db.execute("SELECT * FROM Games WHERE GameID = ?", (game_id,)).fetchone()
    if not game:
        return "Game not found.", 404

    # check if user already owns the game
    already_bought = db.execute("""
        SELECT 1 FROM Purchases WHERE UserID = ? AND GameID = ?
    """, (user_id, game_id)).fetchone()

    if already_bought:
        return redirect(url_for("game_details", game_id=game_id))

    # just did default for payment cuz its simpler
    payment_method = "CreditCard"

    # purchase
    db.execute("""
        INSERT INTO Purchases (UserID, GameID, PurchaseDate, PaymentMethod, PriceAtPurchase)
        VALUES (?, ?, DATE('now'), ?, ?)
    """, (user_id, game_id, payment_method, game["Price"]))

    db.commit()

    return redirect(url_for("user_dashboard"))

# removing/refunding
@app.route("/remove_purchase/<int:game_id>", methods=["POST"])
def remove_purchase(game_id):
    if session.get("role") != "user":
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()

    # deleting purchase
    db.execute("""
        DELETE FROM Purchases
        WHERE UserID = ? AND GameID = ?
    """, (user_id, game_id))

    db.commit()

    return redirect(url_for("user_dashboard"))


#  forum stuff
@app.route("/forums")
def forums():
    db = get_db()

    role = session.get("role")

    # users join forums
    if role == "user":
        member_id = session["user_id"]   
    else:
        # admins / devs are never members (messed up ids so had to do this)
        member_id = -1

    forums = db.execute("""
        SELECT 
            F.ForumID,
            F.Title,
            F.Description,
            F.CreatedOn,
            F.AdminID,
            CASE 
                WHEN M.UserID IS NOT NULL THEN 1
                ELSE 0
            END AS IsMember
        FROM Forums F
        LEFT JOIN Members M 
            ON F.ForumID = M.ForumID 
            AND M.UserID = ?
        ORDER BY F.Title ASC
    """, (member_id,)).fetchall()

    return render_template("forums.html", forums=forums)

# looking in forum
@app.route("/forum/<int:forum_id>")
def forum_view(forum_id):
    db = get_db()

    forum = db.execute("SELECT * FROM Forums WHERE ForumID=?", (forum_id,)).fetchone()
    if not forum:
        return "Forum not found", 404

    # posts
    posts = db.execute("""
        SELECT P.*, U.Name AS UserName
        FROM Posts P
        JOIN Users U ON P.UserID = U.UserID
        WHERE P.ForumID = ?
        ORDER BY P.CreatedOn DESC
    """, (forum_id,)).fetchall()

    # membership check
    is_member = False
    role = session.get("role")
    if role in ("user"):
        uid = session["user_id"]
        is_member = db.execute("""
            SELECT 1 FROM Members WHERE UserID=? AND ForumID=?
        """, (uid, forum_id)).fetchone() is not None

    return render_template(
        "forum_view.html",
        forum=forum,
        posts=posts,
        is_member=is_member
    )

# join for users
@app.route("/forum/<int:forum_id>/join", methods=["POST"])
def join_forum(forum_id):
    role = session.get("role")
    if role not in ("user"):
        return "Only users can join forums.", 403

    uid = session["user_id"]
    db = get_db()

    db.execute("""
        INSERT OR IGNORE INTO Members (UserID, ForumID, JoinedOn)
        VALUES (?, ?, DATE('now'))
    """, (uid, forum_id))

    db.commit()
    return redirect(url_for("forum_view", forum_id=forum_id))

# user create forum
@app.route("/forums/create", methods=["GET", "POST"])
def create_forum():
    if session.get("role") not in ["user", "admin"]: 
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        if session.get("role") == "admin":
            admin_id = session["admin_id"]
        else:
            admin_id = session["user_id"]

        db = get_db()
        db.execute("""
            INSERT INTO Forums (Title, Description, CreatedOn, AdminID)
            VALUES (?, ?, DATE('now'), ?)
        """, (title, description, admin_id))
        db.commit()

        return redirect(url_for("forums"))

    return render_template("create_forum.html")

# deleting for admins
@app.route("/forums/delete/<int:forum_id>", methods=["POST"])
def delete_forum(forum_id):
    if session.get("role") != "admin":
        return "Unauthorized", 403

    db = get_db()
    db.execute("DELETE FROM Forums WHERE ForumID=?", (forum_id,))
    db.commit()

    return redirect(url_for("forums"))

# new user post
@app.route("/forum/<int:forum_id>/post/new", methods=["GET", "POST"])
def new_post(forum_id):
    role = session.get("role")
    if role not in ("user"):
        return "Only users can create posts.", 403

    db = get_db()

    uid = session["user_id"]  

    # have to be member to post
    member = db.execute("""
        SELECT 1 FROM Members WHERE UserID=? AND ForumID=?
    """, (uid, forum_id)).fetchone()

    if not member:
        return "You must join the forum first.", 403

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        db.execute("""
            INSERT INTO Posts (ForumID, UserID, Title, Body, CreatedOn)
            VALUES (?, ?, ?, ?, DATE('now'))
        """, (forum_id, uid, title, body))
        db.commit()

        return redirect(url_for("forum_view", forum_id=forum_id))

    return render_template("new_post.html")

# looking at posts
@app.route("/post/<int:post_id>")
def post_view(post_id):
    db = get_db()

    post = db.execute("""
        SELECT P.*, U.Name AS UserName
        FROM Posts P
        JOIN Users U ON P.UserID = U.UserID
        WHERE PostID=?
    """, (post_id,)).fetchone()

    comments = db.execute("""
        SELECT C.*, U.Name AS UserName
        FROM Comments C
        JOIN Users U ON U.UserID = C.UserID
        WHERE PostID=?
        ORDER BY C.CreatedOn ASC
    """, (post_id,)).fetchall()

    return render_template("post_view.html", post=post, comments=comments)

# user comments
@app.route("/post/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):
    role = session.get("role")
    if role not in ("user"):
        return "Only users can comment.", 403

    body = request.form["content"]
    uid = session["user_id"]
    db = get_db()

    db.execute("""
        INSERT INTO Comments (PostID, UserID, Content, CreatedOn)
        VALUES (?, ?, ?, DATE('now'))
    """, (post_id, uid, body))

    db.commit()
    return redirect(url_for("post_view", post_id=post_id))

# leaving forums
@app.route("/forum/<int:forum_id>/leave", methods=["POST"])
def leave_forum(forum_id):
    role = session.get("role")
    if role not in ("user", "developer"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()

    db.execute("""
        DELETE FROM Members
        WHERE UserID = ? AND ForumID = ?
    """, (user_id, forum_id))

    db.commit()
    return redirect(url_for("forums"))

# deleting post
@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    role = session.get("role")
    if role not in ("user", "developer"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()

    # check if they own the post
    post = db.execute("""
        SELECT * FROM Posts WHERE PostID = ? AND UserID = ?
    """, (post_id, user_id)).fetchone()

    if not post:
        return "Unauthorized", 403

    # delete post/comment
    db.execute("DELETE FROM Comments WHERE PostID = ?", (post_id,))
    db.execute("DELETE FROM Posts WHERE PostID = ?", (post_id,))
    db.commit()

    return redirect(url_for("forum_view", forum_id=post["ForumID"]))

# admin delete 
@app.route("/admin/post/<int:post_id>/delete", methods=["POST"])
def admin_delete_post(post_id):
    if session.get("role") != "admin":
        return "Unauthorized", 403

    db = get_db()

    # forum_id before deleting
    forum_id = db.execute(
        "SELECT ForumID FROM Posts WHERE PostID=?",
        (post_id,)
    ).fetchone()

    if not forum_id:
        return "Post not found", 404

    forum_id = forum_id["ForumID"]

    # delete
    db.execute("DELETE FROM Comments WHERE PostID=?", (post_id,))
    db.execute("DELETE FROM Posts WHERE PostID=?", (post_id,))
    db.commit()

    return redirect(url_for("forum_view", forum_id=forum_id))

# editting
@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    role = session.get("role")
    if role not in ("user", "developer"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()

    post = db.execute("""
        SELECT * FROM Posts WHERE PostID = ? AND UserID = ?
    """, (post_id, user_id)).fetchone()

    if not post:
        return "Unauthorized", 403

    if request.method == "POST":
        new_title = request.form["title"]
        new_body = request.form["body"]

        db.execute("""
            UPDATE Posts
            SET Title = ?, Body = ?
            WHERE PostID = ?
        """, (new_title, new_body, post_id))

        db.commit()
        return redirect(url_for("post_view", post_id=post_id))

    return render_template("edit_post.html", post=post)

# deleting comments
@app.route("/comment/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    role = session.get("role")
    if role not in ("user", "developer"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()

    # check ownership
    comment = db.execute("""
        SELECT * FROM Comments WHERE CommentID = ? AND UserID = ?
    """, (comment_id, user_id)).fetchone()

    if not comment:
        return "Unauthorized", 403

    # delete
    db.execute("DELETE FROM Comments WHERE CommentID = ?", (comment_id,))
    db.commit()

    return redirect(url_for("post_view", post_id=comment["PostID"]))

# admin can delete comment too
@app.route("/admin/comment/<int:comment_id>/delete", methods=["POST"])
def admin_delete_comment(comment_id):
    if session.get("role") != "admin":
        return "Unauthorized", 403

    db = get_db()

    # get postid to return
    post = db.execute(
        "SELECT PostID FROM Comments WHERE CommentID=?",
        (comment_id,)
    ).fetchone()

    if not post:
        return "Comment not found", 404

    post_id = post["PostID"]

    db.execute("DELETE FROM Comments WHERE CommentID=?", (comment_id,))
    db.commit()

    return redirect(url_for("post_view", post_id=post_id))

# editting comments
@app.route("/comment/<int:comment_id>/edit", methods=["GET", "POST"])
def edit_comment(comment_id):
    role = session.get("role")
    if role not in ("user", "developer"):
        return redirect(url_for("login"))

    db = get_db()
    user_id = session["user_id"]

    comment = db.execute("""
        SELECT * FROM Comments WHERE CommentID = ? AND UserID = ?
    """, (comment_id, user_id)).fetchone()

    if not comment:
        return "Unauthorized", 403

    if request.method == "POST":
        new_text = request.form["content"]

        db.execute("""
            UPDATE Comments
            SET Content = ?
            WHERE CommentID = ?
        """, (new_text, comment_id))

        db.commit()
        return redirect(url_for("post_view", post_id=comment["PostID"]))

    return render_template("edit_comment.html", comment=comment)


#  dev stuff
# looking at all the tables of everything basically
@app.route("/view/<table>")
def view_table(table):
    db = get_db()

    # friends table
    if table.lower() == "friends":
        rows = db.execute("""
            SELECT 
                CASE WHEN f.UserID1 < f.UserID2 THEN f.UserID1 ELSE f.UserID2 END AS UserA_ID,
                CASE WHEN f.UserID1 < f.UserID2 THEN f.UserID2 ELSE f.UserID1 END AS UserB_ID,
                (SELECT Name FROM Users WHERE UserID = 
                    CASE WHEN f.UserID1 < f.UserID2 THEN f.UserID1 ELSE f.UserID2 END
                ) AS UserA_Name,
                (SELECT Name FROM Users WHERE UserID = 
                    CASE WHEN f.UserID1 < f.UserID2 THEN f.UserID2 ELSE f.UserID1 END
                ) AS UserB_Name,
                f.FriendSince
            FROM Friends f
            GROUP BY UserA_ID, UserB_ID
            ORDER BY UserA_Name, UserB_Name
        """).fetchall()

        return render_template("view_table.html", rows=rows, table=table)
    
    # creations table
    if table.lower() == "creations":
        rows = db.execute("""
            SELECT 
                C.DeveloperID,
                D.Name AS DeveloperName,
                C.GameID,
                G.Title AS GameTitle
            FROM Creations C
            JOIN Developers D ON C.DeveloperID = D.DeveloperID
            JOIN Games G ON C.GameID = G.GameID
            ORDER BY DeveloperName, GameTitle
        """).fetchall()

        return render_template("view_table.html", rows=rows, table=table)
    
    # statistics table
    if table.lower() == "statistics":
        rows = db.execute("""
            SELECT 
                S.StatID,
                S.GameID,
                G.Title AS GameTitle,
                S.StatName,
                S.StatValue
            FROM Statistics S
            JOIN Games G ON S.GameID = G.GameID
            ORDER BY G.Title, S.StatName
        """).fetchall()

        return render_template("view_table.html", rows=rows, table=table)

    # review table
    if table.lower() == "reviews":
        rows = db.execute("""
            SELECT 
                R.ReviewID,
                R.UserID,
                U.Name AS UserName,
                R.GameID,
                G.Title AS GameTitle,
                R.Rating,
                R.Comment,
                R.ReviewDate
            FROM Reviews R
            JOIN Users U ON R.UserID = U.UserID
            JOIN Games G ON R.GameID = G.GameID
            ORDER BY R.ReviewDate DESC
        """).fetchall()

        return render_template("view_table.html", rows=rows, table=table)

    # members table
    if table.lower() == "members":
        rows = db.execute("""
            SELECT 
                M.UserID,
                U.Name AS UserName,
                M.ForumID,
                F.Title AS ForumTitle,
                M.JoinedOn
            FROM Members M
            JOIN Users U ON M.UserID = U.UserID
            JOIN Forums F ON M.ForumID = F.ForumID
            ORDER BY ForumTitle, UserName
        """).fetchall()

        return render_template("view_table.html", rows=rows, table=table)

    try:
        rows = db.execute(f"SELECT * FROM {table}").fetchall()
    except Exception as e:
        return f"Error loading table '{table}': {e}", 400

    return render_template("view_table.html", rows=rows, table=table)

# sql querying inside the webpage
@app.route("/query", methods=["GET", "POST"])
def query():
    result = None
    error = None

    if request.method == "POST":
        sql = request.form["sql"]
        db = get_db()

        try:
            cursor = db.execute(sql)
            if sql.strip().lower().startswith("select"):
                result = cursor.fetchall()
            else:
                db.commit()
                result = f"{cursor.rowcount} rows affected"
        except Exception as e:
            error = str(e)

    return render_template("query.html", result=result, error=error)

# devs being able to add their game
@app.route("/developer/game/add", methods=["GET", "POST"])
def dev_add_game():
    if session.get("role") != "developer":
        return redirect(url_for("login"))

    db = get_db()
    dev_id = session["dev_id"]

    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        price = request.form["price"]

        # get today's release date
        db.execute("""
            INSERT INTO Games (Title, Genre, Price, ReleaseDate, DeveloperID)
            VALUES (?, ?, ?, DATE('now'), ?)
        """, (title, genre, price, dev_id))

        # new game ID
        game_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        # update creation table db with this new game
        db.execute("""
            INSERT INTO Creations (DeveloperID, GameID)
            VALUES (?, ?)
        """, (dev_id, game_id))

        db.commit()

        return redirect(url_for("developer_dashboard"))

    return render_template("dev_add_game.html")

# dev editing game prop
@app.route("/developer/game/<int:game_id>/edit", methods=["GET", "POST"])
def dev_edit_game(game_id):
    if session.get("role") != "developer":
        return redirect(url_for("login"))

    dev_id = session["dev_id"]
    db = get_db()

    # check if this game is from this developer
    game = db.execute("""
        SELECT G.*
        FROM Games G
        JOIN Creations C ON G.GameID = C.GameID
        WHERE G.GameID = ? AND C.DeveloperID = ?
    """, (game_id, dev_id)).fetchone()

    if not game:
        return "Unauthorized", 403

    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        price = request.form["price"]

        db.execute("""
            UPDATE Games
            SET Title=?, Genre=?, Price=?
            WHERE GameID=?
        """, (title, genre, price, game_id))

        db.commit()

        return redirect(url_for("developer_dashboard"))

    return render_template("dev_edit_game.html", game=game)

# dev deleting game
@app.route("/developer/game/<int:game_id>/delete", methods=["POST"])
def dev_delete_game(game_id):
    if session.get("role") != "developer":
        return redirect(url_for("login"))

    dev_id = session["dev_id"]
    db = get_db()

    # check if own
    game = db.execute("""
        SELECT 1
        FROM Creations
        WHERE GameID=? AND DeveloperID=?
    """, (game_id, dev_id)).fetchone()

    if not game:
        return "Unauthorized", 403

    # delete info from this game from db
    db.execute("DELETE FROM Creations WHERE GameID=?", (game_id,))
    db.execute("DELETE FROM Achievements WHERE GameID=?", (game_id,))
    db.execute("DELETE FROM Reviews WHERE GameID=?", (game_id,))
    db.execute("DELETE FROM Statistics WHERE GameID=?", (game_id,))
    
    # this is for purchases
    # db.execute("DELETE FROM Purchases WHERE GameID=?", (game_id,))

    db.execute("DELETE FROM Games WHERE GameID=?", (game_id,))
    db.commit()

    return redirect(url_for("developer_dashboard"))

# dev manage achievements
@app.route("/developer/game/<int:game_id>/achievements")
def dev_manage_achievements(game_id):
    if session.get("role") != "developer":
        return redirect(url_for("login"))

    dev_id = session["dev_id"]
    db = get_db()

    # check
    owned = db.execute("""
        SELECT 1
        FROM Creations
        WHERE DeveloperID = ? AND GameID = ?
    """, (dev_id, game_id)).fetchone()

    if not owned:
        return "Unauthorized", 403

    achievements = db.execute("""
        SELECT * FROM Achievements
        WHERE GameID = ?
    """, (game_id,)).fetchall()

    return render_template("dev_achievements.html", achievements=achievements, game_id=game_id)

# dev adding
@app.route("/developer/game/<int:game_id>/achievements/add", methods=["POST"])
def dev_add_achievement(game_id):
    if session.get("role") != "developer":
        return redirect(url_for("login"))

    db = get_db()
    title = request.form["title"]
    description = request.form["description"]

    db.execute("""
        INSERT INTO Achievements (GameID, Title, Description)
        VALUES (?, ?, ?)
    """, (game_id, title, description))

    db.commit()

    return redirect(url_for("dev_manage_achievements", game_id=game_id))

# main
@app.route("/")
def login_direct():

    return redirect(url_for("login"))


if __name__ == "__main__":

    
    app.run(debug=True)
