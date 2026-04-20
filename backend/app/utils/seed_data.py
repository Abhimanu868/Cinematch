"""Seed database with 500+ movies and 5000+ synthetic ratings."""
import random
import logging
import time
import asyncio
from sqlalchemy.orm import Session
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.services.auth_service import hash_password
from app.services.tmdb_service import fetch_tmdb_poster_sync, TMDB_API_KEY

logger = logging.getLogger(__name__)

MOVIES_DATA = [
    ("The Shawshank Redemption",1994,"Drama","Two imprisoned men bond over years, finding solace and eventual redemption through acts of common decency.","Frank Darabont","Tim Robbins, Morgan Freeman","prison, hope, freedom, friendship",142,9.3,2500000,80.0),
    ("The Godfather",1972,"Crime, Drama","The aging patriarch of an organized crime dynasty transfers control to his reluctant son.","Francis Ford Coppola","Marlon Brando, Al Pacino","mafia, family, power, crime",175,9.2,1800000,75.0),
    ("The Dark Knight",2008,"Action, Crime, Drama","Batman raises the stakes in his war on crime with the help of Lt. Jim Gordon and District Attorney Harvey Dent.","Christopher Nolan","Christian Bale, Heath Ledger","batman, joker, gotham, superhero",152,9.0,2500000,90.0),
    ("Pulp Fiction",1994,"Crime, Drama","The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.","Quentin Tarantino","John Travolta, Uma Thurman","crime, nonlinear, violence, dark comedy",154,8.9,2000000,85.0),
    ("Forrest Gump",1994,"Drama, Romance","The presidencies of Kennedy and Johnson, the Vietnam War and other events unfold from the perspective of an Alabama man.","Robert Zemeckis","Tom Hanks, Robin Wright","life, history, running, love",142,8.8,2000000,82.0),
    ("Inception",2010,"Action, Sci-Fi, Thriller","A thief who steals corporate secrets through dream-sharing technology is given the task of planting an idea.","Christopher Nolan","Leonardo DiCaprio, Joseph Gordon-Levitt","dreams, heist, mind, reality",148,8.8,2200000,88.0),
    ("Fight Club",1999,"Drama","An insomniac office worker and a soap salesman build a global organization to help vent male aggression.","David Fincher","Brad Pitt, Edward Norton","identity, anarchy, consumerism, violence",139,8.8,2000000,79.0),
    ("The Matrix",1999,"Action, Sci-Fi","A computer hacker learns about the true nature of his reality and his role in the war against its controllers.","Lana Wachowski","Keanu Reeves, Laurence Fishburne","simulation, AI, reality, martial arts",136,8.7,1900000,83.0),
    ("Goodfellas",1990,"Biography, Crime, Drama","The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen and his partners.","Martin Scorsese","Robert De Niro, Ray Liotta","mafia, crime, rise and fall, loyalty",146,8.7,1100000,73.0),
    ("The Lord of the Rings: The Return of the King",2003,"Adventure, Drama, Fantasy","Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam.","Peter Jackson","Elijah Wood, Viggo Mortensen","epic, quest, fantasy, battle",201,9.0,1800000,85.0),
    ("Interstellar",2014,"Adventure, Drama, Sci-Fi","A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.","Christopher Nolan","Matthew McConaughey, Anne Hathaway","space, time, love, survival",169,8.6,1700000,86.0),
    ("The Silence of the Lambs",1991,"Crime, Drama, Thriller","A young FBI cadet must receive the help of an incarcerated and manipulative cannibal killer.","Jonathan Demme","Jodie Foster, Anthony Hopkins","serial killer, FBI, psychology, thriller",118,8.6,1400000,72.0),
    ("Schindler's List",1993,"Biography, Drama, History","In German-occupied Poland, Oskar Schindler gradually becomes concerned for his Jewish workforce.","Steven Spielberg","Liam Neeson, Ralph Fiennes","holocaust, war, humanity, rescue",195,9.0,1300000,70.0),
    ("The Green Mile",1999,"Crime, Drama, Fantasy","The lives of guards on Death Row are affected by one of their charges: a gentle giant with a mysterious gift.","Frank Darabont","Tom Hanks, Michael Clarke Duncan","prison, miracle, death, justice",189,8.6,1300000,71.0),
    ("Se7en",1995,"Crime, Mystery, Thriller","Two detectives hunt a serial killer who uses the seven deadly sins as his motifs.","David Fincher","Brad Pitt, Morgan Freeman","serial killer, detective, sins, dark",127,8.6,1600000,76.0),
    ("Gladiator",2000,"Action, Adventure, Drama","A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family.","Ridley Scott","Russell Crowe, Joaquin Phoenix","rome, revenge, gladiator, honor",155,8.5,1500000,78.0),
    ("The Departed",2006,"Crime, Drama, Thriller","An undercover cop and a mole in the police attempt to identify each other while infiltrating an Irish gang.","Martin Scorsese","Leonardo DiCaprio, Matt Damon","undercover, crime, identity, betrayal",151,8.5,1300000,77.0),
    ("Whiplash",2014,"Drama, Music","A promising young drummer enrolls at a cut-throat music conservatory where his dreams are mentored by an instructor.","Damien Chazelle","Miles Teller, J.K. Simmons","music, obsession, perfection, mentor",106,8.5,900000,80.0),
    ("The Prestige",2006,"Drama, Mystery, Sci-Fi","Two stage magicians engage in competitive one-upmanship in an attempt to create the ultimate stage illusion.","Christopher Nolan","Christian Bale, Hugh Jackman","magic, rivalry, obsession, sacrifice",130,8.5,1300000,79.0),
    ("Django Unchained",2012,"Drama, Western","With the help of a German bounty hunter, a freed slave sets out to rescue his wife from a brutal plantation owner.","Quentin Tarantino","Jamie Foxx, Christoph Waltz","slavery, bounty hunter, revenge, western",165,8.4,1500000,81.0),
    ("Parasite",2019,"Comedy, Drama, Thriller","Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.","Bong Joon-ho","Song Kang-ho, Lee Sun-kyun","class, inequality, family, deception",132,8.5,800000,82.0),
    ("Joker",2019,"Crime, Drama, Thriller","A mentally troubled comedian in Gotham City embarks on a downward spiral of revolution and bloody crime.","Todd Phillips","Joaquin Phoenix, Robert De Niro","mental illness, society, chaos, origin",122,8.4,1100000,83.0),
    ("Avengers: Endgame",2019,"Action, Adventure, Drama","After devastating events, the Avengers assemble once more to reverse Thanos' actions and restore balance.","Anthony Russo","Robert Downey Jr., Chris Evans","superhero, time travel, sacrifice, teamwork",181,8.4,2500000,95.0),
    ("Spider-Man: Into the Spider-Verse",2018,"Animation, Action, Adventure","Teen Miles Morales becomes the Spider-Man of his reality and crosses paths with counterparts from other dimensions.","Bob Persichetti","Shameik Moore, Jake Johnson","spider-man, multiverse, animation, hero",117,8.4,600000,78.0),
    ("The Lion King",1994,"Animation, Adventure, Drama","Lion prince Simba flees his kingdom after the murder of his father, only to learn the true meaning of responsibility.","Roger Allers","Matthew Broderick, Jeremy Irons","lion, africa, coming of age, family",88,8.5,1000000,76.0),
    ("Back to the Future",1985,"Adventure, Comedy, Sci-Fi","Marty McFly is accidentally sent 30 years into the past in a time-traveling DeLorean invented by his friend.","Robert Zemeckis","Michael J. Fox, Christopher Lloyd","time travel, adventure, comedy, 1950s",116,8.5,1100000,77.0),
    ("Alien",1979,"Horror, Sci-Fi","The crew of a commercial spacecraft encounters a deadly lifeform after investigating an unknown transmission.","Ridley Scott","Sigourney Weaver, Tom Skerritt","alien, space, horror, survival",117,8.5,900000,70.0),
    ("WALL-E",2008,"Animation, Adventure, Family","In the distant future, a small waste-collecting robot inadvertently embarks on a space journey that will decide the fate of mankind.","Andrew Stanton","Ben Burtt, Elissa Knight","robot, love, environment, space",98,8.4,1000000,75.0),
    ("The Truman Show",1998,"Comedy, Drama","An insurance salesman discovers his whole life is actually a reality TV show.","Peter Weir","Jim Carrey, Ed Harris","reality TV, freedom, surveillance, identity",103,8.2,1000000,74.0),
    ("Spirited Away",2001,"Animation, Adventure, Family","During her family's move, a young girl enters a world ruled by gods, witches, and spirits.","Hayao Miyazaki","Rumi Hiiragi, Miyu Irino","spirit world, courage, japanese, coming of age",125,8.6,800000,73.0),
    ("Coco",2017,"Animation, Adventure, Family","A boy who dreams of being a musician enters the Land of the Dead to find his great-great-grandfather.","Lee Unkrich","Anthony Gonzalez, Gael García Bernal","music, family, death, mexican culture",105,8.4,600000,76.0),
    ("Mad Max: Fury Road",2015,"Action, Adventure, Sci-Fi","In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler with the help of a drifter.","George Miller","Tom Hardy, Charlize Theron","post-apocalyptic, chase, rebellion, survival",120,8.1,1000000,84.0),
    ("Blade Runner 2049",2017,"Drama, Mystery, Sci-Fi","A young blade runner's discovery of a long-buried secret leads him to track down former blade runner Rick Deckard.","Denis Villeneuve","Ryan Gosling, Harrison Ford","AI, identity, dystopia, future",164,8.0,600000,77.0),
    ("Get Out",2017,"Horror, Mystery, Thriller","A young African-American visits his white girlfriend's parents for the weekend, where his simmering uneasiness about their reception intensifies.","Jordan Peele","Daniel Kaluuya, Allison Williams","racism, horror, mind control, social thriller",104,7.7,700000,78.0),
    ("La La Land",2016,"Comedy, Drama, Music","While navigating their careers in Los Angeles, a pianist and an actress fall in love.","Damien Chazelle","Ryan Gosling, Emma Stone","music, love, dreams, Hollywood",128,8.0,700000,79.0),
    ("The Grand Budapest Hotel",2014,"Adventure, Comedy, Crime","A writer encounters the owner of an aging luxury hotel, who tells of his early years serving as a lobby boy.","Wes Anderson","Ralph Fiennes, Tony Revolori","hotel, adventure, comedy, Europe",99,8.1,600000,72.0),
    ("Arrival",2016,"Drama, Mystery, Sci-Fi","A linguist works with the military to communicate with alien lifeforms after twelve mysterious spacecraft appear.","Denis Villeneuve","Amy Adams, Jeremy Renner","aliens, language, time, communication",116,7.9,600000,76.0),
    ("Jaws",1975,"Adventure, Thriller","A giant great white shark arrives on the shores of a small island and wreaks havoc.","Steven Spielberg","Roy Scheider, Robert Shaw","shark, ocean, fear, summer",124,8.1,1000000,68.0),
    ("Jurassic Park",1993,"Action, Adventure, Sci-Fi","A theme park with cloned dinosaurs turns deadly when the creatures escape their enclosures.","Steven Spielberg","Sam Neill, Laura Dern","dinosaurs, theme park, science, danger",127,8.2,1000000,75.0),
    ("Titanic",1997,"Drama, Romance","A seventeen-year-old aristocrat falls in love with an artist aboard the ill-fated R.M.S. Titanic.","James Cameron","Leonardo DiCaprio, Kate Winslet","ship, romance, disaster, class",194,7.9,1200000,78.0),
    ("The Social Network",2010,"Biography, Drama","The founding of Facebook and the ensuing lawsuits.","David Fincher","Jesse Eisenberg, Andrew Garfield","facebook, startup, ambition, betrayal",120,7.8,700000,76.0),
    ("No Country for Old Men",2007,"Crime, Drama, Thriller","Violence and mayhem ensue after a hunter stumbles upon a drug deal gone wrong.","Coen Brothers","Javier Bardem, Josh Brolin","crime, fate, violence, texas",122,8.2,900000,74.0),
    ("There Will Be Blood",2007,"Drama","A story of family, religion, hatred, oil and madness set in early twentieth century California.","Paul Thomas Anderson","Daniel Day-Lewis, Paul Dano","oil, greed, ambition, religion",158,8.2,500000,70.0),
    ("Eternal Sunshine of the Spotless Mind",2004,"Drama, Romance, Sci-Fi","A couple undergo a procedure to erase each other from their memories when their relationship turns sour.","Michel Gondry","Jim Carrey, Kate Winslet","memory, love, loss, identity",108,8.3,800000,72.0),
    ("The Big Lebowski",1998,"Comedy, Crime","A case of mistaken identity leads a laid-back bowling enthusiast into a wild adventure.","Coen Brothers","Jeff Bridges, John Goodman","bowling, kidnapping, comedy, Los Angeles",117,8.1,700000,68.0),
    ("Toy Story",1995,"Animation, Adventure, Comedy","A cowboy doll is profoundly threatened when a new spaceman figure supplants him as top toy in a boy's room.","John Lasseter","Tom Hanks, Tim Allen","toys, friendship, adventure, Pixar",81,8.3,900000,73.0),
    ("Up",2009,"Animation, Adventure, Comedy","An elderly widower ties thousands of balloons to his house and flies to South America, with a young stowaway.","Pete Docter","Ed Asner, Jordan Nagai","adventure, balloons, friendship, loss",96,8.3,800000,74.0),
    ("Finding Nemo",2003,"Animation, Adventure, Comedy","A clownfish father searches the ocean to find his abducted son with the help of a forgetful blue tang.","Andrew Stanton","Albert Brooks, Ellen DeGeneres","ocean, fish, family, adventure",100,8.2,900000,75.0),
    ("Inside Out",2015,"Animation, Adventure, Comedy","After Riley moves to a new city, her emotions conflict on how best to navigate the world.","Pete Docter","Amy Poehler, Bill Hader","emotions, psychology, growing up, family",95,8.1,700000,76.0),
    ("Ratatouille",2007,"Animation, Comedy, Family","A rat who can cook makes an unusual alliance with a young kitchen worker at a famous Paris restaurant.","Brad Bird","Patton Oswalt, Ian Holm","cooking, paris, rat, dreams",111,8.1,700000,72.0),
]

