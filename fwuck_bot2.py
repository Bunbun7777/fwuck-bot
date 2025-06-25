import discord
from discord.ext import commands
import random
import os
import json
import datetime
from dotenv import load_dotenv
load_dotenv()
print("DISCORD_TOKEN from env:", os.getenv("DISCORD_TOKEN"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='fwuck ', intents=intents)

# ---- REMOVE DEFAULT HELP ----
bot.remove_command('help')

# ---- HELP EMBED FACTORY ----
def get_fwuck_help_embed():
    embed = discord.Embed(
        title="Fwuck Help Menu",
        description=(
            "**Commands:**\n"
            "`fwuck fish` — Go fishing in the sea. 🎣\n"
            "`fwuck blackjack` — Play a round of blackjack. 🃏\n"
            "`fwuck adventure` — Go on a random underwater adventure. 🌊\n"
            "`fwuck talk` — Get a snarky response from Fwuck. 🐡\n"
            "`fwuck market` — Sell your latest fish for FwuckCoin at the snarky market. 🏪\n"
            "`fwuck inventory` — View your fish and treasures in a pretty teal list. 🧰\n"
            "`fwuck freak` — Get a freaky roast from Fwuck. 😛\n"
            "`fwuck minigame` — Play a random sea minigame. 🎲\n"
            "`fwuck minigame_list` — See all minigames and how to play them. 🎲"
        ),
        color=0x1abc9c
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1328106326362161195/1386951222715486228/Pufferfish_large.webp")
    embed.set_footer(text="Fwuck the Pufferfish Bot", icon_url="https://cdn.discordapp.com/attachments/1328106326362161195/1386951222715486228/Pufferfish_large.webp")
    return embed

# ---- CUSTOM HELP COMMAND (PREFIX) ----
@bot.command(name="help")
@commands.cooldown(1, 30, commands.BucketType.user)
async def help_command(ctx):
    embed = get_fwuck_help_embed()
    try:
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I need permission to send embeds in this channel!")

# ---- OVERRIDE SLASH HELP COMMAND ----
@bot.tree.command(name="help", description="Show Fwuck's custom help menu")
async def slash_help(interaction: discord.Interaction):
    embed = get_fwuck_help_embed()
    await interaction.response.send_message(embed=embed, ephemeral=True)

# FWUCK personality
def fwuck_says(msg):
    responses = [
        "You again? What do you want now? 🐡",
        "Pfff, alright, let’s fwuckin’ go.",
        "You smell like algae, but sure, let's play.",
        "Ugh. Fine. One round. Then I'm going back to bubbling in rage."
    ]
    return f"**Fwuck:** {random.choice(responses)}\n{msg}"

# ---- FWUCK CURRENCY, INVENTORY, AND HISTORY SYSTEM ----
fwuck_balances = {}
fwuck_inventories = {}
fwuck_histories = {}

DATA_FILE = "fwuck_data.json"

def load_fwuck_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return (
                data.get("balances", {}),
                data.get("inventories", {}),
                data.get("histories", {})
            )
    except (FileNotFoundError, json.JSONDecodeError):
        return {}, {}, {}

def save_fwuck_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "balances": fwuck_balances,
            "inventories": fwuck_inventories,
            "histories": fwuck_histories
        }, f)

fwuck_balances, fwuck_inventories, fwuck_histories = load_fwuck_data()

def log_fwuck_history(user_id, action):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fwuck_histories.setdefault(user_id, []).append(f"[{now}] {action}")
    # Keep only the last 100 actions per user for space
    if len(fwuck_histories[user_id]) > 100:
        fwuck_histories[user_id] = fwuck_histories[user_id][-100:]
    save_fwuck_data()

