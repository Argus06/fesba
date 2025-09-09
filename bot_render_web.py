import os
from datetime import datetime, timedelta
import pytz

jst = pytz.timezone("Asia/Tokyo")
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import discord
from discord.ext import commands
from dotenv import load_dotenv

scheduler_started = False  # ← スケジューラが起動済みかどうかを管理

# .envファイルを読み込む
load_dotenv()

# BOT_TOKENを取得
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("BOT_TOKEN が設定されていません。環境変数を確認してください。")

# Intents設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ステージとルールを番号に対応させた配列
stages = [
    "アオイの島：演舞台",
    "覇者の塔：エンブレム前",
    "エリジウム：商業区",
    "アストラ島：遺跡前",
    "リベリオンスタジアム",
    "古代遺跡：コロッセオ"
]
rules = [
    "アンテナハック",
    "キャノンエスコート"
]

# ステージとルールのデータ（例として奇数日と偶数日のデータを用意）
stages_odd = [
    {"time": "00:00", "stage": "3", "rule": "1"},
    {"time": "01:00", "stage": "2", "rule": "0"},
    {"time": "02:00", "stage": "0", "rule": "1"},
    {"time": "03:00", "stage": "5", "rule": "0"},
    {"time": "04:00", "stage": "1", "rule": "1"},
    {"time": "05:00", "stage": "1", "rule": "0"},
    {"time": "06:00", "stage": "4", "rule": "1"},
    {"time": "07:00", "stage": "2", "rule": "0"},
    {"time": "08:00", "stage": "5", "rule": "1"},
    {"time": "09:00", "stage": "0", "rule": "0"},
    {"time": "10:00", "stage": "3", "rule": "1"},
    {"time": "11:00", "stage": "3", "rule": "0"},
    {"time": "12:00", "stage": "0", "rule": "1"},
    {"time": "13:00", "stage": "2", "rule": "0"},
    {"time": "14:00", "stage": "1", "rule": "1"},
    {"time": "15:00", "stage": "4", "rule": "0"},
    {"time": "16:00", "stage": "2", "rule": "0"},
    {"time": "17:00", "stage": "5", "rule": "1"},
    {"time": "18:00", "stage": "4", "rule": "0"},
    {"time": "19:00", "stage": "3", "rule": "1"},
    {"time": "20:00", "stage": "5", "rule": "0"},
    {"time": "21:00", "stage": "0", "rule": "1"},
    {"time": "22:00", "stage": "2", "rule": "0"},
    {"time": "23:00", "stage": "1", "rule": "1"},
]
stages_even = [
    {"time": "00:00", "stage": "1", "rule": "0"},
    {"time": "01:00", "stage": "4", "rule": "1"},
    {"time": "02:00", "stage": "0", "rule": "0"},
    {"time": "03:00", "stage": "5", "rule": "1"},
    {"time": "04:00", "stage": "2", "rule": "0"},
    {"time": "05:00", "stage": "3", "rule": "1"},
    {"time": "06:00", "stage": "3", "rule": "0"},
    {"time": "07:00", "stage": "0", "rule": "1"},
    {"time": "08:00", "stage": "4", "rule": "0"},
    {"time": "09:00", "stage": "1", "rule": "1"},
    {"time": "10:00", "stage": "2", "rule": "0"},
    {"time": "11:00", "stage": "4", "rule": "1"},
    {"time": "12:00", "stage": "5", "rule": "0"},
    {"time": "13:00", "stage": "5", "rule": "1"},
    {"time": "14:00", "stage": "1", "rule": "0"},
    {"time": "15:00", "stage": "3", "rule": "1"},
    {"time": "16:00", "stage": "0", "rule": "1"},
    {"time": "17:00", "stage": "0", "rule": "0"},
    {"time": "18:00", "stage": "1", "rule": "1"},
    {"time": "19:00", "stage": "2", "rule": "0"},
    {"time": "20:00", "stage": "4", "rule": "1"},
    {"time": "21:00", "stage": "3", "rule": "0"},
    {"time": "22:00", "stage": "5", "rule": "1"},
    {"time": "23:00", "stage": "4", "rule": "0"},
]

