# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tools and data for San Francisco food-themed bike route planning with route optimization."""

import math
import urllib.parse
from typing import Any

# Approximate coordinates for SF neighborhoods/landmarks used for distance estimation and TSP ordering
LOCATION_COORDINATES: dict[str, tuple[float, float]] = {
    # Hubs & Parks
    "fort mason": (37.8058, -122.4287),
    "marina green": (37.8066, -122.4384),
    "presidio tunnel tops": (37.8028, -122.4590),
    "mission dolores park": (37.7596, -122.4269),
    "alamo square park": (37.7764, -122.4347),
    "duboce park": (37.7694, -122.4332),
    "golden gate park panhandle": (37.7719, -122.4468),
    "washington square park": (37.8008, -122.4098),
    "crissy field east beach": (37.8054, -122.4503),
    "buena vista park": (37.7681, -122.4414),
    "bernal heights park": (37.7431, -122.4146),
    "lafayette park": (37.7915, -122.4278),
    "alta plaza park": (37.7914, -122.4373),
    "glen canyon park": (37.7397, -122.4429),
    # Bakeries & Cookie Crawl
    "arsicault bakery": (37.7834, -122.4591),
    "jane the bakery": (37.7842, -122.4330),
    "b. patisserie": (37.7879, -122.4409),
    "tartine bakery": (37.7614, -122.4241),
    "devil's teeth baking company": (37.7538, -122.5057),
    "neighbor bakehouse": (37.7597, -122.3883),
    "anthony's cookies": (37.7516, -122.4208),
    "the mill": (37.7764, -122.4381),
    "arizmendi bakery": (37.7634, -122.4665),
    "craftsman and wolves": (37.7599, -122.4215),
    # Burrito Trail
    "la taqueria": (37.7517, -122.4181),
    "taqueria el farolito": (37.7527, -122.4182),
    "taqueria cancún": (37.7604, -122.4195),
    "papalote mexican grill": (37.7521, -122.4209),
    "taqueria guadalajara": (37.7212, -122.4371),
    "señor sisig": (37.7566, -122.4213),
    "taqueria san francisco": (37.7529, -122.4101),
    "gordo taqueria": (37.7828, -122.4831),
    "pancho villa taqueria": (37.7648, -122.4216),
    "underdogs tres": (37.7648, -122.4661),
    "taqueria vallarta": (37.7514, -122.4182),
    "el toro taqueria": (37.7628, -122.4219),
    "taqueria los mayas": (37.7828, -122.4628),
    "el castillito": (37.7694, -122.4335),
    "garaje": (37.7817, -122.3967),
    # Pizza Quest
    "tony's pizza napoletana": (37.8003, -122.4090),
    "golden boy pizza": (37.8004, -122.4081),
    "pizzeria delfina": (37.7614, -122.4252),
    "arizmendi bakery (pizza)": (37.7522, -122.4208),
    "little star pizza": (37.7753, -122.4378),
    "slice house by tony gemignani": (37.7698, -122.4491),
    "outta sight pizza": (37.7818, -122.4180),
    "damnfine pizza": (37.7609, -122.5055),
    "square pie guys": (37.7779, -122.4093),
    "il casaro pizzeria": (37.7984, -122.4074),
    # Ice Cream Artisans
    "bi-rite creamery": (37.7616, -122.4257),
    "humphry slocombe": (37.7528, -122.4132),
    "smitten ice cream": (37.7766, -122.4243),
    "salt & straw": (37.7897, -122.4343),
    "mitchell's ice cream": (37.7441, -122.4226),
    "swensen's ice cream": (37.7979, -122.4173),
    "garden creamery": (37.7588, -122.4209),
    "polly ann ice cream": (37.7539, -122.4975),
    "milkbomb ice cream": (37.7645, -122.4011),
    "matcha cafe maiko": (37.7854, -122.4307),
    # Dim Sum, Dumplings & Asian Street Food
    "good mong kok bakery": (37.7954, -122.4069),
    "city discount dim sum": (37.7947, -122.4080),
    "dragon beaux": (37.7807, -122.4789),
    "hang ah tea room": (37.7932, -122.4067),
    "yummy bakery & deli": (37.7952, -122.4060),
    "kingdom of dumpling": (37.7431, -122.4837),
    "saigon sandwich": (37.7831, -122.4184),
    "dinosaurs vietnamese sandwiches": (37.7646, -122.4326),
    # Boba Tea, Craft Coffee & Desserts
    "boba guys": (37.7599, -122.4215),
    "urban ritual": (37.7778, -122.4239),
    "sightglass coffee": (37.7769, -122.4085),
    "ritual coffee roasters": (37.7565, -122.4214),
    "dynamo donut & bike": (37.7516, -122.4124),
    "twisted donuts & coffee": (37.7606, -122.4828),
    "ferry building marketplace": (37.7955, -122.3937),
    "woodhouse fish co": (37.7694, -122.4323),
    # Additional Dim Sum, Banh Mi, Boba, Donuts, Seafood
    "city discount dim sum": (37.7947, -122.4080),
    "tc pastry": (37.7638, -122.4691),
    "yuanbao jiaozi": (37.7634, -122.4801),
    "dumpling time": (37.7702, -122.4039),
    "dumpling home": (37.7758, -122.4224),
    "banh mi ba le": (37.7634, -122.4784),
    "sing sing sandwich shop": (37.7853, -122.4158),
    "dragoneats": (37.8005, -122.4398),
    "l&g vietnamese sandwich": (37.7836, -122.4178),
    "bun mee": (37.7891, -122.4343),
    "duc huong sandwiches": (37.7606, -122.4804),
    "asha tea house": (37.7885, -122.4038),
    "plentea": (37.7909, -122.4042),
    "tp tea": (37.7824, -122.4237),
    "wonderful foods co": (37.7633, -122.4795),
    "milk tea lab": (37.7431, -122.4838),
    "chicha san chen": (37.7844, -122.4069),
    "bob's donut & pastry": (37.7919, -122.4212),
    "uncle boy's": (37.7797, -122.4619),
    "happy donuts": (37.7516, -122.4286),
    "allstar donuts": (37.7512, -122.4312),
    "johnny doughnuts": (37.7766, -122.4226),
    "rolling out cafe": (37.7430, -122.4839),
    "boudin bakery flagship": (37.8085, -122.4151),
    "scoma's restaurant fish prep": (37.8089, -122.4182),
    "hog island oyster co": (37.7955, -122.3937),
    "the codmother fish and chips": (37.8074, -122.4179),
    "acme bread company": (37.7955, -122.3937),
    "hook fish co": (37.7609, -122.5054),
}