# ---- COOLDOWN ERROR HANDLER ----
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        snark = random.choice([
            "Whoa there, barnacle-brain! Cool your fins and try again in a few seconds.",
            "You’re spamming harder than a school of sardines. Wait a bit! 🐡",
            "Patience, guppy. Even pufferfish need a breather.",
            "You’re on cooldown. Go touch some seaweed and try again soon.",
            "Slow down! You’re not a speedboat."
        ])
        await ctx.send(f"**Fwuck:** {snark} (Try again in {error.retry_after:.1f}s)")
    else:
        raise error

# ---- FISHING GAME ----
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def fish(ctx):
    fishes = [
        ("🐠 Clownfish", "common", 1),
        ("🐟 Bass", "common", 1),
        ("🐡 Pufferfish (not me, loser)", "uncommon", 3),
        ("🦈 Shark!", "rare", 7),
        ("🧜‍♀️ Mermaid?!", "legendary", 15)
    ]
    # Weighted probabilities: common=60%, uncommon=25%, rare=10%, legendary=5%
    weights = [30, 30, 20, 7, 3]
    fish, rarity, value = random.choices(fishes, weights=weights, k=1)[0]
    fish_responses = [
        f"You cast your rod... and caught: **{fish}**! Not bad. For a sea slug.",
        f"You caught: **{fish}**! Try not to scare the rest away.",
        f"**{fish}**! Even a blind crab gets lucky sometimes.",
        f"You fished up **{fish}**. Don't eat it all at once, guppy.",
        f"Congrats, you caught **{fish}**. I’ve seen better, but whatever.",
        f"**{fish}**? Wow, you’re really making waves. Not.",
        f"You caught **{fish}**! Don’t let it bite you, rookie.",
        f"**{fish}**. I’d clap, but I don’t have hands.",
        f"You call that fishing? Even a barnacle could do better.",
        f"Nice catch, I guess. Don’t expect a parade.",
        f"You caught **{fish}**. Try not to brag, minnow.",
        f"If you keep this up, you might actually impress a goldfish."
    ]
    user_id = str(ctx.author.id)
    fwuck_inventories.setdefault(user_id, []).append((fish, rarity, value))
    log_fwuck_history(user_id, f"Caught {fish} ({rarity}, {value} value)")
    save_fwuck_data()
    msg = f"**Fwuck:** {random.choice(fish_responses)}\nYour catch has been added to your inventory. Use `fwuck market` to sell it or `fwuck inventory` to see your stash."
    await ctx.send(msg)

# ---- KEEP FISH COMMAND ----
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def keep(ctx):
    user_id = str(ctx.author.id)
    if user_id not in fwuck_inventories or not fwuck_inventories[user_id]:
        await ctx.send("**Fwuck:** You have no fish to keep. Go fish first, guppy.")
        return
    fish, rarity, value = fwuck_inventories[user_id][-1]
    save_fwuck_data()
    await ctx.send(f"**Fwuck:** Fine, keep your precious {fish}. Try not to name it after me.")

# ---- DEFINE ALL POSSIBLE FISH AND THEIR VALUES FOR THE MARKET LIST ----
FISH_MARKET_PRICES = [
    ("🐠 Clownfish", "common", 1),
    ("🐟 Bass", "common", 1),
    ("🐡 Pufferfish (not me, loser)", "uncommon", 3),
    ("🦈 Shark!", "rare", 7),
    ("🧜‍♀️ Mermaid?!", "legendary", 15)
]

