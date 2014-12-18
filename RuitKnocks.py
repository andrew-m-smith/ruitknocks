from flask import Flask, render_template, url_for, request, jsonify
import sys
import sqlite3
import smtplib
import re
import datetime
import inspect
import os.path

app = Flask(__name__)
currentGame = []
debug = False
newDB = False

def __conn():
    db = 'rut.db'
    if debug:
        db = 'test.db'
    return sqlite3.connect(db)


def __log(msg, file):
    l = open('logs/'+file+'.log', 'a')
    l.write(datetime.datetime.now().strftime('At %H:%M:%S On %m-%d-%y : '))
    l.write(msg)
    l.write('\n')
    l.close()

def __newTables():
    try:
        conn = __conn()
        cur = conn.cursor()
        cur.execute("ALTER TABLE games ADD COLUMN team1player1cups INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE games ADD COLUMN team1player2cups INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE games ADD COLUMN team2player1cups INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE games ADD COLUMN team2player2cups INTEGER DEFAULT 0")
        conn.commit()
        conn.close()
        __log("New database schema set up successfully", "db")
        return True
    except Exception, e:
        msg = inspect.stack()[1][3]+' : '+str(e)
        __log("There was an error in setting up new schema. See Error Logs for more details.", "db")
        __log(msg, "error")
        return False

def setupDebug():
    try:
        p = open('rut.db','r')
        data = p.read()
        p.close()
        p = open('test.db','w')
        p.write(data)
        p.close()
        __log("Debug database set up successfully", "db")
        return True
    except Exception, e:
        msg = inspect.stack()[1][3]+' : '+str(e)
        __log("There was an error in debug mode. See Error Logs for more details.", "db")
        __log(msg, "error")
        return False



def setupDB():
    try:
        conn = __conn()
        cur = conn.cursor()
        cur.execute('CREATE TABLE players (pid INTEGER PRIMARY KEY, fname VARCHAR(255), lname VARCHAR(255), wins INTEGER, losses INTEGER, phone INTEGER, carrier VARCHAR(255))')
        cur.execute('CREATE TABLE teams (tid INTEGER PRIMARY KEY , pid1 INTEGER REFERENCES players(pid), pid2 INTEGER REFERENCES players(pid), wins INTEGER, losses INTEGER)')
        cur.execute('CREATE TABLE games (gid INTEGER PRIMARY KEY, tid1 INTEGER REFERENCES teams(tid), tid2 INTEGER REFERENCES teams(tid), cups1 INTEGER DEFAULT 0, cups2 INTEGER DEFAULT 0, team1player1cups INTEGER DEFAULT 0, team1player2cups INTEGER DEFAULT 0, team2player1cups INTEGER DEFAULT 0, team2player2cups INTEGER DEFAULT 0)')
        cur.execute('CREATE TABLE knocks (tid INTEGER REFERENCES teams(tid))')
        cur.execute('CREATE TABLE carriers (name VARCHAR(255), address VARCHAR(255))')
        conn.commit()
        conn.close()
        addCarrier("T-Mobile", "tmomail.net")
        addCarrier("Verizon", "vtext.com")
        addCarrier("AT&T", "text.att.net")
        addCarrier("Sprint", "messaging.sprintpcs.com")
        addCarrier("Virgin Mobile", "vmobl.com")
        addCarrier("MetroPCS", "mymetropcs.com")
        addCarrier("Alltel", "message.alltel.com")
        addCarrier("Credo", "messaging.sprintpcs.com")
        __log("Database set up successfully", "db")
        return True
    except Exception, e:
        msg = inspect.stack()[1][3]+' : '+str(e)
        __log("There was an error. See Error Logs for more details.", "db")
        __log(msg, "error")
        return False


def addCarrier(name, address):
    conn = __conn()
    cur = conn.cursor()
    t = (name, address)
    cur.execute('INSERT INTO carriers (name, address) values (?, ?)', t)
    conn.commit()
    conn.close()
    __log("Carrier: " + name + " added", "db")


def getCarriers():
    conn = __conn()
    cur = conn.cursor()
    cur.execute('SELECT name FROM carriers')
    r = cur.fetchall()
    conn.close()
    n = ()
    for row in r:
        n = n + row
    return n