# Templates for generating additional movies
_EXTRA_TEMPLATES = [
    {"genres":"Action, Thriller","keywords":"espionage, chase, danger","cast":"Action Star, Supporting Actor"},
    {"genres":"Comedy, Romance","keywords":"love, humor, dating","cast":"Comedy Lead, Romantic Interest"},
    {"genres":"Horror, Thriller","keywords":"fear, supernatural, dark","cast":"Scream Queen, Horror Veteran"},
    {"genres":"Sci-Fi, Adventure","keywords":"space, future, technology","cast":"Sci-Fi Lead, AI Voice"},
    {"genres":"Drama","keywords":"family, struggle, redemption","cast":"Drama Lead, Character Actor"},
    {"genres":"Animation, Family","keywords":"friendship, magic, journey","cast":"Voice Actor A, Voice Actor B"},
    {"genres":"Crime, Mystery","keywords":"detective, murder, clues","cast":"Detective Lead, Suspect Actor"},
    {"genres":"Fantasy, Adventure","keywords":"magic, quest, kingdom","cast":"Fantasy Hero, Wizard Actor"},
    {"genres":"Documentary","keywords":"real, investigation, society","cast":"Narrator"},
    {"genres":"Romance, Drama","keywords":"love, heartbreak, passion","cast":"Romantic Lead, Love Interest"},
    {"genres":"Western","keywords":"cowboy, frontier, duel","cast":"Western Hero, Outlaw"},
    {"genres":"Musical, Drama","keywords":"music, performance, fame","cast":"Singer Lead, Band Member"},
    {"genres":"War, Drama","keywords":"battle, courage, sacrifice","cast":"Soldier Lead, Commander"},
    {"genres":"Thriller, Mystery","keywords":"suspense, twist, conspiracy","cast":"Thriller Lead, Agent"},
]

