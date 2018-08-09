from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Owner, Item

engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False},)
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine


# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
DBSession = sessionmaker(bind=engine)
session = DBSession()

# inint from user to catalog to item.
# commit to db.

user1 = User(name='user1')
user1.hash_password('password1')
session.add(user1)

user2 = User(name='user2')
user2.hash_password('password2')
session.add(user2)

user3 = User(name='user3')
user3.hash_password('password3')
session.add(user3)

user4 = User(name='user4')
user4.hash_password('password4')
session.add(user4)

user5 = User(name='user5')
user5.hash_password('password5')
session.add(user5)

session.commit()

user1_id = session.query(User).filter_by(name=user1.name).first().id
user2_id = session.query(User).filter_by(name=user2.name).first().id
user3_id = session.query(User).filter_by(name=user3.name).first().id
user4_id = session.query(User).filter_by(name=user4.name).first().id
user5_id = session.query(User).filter_by(name=user5.name).first().id

owner1 = Owner(name="literature", user_id=user1_id)
owner2 = Owner(name="sculpture", user_id=user2_id)
owner3 = Owner(name="drawing", user_id=user3_id)
owner4 = Owner(name="dance", user_id=user4_id)
owner5 = Owner(name="theatre", user_id=user5_id)
owner6 = Owner(name="painting", user_id=user3_id)
# owner7 = Owner(name="movies", user_id=user3_id)
# owner8 = Owner(name="handicraft", user_id=user4_id)

session.add(owner1)
session.add(owner2)
session.add(owner3)
session.add(owner4)
session.add(owner5)
session.add(owner6)
# session.add(owner7)
# session.add(owner8)

session.commit()

owner1_id = session.query(Owner).filter_by(name=owner1.name).first().id
owner2_id = session.query(Owner).filter_by(name=owner2.name).first().id
owner3_id = session.query(Owner).filter_by(name=owner3.name).first().id
owner4_id = session.query(Owner).filter_by(name=owner4.name).first().id
owner5_id = session.query(Owner).filter_by(name=owner5.name).first().id
owner6_id = session.query(Owner).filter_by(name=owner6.name).first().id
# owner7_id = session.query(Owner).filter_by(name=owner7.name)
# owner8_id = session.query(Owner).filter_by(name=owner8.name)

# owner1
item1 = Item(
        name="Novel",
        description="A novel is a relatively"
        " long work of narrative fiction, normally"
        " in prose, which is "
        " typically published as a book.",
        rate=0,
        price=0,
        owner_id=owner1_id,
        user_id=user1_id)

item2 = Item(
        name="Poem",
        description="A poem is a form of literary art in which "
        "language is used for its aesthetic and "
        "evocative qualities.",
        rate=0,
        price=0,
        owner_id=owner1_id,
        user_id=user2_id)

item3 = Item(
        name="Drama",
        description="Drama is the specific mode of fiction "
        "represented in performance: a play performed in a theatre, "
        "or on radio or television.",
        rate=0,
        price=0,
        owner_id=owner1_id,
        user_id=user1_id)

item4 = Item(
        name="Short Story",
        description="A short story is a piece of prose fiction that "
        "typically can be read in one sitting and focuses on a "
        "self-contained incident or series of linked incidents, "
        "with the intent of evoking a 'single effect' or mood, "
        "however there are many exceptions to this.",
        rate=0,
        price=0,
        owner_id=owner1_id,
        user_id=user3_id)

item5 = Item(
        name="Novella",
        description="A novella is a text of written, fictional, "
        "narrative prose normally longer than a short story but shorter"
        " than a novel, somewhere between 7,500 and 40,000 words.",
        rate=0,
        price=0,
        owner_id=owner1_id,
        user_id=user5_id)

session.add(item1)
session.add(item2)
session.add(item3)
session.add(item4)
session.add(item5)

session.commit()

# owner2
item1 = Item(
        name="Statue",
        description="A statue is a free-standing sculpture in which "
        "the realistic, full-length figures of persons or animals or "
        "non-representational forms are carved in durable material "
        "(like wood, metal, or stone) and placed on a pedestal in a "
        "public place as public art to serve as an impressive and "
        "commanding material support for contemplation of persons, "
        "events, concepts or other realities of religious, historical, "
        "moral, or spiritual import.",
        rate=0,
        price=0,
        owner_id=owner2_id,
        user_id=user5_id)

item2 = Item(
        name="Monumental sculpture",
        description="The term monumental sculpture is often used "
        "in art history and criticism, but not always consistently.",
        rate=0,
        price=0,
        owner_id=owner2_id,
        user_id=user2_id)

item3 = Item(
        name="Sound sculpture",
        description="Sound sculpture (related to sound art and "
        "sound installation) is an intermedia and time based art form "
        "in which sculpture or any kind of art object produces sound, "
        "or the reverse (in the sense that sound is manipulated in such "
        "a way as to create a sculptural as opposed "
        "to temporal form or mass).",
        rate=0,
        price=0,
        owner_id=owner2_id,
        user_id=user1_id)

item4 = Item(
        name="Environmental sculpture",
        description="Environmental sculpture is sculpture that "
        "creates or alters the environment for the viewer, as opposed "
        "to presenting itself figurally or monumentally before the viewer.",
        rate=0,
        price=0,
        owner_id=owner2_id,
        user_id=user3_id)