# Curated database of renowned SF food spots categorized by theme
SF_FOOD_SPOTS: list[dict[str, Any]] = [
    # Chocolate Chip Cookies & Bakeries
    {
        "name": "Arsicault Bakery",
        "theme": "chocolate chip cookie",
        "address": "397 Arguello Blvd, San Francisco, CA 94118",
        "neighborhood": "Inner Richmond",
        "hours": "Wed-Sun 8:00 AM - 3:00 PM",
        "open_time": "08:00",
        "close_time": "15:00",
        "specialty": "Award-winning chocolate chip cookies & croissants",
    },
    {
        "name": "Jane the Bakery",
        "theme": "chocolate chip cookie",
        "address": "1839 Geary Blvd, San Francisco, CA 94115",
        "neighborhood": "Fillmore / Western Addition",
        "hours": "Daily 7:00 AM - 4:00 PM",
        "open_time": "07:00",
        "close_time": "16:00",
        "specialty": "Classic chocolate chip cookies, sourdough, and espresso",
    },
    {
        "name": "B. Patisserie",
        "theme": "chocolate chip cookie",
        "address": "2821 California St, San Francisco, CA 94115",
        "neighborhood": "Pacific Heights",
        "hours": "Wed-Sun 8:00 AM - 4:00 PM",
        "open_time": "08:00",
        "close_time": "16:00",
        "specialty": "Salted chocolate chip cookie & kouign-amann",
    },
    {
        "name": "Tartine Bakery",
        "theme": "chocolate chip cookie",
        "address": "600 Guerrero St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 8:00 AM - 5:00 PM",
        "open_time": "08:00",
        "close_time": "17:00",
        "specialty": "Rye chocolate chip cookie & morning buns",
    },
    {
        "name": "Devil's Teeth Baking Company",
        "theme": "chocolate chip cookie",
        "address": "3876 Noriega St, San Francisco, CA 94122",
        "neighborhood": "Outer Sunset",
        "hours": "Daily 7:00 AM - 4:00 PM",
        "open_time": "07:00",
        "close_time": "16:00",
        "specialty": "Warm chocolate chip cookies & breakfast sandwiches",
    },
    {
        "name": "Neighbor Bakehouse",
        "theme": "chocolate chip cookie",
        "address": "2343 3rd St, San Francisco, CA 94107",
        "neighborhood": "Dogpatch",
        "hours": "Wed-Sun 6:30 AM - 2:00 PM",
        "open_time": "06:30",
        "close_time": "14:00",
        "specialty": "Valrhona chocolate chip cookie & ginger pull-apart",
    },
    {
        "name": "Anthony's Cookies",
        "theme": "chocolate chip cookie",
        "address": "1417 Valencia St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Tue-Sat 10:00 AM - 6:00 PM",
        "open_time": "10:00",
        "close_time": "18:00",
        "specialty": "Fresh-baked classic and toffee chip cookies",
    },
    {
        "name": "The Mill",
        "theme": "chocolate chip cookie",
        "address": "736 Divisadero St, San Francisco, CA 94117",
        "neighborhood": "NoPa",
        "hours": "Daily 7:00 AM - 5:00 PM",
        "open_time": "07:00",
        "close_time": "17:00",
        "specialty": "Sea salt chocolate chip cookie & Josey Baker toast",
    },
    {
        "name": "Arizmendi Bakery",
        "theme": "chocolate chip cookie",
        "address": "1331 9th Ave, San Francisco, CA 94122",
        "neighborhood": "Inner Sunset",
        "hours": "Tue-Sun 7:00 AM - 5:00 PM",
        "open_time": "07:00",
        "close_time": "17:00",
        "specialty": "Worker-owned bakery cookies, muffins & daily focaccia",
    },
    {
        "name": "Craftsman and Wolves",
        "theme": "chocolate chip cookie",
        "address": "746 Valencia St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 8:00 AM - 4:00 PM",
        "open_time": "08:00",
        "close_time": "16:00",
        "specialty": "Gourmet chocolate chip walnut cookies & pastry art",
    },

    # Best Burritos / Mexican
    {
        "name": "La Taqueria",
        "theme": "burrito",
        "address": "2889 Mission St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Wed-Sun 11:00 AM - 8:45 PM",
        "open_time": "11:00",
        "close_time": "20:45",
        "specialty": "Golden dorado-style carnitas burrito (no rice)",
    },
    {
        "name": "Taqueria El Farolito",
        "theme": "burrito",
        "address": "2779 Mission St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 10:00 AM - 2:00 AM",
        "open_time": "10:00",
        "close_time": "02:00",
        "specialty": "Iconic super burrito with carne asada",
    },
    {
        "name": "Taqueria Cancún",
        "theme": "burrito",
        "address": "2288 Mission St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 10:00 AM - 12:00 AM",
        "open_time": "10:00",
        "close_time": "00:00",
        "specialty": "Super burrito al pastor with house avocado salsa",
    },
    {
        "name": "Papalote Mexican Grill",
        "theme": "burrito",
        "address": "3409 24th St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 11:00 AM - 9:00 PM",
        "open_time": "11:00",
        "close_time": "21:00",
        "specialty": "Triple threat burrito and legendary roasted salsa",
    },
    {
        "name": "Taqueria Guadalajara",
        "theme": "burrito",
        "address": "4798 Mission St, San Francisco, CA 94112",
        "neighborhood": "Excelsior",
        "hours": "Daily 9:00 AM - 11:00 PM",
        "open_time": "09:00",
        "close_time": "23:00",
        "specialty": "Super chile verde or lengua burrito",
    },
    {
        "name": "Señor Sisig",
        "theme": "burrito",
        "address": "990 Valencia St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 11:00 AM - 9:00 PM",
        "open_time": "11:00",
        "close_time": "21:00",
        "specialty": "Filipino-fusion California sisig burrito",
    },
    {
        "name": "Taqueria San Francisco",
        "theme": "burrito",
        "address": "2798 24th St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 9:30 AM - 9:00 PM",
        "open_time": "09:30",
        "close_time": "21:00",
        "specialty": "Authentic carnitas & chorizo burritos",
    },
    {
        "name": "Gordo Taqueria",
        "theme": "burrito",
        "address": "2252 Clement St, San Francisco, CA 94121",
        "neighborhood": "Richmond District",
        "hours": "Daily 10:00 AM - 9:00 PM",
        "open_time": "10:00",
        "close_time": "21:00",
        "specialty": "Steamed cheese & carnitas super burrito",
    },
    {
        "name": "Pancho Villa Taqueria",
        "theme": "burrito",
        "address": "3071 16th St, San Francisco, CA 94103",
        "neighborhood": "Mission District",
        "hours": "Daily 10:00 AM - 10:00 PM",
        "open_time": "10:00",
        "close_time": "22:00",
        "specialty": "Mesquite grilled prawn and carne asada burrito",
    },
    {
        "name": "Underdogs Tres",
        "theme": "burrito",
        "address": "1224 9th Ave, San Francisco, CA 94122",
        "neighborhood": "Inner Sunset",
        "hours": "Daily 11:00 AM - 10:00 PM",
        "open_time": "11:00",
        "close_time": "22:00",
        "specialty": "Nick's Way tacos & Baja California burritos",
    },
    {
        "name": "Taqueria Vallarta",
        "theme": "burrito",
        "address": "3033 24th St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 10:00 AM - 11:00 PM",
        "open_time": "10:00",
        "close_time": "23:00",
        "specialty": "Street-style pastor burritos & salsa bar",
    },
    {
        "name": "El Toro Taqueria",
        "theme": "burrito",
        "address": "598 Valencia St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 10:00 AM - 9:00 PM",
        "open_time": "10:00",
        "close_time": "21:00",
        "specialty": "Pollo asado & carnitas burritos with house-made tortilla chips",
    },
    {
        "name": "Taqueria Los Mayas",
        "theme": "burrito",
        "address": "331 Clement St, San Francisco, CA 94118",
        "neighborhood": "Inner Richmond",
        "hours": "Daily 11:00 AM - 9:00 PM",
        "open_time": "11:00",
        "close_time": "21:00",
        "specialty": "Yucatan panuchos, cochinita pibil burritos",
    },
    {
        "name": "El Castillito",
        "theme": "burrito",
        "address": "136 Church St, San Francisco, CA 94114",
        "neighborhood": "Duboce Triangle",
        "hours": "Daily 10:00 AM - 10:00 PM",
        "open_time": "10:00",
        "close_time": "22:00",
        "specialty": "Crispy seared carne asada super burrito along The Wiggle",
    },
    {
        "name": "Garaje",
        "theme": "burrito",
        "address": "475 3rd St, San Francisco, CA 94107",
        "neighborhood": "SoMa",
        "hours": "Mon-Sat 11:30 AM - 8:30 PM",
        "open_time": "11:30",
        "close_time": "20:30",
        "specialty": "Zapatos (pressed griddled burrito-torta hybrids)",
    },

    # Pizza Quest
    {
        "name": "Tony's Pizza Napoletana",
        "theme": "pizza",
        "address": "1570 Stockton St, San Francisco, CA 94133",
        "neighborhood": "North Beach",
        "hours": "Wed-Sun 12:00 PM - 10:00 PM",
        "open_time": "12:00",
        "close_time": "22:00",
        "specialty": "World-champion Margherita & Coal-fired New Yorker",
    },
    {
        "name": "Golden Boy Pizza",
        "theme": "pizza",
        "address": "542 Green St, San Francisco, CA 94133",
        "neighborhood": "North Beach",
        "hours": "Daily 11:30 AM - 11:00 PM",
        "open_time": "11:30",
        "close_time": "23:00",
        "specialty": "Sicilian square clam and garlic slice",
    },
    {
        "name": "Pizzeria Delfina",
        "theme": "pizza",
        "address": "3611 18th St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 11:30 AM - 9:00 PM",
        "open_time": "11:30",
        "close_time": "21:00",
        "specialty": "Clam pie & Salsiccia thin-crust Neapolitan",
    },
    {
        "name": "Arizmendi Bakery (Pizza)",
        "theme": "pizza",
        "address": "1268 Valencia St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Tue-Sun 8:30 AM - 6:00 PM (Pizza from 11:00 AM)",
        "open_time": "11:00",
        "close_time": "18:00",
        "specialty": "Daily rotating artisanal sourdough vegetarian pizza slice",
    },
    {
        "name": "Little Star Pizza",
        "theme": "pizza",
        "address": "846 Divisadero St, San Francisco, CA 94117",
        "neighborhood": "NoPa / Alamo Square",
        "hours": "Tue-Sun 11:30 AM - 9:30 PM",
        "open_time": "11:30",
        "close_time": "21:30",
        "specialty": "Cornmeal deep dish Brass Monkey or Little Star",
    },
    {
        "name": "Slice House by Tony Gemignani",
        "theme": "pizza",
        "address": "1535 Haight St, San Francisco, CA 94117",
        "neighborhood": "Haight-Ashbury",
        "hours": "Daily 11:00 AM - 9:00 PM",
        "open_time": "11:00",
        "close_time": "21:00",
        "specialty": "Grandma square & New York style pepperoni slices",
    },
    {
        "name": "Outta Sight Pizza",
        "theme": "pizza",
        "address": "422 Larkin St, San Francisco, CA 94102",
        "neighborhood": "Civic Center / Tenderloin",
        "hours": "Tue-Sat 11:00 AM - 7:00 PM",
        "open_time": "11:00",
        "close_time": "19:00",
        "specialty": "NY-style crispy crust pepperoni & cacio e pepe slice",
    },
    {
        "name": "DamnFine Pizza",
        "theme": "pizza",
        "address": "1394 46th Ave, San Francisco, CA 94122",
        "neighborhood": "Outer Sunset",
        "hours": "Wed-Sun 12:00 PM - 9:00 PM",
        "open_time": "12:00",
        "close_time": "21:00",
        "specialty": "Coastal wood-fired pizza & hot honey",
    },
    {
        "name": "Square Pie Guys",
        "theme": "pizza",
        "address": "1077 Mission St, San Francisco, CA 94103",
        "neighborhood": "SoMa",
        "hours": "Daily 11:30 AM - 9:30 PM",
        "open_time": "11:30",
        "close_time": "21:30",
        "specialty": "Detroit-style crispy cheesy corner squares",
    },
    {
        "name": "Il Casaro Pizzeria",
        "theme": "pizza",
        "address": "348 Columbus Ave, San Francisco, CA 94133",
        "neighborhood": "North Beach",
        "hours": "Daily 12:00 PM - 10:00 PM",
        "open_time": "12:00",
        "close_time": "22:00",
        "specialty": "Wood-fired Diavola pizza & fresh mozzarella",
    },

    # Ice Cream Artisans
    {
        "name": "Bi-Rite Creamery",
        "theme": "ice cream",
        "address": "3692 18th St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 12:00 PM - 9:00 PM",
        "open_time": "12:00",
        "close_time": "21:00",
        "specialty": "Salted Caramel and Balsamic Strawberry ice cream",
    },
    {
        "name": "Humphry Slocombe",
        "theme": "ice cream",
        "address": "2790A Harrison St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 12:00 PM - 9:00 PM",
        "open_time": "12:00",
        "close_time": "21:00",
        "specialty": "Secret Breakfast (Bourbon & Cornflakes) and Blue Bottle Vietnamese Coffee",
    },
    {
        "name": "Smitten Ice Cream",
        "theme": "ice cream",
        "address": "432 Octavia St, San Francisco, CA 94102",
        "neighborhood": "Hayes Valley",
        "hours": "Daily 12:00 PM - 9:00 PM",
        "open_time": "12:00",
        "close_time": "21:00",
        "specialty": "Liquid nitrogen churned fresh Earl Grey and Cookie Dough",
    },
    {
        "name": "Salt & Straw",
        "theme": "ice cream",
        "address": "2201 Fillmore St, San Francisco, CA 94115",
        "neighborhood": "Pacific Heights",
        "hours": "Daily 11:00 AM - 11:00 PM",
        "open_time": "11:00",
        "close_time": "23:00",
        "specialty": "Sea Salt with Caramel Ribbons & Honey Lavender",
    },
    {
        "name": "Mitchell's Ice Cream",
        "theme": "ice cream",
        "address": "688 San Jose Ave, San Francisco, CA 94110",
        "neighborhood": "Bernal Heights / Mission",
        "hours": "Daily 11:00 AM - 9:00 PM",
        "open_time": "11:00",
        "close_time": "21:00",
        "specialty": "Heritage Ube, Macapuno, and Mango tropical flavors",
    },
    {
        "name": "Swensen's Ice Cream",
        "theme": "ice cream",
        "address": "1999 Hyde St, San Francisco, CA 94109",
        "neighborhood": "Russian Hill",
        "hours": "Daily 12:00 PM - 10:00 PM",
        "open_time": "12:00",
        "close_time": "22:00",
        "specialty": "Original 1948 shop famous for Sticky Peanut Butter and Swiss Orange Chip",
    },
    {
        "name": "Garden Creamery",
        "theme": "ice cream",
        "address": "3566 20th St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Wed-Sun 12:00 PM - 10:00 PM",
        "open_time": "12:00",
        "close_time": "22:00",
        "specialty": "Hojicha, Black Sesame, and coconut milk-based scoops",
    },
    {
        "name": "Polly Ann Ice Cream",
        "theme": "ice cream",
        "address": "3138 Noriega St, San Francisco, CA 94122",
        "neighborhood": "Outer Sunset",
        "hours": "Daily 11:30 AM - 9:00 PM",
        "open_time": "11:30",
        "close_time": "21:00",
        "specialty": "Spin the flavor wheel: Jasmine tea, Durian, and Lychee",
    },
    {
        "name": "Milkbomb Ice Cream",
        "theme": "ice cream",
        "address": "1717 17th St, San Francisco, CA 94103",
        "neighborhood": "Potrero Hill",
        "hours": "Daily 1:00 PM - 9:00 PM",
        "open_time": "13:00",
        "close_time": "21:00",
        "specialty": "Warm glazed donut ice cream sandwiches",
    },
    {
        "name": "Matcha Cafe Maiko",
        "theme": "ice cream",
        "address": "1581 Webster St #175, San Francisco, CA 94115",
        "neighborhood": "Japantown",
        "hours": "Daily 12:00 PM - 8:00 PM",
        "open_time": "12:00",
        "close_time": "20:00",
        "specialty": "Organic Uji matcha and roasted hojicha soft serve parfaits",
    },

    # Dim Sum & Dumplings (Chinatown / Richmond)
    {
        "name": "Good Mong Kok Bakery",
        "theme": "dim sum",
        "address": "1039 Stockton St, San Francisco, CA 94108",
        "neighborhood": "Chinatown",
        "hours": "Daily 7:00 AM - 5:00 PM",
        "open_time": "07:00",
        "close_time": "17:00",
        "specialty": "Steaming har gow, char siu bao, and egg tarts to-go",
    },
    {
        "name": "Hang Ah Tea Room",
        "theme": "dim sum",
        "address": "1 Pagoda Pl, San Francisco, CA 94108",
        "neighborhood": "Chinatown",
        "hours": "Wed-Mon 10:30 AM - 7:30 PM",
        "open_time": "10:30",
        "close_time": "19:30",
        "specialty": "America's oldest dim sum tea house; pork buns and siu mai",
    },
    {
        "name": "Dragon Beaux",
        "theme": "dim sum",
        "address": "5700 Geary Blvd, San Francisco, CA 94121",
        "neighborhood": "Richmond District",
        "hours": "Daily 10:30 AM - 3:00 PM",
        "open_time": "10:30",
        "close_time": "15:00",
        "specialty": "Five-color soup dumplings (xiao long bao) & crispy roast pork",
    },
    {
        "name": "Kingdom of Dumpling",
        "theme": "dim sum",
        "address": "1713 Taraval St, San Francisco, CA 94116",
        "neighborhood": "Parkside / Sunset",
        "hours": "Daily 11:00 AM - 8:30 PM",
        "open_time": "11:00",
        "close_time": "20:30",
        "specialty": "Handmade pan-fried pork & chive potstickers",
    },

    # Boba & Sweet Treats
    {
        "name": "Boba Guys",
        "theme": "boba tea",
        "address": "3491 19th St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Daily 11:30 AM - 8:00 PM",
        "open_time": "11:30",
        "close_time": "20:00",
        "specialty": "Strawberry Matcha Latte with house-made heirloom boba",
    },
    {
        "name": "Urban Ritual",
        "theme": "boba tea",
        "address": "488 Fell St, San Francisco, CA 94102",
        "neighborhood": "Hayes Valley",
        "hours": "Daily 12:00 PM - 7:00 PM",
        "open_time": "12:00",
        "close_time": "19:00",
        "specialty": "Crème Brûlée milk tea & roasted oolong with egg pudding",
    },

    # Sourdough, Seafood & Waterfront
    {
        "name": "Ferry Building Marketplace",
        "theme": "waterfront seafood",
        "address": "1 Ferry Building, San Francisco, CA 94111",
        "neighborhood": "Embarcadero",
        "hours": "Daily 7:00 AM - 7:00 PM",
        "open_time": "07:00",
        "close_time": "19:00",
        "specialty": "Hog Island Oysters, Acme Bread, and Mt Tam triple-cream cheese",
    },
    {
        "name": "Woodhouse Fish Co",
        "theme": "waterfront seafood",
        "address": "2073 Market St, San Francisco, CA 94114",
        "neighborhood": "Castro / Duboce",
        "hours": "Daily 11:30 AM - 9:00 PM",
        "open_time": "11:30",
        "close_time": "21:00",
        "specialty": "Split-top Maine lobster rolls and Dungeness crab chowder sourdough bowls",
    },

    # Craft Donuts & Coffee
    {
        "name": "Dynamo Donut & Bike",
        "theme": "donuts",
        "address": "2760 24th St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "hours": "Wed-Sun 8:00 AM - 3:00 PM",
        "open_time": "08:00",
        "close_time": "15:00",
        "specialty": "Bacon maple apple donut & Four Barrel espresso with garden bike patio",
    },
    {
        "name": "Twisted Donuts & Coffee",
        "theme": "donuts",
        "address": "1243 Noriega St, San Francisco, CA 94122",
        "neighborhood": "Sunset District",
        "hours": "Tue-Sun 7:00 AM - 3:00 PM",
        "open_time": "07:00",
        "close_time": "15:00",
        "specialty": "Artisanal cruffins, ube glazed donuts, and salted caramel twists",
    },

    # Banh Mi & Vietnamese Street Food
    {
        "name": "Saigon Sandwich",
        "theme": "banh mi",
        "address": "560 Larkin St, San Francisco, CA 94102",
        "neighborhood": "Little Saigon / Tenderloin",
        "hours": "Daily 7:00 AM - 4:30 PM",
        "open_time": "07:00",
        "close_time": "16:30",
        "specialty": "Crispy roast pork banh mi on warm French baguettes",
    },
    {
        "name": "Dinosaurs Vietnamese Sandwiches",
        "theme": "banh mi",
        "address": "2245 Market St, San Francisco, CA 94114",
        "neighborhood": "Castro",
        "hours": "Daily 10:30 AM - 6:00 PM",
        "open_time": "10:30",
        "close_time": "18:00",
        "specialty": "Crispy duck and shredded lemongrass chicken banh mi with pickled daikon",
    },
    # Additional Dim Sum Spots
    {
        "name": "City Discount Dim Sum",
        "theme": "dim sum",
        "address": "749 Jackson St, San Francisco, CA 94133",
        "neighborhood": "Chinatown",
        "hours": "Daily 8:00 AM - 5:30 PM",
        "open_time": "08:00",
        "close_time": "17:30",
        "specialty": "Fresh steaming siu mai, turnip cakes, and shrimp dumplings to-go",
    },
    {
        "name": "Yummy Bakery & Deli",
        "theme": "dim sum",
        "address": "607 Jackson St, San Francisco, CA 94133",
        "neighborhood": "Chinatown",
        "hours": "Daily 7:30 AM - 6:00 PM",
        "open_time": "07:30",
        "close_time": "18:00",
        "specialty": "Warm baked pork buns, flaky egg tarts, and cocktail buns",
    },
    {
        "name": "TC Pastry",
        "theme": "dim sum",
        "address": "1098 Irving St, San Francisco, CA 94122",
        "neighborhood": "Inner Sunset",
        "hours": "Daily 7:00 AM - 6:00 PM",
        "open_time": "07:00",
        "close_time": "18:00",
        "specialty": "Sunset favorite for potstickers, turnip cakes, and pork bao",
    },
    {
        "name": "Yuanbao Jiaozi",
        "theme": "dim sum",
        "address": "2110 Irving St, San Francisco, CA 94122",
        "neighborhood": "Sunset District",
        "hours": "Tue-Sun 11:00 AM - 8:30 PM",
        "open_time": "11:00",
        "close_time": "20:30",
        "specialty": "Handmade northern Chinese boiled dumplings with fish & chives",
    },
    {
        "name": "Dumpling Time",
        "theme": "dim sum",
        "address": "11 Division St, San Francisco, CA 94103",
        "neighborhood": "Design District / Mission",
        "hours": "Daily 11:30 AM - 8:30 PM",
        "open_time": "11:30",
        "close_time": "20:30",
        "specialty": "Tom Yum xiao long bao and giant King Dumpling with boba straw",
    },
    {
        "name": "Dumpling Home",
        "theme": "dim sum",
        "address": "298 Gough St, San Francisco, CA 94102",
        "neighborhood": "Hayes Valley",
        "hours": "Wed-Mon 11:30 AM - 8:00 PM",
        "open_time": "11:30",
        "close_time": "20:00",
        "specialty": "Michelin Bib Gourmand juicy pan-fried pork bao (sheng jian bao)",
    },
    # Additional Banh Mi Spots
    {
        "name": "Banh Mi Ba Le",
        "theme": "banh mi",
        "address": "1941 Irving St, San Francisco, CA 94122",
        "neighborhood": "Inner Sunset",
        "hours": "Wed-Mon 8:00 AM - 5:00 PM",
        "open_time": "08:00",
        "close_time": "17:00",
        "specialty": "Special combo pork cold cuts & pâté on house-baked baguettes",
    },
    {
        "name": "Sing Sing Sandwich Shop",
        "theme": "banh mi",
        "address": "309 Hyde St, San Francisco, CA 94109",
        "neighborhood": "Tenderloin",
        "hours": "Daily 7:00 AM - 3:30 PM",
        "open_time": "07:00",
        "close_time": "15:30",
        "specialty": "Classic crispy pork roll and Vietnamese iced coffee",
    },
    {
        "name": "DragonEats",
        "theme": "banh mi",
        "address": "2171 Chestnut St, San Francisco, CA 94123",
        "neighborhood": "Marina",
        "hours": "Daily 11:00 AM - 4:00 PM",
        "open_time": "11:00",
        "close_time": "16:00",
        "specialty": "Five-spice roast pork and garlic chicken banh mi by Marina Green",
    },
    {
        "name": "L&G Vietnamese Sandwich",
        "theme": "banh mi",
        "address": "602 Eddy St, San Francisco, CA 94109",
        "neighborhood": "Tenderloin",
        "hours": "Daily 8:00 AM - 4:00 PM",
        "open_time": "08:00",
        "close_time": "16:00",
        "specialty": "Pâté cha lua and roast beef banh mi with spicy jalapenos",
    },
    {
        "name": "Bun Mee",
        "theme": "banh mi",
        "address": "2015 Fillmore St, San Francisco, CA 94115",
        "neighborhood": "Pacific Heights",
        "hours": "Daily 11:00 AM - 8:00 PM",
        "open_time": "11:00",
        "close_time": "20:00",
        "specialty": "Belly bun banh mi with braised pork belly and sweet caramel citrus",
    },
    {
        "name": "Duc Huong Sandwiches",
        "theme": "banh mi",
        "address": "2116 Noriega St, San Francisco, CA 94122",
        "neighborhood": "Sunset District",
        "hours": "Daily 7:30 AM - 4:30 PM",
        "open_time": "07:30",
        "close_time": "16:30",
        "specialty": "Warm crispy French baguettes with barbecue lemongrass pork",
    },
    # Additional Boba Spots
    {
        "name": "Asha Tea House",
        "theme": "boba tea",
        "address": "17 Kearny St, San Francisco, CA 94108",
        "neighborhood": "Financial District",
        "hours": "Mon-Sat 11:00 AM - 6:00 PM",
        "open_time": "11:00",
        "close_time": "18:00",
        "specialty": "Single-origin artisan matcha and Hong Kong milk tea with boba",
    },
    {
        "name": "Plentea",
        "theme": "boba tea",
        "address": "341 Kearny St, San Francisco, CA 94108",
        "neighborhood": "Chinatown / FiDi",
        "hours": "Daily 11:30 AM - 7:00 PM",
        "open_time": "11:30",
        "close_time": "19:00",
        "specialty": "Fresh brewed tea served in collectible glass flasks with boba",
    },
    {
        "name": "TP TEA",
        "theme": "boba tea",
        "address": "1078 Gough St, San Francisco, CA 94109",
        "neighborhood": "Hayes Valley",
        "hours": "Daily 11:30 AM - 8:00 PM",
        "open_time": "11:30",
        "close_time": "20:00",
        "specialty": "Taiwanese tieguanyin tea latte with tender mini pearls",
    },
    {
        "name": "Wonderful Foods Co",
        "theme": "boba tea",
        "address": "2038 Irving St, San Francisco, CA 94122",
        "neighborhood": "Sunset District",
        "hours": "Daily 8:30 AM - 6:30 PM",
        "open_time": "08:30",
        "close_time": "18:30",
        "specialty": "Old-school roasted brown sugar milk tea and egg puffs",
    },
    {
        "name": "Milk Tea Lab",
        "theme": "boba tea",
        "address": "1714 Taraval St, San Francisco, CA 94116",
        "neighborhood": "Parkside",
        "hours": "Daily 12:00 PM - 9:00 PM",
        "open_time": "12:00",
        "close_time": "21:00",
        "specialty": "Taro storm and jasmine green milk tea with grass jelly and boba",
    },
    {
        "name": "Chicha San Chen",
        "theme": "boba tea",
        "address": "833 Market St, San Francisco, CA 94103",
        "neighborhood": "Downtown",
        "hours": "Daily 11:00 AM - 8:00 PM",
        "open_time": "11:00",
        "close_time": "20:00",
        "specialty": "Freshly patented Teapresso made-to-order dong ding oolong tea",
    },
    # Additional Craft Donuts & Coffee
    {
        "name": "Bob's Donut & Pastry",
        "theme": "donuts",
        "address": "1621 Polk St, San Francisco, CA 94109",
        "neighborhood": "Nob Hill",
        "hours": "24 Hours Daily",
        "open_time": "00:00",
        "close_time": "23:59",
        "specialty": "Famous 24/7 giant apple fritters and glazed buttermilk bars",
    },
    {
        "name": "Uncle Boy's",
        "theme": "donuts",
        "address": "245 Balboa St, San Francisco, CA 94118",
        "neighborhood": "Inner Richmond",
        "hours": "Daily 6:00 AM - 2:00 PM",
        "open_time": "06:00",
        "close_time": "14:00",
        "specialty": "Warm old fashioned glazed and chocolate cake donuts",
    },
    {
        "name": "Happy Donuts",
        "theme": "donuts",
        "address": "3801 24th St, San Francisco, CA 94114",
        "neighborhood": "Noe Valley",
        "hours": "Daily 6:00 AM - 4:00 PM",
        "open_time": "06:00",
        "close_time": "16:00",
        "specialty": "Neighborhood favorite maple bars, blueberry donuts, and coffee",
    },
    {
        "name": "Allstar Donuts",
        "theme": "donuts",
        "address": "3998 24th St, San Francisco, CA 94114",
        "neighborhood": "Noe Valley",
        "hours": "Daily 6:00 AM - 3:00 PM",
        "open_time": "06:00",
        "close_time": "15:00",
        "specialty": "Fluffy glazed twists, jelly donuts, and breakfast sandwiches",
    },
    {
        "name": "Johnny Doughnuts",
        "theme": "donuts",
        "address": "392 Gough St, San Francisco, CA 94102",
        "neighborhood": "Hayes Valley",
        "hours": "Daily 8:00 AM - 3:00 PM",
        "open_time": "08:00",
        "close_time": "15:00",
        "specialty": "Hand-crafted potato dough wildberry and chocolate glazed donuts",
    },
    {
        "name": "Rolling Out Cafe",
        "theme": "donuts",
        "address": "1722 Taraval St, San Francisco, CA 94116",
        "neighborhood": "Parkside",
        "hours": "Wed-Sun 8:00 AM - 3:00 PM",
        "open_time": "08:00",
        "close_time": "15:00",
        "specialty": "Crispy ube mochi donuts and matcha croissants",
    },
    # Additional Waterfront Sourdough & Seafood
    {
        "name": "Boudin Bakery Flagship",
        "theme": "waterfront seafood",
        "address": "160 Jefferson St, San Francisco, CA 94133",
        "neighborhood": "Fisherman's Wharf",
        "hours": "Daily 9:00 AM - 8:00 PM",
        "open_time": "09:00",
        "close_time": "20:00",
        "specialty": "Historic original mother dough sourdough clam chowder bowls",
    },
    {
        "name": "Scoma's Restaurant Fish Prep",
        "theme": "waterfront seafood",
        "address": "1965 Al Scoma Way, San Francisco, CA 94133",
        "neighborhood": "Fisherman's Wharf",
        "hours": "Daily 11:30 AM - 9:00 PM",
        "open_time": "11:30",
        "close_time": "21:00",
        "specialty": "Iconic pier-side cioppino and Dungeness crab cocktail",
    },
    {
        "name": "Hog Island Oyster Co",
        "theme": "waterfront seafood",
        "address": "1 Ferry Bldg Shop 11, San Francisco, CA 94111",
        "neighborhood": "Embarcadero",
        "hours": "Daily 11:00 AM - 7:00 PM",
        "open_time": "11:00",
        "close_time": "19:00",
        "specialty": "Sweetwater oysters, oyster po'boys, and clam chowder with views",
    },
    {
        "name": "The Codmother Fish and Chips",
        "theme": "waterfront seafood",
        "address": "496 Beach St, San Francisco, CA 94133",
        "neighborhood": "Fisherman's Wharf",
        "hours": "Daily 11:30 AM - 7:30 PM",
        "open_time": "11:30",
        "close_time": "19:30",
        "specialty": "Crispy English-style beer battered fish & chips and baja tacos",
    },
    {
        "name": "Acme Bread Company",
        "theme": "waterfront seafood",
        "address": "1 Ferry Building, San Francisco, CA 94111",
        "neighborhood": "Embarcadero",
        "hours": "Daily 7:00 AM - 6:00 PM",
        "open_time": "07:00",
        "close_time": "18:00",
        "specialty": "Crusty rustic sourdough baguettes, epi breads, and herb focaccia",
    },
    {
        "name": "Hook Fish Co",
        "theme": "waterfront seafood",
        "address": "4542 Irving St, San Francisco, CA 94122",
        "neighborhood": "Outer Sunset",
        "hours": "Daily 11:30 AM - 8:00 PM",
        "open_time": "11:30",
        "close_time": "20:00",
        "specialty": "Sustainably caught fish and chips, fish tacos, and poke bowls",
    },
]