# ---- MARKET COMMAND ----
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def market(ctx):
    user_id = str(ctx.author.id)
    inventory = fwuck_inventories.get(user_id, [])
    snarky_market_open = [
        f"Welcome to the market, {ctx.author.display_name}. Try not to stink up the place.",
        "Let’s see what trash—I mean, treasure—you’ve brought.",
        "Oh look, another fishmonger. Don’t get your hopes up.",
        "If you’re here to sell, at least make it interesting.",
        "I hope you washed your fins before coming in here.",
        "The market’s open, but my patience isn’t."
    ]
    # Count each unique item in inventory
    item_counts = {}
    for fish, rarity, value in inventory:
        item_counts[fish] = item_counts.get(fish, 0) + 1
    # Show all possible fish, even if user has 0
    desc = random.choice(snarky_market_open) + "\n\n"
    for fish, rarity, value in FISH_MARKET_PRICES:
        count = item_counts.get(fish, 0)
        desc += f"{fish}: {count} (sells for {value} 🪙, {rarity})\n"
    desc += "\nType `fwuck sell <item name>` to sell something! (e.g., fwuck sell 🦈 Shark!)"
    embed = discord.Embed(
        title="🏪 Fwuck Market",
        description=desc,
        color=0x1abc9c
    )
    embed.set_footer(text=f"FwuckCoin: {fwuck_balances.get(user_id, 0)} 🪙 | Use 'fwuck inventory' to view your stash!", icon_url="https://cdn.discordapp.com/attachments/1328106326362161195/1386951222715486228/Pufferfish_large.webp")
    await ctx.send(embed=embed)

# ---- SELL COMMAND ----
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def sell(ctx, *, item: str = None):
    user_id = str(ctx.author.id)
    inventory = fwuck_inventories.get(user_id, [])
    if not inventory:
        await ctx.send(random.choice([
            "**Fwuck:** You have nothing to sell. Even your hopes are bankrupt.",
            "**Fwuck:** Your inventory is emptier than my sympathy for you.",
            "**Fwuck:** You want to sell air? Because that's all you've got.",
            "**Fwuck:** Come back when you actually own something, barnacle-brain."
        ]))
        return
    if not item:
        await ctx.send(random.choice([
            "**Fwuck:** You need to tell me what to sell. Try `fwuck sell 🦈 Shark!`",
            "**Fwuck:** Sell what? My patience? Type the item name, genius.",
            "**Fwuck:** You forgot the item. Try again, barnacle-brain."
        ]))
        return
    for i, (fish, rarity, value) in enumerate(inventory):
        if fish.lower() == item.strip().lower():
            fwuck_inventories[user_id].pop(i)
            fwuck_balances[user_id] = fwuck_balances.get(user_id, 0) + value
            log_fwuck_history(user_id, f"Sold {fish} for {value} 🪙 FwuckCoin")
            save_fwuck_data()
            snarky_sell = [
                f"Selling your {fish}? Bold move. Here’s {value} 🪙 FwuckCoin.",
                f"I’ll take that {fish} off your fins. Don’t spend it all in one tidepool.",
                f"{fish}? I’ve seen better, but here’s {value} 🪙 FwuckCoin.",
                f"You sure you want to part with {fish}? Too late now! {value} 🪙 FwuckCoin for you.",
                f"Fine, {fish} sold. Try not to blow your {value} 🪙 FwuckCoin on kelp snacks.",
                f"I hope you weren’t attached to {fish}. It’s mine now.",
                f"{fish} is gone. Your wallet’s fatter, but your soul is emptier.",
                f"You sell, I snark. That’s the deal. {value} 🪙 FwuckCoin for {fish}."
            ]
            await ctx.send(f"**Fwuck:** {random.choice(snarky_sell)} Your new balance: {fwuck_balances[user_id]} 🪙 FwuckCoin.")
            return
    await ctx.send(random.choice([
        f"**Fwuck:** You don’t have a '{item}' to sell. Check your inventory with `fwuck inventory`.",
        "**Fwuck:** No such item. Maybe you dreamed it, guppy.",
        "**Fwuck:** If you want to sell imaginary fish, try another server.",
        f"**Fwuck:** I checked twice. You don’t own a '{item}'. Maybe try fishing for real this time.",
        f"**Fwuck:** Selling things you don’t have? Bold strategy. Still not working."
    ]))