# 毎時の投稿を実行する関数
async def send_stage_and_rule():
    now = datetime.now(pytz.utc).astimezone(jst)
    day_type = "even" if now.day % 2 == 0 else "odd"  # 偶数日か奇数日かを判定

    if day_type == "even":
        schedule = stages_even
    else:
        schedule = stages_odd

    # 現在の時刻に対応するデータを取得
    current_hour = now.strftime("%H:00")
    for entry in schedule:
        if entry["time"] == current_hour:
            stage_name = stages[int(entry["stage"])]
            rule_name = rules[int(entry["rule"])]
            message = f"{now.month}月{now.day}日 {current_hour}『{stage_name}』『{rule_name}』です。"
            channel = bot.get_channel(1357707739748368414)  # 投稿先のチャンネルIDを設定

            if channel:
                await channel.send(message)
            break

# !now コマンドの実装
@bot.command(name="now")
async def now_command(ctx):
    # 現在の時刻を取得
    now = datetime.now(pytz.utc).astimezone(jst)
    current_hour = now.strftime("%H:00")  # 時刻を "HH:00" フォーマットで統一
    day_type = "even" if now.day % 2 == 0 else "odd"  # 偶数日か奇数日かを判定

    # 偶数日と奇数日でスケジュールを切り替え
    schedule = stages_even if day_type == "even" else stages_odd

    # スケジュール内で現在の時刻を探す
    for entry in schedule:
        if entry["time"] == current_hour:
            stage_name = stages[int(entry["stage"])]  # ステージ名を取得
            rule_name = rules[int(entry["rule"])]  # ルール名を取得
            message = f"{now.month}月{now.day}日 {current_hour}『{stage_name}』『{rule_name}』です。"
            await ctx.send(message)
            return

    # 該当するスケジュールが見つからない場合
    await ctx.send(f"{now.hour}時のスケジュール情報が見つかりませんでした。")

# !next コマンドの実装
@bot.command(name="next")
async def next_stage_command(ctx):
    # 現在の時刻を取得
    now = datetime.now(pytz.utc).astimezone(jst)
    one_hour_later = now + timedelta(hours=1)  # 現在時刻に1時間を加算
    next_hour = one_hour_later.strftime("%H:00")  # "HH:00" フォーマットで整形
    day_type = "even" if one_hour_later.day % 2 == 0 else "odd"  # 偶数日か奇数日かを判定

    # 偶数日と奇数日でスケジュールを切り替え
    schedule = stages_even if day_type == "even" else stages_odd

    # スケジュール内で1時間後の時刻を探す
    for entry in schedule:
        if entry["time"] == next_hour:
            stage_name = stages[int(entry["stage"])]  # ステージ名を取得
            rule_name = rules[int(entry["rule"])]  # ルール名を取得
            message = f"{one_hour_later.month}月{one_hour_later.day}日 {next_hour}『{stage_name}』『{rule_name}』です。"
            await ctx.send(message)
            return

    # 該当するスケジュールが見つからない場合
    await ctx.send(f"{next_hour}のスケジュール情報が見つかりませんでした。")

# !today コマンドの実装
@bot.command(name="today")
async def today_command(ctx):
    now = datetime.now(pytz.utc).astimezone(jst)
    day_type = "even" if now.day % 2 == 0 else "odd"  # 偶数日 or 奇数日判定

    # 適切なスケジュールを選択
    schedule = stages_even if day_type == "even" else stages_odd

    # スケジュールを整形
    schedule_text = f" **{now.month}月{now.day}日のステージ表**\n"
    for entry in schedule:
        stage_name = stages[int(entry["stage"])]
        rule_name = rules[int(entry["rule"])]
        schedule_text += f" {entry['time']}『{stage_name}』『{rule_name}』\n"

    # メッセージを送信
    await ctx.send(schedule_text)

# !after コマンドの実装
@bot.command(name="after")
async def after_command(ctx):
    now = datetime.now(pytz.utc).astimezone(jst)
    current_time = now.strftime("%H:%M")
    day_type = "even" if now.day % 2 == 0 else "odd"  # 偶数日 or 奇数日判定

    # 適切なスケジュールを選択
    schedule = stages_even if day_type == "even" else stages_odd

    # 現在時刻以降のスケジュールを整形
    schedule_text = f" **{now.month}月{now.day}日の現在以降のステージ表**\n"
    for entry in schedule:
        if entry["time"] >= current_time:
            stage_name = stages[int(entry["stage"])]
            rule_name = rules[int(entry["rule"])]
            schedule_text += f" {entry['time']}『{stage_name}』『{rule_name}』\n"

    # メッセージを送信
    if schedule_text.strip().endswith("ステージ表**"):
        await ctx.send("🛑 現在以降のスケジュールは見つかりませんでした。")
    else:
        await ctx.send(schedule_text)

