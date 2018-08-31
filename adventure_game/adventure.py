#!/usr/local/bin/python3.6

"""
Text Adventure Demo by Al Sweigart (al@inventwithpython.com)
Modified by Christian Sacks (christian@sacks.org.uk)

This program is a small text-adventure game that demonstrates the cmd
and textwrap Python modules. You can find other tutorials like this at
http://inventwithpython.com/blog

The tutorial for this game program is located at: TODO
The github repo for this program is at: https://github.com/christiansacks/learning_python/blob/master/adventure_game/adventure.py


This tutorial does not use classes and object-oriented programming
in order to make it simpler to understand for new programmers. Although
you can see how using dictionaries-in-dictionaries to structures your
data quickly gets unwieldy.

The same goes for using global variables and functions such as inventory,
location, and moveDirection(). These are fine for a small program,
but if you ever want to extend the game they can become burdensome to
work with. But if you are starting out with a toy project, they're fine.
"""


"""
First, we will create some data structures for our game world.

The town looks something like this:

        +---------+     +---------+    +---------+---------+
        | Thief   O  y  | Bakery  |    |  Stone  |  Hotel  |
        | Guild   |     |         |    |  Mason  |         |
+------++------O--+     +----O----+    +----O----+----O----+
| Used |
|Anvils|    x   Town Square   x    +--------+
|      O                           |Obs Deck|
+------++----O----+     +-----O------/  /
        | Black-  O     |   Wizard  /  /
        | smith   |  y  |   Tower     /
        +---------+     +------------+
"""


"""
town sewer will look something like this:

          +---+     +-+     +---+       +---+
          |   |     | |     |   |       |   |
     +----+   +-----+ +-----+   +-------+   +-------+
     +----+   +-----+ +-----+   +-------+   +-------+
          |   |     | |     |   |       |   |
          +---+     | |     +---+       +---+
          +---+     | |     +---+
          |   |     | |     |   |
          |   +-----+ +-----+   |     
          |   +-----+ +-----+   |
          |   |     | |     |   |
          +---+     | |     +---+
                    + +
"""

"""
The internal layout of the hotel looks something like this:

1st Floor
+----------------+-----------+----------------+
|                |           |                |
|                $  Elevator $                |
|                $     1     $                |
|                |           |                |
|                +----$$$----+                |
|    Bar/Grill   |                            |
|                |                            |
|                |                            |
|                                             |
|                                     +-------+
|                                     |       |
|                                     |   R   |
|                |    HOTEL LOBBY     |   e   |
|                |                    |   c   |
|                |                    |   e   |
+----------------+                    |   p   |
|                                     |   t   |
|                                     |   i   |
|                                     |   o   |
|                                     |   n   |
|                                     |       |
+----------------+ ENTRANCE  +--------+-------+


All other floors above 1st
X = Floor number, i.e. X01 on on floor 2 is 
room 202. $ = automatic door

+----------------+-----------+----------------+
|                |           |                |
|     Laundry    $  Elevator $      Ice       |
|      Room      $     1     $    Machine     |
|                |           |                |
+----------------+----$$$----+----------------+
|                             Fire Escape -> /
+------------------+       +------------------+
|                 /         \                 |
|       X01        |       |        X02       |
|                  |       |                  |
+------------------+       +------------------+
|                 /         \                 |
|       X03        |       |        X04       |
|                  |       |                  |
+------------------+       +------------------+
|                 /         \                 |
|       X05        |       |        X06       |
|                  |       |                  |
+------------------+       +------------------+
|                 /         \                 |
|       X07        |       |        X08       |
|                  |       |                  |
+------------------+-------+------------------+

"""

"""
These constant variables are used because if I mistype them, Python will
immediately throw up an error message since no variable with the typo
name will exist. If we mistyped the strings, the bugs that it produces
would be harder to find.
"""

import os, cmd, textwrap, time, threading, sys, random, colorama, pickle, datetime

if len(sys.argv) < 4:
    USERNAME = 'Unknown User'
    NODENUMB = '0'
    USERIPAD = '127.0.0.1'
else:
    USERNAME = sys.argv[1]
    NODENUMB = sys.argv[2]
    USERIPAD = sys.argv[3]

SAVES_FOLDER = '/mystic/scripts/adventure_saves/'

DESC = 'desc'
NORTH = 'north'
SOUTH = 'south'
EAST = 'east'
WEST = 'west'
UP = 'up'
DOWN = 'down'
GROUND = 'ground'
SHOP = 'shop'
GROUNDDESC = 'grounddesc'
SHORTDESC = 'shortdesc'
LONGDESC = 'longdesc'
TAKEABLE = 'takeable'
EDIBLE = 'edible'
DESCWORDS = 'descwords'
COST = 'cost'
SELL = 'sell'
SELLABLE = 'sellable'
GAIN = 'gain'
TYPE = 'type'
NPC = 'npc'
GUESTBOOK = 'guestbook'

BODY = 'body'
SHEILD = 'sheild'
DAMAGE = 'damage'
HUNGER = 'hunger'
THIRST = 'thirst'
LEVEL = 'level'
POINTS = 'points'

SCREEN_WIDTH = 80
location = ''

RED = '\033[1;31;1m'
GREEN = '\033[1;32;1m'
YELLOW = '\033[1;33;1m'
BLUE = '\033[1;34;1m'
PURPLE = '\033[1;35;1m'
CYAN = '\033[1;36;1m'
WHITE = '\033[1;37;1m'

