
import asyncio
from cmath import isnan
from distutils.log import ERROR, error
from email import message
import email
from email.utils import make_msgid
from http import client

from multiprocessing.connection import Client
from ssl import create_default_context

from unicodedata import name
from wsgiref import simple_server
from xml.dom.expatbuilder import FragmentBuilderNS
import requests
import json
import discord
from discord.ext import commands, tasks
from datetime import datetime
from itertools import cycle
import datetime
import sqlite3
import random
import time
import schedule


# 여기는 변수 선언
bot = commands.Bot(command_prefix = '=')
isRaidRunning = False


#여기는 함수 선언
def IsUser(id) :  # 서비스에 가입되어있는지 확인하는 함수
    alr_exist = []
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    cur = con.cursor()
    cur.execute("SELECT User_id FROM User_Info WHERE User_id = ?", (id,))
    rows = cur.fetchall()
    for i in rows :
        alr_exist.append(i[0])
    if id not in alr_exist :
        return 0
    elif id in alr_exist :
        return 1
    con.close()

def IsHoldingMon(id) :  # 몬스터를 보유 중인지 확인하는 함수
    alr_exist = []
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    cur = con.cursor()
    cur.execute("SELECT User_id FROM Hold_Info WHERE User_id = ?", (id,))
    rows = cur.fetchall()
    for i in rows :
        alr_exist.append(i[0])
    if id not in alr_exist :
        return 0
    elif id in alr_exist :
        return 1
    con.close()   

def IsRaid(id) :  # 레이드 유저인지 확인하는 함수
    alr_exist = []
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    cur = con.cursor()
    cur.execute("SELECT User_id FROM Raid_Info WHERE User_id = ?", (id,))
    rows = cur.fetchall()
    for i in rows :
        alr_exist.append(i[0])
    if id not in alr_exist :
        return 0
    elif id in alr_exist :
        return 1
    con.close()       

def Reset() :   # 일정 시간마다 각종 일일 제한 횟수를 초기화 시키는 함수
    print("일일제한 리셋!")
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("UPDATE Task_Info SET Do_num = 0")
    cur.execute("UPDATE Raid_Info SET Do_num = 0")
    cur.execute("UPDATE Task_Info SET Mine_num = 0")
    cur.execute("UPDATE Task_Info SET Tk_num = 0")
    cur.execute("UPDATE Task_Info SET Note_num = 0")
    cur.execute("UPDATE Task_Info SET Battle_name = ''")
    cur.execute("UPDATE Task_Info SET Battle_num = 0")


# 봇 스타팅
token = "OTQ0ODY1OTEyMTQ4ODgxNDgw.YhH09A.43jUXqoJMJgrldGzPMLVw1LVSjs"

@bot.event
async def on_ready():
    print("다음으로 로그인합니다 : ")
    print(bot.user.name)
    print(bot.user.id)
    print("==========")
    bot.loop.create_task(task())
    game = discord.Game("트레이너를 탐색")
    await bot.change_presence(status=discord.Status.online, activity=game)


# 자동 실행 변수 및 함수
schedule.every().day.at("00:00").do(Reset)

async def task():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

# 여기서부터 디스코드 동작


@bot.command()
async def 논쨩(ctx) :
    embed = discord.Embed(title = '논쨩은 사랑입니다', description = ':hearts::hearts::hearts::hearts::hearts::hearts::hearts::hearts::hearts:', color = 0xff0000)
    embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMDdfMjc4/MDAxNjQ2NjU2NzUwNjA4.B-hX8_OlruOo_iNS8A6ivmS63MbiisvVnQNi5ZUx9UQg.zuzhkzRfoegnyNL8bXZ7GGHX-sLcy9aZedGfd3ZERVQg.JPEG.devjune92/1632920087_(2).jpg?type=w773")
    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed = embed) 

@bot.command()
async def 가입(ctx) :
    id = ctx.author.id
    nick = ctx.author.name
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    cur = con.cursor()
    isuser = IsUser(id)
    now = datetime.datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
    if isuser == 0 :
        null = 'NULL'
        cur.execute("INSERT INTO User_Info VALUES(?, ?, ?, ?, ?)", (id, nick, '0', nowDatetime, 0))
        cur.execute("INSERT INTO Stat_Info VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (id, nick, 0, 0, 0, 0, 0, null))
        cur.execute("INSERT INTO Task_Info VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, nick, 0, 0, 0, 0, null, null, null))
        embed = discord.Embed(title = ':wave: 가입', description = '성공적으로 라스아이몬 게임 서비스에 가입되셨습니다.', color = 0xffc0cb)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    elif isuser == 1 :
        embed = discord.Embed(title = ':question: 어라?', description = '이미 라스아이몬 게임 서비스에 가입되어 있습니다.', color = 0xff0000)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    con.close()

@bot.command()
async def 스타팅(ctx) :
    id = ctx.author.id
    nick = ctx.author.name
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    isholdingmon = IsHoldingMon(id)
    now = datetime.datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
    if isuser == 1 :
        if isholdingmon == 1 :
            embed = discord.Embed(title = ':man_facepalming: 이런', description = '이미 라스아이몬을 보유중입니다!', color = 0xff0000)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
        elif isholdingmon == 0 :
            dice = random.randint(1, 4)
            cur.execute("INSERT INTO Hold_Info VALUES(?, ?, ?, ?, ?, ?)", (id, nick, dice, 1, nowDatetime, 0))
            cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = ?", (dice,))
            monname = cur.fetchone()
            embed = discord.Embed(title = ':tada: 축하합니다!', description = monname['Mon_name'] + '이(가) 동료가 되었습니다!', color = 0xff0000)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)  
    elif isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)        
    con.close()   


@bot.command()
async def 정보쪽쪽(ctx) :
    id = ctx.author.id
    nick = ctx.author.display_name
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    member = ctx.guild.get_member(id)
    print(ctx.message.author.avatar_url)
    print(ctx.author.avatar_url)
    print(ctx.message.author.default_avatar_url)
    print(ctx.message.guild.id)
    print(ctx.message)
    print(ctx.message.author.guild)
    print(bot.get_guild)
    print(member)
    print(ctx.guild.get_member)
    print(ctx.guild.get_member_named)
    print(ctx.author)

@bot.command()
async def 정보(ctx) :
    id = ctx.author.id
    nick = ctx.author.display_name
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    isholdingmon = IsHoldingMon(id)
    url = f"https://discord.com/api/guilds/{868125325513605120}/members/{id}"
    res = requests.get(url, headers = {
                     "Authorization": f"Bot {token}",
                     "User-Agent":    f"DiscordBot (https://tmp.com, 1.0"})
    data = json.loads(res.content)
    if data['avatar'] is None:
        pfp = ctx.message.author.avatar_url
    else:
        avatar_ext = ("gif"
                      if data['avatar'].startswith("a_")
                      else "png")

        avatar_url = ( "https://cdn.discordapp.com/guilds/" +
                      f"{868125325513605120}/users/{id}/avatars/" +
                      f"{data['avatar']}.{avatar_ext}")
        pfp = avatar_url
    if isuser == 1 :
        if isholdingmon == 1 :
            cur.execute("SELECT * FROM Hold_Info WHERE User_id = ?", (id,))
            mon_hold = cur.fetchone()
            cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = ?", (mon_hold['Mon_id'], ))
            mon = cur.fetchone()
            cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
            user_i = cur.fetchone()
            cur.execute("SELECT * FROM Stat_Info WHERE User_id = ?", (id,))
            stat = cur.fetchone()
            embed=discord.Embed(title=mon['Mon_name'], description=mon['Mon_grade'], color=0x00ff56)
            embed.set_author(name=nick, url="https://lastidolnote.com/", icon_url=(pfp))
            embed.set_image(url=mon['etc1'])
            embed.add_field(name="> 레벨", value=mon_hold['Mon_level'], inline=True)
            embed.add_field(name="> 체력", value=mon['Mon_hp'] + stat['A_hp'], inline=True)
            embed.add_field(name="> 공격", value=mon['Mon_atk'] + stat['A_atk'], inline=True)
            embed.add_field(name="> 방어", value=mon['Mon_def'] + stat['A_def'], inline=True)
            embed.add_field(name="> 민첩", value=mon['Mon_dex'] + stat['A_dex'], inline=True)
            embed.add_field(name="> 행운", value=mon['Mon_luk'] + stat['A_luk'], inline=True)
            embed.add_field(name="> 보유골드", value=user_i['money'], inline=True)
            embed.add_field(name="> 레벨업 토큰", value=user_i['Lvtk'], inline=True)
            embed.set_footer(text="by Mujiseong")
            await ctx.send(embed=embed)
        elif isholdingmon == 0 :
            embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬을 보유하고 있지 않으시군요ㅠㅠ', color = 0xff0000)
            embed.add_field(name="지금 바로 스타팅 라스아이몬을 얻어보세요!", value="명령어 : =스타팅", inline=True)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)            
    elif isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    con.close()

