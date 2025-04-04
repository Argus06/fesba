import tweepy
import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

# .env ファイルを読み込み
load_dotenv()

# 認証情報の読み込み
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_secret = os.getenv("ACCESS_SECRET")

# Twitter API認証
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
api = tweepy.API(auth)

# ステージとルールの配列
stages = [
    "アオイの島：演舞台",
    "覇者の塔：エンブレム前",
    "エリジウム：商業区",
    "アストラ島：遺跡前",
    "リベリオンスタジアム"
]
rules = [
    "アンテナハック",
    "キャノンエスコート"
]

# スケジュール（奇数日と偶数日）
stages_odd = [
    {"time": "00:00", "stage": "1", "rule": "1"},
    {"time": "01:00", "stage": "1", "rule": "0"},
    {"time": "02:00", "stage": "0", "rule": "1"},
    {"time": "03:00", "stage": "0", "rule": "0"},
    {"time": "04:00", "stage": "4", "rule": "1"},
    {"time": "05:00", "stage": "2", "rule": "0"},
    {"time": "06:00", "stage": "3", "rule": "1"},
    {"time": "07:00", "stage": "3", "rule": "0"},
    {"time": "08:00", "stage": "1", "rule": "1"},
    {"time": "09:00", "stage": "4", "rule": "0"},
    {"time": "10:00", "stage": "0", "rule": "1"},
    {"time": "11:00", "stage": "1", "rule": "0"},
    {"time": "12:00", "stage": "4", "rule": "1"},
    {"time": "13:00", "stage": "0", "rule": "0"},
    {"time": "14:00", "stage": "3", "rule": "1"},
    {"time": "15:00", "stage": "2", "rule": "0"},
    {"time": "16:00", "stage": "3", "rule": "0"},
    {"time": "17:00", "stage": "4", "rule": "1"},
    {"time": "18:00", "stage": "4", "rule": "0"},
    {"time": "19:00", "stage": "3", "rule": "1"},
    {"time": "20:00", "stage": "1", "rule": "0"},
    {"time": "21:00", "stage": "1", "rule": "1"},
    {"time": "22:00", "stage": "0", "rule": "0"},
    {"time": "23:00", "stage": "0", "rule": "1"}
]

stages_even = [
    {"time": "00:00", "stage": "2", "rule": "0"},
    {"time": "01:00", "stage": "4", "rule": "1"},
    {"time": "02:00", "stage": "3", "rule": "0"},
    {"time": "03:00", "stage": "3", "rule": "1"},
    {"time": "04:00", "stage": "4", "rule": "0"},
    {"time": "05:00", "stage": "1", "rule": "1"},
    {"time": "06:00", "stage": "1", "rule": "0"},
    {"time": "07:00", "stage": "0", "rule": "1"},
    {"time": "08:00", "stage": "0", "rule": "0"},
    {"time": "09:00", "stage": "4", "rule": "1"},
    {"time": "10:00", "stage": "2", "rule": "0"},
    {"time": "11:00", "stage": "3", "rule": "1"},
    {"time": "12:00", "stage": "3", "rule": "0"},
    {"time": "13:00", "stage": "1", "rule": "1"},
    {"time": "14:00", "stage": "4", "rule": "0"},
    {"time": "15:00", "stage": "0", "rule": "1"},
    {"time": "16:00", "stage": "1", "rule": "1"},
    {"time": "17:00", "stage": "0", "rule": "0"},
    {"time": "18:00", "stage": "0", "rule": "1"},
    {"time": "19:00", "stage": "2", "rule": "0"},
    {"time": "20:00", "stage": "4", "rule": "1"},
    {"time": "21:00", "stage": "3", "rule": "0"},
    {"time": "22:00", "stage": "3", "rule": "1"},
    {"time": "23:00", "stage": "4", "rule": "0"}
]

# 投稿する関数
def tweet_stage_and_rule():
    now = datetime.now()
    day_type = "even" if now.day % 2 == 0 else "odd"
    schedule = stages_even if day_type == "even" else stages_odd
    current_hour = now.strftime("%H:00")

    for entry in schedule:
        if entry["time"] == current_hour:
            stage_name = stages[int(entry["stage"])]
            rule_name = rules[int(entry["rule"])]
            tweet = f"{now.month}月{now.day}日 {current_hour}『{stage_name}』『{rule_name}』です。"
            try:
                api.update_status(tweet)
                print("ツイート完了:", tweet)
            except Exception as e:
                print("ツイート失敗:", e)
            break

# スケジューラーで毎時0分に実行
scheduler = BlockingScheduler()
scheduler.add_job(tweet_stage_and_rule, 'cron', minute=0)
print("Twitter Bot 起動中...（毎時00分に投稿）")
tweet_stage_and_rule()  # テスト投稿（今すぐ1回ツイート）
scheduler.start()