worldRooms = {
    'Town Square': {
        DESC: 'The town square is a large open space with a fountain in the center. Streets lead in all directions.',
        NORTH: 'North Y Street',
        EAST: 'East X Street',
        SOUTH: 'South Y Street',
        WEST: 'West X Street',
        NPC: [],
        GROUND: ['Welcome Sign', 'Fountain']},
    'North Y Street': {
        DESC: 'The northern end of Y Street has really gone down hill. Pot holes are everywhere, as are stray cats, rats, and wombats.',
        WEST: 'Thief Guild',
        EAST: 'Bakery',
        SOUTH: 'Town Square',
        DOWN: 'North Y Sewer',
        NPC: [],
        GROUND: ['Do Not Take Sign Sign']},
    'Thief Guild': {
        DESC: 'The Thief Guild is a dark den of unprincipled types. You clutch your purse (though several other people here would like to clutch your purse as well).',
        SOUTH: 'West X Street',
        EAST: 'North Y Street',
        NPC: [],
        GROUND: ['Lock Picks', 'Silly Glasses']},
    'Bakery': {
        DESC: 'The delightful smell of meat pies fills the air, making you hungry. The baker flashes a grin, as he slides a box marked "Not Human Organs" under a table with his foot.',
        WEST: 'North Y Street',
        SOUTH: 'East X Street',
        SHOP: ['Meat Pie', 'Donut', 'Bagel', 'Cupcake'],
        NPC: [],
        GROUND: ['Shop Howto']},
    'Stone Mason': {
        DESC: 'The Stone Mason is where you get your gravestone when you die.',
        SOUTH: 'West Masons Alley',
        SHOP: ['Gravestone'],
        NPC: [],
        GROUND: ['Shop Howto']},
    'Hotel Entrance': {
        DESC: 'The only hotel for miles around. You are at the entrance. There isn\'t a bellboy in sight.',
        NORTH: 'Hotel Lobby',
        SOUTH: 'East Masons Alley',
        NPC: [],
        GROUND: []},
    'Hotel Lobby': {
        DESC: 'You are in the hotel lobby. It\'s eerily quiet.',
        NORTH: 'Elevator 1',
        WEST: 'Hotel Restaurant',
        EAST: 'Hotel Reception',
        SOUTH: 'Hotel Entrance',
        NPC: [],
        GROUND: []},
    'Elevator 1': {
        DESC: 'Elevator on the 1st floor.',
        SOUTH: 'Hotel Lobby',
        UP: 'Elevator 2',
        DOWN: 'Elevator B1',
        NPC: [],
        GROUND: []},
    'Hotel Restaurant': {
        DESC: 'You are in the hotel restaurant, looks like it\'s been closed for decades.',
        EAST: 'Hotel Lobby',
        SHOP: ['Meat Pie', 'Donut', 'Continental Breakfast', 'Cheese Board'],
        NPC: [],
        GROUND: ['Shop Howto']},
    'Hotel Reception': {
        DESC: 'You are in the hotel reception, Strange, there isn\'t anyone here. There is a guestbook on the desk, would you like to sign it?',
        WEST: 'Hotel Lobby',
        GUESTBOOK: 'Hotel Reception',
        NPC: [],
        GROUND: []},
    'Elevator 2': {
        DESC: 'Elevator on the 2nd floor.',
        WEST: 'Laundry Room 2',
        EAST: 'Ice Machine 2',
        SOUTH: 'Rooms 201-202',
        UP: 'Elevator 3',
        DOWN: 'Elevator 1',
        NPC: [],
        GROUND: []},
    'Ice Machine 2': {
        DESC: 'Ice Machine room on the 2nd floor.',
        WEST: 'Elevator 2',
        NPC: [],
        GROUND: []},
    'Laundry Room 2': {
        DESC: 'Laundry room on the 2nd floor.',
        EAST: 'Elevator 2',
        NPC: [],
        GROUND: []},
    'Rooms 201-202': {
        DESC: '',
        WEST: 'Room 201',
        EAST: 'Room 202',
        NORTH: 'Elevator 2',
        SOUTH: 'Rooms 203-204',
        NPC: [],
        GROUND: []},
    'Rooms 203-204': {
        DESC: '',
        WEST: 'Room 203',
        EAST: 'Room 204',
        NORTH: 'Rooms 201-202',
        SOUTH: 'Rooms 205-206',
        NPC: [],
        GROUND: []},
    'Rooms 205-206': {
        DESC: '',
        WEST: 'Room 205',
        EAST: 'Room 206',
        NORTH: 'Rooms 203-204',
        SOUTH: 'Rooms 207-208',
        NPC: [],
        GROUND: []},
    'Rooms 207-208': {
        DESC: '',
        WEST: 'Room 207',
        EAST: 'Room 208',
        NORTH: 'Rooms 205-206',
        NPC: [],
        GROUND: []},
    'Room 201': {
        DESC: 'Room 201.',
        EAST: 'Rooms 201-202',
        NPC: [],
        GROUND: []},
    'Room 202': {
        DESC: 'Room 202.',
        WEST: 'Rooms 201-202',
        NPC: [],
        GROUND: []},
    'Room 203': {
        DESC: 'Room 203.',
        EAST: 'Rooms 203-204',
        NPC: [],
        GROUND: []},
    'Room 204': {
        DESC: 'Room 204.',
        WEST: 'Rooms 203-204',
        NPC: [],
        GROUND: []},
    'Room 205': {
        DESC: 'Room 205.',
        EAST: 'Rooms 205-206',
        NPC: [],
        GROUND: []},
    'Room 206': {
        DESC: 'Room 206.',
        WEST: 'Rooms 205-206',
        NPC: [],
        GROUND: []},
    'Room 207': {
        DESC: 'Room 207.',
        EAST: 'Rooms 207-208',
        NPC: [],
        GROUND: []},
    'Room 208': {
        DESC: 'Room 208.',
        WEST: 'Rooms 207-208',
        NPC: [],
        GROUND: []},
    'Elevator 3': {
        DESC: 'Elevator on the 3rd floor.',
        WEST: 'Laundry Room 3',
        EAST: 'Ice Machine 3',
        SOUTH: 'Rooms 301-302',
        DOWN: 'Elevator 2',
        NPC: [],
        GROUND: []},
    'Ice Machine 3': {
        DESC: 'Ice Machine room on the 3rd floor.',
        WEST: 'Elevator 3',
        NPC: [],
        GROUND: []},
    'Laundry Room 3': {
        DESC: 'Laundry room on the 3rd floor.',
        EAST: 'Elevator 3',
        NPC: [],
        GROUND: []},
    'Rooms 301-302': {
        DESC: '',
        WEST: 'Room 301',
        EAST: 'Room 302',
        NORTH: 'Elevator 3',
        SOUTH: 'Rooms 303-304',
        NPC: [],
        GROUND: []},
    'Rooms 303-304': {
        DESC: '',
        WEST: 'Room 303',
        EAST: 'Room 304',
        NORTH: 'Rooms 301-302',
        SOUTH: 'Rooms 305-306',
        NPC: [],
        GROUND: []},
    'Rooms 305-306': {
        DESC: '',
        WEST: 'Room 305',
        EAST: 'Room 306',
        NORTH: 'Rooms 303-304',
        SOUTH: 'Rooms 307-308',
        NPC: [],
        GROUND: []},
    'Rooms 307-308': {
        DESC: '',
        WEST: 'Room 307',
        EAST: 'Room 308',
        NORTH: 'Rooms 305-306',
        NPC: [],
        GROUND: []},
    'Room 301': {
        DESC: 'Room 301.',
        EAST: 'Rooms 301-302',
        NPC: [],
        GROUND: []},
    'Room 302': {
        DESC: 'Room 302.',
        WEST: 'Rooms 301-302',
        NPC: [],
        GROUND: []},
    'Room 303': {
        DESC: 'Room 303.',
        EAST: 'Rooms 303-304',
        NPC: [],
        GROUND: []},
    'Room 304': {
        DESC: 'Room 304.',
        WEST: 'Rooms 303-304',
        NPC: [],
        GROUND: []},
    'Room 305': {
        DESC: 'Room 305.',
        EAST: 'Rooms 305-306',
        NPC: [],
        GROUND: []},
    'Room 306': {
        DESC: 'Room 306.',
        WEST: 'Rooms 305-306',
        NPC: [],
        GROUND: []},
    'Room 307': {
        DESC: 'Room 307.',
        EAST: 'Rooms 307-308',
        NPC: [],
        GROUND: []},
    'Room 308': {
        DESC: 'Room 308.',
        WEST: 'Rooms 307-308',
        NPC: [],
        GROUND: []},
    'Elevator B1': {
        DESC: 'Elevator on the Upper Basement (B1) floor.',
        UP: 'Elevator 1',
        DOWN: 'Elevator B2',
        NPC: [],
        GROUND: []},
    'Elevator B2': {
        DESC: 'Elevator on the Lower Basement (B2) floor.',
        UP: 'Elevator B1',
        NPC: [],
        GROUND: []},
    'West Masons Alley': {
        DESC: '',
        NORTH: 'Stone Mason',
        EAST: 'East Masons Alley',
        WEST: 'East X Street',
        NPC: [],
        GROUND: []},
    'East Masons Alley': {
        DESC: '',
        NORTH: 'Hotel Entrance',
        WEST: 'West Masons Alley',
        NPC: [],
        GROUND: []},
    'West X Street': {
        DESC: 'West X Street is the rich section of town. So rich, they paved the streets with gold. This probably was not a good idea. The thief guild opened up the next day.',
        NORTH: 'Thief Guild',
        EAST: 'Town Square',
        SOUTH: 'Blacksmith',
        WEST: 'Used Anvils Store',
        NPC: [],
        GROUND: []},
    'Used Anvils Store': {
        DESC: 'The anvil store has anvils of all types and sizes, each previously-owned but still in servicable condition. However, due to a bug in the way this game is designed, you can buy anvils like any other item and walk around, but if you drop them they cannot be picked up since their TAKEABLE value is set to False. The code should be changed so that it\'s not possible for shops to sell items with TAKEABLE set to False.',
        EAST: 'West X Street',
        SHOP: ['Anvil'],
        NPC: [],
        GROUND: ['Shop Howto', 'Anvil', 'Anvil', 'Anvil', 'Anvil']},
    'East X Street': {
        DESC: 'East X Street. It\'s like X Street, except East.',
        NORTH: 'Bakery',
        EAST: 'West Masons Alley',
        WEST: 'Town Square',
        SOUTH: 'Wizard Tower',
        NPC: [],
        GROUND: []},
    'Blacksmith': {
        DESC: 'The blacksmith loudly hammers a new sword over her anvil. Swords, axes, butter knives all line the walls of her workshop, available for a price.',
        NORTH: 'West X Street',
        EAST: 'South Y Street',
        SHOP: ['Sword', 'Great Sword', 'War Axe', 'Chainmail T-Shirt'],
        NPC: [],
        GROUND: ['Anvil', 'Shop Howto']},
    'South Y Street': {
        DESC: 'The Christmas Carolers of South Y Street are famous for all legally changing their name to Carol. They are also famous for singing year-round, in heavy fur coats and wool mittens, even in the summer. That\'s dedication to their craft!',
        NORTH: 'Town Square',
        WEST: 'Blacksmith',
        DOWN: 'South Y Sewer',
        NPC: [],
        GROUND: []},
    'Wizard Tower': {
        DESC: 'Zanny magical antics are afoot in the world-famous Wizard Tower. Cauldrons bubble, rats talk, and books float midair in this center of magical discovery.',
        NORTH: 'East X Street',
        UP: 'Observation Deck',
        NPC: [],
        GROUND: ['Crystal Ball', 'Floating Book', 'Floating Book']},
    'Observation Deck': {
        DESC: 'You can see the entire town from the top of the Wizard Tower. Everybody looks like ants, especially the people transformed into ants by the wizards of the tower!',
        DOWN: 'Wizard Tower',
        UP: 'Magical Escalator to Nowhere',
        NPC: [],
        GROUND: ['Telescope']},
    'Magical Escalator to Nowhere': {
        DESC: 'No matter how much you climb the escalator, it doesn\'t seem to be getting you anywhere.',
        UP: 'Magical Escalator to Nowhere',
        DOWN: 'Observation Deck',
        NPC: [],
        GROUND: []},
    'North Y Sewer': {
        DESC: 'The sewer in North Y Street is overrun with rats and sewage. This had better be worth it.',
        UP: 'North Y Street',
        EAST: 'Bakery Sewer',
        WEST: 'Thief Guild Sewer',
        SOUTH: 'Town Square Sewer',
        NPC: [],
        GROUND: []},
    'Town Square Sewer': {
        DESC: 'The sewer underneath the town square.',
        NORTH: 'North Y Sewer',
        SOUTH: 'South Y Sewer',
        NPC: [],
        GROUND: []},
    'South Y Sewer': {
        DESC: 'The sewer in South Y Street is relatively clean for a sewer. It looks like it has been well looked after, and there are signs that this has been used for things other than just waste.',
        UP: 'South Y Street',
        NORTH: 'Town Square Sewer',
        WEST: 'Blacksmith Sewer',
        EAST: 'Wizard Tower Sewer',
        NPC: [],
        GROUND: []},
    'Bakery Sewer': {
        DESC: 'The sewer beneath the Bakery. Is that bread you can smell?',
        EAST: 'Stone Mason Sewer',
        WEST: 'North Y Sewer',
        NPC: [],
        GROUND: []},
    'Stone Mason Sewer': {
        DESC: 'The sewer beneath the Stone Mason. Shhhh, there\'s a ghost here.',
        WEST: 'Bakery Sewer',
        NPC: [],
        GROUND: []},
    'Thief Guild Sewer': {
        DESC: 'The sewer beneath the Thief Guild building. Unsurprisingly there\'s a distinct chance this area has been looted already.',
        EAST: 'North Y Sewer',
        NPC: [],
        GROUND: []},
    'Blacksmith Sewer': {
        DESC: 'The sewer beneath the Blacksmith building. The blacksmith definitely has enough iron in his diet.',
        EAST: 'South Y Sewer',
        NPC: [],
        GROUND: []},
    'Wizard Tower Sewer': {
        DESC: 'The sewer beneath the Wizard Tower. Even this brown sludge smells magical.',
        WEST: 'South Y Sewer',
        NPC: [],
        GROUND: []},
    }