_EXTRA_TITLES = [
    "Midnight Protocol","Echoes of Tomorrow","The Last Frontier","Shadow Conspiracy","Crimson Horizon",
    "Neon Requiem","Silent Storm","Phantom Code","Velvet Uprising","Arctic Mirage",
    "Digital Ghosts","Sapphire Dusk","Iron Resolve","Golden Deception","Emerald City",
    "Fractured Light","Ocean's Whisper","Thunder Below","Crystal Archives","Stellar Drift",
    "The Forgotten Path","Burning Bridges","Azure Dreams","Quantum Echoes","The Silver Line",
    "Obsidian Heart","Cosmic Frontier","The Paper Trail","Lunar Divide","Scarlet Promise",
    "The Glass Fortress","Wild Current","Frozen Legacy","Ember Falls","Twilight Signal",
    "Binary Sunset","Hollow Ground","Diamond Edge","Copper Moon","The Silk Road",
    "Storm Chaser","Dark Matter","The Iron Gate","Celestial Tide","Rust and Bone",
    "The Blue Hour","Prism Effect","Night Garden","Solar Wind","The Marble Palace",
    "Echo Chamber","Crimson Tide","The Black Swan","White Noise","Red Sparrow",
    "Deep Impact","Dark Skies","Bright Star","Cold Mountain","Lost Highway",
    "Winter's Tale","Summer Storm","Spring Awakening","Autumn Sonata","Dawn Patrol",
    "Dusk Runner","Moonlight Sonata","Starlight Express","Sundown Ridge","Nightfall City",
    "The Amber Room","Jade Dragon","Ruby Tuesday","Opal Fire","Pearl Harbor",
    "Topaz Blue","Onyx Rising","Garnet Throne","Quartz Valley","Cobalt Strike",
    "Phoenix Rising","Dragon's Keep","Serpent's Kiss","Eagle's Nest","Wolf Pack",
    "Lion's Den","Hawk's Eye","Falcon Ridge","Tiger's Claw","Bear Mountain",
    "The Architect","The Wanderer","The Guardian","The Cipher","The Catalyst",
    "The Harbinger","The Reckoning","The Outsider","The Pioneer","The Sentinel",
    "Parallel Lives","Distant Thunder","Broken Compass","Hidden Figures","Quiet Fury",
    "Blind Corner","Sharp Objects","Heavy Rain","Clear Danger","True North",
    "False Dawn","Double Cross","Triple Agent","Final Hour","Second Chance",
    "Third Eye","First Light","Last Stand","Zero Hour","One Shot",
    "City of Angels","Town of Shadows","Village of Stars","Kingdom of Dust","Empire of Light",
    "Republic of Fear","Nation of Heroes","World of Wonder","Land of Dreams","Island of Secrets",
    "Bridge of Spies","Tower of Glass","Castle of Sand","Garden of Eden","Forest of Echoes",
    "Desert Storm","Mountain Pass","River Deep","Valley High","Canyon Run",
    "Coast Guard","Border Cross","Frontier Justice","Wasteland Hope","Marshland Mystery",
    "Code Black","Signal Red","Status Green","Alert Blue","Phase Orange",
    "Protocol Seven","Sector Nine","Division Five","Unit Three","Squad Eight",
    "Agent Zero","Spy Games","Covert Action","Secret Mission","Hidden Agenda",
    "Silent Witness","Deadly Silence","Quiet Place","Loud Thunder","Soft Landing",
    "Hard Rain","Smooth Criminal","Rough Diamond","Sharp Shooter","Blunt Force",
    "Thin Ice","Thick Skin","Deep Blue","Shallow Grave","High Noon",
    "Low Tide","Long Road","Short Circuit","Fast Track","Slow Burn",
    "Hot Pursuit","Cold Case","Warm Bodies","Cool Runnings","Bitter Sweet",
    "Sweet Sixteen","Sour Grapes","Fresh Start","Stale Mate","Raw Deal",
    "Cooked Books","Fried Green","Baked Alaska","Frozen Assets","Melting Point",
    "Boiling Point","Breaking Bad","Making Waves","Taking Chances","Giving Grace",
    "Losing Faith","Finding Hope","Seeking Truth","Chasing Glory","Running Wild",
    "Walking Dead","Crawling Dark","Flying High","Falling Down","Rising Sun",
    "Setting Moon","Burning Day","Freezing Night","Floating World","Sinking Ship",
    "Dancing Shadows","Singing Swords","Painting Walls","Drawing Lines","Writing History",
    "Reading Signs","Counting Stars","Measuring Time","Building Dreams","Breaking Rules",
    "Changing Tides","Moving Mountains","Shaking Ground","Turning Tables","Closing Doors",
    "Opening Eyes","Crossing Lines","Pushing Limits","Pulling Strings","Cutting Edge",
    "Tearing Apart","Mending Fences","Healing Wounds","Growing Pains","Shrinking Violet",
    "Expanding Universe","Collapsing Stars","Exploding Myths","Imploding Dreams","Revolving Door",
    "Spinning Wheel","Rolling Thunder","Sliding Scale","Swinging Bridge","Rocking Chair",
    "Floating Island","Drifting Snow","Pouring Rain","Blowing Wind","Crashing Waves",
    "Flickering Flame","Glowing Ember","Shining Star","Sparkling Diamond","Gleaming Gold",
    "Fading Light","Dimming Sun","Brightening Sky","Darkening Storm","Clearing Fog",
    "Gathering Clouds","Scattering Leaves","Falling Petals","Blooming Rose","Wilting Flower",
    "Growing Vine","Climbing Ivy","Spreading Oak","Standing Pine","Bending Willow",
    "Ancient Ruins","Modern Times","Future Perfect","Past Tense","Present Danger",
    "Distant Memory","Close Call","Near Miss","Far Reach","Long Shot",
    "Quick Silver","Slow Motion","Fast Forward","Rewind Time","Pause Button",
    "Play Along","Stop Watch","Start Over","End Game","Middle Ground",
    "Upper Hand","Lower Depths","Inner Peace","Outer Limits","Center Stage",
    "Left Behind","Right Track","Straight Arrow","Crooked Path","Winding Road",
    "Narrow Escape","Wide Open","Broad Daylight","Slim Chance","Thick Plot",
    "Heavy Metal","Light Touch","Dark Horse","Bright Side","Gray Area",
    "Black Mirror","White Fang","Red Alert","Blue Lagoon","Green Light",
    "Yellow Brick","Purple Rain","Orange County","Pink Floyd","Silver Lining",
    "Golden Age","Bronze Medal","Platinum Rule","Copper Wire","Iron Will",
    "Steel Magnolia","Titanium Sky","Carbon Copy","Mercury Rising","Venus Trap",
    "Mars Attack","Jupiter Ascending","Saturn Return","Neptune Dive","Pluto Rising",
    "Solar Flare","Lunar Eclipse","Stellar Nova","Cosmic Ray","Galactic Core",
    "Nebula Heart","Asteroid Belt","Comet Trail","Meteor Shower","Orbit Decay",
    "Gravity Pull","Void Walker","Space Cadet","Time Warp","Dimension Shift",
    "Reality Check","Fantasy Island","Dream Catcher","Nightmare Alley","Vision Quest",
    "Memory Lane","Thought Crime","Mind Field","Brain Storm","Heart Beat",
    "Soul Train","Spirit Guide","Ghost Writer","Shadow Boxer","Light Keeper",
    "Dark Watcher","Night Crawler","Day Breaker","Dawn Treader","Dusk Settler",
    "Twilight Zone","Midnight Sun","High Morning","Afternoon Tea","Evening Star",
]

