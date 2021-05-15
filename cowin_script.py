#My cowin Script
import os
import sys
import copy
import time
import argparse
import datetime
import requests
import winsound
import tabulate
import threading
from hashlib import sha256
from types import SimpleNamespace
from captcha import captcha_builder


#Cowin official urls
BOOKING_URL = "https://cdn-api.co-vin.in/api/v2/appointment/schedule"
BENEFICIARIES_URL = "https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries"
CALENDAR_URL_DISTRICT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={0}&date={1}"
CALENDAR_URL_PINCODE = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByPin?pincode={0}&date={1}"
CAPTCHA_URL = "https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha"
OTP_PUBLIC_URL = "https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP"
OTP_PRO_URL = "https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP"

#My login details
mobile = '' # Enter your mobile number
request_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
data = {'mobile': mobile, 'secret': 'U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw=='}

#Local file Paths
token_path = "session_token.txt"
mobile_path = "registered_mobile_number.txt"
location_path = "location_details.txt"

# Vaccine Search Parameters
minimum_slots = 1
vaccine_type = None      # "COVISHIELD" or "COVAXIN"
search_option = 2
refresh_freq = 15        # in secs
auto_book = "yes-please"
start_date = 2           #2 - tomorrow, 1 - Today
fee_type = ["Free", "Paid"]
center_age_filter = 18

def check_session():
    if os.path.exists(token_path):
        token = open (token_path, "r").read()
        request_header["Authorization"] = f"Bearer {token}"
        _tmp = requests.get(BENEFICIARIES_URL, headers=request_header)
        if _tmp.status_code != 200:
            winsound.Beep(850, 5000)
            gen_otp()
        return _tmp.status_code
    else:
        gen_otp()
    return None

def gen_otp():
    # To generate OTP and authenticate
    if "Authorization" in request_header:
        del request_header["Authorization"]
    mobile_num = set_mobile_number()
    data['mobile'] = str(mobile_num)
    txnId = requests.post(url="https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP", json=data, headers=request_header)
    if txnId.status_code == 200:
        txnId_info = txnId.json()["txnId"]
        token = authenticate_otp(txnId_info)
        request_header["Authorization"] = f"Bearer {token}"
        with open (token_path, "w") as f:
            f.write(str(token)) 
    else:
        print("Unable to generate OTP through <gen_otp> fucntion")
        os.system("exit")

def authenticate_otp(txnId_info):
    # To Authenticate the user and OTP function
    not_verified_flag = False
    while not_verified_flag is not True:
        OTP = input("Enter the OTP: ")
        data = {"otp": sha256(str(OTP.strip()).encode("utf-8")).hexdigest(), "txnId": txnId_info}
        token = requests.post(url="https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp", json=data, headers=request_header)
        if token.status_code == 200:
            token = token.json()["token"]
            #print(f"Token Generated: {token}")
            not_verified_flag = True
        else:
            print("Unable to Validate OTP. Enter again.")
            token = None
    return token
    
def set_mobile_number():
    if mobile.strip() == '':
        if os.path.exists(mobile_path):
            mobile_num = open(mobile_path, 'r').read().strip()
        else:
            mobile_num = mobile
        if mobile_num.strip() == '' or len(mobile_num) != 10:
            mobile_num = input("Enter the registered mobile number (without any 0 prefix or country code or '+' sign): ")
            with open(mobile_path, 'w') as fm:
                fm.write(str(mobile_num))
    else:
        mobile_num = mobile
    return mobile_num

def set_location_preference_by_district():
    if os.path.exists(location_path):
        location_path_info = open(location_path, 'r').read().split("|")
        if len(location_path_info) == 1:
            pincode = location_path_info[0]
        else:
            reqd_districts= []
            state = location_path_info[0]
            district_list = location_path_info[1]
            for district_str in district_list.split(","):
                district_id, district_name = district_str.split(":")
                reqd_districts.append({
                        "district_id": district_id,
                        "district_name": district_name
                    })
    else:
        str_dist = ''
        reqd_districts, state = get_distict_names()
        for reqd_districts_each in reqd_districts:
            str_dist += str(reqd_districts_each["district_id"]) + ":" + str(reqd_districts_each["district_name"]) + ","
        str_dist = state + "|" + str_dist[:-1] # To ignore the last comma
        with open(location_path, 'w') as fl:
            fl.write(str_dist)
            
    return reqd_districts

def set_location_preference_by_pincode():
    locations = []
    pincodes = input("Enter pincodes to search (For multiple, write the pincodes with comma): ")
    for pincode in enumerate(pincodes.split(",")):
        locations.append({"pincode": pincode})
    return locations
            
