# インストールした discord.py を読み込む
import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import random
import re
import os

#環境変数取得
TOKEN = os.environ["MY_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# 接続に必要なオブジェクトを生成
client = discord.Client()

insider = ''
master = ''
dm1 = ''
dm2 = ''
answer = ''
time_def = ''
flag = 0


print(TOKEN)

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('====================')
    print('ログインしました')
    print(client.user.name)
    print(client.user.id)
    print('====================')
    # 挨拶する
    channel = client.get_channel(CHANNEL_ID)
    await greet(channel)

# memberの情報を得る
def get_data(message):
    command = message.content
    data_table = {
        'start': message.guild.members # メンバーのリスト
    }
    return data_table.get(command, '無効なコマンドです')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
	global insider, master, dm1, dm2, answer, flag, time_def
	channel = client.get_channel(CHANNEL_ID)
	# メッセージ送信者がBotだった場合は無視する
	if message.author.bot:
		return

	if message.content == 'reset':
		await channel.send('リセットします。もう一度ゲームをする場合\"start\"と入力してください。')
		flag = 0

	if flag == 0:
		# /membersと送信した時に
		# insider, master, villagerを分類する
		if message.content == 'start':
			member_name = get_name(message)
			member_name.remove(client.user)
			while True:
				n = random.randrange(len(member_name))
				m = random.randrange(len(member_name))
				if n != m:
					break
			
			insider = member_name[n]
			master = member_name[m]
			member_name.remove(insider)
			member_name.remove(master)
			villager = member_name

			dm1 = await insider.create_dm()
			await dm1.send(f"{insider.mention}さん: あなたはインサイダーです")
			dm2 = await master.create_dm()
			await dm2.send(f"{master.mention}さん: あなたはマスターです。\"@答え\"という形で答えを入力してください。")
			for i in villager:
				dm = await i.create_dm()
				await dm.send(f"{i.mention}さん: あなたは一般人です")

			# flagを1にする
			flag = 1

	if flag == 1 and message.content.startswith('@'):
		answer = message.content
		await dm2.send("間違い無ければ👍を送ってください。もしくは、訂正してください。")
		# flagを2にする
		flag = 2

		answer = re.sub(r'@', '', answer)

	if flag == 2 and message.content == '👍':
		await dm1.send(str(answer) + ": これが答えです。")
		await dm2.send("承りました。")
		# flagを3にする
		flag = 3

	if flag == 3:
		time_def = asyncio.ensure_future(timer(channel))
		# flagを4にする
		flag = 4
	
	if flag == 4 and message.mentions:
		if insider == message.mentions[0]:
			await channel.send('正解です。' + str(insider) + 'さんがインサイダーでした。')
		elif insider != message.mentions[0]:
			await channel.send('不正解です。' + str(insider) + 'さんがインサイダーです。')

		time_def.cancel()
		# flagのリセット
		flag = 0


# タイマーの関数
async def timer(channel):
	await channel.send('今から5分間時間を測ります。答えを当ててください。')
	await asyncio.sleep(150)
	await channel.send('半分の時間が経過しました。')
	await asyncio.sleep(90)
	await channel.send('残り1分です。')
	await asyncio.sleep(30)
	await channel.send('残り30秒です。')
	await channel.sleep(20)
	await channel.send('残り10秒です。')
	await channel.sleep(10)
	await channel.send('今から投票に移ります。')

	asyncio.ensure_future(touhyou(channel))

#　投票の関数
async def touhyou(channel):
	await channel.send('3分間与えるので、インサイダーを予想してください。')
	await asyncio.sleep(90)
	await channel.send('半分の時間が経過しました。')
	await asyncio.sleep(30)
	await channel.send('残り1分です。')
	await asyncio.sleep(30)
	await channel.send('残り30秒です。')
	await channel.sleep(20)
	await channel.send('残り10秒です。')
	await channel.sleep(10)
	await channel.send('インサイダーだと思う人を決定し、名前を送ってください。')

# #　早めに完了した際に投票とタイマーのリマインドを行わない
# async def end(channel):
# 	time_def.cancel()


# memberの名前を得る
def get_name(message):
	member_name = get_data(message)

	return member_name

# チャンネルで挨拶
async def greet(channel):
	await channel.send('よろしくお願いします。ゲームを開始する場合\"start\"と入力してください。')

if __name__ == "__main__":
	# Botの起動とDiscordサーバーへの接続
	client.run(TOKEN)