# Curated scenic, bike-friendly San Francisco parks
SF_PARKS: list[dict[str, Any]] = [
    {
        "name": "Mission Dolores Park",
        "address": "Dolores St & 19th St, San Francisco, CA 94114",
        "neighborhood": "Mission District",
        "hours": "Daily 6:00 AM - 10:00 PM",
        "open_time": "06:00",
        "close_time": "22:00",
        "amenities": "Sunny sloping lawn, SF skyline view, picnic benches, bike racks, restrooms",
        "vibe": "The quintessential SF food picnic spot, perfect after picking up burritos, cookies, or ice cream.",
    },
    {
        "name": "Presidio Tunnel Tops & Main Parade Lawn",
        "address": "210 Lincoln Blvd, San Francisco, CA 94129",
        "neighborhood": "Presidio / Marina",
        "hours": "Daily 6:00 AM - 9:00 PM",
        "open_time": "06:00",
        "close_time": "21:00",
        "amenities": "Golden Gate bridge views, expansive lawns, picnic tables, fire pits, bike paths",
        "vibe": "Minutes from Fort Mason along flat bike paths with unmatched Golden Gate panorama.",
    },
    {
        "name": "Marina Green Park",
        "address": "Marina Blvd, San Francisco, CA 94123",
        "neighborhood": "Marina",
        "hours": "Daily 6:00 AM - 10:00 PM",
        "open_time": "06:00",
        "close_time": "22:00",
        "amenities": "Flat waterfront lawn, views of Alcatraz and Golden Gate, wide bike paths",
        "vibe": "Breezy seaside lawn right next to Fort Mason.",
    },
    {
        "name": "Alamo Square Park",
        "address": "Steiner St & Hayes St, San Francisco, CA 94117",
        "neighborhood": "Western Addition / Alamo Square",
        "hours": "Daily 5:00 AM - 12:00 AM",
        "open_time": "05:00",
        "close_time": "23:59",
        "amenities": "Iconic Painted Ladies view, hilltop lawns, dog-friendly, city panoramas",
        "vibe": "Classic SF postcard picnic hill, great stop when riding through Hayes Valley / Western Addition.",
    },
    {
        "name": "Duboce Park",
        "address": "Duboce Ave & Noe St, San Francisco, CA 94115",
        "neighborhood": "Duboce Triangle / Lower Haight",
        "hours": "Daily 6:00 AM - 10:00 PM",
        "open_time": "06:00",
        "close_time": "22:00",
        "amenities": "Sheltered green bowl, bike transit hub at The Wiggle, dog park",
        "vibe": "Relaxed community park connecting The Wiggle bike route between Mission and Panhandle.",
    },
    {
        "name": "Golden Gate Park Panhandle",
        "address": "Oak St & Fell St, San Francisco, CA 94117",
        "neighborhood": "Haight / Panhandle",
        "hours": "Daily 5:00 AM - 12:00 AM",
        "open_time": "05:00",
        "close_time": "23:59",
        "amenities": "Dedicated protected bicycle highway, mature eucalyptus and cypress trees, benches",
        "vibe": "Shady green corridor ideal for a quick picnic snack while cycling west.",
    },
    {
        "name": "Washington Square Park",
        "address": "Filbert St & Stockton St, San Francisco, CA 94133",
        "neighborhood": "North Beach",
        "hours": "Daily 6:00 AM - 10:00 PM",
        "open_time": "06:00",
        "close_time": "22:00",
        "amenities": "Saints Peter and Paul Church backdrop, sunny lawn, historic center of Little Italy",
        "vibe": "Best park for enjoying fresh North Beach pizza, pastries, or gelato.",
    },
    {
        "name": "Crissy Field East Beach",
        "address": "1199 E Beach, San Francisco, CA 94129",
        "neighborhood": "Marina / Presidio",
        "hours": "Daily 6:00 AM - 9:00 PM",
        "open_time": "06:00",
        "close_time": "21:00",
        "amenities": "Sandy beach picnic benches, Golden Gate Bridge views, flat promenade bike trail, restrooms",
        "vibe": "Stunning coastal picnic spot directly accessible via flat waterfront bike lanes.",
    },
    {
        "name": "Alta Plaza Park",
        "address": "Jackson St & Steiner St, San Francisco, CA 94115",
        "neighborhood": "Pacific Heights",
        "hours": "Daily 5:00 AM - 10:00 PM",
        "open_time": "05:00",
        "close_time": "22:00",
        "amenities": "Tiered terraces, grand staircases, 360-degree SF bay and city panoramas",
        "vibe": "Spectacular elevated views overlooking the Marina and Marin Headlands.",
    },
    {
        "name": "Lafayette Park",
        "address": "Gough St & Washington St, San Francisco, CA 94109",
        "neighborhood": "Pacific Heights",
        "hours": "Daily 5:00 AM - 10:00 PM",
        "open_time": "05:00",
        "close_time": "22:00",
        "amenities": "Hilltop green lawns, peaceful walking paths, dog park, city and bay vistas",
        "vibe": "Serene picnic spot with lush grass and panoramic outlooks.",
    },
    {
        "name": "Buena Vista Park",
        "address": "Buena Vista & Haight St, San Francisco, CA 94117",
        "neighborhood": "Haight-Ashbury / Buena Vista",
        "hours": "Daily 5:00 AM - 10:00 PM",
        "open_time": "05:00",
        "close_time": "22:00",
        "amenities": "Wooded hilltop trails, coastal oak groves, expansive viewpoints",
        "vibe": "San Francisco's oldest official park offering a tranquil forested retreat.",
    },
    {
        "name": "Bernal Heights Park",
        "address": "Bernal Heights Blvd, San Francisco, CA 94110",
        "neighborhood": "Bernal Heights / Mission",
        "hours": "Daily 5:00 AM - 10:00 PM",
        "open_time": "05:00",
        "close_time": "22:00",
        "amenities": "360-degree city panorama, hilltop breeze, open grassy knolls",
        "vibe": "Breathtaking south-city vistas right above the Mission food corridor.",
    },
    {
        "name": "Glen Canyon Park",
        "address": "Elk St & Chenery St, San Francisco, CA 94127",
        "neighborhood": "Glen Park",
        "hours": "Daily 6:00 AM - 10:00 PM",
        "open_time": "06:00",
        "close_time": "22:00",
        "amenities": "Canyon picnic meadows, rock formations, rec center, shaded seating",
        "vibe": "Dramatic natural canyon escape with ample lawn picnic areas.",
    },
]


