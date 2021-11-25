corpus = {
    "blackgate speech": """Hold your ground! Hold your ground!
Sons of Gondor, of Rohan, my brothers, I see in your eyes the same fear that would take the heart of me
A day may come when the courage of men fails, when we forsake our friends and break all bonds of fellowship, but it is not this day
An hour of wolves and shattered shields, when the age of men comes crashing down, but it is not this day!
This day we fight!
By all that you hold dear on this good Earth, I bid you stand, Men of the West!""",
    "pride and prejudice": """It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife
he is considered the rightful property of some one or other of their daughters
The day passed much as the day before had done 
Mrs Hurst and Miss Bingley had spent some hours of the morning with the invalid, who continued though slowly to mend;
and in the evening Elizabeth joined their party in the drawing-room
Vanity and pride are different things, though the words are often used synonymously
A person may be proud without being vain
Pride relates more to our opinion of ourselves, vanity to what we would have others think of us
There are few people whom I really love, and still fewer of whom I think well
There is, I believe, in every disposition a tendency to some particular evil—a natural defect, which not even the best education can overcome
Nothing is more deceitful than the appearance of humility
A person who can write a long letter with ease, cannot write ill
Is not general incivility the very essence of love?
Those who do not complain are never pitied
To be fond of dancing was a certain step towards falling in love
For what do we live, but to make sport for our neighbors, and laugh at them in our turn?
Angry people are not always wise
But people themselves alter so much, that there is something new to be observed in them for ever
The distance is nothing when one has motive""",
    "science fiction authors": """The function of science fiction is not always to predict the future, but sometimes to prevent it""",
    "space quotes": """The Earth is the cradle of humanity, but mankind cannot stay in the cradle forever
Earth is a small town with many neighborhoods in a very big universe
It suddenly struck me that that tiny pea, pretty and blue, was the Earth
I put up my thumb and shut one eye, and my thumb blotted out the planet Earth 
I didn’t feel like a giant I felt very, very small
When I first looked back at the Earth, standing on the Moon, I cried
The Earth was small, light blue, and so touchingly alone, our home that must be defended like a holy relic
The Earth was absolutely round
I believe I never knew what the word round meant until I saw Earth from space
That's one small step for man, one giant leap for mankind
Exploration is in our nature
We began as wanderers, and we are wanderers still
We have lingered long enough on the shores of the cosmic ocean
We are ready at last to set sail for the stars
For me, it is far better to grasp the Universe as it really is than to persist in delusion, however satisfying and reassuring
Looking up into the night sky is looking into infinity – distance is incomprehensible and therefore meaningless
Two possibilities exist: either we are alone in the Universe or we are not
Both are equally terrifying""",
    "churchill": """we shall not flag or fail
we shall go on to the end
we shall fight with growing confidence and growing strength in the air,
We shall fight on the beaches,
we shall fight in the fields and in the streets,
we shall never surrender,
It is a good thing for an uneducated man to read books of quotations
There are a terrible lot of lies going about the world, and the worst of it is that half of them are true
To build may have to be the slow and laborious task of years
To destroy can be the thoughtless act of a single day
To improve is to change, so to be perfect is to change often
The farther backward you can look, the farther forward you are likely to see
The price of greatness is responsibility""",
}

if __name__ == "__main__":
    from augustine_text.data_manager import Doc, get_db

    db = get_db().initialize()

    for name, text in corpus.items():
        Doc.from_string(doc_name=name, text=text).save()