def textSend(pid):
    t = (pid,)
    conn = __conn()
    cur = conn.cursor()
    cur.execute('SELECT players.phone, players.fname, carriers.address FROM players JOIN carriers ON carriers.name = players.carrier WHERE players.pid = ?', t)
    n = cur.fetchone()
    conn.close()
    fromaddr = "yougotknocks@gmail.com"
    toaddr = "%s@%s" % (str(n[0]), str(n[2]))
    msg = "To: %s\nFrom: Beirut\nSubject: Hey %s\n It's your turn to play!" % (str(n[1]), str(n[1]))
    username = "yougotknocks"
    password = "Knocks12345"
    if debug:
        msg = "Text sent to " + str(n[0]) + " from debug mode"
        __log(msg, "email")
    else:
        try:
            server = smtplib.SMTP("smtp.gmail.com:587")
            server.starttls()
            server.login(username, password)
            server.sendmail(fromaddr, toaddr, msg)
            server.quit()
            msg = "Text sent to " + str(n[0])
            __log(msg, "email")
        except Exception, e:
            msg = inspect.stack()[1][3]+' : '+str(e)
            __log("There was an error. See Error Logs for more details.", "email")
            __log(msg, "error")


def getPlayer(pid):
    conn = __conn()
    cur = conn.cursor()
    t = (pid,)
    cur.execute('SELECT * FROM players WHERE pid=?', t)
    r = cur.fetchone()
    conn.close()
    return r


def getTeamFromPlayers(pid1, pid2):
    conn = __conn()
    cur = conn.cursor()
    t = (pid1, pid2, pid1, pid2)
    cur.execute('SELECT tid FROM teams WHERE (pid1=? AND pid2=?) OR (pid2=? AND pid1=?)', t)
    r = cur.fetchone()
    conn.close()
    if r is None:
        return r
    else:
        return r[0]


def getTeamPlayers(tid):
    conn = __conn()
    cur = conn.cursor()
    t = (tid,)
    cur.execute('SELECT fname, lname FROM teams JOIN players ON teams.pid1 = players.pid WHERE tid = ?', t)
    p1 = cur.fetchone()
    cur.execute('SELECT fname, lname FROM teams JOIN players ON teams.pid2 = players.pid WHERE tid = ?', t)
    p2 = cur.fetchone()
    conn.close()
    if p1 is None or p2 is None:
        return None
    else:
        return "%s %s and %s %s" % (p1[0], p1[1], p2[0], p2[1])


def getTeamPids(tid):
    conn = __conn()
    cur = conn.cursor()
    t = (str(tid),)
    cur.execute('SELECT pid1, pid2 FROM teams WHERE tid = ?', t)
    p = cur.fetchone()
    conn.close()
    return p


def addPlayer(pid, fname, lname, phone, carrier):
    conn = __conn()
    cur = conn.cursor()
    t = (pid, fname, lname, phone, carrier)
    cur.execute('INSERT INTO players (pid, fname, lname, phone, carrier, wins, losses) values (?, ?, ?, ?, ?, 0, 0)', t)
    conn.commit()
    conn.close()
    msg = ("Added Player:", fname, lname, "ID:", pid, "Phone:", phone, "Carrier:", carrier)
    __log(" ".join(msg), "player")


def addTeam(pid1, pid2):
    conn = __conn()
    cur = conn.cursor()
    t = (pid1, pid2)
    cur.execute('INSERT INTO teams (pid1, pid2, wins, losses) values (?, ?, 0, 0)', t)
    cur.execute('SELECT tid FROM teams ORDER BY tid DESC LIMIT 1')
    r = cur.fetchone()[0]
    conn.commit()
    conn.close()
    msg = ("Team created: PID1:", str(pid1), "PID2:", str(pid2), "Team:", str(r))
    __log(" ".join(msg), "team")
    return r


def teamKnock(tid):
    conn = __conn()
    cur = conn.cursor()
    t = (tid,)
    cur.execute('INSERT INTO knocks (tid) values (?)', t)
    conn.commit()
    conn.close()
    msg = "Team "+str(tid)+" knocked"
    __log(msg, "team")


def checkKnock(tid):
    r = getCurrentGame()
    if tid == r[1] or tid == r[2]:
        return -1
    else:
        conn = __conn()
        cur = conn.cursor()
        cur.execute('SELECT tid FROM knocks')
        r = cur.fetchall()
        conn.close()
        for row in range(0, len(r)):
            if r[row][0] == tid:
                return row
        return None


