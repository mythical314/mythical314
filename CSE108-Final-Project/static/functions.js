const xhttp = new XMLHttpRequest();
const baseUrl = window.location.origin;//works dynamically with localhosting and production deployments like render
const async = true;


// NOTE: now is just meant to be a sign out button function
async function top_right_user_account_button_is_for_login_or_log_out(called_on_page_load, username = "") { //in the top right of website pages, there can be a button to view account info, log in, or log out. this function will determine whether a button is for logging in or logging out, and then do something baased on that

    logged_in = await user_is_logged_in(username);

    if (called_on_page_load) {//if called when the page was loaded
        //get whether the user is logged in and assign the button text to be log out if logged in and log in if not logged in

        button_text = "login or sign out";

        if (logged_in) {
            button_text = "sign out";
        }
        else {
            button_text = "log in";
        }

        button = document.getElementById("login and sign out button");

        button.textContent = button_text;
    }
    else {
        //go to login page or go to sign out page based on whether the user is signed in or logged out
        console.log("log in or sign out");


        sign_out_process();//log out the user
        changePage("/login_page");//send the user to the login page

        // if (logged_in) { //if logged in
        //     sign_out_process();//log out the user
        //     changePage("/login_page");//send the user to the login page
        // }
        // else { //if logged out
        //     changePage("/login_page");//go to login page
        // }

    }
}

//COMPLETED, BUT THE BACK END PART (PYTHON APP) IS NOT SINCE THERE IS A ROUTE AND FUNCTION BUT THE DATABASE FOR USERS IS NOT YET CREATED
async function user_is_logged_in(username) {
    logged_in = false;

    if (username === "")
        username = "-No User Sent In-";

    var request = new XMLHttpRequest();
    request.open("GET", "/check_if_user_is_logged_in/", true);
    request.onreadystatechange = function () {
    if (request.readyState === 4 && request.status === 200) {
        console.log(request.responseText);
        logged_in = request.responseText === "true";
    }
    };
    request.send();

    return logged_in;
}

async function fetchAndValidate(url, options = {}) {
    const response = await fetch(url, options);
    console.log(url)
    if (!response.ok) {
        await handleError(response);
        return null;
    }
    const text = await response.text();
    console.log(text);
    return JSON.parse(text);
}

async function login_process(){
    const username = document.getElementById("Username").value;
    const password = document.getElementById("Password").value;

    const data = await fetchAndValidate('/login', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username: username, password: password})
    });

    if (data) {
        if (data.success == true){
            window.location.href = data.redirect;
        } else {
            alert("Login Unsuccessful");
        }
    }
}

async function sign_out_process(){
    const data = await fetchAndValidate(`/logout`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
    });
    if (data) {
            window.location.href = data.redirect;
    }

}

function changePage(URL) {
    window.location.href = URL;
}


function clearTable(table){
    while (table.rows.length > 0){
        table.deleteRow(0);
    }
}

async function deleteThisQuiz(username, quiz_id){
    xhttp.open('DELETE', baseUrl + "/quiz_list/quizzes/" + username + "/" + quiz_id);
    xhttp.send();
}

async function populateUserQuizzes(username){
    //console.log(baseURL + "/quiz_list/fetch_questions/" + username);
    
    //send GET request to find all classes taught by current user
    xhttp.open('GET', baseUrl + "/quiz_list/quizzes/" + username, async);
    xhttp.send();

    xhttp.onload = function() {
        //clear table
        const table = document.getElementById("quiz_table");
        clearTable(table);

        //Load data from database
        let temp_quizzes = JSON.parse(xhttp.response); //Format: {row.id : [row.quiz_name, row.quiz_topic, row.quiz_private, row.quiz_length]}

        //For every row fetched
        for (let key in temp_quizzes){
            // Creating row w/cells
            let row = table.insertRow();
            let quiz_id = row.insertCell(0);
            let quiz_name = row.insertCell(1);
            let quiz_topic = row.insertCell(2);
            let quiz_private = row.insertCell(3);
            let quiz_length = row.insertCell(4);
            let quiz_edit = row.insertCell(5);
            let quiz_delete = row.insertCell(6);

            //Creating link to insert into the course cell
            const link = document.createElement('a');
            link.href = "../../../quiz_editor/" + username + "/" + key;
            link.textContent = "Edit";
            quiz_edit.appendChild(link);

            const button = document.createElement('button');
            button.textContent = "Delete";
            button.style.color = 'black';
            button.onclick= function(){
                deleteThisQuiz(username, quiz_id.textContent);
            }
            quiz_delete.appendChild(button);

            //Filling in the rest of the table
            quiz_id.innerHTML = key;
            quiz_name.innerHTML = temp_quizzes[key][0];
            quiz_topic.innerHTML = temp_quizzes[key][1];
            quiz_private.innerHTML = temp_quizzes[key][2];
            quiz_length.innerHTML = temp_quizzes[key][3];
        }
    };
}

