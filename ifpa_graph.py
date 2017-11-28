#!/usr/local/bin/python3
import requests
import sys
import os
import re
import time
import datetime
from typing import NamedTuple

from matplotlib import pyplot as plt
from matplotlib.dates import date2num

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.tournaments_list = []
        self.dates_list = []
        self.ratings_list = []
        self.rankings_list = []
        
    def addRatingRanking(self, date, rating, ranking):
        self.dates_list.append(date)
        self.ratings_list.append(rating)
        self.rankings_list.append(ranking)
    def getRatings(self):
        return self.ratings_list
    def getRankings(self):
        return self.rankings_list
    def getDates(self):
        return self.dates_list
    def setName(self,name):
        self.name = name
    def getName(self):
        return self.name

# returns list of tournament that the player has played in.
def get_tournaments(player_id):

    # get the player HTML if it's not already cached
    filename = 'players/' + str(player_id) + '.txt'
    if not os.path.exists(filename):
        url = 'https://www.ifpapinball.com/player.php?p=' + str(player_id)
        print('getting url ' + url)
        r = requests.get(url)
        file = open(filename, 'w')
        file.write(r.text)
        file.close()
        
    # open player file
    file = open(filename, 'r')
    player_html = file.read()
    
    # find tournaments with text like this:
    # /tournaments/view.php?t=21201
    tournaments = re.findall('/tournaments/view.php\?t=(\d+)', player_html)
    
    return (tournaments)

def get_current_rating_ranking(player_id):
    # open player file
    filename = 'players/' + str(player_id) + '.txt'
    file = open(filename, 'r')
    player_html = file.read()

    # find and add player name, current date, rating, and rank as first point in the array
    # for example:
    #                <td class="right">Ranking:</td>
    #                    <td class="right">895th</td>
    #                    <td>87.63</td>
    #                </tr>
    #                <tr>
    #                    <td class="right">Rating:</td>
    #                    <td class="right">82nd</td>
    #                    <td>1714.44</td>
    #                </tr>

    m = re.search('<h1>(.*?)<.*?Ranking:<.*?right">(\d+).*?Rating:.*?right">(\d+).*?(\d+)', player_html, re.DOTALL)
    if m:
        player_name = m.group(1)
        ranking = int(m.group(2))
        rating = int(m.group(4))
        print('current ranking is ' + str(ranking) + ' and rating # is ' + str(rating))
        date = date2num(datetime.datetime.now())
    else:
        print('current ranking & rating not found!')
        return
    return (player_name, rating, ranking, date)

    # grab the ranking from each tournament
    
    #    tournament_indices = player_html.find(search_str)
    #    print(tournament_indices)
    #    tournament = tournament_indices[index:]

    #    tournament_id_str = player_html
    #    score_str[2].isnumeric():  
        
def get_rankings(player_id, tournaments):
    # get the tournament data if don't have it already
    print('getting tournament for ' + str(player_id) + " from " + str(len(tournaments)) + " tournaments.")

#    dates_list = []
#    ratings_list = []
#    rankings_list = []
    player = Player(id,tournaments)

    # get current rating/ranking
        # open player file
    (player_name, rating, ranking, date) = get_current_rating_ranking(player_id)
    player.addRatingRanking(date, rating, ranking)
    player.setName(player_name)
    
#    dates_list.append(date)
#    ratings_list.append(rating)
#    rankings_list.append(ranking)
        
    for tournament_id in tournaments:
        tournament_filename = 'tournaments/' + tournament_id + '.txt'
        if not os.path.exists(tournament_filename):
            url = 'https://www.ifpapinball.com/tournaments/view.php?t=' + str(tournament_id)
            print('getting url ' + url)
            r = requests.get(url)
            file = open(tournament_filename, 'w')
            file.write(r.text)
            file.close()
            time.sleep(0.25) # to be nice to ifpapinball.com, and to catch bugs before they hammer the server

        # find the date & player ranking in the tournament file
        file = open(tournament_filename, 'r')
        tournament_html = file.read()
#        print(tournament_html)
    
        # find player rankings inside the html

#        <td class="left "><span class="us sprite"></span> <a href="/player.php?p=38597">Genele Egea </a></td>
#        <td  >2679</td>
#        <td >1354.49</td>
#        <td >1.52</td>
#                    <tr>
# or alternately, if it's the first tournament played:
# <span class="us sprite"></span> <a href="/player.php?p=53128">Tom Miller CA</a></td>
#        <td  class="highlight"   >27982</td>
#        <td  class="highlight"  >Not Rated</td>
#        <td  class="highlight"  >1.20</td>
    
#        TODO: redo as verbose mode regex using re.X
        match_str = 'sprite"></span> <a href="/player.php\?p=' + str(player_id) +'">(.*?)<.*?(\d+)'
        match_str = match_str + '.*?(\d+).*?<td.*?>([\d|Not Rated]+).*?<td.*?>(\d+)'
        
        m = re.search(match_str, tournament_html, re.DOTALL)
        
        ranking = 0
        rating = 0
        
        # skip tournament if there's no match
        if m:
            player_name = m.group(1)
            ranking = int(m.group(2))
            rating = m.group(3)
            print (rating)

            # skip unrated tournaments. not really useful and throw off the Y axis.
            if rating != 'Not Rated' and int(rating) >200:
#                print ('rating is ' + rating)
                rating = int(rating)

                # find the date string. example:
                # <p id="toursubtitle">Results for the Main Tournament event on October 31, 2017</p>
                #>Results for the Side Tournament event on December 15, 2013</p>
                m = re.search('Results for the .*? event on (.*?)</p>',tournament_html, re.DOTALL)
                if m:
                    date_str = m.group(1)
                    time_object = datetime.datetime.strptime(date_str, '%B %d, %Y')
                    plt_time_object = date2num(time_object)
                    print('tournament ' + str(tournament_id) + ' on ' + date_str + ', rank ' + str(ranking) + ' rating ' + str(rating))

                else:
                    print("*** no date found for tournament " + tournament_id)            

#                dates_list.append(plt_time_object)
                player.addRatingRanking(plt_time_object, rating, ranking)

            else:
                print("skipping unrated tournament " + tournament_id)            
#    return (player_name, dates_list, ratings_list, rankings_list)
    return player

def graph_player(player):
    dates_list = player.getDates()
    rankings_list = player.getRankings()
    ratings_list= player.getRatings()
    player_name = player.getName()
    
    # sort the ratings and rankings based on the date.     
    rankings_list_sorted = [x for _,x in sorted(zip(dates_list,rankings_list))]
    ratings_list_sorted = [x for _,x in sorted(zip(dates_list,ratings_list))]
    dates_list_sorted = sorted(dates_list)

    # set up the graph
    fig = plt.figure(figsize=(8, 5))
#    plt.plot(dates_list, rankings_list,'ro')
    ax = fig.add_subplot(111) #1x1 grid, 1st subplt
#    ax.plot_date(dates_list, rankings_list, 'ro')

    # TODO: sort array so that a line graph can be used. top 20 played tournaments are sorted separately from non-top 20 played tourneys
    ax.plot_date(dates_list_sorted, rankings_list_sorted, '-r')
    ax.set_ylabel('ranking')
    ax.yaxis.label.set_color('red')

    ax2 = ax.twinx()
    ax2.plot_date(dates_list_sorted, ratings_list_sorted,'-b')
    ax2.set_ylabel('rating')
    ax2.yaxis.label.set_color('blue')
    
    plt.title('IFPA rating and rank graph for ' + player_name + ' ' + str(player_id))

#    plt.ylabel('rating/rank')
    plt.xlabel('date')
    png_name = 'graphs/' + player_name.strip() + '_' + str(player_id) +'.png'
    plt.savefig(png_name, dpi=200)

    plt.show()
    plt.close()

def graph_players(players):

    # set up the graph
    fig = plt.figure(figsize=(8, 5))
#    plt.plot(dates_list, rankings_list,'ro')
    ax = fig.add_subplot(111) #1x1 grid, 1st subplt
#    ax.plot_date(dates_list, rankings_list, 'ro')
    title_str = 'IFPA rating comparison for '
    ax.set_ylabel('rating')
    plot_colors = ('-r', '-b', '-y', '-')
    player_num = 0
    for player in players:
        player_num = player_num + 1
        print('player ' + player.getName())
        dates_list = player.getDates()
        rankings_list = player.getRankings()
        ratings_list= player.getRatings()
        player_name = player.getName()
    
            # sort the ratings and rankings based on the date.     
        rankings_list_sorted = [x for _,x in sorted(zip(dates_list,rankings_list))]
        ratings_list_sorted = [x for _,x in sorted(zip(dates_list,ratings_list))]
        dates_list_sorted = sorted(dates_list)

        ax.plot_date(dates_list_sorted, ratings_list_sorted, plot_colors[player_num-1])
#        ax.plot_date(dates_list_sorted2, ratings_list_sorted2,'-b')

        title_str = title_str + ' ' + player.getName()

    plt.xlabel('date')
    plt.title(title_str)

    # don't save to PNG if this is a comparison. not sure it makes sense.
    #    png_name = 'graphs/' + player_name.strip() + '_' + str(player_id) + '_'.png'
    #    plt.savefig(png_name, dpi=200)

    plt.show()
    plt.close()    
  
        
if __name__ == '__main__':
    
    # requires three directories for caching results graphs, tournaments, and players    
    if not os.path.exists('tournaments'):
        os.makedirs('tournaments')
    if not os.path.exists('players'):
        os.makedirs('players')
    if not os.path.exists('graphs'):
        os.makedirs('graphs')

    players = []
    player_num = 0
    player_id = 0
    
    # try to get four player IDs from the argv list
    while player_num < 4:
        player_num = player_num +1
        try:
            player_id = int(sys.argv[player_num])
        except:
            player_id = 0
            if player_num == 1:
                print("Enter one IFPA player_id for rating & ranking graph, or two to four for a rating comparison.")
            sys.exit()

        # get player info
        if (player_id > 0):
            # get list of tournaments the player has played in.
            tournaments = get_tournaments(player_id)
            # get the rankings from that tournaments
            player = get_rankings(player_id, tournaments)
            players.append(player)

    # if only one player was entered, graph a single player's rank & rating, else make a comparison graph
    if player_num == 1:
        graph_player(player)
    else:
        graph_players(players)