# ---- BLACKJACK GAME ----
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def blackjack(ctx):
    def card():
        return random.choice(['2','3','4','5','6','7','8','9','10','J','Q','K','A'])
    def score(hand):
        total = 0
        aces = hand.count('A')
        for card_ in hand:
            if card_ in ['J', 'Q', 'K']:
                total += 10
            elif card_ == 'A':
                total += 11
            else:
                total += int(card_)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
    player = [card(), card()]
    dealer = [card(), card()]
    player_score = score(player)
    dealer_score = score(dealer)
    result = "**You:** " + ', '.join(player) + f" ({player_score})\n"
    result += "**Dealer:** " + ', '.join(dealer) + f" ({dealer_score})\n\n"
    if player_score > 21:
        result += "You busted. 🤡"
    elif dealer_score > 21 or player_score > dealer_score:
        result += "You win. Ugh. Beginners luck."
    elif player_score == dealer_score:
        result += "Tie. Boring."
    else:
        result += "You lose. As expected."
    sea_emojis = [
        "🐡", "🐠", "🦑", "🦀", "🦐", "🦞", "🦈", "🐙", "🐟", "🪸", "🪼", "🌊", "🧜‍♀️", "🧜‍♂️", "🏝️", "🪙", "🦭", "🐬", "🐚", "🪆"
    ]
    blackjack_responses = [
        lambda: f"You play cards like a jellyfish—no backbone! 🙄 {random.choice(sea_emojis)}",
        lambda: f"Next time, try not to embarrass yourself. 🙄 {random.choice(sea_emojis)}",
        lambda: f"I’ve seen barnacles with better luck. 🙄 {random.choice(sea_emojis)}",
        lambda: f"Don’t spend all your winnings in one tidepool. 🙄 {random.choice(sea_emojis)}",
        lambda: f"You call that a strategy? Hah! 🙄 {random.choice(sea_emojis)}",
        lambda: f"Did you learn blackjack from a sea cucumber? 🙄 {random.choice(sea_emojis)}",
        lambda: f"Wow, you’re almost as bad as the dealer. 🙄 {random.choice(sea_emojis)}",
        lambda: f"If you win, it’s a fluke. If you lose, it’s expected. 🙄 {random.choice(sea_emojis)}",
        lambda: f"I’d say ‘good game’ but I’d be lying. 🙄 {random.choice(sea_emojis)}"
    ]
    msg = f"🃏 **Fwuck:** {random.choice(blackjack_responses)()}\n{result}"
    await ctx.send(msg)

# ---- ADVENTURE GAME ----
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def adventure(ctx):
    # Weighted places: kelp forest and pirate ship are most common, whale bones rarest
    places = [
        ("sunken pirate ship 🏴‍☠", 30),
        ("deep kelp forest 🥬", 30),
        ("toxic trench 🗾", 20),
        ("glowing reef 🪸", 15),
        ("ancient whale bones 🐋", 5)
    ]
    # Weighted finds: legendary=3, rare=10, uncommon=22, common=65
    finds = [
        ("legendary golden trout 🐟", 10, "legendary"),  # legendary
        ("a chest of gold 💰", 5, "rare"),              # rare
        ("a cursed pearl 🧿", 3, "uncommon"),           # uncommon
        ("an angry kraken 🐙", 1, "common"),            # common
        ("Fwuck's ex 🪼", 1, "common")                  # common
    ]
    find_weights = [3, 10, 22, 32, 33]  # sum to 100
    place_names, place_weights = zip(*places)
    place = random.choices(place_names, weights=place_weights, k=1)[0]
    find, reward, rarity = random.choices(finds, weights=find_weights, k=1)[0]
    user_id = str(ctx.author.id)
    fwuck_balances[user_id] = fwuck_balances.get(user_id, 0) + reward
    log_fwuck_history(user_id, f"Found {find} ({rarity}) while adventuring in {place} (reward: {reward} FwuckCoin)")
    save_fwuck_data()
    adventure_responses = [
        f"You swam through the {place} and found... **{find}**! I give it a 6/10.",
        f"Exploring the {place}, you discovered **{find}**. Not impressed.",
        f"{place}? Boring. But hey, you found **{find}**. Lucky you.",
        f"You braved the {place} and found **{find}**. Try not to brag.",
        f"**{find}**? I hope you brought a mop for your ego.",
        f"You found **{find}** in the {place}. Don’t get cocky.",
        f"{place} gave you **{find}**. I’m shocked you survived.",
        f"**{find}**? I’ve seen better prizes in a crab trap.",
        f"You found **{find}**. Don’t let it go to your head, barnacle.",
        f"{place} and you come back with **{find}**? Typical.",
        f"If you find anything weirder, let me know. I need a laugh.",
        f"**{find}**? I’d trade it for a decent snack."
    ]
    msg = f"**Fwuck:** {random.choice(adventure_responses)}\nYou earned {reward} FwuckCoin!\nYour total: {fwuck_balances[user_id]} 🪙 FwuckCoin."
    await ctx.send(msg)