async function populateQuizData(quiz_id){
    //send GET request to find all students in the current course
    xhttp.open('GET', baseUrl + "/quiz_editor/questions/" + quiz_id, async);
    xhttp.send();
    xhttp.onload = function() {
        //clear table
        const table = document.getElementById("question_table");
        const meta_table = document.getElementById("meta_table");
        clearTable(table);

        //Load data from database
        let temp_quiz_data = JSON.parse(xhttp.response); //Format: {student:grade}

        if (typeof temp_quiz_data === "string")//if is a string object
            temp_quiz_data = JSON.parse(temp_quiz_data);//parse it again to make it not a string

        
        //For every row fetched
        for (let key in temp_quiz_data){
            if(key !== "meta") {
                // Creating row w/cells
                let row = table.insertRow();
                let questionText = row.insertCell(0);
                let answer1 = row.insertCell(1);
                let answer2 = row.insertCell(2);
                let answer3 = row.insertCell(3);
                let answer4 = row.insertCell(4);
                let correct_answer = row.insertCell(5);
                //Filling in the rest of the table
                questionText.innerHTML = temp_quiz_data[key][0];
                answer1.innerHTML = temp_quiz_data[key][1];
                answer2.innerHTML = temp_quiz_data[key][2];
                answer3.innerHTML = temp_quiz_data[key][3];
                answer4.innerHTML = temp_quiz_data[key][4];
                correct_answer.innerHTML = temp_quiz_data[key][5];
            } else{
                let row = meta_table.rows[0];
                let name = row.cells[0];
                let topic = row.cells[1];
                let q_private = row.cells[2];
                let length = row.cells[3];
                let type = row.cells[4];

                name.innerHTML = temp_quiz_data["meta"][0];
                topic.innerHTML = temp_quiz_data["meta"][1];
                q_private.innerHTML = temp_quiz_data["meta"][2];
                length.innerHTML = temp_quiz_data["meta"][3];
                type.innerHTML = temp_quiz_data["meta"][4];

            }
        }
    };
}

async function saveQuizQuestions(username, quiz_id){
    let temp_data = {};

    //fetch table by ID
    const table = document.getElementById("question_table");
    const meta_table = document.getElementById("meta_table");
    const rows = table.rows;
    const meta_row = meta_table.rows[0].cells;

    let array = [meta_row[0].textContent.trim(), meta_row[1].textContent.trim(), meta_row[2].textContent.trim(), table.rows.length, meta_row[4].textContent.trim()]
    temp_data["meta"] = array;

    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].cells;
        if (cells.length >= 2) {
            let number = i + 1;
            let question = cells[0].textContent.trim();
            let answer1 = cells[1].textContent.trim();
            let answer2 = cells[2].textContent.trim();
            let answer3 = cells[3].textContent.trim();
            let answer4 = cells[4].textContent.trim();
            let correct_answer = cells[5].textContent.trim();
            let array = [question, answer1, answer2, answer3, answer4, correct_answer];
            temp_data[number] = array;
        }
    }

    xhttp.open("PUT", baseUrl + "/quiz_list/quizzes/" + username + "/" + quiz_id);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(temp_data));
    changePage('/quiz_list/' + username);
}

async function directToNewQuiz(username){
    changePage("/quiz_editor/" + username + "/new_quiz");
}

async function addQuizQuestion(){
    const table = document.getElementById("question_table");
    let row = table.insertRow();
    for (let i in [0, 1, 2, 3, 4, 5]){
        row.insertCell(i);
    }
}

async function deleteQuizQuestion(){
    const table = document.getElementById("question_table");
    table.deleteRow(-1);
}