worldItems = {
    'Money': {
        GROUNDDESC: 'A coin is lying on the ground',
        SHORTDESC: 'a coin',
        LONGDESC: 'The local currency used in the game',
        SELLABLE: False,
        TYPE: 'playerStats',
        DESCWORDS: ['money', 'coin']},
    'Welcome Sign': {
        GROUNDDESC: 'A welcome sign stands here.',
        SHORTDESC: 'a welcome sign',
        LONGDESC: 'The welcome sign reads, "Welcome to this text adventure demo. You can type "help" for a list of commands to use. Be sure to check out Al\'s cool programming books at http://inventwithpython.com"',
        TAKEABLE: False,
        SELL: 0,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['welcome', 'sign']},
    'Do Not Take Sign Sign': {
        GROUNDDESC: 'A sign stands here, not bolted to the ground.',
        SHORTDESC: 'a sign',
        LONGDESC: 'The sign reads, "Do Not Take This Sign"',
        SELL: 100,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['sign']},
    'Fountain': {
        GROUNDDESC: 'A bubbling fountain of green water.',
        SHORTDESC: 'a fountain',
        LONGDESC: 'The water in the fountain is a bright green color. Is that... gatorade?',
        TAKEABLE: False,
        TYPE: 'inventory',
        DESCWORDS: ['fountain']},
    'Sword': {
        GROUNDDESC: 'A sword lies on the ground.',
        SHORTDESC: 'a sword',
        LONGDESC: 'A longsword, engraved with the word, "Used". Has 20 DAMAGE',
        SELL: 10,
        SELLABLE: True,
        DAMAGE: 20,
        TYPE: 'inventory',
        DESCWORDS: ['sword', 'longsword']},
    'Great Sword': {
        GROUNDDESC: 'A great sword lies on the ground.',
        SHORTDESC: 'a great sword',
        LONGDESC: 'A longsword, engraved with the word, "Excaleber". Has 40 DAMAGE',
        COST: 100,
        SELL: 50,
        SELLABLE: True,
        DAMAGE: 40,
        TYPE: 'inventory',
        DESCWORDS: ['sword', 'excaleber', 'longsword']},
    'War Axe': {
        GROUNDDESC: 'A mighty war axe lies on the ground.',
        SHORTDESC: 'a war axe',
        LONGDESC: 'The mighty war axe is made with antimony impurities from a fallen star, rendering it surpassingly brittle. Has 50 DAMAGE',
        COST: 150,
        SELL: 75,
        SELLABLE: True,
        DAMAGE: 50,
        TYPE: 'inventory',
        DESCWORDS: ['axe', 'war', 'mighty']},
    'Chainmail T-Shirt': {
        GROUNDDESC: 'A chainmail t-shirt lies wadded up on the ground.',
        SHORTDESC: 'a chainmail t-shirt',
        LONGDESC: 'The chainmail t-shirt has a slogan and arrow engraved on the front: "I\'m with Stupid"',
        SELL: 5,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['chainmail', 'chain', 'mail', 't-shirt', 'tshirt', 'stupid']},
    'Anvil': {
        GROUNDDESC: 'The blacksmith\'s anvil, far too heavy to pick up, rests in the corner.',
        SHORTDESC: 'an anvil',
        LONGDESC: 'The black anvil has the word "ACME" engraved on the side.',
        TAKEABLE: False,
        COST: 10,
        SELL: 10,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['anvil']},
    'Lock Picks': {
        GROUNDDESC: 'A set of lock picks lies on the ground.',
        SHORTDESC: 'a set of lock picks',
        LONGDESC: 'A set of fine picks for picking locks.',
        SELL: 10,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['lockpicks', 'picks', 'set']},
    'Silly Glasses': {
        GROUNDDESC: 'A pair of those silly gag glasses with the nose and fake mustache rest on the ground.',
        SHORTDESC: 'a pair of silly fake mustache glasses',
        LONGDESC: 'These glasses have a fake nose and mustache attached to them. The perfect disguise!',
        SELL: 1,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['glasses', 'silly', 'fake', 'mustache']},
    'Meat Pie': {
        GROUNDDESC: 'A suspicious meat pie rests on the ground.',
        SHORTDESC: 'a meat pie',
        LONGDESC: 'A meat pie. It tastes like chicken.',
        EDIBLE: True,
        GAIN: 30,
        COST: 3,
        SELL: 2,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['pie', 'meat']},
    'Continental Breakfast': {
        GROUNDDESC: 'A continental breakfast rests on the ground. It looks like it was placed there suspiciously.',
        SHORTDESC: 'a large breakfast',
        LONGDESC: 'A continental breakfast, includes sausages, scrambled egg, bacon, hash browns and all the trimmings.',
        EDIBLE: True,
        GAIN: 50,
        COST: 10,
        SELL: 1,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['breakfast']},
    'Cheese Board': {
        GROUNDDESC: 'A cheese board is scattered on the ground, looks like it was thrown. Crumbs!',
        SHORTDESC: 'a large mess of cheese',
        LONGDESC: 'A cheese board with all kinds of cheeses and crackers.',
        EDIBLE: True,
        GAIN: 20,
        COST: 5,
        SELL: 1,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['cheese']},
    'Bagel': {
        GROUNDDESC: 'A bagel rests on the ground. (Gross.)',
        SHORTDESC: 'a bagel',
        LONGDESC: 'It is a donut-shaped bagel.',
        EDIBLE: True,
        GAIN: 10,
        COST: 2,
        SELL: 1,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['bagel']},
    'Donut': {
        GROUNDDESC: 'A donut rests on the ground. (Gross.)',
        SHORTDESC: 'a donut',
        LONGDESC: 'It is a bagel-shaped donut.',
        EDIBLE: True,
        GAIN: 10,
        COST: 2,
        SELL: 1,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['donut']},
    'Cupcake': {
        GROUNDDESC: 'A cupcake rests on the ground. (Gross.)',
        SHORTDESC: 'A cupcake',
        LONGDESC: 'It is a cupcake shaped cupcake',
        EDIBLE: True,
        GAIN: 20,
        COST: 2,
        SELL: 1,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['cupcake']},
    'Crystal Ball': {
        GROUNDDESC: 'A glowing crystal ball rests on a small pillow.',
        SHORTDESC: 'a crystal ball',
        LONGDESC: 'The crystal ball swirls with mystical energy, forming the words "Answer Unclear. Check Again Later."',
        SELL: 10,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['crystal', 'ball']},
    'Floating Book': {
        GROUNDDESC: 'A magical book floats here.',
        SHORTDESC: 'a floating book',
        LONGDESC: 'This magical tomb doesn\'t have a lot of pictures in it. Boring!',
        SELL: 5,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['book', 'floating']},
    'Telescope': {
        GROUNDDESC: 'A telescope is bolted to the ground.',
        SHORTDESC: 'a telescope',
        LONGDESC: 'Using the telescope, you can see your house from here!',
        TAKEABLE: False,
        TYPE: 'inventory',
        DESCWORDS: ['telescope']},
    'README Note': {
        GROUNDDESC: 'A note titled "README" rests on the ground.',
        SHORTDESC: 'a README note',
        LONGDESC: 'The README note reads, "Welcome to the text adventure demo. Be sure to check out the source code to see how this game is put together."',
        SELL: 1,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['readme', 'note']},
    'Shop Howto': {
        GROUNDDESC: 'A "Shopping HOWTO" note rests on the ground.',
        SHORTDESC: 'a shopping howto',
        LONGDESC: 'The note reads, "When you are at a shop, you can type "list" to show what is for sale. "buy <item>" will add it to your inventory, or you can value and sell an item in your inventory with "value <item>" and "sell <item>". Every item has a lower resale value than it\'s original purchase price.',
        EDIBLE: True,
        SELL: 1,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['howto', 'note', 'shop']},
    'Gravestone': {
        GROUNDDESC: 'A new gravestone.',
        SHORTDESC: 'A gravestone',
        LONGDESC: 'This is a gravestone. You can buy one now for your grave when you die.',
        COST: 100,
        SELL: 90,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['gravestone', 'headstone']},
    'Moneybag': {
        GROUNDDESC: 'A money bag is lying on the ground',
        SHORTDESC: 'a bag full of money',
        LONGDESC: 'The local currency used in the game',
        COST: 100,
        SELL: 100,
        SELLABLE: True,
        TYPE: 'inventory',
        DESCWORDS: ['moneybag', 'coins']},
    }

