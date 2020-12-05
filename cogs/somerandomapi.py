from discord import Embed
from discord.ext import commands
from aiohttp import request


class SomeRandomApiCog(commands.Cog, name="fact"):

    """Some random facts about animals!"""

    def __init__(self, client):
        self.client = client

    @commands.command(name="fact", description="Learn something new about animals! Type `.fact dog` to learn something about dogs. You can use: 'dog', 'cat', 'panda', 'fox', 'bird', 'koala', 'kangaroo', 'racoon', 'elephant', 'giraffe', 'whale'.")
    async def animal_fact(self, ctx, animal: str):
        animal = animal.lower()
        facts_channel = self.client.get_channel(784465328268640366)
        if animal in ("dog", "cat", "panda", "fox", "bird", "koala", "kangaroo", "racoon", "elephant", "giraffe", "whale"):
            fact_url = f"https://some-random-api.ml/facts/{animal}"
            image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

            async with request("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]
                else:
                    image_link = None
            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f"{animal.title()} fact",
                            description=data["fact"],
                            color=3066993)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await facts_channel.send(embed=embed)

                else:
                    await facts_channel.send("API returned a {response.status} status.")
        else:
            await facts_channel.send("No facts are available for that animal.")

def setup(client):
    client.add_cog(SomeRandomApiCog(client))
    print("Some random API is loaded.")