async function populateChallengeQuizzes(username){
    xhttp.open('GET', baseUrl + "/challenge_creator/quizzes/" + username, async);
    xhttp.send();
    xhttp.onload = function() {
        //clear table
        const table = document.getElementById("quiz_table");
        clearTable(table);

        //Load data from database
        let temp_quiz_data = JSON.parse(xhttp.response); //Format: {student:grade}

        //For every row fetched
        for (let key in temp_quiz_data){
            // Creating row w/cells
            let row = table.insertRow();
            let name = row.insertCell(0);
            let topic = row.insertCell(1);
            let q_private = row.insertCell(2);
            let length = row.insertCell(3);
            let type = row.insertCell(4);
            let id = row.insertCell(5);


            const button = document.createElement('button');
            button.onclick = function(){
                changePage("/challenge_creator/" + username + "/" + key);
            }
            button.textContent = key;
            button.style.color = 'black';
            id.appendChild(button);


            //Filling in the rest of the table
            name.innerHTML = temp_quiz_data[key][0];
            topic.innerHTML = temp_quiz_data[key][1];
            q_private.innerHTML = temp_quiz_data[key][2];
            length.innerHTML = temp_quiz_data[key][3];
            type.innerHTML = temp_quiz_data[key][4];

        }
    };
}

async function populateChallengeFriends(username, quiz_id){
    xhttp.open('GET', baseUrl + "/challenge_creator/friends/" + username, async);
    xhttp.send();
    xhttp.onload = function() {
        //clear table
        const table = document.getElementById("friend_table");
        clearTable(table);

        //Load data from database
        let temp_quiz_data = JSON.parse(xhttp.response);

        //For every row fetched
        for (let key in temp_quiz_data){
            // Creating row w/cells
            let row = table.insertRow();
            let name = row.insertCell(0);
            let link= row.insertCell(1);
            let friend_name=temp_quiz_data[key][0]


            const button = document.createElement('button');
            button.onclick = function(){
                createChallenge(username, quiz_id, friend_name);
            }
            button.textContent = key;
            button.style.color = 'black';
            link.appendChild(button);

            //Filling in the rest of the table
            name.innerHTML = temp_quiz_data[key][0];
            // winrate.innerHTML = temp_quiz_data[key][1];
        }
    };
}

async function createChallenge(username, quiz_id, challenged_name){
    temp_data = {'data': [username, quiz_id, challenged_name]}
    xhttp.open("POST", baseUrl + "/challenge_creator");
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(temp_data));
    xhttp.onload = function() {
        let challenge_id = JSON.parse(xhttp.response);
        changePage('/challenge_quiz/' + username + "/" + challenge_id['data']);
    }
}

function clearTable(table){
    while (table.rows.length > 0){
        table.deleteRow(0);
    }
}

async function questionOne(username, challenge_id){
    changePage('/challenge_quiz/' + username + "/" + challenge_id + "/1");
}
    
async function checkAnswer(answer, username, challenge_id, current_question){
    let to_question = parseInt(current_question) + 1;
    if (answer !== 0){
        let temp_data = {"current_question": current_question, "answer": answer, "username": username, "challenge_id": challenge_id};
        xhttp.open("POST", baseUrl + "/challenge_quiz/answer");
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify(temp_data));
    }

    changePage('/challenge_quiz/' + username + "/" + challenge_id + "/" + to_question);
}

/* ----------------------------------------------------------------------------------------------------- */
/* -------------------------------         Friends Functions           --------------------------------- */
/* ----------------------------------------------------------------------------------------------------- */
// ================================================================================= //
//                              Friends List Page                                    //
// ================================================================================= //
async function populateFriendsList(username) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('GET', baseUrl + "/friends_list/" + username, true);
    xhttp.send();

    xhttp.onload = function () {
        const table = document.getElementById("friends_table");
        clearTable(table);
        if (xhttp.status !== 200) {
            console.error("Failed to load friends list:", xhttp.statusText);
            return;
        }

        let temp_friends = JSON.parse(xhttp.responseText);
        for (let friend in temp_friends) {
            const friendData = temp_friends[friend];
            let row = table.insertRow();
            let name = row.insertCell(0);
            let addFriend = row.insertCell(1);

            const fullname = friendData.fullname;
            const isRequestSent = friendData.isRequestSent;
            name.textContent = fullname;
            const button = document.createElement("button");
            if (isRequestSent) {
                button.innerText = "➖";
                button.onclick = function () {
                    revokeFriendRequest(username, friend);
                };
                button.style.color = "rgb(160, 30, 7)";
            } else {
                button.innerText = "➕";
                button.onclick = function () {
                    sendFriendRequest(username, friend);
                };
                button.style.color = "rgb(51, 113, 237)";
            }

            button.style.fontSize = "30px";
            button.style.margin = "0 auto";
            addFriend.appendChild(button);
        }
    };
}