# !next5h コマンドの実装
@bot.command(name="next5h")
async def next_5_hours_command(ctx):
    now = datetime.now(pytz.utc).astimezone(jst)
    schedule_text = f"**{now.month}月{now.day}日 {now.hour:02d}時から5時間のステージ表**\n"

    for offset in range(5):
        target_time = now + timedelta(hours=offset)
        target_hour = target_time.hour
        target_day = target_time.day

        # 日によって奇数偶数を判断し、スケジュールリストを取得
        day_type = "even" if target_day % 2 == 0 else "odd"
        schedule = stages_even if day_type == "even" else stages_odd

        # スケジュールから一致する時間を探す
        time_str = f"{target_hour:02d}:00"
        for entry in schedule:
            if entry["time"] == time_str:
                stage_name = stages[int(entry["stage"])]
                rule_name = rules[int(entry["rule"])]
                schedule_text += f"{time_str} 『{stage_name}』『{rule_name}』\n"
                break

    await ctx.send(schedule_text)

# !canon コマンドの実装
@bot.command(name="canon")
async def canon_schedule(ctx):
    now = datetime.now(pytz.utc).astimezone(jst)
    current_time = now.strftime("%H:%M")

    # 今日と明日でスケジュールを用意
    day_types = []
    for offset in [0, 1]:  # 今日と明日
        day = now.day + offset
        day_type = "even" if day % 2 == 0 else "odd"
        schedule = stages_even if day_type == "even" else stages_odd
        day_types.append((day, schedule))

    result = []
    for offset, (day, schedule) in enumerate(day_types):
        for entry in schedule:
            # 今日の場合は current_time 以降、明日は全部
            if offset == 0 and entry["time"] < current_time:
                continue
            if rules[int(entry["rule"])] == "キャノンエスコート":
                stage = stages[int(entry["stage"])]
                message = f"{entry['time']}『{stage}』"
                result.append(message)
                if len(result) >= 5:
                    break
        if len(result) >= 5:
            break

    if result:
        await ctx.send(" **現在以降のキャノンエスコートのスケジュール（最大5件）**\n" + "\n".join(result))
    else:
        await ctx.send(" 現在以降にキャノンエスコートのスケジュールは見つかりませんでした。")

# !hack コマンドの実装
@bot.command(name="hack")
async def canon_schedule(ctx):
    now = datetime.now(pytz.utc).astimezone(jst)
    current_time = now.strftime("%H:%M")

    # 今日と明日でスケジュールを用意
    day_types = []
    for offset in [0, 1]:  # 今日と明日
        day = now.day + offset
        day_type = "even" if day % 2 == 0 else "odd"
        schedule = stages_even if day_type == "even" else stages_odd
        day_types.append((day, schedule))

    result = []
    for offset, (day, schedule) in enumerate(day_types):
        for entry in schedule:
            # 今日の場合は current_time 以降、明日は全部
            if offset == 0 and entry["time"] < current_time:
                continue
            if rules[int(entry["rule"])] == "アンテナハック":
                stage = stages[int(entry["stage"])]
                message = f"{entry['time']}『{stage}』"
                result.append(message)
                if len(result) >= 5:
                    break
        if len(result) >= 5:
            break

    if result:
        await ctx.send(" **現在以降のアンテナハックのスケジュール（最大5件）**\n" + "\n".join(result))
    else:
        await ctx.send(" 現在以降にアンテナハックのスケジュールは見つかりませんでした。")

# 受け取ったコマンドを表示
async def on_message(message):
    print(f"Received message: {message.content}")  # 受信メッセージをログに表示
    await bot.process_commands(message)  # コマンド処理を継続

# Botの起動時
@bot.event
async def on_ready():
    global scheduler_started
    channel = bot.get_channel(1357707739748368414)  # 投稿先のチャンネルIDを設定
    
    if not scheduler_started:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(send_stage_and_rule, "cron", minute=0)
        scheduler.start()
        scheduler_started = True  # フラグを立てる
        print("✅ スケジューラを起動しました。")

    print(f"🟢 Bot is ready as {bot.user}")
    
# Botを起動
if TOKEN:
    bot.run(TOKEN)
else:
    print("BOT_TOKEN が設定されていません。環境変数を確認してください。")

#作業メモ、特定のステージの時間を知るコマンド