playerStats = {
    'Player Name': USERNAME,
    'Player IP': USERIPAD,
    'Node': NODENUMB,
    'Location': 'Town Square',
    'Health': 100,
    'XP': 1,
    'HP': 10,
    'Money': 10,
}

NPCs = {
    'Dave': {
        'Inventory': ['Meat Pie', 'Donut', 'Sword'],
        'Health': 100,
        'XP': 2,
        'HP': 1,
        'Money': 40,
        DESCWORDS: ['dave']},
    'Steve': {
        'Inventory': ['Meat Pie', 'Meat Pie', 'Meat Pie', 'Meat Pie', 'Donut', 'Donut', 'Donut', 'Donut', 'Donut', 'Sword'],
        'Health': 100,
        'XP': 2,
        'HP': 2,
        'Money': 100,
        DESCWORDS: ['steve']},
    'Fred': {
        'Inventory': ['Sword'],
        'Health': 100,
        'XP': 3,
        'HP': 3,
        'Money': 100,
        DESCWORDS: ['fred']},
    'Ghost of Christmas Present': {
        'Inventory': ['Meat Pie', 'Meat Pie', 'Meat Pie', 'Meat Pie', 'Meat Pie', 'Meat Pie', 'Meat Pie', 'Meat Pie', 'Meat Pie', 'Meat Pie', 'War Axe'],
        'Health': 150,
        'XP': 5,
        'HP': 10,
        'Money': 1000,    
        DESCWORDS: ['ghost', 'gocp']},
    'Sam': {
        'Inventory': ['Sword'],
        'Health': 100,
        'XP': 20,
        'HP': 10,
        'Money': 40,
        DESCWORDS: ['sam']},
    'Dean': {
        'Inventory': ['Meat Pie', 'Donut', 'Sword'],
        'Health': 100,
        'XP': 20,
        'HP': 10,
        'Money': 40,
        DESCWORDS: ['dean']},
    'Castiel': {
        'Inventory': ['Sword', 'Great Sword', 'War Axe'],
        'Health': 300,
        'XP': 200,
        'HP': 30,
        'Money': 0,
        DESCWORDS: ['castiel']},
    'Gabriel': {
        'Inventory': ['Sword', 'Great Sword', 'War Axe'],
        'Health': 300,
        'XP': 200,
        'HP': 30,
        'Money': 0,
        DESCWORDS: ['gabriel']},
    'Zachariah': {
        'Inventory': ['Sword', 'Great Sword', 'War Axe'],
        'Health': 300,
        'XP': 200,
        'HP': 50,
        'Money': 100,
        DESCWORDS: ['zachariah']},
    'Anna': {
        'Inventory': ['Sword', 'Great Sword', 'War Axe'],
        'Health': 300,
        'XP': 300,
        'HP': 30,
        'Money': 100,
        DESCWORDS: ['anna']},
    'Michael': {
        'Inventory': ['Sword', 'Great Sword', 'War Axe'],
        'Health': 500,
        'XP': 200,
        'HP': 50,
        'Money': 0,
        DESCWORDS: ['michael']},
    'Lucifer': {
        'Inventory': ['Sword', 'Great Sword', 'War Axe'],
        'Health': 500,
        'XP': 200,
        'HP': 50,
        'Money': 0,
        DESCWORDS: ['lucifer']},
    'Bobby': {
        'Inventory': ['Meat Pie', 'Donut', 'Sword'],
        'Health': 70,
        'XP': 20,
        'HP': 10,
        'Money': 400,
        DESCWORDS: ['bobby']},
    'Ruby': {
        'Inventory': ['Great Sword'],
        'Health': 200,
        'XP': 200,
        'HP': 20,
        'Money': 0,
        DESCWORDS: ['ruby']},
    'Meg': {
        'Inventory': ['Great Sword'],
        'Health': 200,
        'XP': 200,
        'HP': 20,
        'Money': 100,
        DESCWORDS: ['meg']},
}

"""
These variables track where the player is and what is in their inventory.
The value in the location variable will always be a key in the world variable
and the value in the inventory list will always be a key in the worldItems
variable.
"""
location = playerStats['Location'] # start in default player location denoted in the playerStats list
inventory = ['README Note', 'Sword', 'Donut'] # start with blank inventory
showFullExits = True
godMode = False

gameSeconds = 0
gameMinutes = 0
gameHours = 0

