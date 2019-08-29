import requests
import xml.etree.ElementTree as ET
import time
import datetime

#Method to get the xml data for a user's top scrobbled artists and write it to a file
def get_artists(username, api_key, pagenum=1):
    url = "http://ws.audioscrobbler.com/2.0/?method=library.getartists&api_key=" + api_key + "&user=" + username + "&page=" + str(pagenum)
    resp = requests.get(url)
    
    with open('artistdata.xml', 'wb') as xmlfile:
        xmlfile.write(resp.content)

#Method to get the xml data for a user's scrobbles over a period of time and write it to a file
def get_scrobbles(username, api_key, pagenum=1, year=2019, month=1):
    #Gets the utc start and end times for the specified month, which are added to the request url
    start_time = datetime.datetime(year, month, 1, 0, 0, 0)

    #If the month is december (12), then the end time needs to be calculated using january (1)
    if month == 12:
        month = 0
        year = year + 1
    
    end_time = datetime.datetime(year, month + 1, 1, 0, 0, 0)
    start_utc = int(time.mktime(start_time.timetuple()))
    end_utc = int(time.mktime(end_time.timetuple()))

    url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key=" + api_key + "&user=" + username + "&page=" + str(pagenum)
    url = url + "&from=" + str(start_utc) + "&to=" + str(end_utc) + "&limit=200"
    resp = requests.get(url)
    
    with open('monthdata.xml', 'wb') as xmlfile:
        xmlfile.write(resp.content)

#Method to analyze the xml file containing the user's total number of scrobbles for each artist
def parse_artist_xml(total_plays_dict):
    #Creates element tree for the results of library.getartists
    tree = ET.parse("artistdata.xml")
    root = tree.getroot()

    #Returns if the API failed, printing the provided error message
    if root.attrib['status'] == 'failed':
        error_tag = root.find('./error')
        print("Error with last.fm API when getting total artist plays: code = " + str(error_tag.attrib['code']))
        print(root.find('./error').text + "\n")
        return -1

    #Adds each artist and its total number of plays to the dictionary
    for artist in root.findall('./artists/artist'):
        total_plays_dict.update({artist.find('name').text: int(artist.find('playcount').text)})
    
    #Returns the totalPages attribute from the recenttracks tag so we know
    #how many times to call this method (incrementing page # each time)
    second_tag = root.find('./artists')
    return int(second_tag.attrib['totalPages']) + 1

#Method to analyze the xml file containing the user's scrobbles for the specified month
def parse_scrobble_xml(month_plays_dict): 
    #Creates element tree for the results of user.getrecenttracks
    tree = ET.parse("monthdata.xml")
    root = tree.getroot()

    #Returns if the API failed, printing the provided error message
    if root.attrib['status'] == 'failed':
        error_tag = root.find('./error')
        print("Error with last.fm API when getting plays for this month: code = " + str(error_tag.attrib['code']))
        print(root.find('./error').text + "\n")
        return -1

    #Uses each individual scrobble to find each artist's total scrobbles for the month
    for scrobble in root.findall('./recenttracks/track'):
        artist_name = scrobble.find('artist').text
        print(artist_name)
        
        if artist_name in month_plays_dict:
            month_plays_dict[artist_name] = month_plays_dict[artist_name] + 1
        else:
            month_plays_dict.update({artist_name: 1})

    #Returns the totalPages attribute from the recenttracks tag so we know
    #how many times to call this method (incrementing page # each time)
    second_tag = root.find('./recenttracks')
    return int(second_tag.attrib['totalPages']) + 1

def calc_scores(total_plays_dict, month_plays_dict, scores_dict):
    #Goes through each artist in the month dictionary and calculates its "score"
    #Score is defined as the % of the artist's scrobbles that came in that month
    #multiplied by the log of the total number of scrobbles
    month_artists = month_plays_dict.keys()
    total_artists = list(total_plays_dict.keys())
    for artist in month_artists:
        if artist in total_artists:
            scores_dict.update({artist: ((month_plays_dict[artist]/total_plays_dict[artist]) * month_plays_dict[artist])})

def main():
    #Initializing all variables
    user = input("Enter a username: ")
    api_key = input("Enter a last.fm API key: ")
    year = int(input("Enter a year: "))
    month = int(input("Enter a month (in digit form): "))
    total_plays_dict = {}
    month_plays_dict = {}
    scores_dict = {}

    #Makes one call to the get_artists and parse_artist_xml method to see how many pages it needs to get
    #This gets the total number of scrobbles for every artist in the user's library
    get_artists(user, api_key, 1)
    artists_page_limit = parse_artist_xml(total_plays_dict)

    #If an error occurred (method returned < 0, the method exits)
    #Otherwise it calls the methods for all remaining pages, continuing to check for errors
    #Must call these two methods together because it has to parse the xml it gets from
    #one call before making another call, as that causes errors
    if artists_page_limit < 0:
        return
    elif artists_page_limit > 2:
        for i in range(2, artists_page_limit):
            get_artists(user, api_key, i)
            error = parse_artist_xml(total_plays_dict)
            if (error < 0):
                return

    #Operates effectively the same as for artists, but gets number of scrobbles per artist just for that month
    get_scrobbles(user, api_key, 1, year, month)
    scrobbles_page_limit = parse_scrobble_xml(month_plays_dict)

    if scrobbles_page_limit < 0:
        return
    if scrobbles_page_limit > 2:
        for i in range(2, scrobbles_page_limit):
            get_scrobbles(user, api_key, i, year, month)
            error = parse_scrobble_xml(month_plays_dict)
            if (error < 0):
                return

    #Calculates the score for every artist using calc_scores, which are placed in scores_dict
    #Then gets a list with the artists sorted by their corresponding score
    calc_scores(total_plays_dict, month_plays_dict, scores_dict)
    sorted_artists = sorted(scores_dict, key=scores_dict.get, reverse=True)

    #Prints the artists with the top 5 scores for that month
    print("\nYour top 5 artists for month " + str(month) + " of " + str(year) + ":\n")
    for i in range (0, 5):
        artist = sorted_artists[i]
        print(artist + ", score: " + str(scores_dict[artist]) + ", monthly scrobbles: " + str(month_plays_dict[artist]) + ", total scrobbles: " + str(total_plays_dict[artist]) + "\n") 

main()