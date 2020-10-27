from urllib.request import urlopen
from bs4 import BeautifulSoup
import threading
import calendar
import time
REDUNDANT_INDEX = 19

fixtures = {}
old_averages = {}


def get_html(url: str):
    """
    Get the HTML code from the given URL.
    :param url: Input URL
    :return: The HTML code of the website.
    """
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    return html


def parse_name_and_link(game: str):
    """
    Extracting the fixture and the link to it bet comparison. Parsing
    using indices.
    :param game: String of fixture and it's link.
    :return: Tuple of [0]: the fixture and [1]: the fixture's link.
    """
    fixture_end_ind = game.find("link") - 1
    fixture = game[:fixture_end_ind]
    fixture_link_start_ind = len(fixture) + len(" link: ")
    fixture_link = game[fixture_link_start_ind:]
    return fixture, fixture_link


def update_bet_agencies_list(bet_agencies: list,
                             bet_agencies_to_dict: list):
    """
    Filling all bet agencies list that will go the dictionary
    (database).
    :param bet_agencies: List as part of the HTML code, that
           contains all the existing agencies and a few more
           redundant spaces.
    :param bet_agencies_to_dict: List that will go the dictionary
    (database).
    :return: Nothing.
    """
    for bet_agency in bet_agencies:
        # If an agency
        if "bookie" in bet_agency["class"][0]:
            # Skip redundant space in html
            if len(bet_agencies_to_dict) != REDUNDANT_INDEX:
                bet_agencies_to_dict.append(bet_agency.find('a')
                                            ["title"])
            else:
                bet_agencies_to_dict.append(bet_agency.find('a')
                                            ["title"])
                bet_agencies_to_dict.append("ignore")  # Redundant space


def update_opt_num_odds(opt_num_odds: list,
                        opt_num_odds_to_dict: list):
    """
    Filling all odds of a specific option list that will go the
    dictionary (database). The options are: Team #1 wins / Draw/
    Team #2 wins.
    :param opt_num_odds: List as part of the HTML code, that
           contains all the existing odd and a few more
           redundant spaces.
    :param opt_num_odds_to_dict: List that will go the dictionary
    (database).
    :return: Nothing.
    """
    for opt_odd in opt_num_odds:
        opt_num_odd_num = opt_odd.find_all("p")
        if len(opt_num_odd_num) > 0:  # If an odd and not redundant
            opt_num_odds_to_dict.append(opt_num_odd_num[0].text)
        else:
            opt_num_odds_to_dict.append("ignore")


def odd_dict_update(bet_agencies_to_dict: list,
                    opt_num_odds_to_dict: list):
    """
    Updates the dict of odd.
    :param bet_agencies_to_dict: As mentioned above.
    :param opt_num_odds_to_dict: As mentioned above.
    :return: Updated dictinary.
    """
    odds_by_agencies = {
        bet_agencies_to_dict[index]: opt_num_odds_to_dict[index]
        for index in range(len(bet_agencies_to_dict))
        if opt_num_odds_to_dict[index] != "ignore"}

    return odds_by_agencies