function sendFriendRequest(senderUsername, receiverUsername) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('POST', baseUrl + '/send_friend_request', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify({
        sender_username: senderUsername,
        receiver_username: receiverUsername
    }));

    xhttp.onload = function () {
        if (xhttp.status === 200) {
            alert('Friend request sent!');
            populateFriendsList(senderUsername);
        } else {
            console.error('Error sending friend request:', xhttp.statusText);
        }
    };
}

function revokeFriendRequest(senderUsername, receiverUsername) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('POST', baseUrl + '/revoke_friend_request', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify({
        sender_username: senderUsername,
        receiver_username: receiverUsername
    }));

    xhttp.onload = function () {
        if (xhttp.status === 200) {
            alert('Friend request revoked!');
            populateFriendsList(senderUsername); 
        } else {
            console.error('Error revoking friend request:', xhttp.statusText);
        }
    };
}

// ================================================================================= //
//                              Pending Friends Page                                 //
// ================================================================================= //
async function populatePendingFriendsList(username) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('GET', baseUrl + "/pending_friends/" + username, true);
    xhttp.send();

    xhttp.onload = function () {
        const table = document.getElementById("pending_friends_table");
        clearTable(table);

        if (xhttp.status !== 200) {
            console.error("Failed to load pending requests:", xhttp.statusText);
            return;
        }
        let pendingRequests = JSON.parse(xhttp.responseText);

        for (let senderUsername in pendingRequests) {
            const senderData = pendingRequests[senderUsername];
            let row = table.insertRow();
            let name = row.insertCell(0);
            let accept = row.insertCell(1);
            let decline= row.insertCell(2);
            name.textContent = senderData.fullname;

            // Create Accept Button
            const acceptButton = document.createElement("button");
            acceptButton.innerText = "✔️";
            acceptButton.style.fontSize = "20px";
            acceptButton.onclick = function () {
                acceptFriendRequest(username, senderUsername); 
            };
            accept.appendChild(acceptButton);

            // Create Decline Button
            const declineButton = document.createElement("button");
            declineButton.innerText = "✖️";
            declineButton.style.fontSize = "20px";
            declineButton.onclick = function () {
                declineFriendRequest(username, senderUsername); 
            };
            decline.appendChild(declineButton);
        }
    };
}

function acceptFriendRequest(currentUsername, senderUsername) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('POST', baseUrl + '/accept_friend_request', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify({
        recipient_username: currentUsername,
        requester_username: senderUsername
    }));
    xhttp.onload = function () {
        if (xhttp.status === 200) {
            alert('Friend request accepted!');
            populatePendingFriendsList(currentUsername); 
            populateYourFriendsList(currentUsername);   
        } else {
            console.error('Error accepting friend request:', xhttp.statusText);
        }
    };
}

function declineFriendRequest(currentUsername, senderUsername) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('POST', baseUrl + '/decline_friend_request', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify({
        recipient_username: currentUsername,
        requester_username: senderUsername
    }));
    xhttp.onload = function () {
        if (xhttp.status === 200) {
            alert('Friend request declined!');
            populatePendingFriendsList(currentUsername); 
        } else {
            console.error('Error declining friend request:', xhttp.statusText);
        }
    };
}

async function populateYourFriendsList(username) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('GET', baseUrl + "/your_friends/" + username, true);
    xhttp.send();

    xhttp.onload = function () {
        const table = document.getElementById("your_friends_table");
        clearTable(table);

        if (xhttp.status !== 200) {
            console.error("Failed to load your friends:", xhttp.statusText);
            return;
        }
        let pendingRequests = JSON.parse(xhttp.responseText);

        for (let senderUsername in pendingRequests) {
            const senderData = pendingRequests[senderUsername];
            let row = table.insertRow();
            let name = row.insertCell(0);
            let remove= row.insertCell(1);
            name.textContent = senderData.fullname;

            // Create Remove Button
            const removeButton = document.createElement("button");
            removeButton.innerText = "✖️";
            removeButton.style.fontSize = "20px";
            removeButton.onclick = function () {
                removeFriend(username, senderUsername); 
            };
            remove.appendChild(removeButton);
        }
    };
}

