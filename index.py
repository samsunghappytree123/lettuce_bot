# coding=utf-8

import discord, asyncio, ast, datetime, os, dotenv, koreanbots, sqlite3, random

dotenv.load_dotenv(verbose=True)
token = os.getenv("BOT_TOKEN")
admin = [] # 봇 관리자 목록입니다.
prefix = "상추야"

intents = discord.Intents.all()
client = discord.AutoShardedClient(intents=intents)
Bot = koreanbots.Client(client, os.getenv("KOREANBOTS_TOKEN"))

@client.event
async def on_ready():
    print(f"================================================================")
    print(f"{client.user}가 준비되었습니다.")
    print(f"접속 서버 수 : {len(client.guilds)} / 유저 수 : {len(client.users)} / 관리자 수 : {len(admin)}")
    print(f"================================================================")

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

@client.event
async def on_message(message):
    if message.author.bot or str(message.channel.type) == "private" or not message.content.startswith(prefix): return

    if message.content == prefix:
        await message.channel.send(f"{message.author.mention}님 안녕하세요? 저는 {client.user.name}입니다!!\n`커스텀 커맨드`를 소유하고 싶으시면 `삼해트의 작업실` 서버에서 문의해주세요!\n\n`상추야 서포트` 명령어로 이동하실 수 있습니다.")

    elif message.content.startswith(f"{prefix} eval"):
        if message.author.id in admin:
            try:
                prefix_count=len(prefix)+6
                cmd=message.content[prefix_count:]
                fn_name = "_eval_expr"
                cmd = cmd.strip("` ")
                # add a layer of indentation
                cmd = "\n".join(f"{i}" for i in cmd.splitlines())
                # wrap in async def body
                body = f"async def {fn_name}():\n    {cmd}"
                parsed = ast.parse(body)
                body = parsed.body[0].body
                insert_returns(body)
                env = {
                    'client': client,
                    'discord': discord,
                    'message': message,
                    '__import__': __import__
                }
                exec(compile(parsed, filename="<ast>", mode="exec"), env)
                result = (await eval(f"{fn_name}()", env))
                embed=discord.Embed(title="실행 성공", colour=discord.Colour.green(), timestamp=message.created_at)
                embed.add_field(name="`📥 Input (들어가는 내용) 📥`", value=f"```py\n{cmd}```", inline=False)
                embed.add_field(name="`📤 Output (나오는 내용) 📤`", value=f"```py\n{result}```", inline=False)
                embed.add_field(name="`🔧 Type (타입) 🔧`",value=f"```py\n{type(result)}```", inline=False)
                embed.add_field(name="`🏓 Latency (지연시간) 🏓`",value=f"```py\n{str((datetime.datetime.now()-message.created_at)*1000).split(':')[2]}```", inline=False)
                embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send(f"{message.author.mention}, 실행 중 오류가 발생하였습니다.\n\n```py\n{e}```")
        else:
            await message.channel.send(f"{message.author.mention}, 당신은 권한이 없습니다.")

    elif message.content == f"{prefix} hellothisisverification":
        await message.channel.send(f"{message.author.mention}, 저를 개발한 개발자에요!\n\n```{await client.fetch_user(726350177601978438)} / {await client.fetch_user(700561761690189875)} / {await client.fetch_user(737473348141056020)} / {await client.fetch_user(432160630682681347)}```")
    
    elif message.content.startswith(f"{prefix} 배워"):
        try:
            conn = pymysql.connect(
                user='root', 
                passwd='0317', 
                host='ip', 
                db='lettuce', 
                charset='utf8'
            )
            cur = conn.cursor()
            q = message.content.split(" ")[2]
            a = ' '.join(message.content.split(" ")[3:])
            cur.execute("SELECT * FROM custom WHERE question = '{}'".format(q))
            lists = cur.fetchone()
            if not lists == None:
                await message.channel.send(f"{message.author.mention}, 이미 알고 있는 질문이에요! 다른 질문을 해주세요. :(")
                return
            if len(q) >= 10:
                await message.channel.send(f"{message.author.mention}, 질문은 10글자를 초과하실 수 없어요!")
                return
            if len(a) == 0:
                await message.channel.send(f"{message.author.mention}, 답변을 입력해주세요!")
                return
            else:
                embed = discord.Embed(colour=discord.Colour.blurple(), title=f"{client.user.name}에게 지식 가르치기", description=f"{client.user.name}의 가르치기 서비스를 사용하기 전 주의사항을 꼭 읽어주세요!\n```md\n- 질문은 10글자를 초과하실 수 없습니다.\n- 질문에는 띄어쓰기가 들어갈 수 없어요! 띄어쓰기가 있다면 붙여 주세요.\n- {client.user.name}에게 가르친 답변은 모든 서버에서 공유되므로 주의해 주세요!\n- 누가 가르쳤는지 여부도 기록되므로 주의해 주세요!```\n\n**__`✅` 이모지를 클릭할 시 주의 사항을 읽고, 명령어 공유에 동의한 것으로 간주합니다.__**")
                embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
                m = await message.channel.send(content=message.author.mention, embed=embed)
                r = ['✅', '❎']
                for i in r:
                    await m.add_reaction(i)
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout = 60, check = lambda reaction, user: user == message.author and str(reaction.emoji) in r)
                except asyncio.TimeoutError:
                    await message.channel.send(f"{message.author.mention}, 시간이 초과되어 명령어 등록을 취소했어요... 다시 등록할 수 있으니 참고해주세요!")
                else:
                    if str(reaction.emoji) == "❎":
                        await message.channel.send(f"{message.author.mention}, 명령어 등록을 취소했어요...! 다시 등록할 수 있으니 참고해주세요!")
                    else:
                        cur.execute("INSERT INTO custom VALUES ('{}', '{}', '{}')".format(q, a, message.author.id))
                        conn.commit()
                        conn.close()
                        await message.channel.send(f"`{q}`은(는) `{a}`(이)라고요? 알려주셔서 감사합니다! {message.author.mention}님!", allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=False))
        except:
            await message.channel.send(f"{message.author.mention}, `상추야 배워 <질문> <대답>`으로 입력해보실래요?")
    
    elif message.content.startswith(f"{prefix} 잊어"): await message.channel.send(f"{message.author.mention}, 현재 개발중인 기능이에요!")

    elif message.content.startswith(f"{prefix} 도움말"): await message.channel.send(f"{message.author.mention}, 현재 도움말을 작성중이에요! 양해해주세요!")

    else:
        conn = pymysql.connect(
                user='root', 
                passwd='0317', 
                host='ip', 
                db='lettuce', 
                charset='utf8'
            )
        cur = conn.cursor()
        q = message.content.split(" ")[1]
        cur.execute("SELECT * FROM custom WHERE question = '{}'".format(q))
        lists = cur.fetchone()
        if lists == None:
            r = random.choice(['뭐라고요?', '***갸우뚱?***', '전 잘 모르겠는데요...', '뭐라고요? 잘 못들었어요!'])
            await message.channel.send(f"{message.author.mention}, {r}")
        else:
            u = await client.fetch_user(int(lists[2]))
            await message.channel.send(f"{lists[1]}\n\n```{u.name}님이 알려주셨어요!```", allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=False))

async def my_background_task():
    await client.wait_until_ready()
    while not client.is_closed():
        await client.change_presence(status=discord.Status.online, activity=discord.Game(name=f"{prefix} 도움말 | {len(client.guilds)}개의 서버에 참여"))
        await asyncio.sleep(10)
        await client.change_presence(status=discord.Status.online, activity=discord.Game(name=f"{prefix} 도움말 | {len(client.users)}명의 유저와 함께"))
        await asyncio.sleep(10)
client.loop.create_task(my_background_task())

client.run(token)
