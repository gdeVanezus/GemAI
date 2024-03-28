import disnake
from disnake.ext import commands
import logging
import g4f
from sydney import SydneyClient
import aiohttp
import uuid
import io

logger = logging.getLogger("disnake")

AiType = commands.option_enum(
    {
        "ChatGPT": "chatgpt",
        "Bing AI": "bing",
        "BlackBox AI": "blackbox",
        "Meta LLama 2 ": "llama",
    }
)


async def filter_nsfw(prompt):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://gist.githubusercontent.com/ryanlewis/a37739d710ccdb4b406d/raw/0fbd315eb2900bb736609ea894b9bde8217b991a/google_twunter_lol"
        ) as response:
            if response.status == 200:
                nsfw_words_data = await response.text()
                nsfw_words = {line.strip() for line in nsfw_words_data.split("\n")}
                for word in prompt.split():
                    if word.lower() in nsfw_words:
                        return True
                return False
            else:
                return False


class Ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_handlers = {
            "chatgpt": self.chatgpt_handler,
            "bing": self.bing_handler,
            "blackbox": self.blackbox_handler,
            "llama": self.llama_handler,
        }

    async def handle_ai(self, ai_type, inter, message):
        await inter.response.send_message(
            content="<:Cooldown:1222260506778407064> Generating... wait pls"
        )
        if ai_type in self.ai_handlers:
            await self.ai_handlers[ai_type](inter, message)
        else:
            await self.send_error_response(inter, "Invalid AI type")

    async def nsfw_err(self, inter, promt):
        embed = disnake.Embed(
            title="<:Error:1221918470954811422> Your promt have NSFW.",
            description="`lol dont use nsfw promts, or you will be banned in bot.`",
            color=disnake.Colour.brand_green(),
        )
        await inter.edit_original_response(content=None, embed=embed)

    async def handle_image(self, inter, promt, ephemeralbool):
        await inter.response.send_message(
            content="<:Cooldown:1222260506778407064> Generating... wait pls",
            ephemeral=ephemeralbool,
        )
        w = 1024
        h = 1024
        g = await filter_nsfw(promt)
        if g == True:
            await self.nsfw_err(inter, promt)
        else:
            await self.pollinations_handler(inter, promt, w, h)

    async def pollinations_handler(self, inter, promt, w, h):
        link = f"https://image.pollinations.ai/prompt/{promt}?width={w}&height={h}&nologo=rokosbasilisk"
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status == 200:
                    data = await response.read()
                    buffer = io.BytesIO(data)
                    embed = disnake.Embed(
                        title="<:Ok:1222137290625777717> Your generated image.",
                        description="> Promt: {}".format(promt),
                        color=disnake.Colour.brand_green(),
                    )
                    embed.set_image(
                        file=disnake.File(
                            buffer, filename="gemai_{}.jpg".format(inter.author.id)
                        )
                    )
                    await inter.edit_original_response(content=None, embed=embed)
                else:
                    embed = disnake.Embed(
                        title="err.",
                        description=">{} {}".format(response.text, response.status),
                        color=disnake.Colour.brand_green(),
                    )
                    await inter.edit_original_response(content=None, embed=embed)

    async def chatgpt_handler(self, inter, message):
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": message}],
            provider=g4f.Provider.Liaobots,
        )
        await self.send_embed(inter, "ChatGPT", response)

    async def bing_handler(self, inter, message):
        async with SydneyClient() as sydney:
            response = await sydney.ask(message, citations=True)
        await self.send_embed(inter, "Bing AI", response)

    async def blackbox_handler(self, inter, message):
        api = "https://www.blackbox.ai/api/chat"
        payload = {
            "messages": [{"content": message, "role": "user"}],
            "previewToken": None,
            "userId": str(uuid.uuid4()),
            "codeModelMode": True,
            "agentMode": {},
            "trendingAgentMode": {},
            "isMicMode": False,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(api, json=payload) as response:
                response_text = await response.text()
        await self.send_embed(inter, "Blackbox AI", response_text)

    async def llama_handler(self, inter, message):
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": f"{message}"}],
            provider=g4f.Provider.Llama2,
        )
        await self.send_embed(inter, "Meta LLama 2", response)

    async def send_embed(self, inter, title, description):
        embed = disnake.Embed(
            title=title, color=disnake.Colour.brand_green(), description=description
        )
        embed.set_footer(
            text="GemAI | " + title,
            icon_url="https://cdn.discordapp.com/attachments/1105120806519971960/1203770100176658432/discotools-xyz-icon_3.png?ex=65d24d44&is=65bfd844&hm=f27d813fab79aece9d1cac4404813ea76690b59536cf02e611517c5afa12dfc5&",
        )
        await inter.edit_original_response(content=None, embed=embed)

    async def send_error_response(self, inter, error_message):
        embed = disnake.Embed(
            title="Ohh... Error",
            color=disnake.Colour.red(),
        )
        embed.add_field(name="Error:", value=error_message)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="ai",
        description="Chat with AI.",
    )
    async def ai(self, inter: disnake.ApplicationCommandInteraction, message: str, ai: AiType):  # type: ignore
        try:
            await self.handle_ai(ai, inter, message)
        except Exception as e:
            print(e)
            await self.send_error_response(inter, str(e))

    @commands.slash_command(
        name="image",
        description="Create image.",
    )
    async def img(self, inter: disnake.ApplicationCommandInteraction, promt: str, ephemeral: bool):  # type: ignore
        try:
            await self.handle_image(inter, promt, ephemeral)
        except Exception as e:
            print(e)

            await self.send_error_response(inter, str(e))


def setup(bot):
    bot.add_cog(Ai(bot))
    logger.info(f"[ COGS ] Cog: {__name__} loaded")
