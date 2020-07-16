import instance
import time
import common
instance.startup()

with open("textfiles/version.txt", "r") as versionFile:
    version = versionFile.read()
    print("Version: %s" % version)
with open("textfiles/apitoken.txt", "r") as apiFile:
    apitoken = apiFile.read()

# Weavile - PC
if version == "1":  # [0] is command channel
    common.LEADERBOARD_CHANNELS = [466563505462575106, 466913214656020493, 467754615413407745,
                                   468760503125147648, 469079191002939415, 469121554488360971,
                                   469121572523737098, 469121587807780864, 469121601267433493,
                                   469121615838576640, 469121630829019136, 469121663905300490,
                                   469121687506518037, 469121703348273152, 469121718271868928,
                                   469121735795539988, 469121769639378944, 469121782473949186,
                                   469121809162174495, 469121836651642911, 469122055439384577,
                                   478886996064993280, 493847327925075968, 540876695264034834,
                                   540876711202652160, 540876727698718721, 560905350405029888,
                                   560905402825310209, 605836493218643988, 605836537019760640]
# Sneasel - PI
elif version == "0":  # [0] is command channel
    common.LEADERBOARD_CHANNELS = [469095507759726603, 469095668137459712, 469095701947875338,
                                   342760722058706945, 469095719178076170, 469117787076296705,
                                   469150849642266624, 469150873776553994, 469150888150433802,
                                   469150905384828939, 469150918139576320, 469150935663378442,
                                   469150955372412928, 469150979200385025, 469150995268632576,
                                   469151014302384128, 469151036188262420, 469151049828007946,
                                   469151070137090048, 469151084124962816, 469150770881888266,
                                   478894031678603266, 493848833932001301, 540882217845522432,
                                   540882231816617986, 540882247142604810, 560906125026000897,
                                   560906243258974231, 605837275061944355, 605837367764320284]

while True:
    try:
        instance.bot.loop.run_until_complete(instance.bot.start(apitoken))
    except BaseException:
        print("Sneasel went offline..")
        time.sleep(5)