def suggest_food_themes(query_context: str = "", count: int | None = None, shuffle: bool = False) -> dict[str, Any]:
    """Suggests diverse, creative, and seasonal food themes for casual San Francisco bike rides.

    Args:
        query_context: Optional context such as specific neighborhood, season, or holiday.
        count: Number of themes to return (default None returns all available themes).
        shuffle: Whether to rotate/randomize themes for variety (default False).

    Returns:
        A dictionary containing recommended themes with descriptions and highlight spots.
    """
    all_themes = [
        {
            "id": "dim_sum_dumpling",
            "title": "Chinatown Alleyways & Dumpling Roll",
            "type": "creative_specialty",
            "summary": "Cruise along car-free Chinatown alleyways and the Embarcadero sampling piping-hot har gow, char siu bao, and egg tarts fresh out of bamboo steamers.",
            "recommended_park": "Washington Square Park or Marina Green",
            "best_ride_window": "9:30 AM - 1:30 PM (bakeries and dim sum tea houses at peak freshness)",
        },
        {
            "id": "banh_mi_boba",
            "title": "Crispy Banh Mi & Craft Boba Trail",
            "type": "creative_specialty",
            "summary": "Taste test SF's crunchiest baguettes with roasted pork belly and lemongrass tofu, paired with hand-shaken matcha boba in Hayes Valley and Little Saigon.",
            "recommended_park": "Duboce Park or Alamo Square",
            "best_ride_window": "11:00 AM - 2:30 PM",
        },
        {
            "id": "craft_donuts_coffee",
            "title": "Golden Gate Glazed & Third-Wave Roast Ride",
            "type": "creative_specialty",
            "summary": "A high-energy morning ride hitting bacon-apple donuts, artisanal cruffins, and single-origin pour-overs through sunny neighborhood corridors.",
            "recommended_park": "Mission Dolores Park or Panhandle",
            "best_ride_window": "8:30 AM - 12:00 PM",
        },
        {
            "id": "chowder_waterfront",
            "title": "San Francisco Bay Sourdough & Chowder Roll",
            "type": "waterfront_event",
            "summary": "Breeze along the flat, car-free waterfront from Fort Mason to the Ferry Building, feasting on hot clam chowder sourdough bread bowls and fresh oysters.",
            "recommended_park": "Presidio Tunnel Tops or Marina Green",
            "best_ride_window": "11:00 AM - 3:00 PM",
        },
        {
            "id": "chocolate_chip_cookie",
            "title": "The Ultimate Chocolate Chip Cookie Crawl",
            "type": "food_specialty",
            "summary": "Taste test SF's most celebrated chocolate chip cookies, from Arsicault and Jane the Bakery to Tartine's salted rye masterpiece.",
            "recommended_park": "Duboce Park or Alamo Square",
            "best_ride_window": "9:00 AM - 1:00 PM (early bakeries have freshest batches)",
        },
        {
            "id": "burrito",
            "title": "Mission District Golden Burrito Trail",
            "type": "food_specialty",
            "summary": "Cruise along bike-friendly Valencia and Harrison streets to legendary taquerias (La Taqueria, Farolito, Cancún) for the world-famous Mission burrito.",
            "recommended_park": "Mission Dolores Park",
            "best_ride_window": "11:00 AM - 3:00 PM (taquerias fully open by 10-11 AM)",
        },
        {
            "id": "ice_cream",
            "title": "Artisanal Scoop & Sun Tour",
            "type": "food_specialty",
            "summary": "A delightful afternoon ride sampling creative small-batch flavors from Bi-Rite Creamery, Humphry Slocombe, and Smitten.",
            "recommended_park": "Mission Dolores Park or Marina Green",
            "best_ride_window": "12:00 PM - 3:30 PM (scoop shops open by noon)",
        },
        {
            "id": "pizza",
            "title": "North Beach to Mission Slice Quest",
            "type": "food_specialty",
            "summary": "Compare world-champion wood-fired slices, Sicilian squares, and sourdough pies from North Beach through NoPa down to the Mission.",
            "recommended_park": "Washington Square Park or Alamo Square",
            "best_ride_window": "11:30 AM - 3:30 PM (pizzerias fire up ovens by 11:30 AM)",
        },
        {
            "id": "neighborhood_mission_valencia",
            "title": "Valencia Bicycle Corridor & Latin Flavors",
            "type": "neighborhood",
            "summary": "Glide along San Francisco's most bike-friendly corridor lined with bakeries, craft coffee, empanadas, and taquerias.",
            "recommended_park": "Mission Dolores Park",
            "best_ride_window": "10:00 AM - 2:00 PM",
        },
        {
            "id": "weekend_waterfront_breeze",
            "title": "Golden Gate & Waterfront Picnic Ride",
            "type": "event_or_weekend",
            "summary": "Casual seaside spin from Fort Mason through the Marina and Presidio, picking up sourdough, pastries, and treats to picnic at Tunnel Tops.",
            "recommended_park": "Presidio Tunnel Tops or Marina Green",
            "best_ride_window": "9:30 AM - 1:30 PM",
        },
    ]

    selected_themes = list(all_themes)
    if shuffle:
        import random
        random.shuffle(selected_themes)

    if count and count < len(selected_themes):
        selected_themes = selected_themes[:count]

    return {
        "status": "success",
        "themes": selected_themes,
        "note": "A rich blend of original and classic food themes, all designed for bike-friendly routes and park picnics in San Francisco.",
    }


