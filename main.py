from read_board import parse_scoreboard
from create_players import *
from worksheet_manip import get_worksheet_names, match_picture_to_board, update_spreadsheet

lecture = parse_scoreboard(input("Enter image name e.g. \"PhotoImage.png\" or just click ENTER to parse the most recent image: "))

player_names_raw = lecture[0]
player_stats_raw = lecture[1]

print(player_stats_raw)

list_of_players = generate_player_objects(extract_names(player_names_raw), extract_stats(player_stats_raw))

sifted_list_of_players = match_picture_to_board(list_of_players, get_worksheet_names())

update_spreadsheet(sifted_list_of_players[0], sifted_list_of_players[1], input("Enter day (1-14): "))

