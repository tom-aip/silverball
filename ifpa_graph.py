#!/usr/local/bin/python3
import requests
import sys
import os
import re
import time
import datetime

from matplotlib import pyplot as plt
from matplotlib.dates import date2num
        
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

    dates_list = []
    ratings_list = []
    rankings_list = []

    # get current rating/ranking
        # open player file
    (player_name, rating, ranking, date) = get_current_rating_ranking(player_id)
    dates_list.append(date)
    ratings_list.append(rating)
    rankings_list.append(ranking)
        
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
        
        rank = 0
        rating = 0
        
        # skip tournament if there's no match
        if m:
            player_name = m.group(1)
            rank = int(m.group(2))
            rating = m.group(3)
            print (rating)

            # skip unrated tournaments. not really useful and throw off the Y axis.
            if rating != 'Not Rated' and int(rating) >200:
                print ('rating is ' + rating)
                rating = int(rating)
                ratings_list.append(rating)
                rankings_list.append(rank)

                # find the date string. example:
                # <p id="toursubtitle">Results for the Main Tournament event on October 31, 2017</p>
                #>Results for the Side Tournament event on December 15, 2013</p>
                m = re.search('Results for the .*? event on (.*?)</p>',tournament_html, re.DOTALL)
                if m:
                    date_str = m.group(1)
                    time_object = datetime.datetime.strptime(date_str, '%B %d, %Y')
                    plt_time_object = date2num(time_object)
                    print('tournament ' + str(tournament_id) + ' on ' + date_str + ', rank ' + str(rank) + ' rating ' + str(rating))

                else:
                    print("*** no date found for tournament " + tournament_id)            


        #        xaxis_time = time.strftime('%Y.%m%d',time_object)
        #        xaxis_time = float(xaxis_time)
                dates_list.append(plt_time_object)
            else:
                print("skipping unrated tournament " + tournament_id)            
    return (player_name, dates_list, ratings_list, rankings_list)
    

def graph_player(player_name, dates_list, rankings_list, ratings_list):

    # sort the ratings and rankings based on the date.     
    rankings_list_sorted = [x for _,x in sorted(zip(dates_list,rankings_list))]
    ratings_list_sorted = [x for _,x in sorted(zip(dates_list,ratings_list))]
    dates_list_sorted = sorted(dates_list)

    # add data points to the graph
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

    
def graph_two_players(player_name, dates_list, rankings_list, ratings_list, player_name2, dates_list2, rankings_list2, ratings_list2):

    # sort the ratings and rankings based on the date.     
    rankings_list_sorted = [x for _,x in sorted(zip(dates_list,rankings_list))]
    ratings_list_sorted = [x for _,x in sorted(zip(dates_list,ratings_list))]
    dates_list_sorted = sorted(dates_list)

    # sort the ratings and rankings based on the date.     
    rankings_list_sorted2 = [x for _,x in sorted(zip(dates_list2,rankings_list2))]
    ratings_list_sorted2 = [x for _,x in sorted(zip(dates_list2,ratings_list2))]
    dates_list_sorted2 = sorted(dates_list2)

    # add data points to the graph
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111) #1x1 grid, 1st subplt

    ax.plot_date(dates_list_sorted, ratings_list_sorted, '-r')
    ax.set_ylabel('rating')
    ax.plot_date(dates_list_sorted2, ratings_list_sorted2,'-b')
    
    plt.title('IFPA rating comparison for ' + player_name + ' ' + str(player_id) + ' and ' + player_name2 + ' ' + str(player2_id))

    plt.xlabel('date')
    
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

    # get command line arguments
    try:
        player_id = int(sys.argv[1])
    except:
        print("Enter one IFPA player_id for rating & ranking graph, or two for a rating comparison.")
        sys.exit()
    try:
        player2_id = int(sys.argv[2])
    except:
        player2_id = 0

    # get list of tournaments the player has played in.
    tournaments = get_tournaments(player_id)
    (player_name, dates_list, ratings_list, rankings_list) = get_rankings(player_id, tournaments)

    # if a second player comparison was requested, get their data, too
    if (player2_id > 0):
        tournaments2 = get_tournaments(player2_id)
        (player_name2, dates_list2, ratings_list2, rankings_list2) = get_rankings(player2_id, tournaments2)
        graph_two_players(player_name, dates_list, rankings_list, ratings_list,player_name2, dates_list2, rankings_list2, ratings_list2)
    else:
        graph_player(player_name, dates_list, rankings_list, ratings_list)