def get_distict_names():
    # Getting district names
    states = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/states", headers=request_header)
    reqd_districts = []
    if states.status_code == 200:
        states = states.json()["states"]
        state_id = None
        state_values = [[iter_num+1] + list([state_details['state_name']]) for iter_num, state_details in enumerate(states)]
        print(tabulate.tabulate(state_values, tablefmt="grid"))
        state_input = input("Enter the State number from the table above : ")
        state_id = states[int(state_input)-1]["state_id"]
        #for state in states:
        #    if state["state_name"] == state_values[state_input-1][1]##"Karnataka": ###########    Find the state name : Karnataka
        #        state_id = state["state_id"]
        districts = requests.get(f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}", headers=request_header)
        if districts.status_code == 200:
            districts = districts.json()["districts"]
            district_id = None
            district_values = [[iter_num+1] + list([district_details['district_name']]) for iter_num, district_details in enumerate(districts)]
            print(tabulate.tabulate(district_values, tablefmt="grid"))
            district_inputs = input("Enter the District number from the table above (For multiple district enter the number with comma) : ")
            district_input_list = district_inputs.split(",")
            for iter_num, district in enumerate(districts):
                if str(iter_num + 1) in district_input_list:
                    reqd_districts.append({
                        "district_id": district["district_id"],
                        "district_name": district["district_name"]
                    })
            print("Hey", reqd_districts)
        return reqd_districts, states[int(state_input)-1]["state_name"]
    else:
        print("Unable to Fetch District details.")

def get_vaccine_centers_in_district(base_url, start_date_datetime, location_dtls):
    #To get list of vaccination centers in a district
    login_flag = False
    while login_flag == False:
        total_list = []
        for location_each in location_dtls:
            id_ = location_each["district_id"]
            resp = requests.get(base_url.format(id_, start_date_datetime), headers=request_header)
            #print(resp.json())
            if resp.status_code == 200:
                resp = resp.json()
                login_flag = True
                #resp = remove_centers_for_45_above(resp)
                resp = remove_centers_on_other_criterias(resp)
                total_list += resp
            else:
                print("Session timed out. Trying to Login In. Please give OTP.")
                time.sleep(2)
                status_code = check_session()     
    return total_list

def get_vaccine_centers_in_pincode(base_url, start_date_datetime, location_dtls):
    #To get list of vaccination centers in a pincode
    login_flag = False
    while login_flag == False:
        total_list = []
        for location_each in location_dtls:
            id_ = location_each["pincode"]
            resp = requests.get(base_url.format(id_, start_date_datetime), headers=request_header)
            if resp.status_code == 200:
                resp = resp.json()
                login_flag = True
                #resp = remove_centers_for_45_above(resp)
                resp = remove_centers_on_other_criterias(resp)
                total_list += resp
            else:
                print("Session timed out. Trying to Login In. Please give OTP.")
                time.sleep(2)
                status_code = check_session()  
    return total_list

def remove_centers_for_45_above(resp):
    # Remove centers that are for 45+ only
    #with open ("test1.txt", "w") as ff:
        #ff.write(str(resp))
    if "centers" in resp:
        for center in resp["centers"]: 
            if center["sessions"][0]['min_age_limit'] != center_age_filter:
                resp["centers"].remove(center)
    return resp
    
def remove_centers_on_other_criterias(resp):
    #Filter centers on other criteria
    options = []
    #with open ("test2.txt", "w") as ff:
        #ff.write(str(resp))
    if "centers" in resp:
        if len(resp["centers"]) > 0:
            for center in resp["centers"]:
                for session in center["sessions"]:
                    if ((session["available_capacity"] >= minimum_slots)
                        and (session["min_age_limit"] == center_age_filter)
                        and (center["fee_type"] in fee_type)):
                        out = {
                            "name": center["name"],
                            "district": center["district_name"],
                            "pincode": center["pincode"],
                            "center_id": center["center_id"],
                            "available": session["available_capacity"],
                            "date": session["date"],
                            "slots": session["slots"],
                            "session_id": session["session_id"],
                            }
                        options.append(out)
        
    if len(options) > 0:
        options = sorted(
                options,
                key=lambda k: (
                    k["district"].lower(),
                    k["pincode"],
                    k["name"].lower(),
                    datetime.datetime.strptime(k["date"], "%d-%m-%Y"),
                ),
            )    
    else:
        time.sleep(3) # To stop spam
        print("No vaccination center found for the given criteria")
    #print("Options" , options)
    return options

def make_alert_sound():
    winsound.Beep(640, 300)
    winsound.Beep(540, 200)
    winsound.Beep(740, 500)
    winsound.Beep(850, 300)
    winsound.Beep(540, 200)
    winsound.Beep(650, 500)