def placeRandoms():
    rooms = []
    randRooms = []
    
    items = []
    randItems = []

    for room in worldRooms:
        rooms.append(room)
        
    for item in worldItems:
        items.append(item)

    randRange = random.randint(10, len(worldRooms))

    # Lets place some money in some random rooms
    for r in range(randRange):
        randRooms.append(random.choice(rooms))
        
    for i in range(randRange):
        randItems.append(random.choice(items))

    for room in randRooms:
        #worldRooms[room][GROUND].append('Moneybag')
        if len(randItems) > 0:
            item = random.choice(randItems)
            randItems.remove(item)
            worldRooms[room][GROUND].append(item)
            if (len(randItems) % 3) > 1:
                worldRooms[room][GROUND].append('Moneybag')
                #print('Placed Moneybag at %s : %d' % (room, len(randItems) % 3))
            #print('Placed %s at %s : %d' % (item, room, len(randItems) % 3))

    # Lets place some NPC's in some random rooms
    npcs = []
    randNpcs = []
    rooms = []
    randRooms = []

    for item in worldRooms:
        rooms.append(item)

    for i in range(randRange):
        randRooms.append(random.choice(rooms))

    #randRooms = list(set(randRooms))

    for item in NPCs:
        npcs.append(item)

    for i in range(randRange):
        randNpcs.append(random.choice(npcs))

    randNpcs = list(set(randNpcs))


    for room in randRooms:
        if len(randNpcs) > 0:
            npc = random.choice(randNpcs)
            randNpcs.remove(npc)
            worldRooms[room][NPC].append(npc)
#             print('%s placed in %s' % (npc, room))
    print()


def displayLocation(loc):
    """A helper function for displaying an area's description and exits."""
    # Print the room name.
    print(loc)
    print('=' * len(loc))

    # Print the room's description (using textwrap.wrap())
    print('\n'.join(textwrap.wrap(worldRooms[loc][DESC], SCREEN_WIDTH)))

    # Print all the items on the ground.
    if len(worldRooms[loc][GROUND]) > 0:
        print()
        for item in worldRooms[loc][GROUND]:
            print(worldItems[item][GROUNDDESC])

    # Print any NPC's here
    npcs = worldRooms[loc][NPC]
    print()
    for npc in npcs:
        if NPCs[npc]['Health'] > 0:
            print('%s%s%s is nearby.' % (CYAN, npc, WHITE))
        else:
            print('%s\'s body is nearby.' % (npc))

    # Print all the exits.
    exits = []
    for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
        if direction in worldRooms[loc].keys():
            exits.append(direction.title())
    print()
    if showFullExits:
        for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
            if direction in worldRooms[location]:
                print('%s%s%s:\t%s' % (GREEN, direction.title(), WHITE, worldRooms[location][direction]))
    else:
        print('Exits: %s' % ' '.join(exits))


def moveDirection(direction):
    """A helper function that changes the location of the player."""
    if playerStats['Health'] < 1:
        print('You don\'t have enough health to do that.')
        return None

    global location

    if direction in worldRooms[location]:
        print('You move to the %s.' % direction)
        location = worldRooms[location][direction]
        displayLocation(location)
    else:
        print('You cannot move in that direction')

    if not godMode:
        playerStats['Health'] -= 1

    playerStats['Location'] = location


def getAllDescWords(itemList):
    """Returns a list of "description words" for each item named in itemList."""
    itemList = list(set(itemList)) # make itemList unique
    descWords = []
    for item in itemList:
        descWords.extend(worldItems[item][DESCWORDS])
    return list(set(descWords))

def getAllFirstDescWords(itemList):
    """Returns a list of the first "description word" in the list of
    description words for each item named in itemList."""
    itemList = list(set(itemList)) # make itemList unique
    descWords = []
    for item in itemList:
        descWords.append(worldItems[item][DESCWORDS][0])
    return list(set(descWords))

def getFirstItemMatchingDesc(desc, itemList):
    itemList = list(set(itemList)) # make itemList unique
    for item in itemList:
        if desc in worldItems[item][DESCWORDS]:
            return item
    return None

def getAllItemsMatchingDesc(desc, itemList):
    itemList = list(set(itemList)) # make itemList unique
    matchingItems = []
    for item in itemList:
        if desc in worldItems[item][DESCWORDS]:
            matchingItems.append(item)
    return matchingItems

def updatePrompt():
    health = playerStats['Health']
    
    if health > 10:
        healthColour = GREEN
    else:
        healthColour = RED
            
    TextAdventureCmd.prompt = '\n%s[Health:%s%d%s][Money:%s%d%s]\n> %s' % (YELLOW, healthColour, playerStats['Health'], YELLOW, GREEN, playerStats['Money'], YELLOW, WHITE)

def checkNPCs():
        npcs_alive = 0
        npcs_dead = 0
        for room in worldRooms:
            for npc in worldRooms[room][NPC]:
                if NPCs[npc]['Health'] > 0:
                    npcs_alive += 1
                if NPCs[npc]['Health'] < 1:
                    npcs_dead += 1

        totalNPCs = npcs_alive + npcs_dead
        print('NPC\'s still alive: %s\nNPC\'s killed: %s' % (npcs_alive, npcs_dead))
        if npcs_dead == totalNPCs:
            return True
        else:
            return False