def getKnocksList():
    try:
        conn = __conn()
        cur = conn.cursor()
        cur.execute('SELECT teams.tid FROM knocks INNER JOIN teams ON knocks.tid = teams.tid LIMIT 5')
        r = cur.fetchall()
        conn.close()
        return r
    except Exception, e:
        return e


def playTeam():
    conn = __conn()
    cur = conn.cursor()
    cur.execute('SELECT tid FROM knocks LIMIT 1')
    r = cur.fetchone()
    if r is None:
        conn.close()
        return r
    else:
        t = (r[0],)
        cur.execute('DELETE FROM knocks WHERE tid = ?', t)
        cur.execute('SELECT pid1, pid2 FROM teams WHERE tid = ?', t)
        p = cur.fetchone()
        conn.commit()
        conn.close()
        textSend(p[0])
        textSend(p[1])
        msg = "Team " + str(r[0]) + " is now playing"
        __log(msg, "team")
        __log(msg, "game")
        return r[0]


def getWinner():
    conn = __conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM games ORDER BY gid DESC LIMIT 1')
    r = cur.fetchone()
    conn.close()
    p1 = r[3]
    p2 = r[4]
    tid1 = r[1]
    tid2 = r[2]
    if p1 > p2:
        addWin(tid1)
        addLose(tid2)
        __log("Team "+str(tid1)+" won against Team "+str(tid2), "game")
        return tid1
    else:
        addWin(tid2)
        addLose(tid1)
        __log("Team "+str(tid2)+" won against Team "+str(tid1), "game")
        return tid2


def addWin(tid):
    players = getTeamPlayers(tid)
    conn = __conn()
    cur = conn.cursor()
    t1 = (tid,)
    t2 = (players[0], players[1])
    cur.execute('UPDATE teams SET wins = wins + 1 WHERE tid = ?', t1)
    cur.execute('UPDATE players set wins = wins + 1 WHERE pid = ? OR pid = ?', t2)
    conn.commit()
    conn.close()


def addLose(tid):
    players = getTeamPlayers(tid)
    conn = __conn()
    cur = conn.cursor()
    t1 = (tid,)
    t2 = (players[0], players[1])
    cur.execute('UPDATE teams SET losses = losses + 1 WHERE tid = ?', t1)
    cur.execute('UPDATE players set losses = losses + 1 WHERE pid = ? OR pid = ?', t2)
    conn.commit()
    conn.close()


def addGame(tid1, tid2):
    conn = __conn()
    cur = conn.cursor()
    t = (tid1, tid2)
    cur.execute('INSERT INTO games (tid1, tid2, cups1, cups2) values (?, ?, 0, 0)', t)
    conn.commit()
    conn.close()


def getCurrentGame():
    conn = __conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM games WHERE cups1 = 0 AND cups2 = 0 ORDER BY gid DESC LIMIT 1')
    r = cur.fetchone()
    conn.close()
    if r is None:
        r = [None, None, None]
    return r


def endGame(t1p1, t1p2, t2p1, t2p2):
    gid = getCurrentGame()[0]
    conn = __conn()
    cur = conn.cursor()
    t = (int(t1p1)+int(t1p2), int(t2p1)+int(t2p2), t1p1, t1p2, t2p1, t2p2, gid)
    cur.execute('UPDATE games SET cups1=?, cups2=?, team1player1cups=?, team1player2cups=?, team2player1cups=?, team2player2cups=? WHERE gid=?', t)
    conn.commit()
    conn.close()


def cancelKnock(tid):
    conn = __conn()
    cur = conn.cursor()
    t = (tid,)
    cur.execute('DELETE FROM knocks WHERE tid = ?', t)
    conn.commit()
    conn.close()
    msg = "Team "+str(tid)+" cancelled knocks"
    __log(msg, "team")


def clearKnocksTables():
    try:
        conn = __conn()
        cur = conn.cursor()
        cur.execute('DELETE FROM knocks')
        conn.commit()
        conn.close()
        __log("Table 'knocks' cleared.", "db")
        return True
    except Exception, e:
        msg = inspect.stack()[1][3]+' : '+str(e)
        __log("There was an error. See Error Logs for more details.", "db")
        __log(msg, "error")
        return False


