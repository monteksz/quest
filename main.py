import urllib.parse
import json
import requests
import time
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

def decode_tg_login_params(encoded_str):
    encoded_json = encoded_str.split('&')[0].split('=')[1]
    decoded_json = urllib.parse.unquote(encoded_json)
    user_data = json.loads(decoded_json)
    return user_data

def login_to_api(user_data, tg_login_params, account_number):
    url = "https://tgapp-api.matchain.io/api/tgapp/v1/user/login"
    payload = {
        "first_name": user_data['first_name'],
        "last_name": user_data['last_name'],
        "tg_login_params": tg_login_params,
        "uid": user_data['id'],
        "username": user_data['username'],
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data and 'token' in response_data['data']:
            token = response_data['data']['token']
            print(Fore.GREEN + Style.BRIGHT + f"[Akun {account_number}] Token diperoleh: {token}")
            return token
        else:
            print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Token tidak ditemukan dalam respons.")
            return None
    else:
        print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Login gagal.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return None

def get_balance(uid, token, account_number):
    url = "https://tgapp-api.matchain.io/api/tgapp/v1/point/balance"
    payload = {"uid": uid}
    headers = {
        "Authorization": token,
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Origin": "https://tgapp.matchain.io",
        "Pragma": "no-cache",
        "Referer": "https://tgapp.matchain.io/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data:
            balance = response_data['data']
            return balance
        else:
            print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Saldo tidak ditemukan dalam respons.")
            return None
    else:
        print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Gagal mendapatkan saldo.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return None

def check_reward_status(uid, token, account_number):
    url = "https://tgapp-api.matchain.io/api/tgapp/v1/point/reward"
    payload = {"uid": uid}
    headers = {
        "Authorization": token,
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Origin": "https://tgapp.matchain.io",
        "Pragma": "no-cache",
        "Referer": "https://tgapp.matchain.io/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data:
            reward = response_data['data']['reward']
            next_claim_timestamp = response_data['data']['next_claim_timestamp']
            return reward, next_claim_timestamp
        else:
            print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Data reward tidak ditemukan dalam respons.")
            return None, None
    else:
        print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Gagal memeriksa status reward.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return None, None

def claim_reward(uid, token, account_number):
    url = "https://tgapp-api.matchain.io/api/tgapp/v1/point/reward/claim"
    payload = {"uid": uid}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": token,
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Origin": "https://tgapp.matchain.io",
        "Pragma": "no-cache",
        "Referer": "https://tgapp.matchain.io/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data:
            print(Fore.GREEN + Style.BRIGHT + f"[Akun {account_number}] Reward berhasil diklaim: {response_data['data']}")
            start_farming(uid, token, account_number) 

            balance = get_balance(uid, token, account_number)
            if balance is not None:
                print(Fore.GREEN + Style.BRIGHT + f"[Akun {account_number}] Saldo terbaru: {balance}")
            
            return response_data['data']
        else:
            print(Fore.YELLOW + Style.BRIGHT + f"[Akun {account_number}] Belum waktunya klaim reward.")
            return None
    else:
        response_data = response.json()
        if 'next_claim_timestamp' in response_data:
            next_claim_timestamp = response_data['next_claim_timestamp']
            current_timestamp = int(time.time())
            time_diff = next_claim_timestamp - current_timestamp
            next_claim_time = str(timedelta(seconds=time_diff))
            print(Fore.YELLOW + Style.BRIGHT + f"[Akun {account_number}] Waktu berikutnya bisa klaim: {next_claim_time}")
        else:
            print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Gagal melakukan klaim reward.")
            print("Status Code:", response.status_code)
            print("Response:", response_data)
        return None

def start_farming(uid, token, account_number):
    url = "https://tgapp-api.matchain.io/api/tgapp/v1/point/reward/farming"
    payload = {"uid": uid}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": token,
        "Cache-Control": "no-cache",
        "Content-Length": str(len(json.dumps(payload))),
        "Content-Type": "application/json",
        "Origin": "https://tgapp.matchain.io",
        "Pragma": "no-cache",
        "Referer": "https://tgapp.matchain.io/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Priority": "u=1, i",
        "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data:
            print(Fore.GREEN + Style.BRIGHT + f"[Akun {account_number}] Farming berhasil dimulai: {response_data['data']}")
            return response_data['data']
        else:
            print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Data farming tidak ditemukan dalam respons.")
            return None
    else:
        print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Gagal memulai farming.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return None


def play_game(token, account_number):
    url = "https://tgapp-api.matchain.io/api/tgapp/v1/game/play"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": token,
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Origin": "https://tgapp.matchain.io",
        "Pragma": "no-cache",
        "Referer": "https://tgapp.matchain.io/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data:
            game_id = response_data['data']['game_id']
            game_count = response_data['data']['game_count']
            print(Fore.GREEN + Style.BRIGHT + f"[Akun {account_number}] Game ID: {game_id}, Game Count: {game_count}")
            return game_id, game_count
        else:
            print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Data permainan tidak ditemukan dalam respons.")
            return None, None
    else:
        print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Gagal memulai permainan.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return None, None

def get_game_rule(token, account_number):
    url = "https://tgapp-api.matchain.io/api/tgapp/v1/game/rule"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": token,
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Origin": "https://tgapp.matchain.io",
        "Pragma": "no-cache",
        "Referer": "https://tgapp.matchain.io/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data:
            game_rule = response_data['data']['rule']
            game_count = response_data['data']['game_count']
            return game_rule, game_count
        else:
            print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Data aturan permainan tidak ditemukan dalam respons.")
            return None, None
    else:
        print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Gagal mendapatkan aturan permainan.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return None, None

def claim_game(token, game_id, point, account_number):
    url = "https://tgapp-api.matchain.io/api/tgapp/v1/game/claim"
    payload = {
        "game_id": game_id,
        "point": point
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": token,
        "Cache-Control": "no-cache",
        "Content-Length": str(len(json.dumps(payload))),
        "Content-Type": "application/json",
        "Origin": "https://tgapp.matchain.io",
        "Pragma": "no-cache",
        "Referer": "https://tgapp.matchain.io/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data:
            print(Fore.GREEN + Style.BRIGHT + f"[Akun {account_number}] Klaim berhasil: {response_data['data']}")
            return response_data['data']
        else:
            print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Data klaim tidak ditemukan dalam respons.")
            return None
    else:
        print(Fore.RED + Style.BRIGHT + f"[Akun {account_number}] Gagal melakukan klaim.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return None

def convert_timestamp_to_duration(timestamp):
    current_time = int(time.time() * 1000)
    time_difference = timestamp - current_time

    if time_difference <= 0:
        return "Sekarang bisa klaim"

    seconds = time_difference // 1000
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    hours = hours % 24
    minutes = minutes % 60
    seconds = seconds % 60

    return f"{days} hari {hours} jam {minutes} menit {seconds} detik lagi"

def main():
    try:
        with open('data.txt', 'r') as file:
            tg_login_params_list = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print("File data.txt tidak ditemukan.")
        return

    if not tg_login_params_list:
        print("Tidak ada data akun yang ditemukan dalam file data.txt.")
        return

    play_choice = input("Apakah ingin bermain game? (Y/N): ").strip().upper()

    while True:
        for i, tg_login_params in enumerate(tg_login_params_list, start=1):
            print(Fore.BLUE + Style.BRIGHT + f"PENGECEKAN AKUN KE-{i}")

            user_data = decode_tg_login_params(tg_login_params)

            if user_data:
                token = login_to_api(user_data, tg_login_params, i)

                if token:
                    uid = user_data['id']

                    initial_balance = get_balance(uid, token, i)

                    if initial_balance is not None:
                        print(f"[Akun {i}] Saldo akun saat ini: {initial_balance}")

                        reward, next_claim_timestamp = check_reward_status(uid, token, i)

                        if reward is not None:
                            print(f"[Akun {i}] Reward saat ini: {reward}")
                            print(f"[Akun {i}] Waktu berikutnya bisa klaim: {convert_timestamp_to_duration(next_claim_timestamp)}")

                            claimed_reward = claim_reward(uid, token, i)
                            if claimed_reward is not None:
                                print(f"[Akun {i}] Reward berhasil diklaim: {claimed_reward}")
                            else:
                                print(f"[Akun {i}] Tidak ada reward yang tersedia.")
                            
                            if play_choice == 'Y':
                                game_count = 1
                                while game_count > 0:
                                    game_id, game_count = play_game(token, i)
                                    if game_id:
                                        game_rule, game_count = get_game_rule(token, i)
                                        if game_rule:
                                            point = 0
                                            for round_rule in game_rule:
                                                for round_num, objects in round_rule.items():
                                                    print(f"[Akun {i}] Putaran {round_num}:")
                                                    for obj in objects:
                                                        if obj["img"] == "/assets/icon_games_bomb.png":
                                                            print(f"[Akun {i}]   Menghindari bom di posisi {obj['x']}")
                                                        else:
                                                            print(f"[Akun {i}]   Mengumpulkan {obj['objectType']} di posisi {obj['x']} dengan skor {obj['score']}")
                                                            point += obj['score']

                                        claim_response = claim_game(token, game_id, point, i)
                                        if claim_response:
                                            final_balance = get_balance(uid, token, i)
                                            if final_balance is not None:
                                                print(f"[Akun {i}] Saldo setelah bermain: {final_balance}")
                                            else:
                                                print(Fore.RED + Style.BRIGHT + f"[Akun {i}] Gagal mendapatkan saldo setelah bermain.")
                                        else:
                                            print(Fore.RED + Style.BRIGHT + f"[Akun {i}] Gagal klaim poin permainan.")
                                    else:
                                        print(Fore.RED + Style.BRIGHT + f"[Akun {i}] Gagal mendapatkan aturan permainan.")
                                else:
                                    print(Fore.RED + Style.BRIGHT + f"[Akun {i}] Gagal memulai permainan.")

                                if game_count > 0:
                                    print(Fore.YELLOW + Style.BRIGHT + f"[Akun {i}] Jeda 10 detik sebelum permainan berikutnya. Sisa game count: {game_count}")
                                    time.sleep(10)
                        else:
                            print(f"[Akun {i}] Memilih untuk tidak bermain game.")
                    else:
                        print(Fore.RED + Style.BRIGHT + f"[Akun {i}] Gagal mendapatkan saldo akun saat ini.")
                else:
                    print(Fore.RED + Style.BRIGHT + f"[Akun {i}] Gagal mendapatkan token.")
            else:
                print(Fore.RED + Style.BRIGHT + f"[Akun {i}] Gagal mendekode data pengguna.")

            print(Fore.BLUE + Style.BRIGHT + f"[Akun {i}] PENGECEKAN AKUN KE-{i} TELAH BERHASIL DILAKUKAN")
            for remaining_seconds in range(10, 0, -1):
                print(Fore.YELLOW + Style.BRIGHT + f"COOLDOWN: {remaining_seconds} detik", end='\r')
                time.sleep(1)
            print("\n")

        print(Fore.BLUE + Style.BRIGHT + "PENGECEKAN SEMUA AKUN TELAH SELESAI")
        for remaining_seconds in range(60, 0, -1):
            minutes, seconds = divmod(remaining_seconds, 60)
            print(Fore.YELLOW + Style.BRIGHT + f"PENGECEKAN SELANJUTNYA DALAM {minutes:02d}:{seconds:02d}", end='\r')
            time.sleep(1)
        print("\n")

if __name__ == "__main__":
    main()