# ---- BASIC INTERACT ----
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def talk(ctx):
    talk_responses = [
        "You're brave for talking to me without scales.",
        "Did you always sound like a broken shell horn?",
        "You again? Go step on coral.",
        "You're lucky I'm bored enough to respond.",
        "I’d rather talk to a sea cucumber, but here we are.",
        "What do you want now, landwalker?",
        "If you want advice, try not to be you.",
        "You’re about as interesting as a bucket of sand.",
        "I’d roast you, but you’d probably enjoy it.",
        "You want wisdom? Don’t talk to fish.",
        "I’m only listening because I have nothing better to do.",
        "You’re the reason I have trust issues with humans.",
        "If I had a pearl for every dumb question, I’d be rich.",
        "You talk, I zone out. It’s a system.",
        "I’d say something nice, but I’m allergic."
    ]
    sea_emojis = [
        "🐡", "🐠", "🦑", "🦀", "🦐", "🦞", "🦈", "🐙", "🐟", "🪸", "🪼", "🌊", "🧜‍♀️", "🧜‍♂️", "🏝️", "🪙", "🦭", "🐬", "🐚", "🪆"
    ]
    msg = f"**Fwuck:** {random.choice(talk_responses)} {random.choice(sea_emojis)}"
    await ctx.send(msg)

# ---- INVENTORY COMMAND ----
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def inventory(ctx):
    user_id = str(ctx.author.id)
    inventory = fwuck_inventories.get(user_id, [])
    if not inventory:
        desc = random.choice([
            "You have no fish or treasures. Go fish or adventure, guppy!",
            "Your inventory is emptier than a sea urchin’s diary.",
            "Nothing here but your hopes and dreams. Try harder.",
            "No loot? No glory. Get back out there, barnacle-brain.",
            "Your inventory is so empty, even the crabs are laughing.",
            "If emptiness was valuable, you’d be rich right now.",
            "You couldn’t catch a cold, let alone a fish.",
            "I’ve seen more action in a puddle.",
            "You call this an inventory? My patience is fuller than this."
        ])
    else:
        # Count each unique item
        item_counts = {}
        for fish, rarity, value in inventory:
            item_counts[fish] = item_counts.get(fish, 0) + 1
        desc = "\n".join([f"{fish}: {count}" for fish, count in item_counts.items()])
        desc += f"\n\nFwuck says: {random.choice([
            'Not bad, but I’ve seen better collections.',
            'Try not to lose it all in the market.',
            'If you’re proud of this, you need new hobbies.',
            'I’d steal your loot, but I have standards.',
            'You call this treasure? More like trashure.'
        ])}"
    embed = discord.Embed(
        title="🪙 Fwuck Inventory",
        description=desc,
        color=0x1abc9c
    )
    embed.set_footer(text=f"FwuckCoin: {fwuck_balances.get(user_id, 0)} 🪙 | Use 'fwuck market' to sell fish!", icon_url="https://cdn.discordapp.com/attachments/1328106326362161195/1386951222715486228/Pufferfish_large.webp")
    await ctx.send(embed=embed)