def clearAllTables():
    try:
        conn = __conn()
        cur = conn.cursor()
        cur.execute('DELETE FROM knocks')
        cur.execute('DELETE FROM players')
        cur.execute('DELETE FROM games')
        cur.execute('DELETE FROM teams')
        conn.commit()
        conn.close()
        __log("All tables cleared.", "db")
        return True
    except Exception, e:
        msg = inspect.stack()[1][3]+' : '+str(e)
        __log("There was an error. See Error Logs for more details.", "db")
        __log(msg, "error")
        return False


def checkPlayer(pid):
    if getPlayer(pid) is None:
        return 2
    knocks = getKnocksList()
    currentGame = getCurrentGame()
    if currentGame[0] is not None:
        knocks.append((currentGame[1],))
        knocks.append((currentGame[2],))
    for i in knocks:
        pids = getTeamPids(i[0])
        if pids is None:
            pass
        elif int(pid) == pids[0] or int(pid) == pids[1]:
            return 1
    else:
        return 0

def makeJSON(response):
    try:
        knocks = []
        knocksList = getKnocksList()
        for i in knocksList:
            knocks.append(getTeamPlayers(i[0]))
        r = getCurrentGame()
        if r is None:
            teamOne = None
            teamTwo = None
        else:
            teamOne = getTeamPlayers(r[1])
            teamTwo = getTeamPlayers(r[2])
        myCurrentGame = [teamOne, teamTwo]
        carriers = getCarriers()
        myJSON = {}
        myJSON['response'] = response
        myJSON['knocks'] = knocks
        myJSON['currentGame'] = myCurrentGame
        myJSON['carriers'] = carriers
        return jsonify(myJSON)
    except Exception, e:
        return e

@app.errorhandler(404)
@app.route("/")
def index(*opts):
    js = url_for('static', filename='ruitknocks.js')
    jquery = url_for('static', filename='jquery.min.js')
    banner = url_for('static', filename='banner.png')
    style = url_for('static', filename='style.css')
    font = url_for('static', filename='fonts/Snickles/stylesheet.css')
    return render_template("knocks.html", jquery=jquery, js=js, banner=banner, style=style, font=font)

@app.route("/start", methods=["GET", "POST"])
def start():
    return makeJSON("")


@app.route("/knock", methods=["GET", "POST"])
def knock():
    if request.method == "POST":
        playerOne = request.form["playerOne"]
        playerOneStatus = checkPlayer(playerOne)
        playerTwo = request.form["playerTwo"]
        playerTwoStatus = checkPlayer(playerTwo)
        if playerOne == playerTwo:
            return makeJSON("Go find a partner!")
        if playerOneStatus == 1 and playerTwoStatus != 1:
            return makeJSON("Player One already has knocks or is playing.")
        if playerTwoStatus == 1 and playerOneStatus != 1:
            return makeJSON("Player Two already has knocks or is playing.")
        if playerOneStatus == 2 and playerTwoStatus == 2:
            return makeJSON("Neither of you are in the system!")
        if playerOneStatus == 2:
            return makeJSON("Player One is not in the system!")
        if playerTwoStatus == 2:
            return makeJSON("Player Two is not in the system!")
        team = getTeamFromPlayers(playerOne, playerTwo)
        if team is None:
            team = addTeam(playerOne, playerTwo)
        knock = checkKnock(team)
        if knock == -1:
            return makeJSON("You are on the table!")
        elif knock is not None:
            return makeJSON("You have already knocked!")
        elif playerOneStatus == 1 and playerTwoStatus == 1:
            return makeJSON("You both have knocks with other players.")
        else:
            teamKnock(team)
        knock = checkKnock(team)
        if knock is None:
            return makeJSON("There was an error. Please try again.")
        elif knock == -1:
            return makeJSON("It is your turn to play!")
        elif getCurrentGame()[0] is None:
            if len(getKnocksList()) == 2:
                addGame(playTeam(), playTeam())
                return makeJSON("It is your turn to play!")
            else:
                return makeJSON("It is your turn to play, but nobody else has knocks yet.")
        elif knock == 0:
            return makeJSON("You are next on the table!")
        elif knock == 1:
            return makeJSON("There is 1 team ahead of you.")
        else:
            return makeJSON("There are %s teams ahead of you." % str(knock))
    else:
        return makeJSON("There was an error. Please try again.")


