import EventHandler

# Start the bot
EventHandler.startup()
# Read message every loop,  act accordingly

# Sneasel List
id_list = []
with open("version.txt", "r") as versionFile:
    version = versionFile.read()
# Dev list: command channel[0], jogger[1], pikachu[2],
#           support[3], battlegirl[4], pokedex[5],
#           collector[6], scientist[7], breeder[8], 
#           backpacker[9], fisherman[10], youngster[11], 
#           berrymaster[12], gymleader[13], champion[14], 
#           battlelegend[15], ranger[16], unown[17],
#           gentleman[18], pilot[19], totalxp[20]
#
if version == "1":
    id_list = ['466563505462575106', '466913214656020493', '467754615413407745',
               '468760503125147648', '469079191002939415', '469121554488360971',
               '469121572523737098', '469121587807780864', '469121601267433493',
               '469121615838576640', '469121630829019136', '469121663905300490',
               '469121687506518037', '469121703348273152', '469121718271868928',
               '469121735795539988', '469121769639378944', '469121782473949186',
               '469121809162174495', '469121836651642911', '469122055439384577']
elif version == "0":
    id_list = ['469095507759726603', '469095668137459712', '469095701947875338',
               '342760722058706945', '469095719178076170', '469117787076296705',
               '469150849642266624', '469150873776553994', '469150888150433802',
               '469150905384828939', '469150918139576320', '469150935663378442',
               '469150955372412928', '469150979200385025', '469150995268632576',
               '469151014302384128', '469151036188262420', '469151049828007946',
               '469151070137090048', '469151084124962816', '469150770881888266']

print("Version: %s" % version)
EventHandler.checkMessages(id_list)
# Infinite blocking loop
with open("apitoken.txt", "r") as apiFile:
    apitoken = apiFile.read()
EventHandler.client.run(apitoken)
EventHandler.client.close()

# GENERAL-----------------------------------------------------
# test sending backup txt from pi to pc


# OVERALL-----------------------------------------------------
# Funkar bara när spelaren är rankad i samtliga leaderboards

# När spelaren uppdaterar en leaderboard så uppdateras även overall

# score = index i samtliga leaderboards / antal leaderboards


# LEADERBOARDS---------------------------------------------
# Lista på saker att fixa vid nya leaderboards:
#x   Skapa Discord kanal
#x   Skapa .txt fil på PC (Sneasel 1 2018-07-11)
#x   Lägg till .txt i .gitignore + git push + git pull på PI
#x   Skapa .txt fil på Pi
#x   Lägg till i checkMessage leaderboard_list
#x   Om decimaler, lägg till i if not joggerTrue or..: int()
#x   Lägg till joggerTrue och if joggerTrue i leaderboards
#x   Lägg till embed icon i leaderboards, samt ändra title
#x   Lägg till channel ID i main.py, uppdatera channel2 under embeds
#x   Lägg till enhet i ranks
#x   Om decimaler, Lägg till i ranks if not item in "jogger", ...

# Leaderboards to add:
#Jogger
#Pikachu Fan
#Battle Girl
#Pokedex
#Collector
#Scientist
#Breeder
#Backpacker
#Fisherman
#Youngster
#Berry Master
#Gym Leader
#Champion
#Battle Legend
#Pokémon Ranger
#Unown
#Gentleman
#Pilot
#Total XP

# DELETE-----------------------------------------------------


# REFRESH----------------------------------------------------
# ?refresh ger inget error


# RANKS-----------------------------------------------
# ?rank borde ge samma output

# LIST ----------------------------------------------------


# CLAIM----------------------------------------------
# Claimtiden buggar fortfarande, säger 1 minut kvar när man varit på
# servern i flera dagar. Utkommenterat atm.


# ADMIN_CLAIM----------------------------------------


# ?HELP ----------------------------------------------------



# IMPORTERING
# ---------------------------------------------------
# Ändra command channel ID i alla funktionskall
# Ändra role ID för admin under DELETE command (skriv "\Admin"
# Ändra role ID för admin function call för admin_claim command (skriv "\Admin")
# för att få admin ID)
# ctrl+f "message.channel", "message.channel.id", "46"
# skapa claimed kanal, alla andra kanaler kräver claimed role för att se
# claimedkanal får inte skrivas i av folk som är claimed