# ---- MINIGAME LIST COMMAND ----
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def minigame_list(ctx):
    minigames = [
        ("1", "Bubble Pop", "🫧", "Pop all the bubbles by typing 'answer pop' the right number of times!"),
        ("2", "Emoji Memory", "🧠", "Memorize and repeat a sequence of sea emojis!"),
        ("3", "Odd One Out", "🍕", "Spot the land item among the sea creatures!"),
        ("4", "Sea Trivia", "❓", "Answer a snarky sea-themed trivia question!"),
        ("5", "Guess the Fish", "🐡", "Guess which fish Fwuck is thinking of!"),
        ("6", "Shell Shuffle", "🐚", "Find the jewel hidden under the shells!"),
        ("7", "Kraken Math", "🦑", "Solve a tentacle-twisting math problem!")
    ]
    desc = "Here are all the minigames you can play with Fwuck:\n\n"
    for num, name, emoji, description in minigames:
        desc += f"{emoji} **{num}. {name}** — {description}\n"
    desc += ("\nType `fwuck minigame <number>` to play a specific minigame, "
             "or `fwuck minigame random` for a surprise!\n" 
             "(Or just `fwuck minigame` for a random pick.) 🐡")
    embed = discord.Embed(
        title="🎲 Fwuck's Minigame List",
        description=desc,
        color=0x1abc9c
    )
    embed.set_footer(text="Try not to lose to a pufferfish.", icon_url="https://cdn.discordapp.com/attachments/1328106326362161195/1386951222715486228/Pufferfish_large.webp")
    await ctx.send(embed=embed)