session.add(item1)
session.add(item2)
session.add(item3)
session.add(item4)

session.commit()

# owner3
item1 = Item(
        name="Architectural drawing",
        description="An architectural drawing or architect's "
        "drawing is a technical drawing of a building (or "
        "building project) that falls within the definition "
        "of architecture realities of religious, historical, "
        "moral, or spiritual import.",
        rate=0,
        price=0,
        owner_id=owner3_id,
        user_id=user1_id)

item2 = Item(
        name="Engineering drawing",
        description="An engineering drawing, a type of technical "
        "drawing, is used to fully and clearly define requirements "
        "for engineered items.",
        rate=0,
        price=0,
        owner_id=owner3_id,
        user_id=user2_id)

item3 = Item(
        name="Figure drawing",
        description="A figure drawing is a drawing of the human "
        "form in any of its various shapes and postures using any "
        "of the drawing media.",
        rate=0,
        price=0,
        owner_id=owner3_id,
        user_id=user2_id)

item4 = Item(
        name="Subtractive drawing",
        description="Subtractive drawing is a technique in which "
        "the drawing surface is covered with graphite or charcoal and "
        "then erased to make the image.",
        rate=0,
        price=0,
        owner_id=owner3_id,
        user_id=user5_id)

session.add(item1)
session.add(item2)
session.add(item3)
session.add(item4)

session.commit()

# owner4
item1 = Item(
        name="Africa",
        description="Dance in Africa is deeply integrated into "
        "society and major events in a community are frequently "
        "reflected in dances: dances are performed for births and "
        "funerals, weddings and wars.",
        rate=0,
        price=0,
        owner_id=owner4_id,
        user_id=user4_id)

item2 = Item(
        name="Asia",
        description="All Indian classical dances are to varying "
        "degrees rooted in the Natyashastra and therefore share common "
        "features: for example, the mudras (hand positions), some body "
        "positions, and the inclusion of dramatic or expressive acting "
        "or abhinaya.",
        rate=0,
        price=0,
        owner_id=owner4_id,
        user_id=user4_id)

item3 = Item(
        name="Europe and North America",
        description="Folk dances vary across Europe and may date "
        "back hundreds or thousands of years, but many have features "
        "in common such as group participation led by a caller, "
        "hand-holding or arm-linking between participants, and fixed "
        "musical forms known as caroles.",
        rate=0,
        price=0,
        owner_id=owner4_id,
        user_id=user4_id)

item4 = Item(
        name="Latin America",
        description="Dance is central to Latin American "
        "social life and culture.",
        rate=0,
        price=0,
        owner_id=owner4_id,
        user_id=user1_id)

session.add(item1)
session.add(item2)
session.add(item3)
session.add(item4)

session.commit()

# owner5
item1 = Item(
        name="Drama",
        description="Drama is the specific mode of fiction "
        "represented in performance.",
        rate=0,
        price=0,
        owner_id=owner5_id,
        user_id=user5_id)

item2 = Item(
        name="Musical theatre",
        description="Musical theatre is a form of theatrical "
        "performance that combines songs, spoken dialogue, "
        "acting and dance.",
        rate=0,
        price=0,
        owner_id=owner5_id,
        user_id=user2_id)

item3 = Item(
        name="Comedy",
        description="Theatre productions that use humour as a vehicle "
        "to tell a story qualify as comedies. ",
        rate=0,
        price=0,
        owner_id=owner5_id,
        user_id=user3_id)

item4 = Item(
        name="Tragedy",
        description="Aristotle's phrase 'several kinds being "
        "found in separate parts of the play' is a reference to "
        "the structural origins of drama.",
        rate=0,
        price=0,
        owner_id=owner5_id,
        user_id=user1_id)

session.add(item1)
session.add(item2)
session.add(item3)
session.add(item4)

session.commit()

# owner6
item1 = Item(
        name="Allegory",
        description="Allegory is a figurative mode of "
        "representation conveying meaning other than the literal. "
        "Allegory communicates its message by means of symbolic "
        "figures, actions or symbolic representation.",
        rate=0,
        price=0,
        owner_id=owner6_id,
        user_id=user4_id)

item2 = Item(
        name="Bodegon",
        description="In Spanish art, a bodegon is a still life "
        "painting depicting pantry items, such as victuals, game, "
        "and drink, often arranged on a simple stone slab, and also "
        "a painting with one or more figures, but significant still "
        "life elements, typically set in a kitchen or tavern.",
        rate=0,
        price=0,
        owner_id=owner6_id,
        user_id=user1_id)

item3 = Item(
        name="Figure painting",
        description="A figure painting is a work of art in any of the "
        "painting media with the primary subject being the human figure, "
        "whether clothed or nude. Figure painting may also refer to the "
        "activity of creating such a work.",
        rate=0,
        price=0,
        owner_id=owner6_id,
        user_id=user3_id)

item4 = Item(
        name="Illustration painting",
        description="Illustration paintings are those used "
        "as illustrations in books, magazines, and theater or "
        "movie posters and comic books. Today, there is a "
        "growing interest in collecting and admiring the "
        "original artwork. ",
        rate=0,
        price=0,
        owner_id=owner6_id,
        user_id=user5_id)

session.add(item1)
session.add(item2)
session.add(item3)
session.add(item4)

session.commit()
