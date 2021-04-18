# Game Time Pressure
Read games in the pgn file and get the time remaining after every move in the game and generate stats for each player who played under time pressure.

```
Time pressure stats in Champions Chess Tour Skilling Open - Prelims 2020

                       name  games  pts  gtp  gtp_perf
0           Carlsen, Magnus     15  9.0    3      0.33
1          Nakamura, Hikaru     15  9.0    0       NaN
2            Aronian, Levon     15  8.5    5      0.50
3       Nepomniachtchi, Ian     15  8.5    1      0.50
4                So, Wesley     15  8.5    2      1.00
5         Firouzja, Alireza     15  8.0   12      0.54
6               Giri, Anish     15  8.0    5      0.60
7            Le, Quang Liem     15  8.0    8      0.50
8         Radjabov, Teimour     15  8.0    7      0.57
9   Vachier-Lagrave, Maxime     15  8.0    2      0.25
10              Ding, Liren     15  7.5    6      0.42
11    Anton Guijarro, David     15  6.5   11      0.36
12  Vidit, Santosh Gujrathi     15  6.5   11      0.36
13           Svidler, Peter     15  6.0    7      0.43
14         Karjakin, Sergey     15  5.5   11      0.23
15      Duda, Jan-Krzysztof     15  4.5    7      0.29


:: Column name definition ::

gtp     : The number of games where a player is in time pressure.
          A player is in time pressure when the average time in seconds remaining
          on his clock in the last 10 moves in a game is 120 seconds and below.
gtp_perf: The score ratio or score/games for games under time pressure only.
```

## Setup
* Download this repository at this [link](https://github.com/fsmosca/GameTimePressure/archive/refs/heads/main.zip) and unzip it.
* Install python 3
* pip install pandas
* pip install chess

## Command line
The game in the pgn file should have %clk move comment. See sample pgn files under pgn folder.

#### Generate stats

`python time_pressure.py --input ./pgn/2020-champions-chess-tour-skilling-open-prelim.pgn`

#### Help
`python time_pressure.py --help`

```
usage: time_pressure v1.0 [-h] --input INPUT [--time-pressure-sec TIME_PRESSURE_SEC] [--last-n-moves LAST_N_MOVES] [--save-csv]

Read games in pgn file and calculate if a player is in time pressure or not.

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         Input pgn filename (required).
  --time-pressure-sec TIME_PRESSURE_SEC
                        The time pressure threshold in seconds (not required) default=120. If time-pressure-sec is 120 sec or 2 minutes and the average time remaining in the last 10 moves is 2 minutes or    
                        less then this game will considered under time pressure for the player.
  --last-n-moves LAST_N_MOVES
                        The last n moves to be considered in the calculation of time pressure (not required) default=10. If last-n-moves is 10 then we calculate the average time in those moves. If the       
                        value is time-pressure-sec and below then the player is in time pressure.
  --save-csv            If specified the data will be saved in csv file <input pgn file>.csv. Example: python time_pressure.py --save-csv --input skilling_open.pgn

time_pressure v1.0
```

## Credits
* [chess.com](https://www.chess.com/)
* [python-chess](https://github.com/niklasf/python-chess)