function removeFriend(currentUsername, senderUsername) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('POST', baseUrl + '/remove_friend', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify({
        recipient_username: currentUsername,
        requester_username: senderUsername
    }));
    xhttp.onload = function () {
        if (xhttp.status === 200) {
            alert('Friend removed!');
            populateYourFriendsList(currentUsername); 
        } else {
            console.error('Error removing friend:', xhttp.statusText);
        }
    };
}

// ================================================================================= //
//                                 Inbox Page                                        //
// ================================================================================= //
async function populatePendingChallenges(username) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('GET', baseUrl + "/pending_challenges/" + username, true);
    xhttp.send();

    xhttp.onload = function () {
        const table = document.getElementById("pending_challenges_table");
        clearTable(table);

        if (xhttp.status !== 200) {
            console.error("Failed to load pending challenges:", xhttp.statusText);
            return;
        }
        let pendingChallenges = JSON.parse(xhttp.responseText);

        for (let senderUsername in pendingChallenges) {
            const senderData = pendingChallenges[senderUsername];
            let row = table.insertRow();
            let challenger = row.insertCell(0);
            let accept = row.insertCell(1);
            let decline= row.insertCell(2);
            challenger.textContent = senderData.fullname;

            // Create Accept Button
            const acceptButton = document.createElement("button");
            acceptButton.innerText = "✔️";
            acceptButton.style.fontSize = "20px";
            acceptButton.onclick = function () {
                acceptChallenge(username, senderUsername); 
            };
            accept.appendChild(acceptButton);

            // Create Decline Button
            const declineButton = document.createElement("button");
            declineButton.innerText = "✖️";
            declineButton.style.fontSize = "20px";
            declineButton.onclick = function () {
                declineChallenge(username, senderUsername); 
            };
            decline.appendChild(declineButton);
        }
    };
}

function acceptChallenge(currentUsername, senderUsername) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('POST', baseUrl + '/inbox/accept_challenge', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify({
        recipient_username: currentUsername,
        requester_username: senderUsername
    }));
    xhttp.onload = function () {
        if (xhttp.status === 200) {
            try {
                const response = JSON.parse(xhttp.responseText);
                if (response.redirect_url) {
                    window.location.href = response.redirect_url;
                } else {
                    alert('Challenge accepted!');
                    populatePendingChallenges(currentUsername);
                }
            } catch (error) {
                console.error('Error parsing JSON response:', error);
                alert('Error processing server response.');
            }
        } else {
            console.error('Error accepting challenge:', xhttp.statusText);
            alert('Failed to accept challenge.');
        }
    };
}

function declineChallenge(currentUsername, senderUsername) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('POST', baseUrl + '/inbox/decline_challenge', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify({
        recipient_username: currentUsername,
        requester_username: senderUsername
    }));
    xhttp.onload = function () {
        if (xhttp.status === 200) {
            alert('Challenge declined!');
            populatePendingChallenges(currentUsername); 
        } else {
            console.error('Error declining challenge:', xhttp.statusText);
        }
    };
}

async function populateCompletedChallenges(username) {
    const xhttp = new XMLHttpRequest();
    xhttp.open('GET', baseUrl + "/completed_challenges/" + username, true); 
    xhttp.send();

    xhttp.onload = function () {
        const table = document.getElementById("completed_challenges_table");
        clearTable(table);

        if (xhttp.status !== 200) {
            console.error("Failed to load completed challenges:", xhttp.statusText);
            return;
        }

        try {
            const completedChallenges = JSON.parse(xhttp.responseText);
            for (const challenge of completedChallenges) {
                const row = table.insertRow();
                const challengerName = row.insertCell(0);
                const challengerScore = row.insertCell(1);
                const yourScore = row.insertCell(2);

                challengerName.textContent = challenge.challenger_name;
                challengerScore.textContent = challenge.challenger_score;
                yourScore.textContent = challenge.your_score;    
            }

        } catch (error) {
            console.error('Error parsing JSON for completed challenges:', error);
        }
    };
}
