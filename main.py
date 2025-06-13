import json
import discord 
from discord.ext import commands, tasks
import requests
import time

with open('config.json', 'r') as f:
    config = json.load(f)

with open('serviceconfig.json', 'r') as f:
    serviceconfig = json.load(f)

BOT_TOKEN = config['BOT_TOKEN']
JUSTANOTHERPANEL_API_KEY = config['JUSTANOTHERPANEL_API_KEY']
JUSTANOTHERPANEL_API_URL = config['JUSTANOTHERPANEL_API_URL']
EXCHANGE_RATE_API_KEY = config['EXCHANGE_RATE_API_KEY']
EXCHANGE_RATE_API_URL = config['EXCHANGE_RATE_API_URL']
OWNER_ID = config['OWNER_ID']

services = serviceconfig['services']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

last_usage = {service_key: {} for service_key in services}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_connection.start()

@tasks.loop(minutes=5)
async def check_connection():
    try:
        if bot.is_closed():
            await bot.connect()
    except Exception as e:
        print(f"Error during connection check: {e}")

def make_service_command(service_key, service_info):
    async def service_command(ctx, link: str, quantity: int):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("You are not authorized to use this command.")

        user_id = ctx.author.id
        current_time = time.time()
        if user_id in last_usage.get(service_key, {}):
            elapsed = current_time - last_usage[service_key][user_id]
            if elapsed < 60:
                return await ctx.send(f"Please wait {int(60 - elapsed)} seconds before using this command again.")

        service_payload = {
            'key': JUSTANOTHERPANEL_API_KEY,
            'action': 'services'
        }

        try:
            service_response = requests.post(JUSTANOTHERPANEL_API_URL, data=service_payload)
            services_api = service_response.json()
            price_per_1k = None
            for service in services_api:
                if str(service.get("service")) == str(service_info['service_id']):
                    price_per_1k = float(service.get("rate", 0))
                    break

            if price_per_1k is None:
                return await ctx.send("Could not find pricing information for this service.")

            exchange_response = requests.get(EXCHANGE_RATE_API_URL)
            exchange_data = exchange_response.json()
            usd_to_eur = exchange_data['conversion_rates']['EUR']

            price_usd = (price_per_1k / 1000) * quantity
            price_eur = round(price_usd * usd_to_eur, 4)

            class ConfirmView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=30)

                @discord.ui.button(label="✅ Confirm Order", style=discord.ButtonStyle.green)
                async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message("You didn't initiate this command.", ephemeral=True)

                    await interaction.response.defer()

                    order_payload = {
                        'key': JUSTANOTHERPANEL_API_KEY,
                        'action': 'add',
                        'service': service_info['service_id'],
                        'link': link,
                        'quantity': quantity
                    }

                    try:
                        order_response = requests.post(JUSTANOTHERPANEL_API_URL, data=order_payload)
                        result = order_response.json()

                        if 'order' in result:
                            await ctx.send(f"{ctx.author.mention}, order placed! ✅\nAmount: {quantity} {service_key}\nOrder ID: {result['order']}")
                        else:
                            await ctx.send(f"Error placing order: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        await ctx.send(f"API Error: {e}")

                    if service_key not in last_usage:
                        last_usage[service_key] = {}
                    last_usage[service_key][user_id] = current_time
                    self.stop()

                @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.red)
                async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message("You didn't initiate this command.", ephemeral=True)
                    await interaction.response.send_message("Order canceled.", ephemeral=True)
                    self.stop()

            embed = discord.Embed(title=f"{service_info['display_name']} Order Confirmation", color=discord.Color.orange())
            embed.add_field(name="Link", value=link, inline=False)
            embed.add_field(name="Quantity", value=str(quantity), inline=True)
            embed.add_field(name="Estimated Price", value=f"€{price_eur}", inline=True)
            embed.set_footer(text="Confirm within 30 seconds.")

            await ctx.send(embed=embed, view=ConfirmView())

        except Exception as e:
            await ctx.send(f"API Error: {e}")

    return service_command

def register_service_commands():
    for service_key, service_info in services.items():
        command_func = make_service_command(service_key, service_info)
        command_func.__name__ = service_key
        bot.command(name=service_key)(command_func)
        last_usage[service_key] = {}

register_service_commands()

@bot.command(name='help')
async def help_command(ctx):
    if ctx.author.id != OWNER_ID:
        return await ctx.send("You are not authorized to use this command.")

    embed = discord.Embed(title="Bot Help", description="Available commands:", color=discord.Color.blue())
    for service_key, service_info in services.items():
        embed.add_field(name=f"!{service_key} [Link] [Amount]", value=f"Add {service_info['display_name']} with confirmation", inline=False)
    await ctx.send(embed=embed)

bot.run(BOT_TOKEN)