def parse_database(teams_and_links: list):
    """
    Parsing the database from each of today's game. The database is a
    dictionary, which its keys are the game and their values are another
    dictionary, which its keys are the options: Team #1 wins, Team #2
    wins or draw and their values are another dictionary, which its
    keys are all the bet agencies and their value is the odd that each
    agency provides at the moment.
    :param teams_and_links: List of all the fixtures and thei links.
    :return: Nothing.
    """
    # for each_game in teams_and_links:
    # Comment the line below and uncomment the above line for all games
    for j in range(10):
        odds_by_agencies = {}  # Odd (val) per agency (key), each result
        team_wins_or_draw = {}  # Odds comparison (val) per result
        bet_agencies_to_dict = []  # All bet agencies
        # Below are relevant options of  possible results (3)
        opt1_odds_to_dict = []
        opt2_odds_to_dict = []
        opt3_odds_to_dict = []

        each_game = teams_and_links[j]
        fixture, fixture_link = parse_name_and_link(each_game)
        fixture_html = get_html(fixture_link)
        fixture_soup = BeautifulSoup(fixture_html, "html.parser")
        all_bet_agencies = fixture_soup.find(id="oddsTableContainer")
        b_table = 'eventTableHeader'
        bet_agencies_table = all_bet_agencies.find_all('tr',
                                                       class_=b_table)
        # In order to ignore firs 'tr' tag which is not an agency
        bet_agencies_to_dict.append("ignore")
        # List of the agencies
        bet_agencies = bet_agencies_table[0].find_all('td')
        update_bet_agencies_list(bet_agencies,
                                 bet_agencies_to_dict)

        odds = fixture_soup.find(id="t1")  # Odd row
        # Below are the odds of team1 wins/Draw/team2 wins
        opt1_odds = odds.find_all('tr')[0]
        opt2_odds = odds.find_all('tr')[1]
        opt3_odds = odds.find_all('tr')[2]

        # Below are updates of odd per option that will go to the dict
        update_opt_num_odds(opt1_odds, opt1_odds_to_dict)
        update_opt_num_odds(opt2_odds, opt2_odds_to_dict)
        update_opt_num_odds(opt3_odds, opt3_odds_to_dict)

        odds_by_agencies = odd_dict_update(bet_agencies_to_dict,
                                           opt1_odds_to_dict)
        team_wins_or_draw[opt1_odds.find('a').text] = odds_by_agencies

        odds_by_agencies = odd_dict_update(bet_agencies_to_dict,
                                           opt2_odds_to_dict)
        team_wins_or_draw[opt2_odds.find('a').text] = odds_by_agencies

        odds_by_agencies = odd_dict_update(bet_agencies_to_dict,
                                           opt3_odds_to_dict)
        team_wins_or_draw[opt3_odds.find('a').text] = odds_by_agencies

        fixtures[fixture] = team_wins_or_draw


def calculate_avg():
    """
    Calculates the average odd per team/draw, in order to notice
    abnormalities.
    :return: Nothing.
    """
    for game_name in fixtures:
        # Lets look in each game
        for game_results in fixtures[game_name]:
            # Each "game_results" contains each possible outcome (1,2,x)
            counter = 0
            sum = 0
            for website in fixtures[game_name][game_results]:
                odd = fixtures[game_name][game_results][website]
                # Turning the odd from str to float
                if "/" in odd:
                    odds = int(odd.split("/")[0]) / int(odd.split("/")[1])
                counter += 1
                sum += float(odds)

            old_average = 0
            new_average = float(sum / counter)
            fixtures[game_name][game_results]["average"] = new_average
            if game_name in old_averages:
                if game_results in old_averages[game_name]:
                    if "average" in old_averages[game_name][game_results]:
                        old_average = fixtures[game_name][game_results]["average"]
            else:
                old_averages[game_name] = {}
                old_averages[game_name][game_results] = {}
                old_averages[game_name][game_results]["average"] = new_average

            if old_average > 0:
                #  Alert if the odds changed in 20% to any direction.
                if new_average * 0.8 > old_average or new_average * 1.2 < old_average:
                    print("ALERT - ABNORMAL BEHAVIOR")
                    fixtures[game_name][game_results]["alert"] = f"The game's ratio" \
                                                                 f" changed dramatically," \
                                                                 f" by more than 20%!"


def print_to_file():
    """
    Writing to an increasing JSON file.
    :return: Nothing.
    """
    timestamp = str(calendar.timegm(time.gmtime()))
    with open('output.json', 'a') as file:
        file.write(timestamp + ": " + str(fixtures))
        file.write("\n")


def update_half_min(teams_and_links: list):
    """
    Run the whole code each 30 seconds.
    :param teams_and_links:
    :return: Nothing.
    """
    threading.Timer(30.0, update_half_min,
                    [teams_and_links]).start()
    parse_database(teams_and_links)
    calculate_avg()
    print_to_file()

