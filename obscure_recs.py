import requests
import xml.etree.ElementTree as ET

#Method to find more "obscure" recommendations based on an artist
#Checks for failure after every API call; returns null if an error occurs
def get_recs(api_key, artist_to_search):
    #Finds the number of listeners for the specified artist (as well as other info we don't use here)
    url = "http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&api_key=" + api_key + "&artist=" + artist_to_search
    artist_info_root = ET.fromstring(requests.get(url).content)
    #The '&' character causes problems with API calls so it needs to be replaced
    artist_to_search = artist_to_search.replace('&','%26')

    #Checking for API failure
    if artist_info_root.attrib['status'] == 'failed':
        error_tag = artist_info_root.find('./error')
        print("Error with last.fm API when finding artist info: code = " + str(error_tag.attrib['code']))
        print(artist_info_root.find('./error').text + "\n")
        return None

    #Asks the user for how many listeners a similar artist should have to be considered "obscure"
    listeners = artist_info_root.find('./artist/stats/listeners').text
    listener_limit = int(input(artist_to_search + " has " + listeners + " listeners, what would you like to make the listener limit for recommendations? "))

    #Finds a list of similar artists based on the specified artist
    url = "http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&limit=1500&api_key=" + api_key + "&artist=" + artist_to_search
    similar_artists_root = ET.fromstring(requests.get(url).content)

    #Checking for API failure
    if similar_artists_root.attrib['status'] == 'failed':
        error_tag = similar_artists_root.find('./error')
        print("Error with last.fm API when finding similar artists: code = " + str(error_tag.attrib['code']))
        print(similar_artists_root.find('./error').text + "\n")
        return None

    similar_artists_dict = {}
    artists_found = 0
    #For all similar artists, it finds their name and similarity score (a number between 0 and 1 given by Last.fm)
    for similar_artist in similar_artists_root.findall('./similarartists/artist'):
        artist_name = similar_artist.find('name').text
        similarity = similar_artist.find('match').text

        #Getting info about the similar artist so we can find its listener count
        url = "http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&api_key=" + api_key + "&artist=" + artist_name.replace('&', '%26')
        artist_info_root = ET.fromstring(requests.get(url).content)

        #Checking for API failure
        if artist_info_root.attrib['status'] == 'failed':
            error_tag = artist_info_root.find('./error')
            print("Error with last.fm API when finding similar artist info: code = " + str(error_tag.attrib['code']))
            print(artist_info_root.find('./error').text + "\n")
            return None

        #If the similar artist listener count is below the limit (and thus considered obscure),
        #it adds it along with its listener count and similarity score to the dictionary
        #Caps the number of similar artists added to the dict at 10
        similar_artist_listeners = int(artist_info_root.find('./artist/stats/listeners').text)
        if similar_artist_listeners <= listener_limit:
            similar_artists_dict.update({artist_name: [similar_artist_listeners, similarity]})
            artists_found = artists_found + 1

            if artists_found == 10:
                break

    return similar_artists_dict

def main():
    artist_to_search = input("Enter an artist to find recs for: ")
    api_key = input("Enter a last.fm API key: ")

    #Gets the "obscure" similar artist in a dictionary
    #Key is the artist name, value is a list in format [listeners, similarity]
    similar_artists_dict = get_recs(api_key, artist_to_search)

    if similar_artists_dict is not None:
        print("Obscure artist recommendations for " + artist_to_search)
        for artist in similar_artists_dict.keys():
            print(artist + ", Listeners: " + str(similar_artists_dict[artist][0]) + ", Similarity: " + str(similar_artists_dict[artist][1]))

main()