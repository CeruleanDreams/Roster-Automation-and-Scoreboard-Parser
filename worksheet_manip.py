from Levenshtein import distance
import gspread
import configparser


# creating the object of configparser
config_data = configparser.ConfigParser()


# reading data
config_data.read("config.ini")



service_account = gspread.service_account(filename="service_account.json")
spreadsheet = service_account.open(config_data['SPREADSHEET']['SpreadsheetName'])
worksheet = spreadsheet.worksheet(config_data['SPREADSHEET']['WorksheetName'])



row_of_first_name = int(config_data['SPREADSHEET']['RowStartNames'])
column_of_names = config_data['SPREADSHEET']['ColStartNames']
column_of_first_stat = config_data['SPREADSHEET']['ColStartStats']
col_interval_intra_days = int(config_data['SPREADSHEET']['ColIntervalBetweenDays'])


class Stats:
    def __init__(self, kills, deaths, assists):
        self.kills = kills
        self.deaths = deaths
        self.assists = assists

class Players:
    def __init__(self, name, stats):
        self.name = name
        self.stats = stats

def letter_to_number(letter):
    if len(letter) > 1:
        print("Error: must be single letter and uppercase")
        exit()
    if ord(letter) > 90 or ord(letter) < 64:
        print("Error: letter must be uppercase and from A-Z")
        exit()

    return ord(letter)-64

def get_column_number(string_of_letters): #e.g. AA -> 27
        n = 0
        for char in string_of_letters:
            n = n * 26 + 1 + ord(char) - ord('A')
        return n


def number_to_letter(number):
    string_of_letters = "ZABCDEFGHIJKLMNOPQRSTUVWXY"
    if number > 25:
        print("Error: number must belong to [0;25]")
        exit()
    else:
        return string_of_letters[number]


def get_col_name(column_int): #e.g. 26 -> Z

    start_index = 1  # it can start either at 0 or at 1
    letter = ''
    while column_int > 25 + start_index:
        letter += chr(65 + int((column_int - start_index) / 26) - 1)
        column_int = column_int - (int((column_int - start_index) / 26)) * 26
    letter += chr(65 - start_index + (int(column_int)))

    return letter


#print(get_col_name(52))

def get_worksheet_names():

    worksheet_names = worksheet.col_values(get_column_number(column_of_names))
    worksheet_names = worksheet_names[(row_of_first_name - 1):]

    return worksheet_names


def match_picture_to_board(player_list, worksheet_names):
    array_for_board = []
    list_no_matches = []

    for name in worksheet_names:  #Creates the array to update the spreadsheet
        #print(name)
        #print(array_for_board)
        array_for_board.append(["M", "", "", ""]) #Initialises with these default values

    def update_array_for_board(player, index): #Updates the array that will be returned to update the spreadsheet
        array_for_board[index][0] = "P" #Present
        array_for_board[index][1] = player.stats.kills
        array_for_board[index][2] = player.stats.deaths
        array_for_board[index][3] = player.stats.assists

    # Things to add: make it so that first it matches everything, keeping all potential candidates into an array;
    # then finally, it tries matching based on distance for the latter array; it ranks candidates based on their minimum distance
    # while verifying if their number 1 match isn't already taken. Then, from those with the surest matches, it matches them. If they no longer have possible matches,
    # then they're kept and if they're matched then they are removed from the candidates list. By the end, we return that array.

    #Sorting them based on whether they're matched or not
    for player in player_list:
        match = False
        for i, name in enumerate(worksheet_names):
            if player.name == name:
                update_array_for_board(player, i)
                worksheet_names[i] = "MT" #the name has been matched
                match = True
                break

        if match == False:
            list_no_matches.append(player)

    print(array_for_board)
    print(list_no_matches)

    #Calculating potential matches
    for unmatched_player in list_no_matches:
        setattr(unmatched_player, "potential_matches", [])
        #Goes through the available names, and then only adds name
        #as a candidate if of a reasonable distance
        for i, name in enumerate(worksheet_names):
            if name != "MT":
                dist = distance(unmatched_player.name, name)
                #print("Dist:", dist)
                if dist < 3:
                    pot_match = [dist, i]
                    unmatched_player.potential_matches.append(pot_match)

        unmatched_player.potential_matches.sort(key = lambda arr: arr[0]) #Sorting the matches of a player based on the distance
    list_no_matches = sorted(list_no_matches, key = lambda player: player.potential_matches[0][0] if player.potential_matches else float('inf')) #Sorting the players based on who has the highest probability of being matched

    iter_index = 0

    while True:
        if iter_index == len(list_no_matches):
            return([array_for_board, list_no_matches])
            #matches it based on first choice
        if len(list_no_matches[iter_index].potential_matches):
            index_on_board = list_no_matches[iter_index].potential_matches[0][1] #Takes the index of the current player's best match
            print(list_no_matches[iter_index].name, "matched to", worksheet_names[index_on_board])
            update_array_for_board(list_no_matches[iter_index], index_on_board)
            list_no_matches.pop(iter_index) #Since matched, removes it from list of candidates
            for player in list_no_matches: #From every unmatched_players, iterates through its potential candidates to remove the one matched previously
                for candidate_number, candidate in enumerate(player.potential_matches):
                    if candidate[1] == index_on_board:
                        player.potential_matches.pop(candidate_number)
            #Resorts
            list_no_matches = sorted(list_no_matches, key = lambda player: player.potential_matches[0][0] if player.potential_matches else float('inf'))
            #Since array length decreases by 1, no need to move to next index

        else:
            #No match found; will be kept for creating a new entry
            #By this point, only players with no matches remain within list_no_matches

            iter_index += 1


def update_spreadsheet(board_update, unmatched_players, day):
    day = int(day)
    assert day < 15 and day > 0

    #Accounts for skipping the column separating the two subsequent weeks
    if day % 7 == 0:
        column_start_to_update_num = get_column_number(column_of_first_stat) + col_interval_intra_days * (day - 1) + day//7 - 1
    else:
        column_start_to_update_num = get_column_number(column_of_first_stat) + col_interval_intra_days * (
                    day - 1) + day // 7

    #Determining the range for which the player stats will be updated
    column_end_to_update_num = column_start_to_update_num + 3
    col_start = get_col_name(column_start_to_update_num)
    col_end = get_col_name(column_end_to_update_num)
    row_start = str(row_of_first_name)
    row_end = str(row_of_first_name + len(board_update) - 1)

    range = col_start + row_start + ":" + col_end + row_end

    worksheet.update(range, board_update)

    #For the unmatched players
    if unmatched_players:
        print("Found players without a match: ")
        for player in unmatched_players:
            print(player.name)
        proceed = input("Create new entries? Answer (y/n): ")
        if proceed == "y":
            new_entries_names = []
            new_stats_to_copy = []
            for player in unmatched_players:
                new_entries_names.append([player.name]) #Adding the names
                new_stats_to_copy.append(["P", player.stats.kills, player.stats.deaths, player.stats.assists]) #Adding the corresponding stats

            new_row_start = str(int(row_end) + 1)
            new_row_end = str(int(row_end) + len(unmatched_players))

            worksheet.update(column_of_names + new_row_start + ":" + column_of_names + new_row_end, new_entries_names) #Adding names to the bottom
            worksheet.update(col_start + new_row_start + ":" + col_end + new_row_end, new_stats_to_copy)

            print(f"Successfully added {len(unmatched_players)} players to the roster.")