_OVERVIEWS = [
    "A gripping tale of survival against impossible odds in a world turned upside down.",
    "Two unlikely allies must work together to uncover a conspiracy that threatens everything they hold dear.",
    "In a near-future society, one person's discovery could change the course of human history forever.",
    "A heartwarming story of love, loss, and the enduring power of the human spirit.",
    "When darkness falls, a unlikely hero must rise to protect those who cannot protect themselves.",
    "An epic journey across uncharted territories reveals secrets that were meant to stay hidden.",
    "In the corridors of power, nothing is as it seems and trust is the most dangerous currency.",
    "A tale of revenge, redemption, and the thin line between justice and vengeance.",
    "When technology evolves beyond human control, a small team becomes humanity's last hope.",
    "A coming-of-age story that explores the boundaries of friendship, loyalty, and self-discovery.",
    "Deep in hostile territory, a covert operation goes wrong, forcing desperate measures.",
    "An artist's obsessive pursuit of perfection leads them down a dangerous and transformative path.",
    "Ancient mysteries resurface in the modern world, threatening to unleash chaos.",
    "A family torn apart by secrets must confront their past to survive the present.",
]

_DIRECTORS = [
    "James Mitchell","Sarah Chen","Marcus Rodriguez","Elena Volkov","David Park",
    "Lisa Thompson","Michael O'Brien","Aisha Patel","Robert Kim","Jessica Lane",
    "Thomas Wright","Maria Santos","Daniel Lee","Anna Kowalski","Steven Clark",
]

