const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
let mysql = require('mysql');
let moment = require('moment');

require('dotenv').config({path: ".env"});
const db_config = require('./db_config');
const app = express();

let connection = mysql.createConnection(db_config);

connection.connect((err) => {
    console.log('Connection done');
});

connection.on('error', function onError(err) {
    console.log('db error', err);
    throw err;
});

function refreshConnection() {
    if(connection.state !== "authenticated") {
        console.log("Refreshing connection");
        connection = mysql.createConnection(db_config);
        connection.connect((err) => {
            console.log('Connection done');
        });
    }
}

function formatDateUser(date) {
    let tdate = moment(date);
    return tdate.format("DD/MM/YYYY");
}

function formatDateServer(date) {
    if (date !== null) {
        if (/^[0-9]{2}\/[0-9]{2}\/[0-9]{4}$/.test(date)) {
            const [day, month, year] = date.split("/");
            return year + "-" + month + "-" + day;
        }
        return date.substring(0, 10);
    }
    return null;
}

function formatString(string) {
    return string.trim().toLowerCase();
}

function generateRef(use) {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let refLength = 6; //62 characters used for 6 chars long ref is enough and bring theoretically 56.8B possibilities
    let result = 'RF';
    if (use === "hotel") {
        refLength = 8;
        result = 'BK';
    }
    for (let i = 0; i < refLength; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    //TODO tester que la ref n'existe pas déjà
    return result;
}

//parses request body and populates request.body
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

//Where to serve static content
// app.use(express.static(path.join(__dirname, "..", process.env.BUILD_PATH)));

// app.get('/api/tickets/:id', (req, res) => {
//     //get ticket information by ref
//
//     const sql="SELECT * FROM Tickets WHERE ticketRef= ?";
//
//     refreshConnection();
//     connection.query(sql, [req.params.id],(err, results, fields) => {
//         if (!err) {
//             res.send(results[0]);
//             console.log('Result sent');
//         }
//         else {
//             res.send('error during query: ' + err.message);
//             return console.error('error during query: ' + err.message);
//         }
//     });
// });
//
// app.get('/api/tickets', (req, res) => {
//     //get all tickets with account ID
//
//     const sql="SELECT * FROM Tickets WHERE accountID= ?";
//
//     refreshConnection();
//     connection.query(sql, [req.query.accountID],(err, results, fields) => {
//         if (!err) {
//             if (results.length !== 0) {
//                 for(let result of results) {
//                     result.ticketValidityStartDate = formatDateUser(result.ticketValidityStartDate);
//                     result.ticketValidityEndDate = formatDateUser(result.ticketValidityEndDate);
//                 }
//                 res.send(results);
//                 console.log('Result sent');
//             }
//             else {
//                 res.statusCode = 404;
//                 res.send("No tickets related to this account ID");
//             }
//         }
//         else {
//             res.statusCode = 404;
//             res.send("No tickets related to this account ID");
//             return console.error('error during query: ' + err.message);
//         }
//     });
// });
//
// app.post('/api/tickets', (req, res) => {
//     //add a json type ticket object to the database
//     let ticket = req.body;
//     let accountID = null;
//     const sql="INSERT INTO Tickets (`ticketRef`, `ticketValidityStartDate`, `ticketValidityEndDate`, `ticketType`, `visitorAge`, `visitorFirstName`, `visitorLastName`, `accountID`, `email`, `price`)" +
//         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
//
//     console.log(ticket);
//     refreshConnection();
//     if (ticket.connected) {
//         connection.query("SELECT `accountID` FROM `Accounts` WHERE email= ?", [ticket.email],(err, results, fields) => {
//             if (!err) {
//                 if (results.length !== 0) {
//                     accountID = results[0].accountID;
//                 }
//                 addTickets();
//             }
//             else {
//                 res.send('error during query: ' + err.message);
//                 return console.error('error during query: ' + err.message);
//             }
//         });
//     } else {
//         addTickets();
//     }
//
//     function addTickets() {
//         const ref = generateRef();
//         connection.query(sql, [ref, formatDateServer(ticket.ticketStartDate), formatDateServer(ticket.ticketEndDate), ticket.ticketType, ticket.visitorAge, ticket.visitorFirstName, ticket.visitorLastName, accountID, ticket.email, ticket.price],(err, results, fields) => {
//             if (!err) {
//                 res.send(ref);
//                 console.log('Result sent');
//             }
//             else {
//                 res.send('error during query: ' + err.message);
//                 return console.error('error during query: ' + err.message);
//             }
//         });
//     }
// });
//
// app.get('/api/account', (req, res) => {
//     //get account information by email
//
//     const sql="SELECT `accountID`, `firstName`, `lastName`, `email`, `birthDate`, `phoneNumber`, `newsLetterSubscription` FROM `Accounts` WHERE email= ?";
//
//     refreshConnection();
//     connection.query(sql, [req.query.email],(err, results, fields) => {
//         if (!err) {
//             if (results.length !== 0) {
//                 results[0].birthDate = formatDateUser(results[0].birthDate);
//                 res.send(results[0]);
//                 console.log('Result sent');
//             }
//             else {
//                 res.statusCode = 404;
//                 res.send("This account doesn't exist");
//             }
//         }
//         else {
//             res.statusCode = 404;
//             res.send("This account doesn't exist");
//             return console.error('error during query: ' + err.message);
//         }
//     });
// });
//
// app.post('/api/account/register', (req, res) => {
//     //add a json type account object to the database
//
//     let account = req.body;
//     let cypheredPassword = "";
//
//     const sql="INSERT INTO `Accounts`(`firstName`, `lastName`, `birthDate`, `email`, `password`, `phoneNumber`, `newsLetterSubscription`) " +
//         "VALUES (?, ?, ?, ?, ?, ?, ?)";
//
//     refreshConnection();
//     bcrypt.hash(account.password, 10, function(err, hash) {
//         if (!err) {
//             cypheredPassword = hash;
//         }
//         else {
//             cypheredPassword = account.password;
//         }
//         connection.query(sql, [formatString(account.firstName), formatString(account.lastName), formatDateServer(account.birthDate), formatString(account.email), cypheredPassword, account.phoneNumber, account.newsLetter],(err, results, fields) => {
//             if (!err) {
//                 res.statusCode = 201;
//                 res.send(results);
//                 console.log('Result sent');
//             }
//             else {
//                 res.statusCode = 409;
//                 res.send(err.code);
//                 return console.error('error during query: ' + err.code);
//             }
//         });
//     });
// });
//
// app.patch('/api/account/update', (req, res) => {
//     //update a json type account object in the database
//
//     let updateData = req.body;
//     console.log(updateData);
//     console.log(req.query.email);
//
//     const sql="UPDATE `Accounts` SET " + formatString(updateData.key) + "= ? WHERE `email`= ?";
//
//     refreshConnection();
//     switch (updateData.key) {
//         case "birthDate":
//             updateData.value = formatDateServer(updateData.value);
//             console.log(updateData.value);
//             break;
//         default:
//             updateData.value = formatString(updateData.value);
//     }
//     connection.query(sql, [updateData.value, req.query.email], (err, results, fields) => {
//         if (!err) {
//             res.statusCode = 200;
//             res.send(results);
//             console.log('Result sent');
//         }
//         else {
//             if (err.code !== "ER_PARSE_ERROR") {
//                 res.statusCode = 404;
//                 res.send("This account doesn't exist");
//                 return console.error('No such account exist: ' + err.code);
//             }
//         }
//     });
// });
//
// app.post('/api/account/login', (req, res) => {
//     //check if credentials match account object
//
//     let creds = req.body;
//     const sql="SELECT `password` FROM `Accounts` WHERE `email`= ?";
//
//     refreshConnection();
//     connection.query(sql, [formatString(creds.email)],(err, results, fields) => {
//         if (!err) {
//             bcrypt.compare(creds.password, results[0].password, function(err, result) {
//                 if (result) {
//                     res.statusCode = 200;
//                     res.send(creds.email);
//                 }
//                 else {
//                     res.statusCode = 401;
//                     res.send("Password invalid");
//                 }
//             });
//         }
//         else {
//             res.statusCode = 404;
//             res.send("This account doesn't exist");
//             return console.error('No such account exist: ' + err.code);
//         }
//     });
// });

app.get('/api/*', (req, res) => {
    res.send("Ransomware Protection System (RPS) API endpoint\nStatus: " + connection.state);
});

// app.get('/*', (req, res) => {
//     try {
//         res.sendFile(path.join(__dirname, '..', process.env.BUILD_PATH, 'index.html'));
//     }
//     catch (error) {
//         console.log(error);
//     }
// });

app.listen(process.env.PORT || process.env.SERVER_PORT, () => {
    console.log("===============================================");
    console.log("Application is started and listening on port " + process.env.SERVER_PORT);
    console.log("Access the server on: http://localhost:" + process.env.SERVER_PORT);
});
