# for documentation + util
from typing import List, Tuple
from dotenv import load_dotenv
from os import getenv

# for processing website
from bs4 import BeautifulSoup
import requests

# for constructing db inputs
from datetime import datetime
import hashlib

from db import DbHandler

load_dotenv()

"""
Returns:
    [id, theater, location, found]
    id: Unique SHA256 key for uniqueness checking
    theater: name of theater
    location: city, state
    found: today's date in ISO format for convenience
"""
def get_showings(today) -> List[Tuple[str, str, str, str]]:
    # get website
    req = requests.get("https://www.sentaifilmworks.com/a/news/book-your-ticket-to-see-revue-starlight-the-movie-in-theaters")
    html = req.text
    soup = BeautifulSoup(html, features="html5lib")

    # get showings table
    table = soup.select_one("table tbody")
    rows = table.find_all("tr")[1:]
    showings = []
    for row in rows:
        theater, city, state, time = [data.string for data in row.find_all("td")]
        # create unique id for each showing
        showing_key = hashlib.sha256((theater+city+state).encode()).hexdigest()
        showings.append(
            (showing_key, theater, f"{city}, {state}", today)
        )
    return showings

if __name__ == "__main__":
    today = datetime.today().isoformat()[:10]

    showings = get_showings(today)
    with DbHandler("locations.db") as db:
        db.executemany("insert or ignore into showings (id, theater, location, added) values (?, ?, ?, ?);", showings)
        db.execute("select * from showings where added=:date;", {"date": today})
        new_showings = db.fetchall()
        if len(new_showings) == 0:
            print("No new showings added")
        else:
            s = f"{len(new_showings)} new showings!"
            for _, theater, location, __ in new_showings:
                s += f"\n{theater} in *{location}*"
            requests.post(f"https://api.telegram.org/bot{getenv('GKJB_TELEGRAM_TOKEN')}/sendMessage?chat_id={getenv('GKJB_CHAT_ID')}&parse_mode=markdown&text={s}")