def main():
    booked_flag = False
    status_code = check_session()
    # Get Benificiary lists
    beneficiary_flag = False
    while beneficiary_flag == False:
        beneficiaries = requests.get(BENEFICIARIES_URL, headers=request_header)
        if beneficiaries.status_code == 200:
            beneficiaries = beneficiaries.json()["beneficiaries"]
            #print(beneficiaries)
            beneficiary_flag = True
        else:
            print("Unable to get benificiary.")
            time.sleep(2)
            
    refined_beneficiaries = []
    for beneficiary in beneficiaries:
        # To only pull those names that are not booked
        if beneficiary["vaccination_status"] == "Not Vaccinated" and beneficiary["appointments"] == []:
            beneficiary["age"] = datetime.datetime.today().year - int(beneficiary["birth_year"])
            tmp = {
                "bref_id": beneficiary["beneficiary_reference_id"], # Can be hardcoded too 
                "name": beneficiary["name"],
                "vaccine": beneficiary["vaccine"],
                "age": beneficiary["age"],
                "status": beneficiary["vaccination_status"],
            }
            refined_beneficiaries.append(tmp)        
    beneficiary_dtls = copy.deepcopy(refined_beneficiaries)
    
    if isinstance(start_date, int) and start_date == 2:
        start_date_datetime = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    elif isinstance(start_date, int) and start_date == 1:
        start_date_datetime = datetime.datetime.today().strftime("%d-%m-%Y")
    
    #Get district name and id
    #reqd_districts = [{
    #                    "district_id": 294,
    #                    "district_name": "BBMP"
    #                },
    #                {
    #                    "district_id": 265,
    #                    "district_name": "Bangalore Urban"
    #                }]
    location_search_choice = int(input("Do you want to search by Pincode (enter 1) or District (enter 2) : ").strip())
    #location_search_choice == 2 # For Testing
    if location_search_choice == 2:
        reqd_districts = set_location_preference_by_district()
        location_dtls = copy.deepcopy(reqd_districts)
        base_url = CALENDAR_URL_DISTRICT
    else:
        reqd_pincodes = set_location_preference_by_pincode()
        location_dtls = copy.deepcopy(reqd_pincodes)
        base_url = CALENDAR_URL_PINCODE
    if vaccine_type:
        base_url += f"&vaccine={vaccine_type}"

    count_trial_booking = 1
    while booked_flag is not True:
        print(f"Trying to book no: {count_trial_booking}")
        #To find the list of available centers 
        resp_centers_available = []
        start = datetime.datetime.now()
        while len(resp_centers_available) < 1:
            #resp_vaccine_centers_all = get_vaccine_centers_in_district(base_url, start_date_datetime, location_dtls)
            if location_search_choice == 2:
                resp_centers_available = get_vaccine_centers_in_district(base_url, start_date_datetime, location_dtls)
            else:
                resp_centers_available = get_vaccine_centers_in_pincode(base_url, start_date_datetime, location_dtls)
            end = datetime.datetime.now()
            diff = end-start
            if diff.seconds > 250:
                status_code = check_session()
                if status_code != 200:
                    start = datetime.datetime.now()
        print(resp_centers_available)
        winsound.Beep(650, 1000)
        winsound.Beep(750, 1000)
        options = copy.deepcopy(resp_centers_available)
        
        #Count number of benificiary
        can_be_given = 0
        max_avaliable = options[0]['available']
        if max_avaliable == 1:
            can_be_given = 1
        elif max_avaliable == 2:
            can_be_given = 2
        elif max_avaliable == 3:
            can_be_given = 3
        elif max_avaliable >= 4:
            can_be_given = 4
        
        ben_available = len(beneficiary_dtls)
        
        if ben_available <= can_be_given:
            can_be_given = ben_available
        
        ben_id =[]
        for each_ben_num in range(can_be_given):
            ben_id.append(beneficiary_dtls[each_ben_num]["bref_id"])
        new_req = {
            "beneficiaries": ben_id,
            "dose": 1,
            "center_id": options[0]["center_id"],
            "session_id": options[0]["session_id"],
            "slot": options[0]["slots"][1],
        }
        
        # Write the captcha
        t1 = threading.Thread(target=make_alert_sound)
        t1.start()
        t1.join()
        valid_captcha = True
        #########################Testing#######################
        break ###### remove
        while valid_captcha:
            resp = requests.post(CAPTCHA_URL, headers=request_header)
            if resp.status_code == 200:
                captcha = captcha_builder(resp.json())
            else:
                print("No Captcha generating. Check issue")
                print(resp)
            new_req["captcha"] = captcha
            
            resp = requests.post(BOOKING_URL, headers=request_header, json=new_req)
            #print(resp.status_code)
            print("\n")
            if resp.status_code == 401:
                print("TOKEN INVALID")
                #_ = get_vaccine_centers_in_district(base_url, start_date_datetime)
                #if len(_) < 1:
                    #break
            elif resp.status_code == 200:
                print("BOOKED! Check Cowin Portal.")
                print("Booked for " + str(can_be_given) + " person.")
                booked_flag = True
            elif resp.status_code == 400:
                print(f"Response: {resp.status_code} : {resp.text}")
                pass
            else:
                print(f"Response: {resp.status_code} : {resp.text}")
                user_captcha_ans = input("Regenerate Captcha? y/n")
                if user_captcha_ans.lower() == "n":
                    break
                else:
                    continue 
                    
        count_trial_booking += 1
        print(f"Booking Response Code: {resp.status_code}")
        
    

if __name__ == '__main__':
    main()