def find_food_spots(
    theme: str,
    neighborhood: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Finds candidate food spots matching a theme and optional neighborhood filter.

    Args:
        theme: Food theme (e.g., 'chocolate chip cookie', 'burrito', 'pizza', 'ice cream', 'dim sum', 'donuts', 'banh mi').
        neighborhood: Optional SF neighborhood filter (e.g., 'Mission', 'North Beach', 'Marina').
        limit: Max number of candidate spots to return (default 10).

    Returns:
        A dictionary with candidate spots and their hours, address, and specialty.
    """
    clean_theme = theme.lower().strip()
    if "cookie" in clean_theme or "pastr" in clean_theme or "bakery" in clean_theme:
        target_theme = "chocolate chip cookie"
    elif "burrito" in clean_theme or "taco" in clean_theme or "mexican" in clean_theme or "latin" in clean_theme:
        target_theme = "burrito"
    elif "pizza" in clean_theme or "slice" in clean_theme or "pie" in clean_theme:
        target_theme = "pizza"
    elif "ice cream" in clean_theme or "gelato" in clean_theme or "scoop" in clean_theme:
        target_theme = "ice cream"
    elif "dim sum" in clean_theme or "dumpling" in clean_theme or "chinatown" in clean_theme or "bao" in clean_theme:
        target_theme = "dim sum"
    elif "donut" in clean_theme or "doughnut" in clean_theme or "glaze" in clean_theme or "roast" in clean_theme:
        target_theme = "donuts"
    elif "banh mi" in clean_theme or "vietnamese" in clean_theme or "baguette" in clean_theme:
        target_theme = "banh mi"
    elif "boba" in clean_theme or "tea" in clean_theme:
        target_theme = "boba tea"
    elif "chowder" in clean_theme or "seafood" in clean_theme or "sourdough" in clean_theme or "waterfront" in clean_theme or "oyster" in clean_theme:
        target_theme = "waterfront seafood"
    else:
        target_theme = clean_theme

    # 1. Primary matching on theme category
    primary_matches = []
    secondary_matches = []
    for spot in SF_FOOD_SPOTS:
        if spot["theme"].lower() == target_theme or target_theme in spot["theme"].lower():
            primary_matches.append(spot)
        elif any(kw in spot["name"].lower() or kw in spot["specialty"].lower() for kw in clean_theme.split() if len(kw) > 3):
            secondary_matches.append(spot)

    matching_spots = primary_matches + [s for s in secondary_matches if s not in primary_matches]

    if neighborhood:
        filtered = [s for s in matching_spots if neighborhood.lower() in s["neighborhood"].lower() or neighborhood.lower() in s["address"].lower()]
        if filtered:
            matching_spots = filtered

    # If still empty for custom query, return diverse SF culinary highlights
    if not matching_spots:
        matching_spots = list(SF_FOOD_SPOTS)

    return {
        "theme": theme,
        "total_found": len(matching_spots),
        "candidate_spots": matching_spots[:limit],
    }


def lookup_location_info(location_query: str) -> dict[str, Any]:
    """Looks up information for a specific San Francisco food venue or park provided by the user.

    If the location is in the curated database, returns verified hours, address, and specialty.
    If it is a custom location or not found, provides an estimated schedule profile.

    Args:
        location_query: Name or address of the spot (e.g. 'Arsicault Bakery', 'Tartine', 'Bi-Rite', 'Golden Gate Park').

    Returns:
        Dictionary with venue name, address, hours, open_time, close_time, type, and specialty.
    """
    query_clean = location_query.lower().strip()

    # Check food spots database
    for spot in SF_FOOD_SPOTS:
        if query_clean in spot["name"].lower() or spot["name"].lower() in query_clean:
            coords = _get_location_coords(spot["name"] + " " + spot["address"])
            return {
                "found": True,
                "name": spot["name"],
                "address": spot["address"],
                "neighborhood": spot.get("neighborhood", "San Francisco"),
                "hours": spot["hours"],
                "open_time": spot["open_time"],
                "close_time": spot["close_time"],
                "specialty": spot.get("specialty", ""),
                "type": "food",
                "lat": coords[0],
                "lng": coords[1],
            }

    # Check parks database
    for park in SF_PARKS:
        if query_clean in park["name"].lower() or park["name"].lower() in query_clean:
            coords = _get_location_coords(park["name"] + " " + park["address"])
            return {
                "found": True,
                "name": park["name"],
                "address": park["address"],
                "neighborhood": park.get("neighborhood", "San Francisco"),
                "hours": park["hours"],
                "open_time": park["open_time"],
                "close_time": park["close_time"],
                "specialty": park.get("vibe", "Scenic park picnic spot"),
                "type": "park",
                "lat": coords[0],
                "lng": coords[1],
            }

    # If not in curated list, provide default reasonable hours for SF spots
    is_park = "park" in query_clean or "green" in query_clean or "square" in query_clean or "plaza" in query_clean
    coords = _get_location_coords(location_query)
    return {
        "found": False,
        "name": location_query.strip(),
        "address": f"{location_query.strip()}, San Francisco, CA",
        "neighborhood": "San Francisco",
        "hours": "Daily 6:00 AM - 10:00 PM" if is_park else "Daily 9:00 AM - 6:00 PM (verify online)",
        "open_time": "06:00" if is_park else "09:00",
        "close_time": "22:00" if is_park else "18:00",
        "specialty": "Scenic outdoor stop" if is_park else "Custom food spot requested by user",
        "type": "park" if is_park else "food",
        "lat": coords[0],
        "lng": coords[1],
    }


def find_nearby_parks(
    neighborhood: str | None = None,
    near_location: str | None = None,
) -> dict[str, Any]:
    """Finds scenic, bike-friendly parks in San Francisco to stop and eat.

    Args:
        neighborhood: Optional SF neighborhood name.
        near_location: Optional landmark or location name to find nearest park.

    Returns:
        List of matching SF parks with amenities and picnic vibes.
    """
    if neighborhood:
        filtered = [
            p for p in SF_PARKS
            if neighborhood.lower() in p["neighborhood"].lower() or neighborhood.lower() in p["name"].lower()
        ]
        if filtered:
            return {"parks": filtered}

    if near_location:
        near_loc_lower = near_location.lower()
        if "fort mason" in near_loc_lower or "marina" in near_loc_lower:
            return {"parks": [p for p in SF_PARKS if p["name"] in ["Marina Green Park", "Presidio Tunnel Tops & Main Parade Lawn"]]}
        if "mission" in near_loc_lower or "valencia" in near_loc_lower:
            return {"parks": [p for p in SF_PARKS if p["name"] == "Mission Dolores Park"]}
        if "north beach" in near_loc_lower or "chinatown" in near_loc_lower:
            return {"parks": [p for p in SF_PARKS if p["name"] == "Washington Square Park"]}
        if "nopa" in near_loc_lower or "fillmore" in near_loc_lower or "divisadero" in near_loc_lower:
            return {"parks": [p for p in SF_PARKS if p["name"] in ["Alamo Square Park", "Duboce Park"]]}

    return {"parks": SF_PARKS}


def _get_location_coords(location_str: str) -> tuple[float, float]:
    """Helper to lookup or approximate coordinates for a location string."""
    loc_lower = location_str.lower().strip()
    for key, coords in LOCATION_COORDINATES.items():
        if key in loc_lower or loc_lower in key:
            return coords
    # Default fallback: SF city center (Civic Center / Market St)
    return (37.7749, -122.4194)


def _haversine_distance_miles(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Calculates great circle distance in miles between two (lat, lon) coordinates."""
    lat1, lon1 = p1
    lat2, lon2 = p2
    r = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def optimize_stops_order(start_location: str, stops: list[dict[str, Any]], return_to_start: bool = True) -> list[dict[str, Any]]:
    """Orders stops using a nearest-neighbor TSP heuristic to prevent zigzagging and backtracking.

    Args:
        start_location: Origin address or landmark name.
        stops: List of candidate stop dictionaries.
        return_to_start: Whether the route eventually loops back to the start location.

    Returns:
        Reordered list of stops minimizing cycling detour and backtracking.
    """
    if len(stops) <= 1:
        return stops

    start_coords = _get_location_coords(start_location)
    remaining = list(stops)
    ordered_stops: list[dict[str, Any]] = []
    current_coords = start_coords

    while remaining:
        # Pick the nearest stop to current location
        best_idx = 0
        best_dist = float("inf")
        for idx, stop in enumerate(remaining):
            name_or_addr = stop.get("name", "") + " " + stop.get("address", "")
            stop_coords = _get_location_coords(name_or_addr)
            dist = _haversine_distance_miles(current_coords, stop_coords)
            if dist < best_dist:
                best_dist = dist
                best_idx = idx

        chosen_stop = remaining.pop(best_idx)
        ordered_stops.append(chosen_stop)
        name_or_addr = chosen_stop.get("name", "") + " " + chosen_stop.get("address", "")
        current_coords = _get_location_coords(name_or_addr)

    return ordered_stops


def _parse_time_to_minutes(time_str: str) -> int:
    """Parses time strings like '08:30', '8:00 AM', '11:15 AM', '2:00 PM' to minutes since midnight."""
    cleaned = time_str.strip().upper()
    is_pm = "PM" in cleaned
    is_am = "AM" in cleaned
    cleaned = cleaned.replace("AM", "").replace("PM", "").strip()

    parts = cleaned.split(":")
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0

    if is_pm and hours < 12:
        hours += 12
    elif is_am and hours == 12:
        hours = 0

    return hours * 60 + minutes


def _format_minutes_to_time(total_minutes: int) -> str:
    """Formats minutes since midnight into 12-hour AM/PM string, e.g. 630 -> '10:30 AM'."""
    norm_mins = total_minutes % (24 * 60)
    hours = norm_mins // 60
    mins = norm_mins % 60
    period = "AM" if hours < 12 else "PM"
    display_hour = hours % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour}:{mins:02d} {period}"