@app.route("/cancel", methods=["GET", "POST"])
def cancel():
    if request.method == "POST":
        playerOne = getPlayer(request.form["playerOne"])
        if playerOne is None:
            return makeJSON("Player One is not in the system!")
        playerTwo = getPlayer(request.form["playerTwo"])
        if playerTwo is None:
            return makeJSON("Player Two is not in the system!")
        team = getTeamFromPlayers(playerOne[0], playerTwo[0])
        if team is None:
            return makeJSON("You do not have knocks.")
        knock = checkKnock(team)
        if knock is None:
            return makeJSON("You do not have knocks.")
        else:
            cancelKnock(team)
            return makeJSON("You no longer have knocks.")
    else:
        return makeJSON("There was an error. Please try again.")


@app.route("/check", methods=["GET", "POST"])
def check():
    if request.method == "POST":
        playerOne = getPlayer(request.form["playerOne"])
        if playerOne is None:
            return makeJSON("Player One is not in the system!")
        playerTwo = getPlayer(request.form["playerTwo"])
        if playerTwo is None:
            return makeJSON("Player Two is not in the system!")
        team = getTeamFromPlayers(playerOne[0], playerTwo[0])
        if team is None:
            return makeJSON("You do not have knocks.")
        knock = checkKnock(team)
        if knock is None:
            return makeJSON("You do not have knocks.")
        elif knock == -1:
            return makeJSON("You are on the table!")
        elif knock == 0:
            return makeJSON("You are next on the table!")
        elif knock == 1:
            return makeJSON("There is 1 team ahead of you.")
        else:
            return makeJSON("There are %s teams ahead of you." % str(knock))
    else:
        return makeJSON("There was an error. Please try again.")


@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        pid = request.form["playerID"]
        player = checkPlayer(pid)
        if player is not 2:
            return makeJSON("You are already in the system!")
        fname = request.form["firstName"]
        lname = request.form["lastName"]
        phone = request.form["phoneNumber"]
        carrier = request.form["carrier"]
        if carrier not in getCarriers():
            return makeJSON("Your carrier is not supported.")
        addPlayer(pid, fname, lname, phone, carrier)
        return makeJSON("You were successfully added to the system!")
    else:
        return makeJSON("There was an error. Please try again.")


@app.route("/end", methods=["GET", "POST"])
def end():
    if request.method == "POST":
        cupsOne = request.form["cupsOne"]
        cupsTwo = request.form["cupsTwo"]
        cupsThree = request.form["cupsThree"]
        cupsFour = request.form["cupsFour"]
        endGame(cupsOne, cupsTwo, cupsThree, cupsFour)
        winner = getWinner()
        if len(getKnocksList()) > 0:
            nextTeam = playTeam()
            addGame(winner, nextTeam)
            return makeJSON("Congratulations %s!\nYour next opponents are %s" % (getTeamPlayers(winner), getTeamPlayers(nextTeam)))
        else:
            teamKnock(winner)
            return makeJSON("Congratulations %s!\nNobody else has knocks yet." % getTeamPlayers(winner))
    else:
        return makeJSON("There was an error. Please try again.")


@app.route("/clearAll", methods=["GET", "POST"])
def clearAll():
    if not debug:
        return index()
    elif clearAllTables():
        return "Successfully cleared tables"
    else:
        return "There was an error"


@app.route("/clearKnocks", methods=["GET", "POST"])
def clearKnocks():
    if not debug:
        return index()
    elif clearKnocksTables():
        return "Successfully cleared knocks"
    else:
        return "There was an error"


@app.route("/setup", methods=["GET", "POST"])
def setup():
    if not debug:
        return index()
    elif setupDB():
        return "Successfully setup database"
    else:
        return "There was an error"


def main():
	if debug:
		if not setupDebug():
			sys.exit("Error in database setup.")
		if newDB:
			if not __newTables():
				sys.exit("Error in new schema.")
	app.run(debug=debug, host='0.0.0.0', port=80)


if __name__ == '__main__':
    if not os.path.isfile('rut.db'):
        if not setupDB():
        	sys.exit("Error in database setup.")
    for arg in sys.argv:
        if arg == '-d':
            debug = True
        elif arg == '-n':
            debug = True
            newDB = True
    main()
