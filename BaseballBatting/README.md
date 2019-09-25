Description
=======

This module calculates either the batting average or home runs
per at bat depending on the input arguments. `-i` and `--player-id`
display the Player ID, whch is the default argument. `-n` and `--name`
display the player names (first_name last_name). `-g` and `--given-name`
also display the player names (first_name middle_name last_name). `-b`
or `--batting-average` will display player batting averages and is
the default statistic. `a` or `--at-bats-per-home-run` will display a 
player's at bats per home run. Higher batting averages are better than
lower batting averages and low at bats per home run is better than higher
one (The fewer at bats per home run the better). The `-t` or `--top` 
defines the top number of results (the default is 5). The `-s` or `--skip`
option defines the number of results to skip from the top of the results 
(default is 0). The `-m` or `--minimun-at-bats` defines the minimum career
at bats to be considered for the top results (default is 3000).

## Requirements
To run this script you will need at least Python 3.6

## Instructions
If Python 3.7 is already installed:
```console
$ baseballStats.py
```

If Python 3.7 is not installed
```console
$ python3 baseballStats.py
```

## Sample Output

```console
$ baseballStats.py

cobbty01 0.36633143856580674
hornsro01 0.35849749174109874
jacksjo01 0.3557518570568159
odoulle01 0.3492647058823529
delahed01 0.34580559254327564
```

```console
$ baseballStats.py -m1000

cobbty01 0.36633143856580674
barnero01 0.3596821413634463
hornsro01 0.35849749174109874
jacksjo01 0.3557518570568159
meyerle01 0.35550935550935553
```

```console
$ baseballStats.py -g -t10

Tyrus Raymond Cobb 0.36633143856580674
Rogers Hornsby 0.35849749174109874
Joseph Walker Jackson 0.3557518570568159
Francis Joseph O'Doul 0.3492647058823529
Edward James Delahanty 0.34580559254327564
Tristram E. Speaker 0.34467876410004905
William Robert Hamilton 0.34442145471908325
Theodore Samuel Williams 0.3444069556189982
Dennis Joseph Brouthers 0.3424026167112697
George Herman Ruth 0.34210526315789475
```

```console
$ baseballStats.py -g -t5 --skip=5

Tristram E. Speaker 0.34467876410004905
William Robert Hamilton 0.34442145471908325
Theodore Samuel Williams 0.3444069556189982
Dennis Joseph Brouthers 0.3424026167112697
George Herman Ruth 0.34210526315789475
```
```console
$ baseballStats.py -n -a
Mark McGwire 10.612349914236706
Babe Ruth 11.761904761904763
Barry Bonds 12.92257217847769
Giancarlo Stanton 13.750819672131147
Jim Thome 13.761437908496733
```