def build_google_maps_bike_url(origin: str, stops: list[str], destination: str | None = None) -> str:
    """Generates a shareable Google Maps bicycling directions URL.

    Args:
        origin: Start location string (e.g., 'Fort Mason, San Francisco, CA').
        stops: List of intermediate stops and park addresses.
        destination: Optional final stop address. If omitted, defaults back to origin (loop route).

    Returns:
        Google Maps directions URL with travelmode=bicycling.
    """
    base_url = "https://www.google.com/maps/dir/?api=1"
    dest = destination if destination else origin

    params = {
        "origin": origin,
        "destination": dest,
        "travelmode": "bicycling",
    }
    if stops:
        params["waypoints"] = "|".join(stops)

    return f"{base_url}&{urllib.parse.urlencode(params)}"


def calculate_bike_route_schedule(
    start_location: str = "Fort Mason, San Francisco, CA",
    start_time: str = "10:00 AM",
    stops: list[dict[str, Any]] | None = None,
    stop_duration_minutes: int = 20,
    average_transit_minutes: int = 15,
    return_to_start: bool = True,
    end_location: str | None = None,
    optimize_order: bool = True,
) -> dict[str, Any]:
    """Calculates an optimized timetable and route plan for casual cycling with food & park stops.

    Automatically eliminates backtracking by ordering stops geographically and loops back or finishes at end_location.

    Args:
        start_location: Starting point (defaults to 'Fort Mason, San Francisco, CA').
        start_time: Departure time (e.g. '10:00 AM').
        stops: List of stop dicts with name, address, hours, open_time, close_time, and type ('food' or 'park').
        stop_duration_minutes: Time spent at each stop (typically 15-30 minutes).
        average_transit_minutes: Casual bike travel time between stops (typically 12-20 minutes).
        return_to_start: Whether the route ends back at the starting location (default True).
        end_location: Optional explicit end location if different from start_location.
        optimize_order: Whether to automatically sort stops to prevent backtracking (default True).

    Returns:
        Detailed itinerary with timestamps, open hours verification, total time, and map link.
    """
    if not stops:
        stops = []

    # If explicit end_location provided and distinct, don't return to start
    final_destination = end_location if (end_location and end_location.strip()) else (start_location if return_to_start else None)

    # Optimize route ordering to eliminate backtracking if requested
    if optimize_order and len(stops) > 1:
        stops = optimize_stops_order(start_location, stops, return_to_start=(final_destination == start_location))

    current_minutes = _parse_time_to_minutes(start_time)
    itinerary = []

    # Start location record
    start_coords = _get_location_coords(start_location)
    itinerary.append({
        "stop_number": 0,
        "type": "start",
        "name": start_location,
        "address": start_location,
        "departure_time": _format_minutes_to_time(current_minutes),
        "notes": "Starting point for the ride",
        "lat": start_coords[0],
        "lng": start_coords[1],
    })

    stop_addresses = []

    for i, stop in enumerate(stops, start=1):
        current_minutes += average_transit_minutes
        arrival_str = _format_minutes_to_time(current_minutes)

        open_time = stop.get("open_time")
        close_time = stop.get("close_time")
        is_open = True
        hours_status = "Open"

        if open_time and close_time:
            open_min = _parse_time_to_minutes(open_time)
            close_min = _parse_time_to_minutes(close_time)
            if current_minutes < open_min:
                is_open = False
                hours_status = f"Closed upon arrival (Opens at {_format_minutes_to_time(open_min)})"
            elif current_minutes > close_min:
                is_open = False
                hours_status = f"Closed upon arrival (Closed at {_format_minutes_to_time(close_min)})"
            else:
                hours_status = f"Open (Operating hours: {stop.get('hours', 'Regular hours')})"
        else:
            hours_status = f"Open (Operating hours: {stop.get('hours', 'Open to public')})"

        stay_duration = stop.get("duration_minutes", stop_duration_minutes)
        current_minutes += stay_duration
        departure_str = _format_minutes_to_time(current_minutes)

        address = stop.get("address", stop.get("name"))
        stop_addresses.append(address)
        coords = _get_location_coords(stop.get("name", "") + " " + address)

        itinerary.append({
            "stop_number": i,
            "type": stop.get("type", "food"),
            "name": stop.get("name"),
            "address": address,
            "specialty": stop.get("specialty", ""),
            "neighborhood": stop.get("neighborhood", ""),
            "store_hours": stop.get("hours", "Check venue for hours"),
            "arrival_time": arrival_str,
            "departure_time": departure_str,
            "duration_at_stop_minutes": stay_duration,
            "is_open_at_arrival": is_open,
            "open_status": hours_status,
            "lat": coords[0],
            "lng": coords[1],
        })

    # Add final destination stop (either loop back to start or distinct end location)
    if final_destination and stops:
        current_minutes += average_transit_minutes
        final_stop_num = len(stops) + 1
        end_coords = _get_location_coords(final_destination)
        is_loop = (final_destination.strip().lower() == start_location.strip().lower())
        itinerary.append({
            "stop_number": final_stop_num,
            "type": "end",
            "name": f"{final_destination} (Loop Finish)" if is_loop else f"{final_destination} (Trip Finish)",
            "address": final_destination,
            "arrival_time": _format_minutes_to_time(current_minutes),
            "store_hours": "N/A - Finish line",
            "is_open_at_arrival": True,
            "open_status": "Completed ride",
            "notes": "Completed bike route at destination",
            "lat": end_coords[0],
            "lng": end_coords[1],
        })

    total_duration_minutes = current_minutes - _parse_time_to_minutes(start_time)
    total_hours = round(total_duration_minutes / 60, 1)

    google_maps_url = build_google_maps_bike_url(
        origin=start_location,
        stops=stop_addresses,
        destination=final_destination if final_destination else (stop_addresses[-1] if stop_addresses else start_location),
    )

    return {
        "start_location": start_location,
        "end_location": final_destination,
        "destination": final_destination if final_destination else (stop_addresses[-1] if stop_addresses else start_location),
        "return_to_start": (final_destination == start_location),
        "route_optimized": optimize_order,
        "start_time": start_time,
        "end_time": _format_minutes_to_time(current_minutes),
        "total_duration_minutes": total_duration_minutes,
        "total_duration_formatted": f"{total_hours} hours ({total_duration_minutes} minutes)",
        "number_of_stops": len(stops),
        "itinerary": itinerary,
        "google_maps_route_url": google_maps_url,
    }

