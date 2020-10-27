"""
In order to execute, run: 'python main.py in cmd, from the main.py path. Make
sure that all the modules (oddschecker_scraper.py and main.py) are in the same
path.
"""
from bs4 import BeautifulSoup
import oddschecker_scraper


def main():
    # Part 1 - List of games and their links creation

    base_url = "https://www.oddschecker.com"
    football_url = "https://www.oddschecker.com/football"
    teams_and_links = []  # List of all the games and their links, respectively

    football_html = oddschecker_scraper.get_html(football_url)
    football_soup = BeautifulSoup(football_html, "html.parser")
    results = football_soup.find(id="fixtures")  # All fixtures
    games = results.find_all('tr', class_="match-on")  # List of all the games

    for game in games:
        team_a = game.find_all("p")[0].text  # First team's name
        team_b = game.find_all("p")[1].text  # Second team's name
        game_link_prefix = game.find("a")["href"]  # Prefix to the game's link
        if "tips" in game_link_prefix:  # To ignore 'tips' advertises
            game_link_prefix = game.find_all("a")[1]["href"]  # Parse the link
        game_link = base_url + game_link_prefix  # Game's link
        teams_and_links.append(f"{team_a} VS {team_b} link: {game_link}")

    # Part 2 - Database creation

    fixtures = {}  # Will contain all the information about all of the games
    old_averages = {}

    # for each_game in teams_and_links:
    oddschecker_scraper.parse_database(teams_and_links)

    # Part 3 - Alert abnormal behavior of odd changes

    # Update each 30 seconds
    oddschecker_scraper.update_half_min(teams_and_links)


if __name__ == '__main__':
    main()

