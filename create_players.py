class Stats:
    def __init__(self, kills, deaths, assists):
        self.kills = kills
        self.deaths = deaths
        self.assists = assists

class Players:
    def __init__(self, name, stats):
        self.name = name
        self.stats = stats

def extract_stats(text):

    num_arr = []
    tracked_kills = ""
    tracked_deaths = ""
    tracked_assists = ""

    for char in text:
        if char == " ":
            tracked_kills = tracked_deaths
            tracked_deaths = tracked_assists
            tracked_assists = ""

        elif char == "\n":
            if (tracked_assists and tracked_deaths and tracked_assists):
                set_of_states = Stats(int(tracked_kills), int(tracked_deaths), int(tracked_assists))
                print(set_of_states)

                num_arr.append(set_of_states)
                tracked_assists = ""
                tracked_deaths = ""
                tracked_kills = ""

            elif(tracked_assists or tracked_deaths or tracked_assists):
                print("Error: Missing Stats \n Kills:", tracked_kills, "Deaths: ", tracked_deaths, "Assists:",
                     tracked_assists)
                exit()

            else:
                continue
        else:
            tracked_assists += char
            print(tracked_assists)

    print(num_arr)
    return num_arr


def extract_names(text):
    text = text.replace(" _", "_")
    names_arr = text.split("\n")
    for i, name in enumerate(names_arr):
        if name == "":
            names_arr.pop(i)
    for y, name in enumerate(names_arr):
        for j, char in enumerate(name):
            if char == " ":
                names_arr[y] = name[j:]
                names_arr[y] = names_arr[y].replace(" ", "")

    return names_arr


def generate_player_objects(list_names, list_stats):
    if len(list_stats) == len(list_names):
        i = 0
        list_of_players = []
        while i < len(list_stats):
            list_of_players.append(Players(list_names[i], list_stats[i]))
            i += 1
        return list_of_players

    else:
        print("Error: there are more entries for stats than there are names.")
        exit()
