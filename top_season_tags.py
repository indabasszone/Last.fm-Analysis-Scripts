import requests
import xml.etree.ElementTree as ET
import time
import datetime

#Finds the utc registration time for the specified user
def get_register_utc(username, api_key):
    url = "http://ws.audioscrobbler.com/2.0/?method=user.getinfo&api_key=" + api_key + "&user=" + username
    root = ET.fromstring(requests.get(url).content)

    #Checking for API failure
    if root.attrib['status'] == 'failed':
            error_tag = root.find('./error')
            print("Error with last.fm API when finding registration date: code = " + str(error_tag.attrib['code']))
            print(root.find('./error').text + "\n")
            return -1

    return int(root.find('./user/registered').attrib['unixtime'])

#Method to find all tags and their score for the specified season
#Always checks for API failure when making a call
def get_tags_for_season(username, api_key, start_year, start_month, start_day, end_year, end_month, end_day, register_utc):
    start_time = datetime.datetime(start_year, start_month, start_day, 0, 0, 0)
    end_time = datetime.datetime(end_year, end_month, end_day, 0, 0, 0)
    start_utc = int(time.mktime(start_time.timetuple()))
    end_utc = int(time.mktime(end_time.timetuple()))
    artists_dict = {}
    tags_dict = {}
    season_count = 0

    #Checks for whether or not their account was registered during this time period
    while (register_utc < end_utc):
        season_count = season_count + 1
        #Gets the scrobbles for the specified season during the specified year
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key=" + api_key + "&user=" + username + "&page=1"
        url = url + "&from=" + str(start_utc) + "&to=" + str(end_utc) + "&limit=200"
        root = ET.fromstring(requests.get(url).content)

        #Checking for API failure
        if root.attrib['status'] == 'failed':
            error_tag = root.find('./error')
            print("Error with last.fm API when getting scrobbles for this season: code = " + str(error_tag.attrib['code']))
            print(root.find('./error').text + "\n")
            return None

        total_pages = int(root.find('./recenttracks').attrib['totalPages']) + 1

        #Getting total number of artist plays for first page of scrobbles
        for scrobble in root.findall('./recenttracks/track'):
            artist_name = scrobble.find('artist').text

            if artist_name in artists_dict.keys():
                artists_dict[artist_name] = artists_dict[artist_name] + 1
            else:
                artists_dict.update({artist_name: 1})

        #Getting total number of artist plays for remaining pages
        for i in range (2, total_pages):
            url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key=" + api_key + "&user=" + username + "&page=" + str(i)
            url = url + "&from=" + str(start_utc) + "&to=" + str(end_utc) + "&limit=200"
            root = ET.fromstring(requests.get(url).content)

            #Checking for API failure
            if root.attrib['status'] == 'failed':
                error_tag = root.find('./error')
                print("Error with last.fm API when getting scrobbles for this season: code = " + str(error_tag.attrib['code']))
                print(root.find('./error').text + "\n")
                return None

            #For each scrobble, updates the artist's corresponding playcount
            for scrobble in root.findall('./recenttracks/track'):
                artist_name = scrobble.find('artist').text

                if artist_name in artists_dict.keys():
                    artists_dict[artist_name] = artists_dict[artist_name] + 1
                else:
                    artists_dict.update({artist_name: 1})

        #Changing the time parameters to the previous year's season
        start_year = start_year - 1
        end_year = end_year - 1
        start_time = datetime.datetime(start_year, start_month, start_day, 0, 0, 0)
        end_time = datetime.datetime(end_year, end_month, end_day, 0, 0, 0)
        start_utc = int(time.mktime(start_time.timetuple()))
        end_utc = int(time.mktime(end_time.timetuple()))

    print("Found " + str(season_count) + " instance(s) of this season where you have scrobbled")
    #Getting the top tags for the artists scrobbled this season
    for artist in artists_dict.keys():
        url = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&api_key=" + api_key + "&artist=" + artist.replace('&', '%26')
        root = ET.fromstring(requests.get(url).content)

        #Checking for API failure
        if root.attrib['status'] == 'failed':
            error_tag = root.find('./error')
            print("Error with last.fm API when getting tags for artist " + artist + ": code = " + str(error_tag.attrib['code']))
            print(root.find('./error').text + "\n")
            continue
        artist_plays = artists_dict[artist]

        #Finds all top tags for that specific artist
        #The value for that tag is calculated by multiplying the "count" for that tag (a measure of popularity
        #from 0 to 100) by how many times that artist was scrobbled
        for tag in root.findall('./toptags/tag'):
            tag_text = tag.find('name').text
            tag_count = int(tag.find('count').text)
            total_count = tag_count * artist_plays

            if tag_text in tags_dict.keys():
                tags_dict[tag_text] = tags_dict[tag_text] + total_count
            else:
                tags_dict.update({tag_text: total_count})

    return tags_dict

#Prints the top 10 sorted tags for the specified season
def print_sorted_tags(tags_dict, season): 
    #Gets a list of all the tags sorted by their corresponding score, then prints the top 10 from that
    if tags_dict is None:
        print("No scrobbles/error finding scrobbles for" + season)
    else:
        sorted_tags = sorted(tags_dict, key=tags_dict.get, reverse=True)
        print("\nYour top 10 tags for " + season + " are:")
        for i in range (0, 10):
            tag = sorted_tags[i]
            print(tag + ": " + str(tags_dict[tag]))


def main():
    #Getting user information
    username = input("Enter a username: ")
    api_key = input("Enter a last.fm API key: ")

    #Finds the time the user registered then the top tags for every season
    #Registration time limits how far back in time the get_tags method looks
    register_utc = get_register_utc(username, api_key)
    if (register_utc == -1):
        exit(1)
    
    #Finds the top tags for every season
    print("Finding tags for Spring")
    spring_tags = get_tags_for_season(username, api_key, 2019, 3, 20, 2019, 6, 20, register_utc)
    print("Finding tags for Summer")
    summer_tags = get_tags_for_season(username, api_key, 2019, 6, 21, 2019, 9, 22, register_utc)
    print("Finding tags for Fall")
    fall_tags = get_tags_for_season(username, api_key, 2018, 9, 23, 2018, 12, 20, register_utc)
    print("Finding tags for Winter")
    winter_tags = get_tags_for_season(username, api_key, 2018, 12, 21, 2019, 3, 19, register_utc)

    #Prints the top 10 tags for each season using the print_sorted_tags method
    print_sorted_tags(spring_tags, 'spring')
    print_sorted_tags(summer_tags, 'summer')
    print_sorted_tags(fall_tags, 'fall')
    print_sorted_tags(winter_tags, 'winter')

main()