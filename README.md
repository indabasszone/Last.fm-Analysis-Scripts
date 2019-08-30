# Last.fm-Analysis-Scripts
This is a set of python scripts I wrote to perform various analyses on any user's last.fm data. Last.fm is a music tracking site where you can "scrobble" (document, record, track, etc.) all the music you listen to, allowing it to function as a personal database for every song, artist, and album you've heard. Last.fm provides an official API for pulling data from the website, which is what I used for this project. The API returns data in XML files, which python has a library for parsing.

I currently have 3 scripts written, which can be easily run using command line input. They require an API key to run, which can be obtained here: https://www.last.fm/api/account/create

### Top_Month_Artists
This script allows users to see their top artists for a given month based on a calculated score. The score places a greater weight on artists who had a higher percentage of their scrobbles occur in that month. For example, if artist A and B both had 100 scrobbles in a month, but A has 1000 scrobbles overall while B only has 150, B would have a higher score because they were more unique to that month. Music has great nostalgic value and can help people vividly recall memories from certain periods of their life; thus, the goal of this script is to help users figure out what artists "defined" a certain month in their life and help them recall that period of time most effectively.

### Top_Season_Tags
This script is a bit more straightforward, finding a user's top tags for each season (spring, summer, fall, winter) in an effort to see if their listening habits vary throughout the year. Last.fm tags are genres/descriptors that users can assign to songs, artists, and albums that describe the sound or other qualities of the music.

### Obscure_Recs
This script aims to help users find more obscure artist recommendations for an artist of their choice. Users enter an artist and a listener limit, for which the script returns a list of 10 artist recommendations with listener counts under the limit, ordered by their similarity to the initial artist as defined by last.fm. Last.fm has a "similar artists" feature on every artist's webpage, but it often shows the most popular artists first, which the user is more likely to be familiar with. The script helps the user avoid having to dig through the similar artists list to find artists they haven't heard yet.