class ThreadingExample(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        global gameSeconds
        global gameMinutes
        global gameHours

        while True:
            # Do something
            time.sleep(self.interval)
            if gameSeconds < 59:
                gameSeconds += 1
            else:
                gameSeconds = 0
                if gameMinutes < 59:
                    gameMinutes += 1
                else:
                    gameMinutes = 0
                    gameHours += 1
            
            updatePrompt()
            

class TextAdventureCmd(cmd.Cmd):
    prompt = '\n%s[Health:%s%d%s][Money:%s%d%s]\n> %s' % (YELLOW, GREEN, playerStats['Health'], YELLOW, GREEN, playerStats['Money'], YELLOW, WHITE)
    #updatePrompt()
    
    # The default() method is called when none of the other do_*() command methods match.
    def default(self, arg):
        print('I do not understand that command. Type "help" for a list of commands.')

    # A very simple "quit" command to terminate the program:
    def do_quit(self, arg):
        """Quit the game."""
        return True # this exits the Cmd application loop in TextAdventureCmd.cmdloop()

    def do_checknpcs(self, arg):
        """Check how many NPC's are alive and how many are dead"""
        print(checkNPCs())

    def do_signguestbook(self, arg):
        """Signs the guestbook if there's one to sign"""

        if worldRooms[location].get(GUESTBOOK) == None:
            print('You can\'t do that here')
            return

        guestbook = {}

        """
        guestbook = {
            'LOCATION': {
                'timestamp': {
                    NAME: USERNAME,
                    NODE: NODENUMB,
                    IPAD: USERIPAD},
            },
        }
        """

        file_guestbook = '%s%s.dat' % (SAVES_FOLDER, 'guestbook')

        if os.path.exists(file_guestbook) == False:
            print('No previous entries found')
            guestbook = {location: {}}
        else:
            guestbook = pickle.load(open(file_guestbook,'rb'))

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        #st = datetime.datetime.fromtimestamp(ts).strftime('%B %d, %Y %H:%M:%S')

        guestbook[location][st] = {'NAME': USERNAME, 'NODE': NODENUMB, 'IPAD': USERIPAD}
        os.system('clear')
        #print(location)
        #print(worldRooms[location].get(GUESTBOOK))
        #print(guestbook)
        pickle.dump(guestbook, open(file_guestbook,'wb'))
        print('Successfully added to the guestbook')
        guestbook = {}

    def do_readguestbook(self, arg):
        """Shows the entries in a guestbook"""
        if worldRooms[location].get(GUESTBOOK) == None:
            print('You can\'t do that here')
            return

        file_guestbook = '%s%s.dat' % (SAVES_FOLDER, 'guestbook')
        if os.path.exists(file_guestbook) == False:
            print('No previous entries found')
            return


        guestbook = {}
        gb_entries = []
        file_guestbook = '%s%s.dat' % (SAVES_FOLDER, 'guestbook')
        guestbook = pickle.load(open(file_guestbook, 'rb'))

        print('Showing the last 5 entries\n')
        print('.--------------------------+--------------------------+---------------------.')
        print('| ' + '{:25}'.format('Date') + '| ' + '{:25}'.format('Name') + '| ' + '{:20}'.format('IP') + '|')
        print('+--------------------------+--------------------------+---------------------+')


        for entry in guestbook[location]:
            gb_entries.append(entry)

        gb_last5 = gb_entries[-5:]

        for entry in gb_last5:
            user = guestbook[location][entry]['NAME']
            node = guestbook[location][entry]['NODE']
            ipad = guestbook[location][entry]['IPAD']

            entry_text = '| ' + '{:25.24}'.format(entry) + '| ' + '{:25.24}'.format(user) + '| ' + '{:20}'.format(ipad) + '|' 
            print('\n'.join(textwrap.wrap(entry_text, SCREEN_WIDTH)))
        print('\'--------------------------+--------------------------+---------------------\'')


    def do_save(self, arg):
        """Save current player's stats, location, any items carried, and state of any items and npc's left in the world"""
        """This is a work in progress"""
        global playerStats
        global inventory
        global worldRooms
        global NPCs
        global location

        #save player stats to file playername.playerStats
        file = '%s%s.%s' % (SAVES_FOLDER, USERNAME, 'playerStats')
        pickle.dump(playerStats, open(file,'wb'))

        #save player inventory to file playername.inventory
        file = '%s%s.%s' % (SAVES_FOLDER, USERNAME, 'inventory')
        pickle.dump(inventory, open(file,'wb'))

        #save current worldRooms data to file playername.worldRooms
        file = '%s%s.%s' % (SAVES_FOLDER, USERNAME, 'worldRooms')
        pickle.dump(worldRooms, open(file,'wb'))

        #save current NPCs data to file playername.NPCs
        file = '%s%s.%s' % (SAVES_FOLDER, USERNAME, 'NPCs')
        pickle.dump(NPCs, open(file,'wb'))

        print('Saved all data')


    def do_load(self, arg):
        """Load all the previously saved data from a player save"""
        global playerStats
        global inventory
        global worldRooms
        global NPCs
        global location

        file_stats = '%s%s.%s' % (SAVES_FOLDER, USERNAME, 'playerStats')
        file_inven = '%s%s.%s' % (SAVES_FOLDER, USERNAME, 'inventory')
        file_rooms = '%s%s.%s' % (SAVES_FOLDER, USERNAME, 'worldRooms')
        file_npcs  = '%s%s.%s' % (SAVES_FOLDER, USERNAME, 'NPCs')

        #check if a file exists, if not, assume that no save has been done before and return message saying no previous save
        if os.path.exists(file_stats) == False:
            print('No previous saves found')
            return


        #load player stats from file playername.playerStats
        playerStats = pickle.load(open(file_stats,'rb'))

        #load player inventory from file playername.inventory
        inventory = pickle.load(open(file_inven,'rb'))

        #load worldRooms from file playername.worldRooms
        worldRooms = pickle.load(open(file_rooms,'rb'))

        #load NPCs from file playername.NPCs
        NPCs = pickle.load(open(file_npcs,'rb'))

        #print('%s\n%s\n%s' % (playerStats, worldRooms, NPCs))
        location = playerStats['Location']

        updatePrompt()
        print('Loaded all data')


    def do_godMode(self, arg):
        """Enable / Disable God Mode (i.e. don't lose health over time)"""
        global godMode
        choice = arg.lower()
        
        if choice == 'status':
            if godMode == True:
                gmStatus = 'Enabled'
            else:
                gmStatus = 'Disabled'
            
        if choice == 'enable':
            godMode = True
        if choice == 'disable':
            godMode = False
        if choice == '':
            godMode = not godMode

        if godMode == True:
            gmStatus = 'Enabled'
        else:
            gmStatus = 'Disabled'
            
        print('God Mode: %s' % (gmStatus))
        
    def complete_godMode(self, text, line, begidx, endidx):
        possibleItems = ['status', 'enable', 'disable']
        return list(set(possibleItems))

    #def help_combat(self):
    #    print('Combat is not implemented in this program.')

    def help_hit(self):
        print('Use \'hit\' to hit a character.')

    def do_hit(self, arg):
        who = arg

        if playerStats['Health'] < 1:
            print('You don\'t have enough health to do that.')
            return None
            
        if NPCs[who]['Health'] < 1:
            print('You can\'t fight a dead person.')
            return None

        weaponsList = {}
        npcWeaponsList = {}

        swordCount = 0
        waraxeCount = 0
        weaponCount = 0
        
        npcSwordCount = 0
        npcWarAxeCount = 0
        npcWeaponCount = 0

        for item in inventory:
            if item == 'Sword' or item == 'Great Sword':
                swordCount += 1
                weaponsList.__setitem__(item, worldItems[item][DAMAGE])
            if item == 'War Axe':
                waraxeCount += 1
                weaponsList.__setitem__(item, worldItems[item][DAMAGE])
                
        for npcItem in NPCs[who]['Inventory']:
            if npcItem == 'Sword' or npcItem == 'Great Sword':
                npcSwordCount += 1
                npcWeaponsList.__setitem__(npcItem, worldItems[npcItem][DAMAGE])
            if npcItem == 'War Axe':
                npcWarAxeCount += 1
                npcWeaponsList.__setitem__(npcItem, worldItems[npcItem][DAMAGE])

        weaponCount = swordCount + waraxeCount
        npcWeaponCount = npcSwordCount + npcWarAxeCount

        bestWeapon = max(weaponsList, key=lambda key: weaponsList[key])
        bestWeaponDamage = worldItems[bestWeapon][DAMAGE]
        
        npcBestWeapon = max(npcWeaponsList, key=lambda key: npcWeaponsList[key])
        npcBestWeaponDamage = worldItems[npcBestWeapon][DAMAGE]
        
                
        if weaponCount > 0:
            canFight = True
        else:
            canFight = False

        if canFight == True:
            if who in worldRooms[location][NPC]:
                if NPCs[who]['Health'] > 0:
                    dam = random.randint(0, worldItems[bestWeapon][DAMAGE]) # - random.randint(0, NPCs[who]['HP']))
                    if godMode == False:
                        pdam = random.randint(0, (worldItems[npcBestWeapon][DAMAGE])) # - random.randint(0, playerStats['HP']))
                    else:
                        pdam = 0
                    if dam > NPCs[who]['Health']:
                        dam = NPCs[who]['Health']
                        playerStats['XP'] += NPCs[who]['XP']
                        playerStats['HP'] += NPCs[who]['HP']
                        NPCs[who]['XP'] = 0
                        NPCs[who]['HP'] = 0
                    NPCs[who]['Health'] -= dam 
                    if NPCs[who]['Health'] > 0:
                        print('You hit %s with a %s (MAX damage: %s), causing %d damage.\n%s now has %d health.' % (who, bestWeapon, bestWeaponDamage, dam, who, NPCs[who]['Health']))
                    else:
                        print('You killed %s!' % (who))
                    if NPCs[who]['Health'] > 0:
                        if pdam > playerStats['Health']:
                            pdam = playerStats['Health']
                        if pdam > playerStats['HP']:
                            playerStats['Health'] -= pdam - playerStats['HP']
                        print('%s hit you with a %s causing %d damage.' % (who, npcBestWeapon, pdam))
                else:
                    print('%s is dead.' % (who))
            else:
                print('%s isn\'t nearby.' % (who))
        else:
            print('You have nothing to hit %s with.' % (who))

        if not godMode: 
            playerStats['Health'] -= 1
            updatePrompt()

        if checkNPCs == True:
            print('Congratulations, you have defeated all the\nenemies and have won the game!')

    # These direction commands have a long (i.e. north) and show (i.e. n) form.
    # Since the code is basically the same, I put it in the moveDirection()
    # function.
    def do_north(self, arg):
        """Go to the area to the north, if possible."""
        if playerStats['Health'] > 0:
            moveDirection('north')
        else:
            print('You are too weak to move, you should probably eat something.')

    def do_south(self, arg):
        """Go to the area to the south, if possible."""
        if playerStats['Health'] > 0:
            moveDirection('south')
        else:
            print('You are too weak to move, you should probably eat something.')

    def do_east(self, arg):
        """Go to the area to the east, if possible."""
        if playerStats['Health'] > 0:
            moveDirection('east')
        else:
            print('You are too weak to move, you should probably eat something.')

    def do_west(self, arg):
        """Go to the area to the west, if possible."""
        if playerStats['Health'] > 0:
            moveDirection('west')
        else:
            print('You are too weak to move, you should probably eat something.')

    def do_up(self, arg):
        """Go to the area upwards, if possible."""
        if playerStats['Health'] > 0:
            moveDirection('up')
        else:
            print('You are too weak to move, you should probably eat something.')

    def do_down(self, arg):
        """Go to the area downwards, if possible."""
        if playerStats['Health'] > 0:
            moveDirection('down')
        else:
            print('You are too weak to move, you should probably eat something.')

    # Since the code is the exact same, we can just copy the
    # methods with shortened names:
    do_n = do_north
    do_s = do_south
    do_e = do_east
    do_w = do_west
    do_u = do_up
    do_d = do_down

    def do_exits(self, arg):
        """Toggle showing full exit descriptions or brief exit descriptions."""
        global showFullExits
        showFullExits = not showFullExits
        if showFullExits:
            print('Showing full exit descriptions.')
        else:
            print('Showing brief exit descriptions.')

    def do_inventory(self, arg):
        """Display a list of the items in your possession."""

        if len(inventory) == 0:
            print('Inventory:\n  (nothing)')
            return

        # first get a count of each distinct item in the inventory
        itemCount = {}
        for item in inventory:
            if item in itemCount.keys():
                itemCount[item] += 1
            else:
                itemCount[item] = 1

        # get a list of inventory items with duplicates removed:
        print('Inventory:')
        for item in set(inventory):
            if itemCount[item] > 1:
                print('  %s (%s%d%s)' % (item, GREEN, itemCount[item], WHITE))
            else:
                print('  ' + item)

    do_inv = do_inventory

    def do_stats(self, arg):
        """Display the user stats."""

        # get a list of inventory items with duplicates removed:
        print('User Stats:')
        for key in playerStats.keys():
            print('  %s\t%s%s%s' % (key.ljust(11), GREEN, playerStats[key], WHITE))
        print('\nTime played: %dh %dm %ds' % (gameHours, gameMinutes, gameSeconds))

    do_status = do_stats

    def do_loot(self, arg):
        """Loot a dead NPC"""
        item = arg
        if item in worldRooms[location][NPC]:
            lootMoney = NPCs[item]['Money']
            lootInv = len(NPCs[item]['Inventory'])
            healthNPC = NPCs[item]['Health']
            
            if healthNPC < 1:
                # steal NPC's money
                if lootMoney > 0:
                    NPCs[item]['Money'] -= lootMoney
                    playerStats['Money'] += lootMoney
                    updatePrompt()
                    print('Looted %d coins from %s' % (lootMoney, item))
                else:
                    print('No money to loot from %s' % (item))
                    
                # steal all items in NPC's inventory
                if lootInv > 0:
                    for invItem in NPCs[item]['Inventory']:
                        inventory.append(invItem)
                        print('Looted %s from %s' % (invItem, arg))
                    else:
                        NPCs[item]['Inventory'] = []
                print('Nothing else in %s\'s inventory is worth looting.' % (arg))
            else:
                print('Cannot loot as %s is not dead!' % (item))
        else:
            print('%s is not nearby.' % (item))

    def do_take(self, arg):
        """"take <item> - Take an item on the ground."""

        # put this value in a more suitably named variable
        itemToTake = arg.lower()

        if itemToTake == '':
            print('Take what? Type "look" the items on the ground here.')
            return

        cantTake = False

        # get the item name that the player's command describes
        for item in getAllItemsMatchingDesc(itemToTake, worldRooms[location][GROUND]):
            if worldItems[item].get(TAKEABLE, True) == False:
                cantTake = True
                continue # there may be other items named this that you can take, so we continue checking
            print('You take %s.' % (worldItems[item][SHORTDESC]))
            worldRooms[location][GROUND].remove(item) # remove from the ground
            if worldItems[item][TYPE] == 'playerStats':
                playerStats[item] += 1
                updatePrompt()
            else:
                inventory.append(item) # add to inventory
            return

        if cantTake:
            print('You cannot take "%s".' % (itemToTake))
        else:
            print('That is not on the ground.')


    def do_drop(self, arg):
        """"drop <item> - Drop an item from your inventory onto the ground."""

        # put this value in a more suitably named variable
        itemToDrop = arg.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)

        # find out if the player doesn't have that item
        if itemToDrop not in invDescWords:
            print('You do not have "%s" in your inventory.' % (itemToDrop))
            return

        # get the item name that the player's command describes
        item = getFirstItemMatchingDesc(itemToDrop, inventory)
        if item != None:
            print('You drop %s.' % (worldItems[item][SHORTDESC]))
            inventory.remove(item) # remove from inventory
            worldRooms[location][GROUND].append(item) # add to the ground


    def complete_take(self, text, line, begidx, endidx):
        possibleItems = []
        text = text.lower()

        # if the user has only typed "take" but no item name:
        if not text:
            return getAllFirstDescWords(worldRooms[location][GROUND])

        # otherwise, get a list of all "description words" for ground items matching the command text so far:
        for item in list(set(worldRooms[location][GROUND])):
            for descWord in worldItems[item][DESCWORDS]:
                if descWord.startswith(text) and worldItems[item].get(TAKEABLE, True):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique

    def complete_loot(self, text, line, begidx, endidx):
        possibleNPCs = []
        text = text.lower()

        # if the user has only typed "loot" but no NPC name:
        if not text:
            for npc in worldRooms[location][NPC]:
                possibleNPCs.append(npc)
            return possibleNPCs

        return list(set(possibleNPCs)) # make list unique 

    def complete_drop(self, text, line, begidx, endidx):
        possibleItems = []
        itemToDrop = text.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)

        for descWord in invDescWords:
            if line.startswith('drop %s' % (descWord)):
                return [] # command is complete

        # if the user has only typed "drop" but no item name:
        if itemToDrop == '':
            return getAllFirstDescWords(inventory)

        # otherwise, get a list of all "description words" for inventory items matching the command text so far:
        for descWord in invDescWords:
            if descWord.startswith(text):
                possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique


    def do_look(self, arg):
        """Look at an item, direction, or the area:
        "look" - display the current area's description
        "look <direction>" - display the description of the area in that direction
        "look exits" - display the description of all adjacent areas
        "look <item>" - display the description of an item on the ground or in your inventory"""

        lookingAt = arg.lower()
        if lookingAt == '':
            # "look" will re-print the area description
            displayLocation(location)
            return

        if lookingAt == 'exits':
            for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
                if direction in worldRooms[location]:
                    print('%s: %s' % (direction.title(), worldRooms[location][direction]))
            return

        if lookingAt in ('north', 'west', 'east', 'south', 'up', 'down', 'n', 'w', 'e', 's', 'u', 'd'):
            if lookingAt.startswith('n') and NORTH in worldRooms[location]:
                print(worldRooms[location][NORTH])
            elif lookingAt.startswith('w') and WEST in worldRooms[location]:
                print(worldRooms[location][WEST])
            elif lookingAt.startswith('e') and EAST in worldRooms[location]:
                print(worldRooms[location][EAST])
            elif lookingAt.startswith('s') and SOUTH in worldRooms[location]:
                print(worldRooms[location][SOUTH])
            elif lookingAt.startswith('u') and UP in worldRooms[location]:
                print(worldRooms[location][UP])
            elif lookingAt.startswith('d') and DOWN in worldRooms[location]:
                print(worldRooms[location][DOWN])
            else:
                print('There is nothing in that direction.')
            return

        # see if the item being looked at is on the ground at this location
        item = getFirstItemMatchingDesc(lookingAt, worldRooms[location][GROUND])
        if item != None:
            print('\n'.join(textwrap.wrap(worldItems[item][LONGDESC], SCREEN_WIDTH)))
            return

        # see if the item being looked at is in the inventory
        item = getFirstItemMatchingDesc(lookingAt, inventory)
        if item != None:
            print('\n'.join(textwrap.wrap(worldItems[item][LONGDESC], SCREEN_WIDTH)))
            return

        # see if the item being looked at is an NPC
        item = arg
        if item in worldRooms[location][NPC]:
            print(NPCs[item])
            return

        print('You do not see that nearby.')


    def complete_look(self, text, line, begidx, endidx):
        possibleItems = []
        lookingAt = text.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)
        groundDescWords = getAllDescWords(worldRooms[location][GROUND])
        shopDescWords = getAllDescWords(worldRooms[location].get(SHOP, []))

        for npc in worldRooms[location][NPC]:
            possibleItems.append(npc)

        for descWord in invDescWords + groundDescWords + shopDescWords + [NORTH, SOUTH, EAST, WEST, UP, DOWN]:
            if line.startswith('look %s' % (descWord)):
                return [] # command is complete

        # if the user has only typed "look" but no item name, show all items on ground, shop and directions:
        if lookingAt == '':
            possibleItems.extend(getAllFirstDescWords(worldRooms[location][GROUND]))
            possibleItems.extend(getAllFirstDescWords(worldRooms[location].get(SHOP, [])))
            for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
                if direction in worldRooms[location]:
                    possibleItems.append(direction)
            return list(set(possibleItems)) # make list unique

        # otherwise, get a list of all "description words" for ground items matching the command text so far:
        for descWord in groundDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        # otherwise, get a list of all "description words" for items for sale at the shop (if this is one):
        for descWord in shopDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        # check for matching directions
        for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
            if direction.startswith(lookingAt):
                possibleItems.append(direction)

        # get a list of all "description words" for inventory items matching the command text so far:
        for descWord in invDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique


    def do_list(self, arg):
        """List the items for sale at the current location's shop. "list full" will show details of the items."""
        if SHOP not in worldRooms[location]:
            print('This is not a shop.')
            return

        arg = arg.lower()

        print('For sale:')
        for item in worldRooms[location][SHOP]:
            print('  - %s' % (item))
            if arg == 'full':
                print('\n'.join(textwrap.wrap(worldItems[item][LONGDESC], SCREEN_WIDTH)))


    def do_buy(self, arg):
        """"buy <item>" - buy an item at the current location's shop."""
        if SHOP not in worldRooms[location]:
            print('This is not a shop.')
            return

        itemToBuy = arg.lower()

        if itemToBuy == '':
            print('Buy what? Type "list" or "list full" to see a list of items for sale.')
            return

        item = getFirstItemMatchingDesc(itemToBuy, worldRooms[location][SHOP])
        if item != None:
            # NOTE - If you wanted to implement money, here is where you would add
            # code that checks if the player has enough, then deducts the price
            # from their money.
            costs = worldItems[item][COST]
            print('%s costs %d coins' % (worldItems[item][SHORTDESC], costs))

            # if there's enough money in the bank, you can buy item
            moneyAvailable = 0
            moneyAvailable = playerStats['Money']

            print('You have %d coins' % (moneyAvailable))

            if moneyAvailable >= costs:
                playerStats['Money'] -= costs
                inventory.append(item)
                updatePrompt()
                print('You have purchased %s' % (worldItems[item][SHORTDESC]))
                print('You now have %d coins left' % (playerStats['Money']))
            else:
                print('You do not have enough money to buy %s' % (worldItems[item][SHORTDESC]))

            return

        print('"%s" is not sold here. Type "list" or "list full" to see a list of items for sale.' % (itemToBuy))


    def complete_buy(self, text, line, begidx, endidx):
        if SHOP not in worldRooms[location]:
            return []

        itemToBuy = text.lower()
        possibleItems = []

        # if the user has only typed "buy" but no item name:
        if not itemToBuy:
            return getAllFirstDescWords(worldRooms[location][SHOP])

        # otherwise, get a list of all "description words" for shop items matching the command text so far:
        for item in list(set(worldRooms[location][SHOP])):
            for descWord in worldItems[item][DESCWORDS]:
                if descWord.startswith(text):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique


    def do_sell(self, arg):
        """"sell <item>" - sell an item at the current location's shop."""
        if SHOP not in worldRooms[location]:
            print('This is not a shop.')
            return

        itemToSell = arg.lower()

        if itemToSell == '':
            print('Sell what? Type "inventory" or "inv" to see your inventory.')
            return

        for item in inventory:
            if itemToSell in worldItems[item][DESCWORDS]:
                # NOTE - If you wanted to implement money, here is where you would add
                # code that gives the player money for selling the item.
                isSellable = worldItems[item][SELLABLE]
                if isSellable == False:
                    print('This item is not sellable')
                    return
                sells = worldItems[item][SELL]
                """for sellfor in range(sells):
                    inventory.append('Money')"""
                playerStats['Money'] += sells
                updatePrompt()

                print('You have sold %s for %d coins' % (worldItems[item][SHORTDESC], sells))
                inventory.remove(item)
                return

        print('You do not have "%s". Type "inventory" or "inv" to see your inventory.' % (itemToSell))

    def do_value(self, arg):
        """"value <item>" - find out what an item is worth at the current location's shop."""
        if SHOP not in worldRooms[location]:
            print('This is not a shop.')
            return

        itemToValue = arg.lower()

        if itemToValue == '':
            print('Value what? Type "inventory" or "inv" to see your inventory.')
            return

        for item in inventory:
            if itemToValue in worldItems[item][DESCWORDS]:
                # NOTE - If you wanted to implement money, here is where you would add
                # code that gives the player money for selling the item.
                isSellable = worldItems[item][SELLABLE]
                if isSellable == False:
                    print('This item is not sellable')
                    return
                getValue = worldItems[item][SELL]
                if getValue > 1:
                    coinStatus = 's'
                else:
                    coinStatus = ''

                print('The shopkeeper will give you %d coin%s' % (getValue, coinStatus))
                return


    def complete_sell(self, text, line, begidx, endidx):
        if SHOP not in worldRooms[location]:
            return []

        itemToSell = text.lower()
        possibleItems = []

        # if the user has only typed "sell" but no item name:
        if not itemToSell:
            return getAllFirstDescWords(inventory)

        # otherwise, get a list of all "description words" for inventory items matching the command text so far:
        for item in list(set(inventory)):
            for descWord in worldItems[item][DESCWORDS]:
                if descWord.startswith(text):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique


    def do_eat(self, arg):
        """"eat <item>" - eat an item in your inventory."""
        itemToEat = arg.lower()

        if itemToEat == '':
            print('Eat what? Type "inventory" or "inv" to see your inventory.')
            return

        cantEat = False

        for item in getAllItemsMatchingDesc(itemToEat, inventory):
            if worldItems[item].get(EDIBLE, False) == False:
                cantEat = True
                continue # there may be other items named this that you can eat, so we continue checking
            # NOTE - If you wanted to implement hunger levels, here is where
            # you would add code that changes the player's hunger level.
            print('You eat %s' % (worldItems[item][SHORTDESC]))
            playerStats['Health'] += worldItems[item][GAIN]
            inventory.remove(item)
            updatePrompt()
            return

        if cantEat:
            print('You cannot eat that.')
        else:
            print('You do not have "%s". Type "inventory" or "inv" to see your inventory.' % (itemToEat))


    def complete_eat(self, text, line, begidx, endidx):
        itemToEat = text.lower()
        possibleItems = []

        # if the user has only typed "eat" but no item name:
        if itemToEat == '':
            return getAllFirstDescWords(inventory)

        # otherwise, get a list of all "description words" for edible inventory items matching the command text so far:
        for item in list(set(inventory)):
            for descWord in worldItems[item][DESCWORDS]:
                if descWord.startswith(text) and worldItems[item].get(EDIBLE, False):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique


if __name__ == '__main__':
    # Initialize 'colorama'
    colorama.init()
    print(WHITE)
    print('Text Adventure!')
    print('===============')
    print()
    print('Welcome %s from IP %s on node %s' % (USERNAME, USERIPAD, NODENUMB))
#    print('Your security level is %s' % (USERSECL))
    print('(Type "help" for commands.)')
    print()
    placeRandoms()
    displayLocation(location)
    example = ThreadingExample()
    TextAdventureCmd().cmdloop()
    print('Thanks for playing!')

    # Deinitialize 'colorama'
    colorama.deinit()