@bot.command()
async def 노트포인트(ctx) : 
    id = ctx.author.id
    nick = ctx.author.display_name
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    url = "https://lastidolnote.com/api/profile.php?author_id=%s"%(id)			#요청을 보낼 url을 입력.
    response = requests.get(url)		#params라는 인자를 사용
    memberserch = response.json()
    pointserch = memberserch['member']['mb_point']
    embed = discord.Embed(title = '라스아이노트 포인트 확인!', description = '%s님이 보유하신 라스아이노트 포인트는 %spt입니다!'%(nick, pointserch), color = 0xff0000)
    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed = embed)
    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
    Task_i = cur.fetchone()
    if Task_i['Note_num'] >= 200 :
        embed = discord.Embed(title = '이미 오늘 할당량을 모두 교환했습니다', description = '내일 다시 이용해주세요', color = 0xff0000)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)     
    else :    
        embed = discord.Embed(title = '라스아이노트 포인트를 골드로 교환할 수 있습니다', description = '라스아이노트 포인트와 라스아이몬 골드는 1:1의 가치를 가집니다\n  \
        하루 교환 가능한 포인트는 200포인트, 현재 교환한 포인트는 %s포인트입니다\n\n교환을 원하시는 포인트를 타이핑, 혹은 "교환취소"를 타이핑해 주세요'%(Task_i['Note_num']), color = 0xff0000)
        embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMDdfMTkx/MDAxNjQ2NjU2OTEwODQ5.tG4u83UtO7ZcLMYIoNvkJsSXDn8wMO3gDzmwzTRZQqAg.Z-REnoDBZ62YcAWEl36HgU9Qgw9joJ9ilBJtDYjWT08g.PNG.devjune92/%EB%9D%BC%EC%8A%A4%EC%95%84%EC%9D%B4%EB%85%B8%ED%8A%B8.png?type=w773")
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
        def CheckAnswer(message) :
            return message.channel == ctx.channel and message.author.id == id   
        message = await bot.wait_for("message", check=CheckAnswer) 
        if message.content == "교환취소" :
            embed = discord.Embed(title = '교환을 취소하였습니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)   
        else :
            if int(message.content) < 0 : 
                embed = discord.Embed(title = '음수는 입력 불가입니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)  
            else :
                if int(pointserch) < int(message.content) :
                    embed = discord.Embed(title = '보유 라스아이노트 포인트가 입력하신 수치보다 적습니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)      
                else :       
                    if int(message.content) > (200 - Task_i['Note_num']) :
                        embed = discord.Embed(title = '하루 교환 가능한 금액을 초과 입력했습니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await ctx.send(embed = embed)    
                    else :              
                        if int(message.content) <= (200 - Task_i['Note_num']) :
                            changepoint = int(message.content)
                            requests.post('https://lastidolnote.com/api/point.php', {'key':'D90vnAkcd5m70Vkd8ab30Gkfds0Xd9gk', 'author_id':'%s'%(id), 'point':'%s'%(changepoint)})
                            cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(changepoint, id))
                            cur.execute("UPDATE Task_Info SET Note_num = Note_num + %s WHERE User_id = %s"%(changepoint, id))
                            embed = discord.Embed(title = '라스아이노트 포인트 %spt를 골드로 전환하였습니다'%(changepoint), description = '다음에 또 이용해주세요!', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)    
                        else :
                            embed = discord.Embed(title = '정확하지 않은 명령어 입력입니다', description = '다음에 또 이용해주세요!', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)    

@bot.command()
async def 토큰구매소(ctx) :
    id = ctx.author.id
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    tk0 = "🐀"  
    tk100 = "🐇"
    tk200 = "🐕"
    tk300 = "🐂"
    tk400 = "🐘"
    tk500 = "🐅"
    tk700 = "🦖"
    tk1000 = "🐉"
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    else :
        embed = discord.Embed(title = '레벨업 토큰구매소에 오신 것을 환영합니다', description = '레벨업 토큰은 1토큰 당 1골드의 값어치를 지니고 있습니다\n해당 토큰을 이용해 레벨업을 진행할 수 있습니다\n  \
        구매를 원하시는 액수를 아래 이모지에서 선택해주세요\n\n%s취소　%sTk100　%sTk200　%sTk300\n%sTk400　%sTk500　%sTk700　%sTk1000'%(tk0, tk100, tk200, tk300, tk400, tk500, tk700, tk1000), color = 0xff0000)
        embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMDhfMTk3/MDAxNjQ2NzIwODIzNjk1.PDLK_SSZg1c53jhXC0q3ar3Q1Toe6csgIOy3PF6Pzk8g.8p2X8roQFmHcZo8ny1_7AjpGvDB8jsGN3R111ZaWLGkg.PNG.devjune92/%ED%86%A0%ED%81%B0%EA%B5%AC%EB%A7%A4%EC%86%8C.png?type=w773")        
        msg = await ctx.channel.send(embed = embed)
        await msg.add_reaction(tk0)
        await msg.add_reaction(tk100)
        await msg.add_reaction(tk200)
        await msg.add_reaction(tk300)
        await msg.add_reaction(tk400)
        await msg.add_reaction(tk500)
        await msg.add_reaction(tk700)
        await msg.add_reaction(tk1000)
        try :
            def ContinueBuyTk(reaction, user) :
                return str(reaction) in [tk0, tk100, tk200, tk300, tk400, tk500, tk700, tk1000] and user.id == id
            reaction, user = await bot.wait_for('reaction_add', check=ContinueBuyTk)
            if (str(reaction)) == tk0 :
                embed = discord.Embed(title = '토큰 구입을 취소합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                con.close()
            else : 
                cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
                user_i = cur.fetchone()   
                if (str(reaction)) == tk100 :  
                    buy_tk = 100 
                elif (str(reaction)) == tk200 :
                    buy_tk = 200 
                elif (str(reaction)) == tk300 : 
                    buy_tk = 300   
                elif (str(reaction)) == tk400 :  
                    buy_tk = 400  
                elif (str(reaction)) == tk500 :   
                    buy_tk = 500 
                elif (str(reaction)) == tk700 :  
                    buy_tk = 700  
                elif (str(reaction)) == tk1000 :     
                    buy_tk = 1000
                if  user_i['money'] < buy_tk :
                    embed = discord.Embed(title = '😓소지골드가 부족합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)
                    con.close()
                else :
                    cur.execute("UPDATE User_Info SET money = money - %s WHERE User_id = %s"%(buy_tk, id))
                    cur.execute("UPDATE User_Info SET LvTk = LvTk + %s WHERE User_id = %s"%(buy_tk, id))
                    cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
                    user_i = cur.fetchone() 
                    embed = discord.Embed(title = '토큰을 %s개 구입합니다!'%(buy_tk), description = '보유 토큰이 %s개가 되었습니다'%(user_i['LvTk']), color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)
                    con.close()
        except : pass       
            
@bot.command()
async def 레벨업(ctx) :
    id = ctx.author.id
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    isholdingmon = IsHoldingMon(id)
    ok = "⭕"
    no = "❌"
    cur.execute("SELECT * FROM Hold_Info WHERE User_id = ?", (id,))
    mon_hold = cur.fetchone()
    cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = ?", (mon_hold['Mon_id'],))
    mon = cur.fetchone()
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    elif isuser == 1 :
        if isholdingmon == 0 :
            embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬을 보유하고 있지 않으시군요ㅠㅠ', color = 0xff0000)
            embed.add_field(name="지금 바로 스타팅 라스아이몬을 얻어보세요!", value="명령어 : =스타팅", inline=True)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
        elif mon_hold['Mon_level'] == mon['Mon_gradeN'] * 10 :
            embed = discord.Embed(title = '레벨업 진행 불가능', description = '보유하신 라스아이몬이 최고레벨입니다!', color = 0xff0000)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
        else :
            cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = ?", (mon_hold['Mon_id'],))
            mon = cur.fetchone()
            cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
            user_i = cur.fetchone()
            cur.execute("SELECT * FROM Stat_Info WHERE User_id = ?", (id,))
            stat = cur.fetchone()
            need_Tk = (mon_hold['Mon_level'] * 100 * mon['Mon_gradeN'])
            if mon['Mon_gradeN'] == 1 :
                upchance = 100
            else :    
                upchance = 100 - (mon_hold['Mon_level'] * 2 + 2)
            get_stat = mon['Mon_gradeN'] + 2
            embed = discord.Embed(title = '레벨업 진행소에 오신걸 환영합니다',
            description = '보유하신 라스아이몬은 %s이며 레벨은 %s입니다\n다음 레벨로 강화시도 시 필요 토큰은 %s개입니다\n레벨업 성공시 스탯포인트 %s을 얻게되며\n현재 레벨의 레벨업 확률은 %s%%입니다  \
            \n\n%s진행　　%s취소'%(mon['Mon_name'], mon_hold['Mon_level'], need_Tk, get_stat, upchance, ok, no), color = 0xff0000)
            embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMDhfMTQ1/MDAxNjQ2NzIxMjk4MjY3.HDCEBd7DW_nEIQqkofvh-rBuGL_hu7_L7HiH_f2xc5Eg.ftUjS-LspFa4Z5j7n4fNRQymfgHYPxVZWQ4DgHiurR8g.PNG.devjune92/%E2%80%94Pngtree%E2%80%94level_up_neon_vector_icon_5980599.png?type=w773")        
            msg = await ctx.channel.send(embed = embed)
            await msg.add_reaction(ok)
            await msg.add_reaction(no)
            try :
                def ContinueLvUp(reaction, user) :
                    return str(reaction) in [ok, no] and user.id == id
                reaction, user = await bot.wait_for('reaction_add', check=ContinueLvUp)
                if (str(reaction)) == no :
                    embed = discord.Embed(title = '레벨업 진행을 취소합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)
                    con.close()
                elif (str(reaction)) == ok :
                    if need_Tk > user_i['LvTk'] :
                        embed = discord.Embed(title = '😓보유 토큰이 부족합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await ctx.send(embed = embed)
                        con.close()
                    else :
                        tukau_Tk = user_i['LvTk'] - need_Tk
                        seikai_chek = random.randint(1,100)
                        cur.execute("UPDATE User_Info SET LvTk = ? WHERE User_id = ?", (tukau_Tk, id))
                        if seikai_chek > upchance :
                            embed = discord.Embed(title = '🎲주사위를 굴립니다!', description = '데구르르르르르르르르....', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            await asyncio.sleep(5)  
                            embed = discord.Embed(title = '😱레벨업 실패!', description = '다음번에는 성공하시길 빌어요', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            con.close()
                        elif seikai_chek == 100 and mon_hold['Mon_level'] < 9 :
                            stat_point = (mon['Mon_gradeN'] + 2) * 2
                            next_level = mon_hold['Mon_level'] + 2
                            cur.execute("UPDATE Hold_Info SET Mon_level = ? WHERE User_id = ?", (next_level, id))
                            embed = discord.Embed(title = '🎲주사위를 굴립니다!', description = '데구르르르르르르르르....', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            await asyncio.sleep(5)
                            embed = discord.Embed(title = '!!!!!!!!!!!!!!!', description = '%s의 상태가 심상치 않다!'%(mon['Mon_name']), color = 0xff0000)
                            await ctx.send(embed = embed)
                            await asyncio.sleep(2)
                            embed = discord.Embed(title = '🎉🎉레벨업 대성공!🎉🎉', description = '%s의 레벨이 %s로 상승했습니다!'%(mon['Mon_name'], next_level), color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            while stat_point != 0 :
                                embed = discord.Embed(title = '남은 스탯포인트 %s'%(stat_point), description = '원하시는 스탯을 선택해주세요\n되돌릴 수 없으니 신중하게 선택하시길..\n\n  \
                                💪체력(5상승)　🗡️공격\n🛡️방어　🦵민첩　🃏행운', color = 0xff0000)
                                msg = await ctx.channel.send(embed = embed)
                                await msg.add_reaction("💪")
                                await msg.add_reaction("🗡️")
                                await msg.add_reaction("🛡️")
                                await msg.add_reaction("🦵")
                                await msg.add_reaction("🃏")
                                try :
                                    def WhatUChoice(reaction, user) :
                                        return str(reaction) in ["💪", "🗡️", "🛡️", "🦵", "🃏"] and user != bot.user and user.id == id
                                    reaction, user = await bot.wait_for('reaction_add', check=WhatUChoice)
                                    if (str(reaction)) == "🗡️" :  
                                        embed = discord.Embed(title = '공격을 선택하셨습니다', description = '%s의 공격이 1 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_atk = A_atk + 1 WHERE User_id = %s"%(id))
                                    elif (str(reaction)) == "💪" :  
                                        embed = discord.Embed(title = '체력을 선택하셨습니다', description = '%s의 체력이 5 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_hp = A_hp + 5 WHERE User_id = %s"%(id))                                       
                                    elif (str(reaction)) == "🛡️" :  
                                        embed = discord.Embed(title = '방어를 선택하셨습니다', description = '%s의 방어가 1 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_def = A_def + 1 WHERE User_id = %s"%(id))                                      
                                    elif (str(reaction)) == "🦵" :  
                                        embed = discord.Embed(title = '민첩을 선택하셨습니다', description = '%s의 민첩이 1 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_dex = A_dex + 1 WHERE User_id = %s"%(id))                                         
                                    elif (str(reaction)) == "🃏" :  
                                        embed = discord.Embed(title = '행운을 선택하셨습니다', description = '%s의 행운이 1 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_luk = A_luk + 1 WHERE User_id = %s"%(id))
                                except : pass        
                        else :
                            stat_point = mon['Mon_gradeN'] + 2
                            next_level = mon_hold['Mon_level'] + 1
                            cur.execute("UPDATE Hold_Info SET Mon_level = ? WHERE User_id = ?", (next_level, id))
                            embed = discord.Embed(title = '🎲주사위를 굴립니다!', description = '데구르르르르르르르르....', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            await asyncio.sleep(5)
                            embed = discord.Embed(title = '🎉레벨업 성공!🎉', description = '%s의 레벨이 %s로 상승했습니다!'%(mon['Mon_name'], next_level), color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            while stat_point != 0 :
                                embed = discord.Embed(title = '남은 스탯포인트 %s'%(stat_point), description = '원하시는 스탯을 선택해주세요\n되돌릴 수 없으니 신중하게 선택하시길..\n\n  \
                                💪체력(5상승)　🗡️공격\n🛡️방어　🦵민첩　🃏행운', color = 0xff0000)
                                msg = await ctx.channel.send(embed = embed)
                                await msg.add_reaction("💪")
                                await msg.add_reaction("🗡️")
                                await msg.add_reaction("🛡️")
                                await msg.add_reaction("🦵")
                                await msg.add_reaction("🃏")
                                try :
                                    def WhatUChoice(reaction, user) :
                                        return str(reaction) in ["💪", "🗡️", "🛡️", "🦵", "🃏"] and user != bot.user and user.id == id
                                    reaction, user = await bot.wait_for('reaction_add', check=WhatUChoice)
                                    if (str(reaction)) == "🗡️" :  
                                        embed = discord.Embed(title = '공격을 선택하셨습니다', description = '%s의 공격이 1 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_atk = A_atk + 1 WHERE User_id = %s"%(id))
                                    elif (str(reaction)) == "💪" :  
                                        embed = discord.Embed(title = '체력을 선택하셨습니다', description = '%s의 체력이 5 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_hp = A_hp + 5 WHERE User_id = %s"%(id))                                       
                                    elif (str(reaction)) == "🛡️" :  
                                        embed = discord.Embed(title = '방어를 선택하셨습니다', description = '%s의 방어가 1 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_def = A_def + 1 WHERE User_id = %s"%(id))                                      
                                    elif (str(reaction)) == "🦵" :  
                                        embed = discord.Embed(title = '민첩을 선택하셨습니다', description = '%s의 민첩이 1 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_dex = A_dex + 1 WHERE User_id = %s"%(id))                                         
                                    elif (str(reaction)) == "🃏" :  
                                        embed = discord.Embed(title = '행운을 선택하셨습니다', description = '%s의 행운이 1 상승했습니다!'%(mon['Mon_name']), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        stat_point -= 1
                                        cur.execute("UPDATE Stat_Info SET A_luk = A_luk + 1 WHERE User_id = %s"%(id))                                              
                                except : pass
            except : pass   
    con.close         


@bot.command()
async def 진화(ctx) :    
    id = ctx.author.id
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    isholdingmon = IsHoldingMon(id)
    ok = "⭕"
    no = "❌"
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    elif isuser == 1 :    
        if isholdingmon == 0 :
            embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬을 보유하고 있지 않으시군요ㅠㅠ', color = 0xff0000)
            embed.add_field(name="지금 바로 스타팅 라스아이몬을 얻어보세요!", value="명령어 : =스타팅", inline=True)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
        elif isholdingmon == 1 :
            cur.execute("SELECT * FROM Hold_Info WHERE User_id = ?", (id,))
            mon_hold = cur.fetchone()
            cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = ?", (mon_hold['Mon_id'],))
            mon = cur.fetchone()
            cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
            user_i = cur.fetchone()
            use_money = (mon['Mon_gradeN'] * 1000 / 2) + ((mon['Mon_gradeN'] - 1) * 500)
            IsHighestMonGrade = False
            IsLowestMonGrade = False
            if mon['Mon_gradeN'] == 1 :
                IsLowestMonGrade = True
            elif mon['Mon_gradeN'] == 5 :
                IsHighestMonGrade = True
            if IsHighestMonGrade == True :
                embed = discord.Embed(title = ':man_facepalming: 이런', description = '최고 등급의 라스아이몬을 보유하고 계십니다!', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                con.close()
            else :
                embed = discord.Embed(title = '진화소에 오신 것을 환영합니다!', description = '현재 보유 라스아이몬은 %s이며 %s입니다\n진화시 %s골드가 소모됩니다'%(mon['Mon_name'], mon['Mon_grade'], use_money), color = 0xff0000)
                if IsLowestMonGrade == True :
                    embed.add_field(name="보유 라스아이몬이 최하급이므로 하급 라스아이몬 중 랜덤으로 진화됩니다", value="오시가 뽑히길 기도합니다🙏", inline=True)
                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMDhfMTU3/MDAxNjQ2NzE5Mjc3MDc2.4BRiGKUWd4eodBruitovG6B_slrId3K2GeVWS7zXE94g.hpVGNWhpwaT-nPbx19MrM5vfk-KPYSVVelaOohNA9rgg.PNG.devjune92/%EC%A7%84%ED%99%94.png?type=w773")
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                embed = discord.Embed(title = '진화 하시겠습니까?', description = '%s진화　　%s다음에'%(ok, no), color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                msg = await ctx.channel.send(embed = embed)
                await msg.add_reaction(ok)
                await msg.add_reaction(no)  
                try :
                    def ContinueTask(reaction, user) :
                        return str(reaction) in [ok, no] and user.id == id
                    reaction, user = await bot.wait_for('reaction_add', check=ContinueTask)
                    if (str(reaction)) == no :
                        embed = discord.Embed(title = '진화 진행을 취소합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await ctx.send(embed = embed)
                        con.close()
                    elif (str(reaction)) == ok :
                        if mon_hold['mon_level'] != mon['Mon_gradeN'] * 10 :
                            embed = discord.Embed(title = '😓라스아이몬의 레벨이 부족합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            con.close()
                        elif user_i['money'] < use_money :
                            embed = discord.Embed(title = '😓소지골드가 부족합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            con.close()
                        else :
                            cur.execute("UPDATE User_Info SET money = money - %s WHERE User_id = %s"%(use_money, id)) 
                            if IsLowestMonGrade == True :
                                new_mon = random.randint(5, 37)
                            else :
                                new_mon = mon_hold['Mon_id'] + 33
                            cur.execute("UPDATE Hold_Info SET Mon_level = 1 WHERE User_id = %s"%(id)) 
                            cur.execute("UPDATE Hold_Info SET Mon_id = %s WHERE User_id = %s"%(new_mon, id))
                            cur.execute("UPDATE Stat_Info SET A_hp = 0 WHERE User_id = %s"%(id))
                            cur.execute("UPDATE Stat_Info SET A_atk = 0 WHERE User_id = %s"%(id)) 
                            cur.execute("UPDATE Stat_Info SET A_def = 0 WHERE User_id = %s"%(id)) 
                            cur.execute("UPDATE Stat_Info SET A_dex = 0 WHERE User_id = %s"%(id)) 
                            cur.execute("UPDATE Stat_Info SET A_luk = 0 WHERE User_id = %s"%(id))
                            cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = %s"%(new_mon))
                            mon = cur.fetchone()
                            embed = discord.Embed(title = '진화 시작!!', description = '두구두구두구두구두구......', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            await asyncio.sleep(5) 
                            embed = discord.Embed(title = '라스아이몬이 %s(%s)로 진화했습니다!'%(mon['Mon_name'], mon['Mon_grade']), description = '자세한 내용은 =정보를 참고하세요', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            con.close()     
                except : pass        

@bot.command()
async def 리롤(ctx) :  
    id = ctx.author.id
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    isholdingmon = IsHoldingMon(id)
    ok = "⭕"
    no = "❌"
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    elif isuser == 1 :    
        if isholdingmon == 0 :
            embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬을 보유하고 있지 않으시군요ㅠㅠ', color = 0xff0000)
            embed.add_field(name="지금 바로 스타팅 라스아이몬을 얻어보세요!", value="명령어 : =스타팅", inline=True)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
        elif isholdingmon == 1 :
            cur.execute("SELECT * FROM Hold_Info WHERE User_id = ?", (id,))
            mon_hold = cur.fetchone()
            cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = ?", (mon_hold['Mon_id'],))
            mon = cur.fetchone()
            cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
            user_i = cur.fetchone()
            use_money = (mon['Mon_gradeN'] - 1) * 300
            IsLowestMonGrade = mon['Mon_gradeN'] == 1
            refund = int((mon_hold['Mon_level'] - 1) * mon_hold['Mon_level'] / 2 * 100 * mon['Mon_gradeN'])
            if mon_hold['Re_num'] == 31 :
                embed = discord.Embed(title = ':man_facepalming: 이런', description = '31회 실패하셨군요\n관리자에게 문의하세요!', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                con.close()
            elif IsLowestMonGrade == True :
                embed = discord.Embed(title = ':man_facepalming: 이런', description = '최하급은 리롤을 할 수 없습니다', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                con.close()
            else :
                embed = discord.Embed(title = '리롤은 보유한 라스아이몬을 다른 라스아이몬으로 바꾸는 서비스입니다', description = '현재 보유 라스아이몬은 %s이며 %s입니다\n리롤시 %s골드가 소모됩니다\n  \
                31회 리롤 실패시 라스아이몬 선택권 지급!\n현재 리롤 횟수는 %s회 입니다'%(mon['Mon_name'], mon['Mon_grade'], use_money, mon_hold['Re_num']), color = 0xff0000)
                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMDhfMTAg/MDAxNjQ2NzE4OTQyNjM2.Pi3s_egWj4I4mYQq3lgdILmUAe_yqqCw4dGbZxQ2nZkg.yTQH_evLoi61z3XjEYlMISoCnR28paUnzThzOkkLf7Yg.PNG.devjune92/%EB%A6%AC%EB%A1%A4.png?type=w773")
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                embed = discord.Embed(title = '리롤 하시겠습니까?\n리롤 시 해당 레벨업 까지의 레벨업 토큰은 환급됩니다', description = '%s리롤　　%s다음에'%(ok, no), color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                msg = await ctx.channel.send(embed = embed)
                await msg.add_reaction(ok)
                await msg.add_reaction(no)  
                try :
                    def ContinueTask(reaction, user) :
                        return str(reaction) in [ok, no] and user.id == id
                    reaction, user = await bot.wait_for('reaction_add', check=ContinueTask)
                    if (str(reaction)) == no :
                        embed = discord.Embed(title = '리롤 진행을 취소합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await ctx.send(embed = embed)
                        con.close()
                    elif (str(reaction)) == ok :
                        if user_i['money'] < use_money :
                            embed = discord.Embed(title = '😓소지골드가 부족합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            con.close()
                        else :
                            cur.execute("UPDATE User_Info SET money = money - %s WHERE User_id = %s"%(use_money, id)) 
                            new_mon = mon_hold['Mon_id']
                            Front_num = (mon['Mon_gradeN'] - 2) * 33 + 5 
                            End_num = (mon['Mon_gradeN'] - 2) * 32 + mon['Mon_gradeN'] + 35 
                            while new_mon == mon_hold['Mon_id'] :
                                new_mon = random.randint(Front_num, End_num)   
                            cur.execute("UPDATE User_Info SET LvTk = LvTk + %s WHERE User_id = %s"%(refund, id))    
                            cur.execute("UPDATE Hold_Info SET Mon_level = 1 WHERE User_id = %s"%(id)) 
                            cur.execute("UPDATE Hold_Info SET Re_num = Re_num + 1 WHERE User_id = %s"%(id)) 
                            cur.execute("UPDATE Hold_Info SET Mon_id = %s WHERE User_id = %s"%(new_mon, id))
                            cur.execute("UPDATE Stat_Info SET A_hp = 0 WHERE User_id = %s"%(id))
                            cur.execute("UPDATE Stat_Info SET A_atk = 0 WHERE User_id = %s"%(id)) 
                            cur.execute("UPDATE Stat_Info SET A_def = 0 WHERE User_id = %s"%(id)) 
                            cur.execute("UPDATE Stat_Info SET A_dex = 0 WHERE User_id = %s"%(id)) 
                            cur.execute("UPDATE Stat_Info SET A_luk = 0 WHERE User_id = %s"%(id))
                            cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = %s"%(new_mon))
                            mon = cur.fetchone()
                            embed = discord.Embed(title = '리롤 시작!!', description = '두구두구두구두구두구......', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            await asyncio.sleep(5) 
                            embed = discord.Embed(title = '라스아이몬이 %s(%s)로 변경되었습니다!'%(mon['Mon_name'], mon['Mon_grade']), description = '%s토큰이 환급되었습니다\n자세한 내용은 =정보를 참고하세요'%(refund), color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            con.close()     
                except : pass        

@bot.command()
async def 슬롯(ctx) :    
    id = ctx.author.id
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)  
    nobet = "😓"   
    bet0 = "🎮" 
    bet10 = "😁"
    bet50 = "🎃"
    bet100 = "😈"
    bet250 = "💀"
    bet500 = "👹"
    slotEnd = 0
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    else :
        cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
        user_i = cur.fetchone()
        embed = discord.Embed(title = '라스아이 슬롯에 오신 것을 환영합니다!', description = '슬롯을 돌려 대박을 노려보세요!\n  \
        자세한 내용은 "=슬롯도움말" 을 참고!\n\n%sNo bet　%sbet 0G　%sbet 10G　%sbet 50G\n%sbet 100G　%sbet 250G　%sbet 500G'%(nobet, bet0, bet10, bet50, bet100, bet250, bet500), color = 0xff0000)
        embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMDdfMTg1/MDAxNjQ2NjU5ODE3NDU3.dp3aQr7ow7pL2kTUmUcXa5ysri2HUxTh7zSSsr9fHQ8g.R7fHs2tnc_5huQ-8jmHQjfWEYCS3jDusIgb7zAF30pMg.JPEG.devjune92/%EC%8A%AC%EB%A1%AF.jpeg?type=w773")
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        msg = await ctx.channel.send(embed = embed)
        await msg.add_reaction(nobet)
        await msg.add_reaction(bet0)
        await msg.add_reaction(bet10) 
        await msg.add_reaction(bet50)
        await msg.add_reaction(bet100)
        await msg.add_reaction(bet250)
        await msg.add_reaction(bet500)
        try :
            def ContinueTask(reaction, user) :
                return str(reaction) in [nobet, bet0, bet10, bet50, bet100, bet250, bet500] and user.id == id
            reaction, user = await bot.wait_for('reaction_add', check=ContinueTask)
            if (str(reaction)) == nobet :
                embed = discord.Embed(title = '라스아이 슬롯을 종료합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                con.close()
            elif (str(reaction)) == bet0 :
                isBetGold = 0
                nobetgame = 1    
            elif (str(reaction)) == bet10 :
                isBetGold = 10
            elif (str(reaction)) == bet50 :
                isBetGold = 50
            elif (str(reaction)) == bet100 :
                isBetGold = 100      
            elif (str(reaction)) == bet250 :
                isBetGold = 250
            elif (str(reaction)) == bet500 :
                isBetGold = 500
            if isBetGold > user_i['money'] :
                embed = discord.Embed(title = '😓소지골드가 부족합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                con.close()
            else :
                cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
                user_i = cur.fetchone()
                if isBetGold > user_i['money'] :
                    return
                else :    
                    cur.execute("UPDATE User_Info SET money = money - %s WHERE User_id = %s"%(isBetGold, id))
                    while slotEnd == 0 :
                        cur.execute("UPDATE Casino_Info SET Count = Count + 1 WHERE Machine_id = 1")
                        cur.execute("SELECT * FROM Casino_Info WHERE Machine_id = 1")
                        Casino_i = cur.fetchone()
                        prize = isBetGold
                        slotEnd = 1
                        bingoline = 0
                        slot1more = 0
                        isJackpot = 0
                        emojis = "⏳⏳⏳⏳⏳🍒🍒🍒🍒🍒🍒🍒🍒🍒🍉🍉🍉🍉🍉🍉🍉🍉🍉🔔🔔🔔🔔🔔🔔🔔💰💰💰💰💰💰💎💎💎💎💎👑👑👑👑🗼🗼🗼🎰🎰"
                        emojis1 = "⏳🍒🍒🍉🔔"
                        emojis2 = "💰⏳🍉🍉🔔"
                        emojis3 = "⏳🍒🍉"
                        emojis4 = "🍒🎰"
                        emojis5 = "🍒💰"
                        emojis6 = "🍒⏳"
                        a = random.choice(emojis) ; b = random.choice(emojis) ; c = random.choice(emojis) ; d = random.choice(emojis) ; e = random.choice(emojis)
                        f = random.choice(emojis) ; g = random.choice(emojis) ; h = random.choice(emojis) ; i = random.choice(emojis)
                        if Casino_i['Count'] == 10 or Casino_i['Count'] == 70 or Casino_i['Count'] == 170 or Casino_i['Count'] == 190 :
                            a = random.choice(emojis1) ; b = random.choice(emojis1) ; c = random.choice(emojis1)
                            d = random.choice(emojis1) ; f = random.choice(emojis1) ; g = random.choice(emojis1)
                            h = random.choice(emojis1) ; i = random.choice(emojis1)
                        if Casino_i['Count'] == 40 or Casino_i['Count'] == 120 :
                            a = random.choice(emojis2) ; b = random.choice(emojis2) ; c = random.choice(emojis2)
                            d = random.choice(emojis2) ; f = random.choice(emojis2) ; g = random.choice(emojis2)
                            h = random.choice(emojis2) ; i = random.choice(emojis2)   
                        if Casino_i['Count'] == 25 :
                            a = "💎" ; b = "💎" ; c = "💎" ; e = random.choice(emojis3)
                            f = random.choice(emojis4); g = random.choice(emojis5)
                        if Casino_i['Count'] == 175 :
                            g = "💎" ; h = "💎" ; i = "💎" ; e = random.choice(emojis3)
                            f = random.choice(emojis4); a = random.choice(emojis5)   
                        if Casino_i['Count'] == 50 or Casino_i['Count'] == 150 :
                            g = "👑" ; h = "👑" ; i = "👑" ; e = random.choice(emojis6) ; f = "👑" ; g = random.choice(emojis6)
                        if Casino_i['Count'] == 100 :
                            a = "🗼" ; b = "🗼" ; c = "🗼" ; e = "🍉" ; f = "🗼" ; g = random.choice(emojis6) 
                        if Casino_i['Count'] == 200 :
                            g = "🎰" ; h = "🎰" ; i = "🎰" ; e = random.choice(emojis6) ; f = "👑" ; g = random.choice(emojis6)
                            cur.execute("UPDATE Casino_Info SET Count = 0 WHERE Machine_id = 1")
                        embed = discord.Embed(color=1768431, title=f"{ctx.bot.user.name}' Casino | Slots", type="rich")
                        embed.add_field(name="---------------------------\n| 🍀  [  ]  [  ]  [  ]  🍀 |\n---------------------------", value="_ _", inline=False)
                        embed.add_field(name="---------------------------\n| 🍀  [  ]  [  ]  [  ]  🍀 |\n---------------------------", value="_ _", inline=False)
                        embed.add_field(name="---------------------------\n| 🍀  [  ]  [  ]  [  ]  🍀 |\n---------------------------", value="_ _")
                        botMsg = await ctx.send(embed=embed)
                        await asyncio.sleep(1.5)

                        embed.set_field_at(0, name=f"---------------------------\n| 🍀  {a}  [  ]  [  ]  🍀 |\n---------------------------", value="_ _", inline=False)
                        embed.set_field_at(1, name=f"---------------------------\n| 🍀  {d}  [  ]  [  ]  🍀 |\n---------------------------", value="_ _", inline=False)
                        embed.set_field_at(2, name=f"---------------------------\n| 🍀  {g}  [  ]  [  ]  🍀 |\n---------------------------", value="_ _")
                        await botMsg.edit(embed=embed)
                        await asyncio.sleep(1.5)

                        embed.set_field_at(0, name=f"---------------------------\n| 🍀  {a}  {b}  [  ]  🍀 |\n---------------------------", value="_ _", inline=False)
                        embed.set_field_at(1, name=f"---------------------------\n| 🍀  {d}  {e}  [  ]  🍀 |\n---------------------------", value="_ _", inline=False)
                        embed.set_field_at(2, name=f"---------------------------\n| 🍀  {g}  {h}  [  ]  🍀 |\n---------------------------", value="_ _")
                        await botMsg.edit(embed=embed)
                        await asyncio.sleep(1.5)

                        embed.set_field_at(0, name=f"---------------------------\n| 🍀  {a}  {b}  {c}  🍀 |\n---------------------------", value="_ _", inline=False)
                        embed.set_field_at(1, name=f"---------------------------\n| 🍀  {d}  {e}  {f}  🍀 |\n---------------------------", value="_ _", inline=False)
                        embed.set_field_at(2, name=f"---------------------------\n| 🍀  {g}  {h}  {i}  🍀 |\n---------------------------", value="_ _")
                        await botMsg.edit(embed=embed)

                        #slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"
                        embed.color = discord.Color(0x23f518)

                        if a == b == c :  # 1행
                            if a == "🍒" :
                                prize = prize * 2
                            elif a == "🍉" : 
                                prize = prize * 3
                            elif a == "🔔" : 
                                prize = prize * 4
                            elif a == "💰" : 
                                prize = prize * 5
                            elif a == "💎" : 
                                prize = prize * 7
                            elif a == "👑" : 
                                prize = prize * 10
                            elif a == "🗼" : 
                                prize = prize * 30
                            elif a == "🎰" : 
                                prize = prize * 50
                                isJackpot = 1
                            else :
                                slot1more = 1    
                            bingoline += 1
                        if d == e == f :  # 2행
                            if d == "🍒" :
                                prize = prize * 2
                            elif d == "🍉" : 
                                prize = prize * 3
                            elif d == "🔔" : 
                                prize = prize * 4 
                            elif d == "💰" : 
                                prize = prize * 5
                            elif d == "💎" : 
                                prize = prize * 7
                            elif d == "👑" : 
                                prize = prize * 10
                            elif d == "🗼" : 
                                prize = prize * 30 
                            elif d == "🎰" : 
                                prize = prize * 50
                                isJackpot = 1
                            else :
                                slot1more = 1    
                            bingoline += 1
                        if g == h == i :  # 3행
                            if g == "🍒" :
                                prize = prize * 2
                            elif g == "🍉" : 
                                prize = prize * 3
                            elif g == "🔔" : 
                                prize = prize * 4  
                            elif g == "💰" : 
                                prize = prize * 5
                            elif g == "💎" : 
                                prize = prize * 7
                            elif g == "👑" : 
                                prize = prize * 10
                            elif g == "🗼" : 
                                prize = prize * 30 
                            elif g == "🎰" : 
                                prize = prize * 50
                                isJackpot = 1
                            else :
                                slot1more = 1    
                            bingoline += 1
                        if a == d == g :  # 1열
                            if a == "🍒" :
                                prize = prize * 2
                            elif a == "🍉" : 
                                prize = prize * 3
                            elif a == "🔔" : 
                                prize = prize * 4   
                            elif a == "💰" : 
                                prize = prize * 5
                            elif a == "💎" : 
                                prize = prize * 7
                            elif a == "👑" : 
                                prize = prize * 10
                            elif a == "🗼" : 
                                prize = prize * 30
                            elif a == "🎰" : 
                                prize = prize * 50
                                isJackpot = 1
                            else :
                                slot1more = 1    
                            bingoline += 1
                        if b == e == h :  # 2열
                            if b == "🍒" :
                                prize = prize * 2
                            elif b == "🍉" : 
                                prize = prize * 3
                            elif b == "🔔" : 
                                prize = prize * 4   
                            elif b == "💰" : 
                                prize = prize * 5
                            elif b == "💎" : 
                                prize = prize * 7
                            elif b == "👑" : 
                                prize = prize * 10
                            elif b == "🗼" : 
                                prize = prize * 30  
                            elif b == "🎰" : 
                                prize = prize * 50
                                isJackpot = 1
                            else :
                                slot1more = 1    
                            bingoline += 1
                        if c == f == i :  # 3열
                            if c == "🍒" :
                                prize = prize * 2
                            elif c == "🍉" : 
                                prize = prize * 3
                            elif c == "🔔" : 
                                prize = prize * 4  
                            elif c == "💰" : 
                                prize = prize * 5
                            elif c == "💎" : 
                                prize = prize * 7
                            elif c == "👑" : 
                                prize = prize * 10
                            elif c == "🗼" : 
                                prize = prize * 30  
                            elif c == "🎰" : 
                                prize = prize * 50
                                isJackpot = 1
                            else :
                                slot1more = 1    
                            bingoline += 1
                        if a == e == i :  # 좌대각
                            if a == "🍒" :
                                prize = prize * 2
                            elif a == "🍉" : 
                                prize = prize * 3
                            elif a == "🔔" : 
                                prize = prize * 4   
                            elif a == "💰" : 
                                prize = prize * 5
                            elif a == "💎" : 
                                prize = prize * 7
                            elif a == "👑" : 
                                prize = prize * 10
                            elif a == "🗼" : 
                                prize = prize * 30  
                            elif a == "🎰" : 
                                prize = prize * 50
                                isJackpot = 1
                            else :
                                slot1more = 1    
                            bingoline += 1
                        if c == e == g :  # 우대각
                            if c == "🍒" :
                                prize = prize * 2
                            elif c == "🍉" : 
                                prize = prize * 3
                            elif c == "🔔" : 
                                prize = prize * 4   
                            elif c == "💰" : 
                                prize = prize * 5
                            elif c == "💎" : 
                                prize = prize * 7
                            elif c == "👑" : 
                                prize = prize * 10
                            elif c == "🗼" : 
                                prize = prize * 30  
                            elif c == "🎰" : 
                                prize = prize * 50
                                isJackpot = 1
                            else :
                                slot1more = 1
                            bingoline += 1
                        if bingoline == 0 :
                            embed = discord.Embed(title = '당첨라인이 없습니다', description = '라스아이 슬롯을 종료합니다', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            cur.execute("UPDATE Casino_Info SET Profit = Profit + %s WHERE Machine_id = 1"%(isBetGold))
                            slotEnd = 1
                            break
                        elif bingoline != 0 :
                            embed = discord.Embed(title = '잠시만 기다려 주세요', description = '결과를 정산중입니다', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            await asyncio.sleep(5)
                            if isJackpot == 1 :
                                embed = discord.Embed(title = '🎰🎰🎰🎰🎰🎰🎰🎰🎰🎰\n🎰🎰　JACKPOT　🎰🎰\n🎰🎰🎰🎰🎰🎰🎰🎰🎰🎰', description = '_ _', color = 0xff0000)
                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                await ctx.send(embed = embed)
                                await asyncio.sleep(5)
                            if slot1more == 1 :
                                embed = discord.Embed(title = '당첨라인 중 ⏳라인이 있습니다!', description = '슬롯이 1회 더 돌아갑니다!', color = 0xff0000)
                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                await ctx.send(embed = embed)
                                await asyncio.sleep(1)    
                                slotEnd = 0
                            if prize > isBetGold or isBetGold == 0 :
                                casino_loss = prize - isBetGold
                                embed = discord.Embed(title = '🎉🎉%s라인 당첨!🎉🎉'%(bingoline), description = '당첨금으로 %s골드를 획득하셨습니다!'%(prize), color = 0xff0000)
                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                await ctx.send(embed = embed)
                                cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(prize, id))
                                cur.execute("UPDATE Casino_Info SET Loss = Loss + %s WHERE Machine_id = 1"%(casino_loss))
                                await asyncio.sleep(1)                                             
        except : pass    

@bot.command()
async def 슬롯도움말(ctx) :
    embed = discord.Embed(title = '라스아이 슬롯 도움말입니다', description = '도박이 아닌 놀이로 즐겨주세요👍', color = 0xff0000)
    embed.add_field(name="행이나 열, 대각선이 같은 이모지일때 당첨이 됩니다.\n당첨 시 배율은 아래와 같습니다", value="🍒🍒🍒 　: 　Bet Gold의 2배\n🍉🍉🍉 　: 　Bet Gold의 3배\n  \
    🔔🔔🔔　 :　 Bet Gold의 4배\n💰💰💰 　:　 Bet Gold의 5배\n💎💎💎　 :　 Bet Gold의 7배\n👑👑👑　 :　 Bet Gold의 10배\n🗼🗼🗼　 :　 Bet Gold의 30배\n🎰🎰🎰 　:　 Bet Gold의 50배\n⏳⏳⏳ 　: 　추가 1회 슬롯", inline=True)
    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed = embed)

@bot.command()
async def 쿠지(ctx) :  
    id = ctx.author.id
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    isholdingmon = IsHoldingMon(id)
    ok = "⭕"
    no = "❌"
    casino_profit = 0
    casino_loss = 0
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    elif isuser == 1 :    
        if isholdingmon == 0 :
            embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬을 보유하고 있지 않으시군요ㅠㅠ', color = 0xff0000)
            embed.add_field(name="지금 바로 스타팅 라스아이몬을 얻어보세요!", value="명령어 : =스타팅", inline=True)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
        elif isholdingmon == 1 :
            use_money = 100
            embed = discord.Embed(title = '쿠지 뽑기에 오신 것을 환영합니다!', description = '쿠지 뽑기는 일종의 복권 시스템이며\n1회 뽑기 시 100골드가 소모됩니다\n  \
            경품은 10, 30, 50, 130, 190, 500 총 6종입니다\n진행하시겠습니까?\n\n%s진행　　%s취소'%(ok, no), color = 0xff0000)
            embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMDdfMTY4/MDAxNjQ2NjU3NTcxMDQw.LjPv9Rbic0PUz8lduklKESmVb7pWXZM2797S59jGroQg.zFKUN174E-ta2HJ9Vm7xqWPpGrm5rGSxl9XSJu816v0g.JPEG.devjune92/%EC%98%A4%EB%AF%B8%EC%BF%A0%EC%A7%80.jpg?type=w773")
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            msg = await ctx.channel.send(embed = embed)
            await msg.add_reaction(ok)
            await msg.add_reaction(no)  
            try :
                def ContinueTask(reaction, user) :
                    return str(reaction) in [ok, no] and user.id == id
                reaction, user = await bot.wait_for('reaction_add', check=ContinueTask)
                if (str(reaction)) == no :
                    embed = discord.Embed(title = '쿠지 뽑기를 취소합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)
                    con.close()
                elif (str(reaction)) == ok :
                    cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
                    user_i = cur.fetchone()
                    if user_i['money'] < use_money :
                        embed = discord.Embed(title = '😓소지골드가 부족합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await ctx.send(embed = embed)
                        con.close()
                    else :
                        cur.execute("UPDATE User_Info SET money = money - %s WHERE User_id = %s"%(use_money, id)) 
                        embed = discord.Embed(title = '쿠지 뽑기가 진행됩니다', description = '두구두구두구두구......', color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await ctx.send(embed = embed)
                        await asyncio.sleep(5)
                        embed = discord.Embed(title = '과연.....', description = '결과는...........', color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await ctx.send(embed = embed)
                        atari = random.randint(1, 100)
                        if atari < 11 : # 10%
                            get_money = 10
                            casino_profit = 100 - get_money
                        elif atari < 26 : # 15%
                            get_money = 30
                            casino_profit = 100 - get_money
                        elif atari < 52 : # 26%
                            get_money = 50
                            casino_profit = 100 - get_money
                        elif atari < 87 : # 35%
                            get_money = 130 
                            casino_loss = get_money - 100
                        elif atari < 99 : # 12%
                            get_money = 190
                            casino_loss = get_money - 100
                        else : # 2%
                            get_money = 500
                            casino_loss = get_money - 100
                        cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(get_money, id))     
                        cur.execute("UPDATE Casino_Info SET Profit = Profit + %s WHERE Machine_id = 2"%(casino_profit))
                        cur.execute("UPDATE Casino_Info SET Loss = Loss + %s WHERE Machine_id = 2"%(casino_loss))   
                        await asyncio.sleep(5)
                        embed = discord.Embed(title = '결과 발표!', description = '뽑기 결과 보상으로 %s원을 얻었습니다!\n다음에 또 이용해주세요'%(get_money), color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await ctx.send(embed = embed)    
                        con.close()
            except : pass            

# @bot.command()
# async def 도감(ctx) :
#     id = ctx.author.id
#     con = sqlite3.connect('LMDB.db', isolation_level = None)
#     con.row_factory = sqlite3.Row
#     cur = con.cursor()
#     embed = discord.Embed(title = '보고 싶은 라스아이몬의 이름을 타이핑 해주세요', description = 'ex) 시노하라 노조미', color = 0xff0000)
#     embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
#     await ctx.send(embed = embed)
#     def checkAnswer(message) :
#         return message.channel == ctx.channel and message.author.id == id  
#     message = await bot.wait_for("message", check=checkAnswer)
#     serch_index = message.content
#     print(serch_index)
#     print(message.content)
#     cur.execute("SELECT * FROM Mon_Info WHERE Mon_name = ?", (serch_index))
#     mon = cur.fetchone()
#     embed=discord.Embed(title=mon['Mon_name'], description=mon['Mon_grade'], color=0x00ff56)
#     embed.set_author(name="도감", url="https://blog.naver.com/huntingbear21", icon_url="https://cdn.discordapp.com/attachments/541913766296813570/672624076589760512/DRG.png")
#     embed.set_thumbnail(url=mon['etc1'])
#     embed.add_field(name="> 체력", value=mon['Mon_hp'], inline=True)
#     embed.add_field(name="> 공격", value=mon['Mon_atk'], inline=True)
#     embed.add_field(name="> 방어", value=mon['Mon_def'], inline=True)
#     embed.add_field(name="> 민첩", value=mon['Mon_dex'], inline=True)
#     embed.add_field(name="> 행운", value=mon['Mon_luk'], inline=True)
#     embed.set_footer(text="by Mujiseong")
#     await ctx.send(embed=embed)

@bot.command()
async def 토큰획득(ctx) :
    id = ctx.author.id
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    elif isuser == 1 :
        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
        Task_i = cur.fetchone()
        if Task_i['Tk_num'] == 0 :
            cur.execute("UPDATE User_Info SET LvTk = LvTk + 300 WHERE User_id = %s"%(id))
            cur.execute("UPDATE Task_Info SET Tk_num = 1 WHERE User_id = %s"%(id))              
            embed = discord.Embed(title = '하루에 한번, 레벨업 토큰 무료 획득!', description = '300 레벨업 토큰을 획득하셨습니다!', color = 0xff0000)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            msg = await ctx.channel.send(embed = embed)
        else :
            embed = discord.Embed(title = '오늘의 무료 레벨업 토큰을 이미 수령하셨습니다', description = '내일 다시 이용해주세요', color = 0xff0000)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
            con.close()

@bot.command()
async def 광산(ctx) :
    id = ctx.author.id
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    ok = "⭕"
    no = "❌"
    dig = "⛏️"
    stone = 10
    steel = 50
    silver = 70
    gold = 150
    dia = 300
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    elif isuser == 1 :              
        embed = discord.Embed(title = '광산 일로 돈을 벌어보자!\n하루에 10번까지!(그 이상은 몸이 못버텨요..)', description = '곡괭이로 광석을 캐라!\n가치가 있는 광석은 오래 곡괭이질을 해야한다던데...\n시작하시겠습니까?\n\n%s시작　　%s나중에'%(ok, no), color = 0xff0000)
        embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMDVfMjg4/MDAxNjQ2NDg3MDg1NDg3.f1GVpg7vqXq_1xrysvjBT6Q8gWBWf1h4u0iPCbtdO34g.HCYjFS5IZ7ZCX4Ly0Jng1A2t52ZX9vWOa0gZt2kYP5gg.JPEG.devjune92/Mine.jpg?type=w773")
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        msg = await ctx.channel.send(embed = embed)
        await msg.add_reaction(ok)
        await msg.add_reaction(no)
        try :
            def ContinueTask(reaction, user) :
                return str(reaction) in [ok, no] and user != bot.user and user.id == id
            reaction, user = await bot.wait_for('reaction_add', check=ContinueTask)
            if (str(reaction)) == no :
                embed = discord.Embed(title = '광산 작업을 종료합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                con.close()
            elif (str(reaction)) == ok :
                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                DoMineNum = cur.fetchone()
                cur.execute("SELECT * FROM User_Info WHERE User_Id = ?", (id,))
                userInfo = cur.fetchone()
                if DoMineNum['Mine_num'] > 9 :
                    embed = discord.Embed(title = '오늘의 할당량을 모두 채웠습니다', description = '내일 다시 이용해주세요', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)
                    con.close()
                else :
                    cnt = 0
                    mine_end = 0
                    Isalready = 0    
                    cur.execute("UPDATE Task_Info SET Mine_num = Mine_num + 1 WHERE User_id = %s"%(id))
                    embed = discord.Embed(title = '⛏️를 클릭해 내려찍어보자!', description = '비싼 광석을 캐기 위해 클릭!', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    msg = await ctx.channel.send(embed = embed)
                    await msg.add_reaction(dig)
                    try :
                        def ContinueTask(reaction, user) :
                            return str(reaction) in [dig] and user != bot.user and user.id == id
                        reaction, user = await bot.wait_for('reaction_add', check=ContinueTask)
                        if (str(reaction)) == dig :
                            while mine_end == 0 :
                                cnt += 1
                                mine_result = random.randint(1, 5)
                                whatisminedice = random.randint(1, 10)
                                embed = discord.Embed(title = '깡!', description = '%s번 내리쳤다'%(cnt), color = 0xff0000)
                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                if Isalready == 0 :
                                    msg = await ctx.channel.send(embed = embed)
                                    await msg.add_reaction(dig)
                                elif Isalready != 0 :    
                                    await msg.edit(embed=embed)    
                                    await msg.add_reaction(dig)
                                try :    
                                    def ContinueTask(reaction, user) :
                                        return str(reaction) in [dig] and user != bot.user and user.id == id
                                    reaction, user = await bot.wait_for('reaction_add', check=ContinueTask)
                                    if (str(reaction)) == dig :
                                        Isalready = 1   
                                        if mine_result > 3 :
                                            mine_end = mine_end
                                        elif mine_result < 4 :
                                            await asyncio.sleep(2)
                                            embed = discord.Embed(title = '콰직!', description = '묵직한 것이 곡괭이에 걸렸다', color = 0xff0000)
                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                            await ctx.send(embed = embed)
                                            if cnt < 3 :
                                                if whatisminedice < 8 :
                                                    embed = discord.Embed(title = '단단해 보이는 암석이다', description = '%s골드에 판매하였습니다'%(stone), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    mine_end = 1
                                                    cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(stone, id))
                                                    break
                                                else :
                                                    embed = discord.Embed(title = '질 좋아보이는 철광석이다', description = '%s골드에 판매하였습니다'%(steel), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    mine_end = 1
                                                    cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(steel, id))
                                                    break
                                            elif cnt < 5 :
                                                if whatisminedice < 8 :
                                                    embed = discord.Embed(title = '질 좋아보이는 철광석이다', description = '%s골드에 판매하였습니다'%(steel), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    mine_end = 1
                                                    cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(steel, id))
                                                    break
                                                else :
                                                    embed = discord.Embed(title = '반짝거리는 은광석이다', description = '%s골드에 판매하였습니다'%(silver), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    mine_end = 1
                                                    cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(silver, id))
                                                    break
                                            elif cnt < 7 :
                                                if whatisminedice < 8 :
                                                    embed = discord.Embed(title = '반짝거리는 은광석이다', description = '%s골드에 판매하였습니다'%(silver), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    mine_end = 1
                                                    cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(silver, id))
                                                    break
                                                else : 
                                                    embed = discord.Embed(title = '눈이 부신 금광석이다!', description = '%s골드에 판매하였습니다'%(gold), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    mine_end = 1
                                                    cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(gold, id))
                                                    break
                                            else :
                                                if whatisminedice < 8 :
                                                    embed = discord.Embed(title = '눈이 부신 금광석이다!', description = '%s골드에 판매하였습니다'%(gold), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    mine_end = 1
                                                    cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(gold, id))
                                                    break
                                                else :
                                                    embed = discord.Embed(title = '이럴수가! 다이아몬드 광석이다!!', description = '%s골드에 판매하였습니다'%(dia), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    mine_end = 1
                                                    cur.execute("UPDATE User_Info SET money = money + %s WHERE User_id = %s"%(dia, id))
                                                    break     
                                except : pass                                          
                    except : pass                
        except : pass                                

@bot.command()
async def 일과(ctx) :
    id = ctx.author.id
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    ok = "⭕"
    no = "❌"
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    elif isuser == 1 :              
        embed = discord.Embed(title = '숫자 야구 게임으로 골드를 벌어보자!\n기회는 7번!', description = '숫자와 자리 모두 일치한다면 Strike\n숫자는 포함되지만 자리가 틀린 경우 Ball\n3자리 중에 중복되는 숫자는 없어요!\n중간에 포기하고 싶으신 분은 채팅에 일과종료 타이핑!(기회는 차감)\n도전하시겠습니까?\n\n%s도전　　%s나중에'%(ok, no), color = 0xff0000)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        msg = await ctx.channel.send(embed = embed)
        await msg.add_reaction(ok)
        await msg.add_reaction(no)
        try :
            def ContinueTask(reaction, user) :
                return str(reaction) in [ok, no] and user != bot.user and user.id == id
            reaction, user = await bot.wait_for('reaction_add', check=ContinueTask)
            if (str(reaction)) == no :
                embed = discord.Embed(title = '일과 진행을 취소합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                con.close()
            elif (str(reaction)) == ok :
                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                DoTaskNum = cur.fetchone()
                cur.execute("SELECT * FROM User_Info WHERE User_Id = ?", (id,))
                userInfo = cur.fetchone()
                if DoTaskNum['Do_num'] > 2 :
                    embed = discord.Embed(title = '오늘의 일과를 모두 진행했습니다', description = '내일 다시 이용해주세요', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)
                    con.close()
                else :    
                    cur.execute("UPDATE Task_Info SET Do_num = Do_num + 1 WHERE User_id = %s"%(id))    
                    num = []
                    n = 3
                    while len(num) < n :
                        a = random.randint(0, 9)
                        if a not in num :
                            num.append(a)
                    embed = discord.Embed(title = '3자리 숫자를 입력해주세요!', description = '다른 자리 숫자나 문장은 입력 금지!', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)
                    cnt = 0
                    getGold = random.randint(10, 20) * 10
                    LastGold = userInfo['money'] + getGold
                    while True :
                        def CheckAnswer(message) :
                            return message.channel == ctx.channel and message.author.id == id   
                        message = await bot.wait_for("message", check=CheckAnswer)
                        if (message.content.startswith("일과종료")):
                            embed = discord.Embed(title = '도망가시는 건가요?', description = '어쩔 수 없죠~ 대신 오늘 도전 기회 중 1회는 차감돼요~😈', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            break
                        elif message.content.isdigit() == False or len(message.content) != n :
                            embed = discord.Embed(title = '3자리 숫자를 입력해주세요!', description = '다른 자리 숫자나 문장은 입력 금지!', color = 0xff0000)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                        else :
                            strike = 0
                            ball = 0   
                            m = message.content
                            lst = []
                            for i in message.content :
                                lst.append(int(i))
                            for i in range(len(lst)) :
                                for j in range(len(num)) :
                                    if lst[i] == num[j] :
                                        if i == j :
                                            strike += 1
                                        else :
                                            ball += 1    
                            cnt += 1
                            embed = discord.Embed(title = '확인!', description = '%s Strike, %s Ball'%(strike, ball), color = 0xff0000)
                            embed.add_field(name="%s번째 시도"%(cnt), value="⚾"*cnt, inline=True)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                            if cnt == 7 :
                                if strike == len(num) :
                                    cur.execute("UPDATE User_Info SET money = ? WHERE User_id = ?", (LastGold, id)) 
                                    embed = discord.Embed(title = 'Win!', description = '오늘의 일과를 무사히 마쳤습니다!', color = 0xff0000)
                                    embed.add_field(name="보상으로 %s골드를 지급합니다"%(getGold), value="소지골드 : %s골드"%(LastGold), inline=True)
                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                    await ctx.send(embed = embed)
                                    break
                                else :       
                                    embed = discord.Embed(title = '실패!', description = '7번의 기회를 모두 소모하셨습니다ㅠㅠ', color = 0xff0000)
                                    embed.add_field(name="다음에 다시 도전해주세요!", value="😓", inline=True)
                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                    await ctx.send(embed = embed)
                                    break
                            elif strike == len(num) :
                                cur.execute("UPDATE User_Info SET money = ? WHERE User_id = ?", (LastGold, id)) 
                                embed = discord.Embed(title = 'Win!', description = '오늘의 일과를 무사히 마쳤습니다!', color = 0xff0000)
                                embed.add_field(name="보상으로 %s골드를 지급합니다"%(getGold), value="소지골드 : %s골드"%(LastGold), inline=True)
                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                await ctx.send(embed = embed)
                                break
        except : pass                
    con.close()                    


@bot.command()
async def 전적(ctx, user: discord.User) :
    id = ctx.author.id
    nick = ctx.author.name
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    id2 = user.id
    nick2c = user.name
    nick2 = user.display_name
    name_check = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for T_name in name_check.fetchall() :
        if T_name[0] == nick2c :
            break
    if nick2c in T_name :
        if T_name[0] == nick :
            embed = discord.Embed(title = '본인과의 전적을 비교할 순 없겠죠?', description = '정확하게 입력해주세요!', color = 0xff0000)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
        else :    
            cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick, id2))
            score_check = cur.fetchone()
            if score_check == None :
                embed = discord.Embed(title = '상대 전적이 없습니다!', description = '=파이트로 서로 실력을 겨뤄보세요!👊', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
            else :    
                Total_battle = score_check['W'] + score_check['L']
                W_rate = int(score_check['W'] / Total_battle * 100)
                embed = discord.Embed(title = '%s님과의 전적입니다!'%(nick2), description = '총 대전수　:　%s회\n승리 횟수　:　%s회\n패배 횟수　:　%s회'%(Total_battle, score_check['W'], score_check['L']), color = 0xff0000)
                embed.add_field(name="승률은 %s%%입니다"%(W_rate), value="_ _", inline=True)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)    
    else :
        embed = discord.Embed(title = '상대 전적이 없습니다!', description = '=파이트로 서로 실력을 겨뤄보세요!👊', color = 0xff0000)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
        

@bot.command()
async def 파이트도움말(ctx) :
    q_end = 0
    first_window = 0
    while q_end == 0 :
        embed = discord.Embed(title = '파이트 시스템 도움말입니다', description = '파이트에 적용된 각종 시스템에 대해 설명합니다\n파이트 명령어 : =파이트\n\n❌종료　　다음 ▶️', color = 0xff0000)
        if first_window == 0 :
            msg = await ctx.channel.send(embed = embed)
            await msg.add_reaction("↩️")
            await msg.add_reaction("❌")
            await msg.add_reaction("▶️")
        else :
            await msg.edit(embed=embed)    
            await msg.add_reaction("↩️")
            await msg.add_reaction("❌")
            await msg.add_reaction("▶️")
        try :
            def question(reaction, user) :
                return str(reaction) in ["❌", "▶️"] and user != bot.user and user.id == ctx.message.author.id
            reaction, user = await bot.wait_for('reaction_add', check=question)
            if (str(reaction)) == "❌" :
                embed = discord.Embed(title = '파이트도움말을 종료합니다', description = '라스아이몬을 즐겨주세요!', color = 0xff0000)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await msg.edit(embed=embed)
                q_end = 1
                break
            while (str(reaction)) == "▶️" and q_end == 0 :
                embed = discord.Embed(title = '공격 시스템', description = '공격은 🅰️ 버튼을 누르면 실시됩니다\n0부터 라스아이몬의 공격력까지의 범위에서 주사위를 \
                굴려\n나온 값을 공격력으로 취급합니다\n해당 주사위 굴림은 공격선언 시마다 실행합니다\n\n↩️ 처음으로　　❌종료　　다음 ▶️', color = 0xff0000)
                await msg.edit(embed=embed)
                await msg.add_reaction("↩️")
                await msg.add_reaction("❌")
                await msg.add_reaction("▶️")
                try :
                    def question2(reaction, user) :
                        return str(reaction) in ["↩️", "❌", "▶️"] and user != bot.user and user.id == ctx.message.author.id
                    reaction, user = await bot.wait_for('reaction_add', check=question2)
                    if (str(reaction)) == "↩️" :
                        first_window = 1
                        continue
                    elif (str(reaction)) == "❌" :
                        embed = discord.Embed(title = '파이트도움말을 종료합니다', description = '라스아이몬을 즐겨주세요!', color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await msg.edit(embed=embed)
                        q_end = 1
                        break
                    while (str(reaction)) == "▶️" and q_end == 0 :
                        embed = discord.Embed(title = '방어 시스템1', description = '방어는 공격을 받았을 시 자동으로 실시됩니다\n0부터 라스아이몬의 방어력까지의 \
                        범위에서 주사위를 굴려\n나온 값을 방어력으로 취급합니다\n해당 주사위 굴림은 피공격 시마다 실행합니다\n\n↩️ 처음으로　　❌종료　　다음 ▶️', color = 0xff0000)
                        await msg.edit(embed=embed)
                        await msg.add_reaction("↩️")
                        await msg.add_reaction("❌")
                        await msg.add_reaction("▶️")
                        try :
                            def question3(reaction, user) :
                                return str(reaction) in ["↩️", "❌", "▶️"] and user != bot.user and user.id == ctx.message.author.id
                            reaction, user = await bot.wait_for('reaction_add', check=question3)
                            if (str(reaction)) == "↩️" :
                                first_window = 1
                                continue
                            elif (str(reaction)) == "❌" :
                                embed = discord.Embed(title = '파이트도움말을 종료합니다', description = '라스아이몬을 즐겨주세요!', color = 0xff0000)
                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                await msg.edit(embed=embed)
                                q_end = 1
                                break
                            while (str(reaction)) == "▶️" and q_end == 0 :
                                embed = discord.Embed(title = '방어 시스템2', description = '만약 방어자의 주사위 굴림 값이 공격자의 주사위 굴림 값보다 크거나 같다면\n \
                                해당 공격은 실패하고 데미지 계산은 실행하지 않습니다\n단, 크리티컬 시스템이 발동했을 경우는 예외로 합니다\n\n↩️ 처음으로　　❌종료　　다음 ▶️', color = 0xff0000)
                                await msg.edit(embed=embed)
                                await msg.add_reaction("↩️")
                                await msg.add_reaction("❌")
                                await msg.add_reaction("▶️")
                                try :
                                    def question4(reaction, user) :
                                        return str(reaction) in ["↩️", "❌", "▶️"] and user != bot.user and user.id == ctx.message.author.id
                                    reaction, user = await bot.wait_for('reaction_add', check=question4)
                                    if (str(reaction)) == "↩️" :
                                        first_window = 1
                                        continue
                                    elif (str(reaction)) == "❌" :
                                        embed = discord.Embed(title = '파이트도움말을 종료합니다', description = '라스아이몬을 즐겨주세요!', color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await msg.edit(embed=embed)
                                        q_end = 1
                                        break
                                    while (str(reaction)) == "▶️" and q_end == 0 :
                                        embed = discord.Embed(title = '크리티컬 시스템', description = '일정 확률로 공격자의 주사위 굴림 값이 2배가 됩니다\n \
                                        확률은 라스아이몬의 dex의 영향을 받으며 dex수치 1당 0.8%의 확률을 가집니다\n해당 판정은 공격선언 시마다 실행합니다\n\n↩️ 처음으로　　❌종료　　다음 ▶️', color = 0xff0000)
                                        await msg.edit(embed=embed)
                                        await msg.add_reaction("↩️")
                                        await msg.add_reaction("❌")
                                        await msg.add_reaction("▶️")
                                        try :
                                            def question5(reaction, user) :
                                                return str(reaction) in ["↩️", "❌", "▶️"] and user != bot.user and user.id == ctx.message.author.id
                                            reaction, user = await bot.wait_for('reaction_add', check=question5)
                                            if (str(reaction)) == "↩️" :
                                                first_window = 1
                                                continue
                                            elif (str(reaction)) == "❌" :
                                                embed = discord.Embed(title = '파이트도움말을 종료합니다', description = '라스아이몬을 즐겨주세요!', color = 0xff0000)
                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                await msg.edit(embed=embed)
                                                q_end = 1
                                                break
                                            while (str(reaction)) == "▶️" and q_end == 0 :
                                                embed = discord.Embed(title = '회피 시스템', description = '방어 시 일정 확률로 공격자의 공격을 회피합니다\n \
                                                확률은 라스아이몬의 luk의 영향을 받으며\n((1-(luk*1.5/(luk*1.5+100)))*100)%의 확률을 가집니다\n해당 판정은 피공격 시마다 실행합니다\n\n↩️ 처음으로　　❌종료', color = 0xff0000)
                                                await msg.edit(embed=embed)
                                                await msg.add_reaction("↩️")
                                                await msg.add_reaction("❌")
                                                try :
                                                    def question6(reaction, user) :
                                                        return str(reaction) in ["↩️", "❌"] and user != bot.user and user.id == ctx.message.author.id
                                                    reaction, user = await bot.wait_for('reaction_add', check=question6)
                                                    if (str(reaction)) == "↩️" :
                                                        first_window = 1
                                                        continue
                                                    elif (str(reaction)) == "❌" :
                                                        embed = discord.Embed(title = '파이트도움말을 종료합니다', description = '라스아이몬을 즐겨주세요!', color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await msg.edit(embed=embed)
                                                        q_end = 1
                                                        break
                                                except : pass
                                        except : pass
                                except : pass
                        except : pass                           
                except : pass  
        except : pass                    

@bot.command()
async def 레이드정보(ctx) :
    id = ctx.author.id
    israid = IsRaid(id)
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
    raid_i = cur.fetchone()
    if israid == 1 :
        embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '누적 데미지 : %s\n총 도전 횟수 : %s'%(raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    else :
        return    

@bot.command()
async def 레이드(ctx) :
    global isRaidRunning
    if isRaidRunning == False :
        isRaidRunning = True
        id = ctx.author.id
        nick = ctx.author.display_name
        atk = "🅰️"
        skill = "✡️"
        battlerun = "⏹️"
        ok = "⭕"
        no = "❌"
        con = sqlite3.connect('LMDB.db', isolation_level = None)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        isuser = IsUser(id)
        isholdingmon = IsHoldingMon(id)
        israid = IsRaid(id)
        raid_Mon_num = 2001
        import random
        if israid == 0 :
            cur.execute("INSERT INTO Raid_Info VALUES(?, ?, ?, ?, ?, ?)", (id, nick, 0, 0, 0, 0,))  
            embed = discord.Embed(title = '레이드가 처음이시군요?', description = '레이드 정보를 등록합니다', color = 0xff0000)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
        if isuser == 0 :
            embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
            embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
            isRaidRunning = False
        elif isuser == 1 :    
            if isholdingmon == 0 :
                embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬을 보유하고 있지 않으시군요ㅠㅠ', color = 0xff0000)
                embed.add_field(name="지금 바로 스타팅 라스아이몬을 얻어보세요!", value="명령어 : =스타팅", inline=True)
                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                await ctx.send(embed = embed)
                isRaidRunning = False
            elif isholdingmon == 1 :
                cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = %s"%(raid_Mon_num))
                raid_mon = cur.fetchone()
                if raid_mon['Mon_hp'] <= 0 :
                    embed = discord.Embed(title = '현재 레이드가 진행되고 있지 않습니다', description = '다음 레이드를 기다려주세요!', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)
                    isRaidRunning = False
                else :
                    cur.execute("SELECT * FROM Hold_Info WHERE User_id = ?", (id,))
                    mon_hold = cur.fetchone()
                    cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = ?", (mon_hold['Mon_id'],))
                    mon = cur.fetchone()
                    cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
                    user_i = cur.fetchone()
                    cur.execute("SELECT * FROM Stat_Info WHERE User_id = ?", (id,))
                    stat = cur.fetchone()    
                    cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                    raid_i = cur.fetchone()
                    raid_nick = raid_mon['Mon_name']
                    raid_hp1 = raid_mon['Mon_hp']
                    raid_hp2 = raid_mon['Mon_gradeN']
                    raid_atk = raid_mon['Mon_atk']
                    raid_def = raid_mon['Mon_def']
                    raid_dex = raid_mon['Mon_dex']
                    raid_luk = raid_mon['Mon_luk']
                    raid_avoid = int((1 - (raid_luk * 1.5 / (raid_luk * 1.5 + 100))) * 100)
                    chace_num = (10 - raid_i['Do_num'])
                    state_raid_hp = "%s/%s"%(raid_hp1, raid_hp2)
                    start_hp = raid_mon['Mon_hp']
                    embed = discord.Embed(title = '🚨Warnning🚨', description = '레이드 몬스터 출현!', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                    await ctx.send(embed = embed)
                    embed=discord.Embed(title=raid_mon['Mon_name'], description=raid_mon['Mon_grade'], color=0x00ff56)
                    embed.set_author(name='라스아이몬', url="https://blog.naver.com/huntingbear21", icon_url="https://cdn.discordapp.com/attachments/541913766296813570/672624076589760512/DRG.png")
                    embed.set_thumbnail(url=raid_mon['etc1'])
                    embed.add_field(name="> 체력", value=state_raid_hp, inline=True)
                    embed.add_field(name="> 공격", value=raid_mon['Mon_atk'], inline=True)
                    embed.add_field(name="> 방어", value=raid_mon['Mon_def'], inline=True)
                    embed.add_field(name="> 민첩", value=raid_mon['Mon_dex'], inline=True)
                    embed.add_field(name="> 행운", value=raid_mon['Mon_luk'], inline=True)
                    embed.set_footer(text="by Mujiseong")
                    await ctx.send(embed=embed)
                    embed = discord.Embed(title = '레이드 몬스터의 현재 상태입니다', description = '전 유저가 함께 도전하는 레이드\n하루에 10회 도전 가능, 입힌 데미지 누적\n  \
                    현재 %s님의 도전 횟수는 %s회 남았습니다'%(nick, chace_num), color = 0xff0000)
                    await ctx.send(embed=embed)
                    if raid_i['Do_num'] == 10 :
                        embed = discord.Embed(title = '오늘의 레이드를 모두 진행했습니다', description = '내일 다시 이용해주세요', color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        await ctx.send(embed = embed)
                        isRaidRunning = False
                        con.close()
                    else :
                        embed = discord.Embed(title = '도전 하시겠습니까?', description = '%s도전　　%s다음에'%(ok, no), color = 0xff0000)
                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                        msg = await ctx.channel.send(embed = embed)
                        await msg.add_reaction(ok)
                        await msg.add_reaction(no)  
                        try :
                            def ContinueRaid(reaction, user) :
                                return str(reaction) in [ok, no] and user.id == id
                            reaction, user = await bot.wait_for('reaction_add', check=ContinueRaid)
                            if (str(reaction)) == no :
                                embed = discord.Embed(title = '레이드 진행을 취소합니다', description = '다음에 다시 이용해주세요', color = 0xff0000)
                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                await ctx.send(embed = embed)
                                isRaidRunning = False
                                con.close()
                            elif (str(reaction)) == ok :
                                user1_hp1 = (mon['Mon_hp'] + stat['A_hp'])
                                user1_hp2 = (mon['Mon_hp'] + stat['A_hp'])
                                user1_atk = (mon['Mon_atk'] + stat['A_atk'])
                                user1_def = (mon['Mon_def'] + stat['A_def'])
                                user1_dex = (mon['Mon_dex'] + stat['A_dex'])
                                user1_luk = (mon['Mon_luk'] + stat['A_luk'])
                                user1_avoid = int((1 - (user1_luk * 1.5 / (user1_luk * 1.5 + 100))) * 100)
                                cur.execute("UPDATE Raid_Info SET Do_num = Do_num + 1 WHERE User_id = %s"%(id))
                                cur.execute("UPDATE Raid_Info SET etc1 = etc1 + 1 WHERE User_id = %s"%(id))
                                embed=discord.Embed(title=mon['Mon_name'], description=mon['Mon_grade'], color=0x00ff56)
                                embed.set_author(name=nick, url="https://blog.naver.com/huntingbear21", icon_url="https://cdn.discordapp.com/attachments/541913766296813570/672624076589760512/DRG.png")
                                embed.set_thumbnail(url=mon['etc1'])
                                embed.add_field(name="> 레벨", value=mon_hold['Mon_level'], inline=True)
                                embed.add_field(name="> 체력", value=mon['Mon_hp'] + stat['A_hp'], inline=True)
                                embed.add_field(name="> 공격", value=mon['Mon_atk'] + stat['A_atk'], inline=True)
                                embed.add_field(name="> 방어", value=mon['Mon_def'] + stat['A_def'], inline=True)
                                embed.add_field(name="> 민첩", value=mon['Mon_dex'] + stat['A_dex'], inline=True)
                                embed.add_field(name="> 행운", value=mon['Mon_luk'] + stat['A_luk'], inline=True)
                                embed.add_field(name="> 보유골드", value=user_i['money'], inline=True)
                                embed.set_footer(text="by Mujiseong")
                                await ctx.send(embed=embed)
                                user1FirstAtk = True
                                f_end = 0
                                while f_end == 0 :
                                    if user1FirstAtk == True :
                                        embed = discord.Embed(title = '%s님 원하시는 행동을 선택해주세요'%(nick), description = '일반공격 = %s\n특수기 = %s\n항복 = %s'%(atk, skill, battlerun), color = 0xff0000)
                                        msg = await ctx.channel.send(embed = embed)
                                        await msg.add_reaction(atk)
                                        await msg.add_reaction(skill)
                                        await msg.add_reaction(battlerun)                           
                                        try :
                                            def checking2(reaction, user) :
                                                return str(reaction) in [atk, skill, battlerun] and user != bot.user and user.id == id
                                            reaction, user = await bot.wait_for('reaction_add', check=checking2)
                                            if (str(reaction)) == battlerun :
                                                embed = discord.Embed(title = '%s님이 항복하였습니다'%(nick), description = '레이드가 종료되었습니다', color = 0xff0000)
                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                await ctx.send(embed = embed)
                                                f_end += 1
                                                Totaldamage = (start_hp - raid_hp1)
                                                cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                raid_i = cur.fetchone()
                                                embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                await ctx.send(embed = embed)
                                                isRaidRunning = False
                                                break
                                            elif (str(reaction)) == atk :
                                                cri = random.randint(1,125)
                                                power = random.randint(0, user1_atk)
                                                shield = random.randint(0, raid_def)
                                                avoid = random.randint(1,100)
                                                if power == 0 :
                                                    embed = discord.Embed(title = '아이쿠!', description = '손이 미끄러져 공격에 실패했다', color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    user1FirstAtk = not user1FirstAtk
                                                elif user1_dex >= cri :
                                                    damage = ((power * 2) - shield)
                                                    embed = discord.Embed(title = '%s의 공격선언!'%(nick), description = '공격 주사위 결과 %s\n상대의 방어 주사위 결과 %s'%(power, shield), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    if damage <= 0 :
                                                        embed = discord.Embed(title = '%s의 방어성공!'%(raid_nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        if raid_luk >= random.randint(1,250) :
                                                            user1_hp1 -= power
                                                            embed = discord.Embed(title = '이화접목!', description = '%s은(는) 놀라운 기지로 상대의 공격을 그대로 돌려줬다!'%(raid_nick), color = 0xff0000)
                                                            embed.add_field(name="%s의 데미지를 입혔다"%(power), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if user1_hp1 <= 0 :
                                                                embed = discord.Embed(title = '%s의 승리!'%(raid_nick), description = '레이드 실패..', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                Totaldamage = (start_hp - raid_hp1)
                                                                cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                                cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                                cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                                raid_i = cur.fetchone()
                                                                embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                f_end += 1
                                                                isRaidRunning = False
                                                                break
                                                        user1FirstAtk = not user1FirstAtk
                                                    elif raid_avoid < avoid :
                                                        embed = discord.Embed(title = '%s의 회피성공!'%(raid_nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        user1FirstAtk = not user1FirstAtk
                                                    else :
                                                        raid_hp1 -= damage
                                                        embed = discord.Embed(title = '크리티컬!', description = '공격 주사위 결과 값 2배! %s로 상승!'%(power*2), color = 0xff0000)
                                                        embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(raid_nick, raid_hp1, raid_hp2), inline=True)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        user1FirstAtk = not user1FirstAtk
                                                        if raid_hp1 <= 0 :
                                                            embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉레이드 컴플리트!!!🎉', color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            Totaldamage = (start_hp - raid_hp1)
                                                            cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                            cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                            cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                            raid_i = cur.fetchone()
                                                            embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            f_end += 1
                                                            isRaidRunning = False
                                                            break
                                                elif power >= user1_atk / 2 :
                                                    damage = (power - shield)
                                                    embed = discord.Embed(title = '%s의 공격선언!'%(nick), description = '공격 주사위 결과 %s\n상대의 방어 주사위 결과 %s'%(power, shield), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    if damage <= 0 :
                                                        embed = discord.Embed(title = '%s의 방어성공!'%(raid_nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        if raid_luk >= random.randint(1,250) :
                                                            user1_hp1 -= power
                                                            embed = discord.Embed(title = '이화접목!', description = '%s은(는) 놀라운 기지로 상대의 공격을 그대로 돌려줬다!'%(raid_nick), color = 0xff0000)
                                                            embed.add_field(name="%s의 데미지를 입혔다"%(power), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if user1_hp1 <= 0 :
                                                                embed = discord.Embed(title = '%s의 승리!'%(raid_nick), description = '레이드 실패..', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                Totaldamage = (start_hp - raid_hp1)
                                                                cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                                cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                                cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                                raid_i = cur.fetchone()
                                                                embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                f_end += 1
                                                                isRaidRunning = False
                                                                break
                                                        user1FirstAtk = not user1FirstAtk
                                                    elif raid_avoid < avoid :
                                                        embed = discord.Embed(title = '%s의 회피성공!'%(raid_nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        user1FirstAtk = not user1FirstAtk
                                                    else :
                                                        raid_hp1 -= damage
                                                        embed = discord.Embed(title = '정확하게 파고들어 공격을 성공시켰다', description = '놀라운 기량!', color = 0xff0000)
                                                        embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(raid_nick, raid_hp1, raid_hp2), inline=True)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        user1FirstAtk = not user1FirstAtk
                                                        if raid_hp1 <= 0 :
                                                            embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉레이드 컴플리트!!!🎉', color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            Totaldamage = (start_hp - raid_hp1)
                                                            cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                            cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                            cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                            raid_i = cur.fetchone()
                                                            embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            f_end += 1
                                                            isRaidRunning = False
                                                            break            
                                                elif power < user1_atk / 2 :
                                                    damage = (power - shield)
                                                    embed = discord.Embed(title = '%s의 공격선언!'%(nick), description = '공격 주사위 결과 %s\n상대의 방어 주사위 결과 %s'%(power, shield), color = 0xff0000)
                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    if damage <= 0 :
                                                        embed = discord.Embed(title = '%s의 방어성공!'%(raid_nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        if raid_luk >= random.randint(1,250) :
                                                            user1_hp1 -= power
                                                            embed = discord.Embed(title = '이화접목!', description = '%s은(는) 놀라운 기지로 상대의 공격을 그대로 돌려줬다!'%(raid_nick), color = 0xff0000)
                                                            embed.add_field(name="%s의 데미지를 입혔다"%(power), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if user1_hp1 <= 0 :
                                                                embed = discord.Embed(title = '%s의 승리!'%(raid_nick), description = '레이드 실패..', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                Totaldamage = (start_hp - raid_hp1)
                                                                cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                                cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                                cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                                raid_i = cur.fetchone()
                                                                embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                f_end += 1
                                                                isRaidRunning = False
                                                                break
                                                        user1FirstAtk = not user1FirstAtk
                                                    elif raid_avoid < avoid :
                                                        embed = discord.Embed(title = '%s의 회피성공!'%(raid_nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        user1FirstAtk = not user1FirstAtk
                                                    else :
                                                        raid_hp1 -= damage
                                                        embed = discord.Embed(title = '스탭이 흐트러진 맥이 빠진 공격', description = '절반의 힘도 발휘하지 못했다', color = 0xff0000)
                                                        embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(raid_nick, raid_hp1, raid_hp2), inline=True)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        user1FirstAtk = not user1FirstAtk
                                                        if raid_hp1 <= 0 :
                                                            embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉레이드 컴플리트!!!🎉', color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            Totaldamage = (start_hp - raid_hp1)
                                                            cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                            cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                            cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                            raid_i = cur.fetchone()
                                                            embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            f_end += 1
                                                            isRaidRunning = False
                                                            break
                                            elif (str(reaction)) == skill :
                                                embed = discord.Embed(title = '현재 스킬 미구현 상태입니다', description = '다시 공격 선언 해주세요', color = 0xff0000)
                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                await ctx.send(embed = embed)
                                        except : pass
                                    else :
                                        whatRaidMondo = random.randint(1,5)
                                        if whatRaidMondo != 1 :
                                            cri = random.randint(1,125)
                                            power = random.randint(0, raid_atk)
                                            shield = random.randint(0, user1_def)
                                            avoid = random.randint(1,100)
                                            if power == 0 :
                                                embed = discord.Embed(title = '끓어오르는 힘을 진정시키고 있다', description = '이번 턴 아무 행동도 하지 않는다', color = 0xff0000)
                                                embed.set_thumbnail(url=raid_mon['etc1'])
                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                await ctx.send(embed = embed)
                                                user1FirstAtk = not user1FirstAtk
                                            elif raid_dex >= cri :
                                                damage = ((power * 2) - shield)
                                                embed = discord.Embed(title = '%s의 공격선언!'%(raid_nick), description = '공격 주사위 결과 %s\n상대의 방어 주사위 결과 %s'%(power, shield), color = 0xff0000)
                                                embed.set_thumbnail(url=raid_mon['etc1'])
                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                await ctx.send(embed = embed)
                                                if damage <= 0 :
                                                    embed = discord.Embed(title = '%s의 방어성공!'%(nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    if user1_luk >= random.randint(1,250) :
                                                        raid_hp1 -= power
                                                        embed = discord.Embed(title = '이화접목!', description = '%s은(는) 놀라운 기지로 상대의 공격을 그대로 돌려줬다!'%(nick), color = 0xff0000)
                                                        embed.add_field(name="%s의 데미지를 입혔다"%(power), value="%s의 남은 HP = %s/%s"%(raid_nick, raid_hp1, raid_hp2), inline=True)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        if raid_hp1 <= 0 :
                                                            embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉레이드 컴플리트!!!🎉', color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            Totaldamage = (start_hp - raid_hp1)
                                                            cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                            cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                            cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                            raid_i = cur.fetchone()
                                                            embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            f_end += 1
                                                            isRaidRunning = False
                                                            break
                                                    user1FirstAtk = not user1FirstAtk
                                                elif user1_avoid < avoid :
                                                    embed = discord.Embed(title = '%s의 회피성공!'%(nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    user1FirstAtk = not user1FirstAtk
                                                else :
                                                    user1_hp1 -= damage
                                                    embed = discord.Embed(title = '크리티컬!', description = '공격 주사위 결과 값 2배! %s로 상승!'%(power*2), color = 0xff0000)
                                                    embed.set_thumbnail(url=raid_mon['etc1'])
                                                    embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    user1FirstAtk = not user1FirstAtk
                                                    if user1_hp1 <= 0 :
                                                        embed = discord.Embed(title = '%s의 승리!'%(raid_nick), description = '레이드 실패..', color = 0xff0000)
                                                        embed.set_thumbnail(url=raid_mon['etc1'])
                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        Totaldamage = (start_hp - raid_hp1)
                                                        cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                        cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                        cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                        raid_i = cur.fetchone()
                                                        embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        f_end += 1
                                                        isRaidRunning = False
                                                        break
                                            elif power >= raid_atk / 2 :
                                                damage = (power - shield)
                                                embed = discord.Embed(title = '%s의 공격선언!'%(raid_nick), description = '공격 주사위 결과 %s\n상대의 방어 주사위 결과 %s'%(power, shield), color = 0xff0000)
                                                embed.set_thumbnail(url=raid_mon['etc1'])
                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                await ctx.send(embed = embed)
                                                if damage <= 0 :
                                                    embed = discord.Embed(title = '%s의 방어성공!'%(nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    if user1_luk >= random.randint(1,250) :
                                                        raid_hp1 -= power
                                                        embed = discord.Embed(title = '이화접목!', description = '%s은(는) 놀라운 기지로 상대의 공격을 그대로 돌려줬다!'%(nick), color = 0xff0000)
                                                        embed.add_field(name="%s의 데미지를 입혔다"%(power), value="%s의 남은 HP = %s/%s"%(raid_nick, raid_hp1, raid_hp2), inline=True)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        if raid_hp1 <= 0 :
                                                            embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉레이드 컴플리트!!!🎉', color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            Totaldamage = (start_hp - raid_hp1)
                                                            cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                            cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                            cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                            raid_i = cur.fetchone()
                                                            embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            f_end += 1
                                                            isRaidRunning = False
                                                            break
                                                    user1FirstAtk = not user1FirstAtk
                                                elif user1_avoid < avoid :
                                                    embed = discord.Embed(title = '%s의 회피성공!'%(nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    user1FirstAtk = not user1FirstAtk
                                                else :
                                                    user1_hp1 -= damage
                                                    embed = discord.Embed(title = 'キモ日本人の力を見せてやるわ、、', description = '良い一日を!!', color = 0xff0000)
                                                    embed.set_thumbnail(url=raid_mon['etc1'])
                                                    embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    user1FirstAtk = not user1FirstAtk
                                                    if user1_hp1 <= 0 :
                                                        embed = discord.Embed(title = '%s의 승리!'%(raid_nick), description = '레이드 실패..', color = 0xff0000)
                                                        embed.set_thumbnail(url=raid_mon['etc1'])
                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        Totaldamage = (start_hp - raid_hp1)
                                                        cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                        cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                        cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                        raid_i = cur.fetchone()
                                                        embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        f_end += 1
                                                        isRaidRunning = False
                                                        break            
                                            elif power < raid_atk / 2 :
                                                damage = (power - shield)
                                                embed = discord.Embed(title = '%s의 공격선언!'%(raid_nick), description = '공격 주사위 결과 %s\n상대의 방어 주사위 결과 %s'%(power, shield), color = 0xff0000)
                                                embed.set_thumbnail(url=raid_mon['etc1'])
                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                await ctx.send(embed = embed)
                                                if damage <= 0 :
                                                    embed = discord.Embed(title = '%s의 방어성공!'%(nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    if user1_luk >= random.randint(1,250) :
                                                        raid_hp1 -= power
                                                        embed = discord.Embed(title = '이화접목!', description = '%s은(는) 놀라운 기지로 상대의 공격을 그대로 돌려줬다!'%(nick), color = 0xff0000)
                                                        embed.add_field(name="%s의 데미지를 입혔다"%(power), value="%s의 남은 HP = %s/%s"%(raid_nick, raid_hp1, raid_hp2), inline=True)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        if raid_hp1 <= 0 :
                                                            embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉레이드 컴플리트!!!🎉', color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            Totaldamage = (start_hp - raid_hp1)
                                                            cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                            cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                            cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                            raid_i = cur.fetchone()
                                                            embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            f_end += 1
                                                            isRaidRunning = False
                                                            break
                                                    user1FirstAtk = not user1FirstAtk
                                                elif user1_avoid < avoid :
                                                    embed = discord.Embed(title = '%s의 회피성공!'%(nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    user1FirstAtk = not user1FirstAtk
                                                else :
                                                    user1_hp1 -= damage
                                                    embed = discord.Embed(title = 'ハム太郎召喚術!', description = 'ハムハムハム、、', color = 0xff0000)
                                                    embed.set_thumbnail(url=raid_mon['etc1'])
                                                    embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                    await ctx.send(embed = embed)
                                                    user1FirstAtk = not user1FirstAtk
                                                    if user1_hp1 <= 0 :
                                                        embed = discord.Embed(title = '%s의 승리!'%(raid_nick), description = '레이드 실패..', color = 0xff0000)
                                                        embed.set_thumbnail(url=raid_mon['etc1'])
                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        Totaldamage = (start_hp - raid_hp1)
                                                        cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                        cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                        cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                        raid_i = cur.fetchone()
                                                        embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        f_end += 1
                                                        isRaidRunning = False
                                                        break
                                        else :
                                            damage = (raid_atk + 5)
                                            user1_hp1 -= damage
                                            embed = discord.Embed(title = '레이드 몬스터의 분위기가 심상치 않다..!', description = '스킬 발동!', color = 0xff0000)
                                            embed.set_thumbnail(url=raid_mon['etc1'])
                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                            await ctx.send(embed = embed)
                                            embed = discord.Embed(title = '嫌な日本人一位なんて、、、むしろ気持ち良いわ!!', description = '笑笑笑笑笑笑笑笑笑笑笑笑笑笑笑笑笑笑笑', color = 0xff0000)
                                            embed.set_thumbnail(url=raid_mon['etc1'])
                                            embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                            await ctx.send(embed = embed)
                                            user1FirstAtk = not user1FirstAtk
                                            if user1_hp1 <= 0 :
                                                embed = discord.Embed(title = '%s의 승리!'%(raid_nick), description = '레이드 실패..', color = 0xff0000)
                                                embed.set_thumbnail(url=raid_mon['etc1'])
                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                await ctx.send(embed = embed)
                                                Totaldamage = (start_hp - raid_hp1)
                                                cur.execute("UPDATE Raid_Info SET Tatal_damage = Tatal_damage + %s WHERE User_id = %s"%(Totaldamage, id))
                                                cur.execute("UPDATE Mon_Info SET Mon_hp = %s WHERE Mon_id = %s"%(raid_hp1, raid_Mon_num))
                                                cur.execute("SELECT * FROM Raid_Info WHERE User_id = ?", (id,))
                                                raid_i = cur.fetchone()
                                                embed = discord.Embed(title = '현재까지 누적 데미지 및 총 도전 횟수', description = '이번에 입힌 데미지 : %s\n누적 데미지 : %s\n총 도전 횟수 : %s'%(Totaldamage, raid_i['Tatal_damage'], raid_i['etc1']), color = 0xff0000)
                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                await ctx.send(embed = embed)
                                                f_end += 1
                                                isRaidRunning = False
                                                break                                       
                        except : pass        




@bot.command()
async def 파이트(ctx) :
    id = ctx.author.id
    nick = ctx.author.display_name
    nick3 = ctx.author.name
    atk = "🅰️"
    skill = "✡️"
    battlerun = "⏹️"
    challenge = "🆚"
    con = sqlite3.connect('LMDB.db', isolation_level = None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    isuser = IsUser(id)
    isholdingmon = IsHoldingMon(id)
    import random
    if isuser == 0 :
        embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
        embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    elif isuser == 1 :    
        if isholdingmon == 0 :
            embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬을 보유하고 있지 않으시군요ㅠㅠ', color = 0xff0000)
            embed.add_field(name="지금 바로 스타팅 라스아이몬을 얻어보세요!", value="명령어 : =스타팅", inline=True)
            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
            await ctx.send(embed = embed)
        elif isholdingmon == 1 :
            cur.execute("SELECT * FROM Hold_Info WHERE User_id = ?", (id,))
            mon_hold = cur.fetchone()
            cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = ?", (mon_hold['Mon_id'],))
            mon = cur.fetchone()
            cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id,))
            user_i = cur.fetchone()
            cur.execute("SELECT * FROM Stat_Info WHERE User_id = ?", (id,))
            stat = cur.fetchone()
            user1_hp1 = (mon['Mon_hp'] + stat['A_hp'])
            user1_hp2 = (mon['Mon_hp'] + stat['A_hp'])
            user1_atk = (mon['Mon_atk'] + stat['A_atk'])
            user1_def = (mon['Mon_def'] + stat['A_def'])
            user1_dex = (mon['Mon_dex'] + stat['A_dex'])
            user1_luk = (mon['Mon_luk'] + stat['A_luk'])
            user1_avoid = int((1 - (user1_luk * 1.5 / (user1_luk * 1.5 + 100))) * 100)
            user1_skillpoint = int(1 + (user1_luk / 11))
            embed=discord.Embed(title=mon['Mon_name'], description=mon['Mon_grade'], color=0x00ff56)
            embed.set_author(name=nick, url="https://lastidolnote.com/", icon_url=ctx.message.author.avatar_url)
            embed.set_image(url=mon['etc1'])
            embed.add_field(name="> 레벨", value=mon_hold['Mon_level'], inline=True)
            embed.add_field(name="> 체력", value=mon['Mon_hp'] + stat['A_hp'], inline=True)
            embed.add_field(name="> 공격", value=mon['Mon_atk'] + stat['A_atk'], inline=True)
            embed.add_field(name="> 방어", value=mon['Mon_def'] + stat['A_def'], inline=True)
            embed.add_field(name="> 민첩", value=mon['Mon_dex'] + stat['A_dex'], inline=True)
            embed.add_field(name="> 행운", value=mon['Mon_luk'] + stat['A_luk'], inline=True)
            embed.add_field(name="> 보유골드", value=user_i['money'], inline=True)
            embed.add_field(name="> 레벨업 토큰", value=user_i['Lvtk'], inline=True)
            embed.set_footer(text="by Mujiseong")
            await ctx.send(embed=embed)
            embed = discord.Embed(title = '파이터 %s님의 라스아이이몬 정보입니다'%(nick), description = '대전을 원하시는 분은 %s 이모지를 눌러주세요'%(challenge), color = 0xff0000)
            msg = await ctx.channel.send(embed = embed)
            await msg.add_reaction(challenge)
            f_end = 0
            while f_end == 0 :
                try :
                    def NewChallenger(reaction, user) :
                        return str(reaction) in [challenge] and user != bot.user and user.id != id and reaction.message.channel.id == ctx.message.channel.id
                    reaction, user = await bot.wait_for('reaction_add', check=NewChallenger)
                    if (str(reaction)) == challenge :
                        isuser2 = IsUser(user.id)
                        isholdingmon2 = IsHoldingMon(user.id)
                        if isuser2 == 0 :
                            embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬 트레이너가 아니시군요ㅠㅠ', color = 0xff0000)
                            embed.add_field(name="서비스 가입 후 이용해주세요!", value="명령어 : =가입", inline=True)
                            embed.add_field(name="대전을 원하시는 분께서는 다시 이모지를 클릭해주세요", value="상단 %s 이모지 클릭"%(challenge), inline=True)
                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                            await ctx.send(embed = embed)
                        elif isuser2 == 1 :
                            if isholdingmon2 == 0 :
                                    embed = discord.Embed(title = ':man_facepalming: 이런', description = '라스아이몬을 보유하고 있지 않으시군요ㅠㅠ', color = 0xff0000)
                                    embed.add_field(name="지금 바로 스타팅 라스아이몬을 얻어보세요!", value="명령어 : =스타팅", inline=True)
                                    embed.add_field(name="대전을 원하시는 분께서는 다시 이모지를 클릭해주세요", value="상단 %s 이모지 클릭"%(challenge), inline=True)
                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                    await ctx.send(embed = embed)
                            elif isholdingmon2 == 1 :
                                id2 = user.id
                                nick2 = user.display_name
                                nick4 = user.name
                                cur.execute("SELECT * FROM Hold_Info WHERE User_id = ?", (id2,))
                                mon_hold2 = cur.fetchone()
                                cur.execute("SELECT * FROM Mon_Info WHERE Mon_id = ?", (mon_hold2['Mon_id'],))
                                mon2 = cur.fetchone()
                                cur.execute("SELECT * FROM User_Info WHERE User_id = ?", (id2,))
                                user_i2 = cur.fetchone()
                                cur.execute("SELECT * FROM Stat_Info WHERE User_id = ?", (id2,))
                                stat2 = cur.fetchone()
                                user2_hp1 = (mon2['Mon_hp'] + stat2['A_hp'])
                                user2_hp2 = (mon2['Mon_hp'] + stat2['A_hp'])
                                user2_atk = (mon2['Mon_atk'] + stat2['A_atk'])
                                user2_def = (mon2['Mon_def'] + stat2['A_def'])
                                user2_dex = (mon2['Mon_dex'] + stat2['A_dex'])
                                user2_luk = (mon2['Mon_luk'] + stat2['A_luk'])
                                user2_avoid = int((1 - (user2_luk * 1.5 / (user2_luk * 1.5 + 100))) * 100)
                                user2_skillpoint = int(1 + (user2_luk / 11))
                                embed=discord.Embed(title=mon2['Mon_name'], description=mon2['Mon_grade'], color=0x00ff56)
                                embed.set_author(name=nick2, url="https://lastidolnote.com/", icon_url=user.avatar_url)
                                embed.set_image(url=mon2['etc1'])
                                embed.add_field(name="> 레벨", value=mon_hold2['Mon_level'], inline=True)
                                embed.add_field(name="> 체력", value=mon2['Mon_hp'] + stat2['A_hp'], inline=True)
                                embed.add_field(name="> 공격", value=mon2['Mon_atk'] + stat2['A_atk'], inline=True)
                                embed.add_field(name="> 방어", value=mon2['Mon_def'] + stat2['A_def'], inline=True)
                                embed.add_field(name="> 민첩", value=mon2['Mon_dex'] + stat2['A_dex'], inline=True)
                                embed.add_field(name="> 행운", value=mon2['Mon_luk'] + stat2['A_luk'], inline=True)
                                embed.add_field(name="> 보유골드", value=user_i2['money'], inline=True)
                                embed.add_field(name="> 레벨업 토큰", value=user_i2['Lvtk'], inline=True)
                                embed.set_footer(text="by Mujiseong")
                                await ctx.send(embed=embed)
                                who_1 = 0
                                who_2 = 0
                                user1Speed = random.randint(1, user1_dex)
                                user2Speed = random.randint(1, user2_dex)
                                while f_end == 0 :
                                    if user1Speed == user2Speed and who_1 != 1 and who_2 != 1 :
                                        embed = discord.Embed(title = '서로의 빈틈을 노려보지만 틈이 도저히 보이지 않습니다', description = '선공 결정 롤링!', color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        who_f = random.randint(1,2)
                                        if who_f == 1 :
                                            embed = discord.Embed(title = '선공 주사위 결과는 %s!'%(who_f), description = '%s의 선공입니다'%(nick), color = 0xff0000)
                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                            await ctx.send(embed = embed)
                                            who_1 = 1
                                        elif who_f == 2 :
                                            embed = discord.Embed(title = '선공 주사위 결과는 %s!'%(who_f), description = '%s의 선공입니다'%(nick2), color = 0xff0000)
                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                            await ctx.send(embed = embed)
                                            who_2 = 1                        
                                    elif user1Speed > user2Speed or who_1 == 1 :
                                        embed = discord.Embed(title = '%s의 발걸음이 가볍습니다'%(nick), description = '%s의 선공!'%(nick), color = 0xff0000)
                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                        await ctx.send(embed = embed)
                                        user1_f = 1
                                        user2_f = 0
                                        while f_end == 0 :
                                            if user1_f > user2_f :
                                                embed = discord.Embed(title = '%s님 원하시는 행동을 선택해주세요'%(nick), description = '일반공격 = %s\n특수기 = %s\n항복 = %s'%(atk, skill, battlerun), color = 0xff0000)
                                                msg = await ctx.channel.send(embed = embed)
                                                await msg.add_reaction(atk)
                                                await msg.add_reaction(skill)
                                                await msg.add_reaction(battlerun)                           
                                                try :
                                                    def checking2(reaction, user) :
                                                        return str(reaction) in [atk, skill, battlerun] and user != bot.user and user.id == id
                                                    reaction, user = await bot.wait_for('reaction_add', check=checking2)
                                                    if (str(reaction)) == battlerun :
                                                        embed = discord.Embed(title = '%s님이 항복하였습니다'%(nick), description = '배틀이 종료되었습니다', color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                        dummy_check = cur.fetchone()
                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                        dummy_check2 = cur.fetchone()
                                                        if dummy_check == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                        if dummy_check2 == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                        score_i = cur.fetchone()
                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                        score_i2 = cur.fetchone()
                                                        if score_i == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                        if score_i2 == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))      
                                                        con.close()
                                                        f_end += 1
                                                        break
                                                    elif (str(reaction)) == atk :
                                                        cri = random.randint(1,125)
                                                        power = random.randint(0, user1_atk)
                                                        shield = random.randint(0, user2_def)
                                                        avoid = random.randint(1,100)
                                                        if power == 0 :
                                                            embed = discord.Embed(title = '아이쿠!', description = '손이 미끄러져 공격에 실패했다', color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            user2_f += 1
                                                        elif user1_dex >= cri :
                                                            damage = ((power * 2) - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon2['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick2), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user2_luk >= random.randint(1,125) :
                                                                    user1_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick2), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user1_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)    
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user2_f += 1
                                                            elif user2_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick2), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                            else :
                                                                user2_hp1 -= damage
                                                                embed = discord.Embed(title = '크리티컬!', description = '공격 주사위 결과 값 2배! %s로 상승!'%(power*2), color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                                if user2_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id))    
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break
                                                        elif power >= user1_atk / 2 :
                                                            damage = (power - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon2['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick2), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user2_luk >= random.randint(1,125) :
                                                                    user1_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick2), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user1_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user2_f += 1
                                                            elif user2_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick2), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                            else :
                                                                user2_hp1 -= damage
                                                                embed = discord.Embed(title = '정확하게 파고들어 공격을 성공시켰다', description = '놀라운 기량!', color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                                if user2_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break            
                                                        elif power < user1_atk / 2 :
                                                            damage = (power - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon2['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick2), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user2_luk >= random.randint(1,125) :
                                                                    user1_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick2), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user1_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user2_f += 1
                                                            elif user2_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick2), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                            else :
                                                                user2_hp1 -= damage
                                                                embed = discord.Embed(title = '스탭이 흐트러진 맥이 빠진 공격', description = '절반의 힘도 발휘하지 못했다', color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                                if user2_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break
                                                    elif (str(reaction)) == skill :
                                                        if user1_skillpoint != 0 :
                                                            coin_toss = random.randint(1,2)
                                                            if coin_toss == 1 :
                                                                embed = discord.Embed(color=1768431, title=f"휘리릭!", type="rich")
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMjA5/MDAxNjQ3MzQ3MzUwNjMy.EM2ceTGMmdDt-AWweajuaJmzhDZ3Z1_LrD6UmNEfOe0g.P8ZRoc9OnvI3bhzdyw0a5ztHErI5fPGzQq7qYtl83XYg.GIF.devjune92/coin_roll.gif?type=w773")                                
                                                                botMsg = await ctx.send(embed=embed)
                                                                await asyncio.sleep(3)
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMTg3/MDAxNjQ3MzQ3MzcwMjMz.mwYF709u9lCXsfBnikf_3nutFwqENWovk4VoQDUnENAg.RKErb7gYN4ESok7zxb_ZjlIM-z1BgrOdMP_fyyO2NjYg.PNG.devjune92/coin_front.png?type=w773")
                                                                await botMsg.edit(embed=embed)
                                                                await asyncio.sleep(1)
                                                                skill_atk = 50
                                                                embed = discord.Embed(title = '행운의 여신이 당신에게 미소짓습니다!', description = '1~50 주사위 굴림!', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                            elif coin_toss == 2 :
                                                                embed = discord.Embed(color=1768431, title=f"휘리릭!", type="rich")
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMjA5/MDAxNjQ3MzQ3MzUwNjMy.EM2ceTGMmdDt-AWweajuaJmzhDZ3Z1_LrD6UmNEfOe0g.P8ZRoc9OnvI3bhzdyw0a5ztHErI5fPGzQq7qYtl83XYg.GIF.devjune92/coin_roll.gif?type=w773")                                
                                                                botMsg = await ctx.send(embed=embed)
                                                                await asyncio.sleep(3)
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfNjIg/MDAxNjQ3MzQ3Mzg4NDAz.toisCb_OI-Ol7bP-y24gO1vynTReCvdXoxGkco2Kuzcg.tZnI5Vm_Fxo7styOWXS4ipxx9OFU3Kh9L9X1Nw8BFgkg.PNG.devjune92/coin_back.png?type=w773")
                                                                await botMsg.edit(embed=embed)
                                                                await asyncio.sleep(1)
                                                                skill_atk = 10
                                                                embed = discord.Embed(title = '행운의 여신이 당신에게 등을 돌립니다...', description = '1~10 주사위 굴림', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                            power = random.randint(1, skill_atk)
                                                            user2_hp1 -= power
                                                            embed = discord.Embed(title = '%s에게 %s데미지!'%(nick2, power), description = '%s의 남은 HP = %s/%s'%(nick2, user2_hp1, user2_hp2), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            user2_f += 1 
                                                            user1_skillpoint -= 1      
                                                            if user2_hp1 <= 0 :
                                                                embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                dummy_check = cur.fetchone()
                                                                cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                dummy_check2 = cur.fetchone()
                                                                if dummy_check == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                if dummy_check2 == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                score_i = cur.fetchone()
                                                                cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                score_i2 = cur.fetchone()
                                                                if score_i == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                if score_i2 == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id))    
                                                                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                Task_i = cur.fetchone()
                                                                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                Task_i2 = cur.fetchone()
                                                                cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                battle_i = cur.fetchone()
                                                                cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                battle_i2 = cur.fetchone()
                                                                for already_battle in battle_i :
                                                                    for already_battle2 in battle_i2 :
                                                                        if nick4 in already_battle :
                                                                            embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                            await ctx.send(embed = embed)
                                                                        else :
                                                                            if Task_i['Battle_num'] == 3 :
                                                                                embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)                                                                                
                                                                            else :
                                                                                End_battle = already_battle + nick4
                                                                                cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            if Task_i2['Battle_num'] == 3 :
                                                                                embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                await ctx.send(embed = embed)      
                                                                            else :
                                                                                End_battle2 = already_battle2 + nick3
                                                                                cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                await ctx.send(embed = embed)  
                                                                con.close()
                                                                f_end += 1
                                                                break       
                                                        else :
                                                            embed = discord.Embed(title = '스킬 사용 가능 횟수가 0입니다', description = '다시 선택해주세요', color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)                    
                                                except : pass                                                                        
                                            elif user1_f <= user2_f :
                                                embed = discord.Embed(title = '%s님 원하시는 행동을 선택해주세요'%(nick2), description = '일반공격 = %s\n특수기 = %s\n항복 = %s'%(atk, skill, battlerun), color = 0xff0000)
                                                msg = await ctx.channel.send(embed = embed)
                                                await msg.add_reaction(atk)
                                                await msg.add_reaction(skill)
                                                await msg.add_reaction(battlerun)
                                                try :
                                                    def checking3(reaction, user) :
                                                        return str(reaction) in [atk, skill, battlerun] and user != bot.user and user.id == id2
                                                    reaction, user = await bot.wait_for('reaction_add', check=checking3)
                                                    if (str(reaction)) == battlerun :
                                                        embed = discord.Embed(title = '%s님이 항복하였습니다'%(nick2), description = '배틀이 종료되었습니다', color = 0xff0000)
                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                        dummy_check = cur.fetchone()
                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                        dummy_check2 = cur.fetchone()
                                                        if dummy_check == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                        if dummy_check2 == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                        score_i = cur.fetchone()
                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                        score_i2 = cur.fetchone()
                                                        if score_i == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                        if score_i2 == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                        con.close()
                                                        f_end += 1
                                                        break
                                                    elif (str(reaction)) == atk :
                                                        cri = random.randint(1,125)
                                                        power = random.randint(0, user2_atk)
                                                        shield = random.randint(0, user1_def)
                                                        avoid = random.randint(1,100)
                                                        if power == 0 :
                                                            embed = discord.Embed(title = '아이쿠!', description = '손이 미끄러져 공격에 실패했다', color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            user1_f += 1
                                                        elif user2_dex >= cri :
                                                            damage = ((power * 2) - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick2), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user1_luk >= random.randint(1,125) :
                                                                    user2_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user2_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user1_f += 1
                                                            elif user1_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                            else :
                                                                user1_hp1 -= damage
                                                                embed = discord.Embed(title = '크리티컬!', description = '공격 주사위 결과 값 2배! %s로 상승!'%(power*2), color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                                if user1_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break
                                                        elif power >= user2_atk / 2 :
                                                            damage = (power - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick2), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user1_luk >= random.randint(1,125) :
                                                                    user2_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user2_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user1_f += 1
                                                            elif user1_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                            else :
                                                                user1_hp1 -= damage
                                                                embed = discord.Embed(title = '정확하게 파고들어 공격을 성공시켰다', description = '놀라운 기량!', color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                                if user1_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break            
                                                        elif power < user2_atk / 2 :
                                                            damage = (power - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick2), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user1_luk >= random.randint(1,125) :
                                                                    user2_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user2_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user1_f += 1
                                                            elif user1_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                            else :
                                                                user1_hp1 -= damage
                                                                embed = discord.Embed(title = '스탭이 흐트러진 맥이 빠진 공격', description = '절반의 힘도 발휘하지 못했다', color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                                if user1_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break
                                                    elif (str(reaction)) == skill :
                                                        if user2_skillpoint != 0 :
                                                            coin_toss = random.randint(1,2)
                                                            if coin_toss == 1 :
                                                                embed = discord.Embed(color=1768431, title=f"휘리릭!", type="rich")
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMjA5/MDAxNjQ3MzQ3MzUwNjMy.EM2ceTGMmdDt-AWweajuaJmzhDZ3Z1_LrD6UmNEfOe0g.P8ZRoc9OnvI3bhzdyw0a5ztHErI5fPGzQq7qYtl83XYg.GIF.devjune92/coin_roll.gif?type=w773")                                
                                                                botMsg = await ctx.send(embed=embed)
                                                                await asyncio.sleep(3)
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMTg3/MDAxNjQ3MzQ3MzcwMjMz.mwYF709u9lCXsfBnikf_3nutFwqENWovk4VoQDUnENAg.RKErb7gYN4ESok7zxb_ZjlIM-z1BgrOdMP_fyyO2NjYg.PNG.devjune92/coin_front.png?type=w773")
                                                                await botMsg.edit(embed=embed)
                                                                await asyncio.sleep(1)
                                                                skill_atk = 50
                                                                embed = discord.Embed(title = '행운의 여신이 당신에게 미소짓습니다!', description = '1~50 주사위 굴림!', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                            elif coin_toss == 2 :
                                                                embed = discord.Embed(color=1768431, title=f"휘리릭!", type="rich")
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMjA5/MDAxNjQ3MzQ3MzUwNjMy.EM2ceTGMmdDt-AWweajuaJmzhDZ3Z1_LrD6UmNEfOe0g.P8ZRoc9OnvI3bhzdyw0a5ztHErI5fPGzQq7qYtl83XYg.GIF.devjune92/coin_roll.gif?type=w773")                                
                                                                botMsg = await ctx.send(embed=embed)
                                                                await asyncio.sleep(3)
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfNjIg/MDAxNjQ3MzQ3Mzg4NDAz.toisCb_OI-Ol7bP-y24gO1vynTReCvdXoxGkco2Kuzcg.tZnI5Vm_Fxo7styOWXS4ipxx9OFU3Kh9L9X1Nw8BFgkg.PNG.devjune92/coin_back.png?type=w773")
                                                                await botMsg.edit(embed=embed)
                                                                await asyncio.sleep(1)
                                                                skill_atk = 10
                                                                embed = discord.Embed(title = '행운의 여신이 당신에게 등을 돌립니다...', description = '1~10 주사위 굴림', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                            power = random.randint(1, skill_atk)
                                                            user1_hp1 -= power
                                                            embed = discord.Embed(title = '%s에게 %s데미지!'%(nick, power), description = '%s의 남은 HP = %s/%s'%(nick, user1_hp1, user1_hp2), color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            user1_f += 1 
                                                            user2_skillpoint -= 1      
                                                            if user1_hp1 <= 0 :
                                                                embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                dummy_check = cur.fetchone()
                                                                cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                dummy_check2 = cur.fetchone()
                                                                if dummy_check == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                if dummy_check2 == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                score_i = cur.fetchone()
                                                                cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                score_i2 = cur.fetchone()
                                                                if score_i == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                if score_i2 == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                Task_i = cur.fetchone()
                                                                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                Task_i2 = cur.fetchone()
                                                                cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                battle_i = cur.fetchone()
                                                                cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                battle_i2 = cur.fetchone()
                                                                for already_battle in battle_i :
                                                                    for already_battle2 in battle_i2 :
                                                                        if nick4 in already_battle :
                                                                            embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                            await ctx.send(embed = embed)
                                                                        else :
                                                                            if Task_i['Battle_num'] == 3 :
                                                                                embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)                                                                                
                                                                            else :
                                                                                End_battle = already_battle + nick4
                                                                                cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            if Task_i2['Battle_num'] == 3 :
                                                                                embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                await ctx.send(embed = embed)      
                                                                            else :
                                                                                End_battle2 = already_battle2 + nick3
                                                                                cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                await ctx.send(embed = embed)    
                                                                con.close()
                                                                f_end += 1
                                                                break
                                                        else :
                                                            embed = discord.Embed(title = '스킬 사용 가능 횟수가 0입니다', description = '다시 선택해주세요', color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)          
                                                except : pass
                                    elif user2Speed > user1Speed or who_2 == 1 :
                                        embed = discord.Embed(title = '%s의 발걸음이 가볍습니다'%(nick2), description = '%s의 선공!'%(nick2), color = 0xff0000)
                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                        await ctx.send(embed = embed)
                                        user2_f = 1
                                        user1_f = 0
                                        while f_end == 0 : 
                                            if user1_f < user2_f :
                                                embed = discord.Embed(title = '%s님 원하시는 행동을 선택해주세요'%(nick2), description = '일반공격 = %s\n특수기 = %s\n항복 = %s'%(atk, skill, battlerun), color = 0xff0000)
                                                msg = await ctx.channel.send(embed = embed)
                                                await msg.add_reaction(atk)
                                                await msg.add_reaction(skill)
                                                await msg.add_reaction(battlerun)
                                                try :
                                                    def checking3(reaction, user) :
                                                        return str(reaction) in [atk, skill, battlerun] and user != bot.user and user.id == id2
                                                    reaction, user = await bot.wait_for('reaction_add', check=checking3)
                                                    if (str(reaction)) == battlerun :
                                                        embed = discord.Embed(title = '%s님이 항복하였습니다'%(nick2), description = '배틀이 종료되었습니다', color = 0xff0000)
                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                        dummy_check = cur.fetchone()
                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                        dummy_check2 = cur.fetchone()
                                                        if dummy_check == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                        if dummy_check2 == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                        score_i = cur.fetchone()
                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                        score_i2 = cur.fetchone()
                                                        if score_i == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                        if score_i2 == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                        con.close()
                                                        f_end += 1
                                                        break
                                                    elif (str(reaction)) == atk :
                                                        cri = random.randint(1,125)
                                                        power = random.randint(0, user2_atk)
                                                        shield = random.randint(0, user1_def)
                                                        avoid = random.randint(1,100)
                                                        if power == 0 :
                                                            embed = discord.Embed(title = '아이쿠!', description = '손이 미끄러져 공격에 실패했다', color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            user1_f += 1
                                                        elif user2_dex >= cri :
                                                            damage = ((power * 2) - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick2), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user1_luk >= random.randint(1,125) :
                                                                    user2_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user2_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user1_f += 1
                                                            elif user1_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                            else :
                                                                user1_hp1 -= damage
                                                                embed = discord.Embed(title = '크리티컬!', description = '공격 주사위 결과 값 2배! %s로 상승!'%(power*2), color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                                if user1_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break
                                                        elif power >= user2_atk / 2 :
                                                            damage = (power - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick2), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user1_luk >= random.randint(1,125) :
                                                                    user2_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user2_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user1_f += 1
                                                            elif user1_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                            else :
                                                                user1_hp1 -= damage
                                                                embed = discord.Embed(title = '정확하게 파고들어 공격을 성공시켰다', description = '놀라운 기량!', color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                                if user1_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break            
                                                        elif power < user2_atk / 2 :
                                                            damage = (power - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick2), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user1_luk >= random.randint(1,125) :
                                                                    user2_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user2_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user1_f += 1
                                                            elif user1_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                            else :
                                                                user1_hp1 -= damage
                                                                embed = discord.Embed(title = '스탭이 흐트러진 맥이 빠진 공격', description = '절반의 힘도 발휘하지 못했다', color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user1_f += 1
                                                                if user1_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break
                                                    elif (str(reaction)) == skill :
                                                        if user2_skillpoint != 0 :
                                                            coin_toss = random.randint(1,2)
                                                            if coin_toss == 1 :
                                                                embed = discord.Embed(color=1768431, title=f"휘리릭!", type="rich")
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMjA5/MDAxNjQ3MzQ3MzUwNjMy.EM2ceTGMmdDt-AWweajuaJmzhDZ3Z1_LrD6UmNEfOe0g.P8ZRoc9OnvI3bhzdyw0a5ztHErI5fPGzQq7qYtl83XYg.GIF.devjune92/coin_roll.gif?type=w773")                                
                                                                botMsg = await ctx.send(embed=embed)
                                                                await asyncio.sleep(3)
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMTg3/MDAxNjQ3MzQ3MzcwMjMz.mwYF709u9lCXsfBnikf_3nutFwqENWovk4VoQDUnENAg.RKErb7gYN4ESok7zxb_ZjlIM-z1BgrOdMP_fyyO2NjYg.PNG.devjune92/coin_front.png?type=w773")
                                                                await botMsg.edit(embed=embed)
                                                                await asyncio.sleep(1)
                                                                skill_atk = 50
                                                                embed = discord.Embed(title = '행운의 여신이 당신에게 미소짓습니다!', description = '1~50 주사위 굴림!', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                            elif coin_toss == 2 :
                                                                embed = discord.Embed(color=1768431, title=f"휘리릭!", type="rich")
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMjA5/MDAxNjQ3MzQ3MzUwNjMy.EM2ceTGMmdDt-AWweajuaJmzhDZ3Z1_LrD6UmNEfOe0g.P8ZRoc9OnvI3bhzdyw0a5ztHErI5fPGzQq7qYtl83XYg.GIF.devjune92/coin_roll.gif?type=w773")                                
                                                                botMsg = await ctx.send(embed=embed)
                                                                await asyncio.sleep(3)
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfNjIg/MDAxNjQ3MzQ3Mzg4NDAz.toisCb_OI-Ol7bP-y24gO1vynTReCvdXoxGkco2Kuzcg.tZnI5Vm_Fxo7styOWXS4ipxx9OFU3Kh9L9X1Nw8BFgkg.PNG.devjune92/coin_back.png?type=w773")
                                                                await botMsg.edit(embed=embed)
                                                                await asyncio.sleep(1)
                                                                skill_atk = 10
                                                                embed = discord.Embed(title = '행운의 여신이 당신에게 등을 돌립니다...', description = '1~10 주사위 굴림', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                            power = random.randint(1, skill_atk)
                                                            user1_hp1 -= power
                                                            embed = discord.Embed(title = '%s에게 %s데미지!'%(nick, power), description = '%s의 남은 HP = %s/%s'%(nick, user1_hp1, user1_hp2), color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            user1_f += 1 
                                                            user2_skillpoint -= 1      
                                                            if user1_hp1 <= 0 :
                                                                embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                dummy_check = cur.fetchone()
                                                                cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                dummy_check2 = cur.fetchone()
                                                                if dummy_check == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                if dummy_check2 == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                score_i = cur.fetchone()
                                                                cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                score_i2 = cur.fetchone()
                                                                if score_i == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                if score_i2 == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                Task_i = cur.fetchone()
                                                                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                Task_i2 = cur.fetchone()
                                                                cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                battle_i = cur.fetchone()
                                                                cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                battle_i2 = cur.fetchone()
                                                                for already_battle in battle_i :
                                                                    for already_battle2 in battle_i2 :
                                                                        if nick4 in already_battle :
                                                                            embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                            await ctx.send(embed = embed)
                                                                        else :
                                                                            if Task_i['Battle_num'] == 3 :
                                                                                embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)                                                                                
                                                                            else :
                                                                                End_battle = already_battle + nick4
                                                                                cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            if Task_i2['Battle_num'] == 3 :
                                                                                embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                await ctx.send(embed = embed)      
                                                                            else :
                                                                                End_battle2 = already_battle2 + nick3
                                                                                cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                await ctx.send(embed = embed)    
                                                                con.close()
                                                                f_end += 1
                                                                break
                                                        else :
                                                            embed = discord.Embed(title = '스킬 사용 가능 횟수가 0입니다', description = '다시 선택해주세요', color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)
                                                except : pass
                                            elif user1_f >= user2_f :
                                                embed = discord.Embed(title = '%s님 원하시는 행동을 선택해주세요'%(nick), description = '일반공격 = %s\n특수기 = %s\n항복 = %s'%(atk, skill, battlerun), color = 0xff0000)
                                                msg = await ctx.channel.send(embed = embed)
                                                await msg.add_reaction(atk)
                                                await msg.add_reaction(skill)     
                                                await msg.add_reaction(battlerun)                        
                                                try :
                                                    def checking2(reaction, user) :
                                                        return str(reaction) in [atk, skill, battlerun] and user != bot.user and user.id == id
                                                    reaction, user = await bot.wait_for('reaction_add', check=checking2)
                                                    if (str(reaction)) == battlerun :
                                                        embed = discord.Embed(title = '%s님이 항복하였습니다'%(nick), description = '배틀이 종료되었습니다', color = 0xff0000)
                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                        await ctx.send(embed = embed)
                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                        dummy_check = cur.fetchone()
                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                        dummy_check2 = cur.fetchone()
                                                        if dummy_check == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                        if dummy_check2 == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                        score_i = cur.fetchone()
                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                        score_i2 = cur.fetchone()
                                                        if score_i == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                        if score_i2 == None :
                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2)) 
                                                        con.close()
                                                        f_end += 1
                                                        break
                                                    elif (str(reaction)) == atk :
                                                        cri = random.randint(1,125)
                                                        power = random.randint(0, user1_atk)
                                                        shield = random.randint(0, user2_def)
                                                        avoid = random.randint(1,100)
                                                        if power == 0 :
                                                            embed = discord.Embed(title = '아이쿠!', description = '손이 미끄러져 공격에 실패했다', color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            user2_f += 1
                                                        elif user1_dex >= cri :
                                                            damage = ((power * 2) - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon2['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick2), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user2_luk >= random.randint(1,125) :
                                                                    user1_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick2), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user1_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user2_f += 1
                                                            elif user2_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick2), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                            else :
                                                                user2_hp1 -= damage
                                                                embed = discord.Embed(title = '크리티컬!', description = '공격 주사위 결과 값 2배! %s로 상승!'%(power*2), color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                                if user2_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break
                                                        elif power >= user1_atk / 2 :
                                                            damage = (power - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon2['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick2), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user2_luk >= random.randint(1,125) :
                                                                    user1_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick2), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user1_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user2_f += 1
                                                            elif user2_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick2), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                            else :
                                                                user2_hp1 -= damage
                                                                embed = discord.Embed(title = '정확하게 파고들어 공격을 성공시켰다', description = '놀라운 기량!', color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                                if user2_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break            
                                                        elif power < user1_atk / 2 :
                                                            damage = (power - shield)
                                                            embed = discord.Embed(title = '%s의 공격선언!'%(nick), description = '공격 주사위 결과 %s\n%s의 방어 주사위 결과 %s'%(power,mon2['Mon_name'],shield), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            if damage <= 0 :
                                                                embed = discord.Embed(title = '%s의 방어성공!'%(nick2), description = '아무런 데미지도 주지 못했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                if user2_luk >= random.randint(1,125) :
                                                                    user1_hp1 -= shield
                                                                    embed = discord.Embed(title = '공격을 방어당한 상대의 자세가 흐트러졌다!', description = '%s의 방어 주사위 기반 어택!'%(nick2), color = 0xff0000)
                                                                    embed.add_field(name="%s의 데미지를 입혔다"%(shield), value="%s의 남은 HP = %s/%s"%(nick, user1_hp1, user1_hp2), inline=True)
                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    if user1_hp1 <= 0 :
                                                                        embed = discord.Embed(title = '%s의 승리!'%(nick2), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                        await ctx.send(embed = embed)
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                        cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                        dummy_check = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                        dummy_check2 = cur.fetchone()
                                                                        if dummy_check == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                        if dummy_check2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                        score_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                        score_i2 = cur.fetchone()
                                                                        if score_i == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                        if score_i2 == None :
                                                                            cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                        cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick4, id))
                                                                        cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick3, id2))    
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        Task_i = cur.fetchone()
                                                                        cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        Task_i2 = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                        battle_i = cur.fetchone()
                                                                        cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                        battle_i2 = cur.fetchone()
                                                                        for already_battle in battle_i :
                                                                            for already_battle2 in battle_i2 :
                                                                                if nick4 in already_battle :
                                                                                    embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                else :
                                                                                    if Task_i['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)                                                                                
                                                                                    else :
                                                                                        End_battle = already_battle + nick4
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                        await ctx.send(embed = embed)
                                                                                    if Task_i2['Battle_num'] == 3 :
                                                                                        embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)      
                                                                                    else :
                                                                                        End_battle2 = already_battle2 + nick3
                                                                                        cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                        cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                        embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                        embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                        await ctx.send(embed = embed)  
                                                                        con.close()
                                                                        f_end += 1
                                                                        break
                                                                user2_f += 1
                                                            elif user2_avoid < avoid :
                                                                embed = discord.Embed(title = '%s의 회피성공!'%(nick2), description = '놀라운 행운으로 공격을 회피했다', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                            else :
                                                                user2_hp1 -= damage
                                                                embed = discord.Embed(title = '스탭이 흐트러진 맥이 빠진 공격', description = '절반의 힘도 발휘하지 못했다', color = 0xff0000)
                                                                embed.add_field(name="%s의 데미지를 입혔다"%(damage), value="%s의 남은 HP = %s/%s"%(nick2, user2_hp1, user2_hp2), inline=True)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                user2_f += 1
                                                                if user2_hp1 <= 0 :
                                                                    embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                    await ctx.send(embed = embed)
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                    cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                    dummy_check = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                    dummy_check2 = cur.fetchone()
                                                                    if dummy_check == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                    if dummy_check2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                    score_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                    score_i2 = cur.fetchone()
                                                                    if score_i == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                    if score_i2 == None :
                                                                        cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                    cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                    cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id)) 
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    Task_i = cur.fetchone()
                                                                    cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    Task_i2 = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                    battle_i = cur.fetchone()
                                                                    cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                    battle_i2 = cur.fetchone()
                                                                    for already_battle in battle_i :
                                                                        for already_battle2 in battle_i2 :
                                                                            if nick4 in already_battle :
                                                                                embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            else :
                                                                                if Task_i['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)                                                                                
                                                                                else :
                                                                                    End_battle = already_battle + nick4
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                    await ctx.send(embed = embed)
                                                                                if Task_i2['Battle_num'] == 3 :
                                                                                    embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)      
                                                                                else :
                                                                                    End_battle2 = already_battle2 + nick3
                                                                                    cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                    cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                    embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                    embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                    await ctx.send(embed = embed)  
                                                                    con.close()
                                                                    f_end += 1
                                                                    break
                                                    elif (str(reaction)) == skill :
                                                        if user1_skillpoint != 0 :
                                                            coin_toss = random.randint(1,2)
                                                            if coin_toss == 1 :
                                                                embed = discord.Embed(color=1768431, title=f"휘리릭!", type="rich")
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMjA5/MDAxNjQ3MzQ3MzUwNjMy.EM2ceTGMmdDt-AWweajuaJmzhDZ3Z1_LrD6UmNEfOe0g.P8ZRoc9OnvI3bhzdyw0a5ztHErI5fPGzQq7qYtl83XYg.GIF.devjune92/coin_roll.gif?type=w773")                                
                                                                botMsg = await ctx.send(embed=embed)
                                                                await asyncio.sleep(3)
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMTg3/MDAxNjQ3MzQ3MzcwMjMz.mwYF709u9lCXsfBnikf_3nutFwqENWovk4VoQDUnENAg.RKErb7gYN4ESok7zxb_ZjlIM-z1BgrOdMP_fyyO2NjYg.PNG.devjune92/coin_front.png?type=w773")
                                                                await botMsg.edit(embed=embed)
                                                                await asyncio.sleep(1)
                                                                skill_atk = 50
                                                                embed = discord.Embed(title = '행운의 여신이 당신에게 미소짓습니다!', description = '1~50 주사위 굴림!', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                            elif coin_toss == 2 :
                                                                embed = discord.Embed(color=1768431, title=f"휘리릭!", type="rich")
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfMjA5/MDAxNjQ3MzQ3MzUwNjMy.EM2ceTGMmdDt-AWweajuaJmzhDZ3Z1_LrD6UmNEfOe0g.P8ZRoc9OnvI3bhzdyw0a5ztHErI5fPGzQq7qYtl83XYg.GIF.devjune92/coin_roll.gif?type=w773")                                
                                                                botMsg = await ctx.send(embed=embed)
                                                                await asyncio.sleep(3)
                                                                embed.set_image(url="https://postfiles.pstatic.net/MjAyMjAzMTVfNjIg/MDAxNjQ3MzQ3Mzg4NDAz.toisCb_OI-Ol7bP-y24gO1vynTReCvdXoxGkco2Kuzcg.tZnI5Vm_Fxo7styOWXS4ipxx9OFU3Kh9L9X1Nw8BFgkg.PNG.devjune92/coin_back.png?type=w773")
                                                                await botMsg.edit(embed=embed)
                                                                await asyncio.sleep(1)
                                                                skill_atk = 10
                                                                embed = discord.Embed(title = '행운의 여신이 당신에게 등을 돌립니다...', description = '1~10 주사위 굴림', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                            power = random.randint(1, skill_atk)
                                                            user2_hp1 -= power
                                                            embed = discord.Embed(title = '%s에게 %s데미지!'%(nick2, power), description = '%s의 남은 HP = %s/%s'%(nick2, user2_hp1, user2_hp2), color = 0xff0000)
                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                            await ctx.send(embed = embed)
                                                            user2_f += 1       
                                                            user1_skillpoint -= 1  
                                                            if user2_hp1 <= 0 :
                                                                embed = discord.Embed(title = '%s의 승리!'%(nick), description = '🎉승리를 축하합니다!🎉', color = 0xff0000)
                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                await ctx.send(embed = embed)
                                                                cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick3))
                                                                cur.execute("CREATE TABLE IF NOT EXISTS %s (User_id INTEGER PRIMARY KEY, User_nick TEXT, W INTEGER, L INTEGER)"%(nick4))
                                                                cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick3))
                                                                dummy_check = cur.fetchone()
                                                                cur.execute("SELECT * FROM %s WHERE User_id = 1"%(nick4))
                                                                dummy_check2 = cur.fetchone()
                                                                if dummy_check == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (1, "dummy", 0, 0))
                                                                if dummy_check2 == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (1, "dummy", 0, 0))
                                                                cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick3, id2))
                                                                score_i = cur.fetchone()
                                                                cur.execute("SELECT * FROM %s WHERE User_id = %s"%(nick4, id))
                                                                score_i2 = cur.fetchone()
                                                                if score_i == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick3), (id2, nick4, 0, 0))
                                                                if score_i2 == None :
                                                                    cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?)"%(nick4), (id, nick3, 0, 0))      
                                                                cur.execute("UPDATE %s SET W = W + 1 WHERE User_id = %s"%(nick3, id2))
                                                                cur.execute("UPDATE %s SET L = L + 1 WHERE User_id = %s"%(nick4, id))    
                                                                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id,))
                                                                Task_i = cur.fetchone()
                                                                cur.execute("SELECT * FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                Task_i2 = cur.fetchone()
                                                                cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id,))
                                                                battle_i = cur.fetchone()
                                                                cur.execute("SELECT Battle_name FROM Task_Info WHERE User_Id = ?", (id2,))
                                                                battle_i2 = cur.fetchone()
                                                                for already_battle in battle_i :
                                                                    for already_battle2 in battle_i2 :
                                                                        if nick4 in already_battle :
                                                                            embed = discord.Embed(title = '오늘 이미 대전한 상대로 골드가 지급되지 않습니다', description = '다른 상대와 대전해주세요', color = 0xff0000)
                                                                            embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                            await ctx.send(embed = embed)
                                                                        else :
                                                                            if Task_i['Battle_num'] == 3 :
                                                                                embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)                                                                                
                                                                            else :
                                                                                End_battle = already_battle + nick4
                                                                                cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id))
                                                                                cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id))
                                                                                cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle, id))
                                                                                embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
                                                                                await ctx.send(embed = embed)
                                                                            if Task_i2['Battle_num'] == 3 :
                                                                                embed = discord.Embed(title = '%s님은 오늘의 대전 보상을 모두 받으셨습니다'%(nick2), description = '내일 다시 보상을 받을 수 있습니다(일일 3회)', color = 0xff0000)
                                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                await ctx.send(embed = embed)      
                                                                            else :
                                                                                End_battle2 = already_battle2 + nick3
                                                                                cur.execute("UPDATE Task_Info SET Battle_num = Battle_num + 1 WHERE User_id = %s"%(id2))
                                                                                cur.execute("UPDATE User_Info SET Money = Money + 100 WHERE User_id = %s"%(id2))
                                                                                cur.execute("UPDATE Task_Info SET Battle_name = ? WHERE User_id = ?",(End_battle2, id2))
                                                                                embed = discord.Embed(title = '파이트 보상으로 %s님에게 100골드를 지급합니다!'%(nick2), description = '또 파이트를 즐겨주세요', color = 0xff0000)
                                                                                embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                                                await ctx.send(embed = embed)  
                                                                con.close()
                                                                f_end += 1
                                                                break 
                                                        else :
                                                            embed = discord.Embed(title = '스킬 사용 가능 횟수가 0입니다', description = '다시 선택해주세요', color = 0xff0000)
                                                            embed.set_footer(text = f"{user.display_name} | by Mujiseong", icon_url = user.avatar_url)
                                                            await ctx.send(embed = embed)  
                                                except : pass          
                except : pass

bot.run(token)
                                     


# @bot.command()
# async def 테스트(ctx) :
#     id = ctx.author.id
#     redC = "⭕" 
#     blueC = "❌"
#     embed = discord.Embed(title = '테스트입니다.', description = '이모티콘 반응 실험, 무한루프 발생가능성 有', color = 0xff0000)
#     embed.add_field(name="아무거나", value=redC, inline=True)
#     embed.add_field(name="고르세요", value=blueC, inline=True)
#     await ctx.message.delete()
#     msg = await ctx.channel.send(embed = embed)
#     await msg.add_reaction(redC)
#     await msg.add_reaction(blueC)
#     fight = True
#     while fight :
#         try:
#             def checking(reaction, user):
#                 return str(reaction) in [redC, blueC] and user != bot.user      # 추가된 이모티콘이 조건 안에 있어야하고 이모티콘 추가한 사람이 봇이 아니어야함
#             reaction, user = await bot.wait_for('reaction_add', check=checking)
#             if (str(reaction)) == redC or (str(reaction)) == blueC:
#                 if user != ctx.author :   # 이모티콘 추가한 사람이 메세지를 처음 입력한 사람과 다를 경우
#                     embed = discord.Embed(title = '님이 반응하면 안됨;; 작동시킨사람이 반응해야함;', description = ctx.author.display_name + '님 이모지 선택해주세요!', color = 0xff0000)
#                     embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
#                     await ctx.send(embed = embed)
#                     print(user.display_name)        
#                 elif user == ctx.author :
#                     embed = discord.Embed(title = '어게이~ 완벽쓰~', description = '이제 파이트 코드 구현 틀 잡힘 ㅅㄱ~', color = 0xff0000)
#                     embed.set_footer(text = f"{ctx.message.author.display_name} | by Mujiseong", icon_url = ctx.message.author.avatar_url)
#                     await ctx.send(embed = embed)                    
#                     break    
#         except : pass        

#@bot.event
#async def on_message(message):
#    if message.author.bot:
#        return None
#    if (message.content.startswith("무루라이")):
#        embed = discord.Embed(title = '오늘 무루라이는 없습니다.', description = '당일 취소로 환불이 불가능하니 참고해주시기 바랍니다.', color = 0xff0000)
#        embed.set_footer(text = f"{message.author.display_name} | by Mujiseong", icon_url = message.author.avatar_url)
#        await message.channel.send(embed = embed)
#    if (message.content.startswith("무지성") or message.content.startswith("무지쿤") or message.content.startswith("무지세옹구") or message.content.startswith("지성님") or message.content.startswith("지송쿤") or message.content.startswith("지송님") or message.content.startswith("무지송") or message.content.startswith("모나지성")):
#        embed = discord.Embed(title = '무지성 현재 코딩중', description = '두뇌 풀가동!', color = 0xff0000)
#        embed.set_footer(text = f"{message.author.display_name} | by Mujiseong", icon_url = message.author.avatar_url)
#        await message.channel.send(embed = embed)