def seed_movies_and_ratings(db: Session) -> dict:
    """Seed the database with movies and synthetic ratings."""
    existing = db.query(Movie).count()
    if existing >= 50:
        return {"message": f"Database already has {existing} movies. Skipping seed.", "seeded": False}

    random.seed(42)
    movies = []

    # Add curated movies
    for i, m in enumerate(MOVIES_DATA):
        title, year, genres, overview, director, cast, keywords, runtime, rating, votes, pop = m
        
        movie = Movie(
            title=title, release_year=year, genres=genres, 
            overview=overview,
            director=director, cast=cast, keywords=keywords, runtime=runtime,
            vote_average=rating, vote_count=votes, popularity=pop,
        )
        
        try:
            tmdb_data = fetch_tmdb_poster_sync(title=title, year=year)
        except Exception:
            tmdb_data = {}
        if tmdb_data.get("poster_url"):
            movie.poster_url = tmdb_data["poster_url"]
            movie.backdrop_url = tmdb_data.get("backdrop_url")
            movie.tmdb_id = tmdb_data.get("tmdb_id")
            movie.overview = tmdb_data.get("overview") or overview
            print(f"  ✓ Poster found: {title}")
        else:
            movie.poster_url = f"https://placehold.co/300x450/1a1a2e/white?text={title.replace(' ', '+')}"
            print(f"  ✗ No poster (using placeholder): {title}")
        if TMDB_API_KEY:
            time.sleep(0.25)
        
        db.add(movie)
        movies.append(movie)

    # Generate additional movies to reach 500+
    for i, title in enumerate(_EXTRA_TITLES):
        tmpl = _EXTRA_TEMPLATES[i % len(_EXTRA_TEMPLATES)]
        year = random.randint(1970, 2024)
        runtime = random.randint(85, 180)
        rating = round(random.uniform(5.5, 8.5), 1)
        votes = random.randint(5000, 500000)
        pop = round(random.uniform(10.0, 70.0), 1)
        overview = _OVERVIEWS[i % len(_OVERVIEWS)]
        director = _DIRECTORS[i % len(_DIRECTORS)]
        
        movie = Movie(
            title=title, release_year=year, genres=tmpl["genres"], 
            overview=overview,
            director=director, cast=tmpl["cast"], keywords=tmpl["keywords"],
            runtime=runtime, vote_average=rating, vote_count=votes, popularity=pop,
        )
        
        try:
            tmdb_data = fetch_tmdb_poster_sync(title=title, year=year)
        except Exception:
            tmdb_data = {}
        if tmdb_data.get("poster_url"):
            movie.poster_url = tmdb_data["poster_url"]
            movie.backdrop_url = tmdb_data.get("backdrop_url")
            movie.tmdb_id = tmdb_data.get("tmdb_id")
            movie.overview = tmdb_data.get("overview") or overview
            print(f"  ✓ Poster found: {title}")
        else:
            movie.poster_url = f"https://placehold.co/300x450/1a1a2e/white?text={title.replace(' ', '+')}"
            print(f"  ✗ No poster (using placeholder): {title}")
        if TMDB_API_KEY:
            time.sleep(0.25)
        
        db.add(movie)
        movies.append(movie)

    db.commit()
    for m in movies:
        db.refresh(m)

    logger.info(f"Seeded {len(movies)} movies.")

    # Create seed users
    seed_users = []
    for i in range(1, 51):
        user = User(
            username=f"user{i}", email=f"user{i}@example.com",
            hashed_password=hash_password("password123"),
        )
        db.add(user)
        seed_users.append(user)

    # Create admin user
    admin = User(
        username="admin", email="admin@example.com",
        hashed_password=hash_password("admin123"), is_admin=True,
    )
    db.add(admin)
    db.commit()
    for u in seed_users:
        db.refresh(u)
    db.refresh(admin)

    # Generate synthetic ratings
    rating_count = 0
    movie_ids = [m.id for m in movies]
    for user in seed_users:
        n_ratings = random.randint(50, 200)
        rated_movies = random.sample(movie_ids, min(n_ratings, len(movie_ids)))
        for mid in rated_movies:
            score = round(random.uniform(1.0, 5.0) * 2) / 2  # 0.5 increments
            score = max(1.0, min(5.0, score))
            db.add(Rating(user_id=user.id, movie_id=mid, score=score))
            rating_count += 1

    db.commit()
    logger.info(f"Seeded {rating_count} ratings across {len(seed_users)} users.")

    return {"movies": len(movies), "users": len(seed_users) + 1, "ratings": rating_count, "seeded": True}