# ---- BOT ONLINE ----
@bot.event
async def on_ready():
    print(f"Fwuck is loose in the sea... Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} application commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# ---- CUSTOM HELP TRIGGER ----
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

# ---- FREAK COMMAND ----
# Track last freak response per user to avoid repeats
last_freak_response = {}

@bot.command()
async def freak(ctx):
    freaky_emojis = [
        "🐡", "🐠", "🦑", "🦀", "🦐", "🦞", "🦈", "🐙", "🐟", "🪸", "🪼", "🌊", "🧜‍♀️", "🧜‍♂️", "🏝️", "🪙", "🦭", "🐬", "🐚", "🪆",
        "😉", "😜", "😛", "😝", "😏", "💀"
    ]
    freaky_responses = [
        "You want freaky? I’ve seen sea cucumbers do weirder things.",
        "You’re about as freaky as a jellyfish at a disco. Settle down.",
        "Freaky? Please. I’ve seen barnacles with more imagination.",
        "You want me to get freaky? I’m a pufferfish, not your therapist.",
        "You’re the reason the kraken stays in hiding.",
        "Freaky? I’d call you a sea monster, but that’s an insult to monsters.",
        "You’re so freaky, even the mermaids file restraining orders.",
        "Freaky? I’d say you’re unique, but that’s just a nice way of saying weird.",
        "You want freaky? Try not to scare the plankton next time.",
        "You’re the type to ask a pufferfish for dating advice. That’s freaky enough.",
        "You want a roast? You’re so freaky, even the eels swim away.",
        "Freaky? I’d puff up, but you’re not worth the effort."
    ]
    user_id = str(ctx.author.id)
    last_idx = last_freak_response.get(user_id, None)
    choices = list(range(len(freaky_responses)))
    if last_idx is not None and len(choices) > 1:
        choices.remove(last_idx)
    idx = random.choice(choices)
    last_freak_response[user_id] = idx
    msg = f"**Fwuck:** {freaky_responses[idx]} {random.choice(freaky_emojis)}"
    await ctx.send(msg)

# ---- REPLACE MINIGAME COMMAND TO ACCEPT NUMBER OR RANDOM ----
@bot.command()
async def minigame(ctx, which: str = None):
    minigames = [
        "bubble_pop",
        "emoji_memory",
        "odd_one_out",
        "sea_trivia",
        "guess_the_fish",
        "shell_shuffle",
        "kraken_math"
    ]
    minigame_names = [
        "Bubble Pop", "Emoji Memory", "Odd One Out", "Sea Trivia", "Guess the Fish", "Shell Shuffle", "Kraken Math"
    ]
    # Determine which minigame to play
    if which is not None:
        if which.lower() == "random":
            chosen = random.choice(minigames)
        else:
            try:
                idx = int(which) - 1
                if 0 <= idx < len(minigames):
                    chosen = minigames[idx]
                else:
                    await ctx.send(f"**Fwuck:** That's not a valid minigame number, barnacle-brain. Type `fwuck minigame_list` to see your options. 🐡")
                    return
            except ValueError:
                await ctx.send(f"**Fwuck:** I don't know what you want. Type `fwuck minigame_list` for the list. 🐡")
                return
    else:
        chosen = random.choice(minigames)

    sea_emojis = ["🐡", "🐠", "🦑", "🦀", "🦐", "🦞", "🦈", "🐙", "🐟", "🪸", "🪼", "🌊", "🧜‍♀️", "🧜‍♂️", "🏝️", "🪙", "🦭", "🐬", "🐚", "🪆", "🎲"]
    snarky_intro = [
        "Ready for a minigame? Try not to embarrass yourself. {0}",
        "Let’s see if you can handle this, guppy. {0}",
        "Time for a minigame! Don’t cry if you lose. {0}",
        "I hope you’re smarter than a sea cucumber. {0}",
        "Let’s see if you can win something for once. {0}",
        "Minigame time! Try not to get water in your brain. {0}",
        "Here’s a minigame. Don’t mess it up. {0}"
    ]
    intro = random.choice(snarky_intro).format(random.choice(sea_emojis))
    def snarky_reply(kind):
        correct = [
            "You actually got it right? I’m shocked. {0}",
            "Not bad, for a landwalker. {0}",
            "You win this round. Don’t get cocky. {0}",
            "Even a broken shell gets lucky. {0}",
            "Fine, you got it. Don’t expect a medal. {0}"
        ]
        wrong = [
            "Wrong! Even a barnacle could do better. {0}",
            "Nope. Try again when you grow gills. {0}",
            "That’s not it. Maybe next time, guppy. {0}",
            "Incorrect! Did you hit your head on coral? {0}",
            "You call that an answer? Pfft. {0}"
        ]
        timeout = [
            "Too slow! Did you fall asleep? {0}",
            "Time’s up! Even seaweed moves faster. {0}",
            "Missed your chance. Maybe next tide. {0}",
            "You snooze, you lose. Literally. {0}",
            "Guess you’re still thinking... and thinking... {0}"
        ]
        if kind == 'correct':
            return random.choice(correct).format(random.choice(sea_emojis))
        elif kind == 'wrong':
            return random.choice(wrong).format(random.choice(sea_emojis))
        else:
            return random.choice(timeout).format(random.choice(sea_emojis))

    def check_author(m):
        return m.author == ctx.author and m.channel == ctx.channel

    async def wait_for_correct_answer(check_func, correct_value, timeout=60):
        try:
            while True:
                m = await bot.wait_for('message', check=check_author, timeout=timeout)
                user_input = m.content.strip()
                if check_func(user_input, correct_value):
                    await ctx.send(f"**Fwuck:** {snarky_reply('correct')}")
                    return True
                else:
                    await ctx.send(f"**Fwuck:** {snarky_reply('wrong')}")
        except Exception:
            await ctx.send(f"**Fwuck:** {snarky_reply('timeout')}")
            return False

    if chosen == "bubble_pop":
        bubbles = random.randint(3, 7)
        msg = f"**Fwuck:** {intro}\nType `answer pop` {bubbles} times, one per message, to pop all the bubbles! {random.choice(sea_emojis)}"
        await ctx.send(msg)
        popped = 0
        try:
            while popped < bubbles:
                m = await bot.wait_for('message', check=check_author, timeout=60)
                if m.content.strip().lower() == 'answer pop':
                    popped += 1
                    await ctx.send(f"**Fwuck:** Bubble popped! ({popped}/{bubbles}) {random.choice(sea_emojis)}")
                else:
                    await ctx.send(f"**Fwuck:** {snarky_reply('wrong')}")
            await ctx.send(f"**Fwuck:** {snarky_reply('correct')}")
        except Exception:
            if popped == 0:
                await ctx.send(f"**Fwuck:** {snarky_reply('timeout')}")
            else:
                await ctx.send(f"**Fwuck:** You only popped {popped}/{bubbles} bubbles. {snarky_reply('wrong')}")
    elif chosen == "emoji_memory":
        emojis = random.sample(sea_emojis, 4)
        to_memorize = ' '.join(emojis)
        msg = f"**Fwuck:** {intro}\nMemorize these sea emojis: {to_memorize}\nType your answer as `answer {to_memorize}` {random.choice(sea_emojis)}"
        await ctx.send(msg)
        await wait_for_correct_answer(lambda u, c: u == f'answer {c}', to_memorize)
    elif chosen == "odd_one_out":
        group = ["🐟", "🐠", "🐡", "🦈", "🦀"]
        odd = "🍕"
        items = group + [odd]
        random.shuffle(items)
        msg = f"**Fwuck:** {intro}\nWhich one doesn’t belong? {' '.join(items)}\nType your answer as `answer 🍕` or `answer pizza` {random.choice(sea_emojis)}"
        await ctx.send(msg)
        await wait_for_correct_answer(lambda u, c: u.lower() in ['answer 🍕', 'answer pizza'], odd)
    elif chosen == "sea_trivia":
        trivia = [
            ("What’s the largest animal in the ocean?", "blue whale"),
            ("What fish can puff up to scare predators?", "pufferfish"),
            ("What’s the fastest sea creature?", "sailfish"),
            ("What sea animal has eight arms?", "octopus")
        ]
        q, a = random.choice(trivia)
        msg = f"**Fwuck:** {intro}\nSea Trivia: {q}\nType your answer as `answer {a}` {random.choice(sea_emojis)}"
        await ctx.send(msg)
        await wait_for_correct_answer(lambda u, c: u.lower() == f'answer {c}', a)
    elif chosen == "guess_the_fish":
        fish_choices = ["🐡", "🦈", "🐟", "🐠"]
        fish = random.choice(fish_choices)
        msg = f"**Fwuck:** {intro}\nGuess which fish I’m thinking of: {' '.join(fish_choices)}\nType your answer as `answer {fish}` {random.choice(sea_emojis)}"
        await ctx.send(msg)
        await wait_for_correct_answer(lambda u, c: u == f'answer {c}', fish)
    elif chosen == "shell_shuffle":
        shells = ["🐚", "🐚", "💎"]
        random.shuffle(shells)
        jewel_index = shells.index("💎") + 1
        msg = f"**Fwuck:** {intro}\nWhich shell hides the jewel? {' '.join(shells)} (pick 1, 2, or 3)\nType your answer as `answer {jewel_index}` {random.choice(sea_emojis)}"
        await ctx.send(msg)
        await wait_for_correct_answer(lambda u, c: u == f'answer {c}', str(jewel_index))
    elif chosen == "kraken_math":
        a, b = random.randint(1, 10), random.randint(1, 10)
        answer = str(a + b)
        msg = f"**Fwuck:** {intro}\nIf a kraken has {a} tentacles in one wave and {b} in another, how many tentacles in total?\nType your answer as `answer {answer}` {random.choice(sea_emojis)}"
        await ctx.send(msg)
        await wait_for_correct_answer(lambda u, c: u == f'answer {c}', answer)


# ---- RUN BOT ----
# Use the token directly for now, since the environment variable is not set up
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("DISCORD_TOKEN is missing! Make sure your .env file is named exactly '.env', is in the same folder as this script, and contains a line like DISCORD_TOKEN=yourbottokenhere. Then restart the bot.")
bot.run(token)